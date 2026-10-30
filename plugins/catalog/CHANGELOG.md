# Changelog — catalog

## 1.0.3 (2026-10-30)
- `propose` says plainly when `continuum` is installed but the project has no vault: inert, expected, not an error; it proposes `init-project` and leaves it to the user (it is in development).

## 1.0.2 (2026-10-30)
- `propose` never recommends a plugin whose README title says `IN DEVELOPMENT` (today `continuum`): it mentions it in one line
  and installs it only if the user picks it. The fact-sheet command now also prints each README's title line.

## 1.0.1 — first release as `catalog` (2026-10-29)
- Renamed from `catalogo` (private predecessor). Version kept at 1.0.1; all text in English, replies in the user's language.
- Targets the `claude-workbench` marketplace (`andresdeh/claude-workbench`); markers are `claude-workbench:<plugin>`; the
  fact sheet table is `| Fact sheet | |`; categories are `workflow` and `general-rule`.
- Dropped the project-inventory step and the fixed clone path: the inventory was a bookkeeping practice of the private
  predecessor, and nothing needs a working copy of the repo any more.
- New skill `configure`: one table with every installed plugin's options and a hand-off to each plugin's own skill.

History before the rename: 1.0.1 — the install-skill example no longer names a retired plugin. 1.0.0 (2026-10-18) — skill
`proponer`: compares the marketplace with `claude plugin list --json`, proposes install / update / re-enable, connects the project.
