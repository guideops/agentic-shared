# agentic-shared — global skill/agent/command library

Cross-tool, cross-project library shared by **Claude Code**, **Codex**, and
**Hermes**. A skill placed in `skills/<name>/SKILL.md` (agentskills.io frontmatter:
`name`, `description`, optional `metadata.hermes.category`) becomes available in all
three agents, in every project, on every machine that clones this repo and links it.

```
skills/     # SKILL.md skills (one dir per skill)
agents/     # portable subagent defs (some need per-tool wrappers)
commands/   # slash-command / prompt defs
```

## Sync workflow

- **Pull updates:** `git pull` here.
- **Add/edit a skill:** edit under `skills/`, then `git add -A && git commit && git push`.
- Sync is **git only** — never Syncthing (it won't carry symlinks). Keep secrets OUT.

## Server (already wired — `/opt/agentic/shared`)

```bash
ln -sfn /opt/agentic/shared/skills   ~/.claude/skills
ln -sfn /opt/agentic/shared/agents   ~/.claude/agents
ln -sfn /opt/agentic/shared/commands ~/.claude/commands
ln -sfn /opt/agentic/shared/skills   ~/.codex/skills
ln -sfn /opt/agentic/shared/skills   ~/.hermes/skills/shared
```

## Laptop bootstrap

### 1. Clone
```bash
git clone git@github.com:guideops/agentic-shared.git   # pick a stable path, e.g. ~/code/agentic-shared
```

### macOS / Linux laptop
Same symlink commands as the server, pointing at your clone path:
```bash
S=~/code/agentic-shared
ln -sfn "$S/skills" ~/.claude/skills
ln -sfn "$S/agents" ~/.claude/agents
ln -sfn "$S/commands" ~/.claude/commands
ln -sfn "$S/skills" ~/.codex/skills
ln -sfn "$S/skills" ~/.hermes/skills/shared
```

### Windows laptop (cmd.exe **as Administrator** — junctions, not symlinks)
```bat
set S=C:\Users\pawar\code\agentic-shared
mklink /J "C:\Users\pawar\.codex\skills"          "%S%\skills"
mklink /J "C:\Users\pawar\.hermes\skills\shared"  "%S%\skills"
mklink /J "C:\Users\pawar\.claude\commands"       "%S%\commands"
mklink /J "C:\Users\pawar\.claude\agents"         "%S%\agents"
```
> **Caveat:** on Windows `C:\Users\pawar\.claude\skills` is often **plugin-owned** —
> do NOT junction over it wholesale or you'll clobber plugin-managed skills. Either
> junction individual skill dirs *inside* it, or rely on Hermes for the gateway and
> use project-level `.claude/skills` per repo. Codex/Hermes junctions above are safe.

See `agentic-workspace/plans/26-remote-control-plane-and-services.md` (Phase 4) for
the full rationale and the config-layering (global vs project) rules.
