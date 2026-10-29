"""Test of the model-protocol hook: default, user option, project conf, priority and custom text.
Usage: python -I tools/tests/model-protocol.py plugins/model-protocol/hooks/model-protocol.sh
Runs on Windows (Git for Windows) and on Linux/macOS. Expect `FAILURES: 0`."""
import os, pathlib, shutil, subprocess, sys, tempfile

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
S = pathlib.Path(tempfile.mkdtemp(prefix="mp-test-"))
(S / "home").mkdir(); proj = S / "proj"; (proj / ".claude").mkdir(parents=True)
conf = proj / ".claude" / "claude-workbench.conf"
failures = 0


def run(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}
    env.update({"HOME": str(S / "home"), "CLAUDE_PROJECT_DIR": str(proj), **extra})
    p = subprocess.run([BASH, HOOK], capture_output=True, text=True, encoding="utf-8", env=env)
    return p.returncode, p.stdout


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'OK ' if ok else 'BAD'} {name}" + (f"  [{detail}]" if detail and not ok else ""))


c, out = run()
check("1 default: reminder printed", c == 0 and out.startswith("[Model protocol Opus/Sonnet/Haiku") and "Reply to the user in their language" in out, out[:80])
c, out = run(CLAUDE_PLUGIN_OPTION_ENABLED="false")
check("2 user option false: silent", c == 0 and out == "", out)
conf.write_text("continuum.autocommit=true\r\nmodel-protocol.enabled = false\r\n", encoding="utf-8", newline="")
c, out = run()
check("3 project conf false (CRLF, spaces): silent", c == 0 and out == "", out)
conf.write_text("model-protocol.enabled=true\n", encoding="utf-8")
c, out = run(CLAUDE_PLUGIN_OPTION_ENABLED="false")
check("4 project true wins over user false", c == 0 and out.startswith("[Model protocol Opus"), out[:80])
conf.unlink()
(S / "home" / ".claude").mkdir()
(S / "home" / ".claude" / "model-protocol.md").write_text("user text\n", encoding="utf-8")
c, out = run()
check("5 user custom text", "user text" in out and "custom text" in out, out)
(proj / ".claude" / "model-protocol.md").write_text("project text\n", encoding="utf-8")
c, out = run()
check("6 project custom text wins", "project text" in out and "user text" not in out, out)
shutil.rmtree(S, ignore_errors=True)
print("FAILURES:", failures)
sys.exit(1 if failures else 0)
