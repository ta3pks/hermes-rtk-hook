# hermes-rtk-hook

> Hermes Agent plugin that transparently wraps shell tool calls with [`rtk`](https://github.com/ta3pks/rtk) for substantial token savings on dev operations.

**Status:** Work in progress — not yet functional.

## What it does

Most shell tool calls an LLM makes (`git status`, `npm install`, `cargo test`, …) emit far more output than the model needs. `rtk` is a transparent CLI proxy that filters that output to the relevant signal, typically saving 60–90% of the response tokens.

This plugin registers a `pre_tool_call` hook on Hermes Agent so every Bash invocation is automatically rewritten to `rtk <command>`, with sensible skip rules (meta commands, already-prefixed calls, `rtk` not on `$PATH`).

No model behaviour change is required — the plugin is invisible to the agent.

## Requirements

- [hermes-agent](https://hermes-agent.nousresearch.com/)
- [`rtk`](https://github.com/ta3pks/rtk) on `$PATH`

## Installation

> TBD once initial scaffold lands.

## Configuration

> TBD.

## Development

```sh
git clone git@github.com:ta3pks/hermes-rtk-hook.git
cd hermes-rtk-hook
# dev instructions to come once the plugin shape is locked
```

## License

MIT — see [LICENSE](./LICENSE).
