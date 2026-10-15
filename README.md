# Agent Dispatch — which model runs each subagent

[![license](https://img.shields.io/github/license/Octonove/agent-dispatch)](LICENSE)
[![skill](https://img.shields.io/badge/skill-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20any%20agent%20client-1E3A5F)](SKILL.md)
[![español](https://img.shields.io/badge/lee%20en-espa%C3%B1ol-b85f2c)](README.es.md)

A free, standalone skill that stops every subagent from running on your biggest model.

Unless the call, the subagent's definition or `CLAUDE_CODE_SUBAGENT_MODEL` sets a model, Claude
Code runs every subagent on the model you selected for the session
([docs](https://code.claude.com/docs/en/sub-agents)). So when a
task fans out, the agents that translate a `messages.json` cost the same per token as the one
that designs the architecture. This skill makes the split explicit before anything launches:
**the model is picked by the type of task, never by the importance of the project.**

![Agent Dispatch demo: the dispatch line of the Chrome extension example (illustration, not a recorded run)](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/demo.gif)

<!-- invokard-coffee -->
**&#9749; If this saves you time, buy me a coffee.** [![Buy me a coffee with PayPal](https://img.shields.io/badge/PayPal-Buy%20me%20a%20coffee-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?business=stradoxx%40gmail.com&no_recurring=0&currency_code=EUR&item_name=Support%20agent%20dispatch)

Or in USDC. Send **USDC only** and **only on the network shown**; on any other network it is lost with no way to recover it.

| Network | USDC address |
|---|---|
| **Solana** | `5n6Gfosk7SdwbvdtE9xiLWpcGPBBBGDZYRfAkWyCk86g` |
| **Ethereum** (ERC-20) | `0xe176866f9d7fdb498e0d4a983d3e34d84dcd6bfc` |

## The rule in one table

| Type of task | Examples | Model · effort |
|---|---|---|
| **Mechanical** | translations of fixed strings, listing, counting, extracting fields in a fixed format, cutting a long log down to its errors | **small** (e.g. Haiku) · low |
| **Bounded analysis** | summarizing a module, mapping dependencies, writing tests from a clear spec, one mechanical change across many files | **mid** (e.g. Sonnet) · medium |
| **Judgment** | architecture, writing the code that decides how something works, choosing between options, the final review, anything that ships | **the session's model** · the session's |

Before any of that it asks the cheaper question first: **should this be delegated at all, and how
many?** The default is no, and the count starts at zero: most work is inline work, and checking
what a command can check (`grep`, running the tests) is never a reason to delegate.

Plus five guardrails the skill tells the agent to keep: the final reviewer never gets cheapened;
a small or mid agent that fails gets its one retry a tier up, never on the same model; fewer
agents beat more agents, and no agent exists just to re-check another's conclusion; every
subagent gets a **self-contained brief and a return contract** (goal, minimum context, what it
must not touch, what the reviewer will check, output format, definition of done), because it
never sees your conversation; and **every loop declares its cap** before it starts: the success
condition and the maximum number of rounds, one retry of the same approach at most. On top of
that, every run **declares its split and its cap before launching and reports the measured spend
after**, or says "not measured". No invented savings.

In Claude Code the tiers map to the `Agent` tool's own parameters: `model: "haiku"` or
`model: "sonnet"` with `effort` per call (Claude Code 2.1.292 or later), and neither `model` nor
`effort` for judgment, so it inherits both from the session. For other clients, see
[the model names per client](examples/decisions.md#model-names-per-client).

## Worked example: a small Chrome extension

> *Build a small Chrome extension that highlights prices on any page and converts them to euros.
> Popup with a currency selector. UI in English, translated into Spanish, French, German and
> Italian. Tests for the conversion.*

![Dispatch of the Chrome extension example](https://raw.githubusercontent.com/Octonove/agent-dispatch/main/docs/example-chrome-extension.png)

| # | Subtask | Runs on |
|---|---|---|
| 1 | Design: manifest v3, files, permissions, how content script and popup talk | inline · session model |
| 2 | Write the code: content script, popup, service worker, conversion module | inline · session model |
| 3 | Write the conversion tests from the spec | 1 agent · mid · medium |
| 4–7 | Translate `messages.json` into ES, FR, DE, IT, one agent per language | 4 agents · small · low |
| 8 | Validate the manifest, run lint and the tests | inline · a command checks it |
| 9 | Final review: locales complete, permissions match the code, tests green | inline · session model |

```
Dispatch: 5 agents · 1 mid (tests) · 4 small (translations) · inline: design, code, lint + tests, final review · cap: 1 fix round
```

Design and code are one chain of judgment, so they stay with the session; lint and tests are a
command, not worth a subagent. What runs in parallel on cheaper tiers is the work that is truly
independent: the tests and the four translations. The skill puts no number on the saving; the
spend your client reports after the run does. The full walkthrough, with the brief each agent
receives, is in [`examples/chrome-extension.md`](examples/chrome-extension.md), and more cases (no
delegation, one agent, several slices, a failing agent) are in
[`examples/decisions.md`](examples/decisions.md).

## Install

Pick one. The Spanish skill is [`es/SKILL.md`](es/SKILL.md): swap `SKILL.md` for `es/SKILL.md` in
the URLs, or install the `agent-dispatch-es` plugin.

### Claude Code

**Personal skill**, for every project on your machine:

```bash
mkdir -p ~/.claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md \
  -o ~/.claude/skills/agent-dispatch/SKILL.md
```

**Project skill**, committed so your team gets it too:

```bash
mkdir -p .claude/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md \
  -o .claude/skills/agent-dispatch/SKILL.md
```

**Plugin**, from the marketplace in this repository:

```text
/plugin marketplace add Octonove/agent-dispatch
/plugin install agent-dispatch@agent-dispatch
```

From the shell: `claude plugin marketplace add Octonove/agent-dispatch`, then
`claude plugin install agent-dispatch@agent-dispatch`. On Claude Code 2.1.275 or later it is one
step: `/plugin install agent-dispatch --marketplace Octonove/agent-dispatch`. The Spanish plugin
is `agent-dispatch-es@agent-dispatch`. Third-party marketplaces do not auto-update by default:
`claude plugin update agent-dispatch@agent-dispatch` fetches the latest commit.

**Check it:** `/skills` lists it and `/agent-dispatch` runs it by hand (installed as a plugin, the
skill is namespaced: `/agent-dispatch:agent-dispatch`). A new skill is picked up without a
restart; if `~/.claude/skills` or the project's `.claude/skills` did not exist when the session
started, run `/reload-skills`. A plugin installed or updated from the shell needs
`/reload-plugins` in a session that is already open.

**Make it apply every time.** A skill is not always on: Claude Code keeps only its description in
context and loads the body when the description matches what you asked
(`claude plugin details agent-dispatch` estimates about 170 and 2,100 tokens). To make it fire
whenever delegation comes up, add one line to your `CLAUDE.md`:

```text
Before launching any subagent, parallel agents, workflow or loop, apply the agent-dispatch skill.
```

### Cursor

As a skill, which Cursor loads by its description from `.cursor/skills/` (project) or
`~/.cursor/skills/` (user):

```bash
mkdir -p .cursor/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md \
  -o .cursor/skills/agent-dispatch/SKILL.md
```

Or as a rule applied to every request, which then pays for the whole file every time:

```bash
mkdir -p .cursor/rules
body=$(curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md) &&
{ printf '%s\n' '---' 'description: Before launching subagents, decide whether to delegate, how many, and which model each one gets' 'alwaysApply: true' '---'
  printf '%s\n' "$body" | awk 'n >= 2; /^---$/ { n++ }'
} > .cursor/rules/agent-dispatch.mdc
```

To give each tier its own model, define the subagents in `.cursor/agents/` with a `model` field
(see [the model names per client](examples/decisions.md#model-names-per-client)).

### Other clients

Clients that read the [Agent Skills](https://agentskills.io) format from `.agents/skills/`
(Codex, Gemini CLI, GitHub Copilot and OpenCode, according to their docs):

```bash
mkdir -p .agents/skills/agent-dispatch
curl -fsSL https://raw.githubusercontent.com/Octonove/agent-dispatch/main/SKILL.md \
  -o .agents/skills/agent-dispatch/SKILL.md
```

Use `~/.agents/skills/` for every project. Clients without skills: paste the body of `SKILL.md`
(everything after the second `---`) into the system prompt, `AGENTS.md` or the project
instructions. If the client cannot choose a model per subagent, the skill says so in the dispatch
line and applies the rest: whether to delegate, how many, briefs, loop caps, declare and measure.

The Claude Code commands above were run while writing this README: the plugin with
`claude plugin install` and `claude plugin details`, the skill folders with `curl` and
`claude plugin validate`. The Cursor and other-client paths come from each vendor's documentation
and are untested here.

## What you get, and what you don't

- You get a line like `Dispatch: 5 agents · 1 mid · 4 small · inline: design, code, review · cap: 1 fix round`
  before anything runs, and the spend the tool reports when it is done.
- You do **not** get a savings number from the skill. It cannot measure what your tool does
  not report, and it refuses to invent one. Measure your own runs; that is the point.
- Judgment never gets cheaper. If you want everything on Haiku, this is not the skill for you.

## Contributing

`python3 scripts/check.py` runs the repository checks that CI runs on pull requests and on pushes
to `main`: valid frontmatter; the same sections, rules and numbers in English and Spanish; working
internal links; `SKILL.md` under its length limit; and the plugin manifests. CI also runs
`claude plugin validate .` and `claude plugin validate es`. Change both languages in the same
commit.

## Related

- **[Invokard](https://invokard.web.app)** — skill "cards" for Claude and any MCP client. This
  rule is section 1G of **The Orchestrator**, the free card that routes every request to the
  right specialist; if you use that card, the dispatch is already inside it.
- **[CRBRO](https://github.com/Octonove/crbro-memory)** — an open-source MCP server that gives
  your AI persistent memory: neurons, sessions and a search index on your own disk, no account.
  It is where the measured spend of each run ends up when I want to compare weeks.

## License

MIT — do what you want with it, keep the notice. Built by [Octonove](https://github.com/Octonove).
