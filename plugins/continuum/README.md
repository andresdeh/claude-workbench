# continuum (v0.5.1 — IN DEVELOPMENT)

| Fact sheet | |
|---|---|
| Solves | Stop spending context and tokens on session wrap-ups and on re-reading long documentation at the start |
| Components | MCP `memory` (4 tools) · `Stop`/`SubagentStop` log hook · skills `init-project` and `configure` · subagents `reader` (Haiku) and `tester` (Sonnet) |
| Runs code | **Yes**: a Python server over stdio (the MCP) and a Python script at the end of each turn (the hook). Neither calls an AI |
| Reads and writes | Reads and writes **only inside the vault** (`../<project>-memory`, or the folder set in `continuum.vault`); only `.md`; append-only, it never deletes or rewrites text. The hook writes the day's log and, unless `autocommit` is off, makes a commit in the vault's repo (never a push, and not with an e-mail on your `blocked=` list) |
| Requirements | Python 3.8+ and git (the launcher tries `python3`, `python` and `py -3`; the `python` option pins one). No external dependencies |
| Recommended scope | `user` (the MCP and the hook only act if the project's vault exists; they never create it) |
| Context cost | ~450 tokens per agent for the 4 tools' definitions; the routers that get read are ~20 lines |
| How to turn it off | `claude plugin disable continuum@claude-workbench`; in a project with no vault the hook does nothing. Only the commit: `continuum.autocommit=false` |

## Why

Instead of "sessions" that are closed by hand writing status `.md` files, the unit of work is the **task**, and state lives
outside the chat: an Obsidian vault that Claude reads and writes through its own MCP. `/clear` loses its ceremony: you note,
clear, and resume with "continue with [[task]]".

## What it does

| File | What it is |
|---|---|
| `mcp/server.py` | MCP `memory`: `search`, `read`, `note`, `decide`. JSON-RPC over stdio, standard library only |
| `hooks/log_turn.py` | One line per turn with work in `log/YYYY-MM-DD.md`, read from the transcript, and a commit of the vault with everything pending. It never blocks nor fails towards Claude Code |
| `vault.py` | What both share: where the vault is, how a task is named, the language tables |
| `launcher.sh` | Finds a Python that really works and passes it the arguments (POSIX sh) |
| `migrate.py` | Migrates a vault written with the Spanish names of the old `continuo` plugin |
| `skills/init-project/` | Creates the sibling vault with its git, the `CLAUDE.md` block, the `.gitignore`, the permissions and the first task (templates inside) |
| `skills/configure/` | Shows and changes the options below |
| `agents/reader.md` | Haiku, read-only: reads a lot and returns 5-10 lines (conclusion · data · files · pending) |
| `agents/tester.md` | Sonnet: runs tests, returns only the failures and can note them in the task; it does not fix or install |

**Vault by convention.** The project `<parent>/x/` (root of its git repo, even if Claude opens in a subfolder) uses
`<parent>/x-memory/`. If Claude opens inside the vault, that is the vault. `continuum.vault` replaces it.

**Tasks.** The frontmatter carries `status` (`open` / `in progress` / `done`) and `model` (`opus` / `sonnet` / `haiku`: the one that
fits the next step, shown in `tasks/_router` as `→ model`). `note` returns what ended up on disk, re-read.

Rules enforced by the code, not the model: nothing outside the vault nor hidden folders; only `.md`; append-only; the routers
`tasks/_router` and `decisions/_router` regenerate themselves; `read` of a task returns the last 5 entries.

**Language.** Identifiers (folders, states, frontmatter keys, tool names, markers) are always English. The text the code writes
without AI (routers, log, commit messages) follows the vault's `.continuum.json` (`en`, `es`; any other falls back to English;
more languages by pull request). What Claude writes follows the user's language.

## What runs on your machine

The MCP is a Python script started as `git -c alias.continuum=!sh continuum launcher.sh mcp/server.py` (git exists on Windows
and Linux and brings its own `sh`; a bare `bash` on Windows may be WSL's, and `python3` the Microsoft Store shortcut). The hook is
`sh launcher.sh hooks/log_turn.py` on `Stop` and `SubagentStop`. Both stay inside the vault and the project, make no network
calls, and run no AI. See [`SECURITY.md`](../../SECURITY.md).

## Requirements

Python 3.8+ and git. Tested on Windows; Linux not yet verified.

## Install

```
/plugin marketplace add andresdeh/claude-workbench
/plugin install continuum@claude-workbench
```

Then, in a project: "start this project with continuum" → runs `init-project`.

## Config

| Option | Default | Level |
|---|---|---|
| `autocommit` | `true` | user (`/config`), project (`continuum.autocommit=`) |
| `vault` (folder) | `../<project>-memory` | project (`continuum.vault=`) |
| `python` | automatic | user (`/config`) |
| language | `en` | `.continuum.json` inside the vault |

`/continuum:configure` walks through it. The vault's git identity: its own `user.email`, else `preferred=` of
`~/.config/claude-workbench/git-identity` if present, else the e-mail git would use (shown and confirmed), else it asks.
`git-identity` is optional and not required.

## Migrating a vault from `continuo`

`/continuum:init-project` detects `../memoria-<project>` and offers the migration with a plan and diff (`migrate.py`): renames
the folders and notes, rewrites keys, states and links, writes `.continuum.json` (`es`) and renames the folder to
`<project>-memory`.

## Uninstall

`claude plugin uninstall continuum@claude-workbench`. The vault is yours and stays untouched; delete the block between the
`claude-workbench:continuum` markers in `CLAUDE.md` and in `.gitignore` if you want.
