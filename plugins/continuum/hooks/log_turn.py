"""Hook "log": one line per turn with work, WITHOUT using AI.

Attached to Stop (main agent) and SubagentStop (subagents). Reads the transcript, looks only at the
last turn and, if files changed or notes went to the memory, appends a line to <vault>/log/YYYY-MM-DD.md and,
unless autocommit is off, makes a commit in the vault's repo with everything pending (the turn's work and anything
fixed by hand in Obsidian). With no repo, no git identity, or an email on the `blocked=` list of
~/.config/claude-workbench/git-identity, it does not commit: the line stays anyway.

Options: `autocommit` (default true): continuum.autocommit=false in .claude/claude-workbench.conf, or the user option.

Never blocks nor fails towards Claude Code: on any error it exits 0.

Vault: the same one the memory MCP uses (vault.py). If it does not exist, it does nothing: so it can be installed
for all projects without creating folders in those that do not use it.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True  # leave no __pycache__ in the plugin folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vault import find_vault, label, option_on, project_root, task_path  # noqa: E402

IDENTITY_CONF = Path.home() / ".config" / "claude-workbench" / "git-identity"
FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
# loose (the project's .mcp.json) or from the plugin: mcp__plugin_<plugin>_<server>__<tool>
MEMORY_PREFIXES = ("mcp__memory__", "mcp__plugin_continuum_memory__")


def memory_tool(name):
    """'mcp__plugin_continuum_memory__note' -> 'note'; any other tool -> None."""
    for prefix in MEMORY_PREFIXES:
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def last_turn(transcript):
    """The assistant's tool_use blocks since the last real user message."""
    uses = []
    with open(transcript, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") == "user":
                c = d.get("message", {}).get("content")
                is_result = isinstance(c, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in c)
                if not is_result and not d.get("isMeta"):
                    uses = []  # a new turn starts
            elif d.get("type") == "assistant":
                for b in d.get("message", {}).get("content", []) or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        uses.append(b)
    return uses


def inside(path, roots):
    """Is the path in the project or in the vault? (anything else, e.g. a scratchpad, stays out of the log)."""
    try:
        r = Path(path).resolve()
    except (OSError, ValueError):
        return False
    return any(r == b or b in r.parents for b in roots)


def summarize(uses, cwd, roots=()):
    files, tasks, decisions = [], [], 0
    commands = 0
    for u in uses:
        name, inp = u.get("name", ""), u.get("input") or {}
        if name in FILE_TOOLS and inp.get("file_path"):
            path = inp["file_path"]
            if roots and not inside(path, roots):
                continue
            try:
                path = os.path.relpath(path, cwd) if cwd else path
            except ValueError:  # another drive on Windows
                pass
            path = path.replace("\\", "/")  # normalize before comparing: otherwise it repeats
            if path not in files:
                files.append(path)
        elif name in ("Bash", "PowerShell"):
            commands += 1
        elif memory_tool(name) == "note" and inp.get("task"):
            t = task_path(inp["task"])
            if t not in tasks:
                tasks.append(t)
        elif memory_tool(name) == "decide":
            decisions += 1
    return files, tasks, decisions, commands


def blocked_emails():
    """The `blocked=` lines of the git-identity config (this hook does not depend on that plugin, it only reads its file)."""
    try:
        lines = IDENTITY_CONF.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {l.split("=", 1)[1].strip().lower() for l in lines if l.startswith("blocked=")}


def commit(vault, message):
    if not (vault / ".git").exists():
        return

    def git(*args):
        return subprocess.run(["git", "-C", str(vault), *args], capture_output=True,
                              encoding="utf-8", errors="replace", timeout=15)

    email = git("config", "user.email").stdout.strip().lower()
    if not email or email in blocked_emails():
        return
    git("add", "-A")
    git("-c", "user.useConfigOnly=true", "commit", "-q", "-m", message)  # no changes: git fails, no harm


def main():
    event = json.loads(sys.stdin.read() or "{}")
    base = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    vault = find_vault(base)
    if not vault.is_dir():
        return
    is_sub = event.get("hook_event_name") == "SubagentStop"
    transcript = event.get("agent_transcript_path") if is_sub else None
    transcript = transcript or event.get("transcript_path")
    if not transcript or not Path(transcript).exists():
        return
    roots = (project_root(base).resolve(), vault.resolve())
    files, tasks, decisions, commands = summarize(last_turn(transcript), event.get("cwd"), roots)
    if not (files or tasks or decisions):
        return  # a turn with no persistent work: do not clutter the log

    who = f"sub:{event.get('agent_type') or 'subagent'}" if is_sub else label(vault, "main")
    project = project_root(base).name
    parts = [f"{datetime.now():%H:%M}", project, who,
             f"{label(vault, 'session')} {str(event.get('session_id', ''))[:8]}"]
    if tasks:
        parts.append(" ".join(f"[[{t}]]" for t in tasks))
    if decisions:
        parts.append(label(vault, "decisions_n", n=decisions))
    if files:
        sample = ", ".join(f"`{a}`" for a in files[:8])
        parts.append(f"{label(vault, 'files')} {sample}" + (f" (+{len(files) - 8})" if len(files) > 8 else ""))
    if commands:
        parts.append(f"{commands} {label(vault, 'commands')}")

    target = vault / "log" / f"{datetime.now():%Y-%m-%d}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    is_new = not target.exists()
    with open(target, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"# {label(vault, 'log_title', date=f'{datetime.now():%Y-%m-%d}')}\n\n{label(vault, 'log_note')}\n\n")
        f.write("- " + " · ".join(parts) + "\n")
    if option_on("continuum", "autocommit", base):
        commit(vault, label(vault, "log_commit") + " · ".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - a logging hook must never break the session
        pass
    sys.exit(0)
