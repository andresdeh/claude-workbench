# git-identity (v1.0.0)

| Fact sheet | |
|---|---|
| Solves | A private email ending up in the history of a repo (or a push rejected by GitHub with `GH007`) |
| Components | `SessionStart` hook · `PreToolUse` hook (Bash and PowerShell) · skill `configure` |
| Runs code | **Yes**: bash at session start and before every Bash/PowerShell command (it exits at once if the command is not `git commit`/`git push`) |
| Reads and writes | Reads `~/.config/claude-workbench/git-identity` and the repo's git config and log. The hooks write nothing. The skill writes that file and the repo's local identity, with your yes |
| Requirements | bash and git (on Windows, Git for Windows) |
| Recommended scope | `user` (all projects) |
| Context cost | zero when all is fine; a few lines only when the repo signs with a blocked email or the machine is not configured |
| How to turn it off | `claude plugin disable git-identity@claude-workbench`, or `mode = warn` in `/config` to keep only the warning |

## Why

Many people use a private email as their global git identity and then push to a public host. This plugin is **optional and
neutral**: it protects a list of emails *you* name, with no assumption about which one is private or which host you use.

## What it does

- **At session start**: if the project's repo signs with a blocked email, it tells Claude to suggest fixing it. If the machine is not
  configured, it says so once.
- **Before `git commit` / `git push`** (also with `git -C <path>`): blocks (exit 2) if the repo's identity is blocked or, on a push,
  if any commit about to go out carries a blocked email. Over-blocking can only happen in a repo that already signs with a blocked
  email. With `mode = warn` it lets the command run and only tells Claude.
- **Skill `configure`**: creates the machine file, changes the repo's identity and offers to rewrite commits (already pushed
  ones only with an explicit yes and a forced push with *lease*). If the remote is on GitHub it suggests the noreply address.
- **Not covered**: commits made outside Claude Code. On GitHub the option "Block command line pushes that expose my email"
  (Settings → Emails) is the last barrier.

A corporate identity is never touched: only the emails on your `blocked=` list count.

## What runs on your machine

`hooks/git-identity.sh` runs at `SessionStart` and before each Bash/PowerShell command. It reads the tool-call JSON from stdin,
runs read-only `git` commands (`config`, `rev-parse`, `log`) and makes no network calls. See [`SECURITY.md`](../../SECURITY.md).

## Requirements

bash and git. Tested on Windows (Git for Windows) and Linux (see the CI matrix in the repo); macOS not tested.

## Install

```
/plugin marketplace add andresdeh/claude-workbench
/plugin install git-identity@claude-workbench
```

Without configuration the plugin only prints one line at session start suggesting `/git-identity:configure`.

## Config

| Option | Default | Where |
|---|---|---|
| `mode` (`block` / `warn`) | `block` | user (`/config`) |
| `blocked=`, `preferred=` | none | `~/.config/claude-workbench/git-identity` (private to the machine; never in a project) |

## Tests

`python -I tools/tests/git-identity.py plugins/git-identity/hooks/git-identity.sh` (16 cases; expect `FAILURES: 0`).

## Uninstall

`claude plugin uninstall git-identity@claude-workbench`; delete `~/.config/claude-workbench/git-identity` if you want.
