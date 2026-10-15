# Dispatch decisions: whether to delegate, how many, which model

Short, realistic cases, each with the decision, the dispatch line and the rule it rests on
(section numbers refer to [`SKILL.md`](../SKILL.md)). At the end, the model names for each client.

## No delegation

### 1. Rename a function across the repository

> Rename `getUser` to `fetchUser` everywhere and make sure nothing breaks.

`grep` finds every call site, the edit is inline and the test suite says whether anything broke.
A subagent would pay for a whole context to do what two commands already do (section 1).

```
Dispatch: 0 agents · inline
```

### 2. A second opinion on a fix that already passes

> The fix is in and the tests pass. Get another agent to double-check it.

The evidence exists: the test that failed now passes and the diff is short enough to read. A
second agent would re-derive what the test already proved (section 1, guardrail 3). Read the diff
inline; if a path is not covered, write the test that covers it.

```
Dispatch: 0 agents · inline (evidence: the failing test now passes)
```

### 3. Why is CI red?

> CI is red on my pull request. Find out why.

One job log of a few hundred lines fits in context. Read it inline and rerun the failing command.
Delegation only starts to make sense when the log no longer fits (case 5).

```
Dispatch: 0 agents · inline
```

## One agent

### 4. Map a large legacy module before a refactor

> Before we touch billing, I need to know how the session token flows through `billing/`
> (about 140 files).

More reading than fits in one context, so one agent. Mapping dependencies inside a frame you set
is bounded analysis: mid model. The refactor design stays inline; it is judgment, and it needs the
map, not the 140 files.

```
Dispatch: 1 agent · 1 mid (map billing/) · inline: refactor design, code, final review · cap: no loop
```

The brief:

> - **Goal:** map where `SessionToken` is created, read, passed and stored inside `billing/`.
> - **Context:** entry points are `billing/api/*.py`; the token class is in `billing/auth.py`.
> - **Constraints:** read only; do not edit files or start services.
> - **Review focus:** every hop has a file and a line.
> - **Output:** a verdict (map complete or not), the hops as `file:line → file:line`, one per
>   line, plus at most 5 surprises.
> - **Done:** every `SessionToken` reference that `grep` finds in `billing/` is in the map or
>   explained.

### 5. Cut a huge log down to the failures

> Last night's end-to-end run printed 40,000 lines. Which tests failed, and why?

Too long to read inline, and pulling the failures out needs no judgment: one small agent. It
returns each failing test with its first error line and the path of the log. The diagnosis stays
inline.

```
Dispatch: 1 agent · 1 small (extract failures) · inline: diagnosis · cap: no loop
```

## Several agents, one slice each

### 6. The same migration in three independent packages

> Move `packages/web`, `packages/api` and `packages/cli` from `date-lib` v2 to v3 (the codemod is
> written), then decide what replaces the removed `parseLoose`.

The three packages do not import each other: three slices that genuinely run at the same time.
Running a written codemod and fixing its fallout inside one package is bounded analysis, so each
gets the mid model. What replaces `parseLoose` is judgment: inline, once, after the three reports.

```
Dispatch: 3 agents · 3 mid (web, api, cli) · inline: parseLoose decision, final review · cap: 1 fix round per package
```

### 7. "Three reviewers: security, performance, style"

> Review this pull request for security, performance and style, with three reviewers.

Three reviewers of the same diff do not own different slices; they reread the same lines
(section 2, guardrail 3). Propose one reviewer with a checklist that covers the three, or the
review inline if the diff fits in context. If the diff is too big, split it by files, not by
point of view. If the user still wants three, run three and say so in the dispatch line.

```
Dispatch: 0 agents · inline (one review, security + performance + style checklist)
```

### 8. A feature with tests and translations

The Chrome extension in [`chrome-extension.md`](chrome-extension.md): design, code, lint and the
final review inline; the tests (mid) and four translations (small) in parallel.

```
Dispatch: 5 agents · 1 mid (tests) · 4 small (translations) · inline: design, code, lint + tests, final review · cap: 1 fix round
```

## When something goes wrong

### 9. A small agent returns something doubtful

The German translator writes `$BETRAG$` where `en` has `$AMOUNT$`. Its one retry goes to the mid
model, with the same brief plus the finding; it is not run again on the small one (guardrail 2).
If the mid model fails too, the German file is done inline.

### 10. The session already runs the mid model

With Sonnet as the session's model there is nothing above it: bounded analysis and judgment both
run on Sonnet, and mechanical work still goes to Haiku (section 4). The dispatch line says so.

```
Dispatch: 3 agents · 3 small (translations) · inline on the session's model (Sonnet): code, review · cap: 1 fix round
```

## Model names per client

The tiers are the rule; the names change by client and version. Rows checked against each
vendor's documentation in October 2026. Only the Claude Code row was tried in this repository;
the others are untested, so check them against your client's version.

| Client | Small (mechanical) | Mid (bounded analysis) | Judgment | Effort per subagent | Where the spend shows |
|---|---|---|---|---|---|
| Claude Code, `Agent` tool | `model: "haiku"` | `model: "sonnet"` | omit `model` and `effort`: both inherit the session's if the subagent's definition sets neither; if `CLAUDE_CODE_SUBAGENT_MODEL` is set, pass the session's alias, e.g. `model: "opus"` | `effort` per call (`2.1.292`+), or `effort:` in `.claude/agents/*.md` | token count in each subagent's result; `/usage` |
| Cursor | subagent in `.cursor/agents/<name>.md` with `model: fast` or a small model ID | same file, a mid model ID | `model: inherit` | not documented | usage dashboard, per request |
| Codex CLI | subagent TOML in `.codex/agents/` with `model` | same, a mid model | omit `model` | `model_reasoning_effort` | not checked |
| Gemini CLI, GitHub Copilot, OpenCode | subagent definition with a `model` field | same, a mid model | omit it, or `inherit` | not documented | not checked |
| No per-subagent model | none | none | the session's | none | apply sections 1, 2 and 5 to 7, and write "model not selectable" in the dispatch line |
