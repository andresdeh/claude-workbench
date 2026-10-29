# Changelog — continuum

## 0.5.1 — first release as `continuum` (2026-10-29)
- Renamed from `continuo` (private predecessor, 0.5.1 there). Version kept; still in development.
- **English names, fixed**: folders `tasks/ decisions/ log/ agents/`, `index.md`, states `open / in progress / done`, frontmatter
  keys (`status created updated last model` / `date author task`), MCP `memory` with tools `search read note decide`, subagents
  `reader` and `tester`, markers `claude-workbench:continuum`. The code has no aliases for the old Spanish names.
- **Language**: what the code writes without AI follows `.continuum.json` of the vault (`en`, `es`; other → English). Everything
  Claude reads is English with "reply in the user's language".
- **Vault**: sibling folder `<project>-memory`; `continuum.vault=` in `.claude/claude-workbench.conf` replaces it
  (`CONTINUUM_VAULT` stays for tests). `MEMORIA_BOVEDA` is gone.
- **Options**: `autocommit` (commit after each turn, default on; user option or `continuum.autocommit=` in the project) and
  `python` (replaces `CONTINUO_PYTHON`). New skill `configure`.
- **Vault identity** no longer depends on `git-identity`: its own `user.email` → `preferred=` if the file exists → the e-mail git
  would use (shown and confirmed) → ask; also sets `user.name` and `useConfigOnly`. The hook does not commit if the vault's e-mail is
  on the `blocked=` list of `~/.config/claude-workbench/git-identity` (it only reads that file). (Pilot 2, finding 1.)
- **Author**: the git config rules; if the project's `CLAUDE.md` declares another author, the skill points it out and asks, and does
  not edit that line. (Pilot 2, finding 2.)
- `migrate.py` + `init-project` migrate a `memoria-<project>` vault of the old plugin (plan and diff first).

History before the rename (summary): 0.5.1 — vault identity fixed on creation, log without repeated files, `📌 … → /clear`
line. 0.5.0 — packaged (hooks, catalog entry). 0.4.0 — the hook commits the vault. 0.3.0 — `iniciar-proyecto` skill and the
subagents. 0.2.0 — task `modelo` field, `anotar` returns what was saved, vault deduced by convention, launcher. 0.1.0 — MCP and
log hook, tested standalone.
