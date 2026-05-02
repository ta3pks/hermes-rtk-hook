"""Map a shell command line to the matching `rtk pipe -f <name>` filter.

The filter set mirrors `rtk pipe`'s `resolve_filter` table (rtk-ai/rtk
src/cmds/system/pipe_cmd.rs:6). When rtk adds new filters, add the
corresponding command mapping here and a snapshot test in
tests/test_filter_map.py.
"""

from __future__ import annotations

import re
import shlex
from typing import Optional


_SINGLE = {
    "pytest": "pytest",
    "grep": "grep",
    "rg": "rg",
    "find": "find",
    "fd": "fd",
    "tsc": "tsc",
    "vitest": "vitest",
    "mypy": "mypy",
    "prettier": "prettier",
}

_PAIR = {
    ("git", "status"): "git-status",
    ("git", "log"): "git-log",
    ("git", "diff"): "git-diff",
    ("cargo", "test"): "cargo-test",
    ("go", "test"): "go-test",
    ("go", "build"): "go-build",
    ("ruff", "check"): "ruff-check",
    ("ruff", "format"): "ruff-format",
}

_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def derive_filter_name(command: str) -> Optional[str]:
    """Return the rtk pipe filter name for `command`, or None if unmapped.

    Strips leading shell env-var assignments (e.g. `FOO=bar pytest` → `pytest`).
    Returns None for empty input, env-only input, or shlex parse failures
    (unclosed quotes etc.).
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None

    while tokens and _ENV_ASSIGN_RE.match(tokens[0]):
        tokens = tokens[1:]

    if not tokens:
        return None

    head = tokens[0]
    if len(tokens) >= 2:
        mapped = _PAIR.get((head, tokens[1]))
        if mapped is not None:
            return mapped
    return _SINGLE.get(head)
