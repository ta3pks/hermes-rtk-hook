"""Integration tests: invoke the real `rtk` binary if it's on PATH.

Skipped when rtk is not installed so unit tests still pass on CI without rtk.
Catches silent breakage if rtk's CLI surface changes (e.g. `pipe -f` flag rename).
"""

from __future__ import annotations

import shutil

import pytest

from hook import transform_terminal_output


pytestmark = pytest.mark.skipif(
    shutil.which("rtk") is None,
    reason="rtk binary not on PATH",
)


def test_real_rtk_filters_git_status():
    raw = "M  README.md\nM  Cargo.toml\n?? new_file.rs\n"
    out = transform_terminal_output(command="git status --porcelain", output=raw)
    assert out is not None, "rtk pipe -f git-status should succeed on PATH"
    # rtk's git-status filter groups by section ("Modified", "Untracked", etc.)
    # We don't lock to exact format — only that something rtk-shaped came back.
    assert out != raw, "filter should transform the input"
    assert len(out) > 0


def test_real_rtk_filters_find():
    raw = "./src/main.rs\n./src/lib.rs\n./tests/foo.rs\n./Cargo.toml\n"
    out = transform_terminal_output(command="find . -name '*.rs'", output=raw)
    assert out is not None
    assert out != raw


def test_real_rtk_unmapped_command_returns_none():
    # `echo` is intentionally not in the filter map — should fail-open
    out = transform_terminal_output(command="echo hello", output="hello\n")
    assert out is None
