---
name: shared-artifact-output
description: "Use when creating standalone deliverables. Save them in /root/Documents/Hermes for the AW Documents gallery."
version: 1.0.0
author: Guide
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [artifacts, documents, output, agentic-workspace, gallery]
---

# Shared Artifact Output

Use this skill whenever the operator asks for a standalone generated deliverable rather than an Obsidian note or source-code change.

## Canonical destination

Write the final artefact under:

```text
/root/Documents/Hermes/
```

Optional subdirectories are allowed, for example:

```text
/root/Documents/Hermes/reports/
/root/Documents/Hermes/html/
/root/Documents/Hermes/videos/
/root/Documents/Hermes/images/
```

The Agentic Workspace Documents gallery reads this directory through its jailed `/api/hermes/documents` API and polls it approximately every five seconds.

## Routing rules

- Standalone HTML, MP4, PNG, JPG, PDF, DOCX, XLSX, JSON, Markdown exports, audio, and similar deliverables go to `/root/Documents/Hermes/`.
- Obsidian notes remain in the configured Obsidian vault, normally under `/opt/agentic/obsidian/vault/Agentic Output/` or the appropriate vault section.
- Source code and project files remain in the active repository.
- Never use `.claude`, `.codex`, `.hermes`, or `/tmp` as the final destination for an operator-facing deliverable.
- Do not place credentials, tokens, private session databases, or other secrets in the shared folder.
- Use a meaningful filename and report the absolute path after writing.

## Gallery metadata contract

For HTML, add these tags inside `<head>`:

```html
<meta name="hermes-title" content="Short title">
<meta name="hermes-description" content="Short description">
```

For Markdown, add frontmatter near the top:

```yaml
---
title: Short title
description: Short description
---
```

For JSON, include a top-level metadata block when practical:

```json
{
  "_hermes": {
    "title": "Short title",
    "description": "Short description"
  }
}
```

Binary files cannot embed metadata, so use a descriptive filename. The gallery will fall back to a humanized filename.

## Verification

After writing:

1. Confirm the file exists under `/root/Documents/Hermes/`.
2. Confirm it is not a hidden file.
3. If practical, query `https://workspace.ts.internal/api/hermes/documents` or use the local API to confirm it is listed.
4. Return the absolute path to the operator.
