"""Game-independent action model.

Actions are data only. This layer deliberately has no OS input calls.
"""

from dataclasses import dataclass
from typing import Literal

ActionType = Literal[
    "key_down", "key_up", "mouse_move", "mouse_down",
    "mouse_up", "mouse_wheel", "delay"
]

@dataclass(frozen=True)
class Action:
    type: ActionType
    value: str | int | float | None = None
    x: int | None = None
    y: int | None = None
    duration_ms: int = 0

    def validate(self) -> None:
        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
        if self.type == "mouse_move" and (self.x is None or self.y is None):
            raise ValueError("mouse_move requires x and y")
