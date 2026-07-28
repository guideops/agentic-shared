---
name: hindsight-memory
description: 'Manual verbs for the shared Hindsight memory: /remember <fact> stores a durable fact; /recall <query> searches it. Works in Claude Code, Codex, and Hermes.'
---

# Hindsight Memory

Use the local Hindsight API at `http://127.0.0.1:8888` with bank `hermes`.

For `/remember <fact>`, retain the fact with your agent name and the `manual` tag:

```sh
curl -sS -X POST 'http://127.0.0.1:8888/v1/default/banks/hermes/memories' -H 'Content-Type: application/json' --data '{"items":[{"content":"<fact>","tags":["agent:<your-name>","manual"]}],"async":true}'
```

For `/recall <query>`, search the shared bank with this request:

```sh
curl -sS -X POST 'http://127.0.0.1:8888/v1/default/banks/hermes/memories/recall' -H 'Content-Type: application/json' --data '{"query":"<query>","budget":"mid","max_tokens":2048}'
```

Report the stored or retrieved text to the user.
