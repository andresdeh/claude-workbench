---
name: configure
description: Configures the git-identity guard on this machine (which emails must not appear in the user's commits, and which one to use instead), fixes the current repo's identity and any unpushed commits, and shows the plugin options. Use when the git-identity hook warns or blocks, when the user asks which email signs their commits, or when they want to block or allow an email.
---

# Configure git-identity

Language: talk to the user in their language. Never translate keys, file names or values.

The plugin protects a list of emails the user does not want in their commits. It does not assume which email that is nor which
host they use: everything comes from the user's own configuration. A **corporate** identity is not "blocked" unless the user
puts it on the list; do not touch it.

## Options

| Option | Default | Where |
|---|---|---|
| `mode` = `block` / `warn` | `block` | user: `/config` (row "Reaction to a blocked email") |
| `blocked=` (one line per email) | none: the hook only suggests this skill | file `~/.config/claude-workbench/git-identity` |
| `preferred=` (optional) | none | same file; the email this skill proposes |

## 1. Machine configuration (if `~/.config/claude-workbench/git-identity` is missing or the user wants to change it)

The file lives **outside any repo** (it holds a private email; never version it or copy it into a project):

```
blocked=<email you do not want in commits>     # one line per email
preferred=<email to sign with>                 # optional
```

1. Ask with `AskUserQuestion` which email(s) to block and, optionally, which to prefer. If a remote is on GitHub, **suggest**
   (do not impose) the user's GitHub noreply address `<id>+<user>@users.noreply.github.com`: the numeric `id` comes from
   `curl -s https://api.github.com/users/<user>` (field `id`). Remind that on GitHub the options "Keep my email addresses private"
   and "Block command line pushes that expose my email" (Settings → Emails) are the last barrier for commits made outside Claude Code.
2. Show the file's content and write it only after a yes.

## 2. Fix the current repo

1. **Diagnose (read-only):** `git config --show-origin user.email` (local, global or `includeIf`?), remotes (`git remote -v`),
   and unpushed commits with a blocked email: `git log @{u}..HEAD --format='%h %ae %ce'` (no upstream:
   `git log HEAD --not --remotes`). If the identity is not on the blocked list, there is nothing to fix.
2. **Identity:** propose `git config user.email <preferred>` (and `user.name` if missing) **in the repo**, not globally. If the
   blocked email comes from the global config, offer to change that too, as a separate question.
3. **Unpushed commits with a blocked email:** offer to rewrite them (author and committer only, keeping dates), with a prior
   backup (`git bundle create <outside-the-repo>/<repo>-<date>.bundle --all`) and checking afterwards that the tree is identical
   (`git rev-parse <old>^{tree}` = `HEAD^{tree}`).
4. **Already pushed commits:** rewriting them needs a forced push and moving published tags. **Only with an explicit yes**,
   explaining that, and with `--force-with-lease=<branch>:<known remote sha>`. If the repo is private, leaving it as is is valid too.
5. **Verify by re-reading** (`git config user.email`, `git log --format='%ae %ce'`) and report what changed.

## Never

- Bypass the block with `git -c user.email=…`, `GIT_AUTHOR_EMAIL`/`GIT_COMMITTER_EMAIL` or `--author`.
- Write a private email into a versioned file.
- Change the global identity or rewrite published history without asking.
