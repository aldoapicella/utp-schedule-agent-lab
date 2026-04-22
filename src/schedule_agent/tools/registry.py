from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, tool: Callable[..., Any]) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> Callable[..., Any]:
        return self._tools[name]

    def list_names(self) -> list[str]:
        return sorted(self._tools)

