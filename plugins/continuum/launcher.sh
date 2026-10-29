#!/bin/sh
# Continuum launcher: finds a working Python 3.8+ and passes it the arguments.
#
#   sh launcher.sh <script.py> [args...]
#
# Why it exists: on Windows `python3` is often the Microsoft Store shortcut (it runs nothing) and on
# Linux `python` may not exist. Every candidate is really tried, not just looked up in the PATH.
# To pick one by hand: the `python` plugin option (/config), or CONTINUUM_PYTHON=/path/to/python.
#
# The MCP is started with `git -c alias.continuum=!sh continuum launcher.sh ...` (see .mcp.json): git exists on
# Windows and Linux and brings its own sh; a bare `bash` on Windows may be WSL's.
# POSIX sh on purpose (on Linux, git's sh is dash).

probe='import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'

for py in "$CONTINUUM_PYTHON" "$CLAUDE_PLUGIN_OPTION_PYTHON" python3 python "py -3"; do
    [ -n "$py" ] || continue
    # $py unquoted: "py -3" is two words
    if $py -c "$probe" >/dev/null 2>&1; then
        exec $py "$@"
    fi
done

echo "continuum: no Python 3.8 or newer found (tried: python3, python, py -3; or set the python option / CONTINUUM_PYTHON)" >&2
exit 1
