# Changelog — catalog

## 1.0.1 — first release as `catalog` (2026-10-29)
- Renamed from `catalogo` (private predecessor). Version kept at 1.0.1; all text in English, replies in the user's language.
- Targets the `claude-workbench` marketplace (`andresdeh/claude-workbench`); markers are `claude-workbench:<plugin>`; the
  fact sheet table is `| Fact sheet | |`; categories are `workflow` and `general-rule`.
- Dropped the project-inventory step and the fixed clone path: the inventory was a bookkeeping practice of the private
  predecessor, and nothing needs a working copy of the repo any more.
- New skill `configure`: one table with every installed plugin's options and a hand-off to each plugin's own skill.

History before the rename: 1.0.1 — the install-skill example no longer names a retired plugin. 1.0.0 (2026-10-18) — skill
`proponer`: compares the marketplace with `claude plugin list --json`, proposes install / update / re-enable, connects the project.
