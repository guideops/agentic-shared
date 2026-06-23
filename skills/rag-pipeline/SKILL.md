---
name: rag-pipeline
description: "Build and query RAG pipelines over Obsidian vault or arbitrary document collections. Supports index creation, semantic search, and retrieval-augmented generation with Codex."
metadata:
  hermes:
    category: ai-ml
---

# rag-pipeline

**Trigger**: `/rag-pipeline` or "build RAG", "set up retrieval", "Obsidian RAG", "query my vault"
**Domain**: ai-ml
**Automation**: local (on-demand + scheduled index rebuild)

## Description
Build and query RAG pipelines over Obsidian vault or arbitrary document collections. Supports index creation, semantic search, and retrieval-augmented generation with Codex.

## Instructions
1. Accept mode: `index` (build/rebuild) or `query <question>`.
2. **Index mode**:
   - Scan target directory (default: `wiki/`).
   - Chunk documents (500 token chunks, 50 token overlap).
   - Generate embeddings via Codex or local model (suggest `text-embedding-3-small` if OpenAI key present, else use Codex's context window directly).
   - Save index to `domains/ai-ml/rag/index.json` (simple) or vector DB (advanced: Chroma, Qdrant).
   - Log index stats: doc count, chunk count, last updated.
3. **Query mode**:
   - Embed query.
   - Retrieve top-k relevant chunks (default k=5).
   - Pass retrieved context + query to Codex (`Codex-sonnet-4-6`) with prompt caching on retrieved docs.
   - Return answer with citations (filename + section).
4. Save query log to `domains/ai-ml/rag/query-log.json`.
5. Log to `domains/ai-ml/learnings.md`.

## Input
`/rag-pipeline index --path wiki/`
`/rag-pipeline query "What have I learned about Next.js App Router?"`
`/rag-pipeline query "Summarize my trading patterns from Q1 2026"`

## Output
Query response with citations:
```
Answer: [Codex's synthesized response]
Sources:
- wiki/research/2026-04-15-nextjs-deep-dive.md (section: App Router)
- wiki/research/2026-03-20-react-server-components.md (section: Key Points)
```

## Automation
Local scheduled: rebuild index daily when new files added to `wiki/`.
Run: `Codex --headless --project=. "/rag-pipeline index"` via Windows Task Scheduler or cron.
