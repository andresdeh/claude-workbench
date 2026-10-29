# Changelog — model-protocol

## 2.2.0 — first release as `model-protocol` (2026-10-29)
- Renamed from `protocolo-modelo` (private predecessor). Everything the plugin says is now in English; Claude is told to reply
  in the user's language. Version kept at 2.2.0.
- New option `enabled` (user, via `userConfig`; project, via `model-protocol.enabled=` in `.claude/claude-workbench.conf`).
  It replaces the `.off` file.
- Custom text is now `model-protocol.md` (was `protocolo-modelo.txt`).
- New skill `configure`; `instalar` is now `install` and understands the old `claude-tools:protocolo-modelo` markers
  (migration with a diff).
- Markers are now `claude-workbench:model-protocol`.

History before the rename (summary):
- 2.2.0 — no "session close"; the 🔵 line only when the next step in the same thread needs another model.
- 2.1.0 — Haiku as a third level; rule "switching model = `/clear`".
- 2.0.1 — templates moved inside `SKILL.md` (the plugin folder is not readable without permission).
- 2.0.0 — packaged as a plugin (hook registered by `hooks.json`); `install` skill writes the section between markers.
- 1.0.0 — first version: a `UserPromptSubmit` hook injecting the reminder on every turn.
