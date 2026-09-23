"""Validator for the repository's generic macro format."""

from dataclasses import dataclass
from .action_model import Action

@dataclass(frozen=True)
class ValidationLimits:
    max_actions: int = 10000
    max_delay_ms: int = 60000
    max_move_pixels: int = 5000

def validate_actions(actions: list[Action], limits: ValidationLimits = ValidationLimits()) -> None:
    if len(actions) > limits.max_actions:
        raise ValueError("Macro exceeds maximum action count")
    for action in actions:
        action.validate()
        if action.type == "delay" and float(action.value or 0) > limits.max_delay_ms:
            raise ValueError("Delay exceeds safety limit")
        if action.type == "mouse_move":
            if abs(action.x or 0) > limits.max_move_pixels or abs(action.y or 0) > limits.max_move_pixels:
                raise ValueError("Mouse movement exceeds safety limit")
