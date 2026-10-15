# Decisiones de despacho: si delegar, cuántos, qué modelo

Casos breves y realistas, cada uno con la decisión, la línea de despacho y la regla en la que se
apoya (los números de sección son los de [`es/SKILL.md`](../es/SKILL.md)). Al final, los nombres
de modelo de cada cliente.

## Sin delegar

### 1. Renombrar una función en todo el repositorio

> Renombra `getUser` a `fetchUser` en todas partes y asegúrate de que no se rompe nada.

`grep` encuentra cada llamada, la edición se hace en línea y la batería de tests dice si algo se
rompió. Un subagente pagaría un contexto entero por hacer lo que ya hacen dos comandos
(sección 1).

```
Despacho: 0 agentes · en línea
```

### 2. Una segunda opinión sobre un arreglo que ya pasa

> El arreglo está hecho y los tests pasan. Que otro agente lo revise.

La evidencia existe: el test que fallaba ahora pasa y el diff es lo bastante corto para leerlo.
Un segundo agente volvería a deducir lo que el test ya demostró (sección 1, salvaguarda 3). Lee el
diff en línea; si un camino no está cubierto, escribe el test que lo cubra.

```
Despacho: 0 agentes · en línea (evidencia: el test que fallaba ahora pasa)
```

### 3. ¿Por qué está en rojo la CI?

> La CI está en rojo en mi pull request. Averigua por qué.

El log de un job, de unos cientos de líneas, cabe en el contexto. Léelo en línea y vuelve a
ejecutar el comando que falla. Delegar solo empieza a tener sentido cuando el log ya no cabe
(caso 5).

```
Despacho: 0 agentes · en línea
```

## Un agente

### 4. Mapear un módulo heredado grande antes de refactorizar

> Antes de tocar la facturación necesito saber cómo viaja el token de sesión por `billing/`
> (unos 140 ficheros).

Más lectura de la que cabe en un contexto, así que un agente. Mapear dependencias dentro de un
marco que pones tú es analítica acotada: modelo medio. El diseño del refactor se queda en línea;
es juicio, y necesita el mapa, no los 140 ficheros.

```
Despacho: 1 agente · 1 medio (mapa de billing/) · en línea: diseño del refactor, código, revisión final · tope: sin bucle
```

El encargo:

> - **Objetivo:** mapear dónde se crea, se lee, se pasa y se guarda `SessionToken` dentro de
>   `billing/`.
> - **Contexto:** los puntos de entrada son `billing/api/*.py`; la clase del token está en
>   `billing/auth.py`.
> - **Restricciones:** solo lectura; no edites ficheros ni arranques servicios.
> - **Foco de revisión:** cada salto lleva fichero y línea.
> - **Salida:** los saltos como `file:line → file:line`, uno por línea, más como mucho 5
>   sorpresas.
> - **Terminado:** cada referencia a `SessionToken` que encuentra `grep` en `billing/` está en el
>   mapa o explicada.

### 5. Recortar un log enorme a los fallos

> La ejecución end-to-end de anoche imprimió 40.000 líneas. ¿Qué tests fallaron y por qué?

Demasiado largo para leerlo en línea, y sacar los fallos no pide juicio: un agente pequeño.
Devuelve cada test que falla con su primera línea de error y la ruta del log. El diagnóstico se
queda en línea.

```
Despacho: 1 agente · 1 pequeño (extraer fallos) · en línea: diagnóstico · tope: sin bucle
```

## Varios agentes, una parcela cada uno

### 6. La misma migración en tres paquetes independientes

> Pasa `packages/web`, `packages/api` y `packages/cli` de `date-lib` v2 a v3 (el codemod está
> escrito) y después decide qué sustituye al `parseLoose` eliminado.

