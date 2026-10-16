---
name: doc-comments
description: "Read and act on the comments the operator left in the Agentic Workspace Docs page (/docs). Use when the operator says they left comments, 'check my docs comments', 'revise the doc', 'address my feedback on <doc>', or pastes a Docs 'Send to chat' draft. Lists open comments with their quoted text and source line, then edit the doc and resolve each comment."
metadata:
  hermes:
    category: workspace
---

# doc-comments

The operator reads agent-written Markdown in **Agentic Workspace → Docs** (`/docs`),
highlights text and leaves comments. Comments wait until the operator asks; nothing
runs automatically. This skill is how any agent (Claude Code, Codex, Hermes) picks
them up.

## Where things live

- **Docs root** (the files): the shared output folder — `HERMES_DOCS_DIR`, else
  `~/Documents/Hermes` (`/root/Documents/Hermes` on the VPS). Doc paths in comments
  are relative to this root.
- **Comments**: `server/data/rubric.json` inside the Agentic Workspace checkout
  (`/root/agentic-workspace` on the VPS). Read them with the script below — don't
  hand-edit the JSON.

## Steps

1. Find the checkout: `$AW_REPO`, else `/root/agentic-workspace`, else the current
   repo if it contains `scripts/doc-comments.js`.
2. List open comments (plain text, one line per comment with its id):
   ```bash
   node "$AW/scripts/doc-comments.js"              # every doc
   node "$AW/scripts/doc-comments.js" "<doc path>" # one doc
   node "$AW/scripts/doc-comments.js" --root       # print the docs root
   ```
   Each line reads `Line N: "<highlighted text>" → "<comment>" [id …]`.
3. Open the doc at `<docs root>/<doc path>`, address each comment at its line, and
   save the file in place. The Docs page picks up the change within seconds.
4. Resolve each addressed comment:
   ```bash
   node "$AW/scripts/doc-comments.js" --resolve <id>
   ```
   Leave a comment open (and say why) if it needs the operator's decision.
5. Reply with a short list: each comment → what you changed.

## Rules

- Only act when the operator asks. Never poll or auto-run on new comments.
- Edit only the doc the comments are on unless a comment asks otherwise.
- If a comment needs paid tools or generation, confirm cost with the operator first.
- HTTP alternative (same data, needs the dashboard password if one is set):
  `GET /api/docs/comments/summary?path=<doc path>` on the AW server.
