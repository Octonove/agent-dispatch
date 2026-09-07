# Worked example: a small Chrome extension, dispatched

This is the example the skill uses, step by step: what the user asked, how the work was split,
which model each subagent got and why, what each one was told, and what the final review
checked. The numbers of agents are real for this plan; the token spend is whatever your tool
reports for your run — the skill never fills that in for you.

## The prompt

> Build a small Chrome extension that highlights prices on any page and converts them to euros.
> Popup with a currency selector. UI in English, translated into Spanish, French, German and
> Italian. Tests for the conversion.

## Step 0 — delegate at all?

Yes, on the first criterion: there are independent parts (four translations, a test file, a
lint/test run) that can run in parallel and do not need to see the conversation. Design and code
could be done inline; in this plan they are delegated because the user wants the run measured.

## Step 1 — the split, classified by type

| # | Subtask | Type | Why this type |
|---|---|---|---|
| 1 | Design: manifest v3, file layout, permissions (`activeTab`, `storage`), how the content script and the popup exchange the selected currency | judgment | every later decision depends on it |
| 2 | Write the code: content script (find prices, wrap them), popup (selector, saves to `chrome.storage`), service worker, `convert.js` | judgment | code that decides how the thing works |
| 3 | Write `convert.test.js` from the spec of `convert.js` (input formats, rounding, unknown currency) | bounded analysis | the frame is set; the work is inside it |
| 4–7 | Translate `_locales/en/messages.json` into ES, FR, DE, IT — one agent per language | mechanical | fixed strings, output easy to check |
| 8 | Validate `manifest.json`, run `npm run lint` and `npm test`, report the output verbatim | mechanical | run and report, no judgment |
| 9 | Final review: every key in `en` exists in the four locales, permissions in the manifest match what the code calls, tests green, nothing skipped | judgment | it ships after this |

## Step 2 — model and effort per subtask

| Subtasks | Model · effort |
|---|---|
| 1, 2, 9 | session's model (Fable 5.1 in my case) · high |
| 3 | Sonnet · medium |
| 4, 5, 6, 7, 8 | Haiku · low |

## Step 4 — the declaration, before launching

```
Dispatch: 9 agents · 3 session-tier (design, code, final review) · 1 mid (tests) · 5 small (4 translations, lint + tests run)
```

## What each agent is told (briefing + return contract)

Every subagent starts with an empty context. It gets the paths it needs, the spec, and a
return contract. Examples:

**Translator (small, ×4)**
> Translate the values of `_locales/en/messages.json` into French. Keep every key, keep
> placeholders like `$AMOUNT$` untouched, keep the same JSON shape. Write the result to
> `_locales/fr/messages.json`. Return: the path you wrote, the number of keys, and any string
> you were not sure about (max 5).

**Lint + tests (small)**
> Run `npm run lint` and `npm test` in the repo root. Do not fix anything. Return: exit codes,
> the last 30 lines of each output verbatim, and the path of any file the tools flagged.

**Tests from spec (mid)**
> `src/convert.js` exports `convert(amount, from, to, rates)`. Spec: amounts may carry
> thousands separators and either decimal comma or point; result rounded to 2 decimals; unknown
> currency throws. Write `test/convert.test.js` covering each rule and two edge cases. Return:
> the path and the list of cases, one line each.

**Final review (session model)**
> Check that the extension fits together: every key in `_locales/en/messages.json` exists in
> `es`, `fr`, `de`, `it`; every permission in `manifest.json` is used by the code and nothing the
> code calls is missing a permission; the tests the lint agent ran are the ones in `test/`;
> report anything skipped. Return: VERDICT pass/fail, at most 5 findings with file and line,
> one NEXT action.

## Step 5 — the final review

The reviewer is the only agent that sees the whole thing at once. In this plan it is where the
five small agents' work gets verified, by someone who can tell a missing key from a bad
translation. It is never cheapened: the saving is in the translators and the test runner, not
here.

## After the run — measure

Report the spend the tool gives back, split small vs large. If it gives none, write
"not measured". The skill's own line at the end of a run looks like:

```
Spend: 5 small · 1 mid · 3 session-tier — figures as reported by the tool, or "not measured"
```

Without the skill, the same nine agents run on the session's model. With it, five of them do
not. The extension is the same.
