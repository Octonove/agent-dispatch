# Agent Dispatch — qué modelo corre cada subagente

[![license](https://img.shields.io/github/license/Octonove/agent-dispatch)](LICENSE)
[![skill](https://img.shields.io/badge/skill-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20cualquier%20cliente-1E3A5F)](es/SKILL.md)
[![english](https://img.shields.io/badge/read%20in-english-b85f2c)](README.md)

Una skill gratuita y suelta que evita que todos tus subagentes corran con el modelo más grande.

Por defecto, Claude Code le pasa a cada subagente el modelo que tienes seleccionado para la
sesión. Así que cuando una tarea se reparte en nueve agentes, los nueve salen en Fable 5.1 (u
Opus, o el que tengas puesto): los cuatro que traducen un `messages.json` cuestan lo mismo por
token que el que diseña la arquitectura. Esta skill hace el reparto explícito antes de lanzar
nada: **el modelo se elige por el tipo de tarea, nunca por la importancia del proyecto.**

![Demo de Agent Dispatch](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/demo.gif)

<!-- invokard-coffee -->
**&#9749; Si esto te ahorra tiempo, inv&iacute;tame a un caf&eacute;.** [![Inv&iacute;tame a un caf&eacute; con PayPal](https://img.shields.io/badge/PayPal-Inv%C3%ADtame%20a%20un%20caf%C3%A9-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?business=stradoxx%40gmail.com&no_recurring=0&currency_code=EUR&item_name=Support%20agent%20dispatch)

O en USDC. Env&iacute;a **solo USDC** y **solo por la red indicada**; por otra red se pierde y no hay forma de recuperarlo.

| Red | Direcci&oacute;n USDC |
|---|---|
| **Solana** | `5n6Gfosk7SdwbvdtE9xiLWpcGPBBBGDZYRfAkWyCk86g` |
| **Ethereum** (ERC-20) | `0xe176866f9d7fdb498e0d4a983d3e34d84dcd6bfc` |

## La regla en una tabla

| Tipo de tarea | Ejemplos | Modelo · esfuerzo |
|---|---|---|
| **Mecánica** | traducir cadenas fijas, listar, contar, medir, ejecutar un script y reportar la salida, comprobar que un manifest parsea | **pequeño** (p. ej. Haiku) · bajo |
| **Analítica acotada** | resumir un módulo, mapear dependencias, escribir tests a partir de una especificación clara, un cambio mecánico en muchos ficheros | **medio** (p. ej. Sonnet) · medio |
| **Juicio** | arquitectura, escribir el código que decide cómo funciona algo, elegir entre opciones, la revisión final, lo que se entrega | **el modelo de la sesión** (p. ej. Fable 5.1, Opus) · alto |

Antes de todo eso hace la pregunta barata: **¿hay que delegar, y cuántos?** Por defecto no, y la
cuenta empieza en cero — casi todo es trabajo en línea.

Más cuatro salvaguardas que la skill impone: la revisión final nunca se abarata; un agente
pequeño que falla sube la tarea de nivel en vez de reintentarse; menos agentes valen más que más
agentes, y ninguno existe solo para recomprobar la conclusión de otro; y cada ejecución **declara
su reparto antes de lanzar y reporta el gasto medido después**, o dice «sin medir». Nada de
ahorros inventados.

## Ejemplo trabajado: una extensión de Chrome pequeña

> *Haz una extensión de Chrome pequeña que resalte los precios de cualquier página y los
> convierta a euros. Popup con selector de moneda. Interfaz en inglés, traducida a español,
> francés, alemán e italiano. Tests para la conversión.*

![Despacho del ejemplo de la extensión de Chrome](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/example-chrome-extension.es.png)

| # | Subtarea | Modelo · esfuerzo |
|---|---|---|
| 1 | Diseño: manifest v3, ficheros, permisos, cómo hablan el content script y el popup | modelo de sesión · alto |
| 2 | Escribir el código: content script, popup, service worker, módulo de conversión | modelo de sesión · alto |
| 3 | Escribir los tests de conversión a partir de la especificación | medio · medio |
| 4–7 | Traducir `messages.json` a ES, FR, DE, IT — un agente por idioma | pequeño · bajo |
| 8 | Validar el manifest, pasar lint y los tests, reportar la salida literal | pequeño · bajo |
| 9 | Revisión final: idiomas completos, permisos coherentes con el código, tests en verde | modelo de sesión · alto |

Sin la skill: 9 agentes en el modelo de la sesión. Con ella: **3 en el modelo de la sesión, 1 en
el medio, 5 en el pequeño.** La misma extensión. El juicio se quedó donde importa. El recorrido
completo, con el briefing que recibe cada agente, está en
[`examples/chrome-extension.es.md`](examples/chrome-extension.es.md).

## Instalación

**Claude Code** — como skill global (aplica en todos los proyectos):

```bash
mkdir -p ~/.claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md -o ~/.claude/skills/agent-dispatch/SKILL.md
```

O por proyecto: el mismo fichero en `.claude/skills/agent-dispatch/SKILL.md`. Versión en inglés:
[`SKILL.md`](SKILL.md). Claude Code carga las skills solo; la descripción del frontmatter es lo
que hace que aplique cada vez que hay subagentes sobre la mesa.

**Cursor** — copia el cuerpo de `SKILL.md` en una regla (`.cursor/rules/agent-dispatch.mdc`)
con `alwaysApply: true`.

**Cualquier otro cliente** — pega el cuerpo de `SKILL.md` en el system prompt o en las
instrucciones del proyecto. Si el cliente no permite elegir modelo por subagente, la skill lo dice
y aplica el resto (si delegar, cuántos, briefing, declarar, medir).

## Qué te da y qué no

- Te da una línea como `Despacho: 9 agentes · 3 de sesión · 1 medio · 5 pequeños` antes de que
  corra nada, y el gasto que reporte la herramienta al terminar.
- **No** te da una cifra de ahorro. No puede medir lo que tu herramienta no reporta, y se niega a
  inventarla. Mide tus propias ejecuciones: de eso va.
- El juicio nunca se abarata. Si quieres todo en Haiku, esta no es tu skill.

## Relacionado

- **[Invokard](https://invokard.web.app)** — 55 «cartas» de habilidades para Claude y cualquier
  cliente MCP, 9 de ellas gratis. Esta regla es la sección 1G de **El Orquestador**, la carta
  gratuita que enruta cada petición al especialista correcto; si usas esa carta, el despacho ya
  va dentro.
- **[CRBRO](https://github.com/Octonove/crbro-memory)** — un servidor MCP de código abierto que
  da memoria persistente a tu IA: neuronas, sesiones y un índice de búsqueda en tu propio disco,
  sin cuenta. Ahí acaba el gasto medido de cada ejecución cuando quiero comparar semanas.

## Licencia

MIT: haz lo que quieras con ella, conserva el aviso. Hecha por
[Octonove](https://github.com/Octonove).
