---
name: agent-dispatch
description: "Decide si delegar en subagentes (por defecto, no), cuántos (empezando por cero) y qué modelo y esfuerzo lleva cada uno, por el tipo de tarea y nunca por la importancia del proyecto. Úsala antes de lanzar cualquier subagente, agentes en paralelo, agente en segundo plano, flujo o bucle de revisión, o cuando una tarea pueda repartirse. Lo mecánico va a un modelo pequeño, el análisis acotado a uno medio y el juicio se queda en el modelo de la sesión. Declara antes el reparto y el tope de bucle; reporta después el gasto medido."
---

# Despacho de agentes — qué modelo corre cada subagente

Salvo que se diga otra cosa, un subagente corre en el modelo de la sesión, así que traducir a
cuatro idiomas cuesta lo mismo por token que una decisión de arquitectura. Esta regla gobierna una
sola cosa: **el gasto en agentes**. Nunca cambia el modelo de la conversación. Aplícala, en este
orden, cada vez que un trabajo vaya a salir de la conversación: un subagente, agentes en paralelo,
un flujo, un bucle.

## 1. ¿Hay que delegar? Por defecto, no

Delega solo si se cumple una de dos:

- **partes independientes** que de verdad corren a la vez y ahorran tiempo de reloj;
- **más lectura de la que cabe en un contexto** (docenas de ficheros, transcripciones, logs
  largos).

Si no, hazlo en línea. Un subagente no ve esta conversación: cuesta su contexto entero más el
encargo que le escribes, y su respuesta hay que verificarla igual. Nunca es razón para delegar:
comprobar lo que un comando comprueba (`grep`, `curl`, pasar los tests, leer un fichero), ni una
segunda opinión sobre algo que ya está verificado. Donde hay evidencia directa, manda la evidencia.

## 2. ¿Cuántos? Empieza por cero

Cero es la respuesta normal. Un subagente con un buen encargo cubre casi todo lo que merece
delegarse. Varios, solo cuando cada uno tiene una parcela que ningún otro cubre; nombra las
parcelas antes de lanzarlos. Si dos suenan parecidos, sobra uno: una flota es la misma respuesta
pagada varias veces.

## 3. Clasifica cada subtarea por tipo

Escribe las subtareas y clasifica cada una por la clase de trabajo, **nunca por lo importante que
sea el proyecto**:

| Nivel | Qué es | Ejemplos |
|---|---|---|
| **Mecánica** | Sin juicio; el resultado está bien o mal y es fácil de comprobar | traducir cadenas fijas, listar, contar, extraer campos con formato fijo, formatear, renombrar, recortar un log largo a sus errores |
| **Analítica acotada** | Razonar dentro de un marco que ha puesto otro | resumir un módulo, mapear dependencias, escribir tests a partir de una especificación clara, un cambio mecánico en muchos ficheros, comparar dos versiones, pasar un checklist |
| **Juicio** | Decidir, diseñar, o cualquier cosa que se entrega sin otra revisión detrás | arquitectura, el código que decide cómo funciona algo, elegir entre opciones, sintetizar un informe, la revisión final, lo que se publica o se manda a un cliente |

## 4. Modelo y esfuerzo por nivel

| Nivel | Modelo | Esfuerzo | Llamada a `Agent` en Claude Code |
|---|---|---|---|
| Mecánica | **pequeño** (Haiku) | bajo | `model: "haiku"`, `effort: "low"` |
| Analítica acotada | **medio** (Sonnet) | medio | `model: "sonnet"`, `effort: "medium"` |
| Juicio | **el modelo de la sesión** | el de la sesión | sin `model` ni `effort` (hereda los dos) |

- En Claude Code, el juicio solo hereda con un tipo de subagente cuya definición no fije `model`
  ni `effort`. Si está fijado `CLAUDE_CODE_SUBAGENT_MODEL`, pasa el alias de la sesión
  (`model: "opus"` en una sesión Opus).
