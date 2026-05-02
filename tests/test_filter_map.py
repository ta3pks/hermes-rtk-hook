"""Tests for the command → rtk filter-name mapping."""

from filter_map import derive_filter_name


class TestSingleWordCommands:
    def test_pytest(self):
        assert derive_filter_name("pytest") == "pytest"

    def test_pytest_with_args(self):
        assert derive_filter_name("pytest tests/ -v") == "pytest"

    def test_grep(self):
        assert derive_filter_name("grep -rn 'foo' src/") == "grep"

    def test_rg(self):
        assert derive_filter_name("rg --type=py 'foo'") == "rg"

    def test_find(self):
        assert derive_filter_name("find . -name '*.py'") == "find"

    def test_fd(self):
        assert derive_filter_name("fd '*.rs'") == "fd"

    def test_tsc(self):
        assert derive_filter_name("tsc --noEmit") == "tsc"

    def test_vitest(self):
        assert derive_filter_name("vitest run") == "vitest"

    def test_mypy(self):
        assert derive_filter_name("mypy src/") == "mypy"

    def test_prettier(self):
        assert derive_filter_name("prettier --check .") == "prettier"


class TestTwoWordCommands:
    def test_git_status(self):
        assert derive_filter_name("git status") == "git-status"

    def test_git_status_porcelain(self):
        assert derive_filter_name("git status --porcelain") == "git-status"

    def test_git_log(self):
        assert derive_filter_name("git log --oneline -20") == "git-log"

    def test_git_diff(self):
        assert derive_filter_name("git diff HEAD~3") == "git-diff"

    def test_cargo_test(self):
        assert derive_filter_name("cargo test --release") == "cargo-test"

    def test_go_test(self):
        assert derive_filter_name("go test ./...") == "go-test"

    def test_go_build(self):
        assert derive_filter_name("go build ./cmd/server") == "go-build"

    def test_ruff_check(self):
        assert derive_filter_name("ruff check src/") == "ruff-check"

    def test_ruff_format(self):
        assert derive_filter_name("ruff format --check .") == "ruff-format"


class TestNoMatch:
    def test_empty(self):
        assert derive_filter_name("") is None

    def test_whitespace_only(self):
        assert derive_filter_name("   ") is None

    def test_unknown_single(self):
        assert derive_filter_name("echo hello") is None

    def test_unknown_two_word(self):
        assert derive_filter_name("git push") is None

    def test_git_alone(self):
        # git on its own (no subcommand) → no filter
        assert derive_filter_name("git") is None

    def test_cargo_alone(self):
        # cargo without `test` subcommand → no filter
        assert derive_filter_name("cargo build") is None


class TestEdgeCases:
    def test_leading_whitespace(self):
        assert derive_filter_name("  pytest tests/") == "pytest"

    def test_command_with_env_prefix(self):
        # `FOO=bar pytest` — the env-var prefix precedes the command
        assert derive_filter_name("FOO=bar pytest") == "pytest"

    def test_unparseable_quoting(self):
        # Malformed quoting should fail gracefully (return None, not raise)
        assert derive_filter_name("pytest 'unclosed") is None

    def test_command_via_env_only(self):
        # All-env-vars, no command → None
        assert derive_filter_name("FOO=bar BAZ=qux") is None
