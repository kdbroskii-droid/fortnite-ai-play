"""Generic non-weapon item name classifier.

This module is data-driven and safe for OCR text classification. It does not
contain weapon-specific categories.
"""

from __future__ import annotations

import re
from typing import Dict, List


NON_WEAPON_CATEGORIES: Dict[str, List[str]] = {
    "healing_item": ["med kit", "medkit", "bandage", "med mist"],
    "shield_item": ["shield potion", "small shield potion", "shield keg", "slurp juice"],
    "mobility_item": ["shockwave grenade", "impulse", "grappler", "launch pad"],
    "vehicle": ["car", "truck", "boat", "bus", "quad", "motorcycle"],
    "material": ["wood", "brick", "stone", "metal"],
    "objective_item": ["key", "capture point", "quest item"],
    "consumable": ["apple", "mushroom", "corn", "coconut"],
    "device": ["campfire", "launch pad", "bouncer"],
}

_COMPILED_PATTERNS = [
    (category, re.compile(rf"\b{re.escape(item_name.casefold().strip())}\b"))
    for category, names in NON_WEAPON_CATEGORIES.items()
    for item_name in names
]


def normalize_name(name: str) -> str:
    """Normalize OCR text before matching."""
    normalized = name.casefold()
    normalized = re.sub(r"[^\w\s-]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def classify_non_weapon(name: str) -> dict:
    """Return the first matching non-weapon category and boolean flags."""
    normalized = normalize_name(name)

    result = {
        "name": name,
        "normalized_name": normalized,
        "category": "unknown",
    }

    for category in NON_WEAPON_CATEGORIES:
        result[category] = False

    for category, pattern in _COMPILED_PATTERNS:
        if pattern.search(normalized):
            result["category"] = category
            result[category] = True
            return result

    return result


def add_item(category: str, item_name: str) -> None:
    """Add a non-weapon item and compile its pattern immediately."""
    if category not in NON_WEAPON_CATEGORIES:
        NON_WEAPON_CATEGORIES[category] = []

    item_name = item_name.casefold().strip()
    if not item_name or item_name in NON_WEAPON_CATEGORIES[category]:
        return

    NON_WEAPON_CATEGORIES[category].append(item_name)
    _COMPILED_PATTERNS.append(
        (category, re.compile(rf"\b{re.escape(item_name)}\b"))
    )
