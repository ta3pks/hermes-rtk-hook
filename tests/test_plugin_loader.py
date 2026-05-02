"""Verify the plugin loads correctly when imported the way Hermes loads it.

Hermes uses ``importlib.util.spec_from_file_location`` with
``submodule_search_locations`` to load plugin dirs as packages
(see ``~/.hermes/hermes-agent/hermes_cli/plugins.py:1018``). This test mirrors
that path so any future regression in our import shape — e.g. accidentally
breaking relative imports — fails CI rather than silently bricking the plugin
in production.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


_PLUGIN_DIR = Path(__file__).resolve().parent.parent
_NS_PARENT = "hermes_plugins"
_MODULE_NAME = f"{_NS_PARENT}.hermes_rtk_hook"


def _load_plugin_as_hermes_does():
    if _NS_PARENT not in sys.modules:
        ns = types.ModuleType(_NS_PARENT)
        ns.__path__ = []  # type: ignore[attr-defined]
        ns.__package__ = _NS_PARENT
        sys.modules[_NS_PARENT] = ns

    spec = importlib.util.spec_from_file_location(
        _MODULE_NAME,
        _PLUGIN_DIR / "__init__.py",
        submodule_search_locations=[str(_PLUGIN_DIR)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    module.__package__ = _MODULE_NAME
    module.__path__ = [str(_PLUGIN_DIR)]  # type: ignore[attr-defined]
    sys.modules[_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


class _FakeCtx:
    def __init__(self) -> None:
        self.hooks: dict[str, object] = {}

    def register_hook(self, name: str, callback: object) -> None:
        self.hooks[name] = callback


def test_plugin_loads_under_hermes_loader():
    module = _load_plugin_as_hermes_does()
    assert callable(module.register)
    assert callable(module.transform_terminal_output)


def test_register_wires_transform_terminal_output_hook():
    module = _load_plugin_as_hermes_does()
    ctx = _FakeCtx()
    module.register(ctx)
    assert "transform_terminal_output" in ctx.hooks
    assert ctx.hooks["transform_terminal_output"] is module.transform_terminal_output
