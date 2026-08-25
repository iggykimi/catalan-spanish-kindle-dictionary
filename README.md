# Diccionario catalán–español para Kindle — gratis y sin registro

[![Descargar](https://img.shields.io/github/v/release/iggykimi/catalan-spanish-kindle-dictionary?label=descargar&sort=semver)](../../releases/latest)
[![Licencia](https://img.shields.io/badge/licencia-GPL--3.0-blue.svg)](LICENSE)
[![Formato](https://img.shields.io/badge/formato-dicci%C3%B3nario%20Kindle%20(.mobi)-orange)](#instalaci%C3%B3n-en-4-pasos)

**Diccionario bilingüe catalán → español nativo para Amazon Kindle.** 54.578 palabras y más de un millón de formas reconocibles: conjugaciones verbales completas, plurales, apóstrofes (`l'amic`, `s'ha`) y acentos (`bèsties`). Gratuito, sin DRM y sin registro.

## 📥 Descarga

**→ [DESCARGAR EL DICCIONARIO (v1.0.0)](../../releases/latest/download/catalan-spanish-dictionary-v1.0.0.mobi) ←**

Archivo `.mobi` de 6,3 MB. Compatible con todos los Kindle (Paperwhite, Oasis, Scribe, Basic…) y con KOReader.

## Instalación en 4 pasos

1. **Descarga** el archivo del enlace de arriba.
2. **Conecta el Kindle** al ordenador con el cable USB.
3. **Copia** el archivo `.mobi` dentro de la carpeta `documents\dictionaries\` del Kindle (si no existe, créala).
4. **Expulsa** el Kindle con seguridad y, en el dispositivo, ve a *Configuración → Opciones de dispositivo → Idioma y diccionarios → Diccionarios → Catalán* y selecciónalo.

Ya está. Abre un libro en catalán, mantén pulsada una palabra y verás la traducción al español:

| Si pulsas... | Verás... |
|---|---|
| `vaig`, `vam`, `anem` | anar (ir) |
| `sóc`, `eren` | ser |
| `tinc`, `tingut` | tenir |
| `parlaven`, `dient` | parlar, dir |
| `l'amic`, `s'ha` | amic, haver |

---

## Qué incluye

- **Conjugaciones completas**: pulsa cualquier forma verbal (`tindria`, `havent`, `parlessin`) y salta al infinitivo traducido.
- **Plurales y femeninos**: `nen → nens/nena`, `casa → cases`.
- **Apóstrofes inteligentes**: `l'amic`, `d'ull`, `m'anava`, `t'estimo` resuelven a su lema.
- **Acentos**: da igual pulsar `bestia` que `bèstia`.
- **Contracciones y pronombres débiles**: `del`, `pels`, `hi`, `ho`, `en`, `ne`, `cal`.

## Fuentes de datos

El diccionario combina tres proyectos libres, cada uno aportando lo que el otro no tiene:

| Fuente | Aporta | Licencia |
|---|---|---|
| [FreeDict / WikDict](https://freedict.org/) | Base bilingüe ca-es (27.000 lemas) | CC BY-SA 3.0 / GPL |
| [Softcatalà · catalan-dict-tools](https://github.com/Softcatala/catalan-dict-tools) | Morfología catalana (~900.000 formas) | LGPL 2.1 / GPL 2 |
| [Apertium spa-cat](https://github.com/apertium/apertium-spa-cat) | +27.000 pares técnicos y cultos | GPL 2 |

Detalles completos en [NOTICE.md](NOTICE.md).

## Validación

Cobertura medida sobre libros reales, token a token ([metodología](docs/validacion.md)):

| Obra | Época | Cobertura |
|---|---|---|
| *Et vaig donar ulls i vas mirar les tenebres* (Irene Solà) | 2023 | **92,5 %** |
| *L'auca del senyor Esteve* (Rusiñol) | 1907 | 89,3 % |
| *Arrels mortes* | 1909 | 76,8 % |

Los fallos en clásicos son ortografía anterior a Fabra (`ab`, `y`, `vehina`); en prosa moderna, casi todo lo restante son nombres propios.

## Para desarrolladores

Todo el proceso está automatizado en [`pipeline/build.py`](pipeline/build.py): cruza las fuentes, genera las variantes morfológicas y compila el `.mobi` verificando el formato diccionario (EXTH `REF008000`, ca→es) tras cada build.

```bash
cd pipeline
pip install -r requirements.txt
python build.py                # pipeline completo (~5 min)
python build.py --stage mobi   # solo recompilar
```

Requisitos: Python 3.10+, pyglossary, y el binario [KindleGen v2.9](https://www.amazon.com/gp/feature.html?docId=1000765211) colocado en la ruta indicada al inicio del script (no se redistribuye por su licencia). El método es agnóstico al contenido: sirve para construir diccionarios para otros pares de idiomas combinando un StarDict bilingüe libre + un diccionario morfológico del idioma origen.

## Contribuir

- **¿Una palabra no resuelve?** Abre una issue con la palabra y la frase; los huecos reales entran en el suplemento.
- **Correcciones** de traducciones (provienen de Wiktionary/Apertium) o nuevas fuentes bilingües libres.
- **Otros idiomas**: si haces fork para otro par, compártelo.

## Licencia

Código y obra resultante bajo [GPL-3.0](LICENSE). Los datos incorporados conservan sus licencias originales ([NOTICE.md](NOTICE.md)). Proyecto independiente, sin afiliación con Amazon.
