# catalog (v1.0.1)

| Fact sheet | |
|---|---|
| Solves | Knowing which claude-workbench tools are missing or outdated on this machine and in this project, without installing anything on its own |
| Components | skills `propose` and `configure` (no hooks, no MCP) |
| Runs code | **Not by itself.** With the skills, Claude runs `claude plugin …` and `git` commands; those that install or write, only with your yes |
| Reads and writes | Reads the local copy of the marketplace (`marketplace.json`, each `README.md` fact sheet, `CHANGELOG.md`), `claude plugin list` and `.claude/claude-workbench.conf`. With your yes: installs or updates plugins and merges the project's `.claude/settings.json` |
| Requirements | bash and git (on Windows, Git for Windows); the marketplace added on the machine |
| Recommended scope | `user` (all projects) |
| Context cost | only the skills' descriptions, always loaded |
| How to turn it off | `claude plugin disable catalog@claude-workbench` |

## Why

A collection of plugins only helps if it reaches the projects. This plugin compares the marketplace with what is installed,
**proposes** what fits the project (and new versions, because `autoUpdate` is off) and installs only on your yes.

## What it does

- `propose`: diagnoses (read-only), classifies each plugin (recommend / mention / update / re-enable / run its install skill),
  installs what you pick, and can declare the marketplace and plugins in the project's `.claude/settings.json`.
- `configure`: one table with the options of every installed claude-workbench plugin, and a hand-off to each plugin's own
  `configure` skill.

## What runs on your machine

Nothing runs on its own: it has no hooks. See [`SECURITY.md`](../../SECURITY.md).

## Requirements

bash and git; the marketplace added with `claude plugin marketplace add andresdeh/claude-workbench --scope user`.

## Install

```
/plugin marketplace add andresdeh/claude-workbench
/plugin install catalog@claude-workbench
```

Then ask in any project: "which claude-workbench tools fit here?", "connect this project to claude-workbench" or "are there new versions?".

## Rules it follows

- Plugins with `category: general-rule` (today `git-identity`) are offered as recommended.
- It never installs from third-party marketplaces and never turns `autoUpdate` on.
- For a plugin to show up well in the catalog, its `README.md` must open with the `| Fact sheet | |` table.

## Config

This plugin has no options of its own. `/catalog:configure` lists the options of the other claude-workbench plugins.

## Uninstall

`claude plugin uninstall catalog@claude-workbench`.
