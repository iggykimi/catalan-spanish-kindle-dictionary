#!/usr/bin/env python3
"""Build a Catalan-Spanish Kindle dictionary (.mobi).

Pipeline stages:
  1. morphology   - load lemma->forms map from the Softcatala dictionary
  2. base         - FreeDict cat-spa StarDict -> tabfile
  3. inflections  - attach Softcatala inflected forms as lookup variants
  4. elisions     - apostrophe clitic variants per part of speech
  5. accents      - bidirectional accented/unaccented pairs
  6. supplements  - contractions, weak pronouns, gap-filling lemmas
  7. apertium     - merge filtered Apertium spa-cat bilingual pairs
  8. mobi         - compile with kindlegen and stamp version metadata

Usage:
  python build.py            # full pipeline
  python build.py --stage mobi
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import shutil
import struct
import subprocess
import sys

# Configuration - adjust paths to your machine
WORK = pathlib.Path(r"C:\tmp\kindle-ca")
OUT_DIR = WORK / "release"

FREEDICT_TABFILE = WORK / "cat-spa.txt"
SOFTCATALA_DICT = WORK / "diccionari.txt"
APERTIUM_METADIX = WORK / "apertium-spa-cat.metadix"
KINDLEGEN = WORK / "kindlegen" / "kindlegen.exe"

VERSION = "1.0.0"
DICT_TITLE = f"Catala-Espanyol Kindle Dictionary v{VERSION}"
SOURCE_LANG, TARGET_LANG = "ca", "es"

VOWELS = set("aeiouàáèéíìòóúüïAEIOUÀÁÈÉÍÌÒÓÚÜÏhH")
VERB_ELISIONS = ["l'", "d'", "n'", "s'", "m'", "t'"]
NOUN_ELISIONS = ["l'", "d'", "n'"]
POS_LABEL = {"n": "nom", "adj": "adjectiu", "vblex": "verb", "vbmod": "verb",
             "vbser": "verb", "vbhaver": "verb", "adv": "adverbi", "preadv": "adverbi"}
CONTENT_POS = set(POS_LABEL)


def grammar(tag: str, text: str) -> str:
    return f'<div><font class="grammar" color="green">{tag}</font></div>{text}'


# --- Stage 1: morphology -----------------------------------------------------
def load_morphology() -> tuple[dict[str, set[str]], set[str]]:
    print("[morphology] loading", SOFTCATALA_DICT.name)
    lemma_forms: dict[str, set[str]] = collections.defaultdict(set)
    with open(SOFTCATALA_DICT, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) >= 2 and "'" not in parts[0] and 1 < len(parts[0]) <= 25:
                lemma_forms[parts[1].lower()].add(parts[0])
    forms = set()
    for s in lemma_forms.values():
        forms |= s
    print(f"[morphology] {len(lemma_forms)} lemmas, {len(forms)} word forms")
    return lemma_forms, forms


# --- Stage 2: base bilingual -------------------------------------------------
def load_base_tabfile() -> list[list]:
    print("[base] loading", FREEDICT_TABFILE.name)
    entries = []
    for line in FREEDICT_TABFILE.read_text(encoding="utf-8").splitlines():
        if "\t" not in line or line.startswith("##"):
            continue
        head, defi = line.split("\t", 1)
        parts = head.split("|")
        entries.append([parts[0], parts[1:], defi])
    print(f"[base] {len(entries)} entries")
    return entries


# --- Stage 3: inflection variants -------------------------------------------
def apply_inflections(entries: list[list], lemma_forms: dict[str, set[str]]) -> None:
    added = 0
    for ent in entries:
        head, variants, _ = ent
        if " " in head or len(head) < 2:
            continue
        key = head[:-3].lower() if head.endswith("-se") else head.lower()
        forms = lemma_forms.get(key) or lemma_forms.get(head.lower())
        if not forms:
            continue
        exist = {f.lower() for f in [head] + variants}
        extra = sorted(
            f for f in forms
            if f.lower() != head.lower() and " " not in f and 1 < len(f) <= 25
            and f.lower() not in exist
        )[:400]
        if extra:
            ent[1] = variants + extra
            added += len(extra)
    print(f"[inflections] {added} variants")


# --- Stage 4: apostrophe elisions --------------------------------------------
def apply_elisions(entries: list[list]) -> int:
    added = 0
    for ent in entries:
        head, variants, defi = ent
        prefixes = VERB_ELISIONS if ">verb<" in defi else NOUN_ELISIONS
        all_forms = [head] + variants
        existing = {f.lower() for f in all_forms}
        by_prefix: dict[str, list[str]] = collections.defaultdict(list)
        seen: set[str] = set()
        for form in all_forms:
            fl = form.lower()
            if not form or "'" in form or len(form) > 14 or form[0] not in VOWELS:
                continue
            for p in prefixes:
                cand = p + form
                cl = cand.lower()
                if cl not in existing and cl not in seen and len(cand) <= 25:
                    seen.add(cl)
                    by_prefix[p].append(cand)
        fair: list[str] = []
        while len(fair) < 400:
            progressed = False
            for p in VERB_ELISIONS:
                bucket = by_prefix.get(p)
                if bucket:
                    fair.append(bucket.pop(0))
                    progressed = True
                    if len(fair) >= 400:
                        break
            if not progressed:
                break
        if fair:
            ent[1] = variants + fair
            added += len(fair)
    print(f"[elisions] {added} variants")
    return added


# --- Stage 5: accents ---------------------------------------------------------
def apply_accents(entries: list[list], soft_forms: set[str]) -> None:
    import unicodedata

    def strip_accents(s: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

    strip_map: dict[str, set[str]] = {}
    for w in soft_forms:
        s = strip_accents(w)
        if s != w:
            strip_map.setdefault(s, set()).add(w)

    added = 0
    for head, variants, _ in entries:
        forms = [head] + variants
        exist = {f.lower() for f in forms}
        extra: set[str] = set()
        for form in forms:
            if "'" in form or len(form) > 20 or len(form) < 3:
                continue
            fl = form.lower()
            sa = strip_accents(fl)
            if sa != fl:
                if sa not in exist:
                    extra.add(sa)
            else:
                for cand in strip_map.get(fl, ()):
                    extra.add(cand)
                    if len(extra) >= 12:
                        break
        extra = {e for e in extra if e.lower() not in exist}
        if extra:
            variants.extend(sorted(extra))
            added += len(extra)
    print(f"[accents] {added} variants")


# --- Stage 6: manual supplement ----------------------------------------------
SUPPLEMENT = [
    ("hi", ["n'hi", "l'hi", "m'hi", "t'hi", "s'hi"],
     ("pronom", "(locatiu) allí, ahí; hi ha: hay")),
    ("ho", ["l'ho", "m'ho", "t'ho", "s'ho", "n'ho"],
     ("pronom", "(neutre) lo; ho sé: lo sé")),
    ("en", ["n'en", "l'en", "m'en", "t'en", "s'en"],
     ("prep/pronom", "de, en; (pron.) de ello")),
    ("se", ["se'n", "s'en"], ("pronom", "se (reflexivo); se'n va: se va")),
    ("es", [], ("pronom", "se (reflexivo)")),
    ("ben", [], ("adverbi", "bien, muy")),
    ("prop", [], ("adverbi", "cerca; de prop: de cerca")),
    ("sobte", ["sobtes"], ("nom masculí", "susto; de sobte: de repente")),
    ("dintre", ["endintre"], ("adverbi", "dentro")),
    ("enmig", [], ("adverbi", "en medio (de)")),
    ("mas", ["masos", "masia", "masies"], ("nom masculí", "masía, casa de campo catalana")),
    ("del", [], ("contracció", "de + el")),
    ("dels", [], ("contracció", "de + els")),
    ("al", [], ("contracció", "a + el")),
    ("als", [], ("contracció", "a + els")),
    ("pel", [], ("contracció", "per + el")),
    ("pels", [], ("contracció", "per + els")),
    ("cal", [], ("verb", "hay que (cal fer: hay que hacer); ca l'Joan: casa de Joan")),
    ("lo", ["los"], ("article/pronom", "artículo masculino arcaico/regional; neutro: lo més")),
]

GAP_LEMMAS = {
    "buscar": ("verb", "buscar"),
    "exclamar": ("verb", "exclamar, decir con exclamación"),
    "toro": ("nom masculí", "toro"),
    "mirallet": ("nom masculí", "espejito (diminutivo de mirall)"),
}


def apply_supplement(entries: list[list], lemma_forms: dict[str, set[str]]) -> None:
    heads = {e[0].lower() for e in entries}
    for head, variants, (tag, gloss) in SUPPLEMENT:
        if head in heads:
            continue
        entries.append([head, list(variants), grammar(tag, gloss)])
    for lemma, (tag, gloss) in GAP_LEMMAS.items():
        if lemma in heads:
            continue
        variants = sorted(f for f in lemma_forms.get(lemma, set()) if f.lower() != lemma)[:80]
        entries.append([lemma, variants, grammar(tag, gloss)])
    print(f"[supplement] total entries now {len(entries)}")


# --- Stage 7: Apertium merge --------------------------------------------------
def parse_apertium(metadix_text: str) -> list[tuple[str, list[str], str]]:
    main = metadix_text[metadix_text.find('<section id="main"'):]
    pair_re = re.compile(r"<p>\s*<l>(.*?)</l>\s*<r>(.*?)</r>\s*</p>", re.S)
    par_re = re.compile(r'<par n="[^"]*"\s*/?>')
    tag_re = re.compile(r'<s n="([^"]+)"')

    def side(txt: str) -> tuple[str, list[str]]:
        cleaned = par_re.sub("", txt)
        return re.sub(r"<[^>]+>", "", cleaned).strip(), tag_re.findall(cleaned)

    pairs = []
    for e in re.findall(r"<e[^>]*>(.*?)</e>", main, re.S):
        m = pair_re.search(e)
        if not m:
            continue
        spa_lem, _ = side(m.group(1))
        cat_lem, cat_tags = side(m.group(2))
        if spa_lem and cat_lem:
            pairs.append((cat_lem, cat_tags, spa_lem))
    return pairs


def apply_apertium(entries: list[list], lemma_forms: dict[str, set[str]], soft_forms: set[str]) -> None:
    print("[apertium] parsing", APERTIUM_METADIX.name)
    pairs = parse_apertium(APERTIUM_METADIX.read_text(encoding="utf-8", errors="ignore"))
    heads = {e[0].lower() for e in entries}
    added = 0
    seen: set[str] = set()
    for cat_lem, cat_tags, spa_lem in pairs:
        rl = cat_lem.lower()
        pos = next((t for t in cat_tags if t in CONTENT_POS), None)
        if not pos or not rl or rl in heads or rl in seen:
            continue
        if {"np"} & set(cat_tags) or "top" in cat_tags:
            continue
        if " " in cat_lem or len(rl) < 2 or len(rl) > 30 or rl not in soft_forms:
            continue
        seen.add(rl)
        variants = sorted(f for f in lemma_forms.get(rl, set()) if f.lower() != rl)[:100]
        entries.append([cat_lem, variants, grammar(POS_LABEL[pos], spa_lem)])
        added += 1
    print(f"[apertium] {added} new entries")


# --- Stage 8: compile ----------------------------------------------------------
def write_tabfile(entries: list[list], path: pathlib.Path) -> None:
    lines = []
    for head, variants, defi in entries:
        hp = head + ("|" + "|".join(variants) if variants else "")
        lines.append(hp + "\t" + defi)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[tabfile] wrote {path.name} ({path.stat().st_size:,} bytes)")


def run_pyglossary(src: pathlib.Path, dst_dir: pathlib.Path) -> pathlib.Path:
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    pygl = shutil.which("pyglossary")
    if not pygl:
        sys.exit("pyglossary not found on PATH (pip install pyglossary)")
    subprocess.run(
        [pygl, str(src), str(dst_dir), "--read-format=Tabfile", "--write-format=Mobi",
         "--source-lang", SOURCE_LANG, "--target-lang", TARGET_LANG, "--no-interactive"],
        check=True,
    )
    return dst_dir / "OEBPS"


def patch_opf(oebps: pathlib.Path) -> None:
    opf = oebps / "content.opf"
    txt = opf.read_text(encoding="utf-8")
    txt = re.sub(r"<dc:Title>.*?</dc:Title>",
                 f"<dc:Title>{DICT_TITLE}</dc:Title>", txt, flags=re.S)
    opf.write_text(txt, encoding="utf-8")


def run_kindlegen(oebps: pathlib.Path, out: pathlib.Path) -> pathlib.Path:
    if not KINDLEGEN.exists():
        sys.exit(
            "kindlegen.exe not found. Download Amazon KindleGen v2.9 "
            "(search 'kindlegen_win32_v2_9 archive.org') and place it at "
            f"{KINDLEGEN}"
        )
    proc = subprocess.run(
        [str(KINDLEGEN), str(oebps / "content.opf"), "-gen_ff_mobi7",
         "-dont_append_source", "-o", out.name],
        cwd=str(oebps.parent),
        capture_output=True, text=True,
    )
    # kindlegen exits 1 when it compiles with warnings; only fail if no output
    if proc.returncode not in (0, 1):
        print(proc.stdout[-3000:])
        sys.exit(f"kindlegen failed with exit code {proc.returncode}")
    # kindlegen writes -o next to the source .opf
    produced = oebps / out.name
    if not produced.exists():
        print(proc.stdout[-3000:])
        sys.exit("kindlegen produced no output file")
    if produced != out:
        shutil.move(str(produced), str(out))
    print(f"[kindlegen] built {out} (exit {proc.returncode}: warnings ok)")
    return out


def verify_mobi(path: pathlib.Path) -> dict[str, str]:
    data = path.read_bytes()
    exth_off = next(m.start() for m in re.finditer(b"EXTH", data))
    count = struct.unpack(">I", data[exth_off + 8:exth_off + 12])[0]
    off = exth_off + 12
    fields: dict[int, str] = {}
    for _ in range(count):
        rtype = struct.unpack(">I", data[off:off + 4])[0]
        rlen = struct.unpack(">I", data[off + 4:off + 8])[0]
        if rtype in (105, 110, 524, 531, 532):
            fields[rtype] = data[off + 8:off + rlen].decode("utf-8", "ignore")[:20]
        off += rlen
    assert fields.get(110) == "REF008000", "missing dictionary flag REF008000"
    assert fields.get(524) == SOURCE_LANG and fields.get(532) == TARGET_LANG, "wrong languages"
    print(f"[verify] EXTH OK: {fields}")
    return {str(k): v for k, v in fields.items()}


# --- Main -----------------------------------------------------------------------
STAGES = {}


def stage(name):
    def deco(fn):
        STAGES[name] = fn
        return fn
    return deco


@stage("all")
def build_all(args: argparse.Namespace) -> None:
    lemma_forms, soft_forms = load_morphology()
    entries = load_base_tabfile()
    apply_inflections(entries, lemma_forms)
    apply_elisions(entries)
    apply_accents(entries, soft_forms)
    apply_supplement(entries, lemma_forms)
    apply_apertium(entries, lemma_forms, soft_forms)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tab = OUT_DIR / f"catalan-spanish-v{VERSION}.txt"
    write_tabfile(entries, tab)
    oebps = run_pyglossary(tab, OUT_DIR / "build")
    patch_opf(oebps)
    out = OUT_DIR / f"catalan-spanish-dictionary-v{VERSION}.mobi"
    run_kindlegen(oebps, out)
    verify_mobi(out)


@stage("mobi")
def build_mobi_only(args: argparse.Namespace) -> None:
    src = OUT_DIR / f"catalan-spanish-v{VERSION}.txt"
    oebps = run_pyglossary(src, OUT_DIR / "build")
    patch_opf(oebps)
    out = OUT_DIR / f"catalan-spanish-dictionary-v{VERSION}.mobi"
    run_kindlegen(oebps, out)
    verify_mobi(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=[*STAGES], default="all")
    args = ap.parse_args()
    STAGES[args.stage](args)


if __name__ == "__main__":
    main()
