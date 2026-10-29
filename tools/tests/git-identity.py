"""Test of the git-identity hook with real JSON (json.dumps escapes the way Claude Code does).
Usage: python -I tools/tests/git-identity.py plugins/git-identity/hooks/git-identity.sh
Runs on Windows (Git for Windows) and on Linux/macOS. Expect `FAILURES: 0`."""
import json, os, pathlib, shutil, subprocess, sys, tempfile

HOOK = sys.argv[1]


def find_bash():
    # On Windows, prefer the bash.exe of Git for Windows: a bash.exe on PATH may be WSL's launcher.
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            cand = pathlib.Path(git).resolve().parent.parent / "bin" / "bash.exe"
            if cand.exists():
                return str(cand)
    return shutil.which("bash") or sys.exit("bash not found")


BASH = find_bash()
S = pathlib.Path(tempfile.mkdtemp(prefix="gid-test-"))
NOHOOKS = f"core.hooksPath={os.devnull}"

home = S / "home"
(home / ".config/claude-workbench").mkdir(parents=True)
(home / ".config/claude-workbench/git-identity").write_text(
    "blocked=Me@Blocked.test\npreferred=1+me@users.noreply.github.com\n", encoding="utf-8", newline="\n")
blocked_repo, ok = S / "repo blocked", S / "repoOK"


def git(repo, *a, env=None):
    subprocess.run(["git", "-C", str(repo), "-c", NOHOOKS, *a], check=True, capture_output=True,
                   env={**os.environ, **(env or {})})


for r, mail in ((blocked_repo, "me@blocked.test"), (ok, "1+me@users.noreply.github.com")):
    r.mkdir(parents=True); git(r, "init", "-q"); git(r, "config", "user.email", mail); git(r, "config", "user.name", "me")
git(ok, "commit", "-q", "--allow-empty", "-m", "base")
git(ok, "commit", "-q", "--allow-empty", "-m", "blocked, unpushed", env={"GIT_AUTHOR_EMAIL": "me@blocked.test"})
ok2 = S / "repoOK2"; ok2.mkdir(); git(ok2, "init", "-q"); git(ok2, "config", "user.email", "1+me@users.noreply.github.com")
git(ok2, "config", "user.name", "me"); git(ok2, "commit", "-q", "--allow-empty", "-m", "clean")


def run(mode, stdin="", h=home, project=None, extra_env=None):
    env = {**os.environ, "HOME": str(h), **(extra_env or {})}
    if project: env["CLAUDE_PROJECT_DIR"] = str(project)
    p = subprocess.run([BASH, HOOK, mode], input=stdin, capture_output=True, text=True, encoding="utf-8", env=env)
    return p.returncode, (p.stdout + p.stderr).strip().replace("\n", " ")[:110]


cases = [  # (name, cwd, tool, command, expected exit)
    ("1 commit, blocked repo (cwd)", blocked_repo, "Bash", 'git commit -m "x"', 2),
    ("2 commit, OK repo (cwd)", ok2, "Bash", 'git commit -m "x"', 0),
    ("3 -C \"path with spaces\", message with 'git push'", ok2, "Bash", f'git -C "{blocked_repo}" commit -m "git push"', 2),
    ("4 -C 'path' push (PowerShell)", ok2, "PowerShell", f"git -C '{blocked_repo.as_posix()}' push", 2),
    ("5 push with an unpushed blocked commit", ok, "Bash", "cd x && git push origin main", 2),
    ("6 commit in OK repo with an old blocked commit", ok, "Bash", "git commit -m y", 0),
    ("7 ls", blocked_repo, "Bash", "ls -la", 0),
    ("8 git status, blocked repo", blocked_repo, "Bash", "git status", 0),
    ("9 'gitcommit' and git log --grep=commit", blocked_repo, "Bash", "echo gitcommit; git log --grep=commit", 0),
    ("10 -C path without quotes", ok2, "Bash", f"git -C {ok.as_posix()} push", 2),
    ("11 outside a repo", S, "Bash", "git commit -m x", 0),
]
failures = 0
for name, cwd, tool, cmd, expected in cases:
    stdin = json.dumps({"cwd": str(cwd), "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": cmd}})
    code, out = run("before", stdin)
    mark = "OK " if code == expected else "BAD"; failures += code != expected
    print(f"{mark} {name:<52} exit={code} {out}")

# mode=warn: lets the command through (exit 0) but tells Claude
stdin = json.dumps({"cwd": str(blocked_repo), "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git commit -m x"}})
code, out = run("before", stdin, extra_env={"CLAUDE_PLUGIN_OPTION_MODE": "warn"})
good = code == 0 and "additionalContext" in out and "mode=warn" in out
failures += not good
print(f"{'OK ' if good else 'BAD'} {'12 mode=warn (exit 0 + additionalContext)':<52} exit={code} {out}")

for name, project, h, expected_txt in (("start, blocked repo", blocked_repo, home, "blocked email"), ("start, OK repo", ok2, home, ""),
                                       ("start, not configured", ok2, S / "empty", "Not configured")):
    code, out = run("start", "", h, project)
    good = code == 0 and ((expected_txt in out) if expected_txt else out == "")
    failures += not good
    print(f"{'OK ' if good else 'BAD'} {name:<52} exit={code} {out}")
code, out = run("before", json.dumps({"cwd": str(blocked_repo), "tool_input": {"command": "git commit"}}), S / "empty")
print(f"{'OK ' if code == 0 else 'BAD'} {'before, not configured (lets it through)':<52} exit={code}"); failures += code != 0
shutil.rmtree(S, ignore_errors=True)
print("FAILURES:", failures)
sys.exit(1 if failures else 0)
