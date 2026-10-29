---
name: init-project
description: Prepares a project to work with continuum - creates the sibling vault ../<project>-memory as its own git repo (tasks, decisions, log), the CLAUDE.md block between markers, the .gitignore that keeps CLAUDE.md and local settings private, and the first task. Also updates an existing setup and migrates a vault written with the Spanish names of the old `continuo` plugin. Use when the user starts a new project with continuum, asks to connect a project to the memory or to Obsidian, or when the memory MCP says the vault does not exist.
---

# Start a project with continuum

Language: talk to the user in their language, and write the notes, the `CLAUDE.md` block and the first task in it too. **Never
translate identifiers**: folders (`tasks/ decisions/ log/ agents/`), states (`open`, `in progress`, `done`), frontmatter keys,
tool names (`search read note decide`), markers and `[[links]]`. The templates are **at the end of this file** (nothing else needs
to be read). Two **sibling** folders, each with its own git:

```
<parent>/
  <project>/          the code (published if you want)
  <project>-memory/   the vault (never published; no remote)
```

Siblings and not one inside the other: a `git add .` of the code cannot drag the memory along. The memory MCP and the hook find
the vault by this name (or by `continuum.vault=` in `.claude/claude-workbench.conf`). Everything written into `CLAUDE.md` goes
between markers:

```
<!-- claude-workbench:continuum v0.5.1 start -->
... the template "CLAUDE.md (block)" ...
<!-- claude-workbench:continuum end -->
```

## Steps (in order; write nothing before step 4)

1. **Diagnose (read-only, one Bash command).** Root = `git -C "$CLAUDE_PROJECT_DIR" rev-parse --show-toplevel` (no repo:
   `$CLAUDE_PROJECT_DIR`). Name = the last folder of the root. Find out:
   - Does the code have git? A remote (`git remote -v`)? Commits? Which `user.email` and `user.name` (local, else global)?
   - The vault, in this order: `continuum.vault=` in `.claude/claude-workbench.conf`; else `../<name>-memory`. Does it not exist
     (→ create) · exist with `index.md` (→ already there; only check what is missing) · exist with something else (→ **stop** and
     ask; never write into a foreign folder)? **Legacy vault**: `../memoria-<name>` with `indice.md` or `tareas/` → this is a
     **migration** (step 4, "Migration").
   - `CLAUDE.md`: does it exist? Is it versioned (`git ls-files --error-unmatch CLAUDE.md`)? Does it already have the markers
     `claude-workbench:continuum` (→ **update**: compare versions and replace only what is inside)? The legacy markers
     `claude-tools:continuo` (→ migration: the block is replaced by the new one)? Does it declare an author or e-mail for commits?
   - `.gitignore`: does it exist? Does it already ignore `CLAUDE.md` and `.claude/settings.local.json`? Legacy block `claude-tools:continuo`?
   - `.claude/settings.local.json`: legacy permissions `mcp__plugin_continuo_memoria__*`?
   - `docs/` status files (e.g. `docs/CURRENT-STATE.md`): if one exists, read its first 40 lines to propose the first task.
   - Summarize in 3-6 lines.
2. **Ask with `AskUserQuestion`** (only what applies; the first option is the recommended one):
   - **Language** of the vault (new vault only): the user's language. `en` and `es` have label tables; for any other, the notes
     are written in that language but what the code writes (routers, log) falls back to English.
   - If `CLAUDE.md` is already versioned: *stop versioning it* (`git rm --cached`; it stays in the history already made, and if it
     was published it is already public) · *keep it versioned* (the block carries no paths or private data).
   - First task: *propose one from what was diagnosed* · *start with no tasks*. Also ask which model goes next.
   - **Identity of the vault** (see step 4): only if it cannot be resolved without asking.
