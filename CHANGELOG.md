# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), versionado con [SemVer](https://semver.org/lang/es/).

## [1.0.0] - 2026-08-25

Primera versión pública.

### Añadido
- Diccionario catalán→español compilado para Kindle (`.mobi`, 6,3 MB): 54.578 lemas, ~1.100.000 formas indexadas.
- Conjugación verbal completa para ~6.300 verbos (presente, imperfecto, futuro, condicional, subjuntivo, participio, gerundio) vía morfología de Softcatalà.
- Elisión con apóstrofe por categoría gramatical: verbos reciben clíticos `l' d' n' s' m' t'`; nombres solo artículo `l'`.
- Tolerancia a acentos bidireccional validada contra las formas reales del diccionario Softcatalà.
- Contracciones (`del`, `dels`, `al`, `als`, `pel`, `pels`, `cal`) y pronombres débiles (`hi`, `ho`, `en`, `ne`) con sus combinaciones clíticas.
- Fusión filtrada del diccionario bilingüe Apertium spa-cat (+27.368 lemas técnicos/cultos).
- Pipeline reproducible (`pipeline/build.py`) con verificación programática del formato diccionario (EXTH: REF008000, ca→es).
- Validación sobre tres obras reales (moderna y clásicas) documentada en `docs/validacion.md`.

[1.0.0]: https://github.com/iggykimi/catalan-spanish-kindle-dictionary/releases/tag/v1.0.0
