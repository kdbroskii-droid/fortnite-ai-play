"""Conservative OCR-to-HUD parser."""
from __future__ import annotations
import re
from typing import Any
from .perception import TextDetection


class HudParser:
    def __init__(self) -> None:
        self.number = re.compile(r"(?<!\d)(\d{1,5})(?!\d)")

    def _numbers(self, text: str) -> list[int]:
        return [int(x) for x in self.number.findall(text)]

    def parse(self, detections: list[TextDetection]) -> dict[str, Any]:
        out: dict[str, Any] = {"weapon_slots": []}
        for d in detections:
            t = d.text.strip()
            low = t.lower()
            nums = self._numbers(t)
            if any(k in low for k in ("wood", "brick", "metal")) and nums:
                value = nums[-1]
                if "wood" in low: out["wood"] = value
                if "brick" in low: out["brick"] = value
                if "metal" in low: out["metal"] = value
            elif "shield" in low and nums:
                out["shield"] = nums[-1]
            elif "health" in low and nums:
                out["health"] = nums[-1]
            elif "ammo" in low or "reload" in low:
                if len(nums) >= 2:
                    out["ammo_in_magazine"], out["ammo_reserve"] = nums[-2], nums[-1]
                elif nums:
                    out["ammo_in_magazine"] = nums[-1]
            elif "storm" in low and nums:
                out["storm_time_remaining"] = float(nums[-1])
            elif "elimination" in low or "elim" in low:
                if nums: out["eliminations"] = nums[-1]
            elif t and len(t) <= 40 and not nums and self._looks_like_weapon(t):
                out["current_weapon"] = t
        return out

    @staticmethod
    def _looks_like_weapon(text: str) -> bool:
        words = text.lower().split()
        hints = {"rifle", "shotgun", "smg", "pistol", "sniper", "launcher", "bow", "blade"}
        return any(w.strip(".,:;()[]") in hints for w in words)
