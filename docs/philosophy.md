# Philosophy

## Where this comes from

Every new project started the same way: asking Claude Code to set up, once again, the documentation that saves tokens, the
hooks, the rule about which model does what. Whatever was learned in one project stayed in that project, and the way of
working drifted apart between projects and machines.

Claude Code plugins and marketplaces already solve the mechanics of sharing that: one git repository holds the marketplace
and the plugins, and any machine can add it. What this repository adds is a set of rules about **how** those plugins behave.
They are below, followed by the reason each plugin exists.

## Principles

### 1. Propose, don't install

A hook runs code on every message, and an MCP server runs with your permissions. Installing one is a decision about your
machine, so it is yours to make.

- `catalog` diagnoses and **proposes**: what it would install, why, and the fact sheet of each plugin. It installs only what you
  say yes to, and never from third-party marketplaces.
- Versions are pinned in each `plugin.json`, so a new commit does not reach you until the version changes. Automatic updates
  stay off; `catalog` tells you when there is something new and shows the changelog.
- Every plugin README opens with the same fact sheet (what runs, what it reads and writes, context cost, how to turn it off),
  so the decision can be made without reading the code. You can still read it: nothing is minified or downloaded at runtime.

### 2. Mechanical work without AI

An earlier attempt at automating session wrap-ups used the model to decide when to close and how to document. It spent tokens
on bookkeeping and still needed supervision. The lesson: anything that can be done by a script should be.

- The hooks in this repository are plain bash or Python. None of them calls a model or the network.
- `continuum` writes its log line and its commit from the transcript, with code. Claude only writes what needs judgment: a note
  when something is decided.
- When the code produces text on its own (log lines, commit messages, index headers) it uses a small table of labels per
  language, not a model.

### 3. Rules live in code, not in prose

A rule written in `CLAUDE.md` is read once and then competes with everything else in the context. A rule that must always hold
belongs where it cannot be forgotten:

- The model split is re-injected on every message by a hook, not left in `CLAUDE.md` alone.
- `continuum`'s server enforces what the model must not do: nothing outside the vault, only `.md` files, append-only. The format
  of a note is set by the code, not by the prompt.
- Your git identity is set in git's config, which git and the hooks read without AI. A line in `CLAUDE.md` saying who the author
  is would go stale without warning; `git-identity` checks the config instead.

### 4. Spend context where it pays

Before building `continuum`, 85 real sessions of a large project were measured:

- The median context at the first turn was ~56k tokens; 67 of the 85 sessions went past 120k.
- 83 % of all the context processed happened in turns above 120k tokens. Long threads are where the cost is.
- Reading status documents at the start cost a median of ~8k tokens per session: real, but small next to the above.

A follow-up experiment ran the same task three ways. A subagent with a trimmed context (no `CLAUDE.md`, only the tools it
needs) started with ~29k fewer tokens than a regular one; a regular subagent could cost **more** than doing the work in the main
thread. So the levers, in order:

1. **Short threads per task.** Note what matters, `/clear`, resume from the note.
2. **Trimmed subagents** for heavy reading and repetitive tests, returning a fixed short format.
3. **Few tools.** Each MCP tool's definition is paid by every agent; `continuum` has four.

Indexes and routers help a little. They are not the main saving, and the docs here do not pretend they are.

### 5. Never overwrite what is yours

- Anything a plugin writes into one of your files (`CLAUDE.md`, `.gitignore`, `.claude/settings.json`) goes between markers
  named `claude-workbench:<plugin>`, after a diff you approve. Text outside the markers is never touched.
- `continuum` only appends to the vault. Deleting or rewriting is something you do, in Obsidian or by hand.
- Uninstalling a plugin leaves your data in place. Each README says which block to delete if you want it gone.

### 6. Privacy is a barrier, not a habit

Things leak by accident: a server name in a changelog, a private e-mail in a commit, notes pushed with the code.

- The vault is a **sibling** repository of the project (`<project>-memory`), never a subfolder: a `git add .` in the project
  cannot pick it up, and it is never pushed by the plugin.
- `git-identity` blocks commits and pushes signed with an e-mail you listed. The list lives on your machine, not in any project.
- This repository guards itself with `tools/barrier/`: git hooks that reject a commit or a push containing any term from a list
  kept outside version control (the list is itself private data). gitleaks runs in CI on top of it.

### 7. Your language

Plugins talk to you, and write for you, in your language. What the code depends on does not change with it:

- **Fixed in English:** folder names, task states, frontmatter keys, tool names, markers. If they followed the language, a vault
  would break when another person opened it.
- **In your language:** what Claude says and writes, and what the code writes on its own when there is a label table for that
  language (today `en` and `es`; others fall back to English, and adding one is a small pull request).

### 8. Honest about where it was tested

Each README says on which platforms a plugin actually ran. "Linux not yet verified" stays there until the CI matrix passes.

## Why each plugin exists

### `catalog`

A collection only helps if it reaches the projects. Without a catalog, every new project means remembering which plugins exist,
which version is current and which install skill is still missing. `catalog` turns that into one question, and it is a skill
rather than a hook on purpose: a session-start hook would cost context in every session, while a skill's description is already
loaded and only acts when asked.

### `model-protocol`

Opus is for thinking: design, choices between alternatives, debugging that is not obvious. Sonnet is for mechanical work that
needs judgment; Haiku for simple mechanical work. Spending Opus on a routine commit wastes money, and forcing Sonnet through a
design decision wastes the decision. A rule in `CLAUDE.md` was not enough, so a hook recalls it on every message (~200 tokens)
and asks Claude to say when the work ahead belongs to another model and stop until you switch. Switching is also a good moment
for `/clear`, since the cache is per model.

### `git-identity`

Many people use a private e-mail as their global git identity and then push to a public host; once a commit is out, the e-mail
is in the history. The plugin is **optional and neutral**: it protects only the e-mails *you* list, with no assumption about
which one is private or which host you use. It covers what happens inside Claude Code; for the rest, hosts like GitHub offer
their own last barrier, and the README says where.

### `continuum`

Working in "sessions" meant closing a tab by hand at some context size, writing status files so the next session could pick up.
The thresholds were rules without data, and the wrap-up itself cost tokens. `continuum` removes the session as the unit of work:

- The unit is the **task**. You resume "continue with [[task]]", not "the previous session".
- State lives outside the chat, in an Obsidian vault that is just a folder of `.md` files (Obsidian is only your view of it; it
  does not need to be open).
- Notes are written when something is decided, not at the end. Retrieval is by query (`search`, then `read` one note), never by
  reading everything.
- A hook records each turn's work and commits the vault, so the memory has history, including your own edits in Obsidian.

Generic memory servers already exist. The ones reviewed had twenty or more tools, some overwrote notes without detecting
conflicts (a problem with several subagents in parallel), and some compressed memory with a model in the background, spending
tokens. `continuum` is small on purpose: four tools, standard-library Python, nothing to install.
