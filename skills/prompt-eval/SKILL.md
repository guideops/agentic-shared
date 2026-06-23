---
name: prompt-eval
description: "Evaluate and iterate on system prompts. Tests against sample inputs, scores output quality, identifies failure modes, and suggests improvements."
metadata:
  hermes:
    category: ai-ml
---

# prompt-eval

**Trigger**: `/prompt-eval <prompt or file>` or "evaluate this prompt", "test my prompt", "score prompt"
**Domain**: ai-ml
**Automation**: local (on-demand)

## Description
Evaluate and iterate on system prompts. Tests against sample inputs, scores output quality, identifies failure modes, and suggests improvements.

## Instructions
1. Accept prompt (inline or file path) + optional test cases.
2. If no test cases provided, generate 5 diverse test inputs (happy path, edge cases, adversarial).
3. Run prompt against each test case via Codex API (model: `Codex-haiku-4-5` for evals — cost-efficient).
4. Score each output on:
   - **Relevance** (1-5): Does output answer the input?
   - **Format** (1-5): Does output match expected format?
   - **Safety** (1-5): Any harmful/hallucinated content?
   - **Consistency** (1-5): Same prompt, different run = similar output?
5. Identify failure patterns across test cases.
6. Generate improved prompt variant addressing failure modes.
7. Re-run improved prompt — compare scores.
8. Save eval results to `domains/ai-ml/evals/YYYY-MM-DD-<prompt-name>.json`.
9. Log findings to `domains/ai-ml/learnings.md`.

## Input
`/prompt-eval "You are a research assistant. Summarize this article in 3 bullet points."`
Or: `/prompt-eval --file prompts/research-system.md`
Or: `/prompt-eval --file prompts/research.md --cases test-cases/research.json`

## Output
```json
{
  "prompt_name": "research-system",
  "date": "YYYY-MM-DD",
  "model": "Codex-haiku-4-5",
  "test_cases": 5,
  "scores": {
    "relevance": 4.2,
    "format": 3.8,
    "safety": 5.0,
    "consistency": 4.0,
    "overall": 4.25
  },
  "failure_modes": [...],
  "improved_prompt": "..."
}
```

## Automation
None — on-demand. Integrate into agent-builder workflow as validation step.
