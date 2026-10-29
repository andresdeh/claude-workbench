# Contributing

This is a personal collection, public so others can use it and learn from it. For now only the owner edits `main`.

## Issues

Welcome: bugs, a platform where something fails (say which OS, shell and Claude Code version), and ideas. For a bug, include
the plugin and its version (`claude plugin list`) and what you expected. Security problems go through [`SECURITY.md`](SECURITY.md),
not an issue.

## Pull requests

Please **open an issue first** and wait for a reply: a plugin here is code that runs on other people's machines, so what goes
in is decided before it is written. Good candidates: a fix, a label table for another language (`plugins/continuum/vault.py`),
a platform fix (macOS, Linux), a clearer README.

Before you open one:

1. `claude plugin validate . --strict` passes at the root and in the plugin you touched.
2. The tests pass: `python -I tools/tests/<plugin>.py <path>` (see the plugin's README) ends with `FAILURES: 0`.
3. A change that must reach users bumps the version in that plugin's `plugin.json` (only there, not in `marketplace.json`) and
   adds an entry to its `CHANGELOG.md`.
4. Hooks use the *shell* form with `"shell": "bash"` and `"${CLAUDE_PLUGIN_ROOT}"` in quotes; never `~` or absolute paths.
   Scripts are executable in git (`git update-index --chmod=+x`). Files use LF.
5. Anything a plugin writes into a user's file goes between `claude-workbench:<plugin>` markers, after a diff the user approves.
6. **No private data**: no company, server, domain, account or personal path, and no personal e-mail in commits. Enable the
   barrier with `tools/barrier/instalar.sh` and fill in your own list in `.git/info/forbidden-terms.txt`. The branch of a pull
   request is public even if it is never merged, so clean **before** you push.
7. Text for users is in English; what a plugin shows or writes while in use follows the user's language (see
   [`docs/philosophy.md`](docs/philosophy.md), principle 7).

Commits: a short imperative subject (`feat:`, `fix:`, `docs:`, `chore:`).

## License

By contributing you agree your work is released under the [Apache License 2.0](LICENSE).
