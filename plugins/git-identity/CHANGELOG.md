# Changelog — git-identity

## 1.0.0 — first release as `git-identity` (2026-10-29)
- Renamed from `identidad-git` (private predecessor, 1.0.0 there). Version kept.
- Now **optional and neutral**: protects a list of emails the user names (`blocked=`, one or more) with an optional `preferred=`.
  It no longer assumes a "personal" email or GitHub; the GitHub noreply address is only a suggestion of the `configure` skill.
- Config moved to `~/.config/claude-workbench/git-identity`. Without it, the hook prints one line at session start that
  suggests the skill, and does nothing else.
- New user option `mode` (`block` / `warn`); `warn` lets the command run and tells Claude through `additionalContext`.
- Messages cite "your configuration" instead of a rule of the author; all text in English with "reply in the user's language".
- Skill `configurar` → `configure`. Test made portable (Git for Windows or Linux bash, `tempfile`, `os.devnull`); 16 cases.

History before the rename: 1.0.0 (2026-10-18) — `SessionStart` warning, `PreToolUse` block of `git commit`/`git push`
(also with `git -C <path>` and unpushed commits) and the `configurar` skill.
