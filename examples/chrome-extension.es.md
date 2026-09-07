# Ejemplo trabajado: una extensión de Chrome pequeña, despachada

Es el ejemplo que usa la skill, paso a paso: qué pidió el usuario, cómo se repartió el trabajo,
qué modelo recibió cada subagente y por qué, qué se le dijo a cada uno y qué comprobó la revisión
final. El número de agentes es real para este plan; el gasto en tokens es el que reporte tu
herramienta en tu ejecución: la skill nunca lo rellena por ti.

## El prompt

> Haz una extensión de Chrome pequeña que resalte los precios de cualquier página y los convierta
> a euros. Popup con selector de moneda. Interfaz en inglés, traducida a español, francés, alemán
> e italiano. Tests para la conversión.

## Paso 0 — ¿hay que delegar?

Sí, por el primer motivo: hay partes independientes (cuatro traducciones, un fichero de tests, una
pasada de lint y tests) que pueden correr en paralelo y no necesitan ver la conversación. Diseño
y código podrían hacerse en línea; en este plan se delegan porque el usuario quiere medir la
ejecución.

## Paso 1 — el reparto, clasificado por tipo

| # | Subtarea | Tipo | Por qué ese tipo |
|---|---|---|---|
| 1 | Diseño: manifest v3, estructura de ficheros, permisos (`activeTab`, `storage`), cómo se pasan el content script y el popup la moneda elegida | juicio | todas las decisiones posteriores dependen de esto |
| 2 | Escribir el código: content script (encontrar precios, envolverlos), popup (selector, guarda en `chrome.storage`), service worker, `convert.js` | juicio | código que decide cómo funciona la cosa |
| 3 | Escribir `convert.test.js` a partir de la especificación de `convert.js` (formatos de entrada, redondeo, moneda desconocida) | analítica acotada | el marco está puesto; el trabajo es dentro de él |
| 4–7 | Traducir `_locales/en/messages.json` a ES, FR, DE, IT — un agente por idioma | mecánica | cadenas fijas, resultado fácil de comprobar |
| 8 | Validar `manifest.json`, pasar `npm run lint` y `npm test`, reportar la salida literal | mecánica | ejecutar y reportar, sin juicio |
| 9 | Revisión final: cada clave de `en` existe en los cuatro idiomas, los permisos del manifest coinciden con lo que llama el código, tests en verde, nada saltado | juicio | después de esto se entrega |

## Paso 2 — modelo y esfuerzo por subtarea

| Subtareas | Modelo · esfuerzo |
|---|---|
| 1, 2, 9 | modelo de la sesión (Fable 5.1 en mi caso) · alto |
| 3 | Sonnet · medio |
| 4, 5, 6, 7, 8 | Haiku · bajo |

## Paso 4 — la declaración, antes de lanzar

```
Despacho: 9 agentes · 3 de sesión (diseño, código, revisión final) · 1 medio (tests) · 5 pequeños (4 traducciones, lint + tests)
```

## Qué se le dice a cada agente (briefing + contrato de retorno)

Cada subagente arranca con el contexto vacío. Recibe las rutas que necesita, la especificación y
un contrato de retorno. Ejemplos:

**Traductor (pequeño, ×4)**
> Traduce los valores de `_locales/en/messages.json` al francés. Conserva todas las claves,
> no toques los marcadores como `$AMOUNT$`, mantén la misma forma del JSON. Escribe el resultado
> en `_locales/fr/messages.json`. Devuelve: la ruta escrita, el número de claves y las cadenas de
> las que no estés seguro (máximo 5).

**Lint + tests (pequeño)**
> Ejecuta `npm run lint` y `npm test` en la raíz del repo. No arregles nada. Devuelve: códigos de
> salida, las últimas 30 líneas de cada salida tal cual, y la ruta de cualquier fichero que las
> herramientas señalen.

**Tests desde la especificación (medio)**
> `src/convert.js` exporta `convert(amount, from, to, rates)`. Especificación: los importes pueden
> llevar separador de miles y coma o punto decimal; el resultado se redondea a 2 decimales; una
> moneda desconocida lanza error. Escribe `test/convert.test.js` cubriendo cada regla y dos casos
> límite. Devuelve: la ruta y la lista de casos, uno por línea.

**Revisión final (modelo de sesión)**
> Comprueba que la extensión encaja: cada clave de `_locales/en/messages.json` existe en `es`,
> `fr`, `de`, `it`; cada permiso de `manifest.json` lo usa el código y nada de lo que llama el
> código se queda sin permiso; los tests que pasó el agente de lint son los de `test/`; reporta
> cualquier cosa saltada. Devuelve: VEREDICTO pasa/no pasa, como mucho 5 hallazgos con fichero y
> línea, una acción SIGUIENTE.

## Paso 5 — la revisión final

El revisor es el único agente que ve el conjunto a la vez. En este plan es donde se verifica el
trabajo de los cinco agentes pequeños, por alguien que distingue una clave que falta de una mala
traducción. Nunca se abarata: el ahorro está en los traductores y en el que pasa los tests, no
aquí.

## Después de la ejecución — medir

Reporta el gasto que devuelva la herramienta, separando pequeños y grandes. Si no da ninguno,
escribe «sin medir». La línea de la skill al final de una ejecución es así:

```
Gasto: 5 pequeños · 1 medio · 3 de sesión — cifras tal como las reporta la herramienta, o «sin medir»
```

Sin la skill, los mismos nueve agentes corren en el modelo de la sesión. Con ella, cinco no. La
extensión es la misma.
