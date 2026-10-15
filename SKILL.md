---
name: agent-dispatch
description: "Decides whether to delegate to subagents at all (default: no), how many (start at zero) and which model and effort each one gets, by task type and never by project importance. Use before launching any subagent, parallel agents, background agent, workflow or review loop, or when a task could fan out. Mechanical work goes to a small model, bounded analysis to a mid model, judgment stays on the session's model. Declares the split and the loop cap first; reports the measured spend after."
---

# Agent Dispatch — which model runs each subagent

Unless told otherwise, a subagent runs on the session's model, so a four-language translation
costs the same per token as an architecture decision. This rule governs one thing: **the spend
on agents**. It never changes the model of the conversation. Apply it, in order, every time work
is about to leave the conversation: a subagent, parallel agents, a workflow, a loop.

## 1. Delegate at all? Default: no

Delegate only if one of these holds:

- **independent parts** that genuinely run at the same time and save wall-clock;
- **more reading than fits in one context** (dozens of files, transcripts, long logs).

Otherwise work inline. A subagent does not see this conversation: it costs its whole context
plus the brief you write, and its answer still has to be verified. Never a reason to delegate:
checking what a command can check (`grep`, `curl`, running the tests, reading a file), or a
second opinion on work that is already verified. Where direct evidence exists, it decides.

## 2. How many? Start at zero

Zero is the normal answer. One well-briefed subagent covers most of what is worth delegating.
Several only when each owns a slice no other covers; name the slices before launching. If two
sound alike, drop one: a fleet is the same answer paid for several times.

## 3. Classify each subtask by type

Write the subtasks down and classify each by the kind of work, **never by how important the
project is**:

| Tier | What it is | Examples |
|---|---|---|
| **Mechanical** | No judgment; the output is right or wrong and easy to check | translating fixed strings, listing, counting, extracting fields in a fixed format, formatting, renaming, cutting a long log down to its errors |
| **Bounded analysis** | Reasoning inside a frame someone else set | summarizing a module, mapping dependencies, writing tests from a clear spec, one mechanical change across many files, comparing two versions, filling a checklist |
| **Judgment** | Deciding, designing, or anything that ships without another review | architecture, the code that decides how something works, choosing between options, synthesizing a report, the final review, anything published or sent to a client |

## 4. Model and effort per tier

| Tier | Model | Effort | Claude Code `Agent` call |
|---|---|---|---|
| Mechanical | **small** (Haiku) | low | `model: "haiku"`, `effort: "low"` |
| Bounded analysis | **mid** (Sonnet) | medium | `model: "sonnet"`, `effort: "medium"` |
| Judgment | **the session's model** | high | no `model` (it inherits), `effort: "high"` |

- The names are examples: use the tiers your client offers. Never go above the session's model;
  if the session already runs the mid model, bounded analysis and judgment both stay on it.
- Unsure between two tiers: take the lower one. The final review (section 7) checks it.
- If the client cannot set the model or the effort per subagent (in Claude Code, `effort` needs
  version `2.1.292` or later), do not pretend you did: apply the rest and say so in the dispatch
  line.

## 5. Guardrails that are not negotiable

1. **The final reviewer and whoever synthesizes never get cheapened.** The saving comes from the
   mechanical work, never from what keeps a mistake from shipping.
2. **Failure moves the task up a tier.** A small or mid agent that fails or returns something
   doubtful gets its retry one tier up, never on the same model. At the session tier, the work
   comes back inline.
3. **Fewer agents.** One reviewer with a clear checklist beats three vague ones. One translator
   per language, not two "just in case". No agent whose only job is to re-check another's
   conclusion. Hand each mechanical result to the next step as it arrives, unless that step needs
   all of them at once.
4. **Every subagent gets a self-contained brief and a return contract.** What is not in the brief
   does not exist for it. The brief carries 6 things: goal; minimum context (paths, decisions
   already made); constraints (what must not be touched, published or run); review focus (what
   the reviewer will check); output format; definition of done. Ask for a verdict, at most 5
   findings, and file paths instead of pasted contents. If you can't write the brief, the task
   isn't ready to delegate.
5. **Every loop declares its cap.** Before any loop or review-and-fix round (agents, workflows,
   a `/loop`), state the success condition and the maximum number of rounds. At most 1 retry of
   the same approach (rule 2 says on which model). A watch loop the user asked for may stay open
   with its stop condition. At the cap no new round opens: every open finding is fixed, parked as
   debt, or rejected with a reason.

## 6. Declare before, measure after

Before launching, one line the user can read, with the cap on it:

```
Dispatch: 5 agents · 1 mid (tests) · 4 small (translations) · inline: design, code, lint + tests, final review · cap: 1 fix round
```

If nothing is delegated, say that instead: "Dispatch: 0 agents · inline". When the work is done,
report the spend the client gives back, per tier (in Claude Code: the token count each subagent
returns, or `/usage`). With no figure, write **"not measured"**. Never estimate a saving: without
a figure there is no saving, only the feeling of one.

## 7. The final review

The last step, inline or by one session-tier agent, checks that the parts fit together: every
string the code uses exists in every locale, permissions match what the code calls, the tests
that ran are the ones that matter, nothing was silently skipped. This is where the small models'
work is verified, once, by someone who can tell.

## Example

*"A Chrome extension that converts prices to euros, with a currency popup, UI in English plus
Spanish, French, German and Italian, and tests for the conversion."* Design and code are one
chain of judgment: inline. Then the tests (mid) and the 4 translations (small, one per language)
run in parallel. Lint and tests are a command and the final review is judgment: inline. That gives
the dispatch line in section 6. More cases and the model names per client:
https://github.com/Octonove/agent-dispatch/blob/main/examples/decisions.md
