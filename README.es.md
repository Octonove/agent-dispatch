# Agent Dispatch — qué modelo corre cada subagente

[![license](https://img.shields.io/github/license/Octonove/agent-dispatch)](LICENSE)
[![skill](https://img.shields.io/badge/skill-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20cualquier%20cliente-1E3A5F)](es/SKILL.md)
[![english](https://img.shields.io/badge/read%20in-english-b85f2c)](README.md)

Una skill gratuita y suelta que evita que todos tus subagentes corran con el modelo más grande.

Salvo que la llamada, la definición del subagente o `CLAUDE_CODE_SUBAGENT_MODEL` fijen un
modelo, Claude Code corre cada subagente en el modelo que tienes seleccionado para la sesión
([documentación](https://code.claude.com/docs/en/sub-agents)). Así que cuando una tarea se
reparte, los agentes que traducen un `messages.json` cuestan lo mismo por token que el que diseña
la arquitectura. Esta skill hace el reparto explícito antes de lanzar nada: **el modelo se elige
por el tipo de tarea, nunca por la importancia del proyecto.**

![Demo de Agent Dispatch: la línea de despacho del ejemplo de la extensión de Chrome (ilustración, no una ejecución grabada)](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/demo.gif)

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
| **Mecánica** | traducir cadenas fijas, listar, contar, extraer campos con formato fijo, recortar un log largo a sus errores | **pequeño** (p. ej. Haiku) · bajo |
| **Analítica acotada** | resumir un módulo, mapear dependencias, escribir tests a partir de una especificación clara, un cambio mecánico en muchos ficheros | **medio** (p. ej. Sonnet) · medio |
| **Juicio** | arquitectura, escribir el código que decide cómo funciona algo, elegir entre opciones, la revisión final, lo que se entrega | **el modelo de la sesión** · el de la sesión |

Antes de todo eso hace la pregunta barata: **¿hay que delegar, y cuántos?** Por defecto no, y la
cuenta empieza en cero: casi todo es trabajo en línea, y comprobar lo que comprueba un comando
(`grep`, pasar los tests) nunca es razón para delegar.

Más cinco salvaguardas que la skill le pide al agente: la revisión final nunca se abarata; un
agente pequeño o medio que falla recibe su único reintento un nivel más arriba, nunca en el mismo
modelo; menos agentes valen más que más agentes, y ninguno existe solo para recomprobar la
conclusión de otro; cada subagente recibe un **encargo autocontenido y un contrato de retorno**
(objetivo, contexto mínimo, qué no tocar, qué mirará quien revise, formato de salida y criterio de
terminado), porque nunca ve tu conversación; y **todo bucle declara su tope** antes de empezar: la
condición de éxito y el máximo de rondas, con un solo reintento del mismo enfoque. Además, cada
ejecución **declara su reparto y su tope antes de lanzar y reporta el gasto medido después**, o
dice «sin medir». Nada de ahorros inventados.

En Claude Code los niveles se traducen en parámetros de la propia herramienta `Agent`:
`model: "haiku"` o `model: "sonnet"` con `effort` por llamada (Claude Code 2.1.292 o
posterior), y ni `model` ni `effort` para el juicio, que así hereda los dos de la sesión: usa un
tipo de subagente cuya definición no fije ninguno y, si está fijado `CLAUDE_CODE_SUBAGENT_MODEL`,
pasa el alias de la sesión, como `model: "opus"`. Para otros clientes, mira
[los nombres de modelo por cliente](examples/decisions.es.md#nombres-de-modelo-por-cliente).

## Ejemplo trabajado: una extensión de Chrome pequeña

> *Haz una extensión de Chrome pequeña que resalte los precios de cualquier página y los
> convierta a euros. Popup con selector de moneda. Interfaz en inglés, traducida a español,
> francés, alemán e italiano. Tests para la conversión.*

![Despacho del ejemplo de la extensión de Chrome](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/example-chrome-extension.es.png)

| # | Subtarea | Dónde corre |
|---|---|---|
| 1 | Diseño: manifest v3, ficheros, permisos, cómo hablan el content script y el popup | en línea · modelo de sesión |
| 2 | Escribir el código: content script, popup, service worker, módulo de conversión | en línea · modelo de sesión |
| 3 | Escribir los tests de conversión a partir de la especificación | 1 agente · medio · medio |
| 4–7 | Traducir `messages.json` a ES, FR, DE, IT, un agente por idioma | 4 agentes · pequeño · bajo |
| 8 | Validar el manifest, pasar lint y los tests | en línea · lo comprueba un comando |
| 9 | Revisión final: idiomas completos, permisos coherentes con el código, tests en verde | en línea · modelo de sesión |

```
Despacho: 5 agentes · 1 medio (tests) · 4 pequeños (traducciones) · en línea: diseño, código, lint + tests, revisión final · tope: 1 ronda de corrección
```

Diseño y código son una misma cadena de juicio, así que se quedan en la sesión; lint y tests son
un comando, no merecen un subagente. Lo que corre en paralelo y en niveles más baratos es el
trabajo de verdad independiente: los tests y las cuatro traducciones. La skill no le pone cifra al
ahorro; se la pone el gasto que reporte tu cliente después de la ejecución. El recorrido
completo, con el encargo que recibe cada agente, está en
[`examples/chrome-extension.es.md`](examples/chrome-extension.es.md), y más casos (no delegar, un
agente, varias parcelas, un agente que falla) en [`examples/decisions.es.md`](examples/decisions.es.md).

## Instalación

Elige una. La skill en inglés es [`SKILL.md`](SKILL.md): cambia `es/SKILL.md` por `SKILL.md` en
las URL, o instala el plugin `agent-dispatch`.

### Claude Code

**Skill personal**, para todos los proyectos de tu máquina:

```bash
mkdir -p ~/.claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md \
  -o ~/.claude/skills/agent-dispatch/SKILL.md
```

**Skill de proyecto**, en el repositorio para que la tenga todo el equipo:

```bash
mkdir -p .claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md \
  -o .claude/skills/agent-dispatch/SKILL.md
```

**Plugin**, desde el marketplace de este repositorio:

```text
/plugin marketplace add Octonove/agent-dispatch
/plugin install agent-dispatch-es@agent-dispatch
```

Desde la terminal: `claude plugin marketplace add Octonove/agent-dispatch` y después
`claude plugin install agent-dispatch-es@agent-dispatch`. En Claude Code 2.1.275 o posterior es un
solo paso: `/plugin install agent-dispatch-es --marketplace Octonove/agent-dispatch`. El plugin en
inglés es `agent-dispatch@agent-dispatch`. Los marketplaces de terceros no se actualizan solos por
defecto: `claude plugin update agent-dispatch-es@agent-dispatch` trae el último commit.

**Compruébalo:** `/skills` la lista y `/agent-dispatch` la ejecuta a mano (instalada como plugin,
lleva el espacio de nombres: `/agent-dispatch-es:agent-dispatch`). Una skill nueva se carga sin
reiniciar; si `~/.claude/skills` o el `.claude/skills` del proyecto no existían al empezar la
sesión, ejecuta `/reload-skills`. Un plugin instalado o actualizado desde la terminal necesita
`/reload-plugins` en una sesión ya abierta.

**Que aplique siempre.** Una skill no está siempre activa: Claude Code solo mantiene su
descripción en el contexto y carga el cuerpo cuando la descripción encaja con lo que pides
(`claude plugin details agent-dispatch-es` estima unos 250 y 3.000 tokens). Para que salte cada
vez que se plantea delegar, añade una línea a tu `CLAUDE.md`:

```text
Antes de lanzar cualquier subagente, agentes en paralelo, flujo o bucle, aplica la skill agent-dispatch.
```

### Cursor

Como skill, que Cursor carga por su descripción desde `.cursor/skills/` (proyecto) o
`~/.cursor/skills/` (usuario):

```bash
mkdir -p .cursor/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md \
  -o .cursor/skills/agent-dispatch/SKILL.md
```

O como regla aplicada en cada petición, que entonces paga el fichero entero cada vez:

```bash
mkdir -p .cursor/rules
body=$(curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md) &&
{ printf '%s\n' '---' 'description: Antes de lanzar subagentes, decide si delegar, cuántos y qué modelo lleva cada uno' 'alwaysApply: true' '---'
  printf '%s\n' "$body" | awk 'n >= 2; /^---$/ { n++ }'
} > .cursor/rules/agent-dispatch.mdc
```

Para dar a cada nivel su modelo, define los subagentes en `.cursor/agents/` con un campo `model`
(mira [los nombres de modelo por cliente](examples/decisions.es.md#nombres-de-modelo-por-cliente)).

### Otros clientes

Clientes que leen el formato [Agent Skills](https://agentskills.io) desde `.agents/skills/`
(Codex, Gemini CLI, GitHub Copilot y OpenCode, según su documentación):

```bash
mkdir -p .agents/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/es/SKILL.md \
  -o .agents/skills/agent-dispatch/SKILL.md
```

Usa `~/.agents/skills/` para todos los proyectos. Clientes sin skills: pega el cuerpo de
`es/SKILL.md` (todo lo que va después del segundo `---`) en el system prompt, en `AGENTS.md` o en
las instrucciones del proyecto. Si el cliente no permite elegir modelo por subagente, la skill lo
dice en la línea de despacho y aplica el resto: si delegar, cuántos, encargos, topes de bucle,
declarar y medir.

Los comandos de Claude Code de arriba se ejecutaron al escribir este README: el plugin con
`claude plugin install` y `claude plugin details`, las carpetas de skill con `curl` y
`claude plugin validate`. Las rutas de Cursor y de otros clientes salen de la documentación de
cada fabricante y no se han probado aquí.

## Qué te da y qué no

- Te da una línea como `Despacho: 5 agentes · 1 medio · 4 pequeños · en línea: diseño, código, revisión · tope: 1 ronda de corrección`
  antes de que corra nada, y el gasto que reporte la herramienta al terminar.
- **No** te da una cifra de ahorro. No puede medir lo que tu herramienta no reporta, y se niega a
  inventarla. Mide tus propias ejecuciones: de eso va.
- El juicio nunca se abarata. Si quieres todo en Haiku, esta no es tu skill.

## Contribuir

`python3 scripts/check.py` ejecuta las comprobaciones del repositorio que hace la CI en cada pull
request y en cada push a `main`: frontmatter válido; las mismas secciones, reglas y cifras en
inglés y en español; enlaces internos que funcionan; `SKILL.md` por debajo de su límite de
longitud; y los manifiestos del plugin. La CI además ejecuta `claude plugin validate .` y
`claude plugin validate es`. Cambia los dos idiomas en el mismo commit.

## Relacionado

- **[Invokard](https://invokard.web.app)** — «cartas» de habilidades para Claude y cualquier
  cliente MCP. Esta regla es la sección 1G de **El Orquestador**, la carta gratuita que enruta
  cada petición al especialista correcto; si usas esa carta, el despacho ya va dentro.
- **[CRBRO](https://github.com/Octonove/crbro-memory)** — un servidor MCP de código abierto que
  da memoria persistente a tu IA: neuronas, sesiones y un índice de búsqueda en tu propio disco,
  sin cuenta. Ahí acaba el gasto medido de cada ejecución cuando quiero comparar semanas.

## Licencia

MIT: haz lo que quieras con ella, conserva el aviso. Hecha por
[Octonove](https://github.com/Octonove).
