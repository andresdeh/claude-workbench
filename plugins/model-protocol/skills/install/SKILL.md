---
name: install
description: Adds or updates the "MODEL PROTOCOL (Opus / Sonnet / Haiku)" section in the project's CLAUDE.md, between markers and without touching anything else. Use when the user asks to install, enable or update the model protocol in a project, or when the model-protocol plugin was just installed and the section is missing.
---

# Install the protocol section in CLAUDE.md

The hook already reminds Claude of the protocol on every message; this skill writes the **full version** into the project's
`CLAUDE.md`. A plugin cannot ship its own `CLAUDE.md`, which is why a skill does it. The template is **at the end of this file**
(nothing else needs to be read).

Language: write the block in the user's language. Do not translate identifiers, markers or links.

Markers (everything you write goes between them; nothing outside them is touched):

```
<!-- claude-workbench:model-protocol v2.2.0 start -->
... template content ...
<!-- claude-workbench:model-protocol end -->
```

## Steps

1. **Diagnose (read-only, no questions).** Read the project's `CLAUDE.md` (`$CLAUDE_PROJECT_DIR`) if it exists. Look for:
   - the markers `claude-workbench:model-protocol` → this is an **update**: read the installed version and show the plugin's
     `CHANGELOG.md` between the two versions;
   - a hand-written model rule (the words "Opus", "Sonnet", "/model") without markers → it may duplicate or contradict;
   - the legacy markers `claude-tools:protocolo-modelo` → this is a **migration**: the old block is replaced by the new one,
     with the same diff and approval as an update;
   - a hook registered by hand in `settings.json` (search for `model-protocol.sh` or `protocolo-modelo.sh`) → the reminder would
     arrive **twice**; warn and offer to remove that block (merge and validate the JSON, never replace the whole file).
2. **Ask with `AskUserQuestion`** (recommend the first option):
   - Where it goes: *top of CLAUDE.md (recommended)* · *where I say* · *do not add the section, only the hook*.
   - If there is a rule of their own: *replace it with the section* · *merge* · *keep it and add the section*.
   - If there is no `CLAUDE.md`: confirm that a minimal one is created (title + the block). Do not run `/init` on top.
3. **Show the diff** (which lines are added and where) and wait for a yes.
4. **Write** only between markers with Edit/Write (accents intact). In an update, replace only what is inside.
5. **Verify by re-reading the file**: a single pair of markers, the rest of `CLAUDE.md` identical to before.
6. Report: file touched, version installed, how to turn the hook off in this project (`model-protocol.enabled=false` in
   `.claude/claude-workbench.conf`, or the `/model-protocol:configure` skill), and that a new hook loads on restart or on `/hooks`.

## Templates

Copy the text between `~~~~` as is (without the `~~~~` line), then write it in the user's language.

### CLAUDE.md (block between markers)

~~~~markdown
## ⭐ MODEL PROTOCOL (Opus / Sonnet / Haiku) — high priority, applies on EVERY turn

> Installed from the `model-protocol` plugin of claude-workbench (the version is in the marker above). A hook (`UserPromptSubmit`)
> reminds Claude of it on every message; this section is the full version.

**Goal:** do not spend Opus on mechanical work that Sonnet solves just as well, nor Sonnet on what Haiku solves just as well,
and do not force a smaller model onto what needs depth. The system tells which model is active on each turn: use that.

| Belongs to **Opus** | Belongs to **Sonnet** | Belongs to **Haiku** |
|---|---|---|
| design (architecture, templates, triggers, new scripts) | documentation, leaving the state noted | search, count, list |
| decisions between alternatives | commits, housekeeping | extract data from a text |
| non-obvious debugging | routine reads / queries | summarize long outputs |
| security findings and review | edits that follow an already-decided pattern | tasks of a read-only subagent |
| analysis of someone else's code | writing up something already solved, tests | |

An activity that is not in the table: decide it on the spot with the same criterion
(design / decision / non-obvious, or mechanical / already decided?).

**Mandatory checkpoints** (this is where it failed when it was just "one more rule"):
1. **At the start:** say in one line which model is active and whether the requested task belongs to it.
2. **At the end of a block of work** (a design, an analysis, a prototype): look at what comes next **in this thread**. If it
   changes type → line «🔵 Model: <active> · next: <type> → better <X>». If what follows goes in another thread, there is
   no line: the model goes in the prompt or in the task (point 4).
3. **If a switch is needed:** STOP, ask for `/model` and wait for confirmation. Do not go on "just a bit more" with the
   wrong model.
4. **When writing a prompt to resume in another thread:** the first line is «Model to start: X», and if the task has phases
   of a different type, mark «→ switch to Y here» at the right step.
5. **Switching models = `/clear`.** The cache is per model: when switching, note the state outside the chat, `/clear`, `/model`
   and resume from what was noted, instead of dragging the whole context into the new model.

Without a transition the line is not written: the marker is only for changes in the type of work.
There is no "session close": leaving the state noted is part of the work and does not call for a model switch.
Not every thread needs all three models.
~~~~
