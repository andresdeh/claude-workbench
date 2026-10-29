#!/usr/bin/env bash
# git-identity.sh — optional guard for the emails you do not want in your commits.
# Mode "start" (SessionStart): warns if the project's repo signs with a blocked email. Silent when all is fine.
# Mode "before" (PreToolUse of Bash/PowerShell): blocks `git commit` / `git push` if the repo's identity is a blocked
# email or if a commit about to be pushed carries one. Exit 2 = block; stderr text reaches Claude.
# With the user option mode=warn it only tells Claude (additionalContext) and lets the command run.
# Per-machine config, outside any repo: ~/.config/claude-workbench/git-identity
#   blocked=<email>      (one or more lines; emails you do not want in your commits)
#   preferred=<email>    (optional; the one the configure skill proposes, e.g. a GitHub noreply address)
# It never fails by itself: when in doubt it lets the command through.
CONF="$HOME/.config/claude-workbench/git-identity"
mode="${1:-}"
reaction="${CLAUDE_PLUGIN_OPTION_MODE:-block}"
input=$(cat 2>/dev/null)

if [ ! -r "$CONF" ]; then
  [ "$mode" = start ] && echo "[git-identity] Not configured on this machine ($CONF is missing): suggest the git-identity:configure skill. Reply to the user in their language."
  exit 0
fi
preferred=$(sed -n 's/^preferred=//p' "$CONF" | head -1 | tr -d '\r')
blocked=$(sed -n 's/^blocked=//p' "$CONF" | tr -d '\r' | tr 'A-Z' 'a-z')
[ -n "$blocked" ] || exit 0
# No -i: both sides are already lowercase, and `grep -ixF` aborts in Git for Windows' grep.
is_blocked() { printf '%s\n' "$blocked" | grep -qxF -- "$(printf '%s' "$1" | tr 'A-Z' 'a-z')"; }
unjson() { printf '%s' "$1" | sed 's/\\\\/\\/g'; }

if [ "$mode" = start ]; then
  dir="${CLAUDE_PROJECT_DIR:-$PWD}"
  git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 || exit 0
  email=$(git -C "$dir" config user.email)
  if [ -n "$email" ] && is_blocked "$email"; then
    echo "[git-identity] This repo signs with a blocked email, per the user's configuration. Sign with ${preferred:-another identity} instead."
    echo "Suggest the git-identity:configure skill before any commit (commits and pushes are ${reaction}ed). Reply to the user in their language."
  fi
  exit 0
fi

[ "$mode" = before ] || exit 0
# Is it a git commit / git push? (on the raw JSON: enough to detect, no need to parse it)
# Deliberately broad (a -C path may contain spaces): `git` and, later, `commit` or `push` as a standalone word.
# A false positive only blocks in a repo that already signs with a blocked email.
is_git() { printf '%s' "$input" | grep -qE "(^|[^[:alnum:]_-])git([[:space:]].*)?[[:space:]]($1)([[:space:]\"]|\\\\|\$)"; }
is_git 'commit|push' || exit 0
# Repo folder: the one in `git -C <path>` if any, else "cwd". In the raw JSON a quote in the command appears as \"
# and a backslash as \\ (inside [...] the backslash is literal: [^\"] = neither backslash nor quote).
dir=""
re_c='git[[:space:]]+-C[[:space:]]+\\"(([^\"]|\\\\)*)\\"'
re_s="git[[:space:]]+-C[[:space:]]+'([^']*)'"
re_b='git[[:space:]]+-C[[:space:]]+(([^[:space:]\"]|\\\\)+)'
re_cwd='"cwd"[[:space:]]*:[[:space:]]*"(([^\"]|\\\\)*)"'
if [[ $input =~ $re_c ]]; then dir=${BASH_REMATCH[1]}
elif [[ $input =~ $re_s ]]; then dir=${BASH_REMATCH[1]}
elif [[ $input =~ $re_b ]]; then dir=${BASH_REMATCH[1]}
elif [[ $input =~ $re_cwd ]]; then dir=${BASH_REMATCH[1]}
fi
dir=$(unjson "${dir:-$PWD}")
git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 || exit 0
reasons=()
email=$(git -C "$dir" config user.email)
[ -n "$email" ] && is_blocked "$email" && reasons+=("the repo signs with a blocked email ($email)")
if is_git push; then
  if git -C "$dir" rev-parse '@{u}' >/dev/null 2>&1; then range=('@{u}..HEAD'); else range=(HEAD --not --remotes); fi
  for c in $(git -C "$dir" log "${range[@]}" --format='%ae%n%ce' 2>/dev/null | sort -u); do
    is_blocked "$c" && { reasons+=("commits about to be pushed are signed with a blocked email ($c)"); break; }
  done
fi
[ ${#reasons[@]} -eq 0 ] && exit 0
msg="git-identity (your configuration in $CONF): ${reasons[*]}. Sign with ${preferred:-another identity}. Run the git-identity:configure skill (it changes the repo's identity and offers to rewrite commits not yet pushed). Do not bypass this with -c user.email or GIT_* variables. Reply to the user in their language."
if [ "$reaction" = warn ]; then
  esc=$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"WARNING (mode=warn, command not blocked): %s"}}\n' "$esc"
  exit 0
fi
echo "BLOCKED by $msg" >&2
exit 2
