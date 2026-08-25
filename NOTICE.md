# Avisos de licencias y fuentes (NOTICE)

Este proyecto combina datos de terceros. Cada fuente conserva su licencia original; el resultado compilado se distribuye bajo GPL-3.0 en cumplimiento de las licencias share-alike de los datos incorporados.

## 1. FreeDict cat-spa / WikDict

- **Qué aporta**: base bilingüe catalán→español (~27.000 lemas con definición).
- **Origen**: https://freedict.org/ — paquete `cat-spa` (generado por WikDict, https://www.wikdict.com/, a partir de Wiktionary vía DBnary).
- **Licencia**: Creative Commons Attribution-ShareAlike 3.0 Unported (declarada en el propio fichero `.ifo`) y GPL (packaging FreeDict). Ver `COPYING` del paquete original.

## 2. Softcatalà · catalan-dict-tools

- **Qué aporta**: morfología completa del catalán (`diccionari.txt`, ~900.000 formas inflexivas): conjugación verbal, plurales, femeninos.
- **Origen**: https://github.com/Softcatala/catalan-dict-tools — fichero `resultats/lt/diccionari.txt`.
- **Licencia**: dual LGPL 2.1 / GPL 2 (según README del proyecto). Este derivado se distribuye bajo GPL-3.0.

## 3. Apertium spa-cat

- **Qué aporta**: pares bilingües adicionales español↔catalán (vocabulario técnico y culto, ~27.000 entradas tras filtrado).
- **Origen**: https://github.com/apertium/apertium-spa-cat — fichero `apertium-spa-cat.spa-cat.metadix`.
- **Licencia**: GPL 2 (fichero `COPYING` del repositorio).

## 4. Herramientas de compilación (no redistribuidas)

- **pyglossary** — https://github.com/ilius/pyglossary — GPL-3.0. Se instala por pip; no se incluye en este repo.
- **Amazon KindleGen v2.9** — herramienta propietaria de Amazon usada solo localmente para compilar el `.mobi`. **No se redistribuye** con este proyecto: cada usuario debe descargarla por su cuenta. Este proyecto no está afiliado a Amazon.

## Suplemento manual

Las entradas de contracciones (`del`, `pels`…), pronombres débiles (`hi`, `ho`, `en`, `ne`) y lemas puntuales añadidos como parche se publican aquí bajo la misma GPL-3.0 del proyecto.
