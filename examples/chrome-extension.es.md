# Ejemplo trabajado: una extensión de Chrome pequeña, despachada

Es el ejemplo que usa la skill, paso a paso: qué subtareas se quedan en línea y por qué, cuáles
se delegan y a qué modelo, qué se le dice a cada agente delegado y qué comprueba la revisión
final. El número de agentes es el del plan; el gasto en tokens es el que reporte tu cliente en tu
ejecución. La skill nunca lo rellena por ti.

## El prompt

> Haz una extensión de Chrome pequeña que resalte los precios de cualquier página y los convierta
> a euros. Popup con selector de moneda. Interfaz en inglés, traducida a español, francés, alemán
> e italiano. Tests para la conversión.

## Paso 1 — ¿hay que delegar?

En parte. Diseño y código son una misma cadena: el código depende del diseño y los dos son
juicio, así que se quedan en línea en el modelo de la sesión. Cuando el código existe, hay cinco
partes independientes que pueden correr a la vez: los tests de conversión y las cuatro
traducciones. Lint y tests son un comando, y lo ejecuta la propia sesión: un comando que
comprueba algo nunca es razón para delegar.

## Paso 2 — ¿cuántos?

Cinco, cada uno con su parcela: un fichero de tests y un idioma por traductor. Ni un segundo
revisor ni un traductor «por si acaso».

## Paso 3 — el reparto, clasificado por tipo

| # | Subtarea | Tipo | Dónde corre | Por qué |
|---|---|---|---|---|
| 1 | Diseño: manifest v3, estructura de ficheros, permisos (`activeTab`, `storage`), cómo se pasan el content script y el popup la moneda elegida | juicio | en línea | todas las decisiones posteriores dependen de esto |
| 2 | Código: content script (encontrar precios, envolverlos), popup (selector, guarda en `chrome.storage`), service worker, `convert.js` | juicio | en línea | código que decide cómo funciona la cosa |
| 3 | `test/convert.test.js` a partir de la especificación de `convert.js` | analítica acotada | 1 agente | el marco está puesto; corre mientras corren las traducciones |
| 4–7 | Traducir `_locales/en/messages.json` a ES, FR, DE, IT | mecánica | 4 agentes, uno por idioma | cadenas fijas, resultado fácil de comprobar |
| 8 | Validar `manifest.json`, pasar `npm run lint` y `npm test` | mecánica | en línea | lo comprueba un comando y la salida es corta |
| 9 | Revisión final: idiomas completos, permisos coherentes con el código, tests en verde, nada saltado | juicio | en línea | después de esto se entrega |

## Paso 4 — modelo y esfuerzo

| Subtareas | Modelo · esfuerzo | Llamada a `Agent` en Claude Code |
|---|---|---|
| 1, 2, 8, 9 | modelo de la sesión, en línea | ninguna |
| 3 | medio · medio | `model: "sonnet"`, `effort: "medium"` |
| 4–7 | pequeño · bajo | `model: "haiku"`, `effort: "low"` |

## Paso 5 — salvaguardas y tope

- Una ronda de corrección tras la revisión final. Un hallazgo que siga abierto después se aparca
  como deuda o se rechaza con motivo; no se abre una segunda ronda.
- Un traductor que rompe un marcador recibe su único reintento en el modelo medio, no otra pasada
  en el pequeño. Si también falla, ese idioma se hace en línea.

## Paso 6 — la declaración, antes de lanzar

```
Despacho: 5 agentes · 1 medio (tests) · 4 pequeños (traducciones) · en línea: diseño, código, lint + tests, revisión final · tope: 1 ronda de corrección
```

## Qué se le dice a cada agente delegado

Cada subagente arranca con el contexto vacío. Su encargo lleva las seis cosas que pide la skill:
objetivo, contexto, restricciones, foco de revisión, salida y criterio de terminado.

**Traductor (pequeño, ×4; se muestra el francés)**

> - **Objetivo:** traduce los valores de `_locales/en/messages.json` al francés.
> - **Contexto:** cadenas de la interfaz de una extensión de Chrome; el código las lee por clave, y
>   los marcadores como `$AMOUNT$` se rellenan al ejecutar.
> - **Restricciones:** no cambies claves, marcadores ni la forma del JSON; escribe solo
>   `_locales/fr/messages.json`.
> - **Foco de revisión:** quien revise comparará el conjunto de claves y los marcadores con `en`.
> - **Salida:** la ruta escrita, el número de claves y como mucho 5 cadenas de las que no estés
>   seguro.
> - **Terminado:** el fichero parsea como JSON y tiene exactamente las claves de `en`.

**Tests desde la especificación (medio)**

> - **Objetivo:** escribe `test/convert.test.js` para `src/convert.js`.
> - **Contexto:** `convert(amount, from, to, rates)`. Los importes pueden llevar separador de miles
>   y coma o punto decimal; el resultado se redondea a 2 decimales; una moneda desconocida lanza
>   error.
> - **Restricciones:** no edites `src/` ni añadas dependencias.
> - **Foco de revisión:** un test por regla más dos casos límite; ningún test que solo repita el
>   código.
> - **Salida:** la ruta y la lista de casos, uno por línea.
> - **Terminado:** `npm test` ejecuta el fichero; los tests que fallen se reportan, no se arreglan.

## Paso 7 — la revisión final, en línea

Cada clave de `_locales/en/messages.json` existe en `es`, `fr`, `de` e `it` con los mismos
marcadores; cada permiso de `manifest.json` lo usa el código y nada de lo que llama el código se
queda sin permiso; los tests que se pasaron son los de `test/`; nada se saltó. El resultado es un
veredicto (pasa o no pasa), como mucho 5 hallazgos con fichero y línea, y una acción siguiente.
Aquí se verifica, una vez y por alguien que distingue una clave que falta de una mala traducción,
el trabajo de los cinco agentes.

## Después de la ejecución — medir

Reporta el gasto por nivel tal como lo devuelva el cliente. En Claude Code, el resultado de cada
subagente trae su recuento de tokens, y `/usage` muestra el uso por modelo. Si no hay cifra,
escribe «sin medir»:

```
Gasto: 1 medio · 4 pequeños — tokens tal como los reporta el cliente, o «sin medir»
```

El plan no promete ningún ahorro. La línea de después de la ejecución es la única cifra que
cuenta.
