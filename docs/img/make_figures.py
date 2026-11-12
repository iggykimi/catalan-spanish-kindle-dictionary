"""Generate the README figures (light and dark SVG variants).

Stdlib only. Run from anywhere:  python docs/img/make_figures.py
Coverage numbers come from docs/validacion.md; update both together.
"""

import pathlib

OUT = pathlib.Path(__file__).parent
FONT = "system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

THEMES = {
    "light": {
        "text": "#1f2328",
        "muted": "#59636e",
        "line": "#d1d9e0",
        "accent": "#1f8a70",
        "warm": "#bf8700",
    },
    "dark": {
        "text": "#e6edf3",
        "muted": "#9198a1",
        "line": "#3d444d",
        "accent": "#22d3a7",
        "warm": "#e3b341",
    },
}

# (title, subtitle, tokens, coverage %) — docs/validacion.md, v1.0.0
COVERAGE = [
    (
        "Et vaig donar ulls i vas mirar les tenebres",
        "Irene Solà · prosa contemporánea · 2023",
        "51.547",
        92.5,
    ),
    ("L'auca del senyor Esteve", "Santiago Rusiñol · clásico · 1907", "53.261", 89.3),
    ("Arrels mortes", "pre-normativo · 1909", "14.920", 76.8),
]

# Original text written for this figure (not from any book).
PROSE = [
    "El carrer encara feia olor de pa i de",
    "pluja, i el forn tenia el vidre entelat.",
    "Una mica abans que sonessin les campanes,",
    "vaig creuar la plaça fins al cantó on",
    "m'esperava l'amic de sempre, amb les",
    "mans a les butxaques i un llibre sota",
    "el braç. Feia anys que no ens vèiem.",
]
HIGHLIGHT_LINE = 3  # the line that starts with "vaig"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w: int, h: int, label: str, body: list[str]) -> str:
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}" '
        f'font-family="{FONT}">'
    )
    return "\n".join([head, *body, "</svg>", ""])


def text(x, y, s, c, size=13, weight=None, anchor=None) -> str:
    extra = f' font-weight="{weight}"' if weight else ""
    extra += f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'  <text x="{x}" y="{y}" font-size="{size}" fill="{c}"{extra}>{esc(s)}</text>'
    )


def bar(x, y, w, h, r, fill) -> str:
    """Bar square at the baseline, rounded at the data end."""
    return (
        f'  <path d="M{x},{y} h{w - r} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r} '
        f'a{r},{r} 0 0 1 -{r},{r} h-{w - r} z" fill="{fill}"/>'
    )


def coverage(t: dict) -> str:
    w, h = 760, 250
    x0, x1 = 340, 690  # 0 % and 100 %
    scale = (x1 - x0) / 100
    b = [
        text(8, 24, "Cobertura sobre obras reales", t["text"], 16, 600),
        text(
            8,
            44,
            "Tokens que el diccionario resuelve, simulando la búsqueda del Kindle",
            t["muted"],
            12,
        ),
    ]
    top, row, bh = 68, 50, 16
    bottom = top + row * len(COVERAGE)
    for pct in (0, 25, 50, 75, 100):
        x = x0 + pct * scale
        b.append(
            f'  <line x1="{x}" y1="{top - 6}" x2="{x}" y2="{bottom - 10}" stroke="{t["line"]}" stroke-width="1"/>'
        )
        b.append(text(x, bottom + 8, f"{pct} %", t["muted"], 12, anchor="middle"))
    for i, (title, sub, tokens, pct) in enumerate(COVERAGE):
        y = top + i * row
        b.append(text(8, y + 12, title, t["text"]))
        b.append(text(8, y + 30, sub, t["muted"], 12))
        b.append(
            f"  <g><title>{esc(title)}: {str(pct).replace('.', ',')} % de {tokens} tokens</title>"
        )
        b.append(bar(x0, y, round(pct * scale, 1), bh, 4, t["accent"]))
        b.append("  </g>")
        b.append(
            text(
                752,
                y + 13,
                f"{str(pct).replace('.', ',')} %",
                t["text"],
                13,
                600,
                "end",
            )
        )
    return svg(
        w,
        h,
        "Cobertura del diccionario sobre tres obras reales: 92,5 %, 89,3 % y 76,8 %",
        b,
    )


