# Worked example: a small Chrome extension, dispatched

This is the example the skill uses, step by step: which subtasks stay inline and why, which ones
are delegated and to which model, what each delegated agent is told, and what the final review
checks. The number of agents is the plan's; the token spend is whatever your client reports for
your run. The skill never fills it in for you.

## The prompt

> Build a small Chrome extension that highlights prices on any page and converts them to euros.
> Popup with a currency selector. UI in English, translated into Spanish, French, German and
> Italian. Tests for the conversion.

## Step 1 — delegate at all?

Partly. Design and code are one chain: the code depends on the design and both are judgment, so
they stay inline on the session's model. Once the code exists, five parts are independent and can
run at the same time: the conversion tests and the four translations. Lint and tests are a
command, and the session runs it itself: a command that checks something is never a reason to
delegate.

## Step 2 — how many?

Five, one slice each: one test file and one locale per translator. No second reviewer and no
translator "just in case".

## Step 3 — the split, classified by type

| # | Subtask | Type | Where it runs | Why |
|---|---|---|---|---|
| 1 | Design: manifest v3, file layout, permissions (`activeTab`, `storage`), how the content script and the popup share the selected currency | judgment | inline | every later decision depends on it |
| 2 | Code: content script (find prices, wrap them), popup (selector, saves to `chrome.storage`), service worker, `convert.js` | judgment | inline | code that decides how the thing works |
| 3 | `test/convert.test.js` from the spec of `convert.js` | bounded analysis | 1 agent | the frame is set; it runs while the translations run |
| 4–7 | Translate `_locales/en/messages.json` into ES, FR, DE, IT | mechanical | 4 agents, one per language | fixed strings, output easy to check |
| 8 | Validate `manifest.json`, run `npm run lint` and `npm test` | mechanical | inline | a command checks it and the output is short |
| 9 | Final review: locales complete, permissions match the code, tests green, nothing skipped | judgment | inline | it ships after this |

## Step 4 — model and effort

| Subtasks | Model · effort | Claude Code `Agent` call |
|---|---|---|
| 1, 2, 8, 9 | session's model, inline | none |
| 3 | mid · medium | `model: "sonnet"`, `effort: "medium"` |
| 4–7 | small · low | `model: "haiku"`, `effort: "low"` |

## Step 5 — guardrails and cap

- One fix round after the final review. A finding still open after it is parked as debt or
  rejected with a reason; no second round opens.
- A translator that breaks a placeholder gets its one retry on the mid model, not another run on
  the small one. If that fails too, the locale is done inline.

## Step 6 — the declaration, before launching

```
Dispatch: 5 agents · 1 mid (tests) · 4 small (translations) · inline: design, code, lint + tests, final review · cap: 1 fix round
```

## What each delegated agent is told

Every subagent starts with an empty context. Its brief carries the six things the skill asks for:
goal, context, constraints, review focus, output and definition of done.

**Translator (small, ×4; French shown)**

> - **Goal:** translate the values of `_locales/en/messages.json` into French.
> - **Context:** UI strings of a Chrome extension; the code reads them by key, and placeholders like
>   `$AMOUNT$` are filled at run time.
> - **Constraints:** do not change keys, placeholders or the JSON shape; write only
>   `_locales/fr/messages.json`.
> - **Review focus:** the reviewer will compare the key set and the placeholders with `en`.
> - **Output:** a verdict (done or blocked), the path you wrote, the number of keys, and at most 5
>   strings you were unsure about.
> - **Done:** the file parses as JSON and has exactly the keys of `en`.

**Tests from the spec (mid)**

> - **Goal:** write `test/convert.test.js` for `src/convert.js`.
> - **Context:** `convert(amount, from, to, rates)`. Amounts may carry thousands separators and a
>   decimal comma or point; the result is rounded to 2 decimals; an unknown currency throws.
> - **Constraints:** do not edit `src/` and do not add dependencies.
> - **Review focus:** one test per rule plus two edge cases; no test that just restates the code.
> - **Output:** a verdict (all pass, or how many fail), the path, and the list of cases, one line
>   each; at most 5 failing tests, with file and line.
> - **Done:** `npm test` runs the file; failing tests are reported, not fixed.

## Step 7 — the final review, inline

Every key in `_locales/en/messages.json` exists in `es`, `fr`, `de` and `it` with the same
placeholders; every permission in `manifest.json` is used by the code and nothing the code calls
is missing one; the tests that ran are the ones in `test/`; nothing was skipped. The result is a
verdict (pass or fail), at most 5 findings with file and line, and one next action. This is where
the five agents' work is verified, once, by someone who can tell a missing key from a bad
translation.

## After the run — measure

Report the spend per tier as the client gives it back. In Claude Code each subagent's result
carries its token count, and `/usage` shows usage by model. With no figure, write
"not measured":

```
Spend: 1 mid · 4 small — tokens as the client reports them, or "not measured"
```

The plan promises no saving. The line after the run is the only number that counts.
