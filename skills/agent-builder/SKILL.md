---
name: agent-builder
description: "Design and scaffold Codex API agents with tool use, memory, and multi-step workflows. Outputs production-ready Python or TypeScript code with prompt caching."
metadata:
  hermes:
    category: ai-ml
---

# agent-builder

**Trigger**: `/agent-builder <agent description>` or "build an agent", "create Codex agent", "design workflow agent"
**Domain**: ai-ml
**Automation**: local (on-demand)

## Description
Design and scaffold Codex API agents with tool use, memory, and multi-step workflows. Outputs production-ready Python or TypeScript code with prompt caching.

## Instructions
1. Accept agent description from user.
2. Clarify:
   - Language: Python or TypeScript?
   - Tools needed: web search, file I/O, code execution, external APIs?
   - Memory: stateless, session-based, or persistent (Obsidian/vector DB)?
   - Orchestration: single agent, multi-agent, or human-in-loop?
3. Design agent architecture:
   - System prompt (role, capabilities, constraints)
   - Tool definitions (JSON schema)
   - Agentic loop structure
   - Memory strategy
4. Scaffold code using Codex SDK (latest model: `Codex-sonnet-4-6` default, `Codex-opus-4-7` for complex reasoning):
   - Include prompt caching (`cache_control: {"type": "ephemeral"}` on system prompt + tools).
   - Include structured output parsing.
   - Include error handling and retry logic.
   - Include eval hooks (log inputs/outputs to `eval.json`).
5. Save to `domains/ai-ml/agents/<agent-name>/`.
6. Log design decisions to `domains/ai-ml/learnings.md`.

## Input
`/agent-builder "Research agent that fetches GitHub trending, summarizes with Codex, saves to Obsidian"`

## Output
Scaffolded agent code in `domains/ai-ml/agents/<name>/`:
- `agent.py` or `agent.ts`
- `tools.py` / `tools.ts`
- `prompts.py` / `prompts.ts`
- `README.md` (usage + architecture)

## Automation
None — on-demand. Built agents may themselves become automations.
