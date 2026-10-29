# claude-workbench

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/andresdeh/claude-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/andresdeh/claude-workbench/actions/workflows/ci.yml)

A small, personal collection of [Claude Code](https://code.claude.com) plugins for working the same way in every project,
on every machine: a reminder to split work between models, an optional guard for the e-mails you keep out of your commits,
memory that survives `/clear`, and a catalog that proposes them without installing anything on its own.

Each plugin is independent. Install one, some or all.

## Install

**Step 1: add the marketplace** (once per machine). Inside Claude Code:

```
/plugin marketplace add andresdeh/claude-workbench
```

**Step 2: install what you want.** Each plugin is independent and Claude Code has no "install everything" command, so you pick
by name. Run the lines one at a time inside Claude Code.

Everything:

```
/plugin install catalog@claude-workbench
/plugin install model-protocol@claude-workbench
/plugin install git-identity@claude-workbench
/plugin install continuum@claude-workbench
```

Only some: keep just the lines you want from that block. Not sure which? Install only `catalog`, then ask in any project:
*"which claude-workbench tools fit here?"*. It compares the marketplace with what you have, explains each plugin and installs
only what you say yes to.

Prefer the terminal? The same thing, all at once and without opening Claude Code:

```bash
claude plugin marketplace add andresdeh/claude-workbench
claude plugin install catalog@claude-workbench
claude plugin install model-protocol@claude-workbench
claude plugin install git-identity@claude-workbench
claude plugin install continuum@claude-workbench
```

Some plugins need one extra step inside a project (`model-protocol` and `continuum` have an `install` / `init-project` skill);
each plugin's README says which.

## Use it with Obsidian

[`continuum`](plugins/continuum/) keeps a project's memory (tasks, decisions, daily log) as plain Markdown notes in a folder
next to it, `../<project>-memory`. That folder is a normal Obsidian vault: open it with *Obsidian → Open folder as vault* and
you see the project's state as notes, links and graph, including what Claude wrote. Your edits there are committed with the
rest. Obsidian is optional and only a viewer; without it the notes are still readable files.

## Plugins

| Plugin | What it does | Runs on your machine | Status |
|---|---|---|---|
| [`catalog`](plugins/catalog/) | Proposes the plugins that fit the project and their new versions; one table with every plugin's options | nothing on its own (skills only) | 1.0.1 |
| [`model-protocol`](plugins/model-protocol/) | Reminds Claude on every message which work belongs to Opus, Sonnet or Haiku, and when to ask you to switch | a read-only bash script per message (~200 tokens) | 2.2.0 |
| [`git-identity`](plugins/git-identity/) | Blocks (or warns about) `git commit`/`git push` signed with an e-mail you listed; fixes the repo with your yes | a bash script at session start and before `git` commands | 1.0.0 |
| [`continuum`](plugins/continuum/) | Work by tasks instead of sessions: memory in an Obsidian vault next to the project, read and written through its own MCP; a hook logs each turn without AI | a Python MCP server and a Python hook, both confined to the vault | 0.5.1, in development |

Every plugin README opens with a fact sheet: what it solves, what it runs, what it reads and writes, what it costs in context
and how to turn it off. [`SECURITY.md`](SECURITY.md) lists everything that executes on your machine.

## Configuration

Options have three levels; the most specific one that says something wins:

1. **Default**, declared in each `plugin.json`.
2. **User**, asked when you enable the plugin and changed later in `/config`.
3. **Project**, in one versioned file, `.claude/claude-workbench.conf`, one `plugin.option=value` per line.

`/<plugin>:configure` shows each option with its effective value and where it comes from; `/catalog:configure` shows all of
them in one table. Private data (such as the e-mails `git-identity` blocks) never goes into a project: it lives in
`~/.config/claude-workbench/`.

## Philosophy, in five lines

- **Propose, don't install.** A hook runs code on every message; nothing gets installed or updated without your yes.
- **Mechanical work without AI.** Hooks are plain scripts; no plugin spends tokens on bookkeeping.
- **Rules live in code, not in prose.** What must always hold is enforced by a hook or a server, not hoped for in `CLAUDE.md`.
- **Never overwrite what is yours.** Changes to your files go between markers, after a diff you approve.
- **Your language.** Plugins talk and write in your language; identifiers stay in English so nothing breaks when it changes.

The long version, and why each plugin exists: [`docs/philosophy.md`](docs/philosophy.md).

## Where it was tested

| Platform | Status |
|---|---|
| Windows 10/11 with Git for Windows | tested |
| Linux | pending (CI matrix) |
| macOS | not tested |

Requirements: Claude Code, git and bash (on Windows, Git for Windows); Python 3.8+ for `continuum`.

## Contributing

Issues are welcome. For pull requests, open an issue first: see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[Apache 2.0](LICENSE). See [`NOTICE`](NOTICE).