def lookup(t: dict) -> str:
    w, h = 760, 460
    b = [
        # Device: bezel and screen.
        f'  <rect x="40" y="12" width="340" height="436" rx="28" fill="none" stroke="{t["line"]}" stroke-width="2"/>',
        f'  <rect x="60" y="36" width="300" height="380" rx="6" fill="none" stroke="{t["line"]}" stroke-width="1"/>',
    ]
    lx, ly, lh = 76, 72, 22
    hy = ly + HIGHLIGHT_LINE * lh
    b.append(
        f'  <rect x="{lx - 3}" y="{hy - 15}" width="30" height="20" rx="3" '
        f'fill="{t["warm"]}" fill-opacity="0.18" stroke="{t["warm"]}" stroke-width="1.5"/>'
    )
    for i, line in enumerate(PROSE):
        b.append(text(lx, ly + i * lh, line, t["text"]))

    # Dictionary popup. Entry text is the real v1.0.0 entry for "anar".
    px, py, pw, ph = 68, 230, 284, 162
    b += [
        f'  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="none" stroke="{t["line"]}" stroke-width="1.5"/>',
        text(px + 16, py + 22, "Diccionari català → español", t["muted"], 12),
        f'  <line x1="{px}" y1="{py + 34}" x2="{px + pw}" y2="{py + 34}" stroke="{t["line"]}" stroke-width="1"/>',
        text(px + 16, py + 64, "anar", t["text"], 16, 600),
        text(px + 58, py + 64, "/aˈna/ · verb", t["muted"], 12),
        f'  <rect x="{px + pw - 96}" y="{py + 47}" width="82" height="24" rx="6" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>',
        text(px + pw - 55, py + 63, "vaig → anar", t["text"], 12, anchor="middle"),
        text(px + 16, py + 92, "Moure's d'un lloc a un altre.", t["muted"], 12),
        text(px + 16, py + 118, "1. ir", t["text"], 13, 600),
        text(px + 16, py + 140, "2. andar", t["text"], 13, 600),
    ]

    # Explanation on the right; each step sits on the row it describes.
    sx = 452
    steps = [
        (hy - 5, "Mantienes pulsada «vaig»", "una forma conjugada, no el infinitivo"),
        (
            py + 59,
            "El índice de formas la lleva al lema",
            "vaig → anar, entre 1,1 millones de formas",
        ),
        (py + 129, "Y ves la traducción al español", "sin salir del libro"),
    ]
    b.append(text(420, 48, "Qué hace el diccionario", t["text"], 16, 600))
    for n, (cy, label, sub) in enumerate(steps, 1):
        b += [
            f'  <line x1="388" y1="{cy}" x2="420" y2="{cy}" stroke="{t["line"]}" stroke-width="1" stroke-dasharray="3 3"/>',
            f'  <circle cx="432" cy="{cy}" r="11" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>',
            text(432, cy + 4, str(n), t["text"], 12, 600, "middle"),
            text(sx, cy + 4, label, t["text"]),
            text(sx, cy + 22, sub, t["muted"], 12),
        ]
    return svg(
        w,
        h,
        "Pantalla esquemática de un Kindle: al pulsar «vaig» aparece la entrada «anar», traducida como ir, andar",
        b,
    )


def main() -> None:
    for name, build in (("cobertura", coverage), ("lookup", lookup)):
        for mode, theme in THEMES.items():
            (OUT / f"{name}-{mode}.svg").write_text(
                build(theme), encoding="utf-8", newline="\n"
            )


if __name__ == "__main__":
    main()
