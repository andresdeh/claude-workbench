---
name: propose
description: Catalog of claude-workbench - compares the plugins of the claude-workbench marketplace with the installed ones, proposes which to install or update (with their fact sheet, installing nothing without a yes), and connects the project. Use when starting or connecting a project, when the user asks which tools or plugins exist or whether there are new versions, or when a need appears that a claude-workbench tool could solve.
---

# claude-workbench catalog: propose, never install on its own

Language: talk to the user in their language. Never translate plugin names, keys, file names or markers.

Only the **claude-workbench** marketplace. Nothing is ever installed from a third-party marketplace this way, and nothing is
installed, updated or written without a yes from the user through `AskUserQuestion`. Commands are bash (on Windows, the Bash of
Git for Windows).

## 1. Diagnosis (read-only)

1. `claude plugin marketplace update claude-workbench` (fetches the published version; if the network fails, go on with the copy
   there is and say so). If the marketplace is not added, explain the one-time step per machine and stop:
   `claude plugin marketplace add andresdeh/claude-workbench --scope user`.
2. `claude plugin marketplace list --json` → `installLocation` and `url` of `claude-workbench`.
3. `claude plugin list --json` → what is installed (`id`, `version`, `scope`, `enabled`).
4. Read the catalog and the fact sheets with **one** command (`M` = the `installLocation`; on Windows it works as is in quotes):

   ```bash
   M='<installLocation>'; cat "$M/.claude-plugin/marketplace.json"
   for d in "$M"/plugins/*/; do echo "== $(basename "$d")"; grep -h '"version"' "$d/.claude-plugin/plugin.json"; head -1 "$d/README.md"
     awk '/^\| Fact sheet/{f=1} f&&/^$/{exit} f' "$d/README.md"; done
   ```

   The fact sheet is the table that starts with `| Fact sheet |` at the top of each plugin's `README.md`; the line before it is the
   title, which carries the status (for example `IN DEVELOPMENT`). Read nothing else of the plugin.
5. Look at the current project without writing: `CLAUDE.md` (does it already have blocks `<!-- claude-workbench:<plugin> … -->`?),
   `docs/`, `.claude/settings.json` (does it already declare `claude-workbench`?) and whether it is a git repo.

## 2. Compare and propose

Classify each plugin of the catalog (except `catalog`):

| Case | What to propose |
|---|---|
| Not installed and its README title says `IN DEVELOPMENT` | Never recommend it, whatever its `category`: mention it in one line as "in development" and install it only if the user picks it |
| Not installed and `category` = `general-rule` | Offer it as recommended: these are rules the user may want in every project |
| Not installed and it solves something this project shows (by its `description`, `tags` and what was seen in step 1.5) | Install, saying **why** in one line |
| Not installed and unrelated to the project | Mention it in one line, without recommending it |
| Installed with a lower version than the `plugin.json` one | Update (`autoUpdate` is off on purpose): summarize what is new from the `CHANGELOG.md` between both versions (`sed -n '1,40p' "$M/plugins/<p>/CHANGELOG.md"`); if it is a MAJOR version, warn that how it installs or what it writes changes |
| Installed but `enabled: false` | Ask whether to re-enable; do not insist |
| Installed and up to date, but its block is missing in `CLAUDE.md` (it has an install skill) | Propose running that skill |

Show a short table (plugin · what it solves · runs code · context cost · scope) and ask with `AskUserQuestion`
(`multiSelect: true`), recommended first and marked "(Recommended)". The description of each option carries what weighs most for
deciding: whether it **runs code** (hook) and what it writes. If there is nothing to propose, say so in one line and go to step 4.

## 3. Install or update (only what was chosen)

1. Install: `claude plugin install <p>@claude-workbench --scope <scope from the fact sheet>`. Update: `claude plugin update <p>@claude-workbench`.
2. Re-read with `claude plugin list --json` and confirm version and scope. If something failed, show the error as is.
3. Warn that new or updated plugins load on **restart of Claude Code**. If the plugin ships a skill that writes into the project
   (for example `model-protocol:install`, `continuum:init-project`, `git-identity:configure`), give the phrase to ask for it after the
   restart; that skill does its own diagnosis and asks for its own yes.

## 4. Connect the project (optional)

So that on another machine the project asks for the same marketplace and plugins, offer to declare them in the project's
`.claude/settings.json` (it is versioned with the project):

```json
{
  "extraKnownMarketplaces": { "claude-workbench": { "source": { "source": "git", "url": "<url from step 1.2>" } } },
  "enabledPlugins": { "<p>@claude-workbench": true }
}
```

- **Merge** with whatever the file already has (never replace it), show the diff and write only after a yes.
- The `url` comes from step 1.2 (the HTTPS one that already works on this machine); it is not invented.
- Do not declare plugins the user did not choose, nor the `general-rule` ones if they prefer them at user level only.
- If the project is not the user's own and they do not want the repo to mention claude-workbench, skip this step.

## 5. Wrap-up

Summarize in a few lines: what was installed or updated (with version), what is left for after the restart, and whether the
project was declared.

## Never

- Install, update, re-enable or write without an explicit yes.
- Install from another marketplace, or suggest `autoUpdate: true`.
- Put in `settings.json` data that belongs to a company (servers, domain, accounts, internal paths).
