---
name: configure
description: Shows and changes the options of the continuum plugin (commit after each turn, vault location, Python to use, language of the vault). Use when the user asks to turn the vault's automatic commit on or off, to move or point the vault elsewhere, or to change the language the code writes the log and routers in.
---

# Configure continuum

Language: talk to the user in their language. Never translate keys, file names or values.

## Options

| Option | Default | Where it can be set |
|---|---|---|
| `autocommit` | `true` | user: `/config` ("Commit the vault after each turn"); project: `continuum.autocommit=` |
| `vault` (folder) | `../<project>-memory` | project: `continuum.vault=<folder>` in `.claude/claude-workbench.conf` (relative paths start at the project root) |
| `python` | automatic | user: `/config` ("Python to use") |
| language | `en` | `.continuum.json` inside the vault: `{"language": "es"}` (only `en` and `es` have tables; any other falls back to English) |

Priority for `autocommit`, lowest to highest: plugin default → user → project. `CONTINUUM_VAULT` (environment variable) exists only for tests.

## Steps

1. **Read, without asking:** the effective value of each option and which level it comes from (project file
   `$CLAUDE_PROJECT_DIR/.claude/claude-workbench.conf`, last line per key wins; `pluginConfigs` in `~/.claude/settings.json`;
   default), and the vault's `.continuum.json`. Find the vault with the same rule as the plugin (project conf, else the sibling folder).
2. **Ask** with `AskUserQuestion` what to change and at which level.
3. **Project level:** show the diff of `.claude/claude-workbench.conf` (create it if missing; other plugins' lines stay untouched) and
   write it after a yes. The file is versioned: personal preferences belong at user level. If `vault` changes, remind that the
   folder must exist (this skill does not move it) and that a vault outside the sibling convention should be listed here.
4. **User level:** do not edit `settings.json` by hand: tell the user to open `/config` and change the row.
5. **Language:** show the diff of `.continuum.json` and write it after a yes. It only changes what the code writes from now on
   (routers, log); existing notes are not translated.
6. **Verify** by reading back and report the effective values. Changes apply from the next turn.