3. **Show the plan and the diff**: the vault folder and its files; the lines added to `CLAUDE.md`, `.gitignore` and
   `.claude/settings.local.json`; the git commands (the two `init` if missing, the vault's local identity and the **only**
   commit: the vault's initial one). For a migration, the output of `migrate.py` without `--apply`. Wait for the yes.
4. **Write** (accents: Write/Edit, never PowerShell 5.1; git through Bash):
   - **Vault**: create the folders and files of the "Vault" templates (`<project>` → real name, `YYYY-MM-DD` → today), and
     `.continuum.json` with `{"language": "<code>"}`. An existing file is **never** overwritten. `git init` inside and the **vault's
     local identity**, in this order: the vault's own `user.email` if already set → `preferred=` of
     `~/.config/claude-workbench/git-identity` if that file exists → the e-mail git would use (the code's local one, else the global
     one), **shown to the user and confirmed in the plan** → if none, ask. `user.name`: the code's → the global one → ask.
     Never an e-mail on the `blocked=` list of that file. Set `git config user.useConfigOnly true` in the vault, then
     `git add -A` and `git -c user.useConfigOnly=true commit -m "Initial vault (continuum)"`: without that option git on Windows
     invents an identity from the user and machine names instead of failing, and the hook would then never commit. **No remote.**
   - **Code**: `git init` only if it had none. `.gitignore`: append the template block at the end (create it if missing; do not
     touch the other lines; replace the legacy block if there is one). If *stop versioning `CLAUDE.md`* was chosen: `git rm --cached CLAUDE.md`.
   - **`CLAUDE.md`**: only between markers, `<project>` → real name (if it does not exist: a title and the block). A legacy
     `claude-tools:continuo` block is replaced whole, markers included; nothing else. **If `CLAUDE.md` declares another commit
     author or e-mail than the git config, point it out and ask which one stays in the git config; do not edit that line yourself**
     (the git config rules: it is what git and the hooks read).
   - **`.claude/settings.local.json`**: merge (read, add, never lose keys) the template permissions; offer to remove the legacy
     `mcp__plugin_continuo_memoria__*` ones. Do not add `env.CONTINUUM_VAULT` (it is only for tests): if the vault is not at
     `../<name>-memory`, put `continuum.vault=<folder>` in `.claude/claude-workbench.conf`.
   - **Migration** (legacy vault `memoria-<name>`): after the yes, run
     `sh "${CLAUDE_PLUGIN_ROOT}/launcher.sh" "${CLAUDE_PLUGIN_ROOT}/migrate.py" "<legacy vault>" --apply --commit`
     (the same command without `--apply` printed the plan). It renames folders and notes, rewrites keys, states and links, writes
     `.continuum.json` (`es`), commits and renames the folder to `<name>-memory`. If the rename fails (Obsidian open), tell the user to
     close it and rename the folder by hand. Then update the `CLAUDE.md` block, `.gitignore` and permissions as above. Obsidian:
     the vault must be reopened from its new path.
   - **First task**, if chosen: with the `note` tool of the `memory` MCP (`status: open`, `model` the chosen one). If the MCP is
     not loaded yet, say to ask for it after restarting: "note the first task: …".
5. **Verify by re-reading**: `git -C <vault> log --format='%h %ae'` (one commit, with the intended e-mail) and `git remote -v`
   (empty); `git check-ignore CLAUDE.md .claude/settings.local.json` in the code (if chosen private); markers only once in
   `CLAUDE.md` and the rest as before; `read tasks/_router` through the MCP if it is loaded.
6. **Report**: full paths of what was created and touched, and that in Obsidian the folder `<name>-memory` is opened as a vault
   (it need not be open). Do not commit in the code unless asked; if the code has no `user.email` (local or global), warn that
   before its first commit the user should set one (git would invent one).

## Templates

Copy the text between `~~~~` as is (without the `~~~~` line), then write the prose in the user's language.

### CLAUDE.md (block)

~~~~markdown
## Project memory (continuum)

State does not live in the chat nor in `docs/`: it lives in the vault `../<project>-memory` and is used **through the `memory`
MCP** (`search`, `read`, `note`, `decide`), never by reading or editing its files directly.

- **At the start**: `read tasks/_router`. If the user names a task, `read` that one (it brings the latest entries). For something
  specific, `search`. Do not read long documentation "to catch up".
- **When deciding something**: `decide` with its task, at that moment, not at the end.
- **When finishing a stretch** (a step of the plan, a block of design, a fix): `note` in the task where it stands (the first line
  is the summary), with `status` and the `model` of the next step (`opus` design and decisions · `sonnet` mechanical with judgment
  · `haiku` simple mechanical). Then **propose `/clear` and stop**, even if the next step uses the same model: short threads per
  stretch save the most. End with a fixed line «📌 Noted in [[tasks/…]] → `/clear`[ · `/model <x>`] · "continue with
  [[tasks/…]]"». No need to write a prompt: the task replaces it. Skip the `/clear` request only if the stretch was short.
- **Subagents** (inside the work, never to decide): `continuum:reader` to read a lot and bring back 5-10 lines;
  `continuum:tester` to run tests and bring back only the failures.
- The vault is never published. This `CLAUDE.md` is private to the project.
~~~~

### Code .gitignore (block at the end)

~~~~text
# claude-workbench:continuum start
CLAUDE.md
CLAUDE.local.md
.claude/settings.local.json
# claude-workbench:continuum end
~~~~

(If keeping `CLAUDE.md` versioned was chosen, the block goes without the `CLAUDE.md` line.)

### .claude/settings.local.json (keys to merge)

~~~~json
{
  "permissions": {
    "allow": [
      "mcp__plugin_continuum_memory__search",
      "mcp__plugin_continuum_memory__read",
      "mcp__plugin_continuum_memory__note",
      "mcp__plugin_continuum_memory__decide"
    ]
  }
}
~~~~

### Vault: `index.md`

~~~~markdown
# Memory of <project>

Root router. Claude writes it through the memory MCP; here it is read and, if needed, fixed by hand.
Each folder has its own `_router` (one line per note). Created YYYY-MM-DD.

- [[tasks/_router|Tasks]] · one note per task: status and the model for the next step
- [[decisions/_router|Decisions]] · one note per decision, linked to its task
- [[log/_router|Log]] · one line per turn with work, written by a hook without AI
- [[agents/_router|Agents]] · what each kind of subagent has learned
~~~~

### Vault: `tasks/_router.md` and `decisions/_router.md`

The title and the italic line must match the label table of the vault's language (the code rewrites these files in that language):

| Language | `tasks/_router.md` | `decisions/_router.md` |
|---|---|---|
| `en` (and any other) | `# Tasks` · `_Generated by the memory MCP. Do not edit by hand._` | `# Decisions` · `_Generated by the memory MCP. The 50 most recent._` |
| `es` | `# Tareas` · `_Generado por el MCP memoria. No editar a mano._` | `# Decisiones` · `_Generado por el MCP memoria. Las 50 más recientes._` |

### Vault: `log/_router.md`

~~~~markdown
# Log

One file per day (`YYYY-MM-DD.md`), written by the hook at the end of each turn with work. No AI: just which agent, which tasks
and which files.
~~~~

### Vault: `agents/_router.md`

~~~~markdown
# Agents

One note per kind of subagent (`agents/reader`, `agents/tester`): what it is worth knowing when it starts in this project (where
the logs are, how tests are run). The subagent reads it at the start; it is written by hand.
~~~~

### Vault: `.gitignore`

~~~~text
.obsidian/workspace*.json
.obsidian/cache
.trash/
*.md.tmp
~~~~
