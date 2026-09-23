"""Safe aim-decision simulator.

This module models target selection probabilities without moving a cursor,
sending input, or firing in a game.
"""

from dataclasses import dataclass
import random
from typing import Literal

AimResult = Literal["miss", "torso", "head"]

@dataclass(frozen=True)
class AimConfig:
    miss_percent: float = 3.0
    torso_percent: float = 67.0
    head_percent: float = 30.0

    def validate(self) -> None:
        total = self.miss_percent + self.torso_percent + self.head_percent
        if abs(total - 100.0) > 1e-9:
            raise ValueError(f"Probabilities must total 100%, got {total}%")
        if min(self.miss_percent, self.torso_percent, self.head_percent) < 0:
            raise ValueError("Probabilities cannot be negative")

def simulate_shot(config: AimConfig = AimConfig(), rng: random.Random | None = None) -> AimResult:
    config.validate()
    rng = rng or random
    roll = rng.random() * 100.0
    if roll < config.miss_percent:
        return "miss"
    if roll < config.miss_percent + config.torso_percent:
        return "torso"
    return "head"

def simulate_magazine(size: int, config: AimConfig = AimConfig(), seed: int | None = None) -> list[AimResult]:
    if size < 1:
        raise ValueError("Magazine size must be at least 1")
    rng = random.Random(seed)
    return [simulate_shot(config, rng) for _ in range(size)]
