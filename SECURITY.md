# Security

## What runs on your machine

Installing a plugin from this repository can execute code on every message or turn. This is everything that does, and nothing
else does. All of it is plain bash or Python in this repository, readable before you install; none of it downloads code at
runtime, calls a model, or makes a network call.

| Plugin | Trigger | What runs | Reads | Writes |
|---|---|---|---|---|
| `model-protocol` | every user message (`UserPromptSubmit`) | `hooks/model-protocol.sh` | `.claude/claude-workbench.conf`, `.claude/model-protocol.md`, `~/.claude/model-protocol.md` | nothing; prints the reminder |
| `git-identity` | session start; before each Bash/PowerShell command | `hooks/git-identity.sh` | `~/.config/claude-workbench/git-identity`; the repo's git config and log (read-only `git` commands) | nothing; it may block `git commit`/`git push` (exit 2) |
| `continuum` | end of each turn (`Stop`, `SubagentStop`) | `launcher.sh` → `hooks/log_turn.py` | the turn's transcript | the day's log in the vault; unless `autocommit` is off, one commit in the **vault's** repo (never a push) |
| `continuum` | MCP server, while Claude Code runs | `git -c alias.continuum=!sh continuum launcher.sh mcp/server.py` | `.md` files inside the vault | `.md` files inside the vault, append-only |
| `catalog` | none | skills only: Claude runs `claude plugin …` and `git` commands you approve | the local marketplace copy, `.claude/claude-workbench.conf` | with your yes: installs plugins, merges `.claude/settings.json` |
| `model-protocol`, `continuum`, `git-identity`, `catalog` | when you invoke their skills | Claude edits `CLAUDE.md`, `.gitignore`, `.claude/claude-workbench.conf`, the vault | those files | only between `claude-workbench:<plugin>` markers and after a diff you approve |

Boundaries the code enforces:

- `continuum` writes **only inside the vault**, only `.md`, never outside it or in hidden folders, and never deletes or rewrites
  existing text.
- `git-identity` hooks never write. The skill writes the machine file and the repo's local identity, with your yes; rewriting
  already-pushed commits needs an explicit yes and a forced push with lease.
- No plugin pushes. The only `git push` in this ecosystem is yours.

To see what is registered after installing, open `/hooks` in Claude Code. To stop any of it:
`claude plugin disable <plugin>@claude-workbench`.

## Updates

Auto-update is off for this marketplace unless you turn it on. Each plugin's version is pinned in its `plugin.json`, so a commit
does not reach you until the version changes; read the plugin's `CHANGELOG.md` before running `claude plugin update`.

## Reporting a vulnerability

Please do **not** open a public issue. Use GitHub's private vulnerability reporting: the **Security** tab of the repository →
**Report a vulnerability**. Include the plugin and version, what you observed and, if possible, the smallest way to reproduce it.
Expect an answer within a few days; this is a personal project maintained by one person.

Out of scope: behavior of Claude Code itself, and of third-party marketplaces or plugins.

## What this repository does about leaks

Commits are checked locally by `tools/barrier/` against a private list, and CI runs gitleaks on every push and pull request.
If you find a secret or private data in the history, report it through the channel above.
