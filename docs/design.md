# Design

What was verified about Claude Code's plugin system (against its documentation, October 2026) and the rules this repository
derives from it. For the reasoning behind the plugins themselves, see [`philosophy.md`](philosophy.md).

## 1. What the documentation says

| Topic | Fact | Consequence |
|---|---|---|
| Marketplace | `.claude-plugin/marketplace.json` at the root: `name`, `owner.name` and `plugins[]` are required. Each entry: `name` + `source`; a relative source starts with `./` (or resolves under `metadata.pluginRoot`) | one repo is the marketplace **and** the plugins, in `plugins/<name>/` |
| Manifest | `.claude-plugin/plugin.json`; only `name` is required. Conventional folders: `skills/<n>/SKILL.md`, `agents/`, `commands/`, `hooks/hooks.json`, `.mcp.json` | the convention is used, with no hand-written paths |
| What a plugin carries | skills, subagents, commands, hooks, MCP, LSP, output styles, `bin/`… **A plugin's own `CLAUDE.md` is NOT loaded** | the block in a project's `CLAUDE.md` is written by a **skill**, never by the plugin alone (§4) |
| Version | `plugin.json` wins; declaring it in both places makes `validate` warn. **With a pinned `version`, users do not get new commits until it changes**; without `version`, every commit is a new version | `version` lives **only** in `plugin.json`; publishing means bumping it (§3) |
| Private repo | Claude Code uses the machine's `git`, without asking: SSH (with an agent) or HTTPS with a stored credential helper. A bare `GITHUB_TOKEN` is not enough | not an issue for this public repo; relevant to forks |
| Updating | `claude plugin marketplace update <name>`; auto-update is **off** by default for third-party marketplaces (`"autoUpdate": true` turns it on) | it stays off (§5) |
| Project declaration | `.claude/settings.json`: `extraKnownMarketplaces.<n>.source` + `enabledPlugins["plugin@marketplace"]: true`. Only applies after the user accepts folder trust | this is how a project is "connected" (§5) |
| Hooks | `hooks/hooks.json` with the `"hooks"` wrapper. `${CLAUDE_PLUGIN_ROOT}` (changes with each version), `${CLAUDE_PLUGIN_DATA}` (persists), `${CLAUDE_PROJECT_DIR}`. *Shell* form: `sh -c` on Linux, **Git Bash on Windows** if present (else PowerShell); the `"shell"` field pins it | §6 |
| Plugin options | `userConfig` in `plugin.json` is asked when the plugin is enabled, shown in `/config` and stored in `pluginConfigs` of `~/.claude/settings.json`. It reaches hooks as `CLAUDE_PLUGIN_OPTION_<KEY>` and MCP/skills as `${user_config.key}`. `pluginConfigs` is read **only at user or managed level**, never from the project | project-level options live in a file of their own (§7) |
| CLI | `claude plugin validate <path> [--strict]`, `install <p>@<m> --scope user\|project\|local`, `list --json`, `update`, `disable` | `validate --strict` before every commit |

## 2. Structure

```
.claude-plugin/marketplace.json   the catalog (name, description, tags, category and source of each plugin)
plugins/<name>/                   one plugin per folder
├── .claude-plugin/plugin.json    name, version, description, author, keywords, userConfig
├── README.md                     the fact sheet (§3) + how to use it
├── CHANGELOG.md
└── skills/  hooks/  agents/  .mcp.json   whatever it carries
docs/                             philosophy and this design
tools/barrier/                    pre-commit, commit-msg and pre-push against private data (§8)
tools/tests/                      tests for the hooks and the MCP
.github/                          CI and issue templates
```

Templates a skill copies live **inside** its `SKILL.md`, not in separate files (§4 rule 6).

## 3. Fact sheet and versions

