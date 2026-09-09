# Agent Dispatch — which model runs each subagent

[![license](https://img.shields.io/github/license/Octonove/agent-dispatch)](LICENSE)
[![skill](https://img.shields.io/badge/skill-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20any%20agent%20client-1E3A5F)](SKILL.md)
[![español](https://img.shields.io/badge/lee%20en-espa%C3%B1ol-b85f2c)](README.es.md)

A free, standalone skill that stops every subagent from running on your biggest model.

By default, Claude Code hands every subagent the model you have selected for the session. So
when a task fans out into nine agents, all nine run on Fable 5.1 (or Opus, or whatever you
picked) — the four that translate a `messages.json` file cost the same per token as the one
that designs the architecture. This skill makes the split explicit before anything launches:
**the model is picked by the type of task, never by the importance of the project.**

![Agent Dispatch demo](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/demo.gif)

## The rule in one table

| Type of task | Examples | Model · effort |
|---|---|---|
| **Mechanical** | translations of fixed strings, listing, counting, measuring, running a script and reporting the output, checking that a manifest parses | **small** (e.g. Haiku) · low |
| **Bounded analysis** | summarizing a module, mapping dependencies, writing tests from a clear spec, one mechanical change across many files | **mid** (e.g. Sonnet) · medium |
| **Judgment** | architecture, writing the code that decides how something works, choosing between options, the final review, anything that ships | **the session's model** (e.g. Fable 5.1, Opus) · high |

Before any of that it asks the cheaper question first: **should this be delegated at all, and how
many?** The default is no, and the count starts at zero — most work is inline work.

Plus four guardrails the skill enforces: the final reviewer never gets cheapened; a small agent
that fails moves the task up a tier instead of being retried; fewer agents beat more agents, and
no agent exists just to double-check another's conclusion;
and every run **declares its split before launching and reports the measured spend after** —
or says "not measured". No invented savings.

## Worked example: a small Chrome extension

> *Build a small Chrome extension that highlights prices on any page and converts them to euros.
> Popup with a currency selector. UI in English, translated into Spanish, French, German and
> Italian. Tests for the conversion.*

![Dispatch of the Chrome extension example](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/example-chrome-extension.png)

| # | Subtask | Model · effort |
|---|---|---|
| 1 | Design: manifest v3, files, permissions, how content script and popup talk | session model · high |
| 2 | Write the code: content script, popup, service worker, conversion module | session model · high |
| 3 | Write the conversion tests from the spec | mid · medium |
| 4–7 | Translate `messages.json` into ES, FR, DE, IT — one agent per language | small · low |
| 8 | Validate the manifest, run lint and the tests, report the output verbatim | small · low |
| 9 | Final review: locales complete, permissions match the code, tests green | session model · high |

Without the skill: 9 agents on the session's model. With it: **3 on the session's model, 1 on
the mid model, 5 on the small one.** Same extension. The judgment stayed where it matters.
The full walkthrough, with the briefing each agent receives, is in
[`examples/chrome-extension.md`](examples/chrome-extension.md).

## Install

**Claude Code** — as a global skill (applies in every project):

```bash
mkdir -p ~/.claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md -o ~/.claude/skills/agent-dispatch/SKILL.md
```

Or per project: put the same file at `.claude/skills/agent-dispatch/SKILL.md`. Spanish version:
[`es/SKILL.md`](es/SKILL.md). Claude Code loads skills automatically; the description in the
frontmatter is what makes it apply whenever subagents are on the table.

**Cursor** — copy the body of `SKILL.md` into a rule (`.cursor/rules/agent-dispatch.mdc`) with
`alwaysApply: true`.

**Any other client** — paste the body of `SKILL.md` into your system prompt or project
instructions. If the client cannot choose a model per subagent, the skill says so and applies
the rest (whether to delegate, how many, briefing, declare, measure).

## What you get, and what you don't

- You get a line like `Dispatch: 9 agents · 3 session-tier · 1 mid · 5 small` before anything
  runs, and the spend the tool reports when it is done.
- You do **not** get a savings number from the skill. It cannot measure what your tool does
  not report, and it refuses to invent one. Measure your own runs; that is the point.
- Judgment never gets cheaper. If you want everything on Haiku, this is not the skill for you.

## Related

- **[Invokard](https://invokard.web.app)** — 55 skill "cards" for Claude and any MCP client,
  9 of them free. This rule is section 1G of **The Orchestrator**, the free card that routes
  every request to the right specialist; if you use that card, the dispatch is already inside it.
- **[CRBRO](https://github.com/Octonove/crbro-memory)** — an open-source MCP server that gives
  your AI persistent memory: neurons, sessions and a search index on your own disk, no account.
  It is where the measured spend of each run ends up when I want to compare weeks.

## License

MIT — do what you want with it, keep the notice. Built by [Octonove](https://github.com/Octonove).
