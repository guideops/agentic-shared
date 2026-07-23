---
name: align
description: Ask short clarifying questions before starting work to catch wrong assumptions early. /align asks numbered questions with lettered options about the pending task, waits for answers, then proceeds steered. "/align 5" forces exactly 5 questions. Trigger also on "align first", "ask me before you start", "clarify before building".
---

# Align

Before touching the task, interrogate it. Numbered questions, lettered options, wait for answers. Narrows the outcome space so the first attempt lands near the target instead of burning correction prompts.

## When invoked

`/align` applies to the task described in the same message, or — if invoked bare — to the most recent pending request in the conversation. If there is no pending task at all, say so and ask what to align on.

## 1. Decide question count

Default: **you decide from ambiguity**, minimum 2, cap 7.
- Vague one-liner brief → more questions (5–7)
- Detailed spec with one or two gaps → fewer (2–3)
- `/align N` → exactly N questions (clamp to 1–10)

## 2. Qualify every question

Each question must be **decision-changing**: a different answer produces visibly different work. Before asking anything, check whether the answer is already discoverable — in the conversation, the repo, project STATE.md, or vault docs. Never ask what you can look up. Never ask trivia, preferences that don't affect this task, or questions with an obvious conventional default.

Good territory (from most to least commonly missing):
- **Scope** — full build vs prototype vs spec-only; which parts are in/out
- **Ownership / access** — whose account, whose repo, who maintains it after
- **Output format** — file, doc, deployed thing, message draft; where it lives
- **Constraints** — stack, budget, deadline, existing patterns to reuse
- **Human-in-the-loop** — full auto vs confirm-each-step vs confirm-risky-only
- **Edge behavior** — what happens on failure, empty input, conflict

One unknown per question. No compound questions.

## 3. Ask — exact format

Plain text in chat (not AskUserQuestion). End the turn after asking; do not start any work.

```
**1. <Question>?**
- A) <Concrete option>
- B) <Concrete option>
- C) <Concrete option>

**2. <Question>?**
- A) ...
- B) ...
```

Rules:
- 2–4 lettered options per question, each **concrete and mutually exclusive** — no "it depends", no "other" (free text is always implied)
- When genuinely uncertain territory, last option may be `X) Not sure — find out and recommend`
- If you have a recommendation, put it first and mark it `(recommended)`
- Close with: `Answer any way — "1A 2B...", free text, or mix.`

## 4. Parse answers

Accept `1A 2B 3C`, `1a2b3c`, per-line answers, free text, or mixtures. Free text overrides any letter for that question. Unanswered question → use your recommended option and say which default you took. Answer of `X` / "find out" → that becomes a task step: investigate, then recommend before acting on it.

## 5. Restate and proceed

Restate the aligned understanding in **2–3 lines max** — the shape of the deliverable, key choices locked, anything you defaulted. Then start immediately. No "shall I proceed?" — alignment already happened.

## Anti-patterns

- Asking questions then ignoring the answers
- Padding to hit a count — if only 2 things are genuinely ambiguous, ask 2, even under `/align 5`... exception: explicit `/align N` means the user wants N; find the N most decision-changing unknowns
- Generic options ("A) Yes B) No") when specific options would teach the user what the real choice is
- Re-asking something answered earlier in the session
- Using this skill to stall on tasks that are already fully specified — if nothing is ambiguous, say "already aligned, no questions" and go