Los tres paquetes no se importan entre sí: tres parcelas que de verdad corren a la vez. Ejecutar
un codemod escrito y arreglar lo que rompe dentro de un paquete es analítica acotada, así que cada
uno lleva el modelo medio. Qué sustituye a `parseLoose` es juicio: en línea, una vez, después de
los tres informes.

```
Despacho: 3 agentes · 3 medios (web, api, cli) · en línea: decisión de parseLoose, revisión final · tope: 1 ronda de corrección por paquete
```

### 7. «Tres revisores: seguridad, rendimiento, estilo»

> Revisa este pull request en seguridad, rendimiento y estilo, con tres revisores.

Tres revisores del mismo diff no tienen parcelas distintas; releen las mismas líneas (sección 2,
salvaguarda 3). Propón un revisor con un checklist que cubra las tres cosas, o la revisión en
línea si el diff cabe en el contexto. Si el diff es demasiado grande, pártelo por ficheros, no por
puntos de vista. Si el usuario sigue queriendo tres, lanza tres y dilo en la línea de despacho.

```
Despacho: 0 agentes · en línea (una revisión, checklist de seguridad + rendimiento + estilo)
```

### 8. Una funcionalidad con tests y traducciones

La extensión de Chrome de [`chrome-extension.es.md`](chrome-extension.es.md): diseño, código,
lint y revisión final en línea; los tests (medio) y cuatro traducciones (pequeño) en paralelo.

```
Despacho: 5 agentes · 1 medio (tests) · 4 pequeños (traducciones) · en línea: diseño, código, lint + tests, revisión final · tope: 1 ronda de corrección
```

## Cuando algo sale mal

### 9. Un agente pequeño devuelve algo dudoso

El traductor de alemán escribe `$BETRAG$` donde `en` tiene `$AMOUNT$`. Su único reintento va al
modelo medio, con el mismo encargo más el hallazgo; no se vuelve a lanzar en el pequeño
(salvaguarda 2). Si el medio también falla, el fichero alemán se hace en línea.

### 10. La sesión ya corre el modelo medio

Con Sonnet como modelo de la sesión no hay nada por encima: la analítica acotada y el juicio
corren los dos en Sonnet, y lo mecánico sigue yendo a Haiku (sección 4). La línea de despacho lo
dice.

```
Despacho: 3 agentes · 3 pequeños (traducciones) · en línea en el modelo de la sesión (Sonnet): código, revisión · tope: 1 ronda de corrección
```

## Nombres de modelo por cliente

Los niveles son la regla; los nombres cambian según el cliente y la versión. Filas contrastadas
con la documentación de cada fabricante en octubre de 2026. Solo la fila de Claude Code se ha
probado en este repositorio; las demás están sin probar, así que compruébalas con la versión de tu
cliente.

| Cliente | Pequeño (mecánica) | Medio (analítica acotada) | Juicio | Esfuerzo por subagente | Dónde se ve el gasto |
|---|---|---|---|---|---|
| Claude Code, herramienta `Agent` | `model: "haiku"` | `model: "sonnet"` | sin `model`: hereda el de la sesión | `effort` por llamada (`2.1.292`+), o `effort:` en `.claude/agents/*.md` | recuento de tokens en el resultado de cada subagente; `/usage` |
| Cursor | subagente en `.cursor/agents/<name>.md` con `model: fast` o el ID de un modelo pequeño | el mismo fichero, el ID de un modelo medio | `model: inherit` | no documentado | panel de uso, por petición |
| Codex CLI | subagente TOML en `.codex/agents/` con `model` | igual, un modelo medio | sin `model` | `model_reasoning_effort` | sin comprobar |
| Gemini CLI, GitHub Copilot, OpenCode | definición del subagente con un campo `model` | igual, un modelo medio | sin él, o `inherit` | no documentado | sin comprobar |
| Sin modelo por subagente | ninguno | ninguno | el de la sesión | ninguno | aplica las secciones 1, 2 y 5 a 7, y escribe «modelo no seleccionable» en la línea de despacho |
