"""Tests for the transform_terminal_output hook callback."""

from __future__ import annotations

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from hook import transform_terminal_output


@pytest.fixture
def mock_rtk_on_path():
    with patch("hook.shutil.which", return_value="/usr/local/bin/rtk"):
        yield


@pytest.fixture
def mock_rtk_missing():
    with patch("hook.shutil.which", return_value=None):
        yield


class TestEarlyReturns:
    def test_empty_output(self, mock_rtk_on_path):
        assert transform_terminal_output(command="git status", output="") is None

    def test_whitespace_only_output(self, mock_rtk_on_path):
        assert transform_terminal_output(command="git status", output="   \n  ") is None

    def test_empty_command(self, mock_rtk_on_path):
        assert transform_terminal_output(command="", output="some output") is None

    def test_unknown_command(self, mock_rtk_on_path):
        # `echo hello` is not in the filter map
        assert transform_terminal_output(command="echo hello", output="hello") is None

    def test_rtk_not_on_path(self, mock_rtk_missing):
        assert transform_terminal_output(command="pytest", output="some pytest output") is None


class TestFilteringHappyPath:
    def test_returns_filtered_output(self, mock_rtk_on_path):
        with patch("hook.subprocess.run") as run:
            run.return_value = MagicMock(returncode=0, stdout="filtered\n", stderr="")
            result = transform_terminal_output(
                command="git status", output="raw_output"
            )
            assert result == "filtered\n"
            args, kwargs = run.call_args
            assert args[0] == ["rtk", "pipe", "-f", "git-status"]
            assert kwargs["input"] == "raw_output"
            assert kwargs["timeout"] == 5
            assert kwargs["text"] is True

    def test_two_word_command(self, mock_rtk_on_path):
        with patch("hook.subprocess.run") as run:
            run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
            transform_terminal_output(command="cargo test --release", output="raw")
            args, _ = run.call_args
            assert args[0] == ["rtk", "pipe", "-f", "cargo-test"]


class TestFailOpen:
    def test_rtk_nonzero_exit(self, mock_rtk_on_path):
        with patch("hook.subprocess.run") as run:
            run.return_value = MagicMock(returncode=1, stdout="", stderr="bad")
            assert transform_terminal_output(command="git status", output="raw") is None

    def test_rtk_returns_empty_stdout(self, mock_rtk_on_path):
        with patch("hook.subprocess.run") as run:
            run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            assert transform_terminal_output(command="git status", output="raw") is None

    def test_rtk_timeout(self, mock_rtk_on_path):
        with patch("hook.subprocess.run", side_effect=subprocess.TimeoutExpired("rtk", 5)):
            assert transform_terminal_output(command="git status", output="raw") is None

    def test_rtk_file_not_found(self, mock_rtk_on_path):
        with patch("hook.subprocess.run", side_effect=FileNotFoundError):
            assert transform_terminal_output(command="git status", output="raw") is None

    def test_rtk_os_error(self, mock_rtk_on_path):
        with patch("hook.subprocess.run", side_effect=OSError("EACCES")):
            assert transform_terminal_output(command="git status", output="raw") is None

    def test_unexpected_exception(self, mock_rtk_on_path):
        # Any other exception should fail-open, not propagate
        with patch("hook.subprocess.run", side_effect=RuntimeError("kaboom")):
            assert transform_terminal_output(command="git status", output="raw") is None


class TestExtraKwargsAccepted:
    """The hook receives extra kwargs (returncode, task_id, env_type) — must accept silently."""

    def test_accepts_extra_kwargs(self, mock_rtk_on_path):
        with patch("hook.subprocess.run") as run:
            run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
            result = transform_terminal_output(
                command="git status",
                output="raw",
                returncode=0,
                task_id="task-123",
                env_type="local",
            )
            assert result == "ok\n"
