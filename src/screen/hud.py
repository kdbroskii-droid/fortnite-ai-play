"""Conservative OCR-to-HUD parser."""
from __future__ import annotations
import re
from typing import Any
from .perception import TextDetection


class HudParser:
    WEAPON_TYPES = (
        "shotgun", "pistol", "rifle", "sniper rifle", "sniper", "dmr",
        "smg", "submachine gun", "launcher", "bow", "blade",
    )

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
            weapon = self.detect_weapon_type(t)
            if weapon:
                out["current_weapon"] = weapon
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
        return out

    @classmethod
    def detect_weapon_type(cls, text: str) -> str | None:
        """Return a normalized weapon category if OCR contains one."""
        low = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
        low = re.sub(r"\s+", " ", low).strip()
        for weapon in cls.WEAPON_TYPES:
            if re.search(r"\b" + re.escape(weapon) + r"\b", low):
                if weapon == "sniper":
                    return "sniper rifle"
                if weapon == "submachine gun":
                    return "smg"
                return weapon
        return None
