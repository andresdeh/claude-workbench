---
name: configure
description: Shows and changes the options of the model-protocol plugin (whether the Opus/Sonnet/Haiku reminder is on, and the custom text). Use when the user asks to turn the model reminder on or off, for one project or for all, or to customize its text.
---

# Configure model-protocol

Language: talk to the user in their language. Never translate keys, file names or values.

## Options

| Option | Default | Where it can be set |
|---|---|---|
| `enabled` | `true` | user: `/config` (row "Enable the model reminder"); project: `.claude/claude-workbench.conf` |
| custom text | generic text | file `model-protocol.md` in `~/.claude/` (user) or in the project's `.claude/` (project wins) |

Priority, lowest to highest: plugin default → user → project.

## Steps

1. **Read, without asking.** Find the effective value of `enabled` and say which level it comes from:
   - project: the last line `model-protocol.enabled=...` in `$CLAUDE_PROJECT_DIR/.claude/claude-workbench.conf`;
   - user: look for `model-protocol` in `~/.claude/settings.json` under `pluginConfigs`; if it is not there, the default applies;
   - custom text: check whether `.claude/model-protocol.md` or `~/.claude/model-protocol.md` exists.
2. **Ask** with `AskUserQuestion` what to change and at which level (project or user).
3. **Project level:** show the diff of `.claude/claude-workbench.conf` (create it if missing; the format is one
   `plugin.key=value` line, other plugins' lines stay untouched) and write it after a yes. Remind that the file is versioned,
   so a team sees it: personal preferences belong at user level.
4. **User level:** do not edit `settings.json` by hand. Tell the user to open `/config` and change the row, or to edit the
   file `~/.claude/model-protocol.md` for the text.
5. **Verify** by reading the file back and report the effective value. The hook picks up the change on the next message.
