# Metodología de validación

La calidad del diccionario no se afirma, se mide. Este documento describe cómo se valida cada versión y los resultados obtenidos.

## Método

1. **Corpus**: se procesa el texto completo de obras en catalán (epub o txt), eliminando etiquetas HTML y material paratextual.
2. **Tokenización idéntica a Kindle**: minúsculas; el apóstrofe (tanto `'` ASCII como `’` U+2019) queda pegado a la palabra (`l'amic` es un token); se separan signos de puntuación.
3. **Lookup simulado**: cada token se busca contra el índice completo de formas del diccionario (lemas + todas las variantes `idx:iform`). Un token "resuelve" si existe alguna entrada que lo contenga.
4. **Cobertura** = tokens resueltos / tokens totales.

Este método es conservador: cuenta como fallo cualquier token sin entrada, incluidos nombres propios y palabras de otros idiomas dentro del texto.

## Resultados v1.0.0

| Obra | Época | Tokens | Cobertura |
|---|---|---|---|
| *Et vaig donar ulls i vas mirar les tenebres* — Irene Solà (epub) | 2023 | 51.547 | **92,5 %** |
| *L'auca del senyor Esteve* — Santiago Rusiñol (Project Gutenberg) | 1907 | 53.261 | 89,3 % |
| *Arrels mortes* (Project Gutenberg) | 1909 | 14.920 | 76,8 % |

## Análisis de los fallos

- **Prosa moderna (Solà)**: del 7,5 % restante, la mayoría son nombres propios de personajes y topónimos (*Bernadeta*, *Pernales*, *Vic*), fragmentos de diálogo en español (`y`, `los`, `yo`) y vocabulario dialectal muy local.
- **Clásicos**: los fallos dominantes son ortografía pre-normativa anterior a les Normes de Fabra de 1913/1917: `ab` (=amb), `y` (=i), `vehina` (=veïna), `aixís` (=així), enclíticos antiguos (`que'l`, `no's`, `se'n` con grafía antigua). Son formas que ningún diccionario moderno indexa y que solo justificarían una capa histórica específica.

## Verificación estructural

Además de cobertura, cada build verifica programáticamente:

1. Cabecera Palm `BOOK/MOBI`.
2. Registro EXTH presente con:
   - `110 = REF008000` (clasificación diccionario BISG)
   - `105 = Dictionaries`
   - `524/531 = ca`, `532 = es` (idiomas in/out del diccionario)
3. Presencia de `<idx:iform>` en el contenido compilado (muestreo de variantes conocidas: `vaig → anar`, `l'amic → amic`).
4. SHA-256 del artefacto final registrado en el release.

## Limitaciones conocidas

- Las locuciones verbales multi-palabra del diccionario Apertium llegan concatenadas en la fuente (`venirabajo`) y se descartan; no existe versión con espacios en su historial git (verificado hasta el commit fundacional de 2020).
- Libros con apóstrofe tipográfico U+2019: el Kindle normaliza ambos caracteres en la búsqueda; si apareciera algún fallo atribuible a esto, se puede regenerar el índice duplicando variantes con U+2019.
