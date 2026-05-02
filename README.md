# hermes-rtk-hook

> Hermes Agent plugin that pipes shell tool output through [`rtk`](https://github.com/rtk-ai/rtk) for 60–90% token savings on dev operations.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

## What it does

Most shell tool calls a Hermes agent makes (`git status`, `cargo test`, `pytest`, `find`, …) emit far more output than the model needs. RTK is a CLI proxy that filters that noise to relevant signal. RTK already supports filter-only mode via `rtk pipe -f <filter>` (reads stdin, emits filtered stdout).

This plugin registers Hermes' `transform_terminal_output` hook and pipes raw shell output through `rtk pipe` whenever the command matches a known filter. Fail-open: if rtk is missing, the command isn't supported, or anything errors, the model sees the original output unchanged.

### Why output-side, not args-rewrite

RTK's other integrations (Claude Code, Cursor, Gemini CLI, Copilot) rewrite the *command* — `git status` → `rtk git status` — at the PreToolUse stage. Hermes' `pre_tool_call` hook is currently observe-or-block only (no rewrite action), so this plugin filters on the *output* side instead, after the command has run. Same token savings reach the model; slight loss is filtering happens after the original command's wall-clock cost.

If/when Hermes adds a `pre_tool_call` rewrite action, this plugin can pivot to the args-rewrite model and gain the small efficiency back.

## Requirements

- [Hermes Agent](https://hermes-agent.nousresearch.com/) ≥ 0.11 (needs the `transform_terminal_output` hook)
- [`rtk`](https://github.com/rtk-ai/rtk) on `$PATH`
- Python 3.10+

## Installation

```sh
# Clone into the Hermes plugin directory
git clone https://github.com/ta3pks/hermes-rtk-hook.git ~/.hermes/plugins/hermes-rtk-hook

# Enable the plugin in your Hermes config
hermes plugins enable hermes-rtk-hook

# Verify it loaded
hermes plugins list | grep hermes-rtk-hook
```

Or symlink from a development checkout:

```sh
git clone https://github.com/ta3pks/hermes-rtk-hook.git ~/projects/hermes-rtk-hook
ln -s ~/projects/hermes-rtk-hook ~/.hermes/plugins/hermes-rtk-hook
hermes plugins enable hermes-rtk-hook
```

## Configuration

The plugin reads no config of its own. It piggybacks on rtk's existing filter set — see `rtk help pipe` for the canonical list. To extend coverage, [add a filter to rtk upstream](https://github.com/rtk-ai/rtk) and a corresponding line in [`filter_map.py`](./filter_map.py).

Currently mapped commands → rtk filters:

| Command pattern | Filter |
|---|---|
| `pytest …` | `pytest` |
| `grep …` / `rg …` | `grep` / `rg` |
| `find …` / `fd …` | `find` / `fd` |
| `tsc …` | `tsc` |
| `vitest …` | `vitest` |
| `mypy …` | `mypy` |
| `prettier …` | `prettier` |
| `git status …` | `git-status` |
| `git log …` | `git-log` |
| `git diff …` | `git-diff` |
| `cargo test …` | `cargo-test` |
| `go test …` / `go build …` | `go-test` / `go-build` |
| `ruff check …` / `ruff format …` | `ruff-check` / `ruff-format` |

Anything not in this table is passed through unchanged.

## Development

```sh
git clone https://github.com/ta3pks/hermes-rtk-hook.git
cd hermes-rtk-hook
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```

The test suite includes:
- Unit tests for the command → filter-name mapping ([`tests/test_filter_map.py`](./tests/test_filter_map.py))
- Hook-callback tests with mocked subprocess ([`tests/test_hook.py`](./tests/test_hook.py))
- Integration tests that hit the real `rtk` binary if it's on `$PATH` ([`tests/test_integration.py`](./tests/test_integration.py))

## License

MIT — see [LICENSE](./LICENSE).
