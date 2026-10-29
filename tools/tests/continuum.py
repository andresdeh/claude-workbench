"""Test of the continuum plugin: MCP, log hook, vault resolution and migration of an old Spanish vault.
Usage: python -I tools/tests/continuum.py plugins/continuum
Runs on Windows and Linux. Expect `FAILURES: 0`."""
import json, os, pathlib, shutil, subprocess, sys, tempfile

PLUGIN = pathlib.Path(sys.argv[1]).resolve()
PY = sys.executable
S = pathlib.Path(tempfile.mkdtemp(prefix="cont-test-"))
failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'OK ' if ok else 'BAD'} {name}" + (f"  [{detail}]" if detail and not ok else ""))


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, encoding="utf-8", errors="replace")


def env_with(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE_", "CONTINUUM_"))}
    e["HOME"] = e["USERPROFILE"] = str(S / "home")
    e.update(extra)
    return e


(S / "home").mkdir()

# ---------------------------------------------------------------- MCP
vault = S / "v-memory"; vault.mkdir()
server = subprocess.Popen([PY, "-I", str(PLUGIN / "mcp" / "server.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env_with(CONTINUUM_VAULT=str(vault)))


def rpc(method, params=None, id_=[0]):
    id_[0] += 1
    server.stdin.write(json.dumps({"jsonrpc": "2.0", "id": id_[0], "method": method, "params": params or {}}) + "\n")
    server.stdin.flush()
    return json.loads(server.stdout.readline())["result"]


def call(name, **args):
    r = rpc("tools/call", {"name": name, "arguments": args})
    return r["isError"], r["content"][0]["text"]


check("mcp initialize", rpc("initialize")["serverInfo"]["name"] == "memory")
check("mcp tools", sorted(t["name"] for t in rpc("tools/list")["tools"]) == ["decide", "note", "read", "search"])
err, out = call("note", task="My task", text="First line\nmore", status="in progress", model="opus", author="main")
check("note creates the task", not err and "Created [[tasks/my-task]]" in out and "status: in progress" in out, out)
err, out = call("note", task="tasks/my-task", text="second", status="invalid")
check("note rejects a bad status", err and "Invalid status" in out, out)
err, out = call("decide", title="Use X", text="because Y", task="my-task")
check("decide links to the task", not err and "linked to [[tasks/my-task]]" in out, out)
err, out = call("read", note="tasks/my-task")
check("read task", not err and "### " in out and "Decision: [[decisions/" in out, out)
err, out = call("search", text="because")
check("search finds the decision", not err and "decisions/" in out, out)
err, out = call("read", note="../../etc/passwd")
check("path outside the vault refused", err, out)
router = (vault / "tasks" / "_router.md").read_text(encoding="utf-8")
check("router English labels and states", "# Tasks" in router and "## in progress" in router and "→ opus" in router, router)
fm = (vault / "tasks" / "my-task.md").read_text(encoding="utf-8")
check("frontmatter keys", all(k in fm for k in ("status:", "created:", "updated:", "last:", "model:")), fm[:200])
(vault / ".continuum.json").write_text('{"language": "es"}', encoding="utf-8")
call("note", task="my-task", text="otra")
router = (vault / "tasks" / "_router.md").read_text(encoding="utf-8")
check("router follows .continuum.json (es)", "# Tareas" in router and "## in progress" in router, router)
server.stdin.close(); server.wait(timeout=5)

# ---------------------------------------------------------------- vault resolution
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLUGIN))
import vault as V  # noqa: E402

proj = S / "work" / "proj"; (proj / ".claude").mkdir(parents=True); (proj / "sub").mkdir()
subprocess.run(["git", "-C", str(proj), "init", "-q"], check=True)
for k in list(os.environ):
    if k.startswith("CONTINUUM_") or k == "CLAUDE_PROJECT_DIR":
        del os.environ[k]
check("vault by convention (from a subfolder)", V.find_vault(proj / "sub") == (S / "work" / "proj-memory").resolve())
(proj / ".claude" / "claude-workbench.conf").write_text("model-protocol.enabled=false\r\ncontinuum.vault = ../elsewhere\r\n", encoding="utf-8")
check("vault from conf (relative to project root)", V.find_vault(proj) == (S / "work" / "elsewhere").resolve())
(proj / ".claude" / "claude-workbench.conf").write_text("continuum.autocommit=false\n", encoding="utf-8")
check("autocommit off from conf", V.option_on("continuum", "autocommit", proj) is False)
os.environ["CLAUDE_PLUGIN_OPTION_AUTOCOMMIT"] = "false"
(proj / ".claude" / "claude-workbench.conf").write_text("continuum.autocommit=true\n", encoding="utf-8")
check("project conf wins over the user option", V.option_on("continuum", "autocommit", proj) is True)
del os.environ["CLAUDE_PLUGIN_OPTION_AUTOCOMMIT"]
(proj / ".claude" / "claude-workbench.conf").unlink()

# ---------------------------------------------------------------- hook
def make_vault(path, email="me@example.test"):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(path), "init", "-q"], check=True)
    git(path, "config", "user.email", email); git(path, "config", "user.name", "me")
    (path / "seed.md").write_text("seed\n", encoding="utf-8")
    git(path, "add", "-A"); git(path, "-c", "user.useConfigOnly=true", "commit", "-q", "-m", "seed")


