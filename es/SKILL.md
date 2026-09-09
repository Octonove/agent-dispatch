---
name: agent-dispatch
description: "Regla siempre activa para cualquier cliente que pueda lanzar subagentes (Claude Code, Cursor, Antigravity…). Antes de delegar decide si hay que delegar —por defecto no—, después cuántos empezando por cero, cómo repartir el trabajo y qué modelo y esfuerzo lleva cada subagente: por el tipo de tarea, nunca por la importancia del proyecto. Lo mecánico (traducciones, listar, medir, ejecutar scripts) va a un modelo pequeño; el análisis acotado a uno medio; diseño, código, decisiones y la revisión final se quedan en el modelo de la sesión. Declara el reparto antes de lanzar y reporta el gasto medido después."
---

# Despacho de agentes — qué modelo corre cada subagente

Trabajas dentro de un cliente que puede lanzar subagentes (las herramientas `Agent` y `Workflow`
de Claude Code, los agentes en segundo plano de Cursor, o similares). Por defecto cada subagente
hereda el modelo que tienes seleccionado para la sesión, así que traducir a cuatro idiomas cuesta
lo mismo por token que una decisión de arquitectura. Esta regla lo arregla. Gobierna una sola
cosa: **el gasto en agentes**. Nunca cambia el modelo de la conversación.

Aplícala cada vez que un trabajo vaya a salir de la conversación. Aplícala en este orden.

## 0. ¿Hay que delegar? Por defecto, no

Delega solo si se cumple una de dos:

- **partes independientes** que de verdad corren a la vez y ahorran tiempo de reloj;
- **más lectura de la que cabe en un contexto** (docenas de ficheros, transcripciones,
  resultados largos).

Si no, hazlo en línea. Un subagente no ve esta conversación: cuesta su contexto entero más el
briefing que le escribes, y su respuesta hay que verificarla igual. Dos cosas no son nunca razón
para delegar: comprobar lo que un comando comprueba (`curl`, `grep`, leer un fichero), y pedir
una segunda opinión sobre algo que ya está verificado — donde hay evidencia directa, manda la
evidencia.

## 0b. ¿Cuántos? Empieza por cero

Cero es la respuesta normal: casi todo es trabajo en línea. Uno bien briefeado cubre casi todo lo
que sí merece delegarse. Varios, solo cuando cada uno tiene una parcela que ningún otro cubre, y
la nombras antes de lanzarlos. Si al escribir el reparto dos suenan parecidos, sobra uno. Una
flota no es rigor: es la misma respuesta pagada varias veces.

## 1. Reparte el trabajo y clasifica cada parte por TIPO

Escribe las subtareas. Clasifica cada una por la clase de trabajo que es — **nunca por lo
importante que sea el proyecto**. Tres niveles:

| Nivel | Qué es | Ejemplos |
|---|---|---|
| **Mecánica** | Sin juicio; el resultado está bien o mal y es fácil de comprobar | traducir cadenas fijas, listar ficheros, contar, medir tamaños, transcribir una salida literal, ejecutar un script ya escrito y reportar lo que imprime, comprobar que un JSON o un manifest parsea, extraer campos con formato fijo, formatear, renombrar |
| **Analítica acotada** | Razonar dentro de un marco claro que ha puesto otro | resumir un módulo, mapear dependencias, escribir tests a partir de una especificación clara, aplicar un cambio mecánico en muchos ficheros, comparar dos versiones de un texto, pasar un checklist |
| **Juicio** | Decidir, diseñar, o cualquier cosa que se entrega sin otra revisión detrás | arquitectura, escribir el código que decide cómo funciona algo, elegir entre opciones, sintetizar un informe, la revisión final que comprueba que todo encaja, lo que se publica o se manda a un cliente |

## 2. Asigna modelo y esfuerzo por nivel

| Nivel | Modelo | Esfuerzo |
|---|---|---|
| Mecánica | **pequeño** (p. ej. Haiku) | bajo |
| Analítica acotada | **medio** (p. ej. Sonnet) | medio |
| Juicio | **el modelo de la sesión** (p. ej. Fable 5.1, Opus) | alto |

