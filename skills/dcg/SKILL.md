---
name: dcg
description: "Destructive Command Guard is installed on this box as a PreToolUse hook for Claude Code, Codex, and Hermes. Use when a shell command is BLOCKED by dcg, when deciding whether a command is safe to run, or when tuning what dcg blocks (packs, allowlist, custom block rules)."
---

# dcg — Destructive Command Guard

`dcg` intercepts every Bash/terminal command from Claude Code, Codex CLI, and
Hermes **before** it runs and blocks destructive ones. It is already installed
and wired — this skill is about working with it, not installing it.

## When a command gets BLOCKED

You will see `BLOCKED by dcg` with a reason and a rule ID. Do this, in order:

1. **Believe it.** The default is allow; a block means a rule actually matched.
   Re-read the command — a typo or an over-broad path is the usual cause.
2. **Use the safe alternative.** Every denial prints one. `git stash` instead of
   `git reset --hard`, `>>` instead of `>`, and so on.
3. **Use a non-shell tool.** dcg only sees Bash. Writing or truncating a file is
   almost always better done with the Write/Edit tool, which dcg does not gate.
4. **If it is a genuine false positive**, tell the user what fired and let them
   choose. Do not silently bypass.

Never wrap a blocked command in `DCG_BYPASS=1`, base64, or an inline script to
get past the guard. Bypassing without asking defeats the point of the tool.

## Escape hatches (user's call, not yours)

| Method | Scope | Command |
|---|---|---|
| One-shot bypass | single command | `DCG_BYPASS=1 <command>` |
| Allow-once code | single command | `dcg allow-once <code>` (code is printed in the denial) |
| Permanent allowlist | rule or pattern | `dcg allowlist add <rule-id> -r "reason"` |

## Useful commands

```bash
dcg test "<command>"      # would this be blocked?
dcg explain "<command>"   # why, with the rule and the safer alternative
dcg doctor                # verify hook is registered in every agent
dcg packs                 # what is enabled
dcg config                # effective config and where it came from
dcg stats                 # what has been blocked lately
dcg suggest-allowlist     # allowlist candidates from real history
```

Before running anything you suspect is destructive, `dcg test` it first — it is
sub-millisecond and costs nothing.

## This workspace's configuration

Config: `/root/.config/dcg/config.toml`. Binary: `/usr/local/bin/dcg` (built
from source, v0.7.5+).

Wired into:

| Agent | Where |
|---|---|
| Claude Code (main) | `/root/.claude/settings.json` → `PreToolUse` `Bash\|PowerShell` |
| Claude Code (acct2) | `/root/.claude-acct2/settings.json` |
| Codex CLI | `/root/.codex/hooks.json` → `PreToolUse` `Bash` |
| Hermes Agent | `/root/.hermes/config.yaml` → `hooks.pre_tool_call`, matcher `terminal` |

Packs on beyond the defaults (core.git, core.filesystem, system.disk):
`database.postgresql`, `database.sqlite`, `database.supabase`,
`containers.docker`, `containers.compose`, `system.services`, `remote.rsync`,
`package_managers`.

### Local tuning you should know about

- **`> /root/...` is a warning, not a block.** HOME is the workspace on this
  box, so the default "no truncating redirect under $HOME" rule would fire on
  ordinary file writes. It is downgraded to `warn`.
- **Hard blocks replace it on the paths that matter:** shell/ssh dotfiles,
  agent configs (`.claude`, `.claude-acct2`, `.codex`, `.hermes`), `/etc/`, the
  Obsidian vault, and the shared skills library.
- **Extra local rules:** recursive deletes inside the Syncthing-synced vault,
  deleting/truncating live Hermes or Codex `.db`/`.sqlite` files, and
  `systemctl disable|mask` on caddy / headscale / tailscaled / cli-proxy-api /
  aura / runway / syncthing.
- **Known false positive:** custom block patterns in `[overrides] block` are raw
  regex and are *not* context-aware. Mentioning one of those paths inside a
  quoted string (a `grep`, a `printf`, a heredoc) can trip a block even though
  nothing destructive would run. Built-in pack rules do not have this problem.
  Workaround: put the data in a file with the Write tool instead of inlining it.

### Adding a rule

Edit `[overrides] block` in `/root/.config/dcg/config.toml`:

```toml
{ pattern = "<regex>", reason = "<what the user should do instead>" },
```

Then `dcg test "<the command>"` to confirm it fires, and `dcg doctor` to confirm
the config still parses. Prefer enabling a real pack over hand-writing regex —
`dcg packs` lists 50+.

## Reference

- `reference/upstream-skill.md` — upstream skill doc (architecture, pack system)
- `reference/upstream-agents.md` — upstream contributor/agent guide
- Repo: https://github.com/Dicklesworthstone/destructive_command_guard