- Los nombres son ejemplos: usa los niveles que ofrezca tu cliente. Nunca subas por encima del
  modelo de la sesión; si la sesión ya corre el modelo medio, la analítica acotada y el juicio se
  quedan los dos en él.
- Si dudas entre dos niveles, elige el de abajo. La revisión final (sección 7) lo comprueba.
- Si el cliente no deja fijar el modelo o el esfuerzo por subagente (en Claude Code, `effort` pide
  la versión `2.1.292` o posterior), no finjas que lo has hecho: aplica el resto y dilo en la línea
  del despacho.

## 5. Salvaguardas que no se negocian

1. **La revisión final y quien sintetiza nunca se abaratan.** El ahorro sale de lo mecánico,
   jamás de lo que evita que un fallo se publique.
2. **Un fallo sube la tarea de nivel.** Si un agente pequeño o medio falla o devuelve algo dudoso,
   su reintento va un nivel más arriba, nunca en el mismo modelo. En el nivel de la sesión, el
   trabajo vuelve a hacerse en línea.
3. **Menos agentes.** Un revisor con un checklist claro vale más que tres vagos. Un traductor por
   idioma, no dos «por si acaso». Ningún agente cuyo único trabajo sea recomprobar la conclusión
   de otro. Pasa cada resultado mecánico al paso siguiente según llega, salvo que ese paso
   necesite todos a la vez.
4. **Cada subagente recibe un encargo autocontenido y un contrato de retorno.** Lo que no está en
   el encargo no existe para él. El encargo lleva 6 cosas: objetivo; contexto mínimo (rutas y
   decisiones ya tomadas); restricciones (qué no tocar, publicar ni ejecutar); foco de revisión
   (qué mirará quien revise); formato de salida; criterio de terminado. Pide un veredicto, como
   mucho 5 hallazgos y rutas de fichero en vez de contenidos pegados. Si no sabes escribir el
   encargo, la tarea todavía no está lista para delegarse.
5. **Todo bucle declara su tope.** Antes de cualquier bucle o ronda de revisión y corrección
   (agentes, flujos, un `/loop`), fija la condición de éxito y el máximo de rondas. Como mucho 1
   reintento del mismo enfoque (la salvaguarda 2 dice en qué modelo). Un bucle de vigilancia que pide el
   usuario puede quedar abierto con su condición de parada. Al llegar al tope no se abre otra
   ronda: cada hallazgo abierto queda corregido, aparcado como deuda o rechazado con motivo.

## 6. Declara antes, mide después

Antes de lanzar, una línea que el usuario pueda leer, con el tope incluido:

```
Despacho: 5 agentes · 1 medio (tests) · 4 pequeños (traducciones) · en línea: diseño, código, lint + tests, revisión final · tope: 1 ronda de corrección
```

Si no se delega nada, dilo así: «Despacho: 0 agentes · en línea». Al terminar, reporta el gasto
que devuelva el cliente, por nivel (en Claude Code: el recuento de tokens que devuelve cada
subagente, o `/usage`). Si no hay cifra, escribe **«sin medir»**. Nunca estimes un ahorro: sin
cifra no hay ahorro, solo la sensación de haberlo tenido.

## 7. La revisión final

El último paso, en línea o con un agente de nivel sesión, comprueba que las partes encajan: cada
cadena que usa el código existe en todos los idiomas, los permisos coinciden con lo que llama el
código, los tests que se pasaron son los que importan, nada se saltó en silencio. Aquí se
verifica, una vez y por alguien que sabe distinguir, el trabajo de los modelos pequeños.

## Ejemplo

*«Una extensión de Chrome que convierta precios a euros, con un popup de moneda, interfaz en
inglés más español, francés, alemán e italiano, y tests para la conversión.»* Diseño y código son
una misma cadena de juicio: en línea. Después, los tests (medio) y las 4 traducciones (pequeño,
una por idioma) corren en paralelo. Lint y tests son un comando y la revisión final es juicio: en
línea. Sale la línea de despacho de la sección 6. Más casos y los nombres de modelo por cliente:
https://github.com/Octonove/agent-dispatch/blob/main/examples/decisions.es.md
