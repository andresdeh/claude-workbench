#!/usr/bin/env bash
# model-protocol.sh — UserPromptSubmit hook for Claude Code.
# Injects, on EVERY turn, a reminder of the Opus/Sonnet/Haiku split, so it does not depend on
# the model "remembering" a rule written in CLAUDE.md.
#
# Settings, lowest to highest priority:
#   1. plugin default (enabled)
#   2. user option "enabled" (arrives as CLAUDE_PLUGIN_OPTION_ENABLED; change it with /config)
#   3. project file .claude/claude-workbench.conf, line:  model-protocol.enabled=false
# Own text, no script edits: .claude/model-protocol.md in the project, else ~/.claude/model-protocol.md.
#
# Output: plain text on stdout with exit 0 -> Claude Code adds it as context for the turn.
# It does not read the user's prompt and writes nothing: read-only, and it never fails.

PROTOCOL_VERSION="2.2.0"
PROJECT="${CLAUDE_PROJECT_DIR:-$PWD}"

# conf_get <key>: last value of "model-protocol.<key>=" in the project conf; empty if none.
conf_get() {
  local f="$PROJECT/.claude/claude-workbench.conf"
  [ -r "$f" ] || return 0
  grep -E "^[[:space:]]*model-protocol\.$1[[:space:]]*=" "$f" | tail -n 1 \
    | sed -E 's/^[^=]*=[[:space:]]*//; s/[[:space:]]+$//; s/\r$//'
}

enabled="$(conf_get enabled)"
[ -n "$enabled" ] || enabled="${CLAUDE_PLUGIN_OPTION_ENABLED:-true}"
case "$(printf '%s' "$enabled" | tr '[:upper:]' '[:lower:]')" in
  false|0|no|off) exit 0 ;;
esac

for f in "$PROJECT/.claude/model-protocol.md" "$HOME/.claude/model-protocol.md"; do
  if [ -r "$f" ]; then
    printf '[Model protocol v%s · custom text: %s]\n' "$PROTOCOL_VERSION" "$f"
    cat "$f"
    exit 0
  fi
done

cat <<TXT
[Model protocol Opus/Sonnet/Haiku v${PROTOCOL_VERSION} — automatic reminder]
1. The system says which model is active: use that, do not assume it.
2. Classify THIS turn's work. Opus: design, choices between alternatives, non-obvious debugging,
   security, analysis of someone else's code. Sonnet: documentation, leaving the state noted,
   commits, routine reads, edits that follow an already-decided pattern, housekeeping. Haiku:
   simple mechanical work (search, count, extract, summarize output); also as a subagent's model.
3. Only if what comes next IN THIS THREAD needs a model other than the active one: end the reply
   with a line «🔵 Model: <active> · next: <type> → better <Opus|Sonnet|Haiku>» and, if a switch
   is needed, STOP and ask for /model before going on. Switching models is a good moment for
   /clear (the cache is per model): note the state, /clear, /model, resume.
   No transition in this thread (what follows goes elsewhere, or is the same kind) → no line.
4. Any prompt written to resume in another thread starts with «Model to start: X» and marks the
   step where to switch.
Reply to the user in their language, including the 🔵 line and those prompts.
TXT
exit 0
