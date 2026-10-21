---
name: dream-review
description: Run or inspect the Agentic Workspace Dream Review through its server-owned API, including read-only /dream doctor checks. Reviews agent improvements and work outcomes with explicit coverage and concrete proposals for approval.
metadata:
  hermes:
    category: research
---

# Dream Review

Use for `/dream`, “run dream”, or explicit Dream Review status/doctor requests in an Agentic Workspace deployment. This skill is an API client, not an independent review author. Its Steps mirror `.claude/commands/dream.md` in the workspace.

## Steps

1. Resolve the workspace from `$AGENTIC_WORKSPACE`, the current checkout containing `server/dream/runner.js`, or `/root/agentic-workspace`. Use the running AW API at `$AW_URL` or `http://localhost:3001`. If unavailable, report the blocker; do not invent a review or start a separate author agent.

2. On `/dream doctor`, use read-only checks only: `GET /api/dream`, `hermes cron status`, and `hermes cron list`. Report last successful generation date, latest run status/errors, source coverage, desired schedule versus actual native job state, scheduler heartbeat and effective timezone. A quiet successful review, partial coverage, failed run and missing run are distinct. Do not POST, repair cron, create findings, or write files in doctor mode.

3. On `/dream` or an explicit request to run a review, enqueue once with `POST /api/dream/run` and `Accept: application/json`. The response supplies `runId`, `attached`, and `statusUrl`. Poll that server-owned status URL through a terminal state (`succeeded`, `partial`, `failed`, `cancelled`). Attaching to an existing run is correct; do not create another scheduler or duplicate author process. If observation is interrupted, inspect the same run ID before retrying. Do not blindly requeue failed or timed-out work.

4. Read `GET /api/dream` after terminal completion. Summarize only validated findings with their source evidence, missing agents/data, full generation date, and prepared next step. Zero findings is valid. A partial run must say what is missing; a failed run must preserve the previous review's original date. Do not call an opened/sent chat draft a completed change or an observed improvement.

5. Dream gives agent improvement and useful work outcomes equal eligibility. It reviews Hermes, Claude and Codex within explicit source coverage, respects their existing native learning, retains durable dismissals, and evaluates results weekly when enough evidence exists. It does not infer answer quality from note age, context occupancy from cumulative tokens, or business value from completed tasks/files. No external research or paid upgrade is required.

6. The server owns review records, authoring, decision/approval/execution records, run logging, and ACL-routed vault digests. Never write `dream-latest.json`, a shared author output, a digest, a norms file, or server decision state from this skill. Never copy old signal packs into a new review. Do not append another runs.json/learnings row: terminal logging belongs to the server.

7. Prepare concrete changes for operator review through the existing unsent Agent Chat draft or a trusted typed action. Reading evidence and preparing a proposal are authorized review work; changing skills, memory, instructions, routing, tasks or deliverables requires approval of the concrete scope. No model-authored shell command/path may become an executor. Opening a draft does not send it. Existing native memory/skill settings stay owned by their agent.
