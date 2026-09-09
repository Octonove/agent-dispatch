---
name: agent-dispatch
description: "Always-on rule for any client that can launch subagents (Claude Code, Cursor, Antigravity…). Before delegating, it decides whether to delegate at all — the default is no — then how many (starting at zero), how to split the work, and which model and effort each subagent gets, by the type of task and never by the importance of the project. Mechanical work (translations, listing, measuring, running scripts) goes to a small model; bounded analysis to a mid model; design, code, decisions and the final review stay on the session's model. Declares the split before launching and reports the measured spend after."
---

# Agent Dispatch — which model runs each subagent

You are running inside a client that can launch subagents (Claude Code's `Agent` and `Workflow`
tools, Cursor's background agents, or similar). By default every subagent inherits the model you
have selected for the session, so a four-language translation costs the same per token as an
architecture decision. This rule fixes that. It governs one thing only: **the spend on agents**.
It never changes the model of the conversation itself.

Apply it every time work is about to leave the conversation. Apply it in order.

## 0. Should this be delegated at all?

Delegate only if one of these holds:

- **independent parts** that genuinely run at the same time and save wall-clock;
- **more reading than fits in one context** (dozens of files, transcripts, long outputs).

Otherwise do the work inline. A subagent does not see this conversation: it costs its whole
context plus the briefing you write for it, and its answer still has to be verified. Two things
are never a reason to delegate: checking something a command can check (`curl`, `grep`, reading
a file), and getting a second opinion on work that is already verified — where direct evidence
exists, the evidence decides.

## 0b. How many? Start at zero

Zero is the normal answer: most work is inline work. One well-briefed subagent covers most of
what is worth delegating at all. Several only when each one owns a slice no other one can cover
— and you name those slices before launching. If two of them sound alike as you write the split,
one is redundant: drop it. A fleet is not thoroughness; it is the same answer paid for several
times.

## 1. Split the work and classify each part by TYPE

Write the subtasks down. Classify each one by what kind of work it is — **never by how important
the project is**. Three tiers:

| Tier | What it is | Examples |
|---|---|---|
| **Mechanical** | No judgment; the output is right or wrong and easy to check | translations of fixed strings, listing files, counting, measuring sizes, transcribing an output verbatim, running an already-written script and reporting what it prints, checking that a JSON or a manifest parses, extracting fields with a fixed format, formatting, renaming |
| **Bounded analysis** | Reasoning inside a clear frame someone else set | summarizing a module, mapping dependencies, writing tests from a clear spec, applying one mechanical change across many files, comparing two versions of a text, filling a checklist |
| **Judgment** | Deciding, designing, or anything that ships without another review | architecture, writing the code that decides how something works, choosing between options, synthesizing a report, the final review that checks everything fits together, anything published or sent to a client |

## 2. Assign a model and an effort per tier

| Tier | Model | Effort |
|---|---|---|
| Mechanical | **small** (e.g. Haiku) | low |
| Bounded analysis | **mid** (e.g. Sonnet) | medium |
| Judgment | **the session's model** (e.g. Fable 5.1, Opus) | high |

The model names are examples: use whatever tiers your client offers. If you hesitate between two
tiers, the lower one plus a verification by the upper one is cheaper than the upper one used
blind.

If your client does not let you choose a model or an effort per subagent, do not pretend you
did: apply everything else (whether to delegate, how many, in what order, briefing, declare,
measure) and say so in one line.

## 3. Guardrails that are not negotiable

1. **The final reviewer and whoever synthesizes never get cheapened.** The saving comes from
   the mechanical work, never from what keeps a mistake from shipping.
2. **If a small agent fails or returns something doubtful, the task moves up one tier.** It is
   not retried on the same model.
3. **Fewer agents.** One reviewer with a clear checklist beats three vague ones. One translator
   per language, not two "just in case". No agent whose only job is to double-check another's
   conclusion. Mechanical agents run as a pipeline, not as a barrier, unless the next step needs
   all their results at once.
4. **Every subagent gets a briefing and a return contract.** It does not see this conversation,
   so tell it what it needs; and tell it what to hand back — a verdict, at most five findings,
   file paths instead of pasted contents.

## 4. Declare before, measure after

Before launching, one line the user can read:

```
Dispatch: 9 agents · 3 session-tier (design, code, final review) · 1 mid (tests) · 5 small (4 translations, lint + tests run)
```

When the work is done, report the spend the tool gives back, split between small and large.
If the tool gives no figure, write **"not measured"**. Never invent a saving: without a figure
there is no saving, only the feeling of one.

## 5. The final review

The last agent, or you inline, is always judgment-tier and checks that the parts fit together:
every string referenced by the code exists in every locale, permissions match what the code
uses, the tests the mechanical agent ran are the tests that matter, nothing was silently
skipped. This is where the small models' work is verified, once, by someone who can tell.

## Worked example: a small Chrome extension

Prompt: *"Build a small Chrome extension that highlights prices on any page and converts them to
euros. Popup with a currency selector. UI in English, translated into Spanish, French, German and
Italian. Tests for the conversion."*

| # | Subtask | Tier | Model · effort |
|---|---|---|---|
| 1 | Design: manifest v3, files, permissions, how the content script and the popup talk | judgment | session model · high |
| 2 | Write the code: content script, popup, service worker, conversion module | judgment | session model · high |
| 3 | Write the conversion tests from the spec | bounded analysis | mid · medium |
| 4–7 | Translate `messages.json` into ES, FR, DE, IT (one agent each) | mechanical | small · low |
| 8 | Validate the manifest, run lint and the tests, report the output verbatim | mechanical | small · low |
| 9 | Final review: locales complete, permissions match the code, tests green | judgment | session model · high |

Without this rule: 9 agents on the session's model. With it: 3 on the session's model, 1 on the
mid model, 5 on the small one. The extension is the same; the judgment stayed where it matters.

## Where this comes from

This rule is section 1G of **The Orchestrator**, the free routing card of
[Invokard](https://invokard.web.app). If that card is loaded, the rule already applies and you
do not need this file. This is the standalone version for anyone who only wants the dispatch.
