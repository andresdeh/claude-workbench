# model-protocol (v2.2.0)

| Fact sheet | |
|---|---|
| Solves | Spending Opus on mechanical work, and forcing Sonnet onto work that needs depth |
| Components | `UserPromptSubmit` hook · skills `install` and `configure` |
| Runs code | **Yes**: a bash script on every user message (read-only; it does not read the prompt and writes nothing) |
| Reads and writes | Reads `.claude/claude-workbench.conf`, `.claude/model-protocol.md` and `~/.claude/model-protocol.md` if they exist. The hook writes nothing. The `install` skill writes to `CLAUDE.md`, between markers and with your yes |
| Requirements | bash (on Windows, Git for Windows) |
| Recommended scope | `user` (all projects) |
| Context cost | ~200 tokens per message |
| How to turn it off | One project: `model-protocol.enabled=false` in `.claude/claude-workbench.conf`. Everywhere: `/config`, or `claude plugin disable model-protocol@claude-workbench` |

## Why

Claude Code runs on Opus (for thinking), Sonnet (for mechanical work that needs judgment) or Haiku (for simple mechanical
work). A rule in `CLAUDE.md` was not enough: it has to be recalled on every message. This plugin does that with a hook and,
separately, writes the full rule into `CLAUDE.md`.

## What it does

- On every message the hook adds a short reminder: which kind of work belongs to which model, and when to flag a switch
  (`🔵 Model: … → better …`) and stop to ask for `/model`.
- The `install` skill writes the full rule into the project's `CLAUDE.md` between markers
  (`<!-- claude-workbench:model-protocol … -->`), after showing a diff.
- The `configure` skill shows and changes the options below.

## What runs on your machine

One bash script, `hooks/model-protocol.sh`, runs on each `UserPromptSubmit`. It only reads the three optional files above and
prints text. It makes no network calls and does not read your prompt. See [`SECURITY.md`](../../SECURITY.md).

## Requirements

bash. On Windows, Git for Windows provides it. Tested on Windows; Linux not yet verified.

## Install

```
/plugin marketplace add andresdeh/claude-workbench
/plugin install model-protocol@claude-workbench
```

Then ask: "install the model protocol in this project" → runs the `install` skill. Restart Claude Code or open `/hooks`.

## Config

Three levels; the lowest wins only when the higher ones say nothing: plugin default → user (`/config`) → project
(`.claude/claude-workbench.conf`).

| Option | Default | Level |
|---|---|---|
| `enabled` | `true` | user, project (`model-protocol.enabled=false`) |
| custom text | generic | file `model-protocol.md` in `~/.claude/` or in the project's `.claude/` (project wins) |

`/model-protocol:configure` walks through it.

## Uninstall

`claude plugin uninstall model-protocol@claude-workbench`. If you ran `install`, delete the block between the
`claude-workbench:model-protocol` markers in `CLAUDE.md`.