def run_hook(project, transcript, **extra):
    event = {"hook_event_name": "Stop", "transcript_path": str(transcript), "cwd": str(project), "session_id": "abcdef123456"}
    return subprocess.run([PY, "-I", str(PLUGIN / "hooks" / "log_turn.py")], input=json.dumps(event), capture_output=True,
                          text=True, encoding="utf-8", env=env_with(CLAUDE_PROJECT_DIR=str(project), **extra))


def transcript_for(project):
    lines = [
        {"type": "user", "message": {"content": "do it"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": str(project / "a.txt")}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": str(project / "a.txt")}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": str(S / "outside.txt")}},
            {"type": "tool_use", "name": "mcp__plugin_continuum_memory__note", "input": {"task": "My task"}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
    ]
    t = S / "transcript.jsonl"
    t.write_text("\n".join(json.dumps(l) for l in lines) + "\n", encoding="utf-8")
    return t


def commits(v):
    return len(git(v, "log", "--format=%h").stdout.split())


tr = transcript_for(proj)
v = S / "work" / "proj-memory"; make_vault(v)
before = commits(v)
r = run_hook(proj, tr)
logf = next((v / "log").glob("*.md"), None)
text = logf.read_text(encoding="utf-8") if logf else ""
check("hook writes the log line (en)", "[[tasks/my-task]]" in text and "`a.txt`" in text and "outside.txt" not in text
      and text.count("a.txt") == 1 and "1 commands" in text and "session abcdef12" in text, text + r.stderr)
check("hook commits the vault", commits(v) == before + 1, git(v, "log", "--format=%s", "-1").stdout)

(v / ".continuum.json").write_text('{"language": "es"}', encoding="utf-8")
for f in (v / "log").glob("*.md"): f.unlink()
git(v, "add", "-A"); git(v, "-c", "user.useConfigOnly=true", "commit", "-q", "-m", "es")
run_hook(proj, tr)
text = next((v / "log").glob("*.md")).read_text(encoding="utf-8")
check("hook labels follow the vault language (es)", "# Bitácora" in text and "sesión abcdef12" in text and "comandos" in text, text)

n = commits(v)
run_hook(proj, tr, CLAUDE_PLUGIN_OPTION_AUTOCOMMIT="false")
check("autocommit=false (user option): line written, no commit", commits(v) == n and git(v, "status", "--short").stdout.strip() != "")
git(v, "add", "-A"); git(v, "-c", "user.useConfigOnly=true", "commit", "-q", "-m", "sync")
n = commits(v)
(S / "home" / ".config" / "claude-workbench").mkdir(parents=True)
(S / "home" / ".config" / "claude-workbench" / "git-identity").write_text("blocked=Me@Example.test\n", encoding="utf-8")
run_hook(proj, tr)
check("blocked e-mail: no commit", commits(v) == n)
(S / "home" / ".config" / "claude-workbench" / "git-identity").unlink()
r = run_hook(S / "nowhere", tr)
check("no vault: hook does nothing and exits 0", r.returncode == 0)

# ---------------------------------------------------------------- migration
old = S / "memoria-Demo"
for d in ("tareas", "decisiones", "bitacora", "agentes"):
    (old / d).mkdir(parents=True)
(old / "indice.md").write_text("# Memoria\n- [[tareas/_router|Tareas]]\n- [[agentes/_router|Agentes]]\n", encoding="utf-8")
(old / "tareas" / "_router.md").write_text("# Tareas\n\n## en curso\n- [[tareas/t1]] · 2026-10-01 · → opus · x\n", encoding="utf-8")
(old / "tareas" / "t1.md").write_text("---\nestado: en curso\ncreada: 2026-10-01\nactualizada: 2026-10-02 10:00\nultimo: algo - bien\nmodelo: opus\n---\n\n# T1\n\n### 2026-10-02 10:00 · claude\nVer [[decisiones/2026-10-02-d]]\n", encoding="utf-8")
(old / "decisiones" / "2026-10-02-d.md").write_text("---\nfecha: 2026-10-02 10:00\nautor: claude\ntarea: \"[[tareas/t1]]\"\n---\n\n# D\nTarea: [[tareas/t1]]\n", encoding="utf-8")
(old / "bitacora" / "2026-10-02.md").write_text("# Bitácora\n- 10:00 · [[tareas/t1]]\n", encoding="utf-8")
(old / "agentes" / "lector.md").write_text("# lector\n", encoding="utf-8")
make_vault(old)
mig = [PY, "-I", str(PLUGIN / "migrate.py"), str(old)]
r = subprocess.run(mig, capture_output=True, text=True, encoding="utf-8", env=env_with())
check("migrate plan changes nothing", (old / "tareas").is_dir() and not (old / "tasks").exists() and "plan only" in r.stdout, r.stdout + r.stderr)
r = subprocess.run(mig + ["--apply", "--commit"], capture_output=True, text=True, encoding="utf-8", env=env_with())
new = S / "Demo-memory"
t1 = (new / "tasks" / "t1.md").read_text(encoding="utf-8") if new.exists() else ""
check("migrate renames the folder and the subfolders", new.is_dir() and not old.exists()
      and all((new / d).is_dir() for d in ("tasks", "decisions", "log", "agents")) and (new / "index.md").exists()
      and (new / "agents" / "reader.md").exists(), r.stdout + r.stderr)
check("migrate rewrites keys, states and links", "status: in progress" in t1 and "model: opus" in t1 and "last: algo - bien" in t1
      and "[[decisions/2026-10-02-d]]" in t1 and "estado" not in t1, t1)
dec = (new / "decisions" / "2026-10-02-d.md").read_text(encoding="utf-8") if new.exists() else ""
check("migrate decisions and router", 'task: "[[tasks/t1]]"' in dec and "## in progress" in (new / "tasks" / "_router.md").read_text(encoding="utf-8"), dec)
check("migrate writes .continuum.json (es) and commits", json.loads((new / ".continuum.json").read_text())["language"] == "es"
      and git(new, "log", "--format=%s", "-1").stdout.strip() == "Migrate vault to continuum names")
r = subprocess.run([PY, "-I", str(PLUGIN / "migrate.py"), str(new)], capture_output=True, text=True, encoding="utf-8", env=env_with())
check("migrate is idempotent", "nothing to migrate" in r.stdout, r.stdout)

shutil.rmtree(S, ignore_errors=True)
print("FAILURES:", failures)
sys.exit(1 if failures else 0)
