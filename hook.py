"""Hermes `transform_terminal_output` hook: pipe shell output through rtk."""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional

try:
    from .filter_map import derive_filter_name
except ImportError:  # standalone import (pytest, REPL) — package context absent
    from filter_map import derive_filter_name  # type: ignore[no-redef]


_RTK_TIMEOUT_SECS = 5


def transform_terminal_output(
    command: str,
    output: str,
    **_unused: object,
) -> Optional[str]:
    """Hermes hook callback. Returns filtered output, or None to keep original.

    Fail-open: any error path (rtk missing, timeout, non-zero exit, empty
    stdout, unexpected exception) returns None so the model still sees the
    original output rather than a broken result.
    """
    if not command or not output or not output.strip():
        return None

    filter_name = derive_filter_name(command)
    if filter_name is None:
        return None

    if shutil.which("rtk") is None:
        return None

    try:
        proc = subprocess.run(
            ["rtk", "pipe", "-f", filter_name],
            input=output,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_RTK_TIMEOUT_SECS,
        )
    except Exception:
        return None

    if proc.returncode != 0 or not proc.stdout:
        return None

    return proc.stdout
