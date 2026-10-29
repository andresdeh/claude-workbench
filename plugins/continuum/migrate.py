"""Migrates a vault written with the Spanish names of the private predecessor (`continuo`) to the continuum names.

    sh launcher.sh migrate.py <old-vault> [--apply] [--commit]

Without --apply it only prints the plan (nothing is written). With --apply it:
  1. renames tareas/ decisiones/ bitacora/ agentes/ -> tasks/ decisions/ log/ agents/, indice.md -> index.md and the
     agent notes lector/probador -> reader/tester (`git mv` when the vault is a repo);
  2. rewrites the frontmatter keys (estado -> status, ...), the task states (abierta / en curso / hecha ->
     open / in progress / done) and the [[links]] to the renamed folders;
  3. writes .continuum.json with {"language": "es"} (the history stays in Spanish; the code keeps writing in Spanish);
  4. with --commit, commits the vault (needs a git identity; never pushes);
  5. last, renames the folder memoria-<project> -> <project>-memory.
Idempotent: on an already migrated vault it reports "nothing to migrate".
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DIRS = {"tareas": "tasks", "decisiones": "decisions", "bitacora": "log", "agentes": "agents"}
NOTES = {"agents/lector": "agents/reader", "agents/probador": "agents/tester"}
KEYS = {"estado": "status", "creada": "created", "actualizada": "updated", "ultimo": "last", "modelo": "model",
        "fecha": "date", "autor": "author", "tarea": "task"}
STATES = {"abierta": "open", "en curso": "in progress", "hecha": "done"}
LINK = re.compile(r"\[\[(tareas|decisiones|bitacora|agentes)/")
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def rewrite(text):
    """Frontmatter keys and states, then the links. Returns the new text."""
    m = FM.match(text)
    if m:
        out = []
        for line in m.group(1).split("\n"):
            key, sep, value = line.partition(":")
            new_key = KEYS.get(key.strip(), key)
            if new_key == "status":
                value = " " + STATES.get(value.strip(), value.strip())
            out.append(f"{new_key}{sep}{value}" if sep else line)
        text = "---\n" + "\n".join(out) + "\n---\n" + text[m.end():]
    text = LINK.sub(lambda mm: f"[[{DIRS[mm.group(1)]}/", text)
    text = text.replace("[[indice", "[[index")
    for old, new in NOTES.items():
        text = text.replace(f"[[{old}", f"[[{new}")
    # the tasks router groups tasks under their state
    text = re.sub(r"(?m)^## (abierta|en curso|hecha)$", lambda mm: f"## {STATES[mm.group(1)]}", text)
    return text


def git(vault, *args):
    return subprocess.run(["git", "-C", str(vault), *args], capture_output=True, encoding="utf-8", errors="replace")


def move(vault, src, dst, is_repo, apply):
    print(f"  rename {src} -> {dst}")
    if not apply:
        return
    (vault / dst).parent.mkdir(parents=True, exist_ok=True)
    if is_repo and git(vault, "mv", src, dst).returncode == 0:
        return
    os.rename(vault / src, vault / dst)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    apply, do_commit = "--apply" in argv, "--commit" in argv
    if len(args) != 1:
        sys.exit("usage: migrate.py <old-vault> [--apply] [--commit]")
    vault = Path(args[0]).resolve()
    if not vault.is_dir():
        sys.exit(f"not a folder: {vault}")
    old_dirs = [d for d in DIRS if (vault / d).is_dir()]
    old_index = (vault / "indice.md").exists()
    if not old_dirs and not old_index:
        print("nothing to migrate (no Spanish folders found).")
        return
    is_repo = (vault / ".git").exists()
    print(f"vault: {vault}  ({'git repo' if is_repo else 'no git'})  mode: {'APPLY' if apply else 'plan only'}")

    print("folders and files:")
    for d in old_dirs:
        if (vault / DIRS[d]).exists():
            sys.exit(f"cannot migrate: {DIRS[d]}/ already exists next to {d}/")
        move(vault, d, DIRS[d], is_repo, apply)
    if old_index:
        move(vault, "indice.md", "index.md", is_repo, apply)
    for old, new in NOTES.items():
        src = old if apply else old.replace("agents/", "agentes/")
        if (vault / (src + ".md")).exists():
            move(vault, src + ".md", new + ".md", is_repo, apply)

    changed = 0
    print("content rewrites (frontmatter keys, states, links):")
    for p in sorted(vault.rglob("*.md")):
        if any(part.startswith(".") for part in p.relative_to(vault).parts):
            continue
        text = p.read_text(encoding="utf-8")
        new = rewrite(text)
        if new != text:
            changed += 1
            if apply:
                p.write_text(new, encoding="utf-8", newline="\n")
    print(f"  {changed} file(s) {'rewritten' if apply else 'would change'}"
          + ("" if apply else " (counted on the old names)"))

    print("language file:")
    print('  .continuum.json {"language": "es"}')
    if apply:
        (vault / ".continuum.json").write_text(json.dumps({"language": "es"}) + "\n", encoding="utf-8", newline="\n")

    if do_commit and apply and is_repo:
        git(vault, "add", "-A")
        r = git(vault, "-c", "user.useConfigOnly=true", "commit", "-q", "-m", "Migrate vault to continuum names")
        print("commit:", "done" if r.returncode == 0 else f"FAILED ({r.stderr.strip()[:200]})")

    target = vault.with_name(vault.name[len("memoria-"):] + "-memory") if vault.name.startswith("memoria-") else None
    if target:
        print(f"vault folder: {vault.name} -> {target.name}")
        if apply:
            if target.exists():
                print(f"  NOT renamed: {target.name} already exists")
            else:
                try:
                    os.rename(vault, target)
                    print(f"  renamed. New path: {target}")
                except OSError as e:
                    print(f"  NOT renamed ({e}). Close Obsidian and any terminal inside it, then rename it by hand.")
    print("done." if apply else "plan only: run again with --apply to write.")


if __name__ == "__main__":
    main(sys.argv[1:])
