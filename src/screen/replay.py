"""Replay recorded observations without connecting to a live game."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterator
from .recorder import ScreenState


def save_states(states: list[ScreenState], path: str | Path) -> None:
    Path(path).write_text(json.dumps([s.to_dict() for s in states], indent=2), encoding="utf-8")


def load_states(path: str | Path) -> list[ScreenState]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ScreenState(**item) for item in data]


def replay(path: str | Path) -> Iterator[ScreenState]:
    yield from load_states(path)
