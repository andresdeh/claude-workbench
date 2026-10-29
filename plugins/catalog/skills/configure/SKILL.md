---
name: configure
description: One table with the options of every installed claude-workbench plugin (value, level it comes from), and a hand-off to each plugin's own configure skill to change them. Use when the user asks what can be configured in claude-workbench, wants to see all the settings at once, or wants to change one without knowing which plugin owns it.
---

# Configure claude-workbench (all plugins)

Language: talk to the user in their language. Never translate keys, plugin names or values.

Three levels, the lowest wins only when the higher ones say nothing: **plugin default** → **user** (`userConfig`, visible in `/config`)
→ **project** (`.claude/claude-workbench.conf`, one versioned file, one `plugin.key=value` line per option).
Private lists (for example the emails of `git-identity`) never go in a project file: they live in
`~/.config/claude-workbench/`.

## Steps

1. **Find what is installed (read-only):** `claude plugin list --json` and keep the plugins of the `claude-workbench`
   marketplace. For each one, read its `README.md` "Config" table in the install location
   (`claude plugin marketplace list --json` → `installLocation`).
2. **Read the effective values:** the project file `$CLAUDE_PROJECT_DIR/.claude/claude-workbench.conf` (last line per key wins),
   the plugin's entry under `pluginConfigs` in `~/.claude/settings.json` if there is one, and the plugin default. Build one table:
   `plugin · option · effective value · level it comes from`.
3. **Ask** (`AskUserQuestion`) which option to change. Do not write anything yourself: hand off to the plugin's own skill
   (`/model-protocol:configure`, `/git-identity:configure`, `/continuum:configure`), which shows the diff and asks for a yes.
4. For a user-level option that has a `/config` row, tell the user they can also change it there.