Los nombres de modelo son ejemplos: usa los niveles que ofrezca tu cliente. Si dudas entre dos
niveles, el de abajo más una verificación del de arriba sale más barato que el de arriba a ciegas.

Si tu cliente no deja elegir modelo ni esfuerzo por subagente, no finjas que lo has hecho: aplica
todo lo demás (si delegar, cuántos, en qué orden, briefing, declarar, medir) y dilo en una línea.

## 3. Salvaguardas que no se negocian

1. **La revisión final y quien sintetiza nunca se abaratan.** El ahorro se toma en lo mecánico,
   jamás en lo que evita que un fallo se publique.
2. **Si un agente pequeño falla o devuelve algo dudoso, la tarea sube un nivel.** No se reintenta
   en el mismo modelo.
3. **Menos agentes.** Un revisor con un checklist claro vale más que tres vagos. Un traductor por
   idioma, no dos «por si acaso». Ningún agente cuyo único trabajo sea recomprobar la conclusión
   de otro. Los agentes mecánicos van en pipeline, no en barrera, salvo que el paso siguiente
   necesite todos sus resultados a la vez.
4. **Cada subagente recibe un briefing y un contrato de retorno.** No ve esta conversación, así
   que dile lo que necesita; y dile qué devolver: un veredicto, como mucho cinco hallazgos, rutas
   de fichero en vez de contenidos pegados.

## 4. Declara antes, mide después

Antes de lanzar, una línea que el usuario pueda leer:

```
Despacho: 9 agentes · 3 de sesión (diseño, código, revisión final) · 1 medio (tests) · 5 pequeños (4 traducciones, lint + tests)
```

Al terminar, reporta el gasto que devuelva la herramienta, separando pequeños y grandes. Si la
herramienta no da cifra, escribe **«sin medir»**. Nunca inventes un ahorro: sin cifra no hay
ahorro, solo la sensación de haberlo tenido.

## 5. La revisión final

El último agente, o tú en línea, es siempre de nivel juicio y comprueba que las partes encajan:
cada cadena que usa el código existe en todos los idiomas, los permisos coinciden con lo que el
código usa, los tests que corrió el agente mecánico son los que importan, nada se saltó en
silencio. Aquí se verifica, una vez y por alguien que sabe distinguir, el trabajo de los modelos
pequeños.

## Ejemplo trabajado: una extensión de Chrome pequeña

Prompt: *«Haz una extensión de Chrome pequeña que resalte los precios de cualquier página y los
convierta a euros. Popup con selector de moneda. Interfaz en inglés, traducida a español, francés,
alemán e italiano. Tests para la conversión.»*

| # | Subtarea | Nivel | Modelo · esfuerzo |
|---|---|---|---|
| 1 | Diseño: manifest v3, ficheros, permisos, cómo hablan el content script y el popup | juicio | modelo de sesión · alto |
| 2 | Escribir el código: content script, popup, service worker, módulo de conversión | juicio | modelo de sesión · alto |
| 3 | Escribir los tests de conversión a partir de la especificación | analítica acotada | medio · medio |
| 4–7 | Traducir `messages.json` a ES, FR, DE, IT (un agente por idioma) | mecánica | pequeño · bajo |
| 8 | Validar el manifest, pasar lint y los tests, reportar la salida literal | mecánica | pequeño · bajo |
| 9 | Revisión final: idiomas completos, permisos coherentes con el código, tests en verde | juicio | modelo de sesión · alto |

Sin esta regla: 9 agentes en el modelo de la sesión. Con ella: 3 en el modelo de la sesión, 1 en
el medio, 5 en el pequeño. La extensión es la misma; el juicio se quedó donde importa.

## De dónde sale

Esta regla es la sección 1G de **El Orquestador**, la carta gratuita de enrutado de
[Invokard](https://invokard.web.app). Si esa carta está cargada, la regla ya aplica y no necesitas
este fichero. Esta es la versión suelta para quien solo quiera el despacho.
