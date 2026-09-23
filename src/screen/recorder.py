"""Screen recording and HUD-state perception.

The recorder is deliberately observation-only. It captures frames and stores
structured HUD information, but does not move the mouse, press keys, fire,
or turn visual detections into targeting commands.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from time import monotonic
from typing import Any, Iterable, Optional
import json


@dataclass
class ScreenState:
    """Structured state that can be populated from a captured frame."""

    frame_number: int = 0
    timestamp: float = 0.0

    # HUD/game-state observations.
    players_visible: int = 0
    crosshair_center_x: Optional[float] = None
    crosshair_center_y: Optional[float] = None
    crosshair_spread: Optional[float] = None
    bullet_drop_indicator: Optional[float] = None

    current_weapon: Optional[str] = None
    weapon_slots: list[str] = field(default_factory=list)
    ammo_reserve: Optional[int] = None
    ammo_in_magazine: Optional[int] = None

    wood: Optional[int] = None
    brick: Optional[int] = None
    metal: Optional[int] = None

    health: Optional[int] = None
    shield: Optional[int] = None
    sprinting: Optional[bool] = None
    build_mode: Optional[bool] = None
    editing: Optional[bool] = None
    reloading: Optional[bool] = None
    interaction_prompt: Optional[str] = None

    storm_phase: Optional[int] = None
    storm_time_remaining: Optional[float] = None
    match_time: Optional[float] = None
    eliminations: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FrameRecorder:
    """Collect frames supplied by an external capture source.

    This class intentionally does not implement game input or targeting.
    A frame may be any image-like object supported by the caller.
    """

    def __init__(self, sample_interval: float = 0.0) -> None:
        if sample_interval < 0:
            raise ValueError("sample_interval must be >= 0")
        self.sample_interval = sample_interval
        self.frames: list[Any] = []
        self.states: list[ScreenState] = []
        self._last_sample = 0.0
        self._frame_number = 0

    def should_sample(self, now: Optional[float] = None) -> bool:
        now = monotonic() if now is None else now
        return self.sample_interval == 0 or now - self._last_sample >= self.sample_interval

    def add_frame(self, frame: Any, state: Optional[ScreenState] = None,
                  now: Optional[float] = None) -> Optional[ScreenState]:
        """Store one frame and its observation state."""
        now = monotonic() if now is None else now
        if not self.should_sample(now):
            return None

        self._frame_number += 1
        self._last_sample = now
        self.frames.append(frame)

        if state is None:
            state = ScreenState(frame_number=self._frame_number, timestamp=now)
        else:
            state.frame_number = self._frame_number
            state.timestamp = now

        self.states.append(state)
        return state

    def latest_state(self) -> Optional[ScreenState]:
        return self.states[-1] if self.states else None

    def export_states(self, path: str | Path) -> None:
        """Write observed state as JSON without writing image data."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([state.to_dict() for state in self.states], indent=2),
            encoding="utf-8",
        )


class HudPerception:
    """Adapter for a future computer-vision/OCR implementation.

    `observe()` accepts already-detected values and normalizes them into a
    ScreenState. It intentionally has no player-target selection or input
    output functionality.
    """

    def observe(self, frame: Any, **observations: Any) -> ScreenState:
        allowed = set(ScreenState.__dataclass_fields__)
        clean = {key: value for key, value in observations.items() if key in allowed}
        return ScreenState(**clean)


def state_from_mapping(mapping: dict[str, Any]) -> ScreenState:
    """Create a ScreenState from a detector/OCR result mapping."""
    allowed = set(ScreenState.__dataclass_fields__)
    return ScreenState(**{k: v for k, v in mapping.items() if k in allowed})