`plugin.json` carries what Claude Code understands; the **fact sheet** (the table that opens each plugin's `README.md`)
carries what a person needs to decide whether to install it:

| Field | Example |
|---|---|
| Solves | one line |
| Components | hook `UserPromptSubmit` · skill `install` |
| Runs code | yes: bash on every message / no |
| Reads and writes | reads `.claude/claude-workbench.conf`; writes nothing |
| Requirements | bash (Git for Windows) |
| Recommended scope | `user` (all projects) or `project` |
| Context cost | ~200 tokens per message |
| How to turn it off | `claude plugin disable …` or an option |

It cannot live in `marketplace.json`: `validate --strict` rejects custom fields. So the README **opens with the
`| Fact sheet | |` table**, and `catalog` extracts it without reading the rest.

**Versions.** SemVer in `plugin.json` only. MAJOR: how it installs or is configured, or what it writes, changes. MINOR: new
behavior or text. PATCH: a fix. Every change that must reach projects bumps the version (otherwise nobody receives it) and is
noted in the plugin's `CHANGELOG.md`. The commit that publishes a version carries the tag `<plugin>-v<version>`.

## 4. A skill must not overwrite an existing `CLAUDE.md`

Because a plugin cannot ship a `CLAUDE.md`, a skill writes the block. Rules:

1. **Everything it writes goes between markers**: `<!-- claude-workbench:<plugin> v<version> start -->` …
   `<!-- claude-workbench:<plugin> end -->`. Outside the markers it never touches anything; an update replaces only the inside.
2. **Diagnose first, ask second, write last.** Is there a `CLAUDE.md`? Are there markers already (→ an update; show the
   `CHANGELOG` between versions)? Is an equivalent rule already written by hand (→ ask: replace, merge or leave)?
3. **Show the diff** and wait for a yes before writing.
4. Documentation files are **created only if missing**. Never overwritten.
5. If `CLAUDE.md` does not exist, create it minimal: the marked block and a title. No `/init` on top without asking.
6. **Templates go inside `SKILL.md`.** A skill that has to *read* `${CLAUDE_PLUGIN_ROOT}/templates/…` runs into the plugin
   folder being outside the allowed directories (denied in non-interactive mode; a permission prompt on every install in
   interactive mode). The `SKILL.md` content enters the context when the skill is invoked, with no permissions involved.

## 5. Connecting a project, and "propose, don't install"

Once per machine: `claude plugin marketplace add andresdeh/claude-workbench --scope user`.

Per project, in the versioned `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": { "claude-workbench": { "source": { "source": "github", "repo": "andresdeh/claude-workbench" } } },
  "enabledPlugins": { "model-protocol@claude-workbench": true }
}
```

`autoUpdate` stays **off**: a plugin with a hook runs new code on every message, so a new version is accepted by hand
(`claude plugin update`). `catalog` is a plugin with **skills and no hook** (a session-start hook would spend context in every
session; a skill's description is already loaded and costs less). It updates the marketplace, locates the local copy with
`claude plugin marketplace list --json`, compares with `claude plugin list --json`, and **proposes** (install, update,
re-enable, or run a missing install skill). Only on a yes does it run `claude plugin install`. It never installs from
third-party marketplaces.

## 6. Hooks that work on Windows and Linux

- *Shell* form with `"shell": "bash"` and the path by variable, in quotes:
  `"command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/model-protocol.sh\""`. Never `~` or absolute paths.
- **Not** the *exec* form with `"command": "bash"` on Windows: `PATH` may resolve `bash` to `System32\bash.exe`, which is
  **WSL**, and the hook would run inside the distro. On Windows the requirement is Git for Windows.
- Inside scripts: `$CLAUDE_PROJECT_DIR` and `$HOME`, never a literal `~` in config files.
- Data that must survive an update: `${CLAUDE_PLUGIN_DATA}`, not the plugin folder.
- `continuum`'s MCP does not go through a shell, and on Windows a bare `bash` may be WSL's and `python3` the Microsoft Store
  shortcut. It starts as `git -c alias.continuum=!sh continuum launcher.sh mcp/server.py`: git exists on both platforms and runs
  `!` aliases with its own `sh`; `launcher.sh` really tries `python3`, `python` and `py -3` (or the `python` option).
- `.gitattributes` forces `eol=lf`: a CRLF in a hook script breaks it on Linux.

## 7. Options at three levels

Default (`plugin.json`) → user (`userConfig`, `/config`) → project (`.claude/claude-workbench.conf`, one file, `plugin.key=value`
per line, readable by a bash hook with `grep`). Private lists never go to a project file; they live in
`~/.config/claude-workbench/`. Each plugin has a `configure` skill that shows every option with its effective value and level,
and writes the project level after showing a diff. The user level is left to `/config` for now.

## 8. Barrier against private data

Anything that reaches this repository is public. `tools/barrier/`:

- `pre-commit` checks what is staged, the author and the committer; `commit-msg` checks the message; `pre-push` checks **every**
  outgoing commit (author, message, diff) and the final tree.
- The list of forbidden expressions lives in `.git/info/forbidden-terms.txt`, **outside version control** (the list is itself
  private data). Without a list the barrier rejects everything.
- Enabled per clone with `tools/barrier/instalar.sh` (`core.hooksPath=tools/barrier`). CI runs gitleaks on top.

## 9. Lessons from testing

| Lesson | What to do |
|---|---|
| The CLI registers a marketplace as `"source": "git"` (with `url`) | use `claude plugin marketplace add` and copy what it writes |
| A skill cannot read the plugin folder without permission | templates inside `SKILL.md` (§4 rule 6) |
| A user-level hook and the plugin's both run | when moving a hook into a plugin, remove the manual one in the same step |
| Test without touching the real config | `CLAUDE_CONFIG_DIR=<throwaway folder>` + `claude -p --plugin-dir …` |
| `claude -p --allowedTools X "prompt"` swallows the prompt | write `"--allowedTools=X"` |
| Git on Windows leaves read-only objects: `rmtree` fails silently | a fresh test folder per run |
| A Git Bash heredoc eats backslashes | write scripts with an editor tool, never by heredoc |
| Rewriting published history | backup bundle, `filter-branch` only the e-mail, identical tree, `--force-with-lease=<branch>:<sha>` |
