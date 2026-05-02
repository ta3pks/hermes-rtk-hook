"""hermes-rtk-hook plugin entry point.

Hermes Agent calls `register(ctx)` after loading `plugin.yaml`. We register a
single `transform_terminal_output` callback that pipes shell tool output
through `rtk pipe -f <filter>` for token-efficient filtering.
"""

from __future__ import annotations

try:
    from .hook import transform_terminal_output
except ImportError:  # standalone import (pytest, REPL) — package context absent
    from hook import transform_terminal_output  # type: ignore[no-redef]


def register(ctx) -> None:
    ctx.register_hook("transform_terminal_output", transform_terminal_output)
