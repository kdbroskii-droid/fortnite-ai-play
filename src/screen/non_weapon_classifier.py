"""Generic non-weapon item name classifier.

This module is intentionally data-driven: add or remove non-weapon names
from the category lists without changing the matching logic.
"""

from __future__ import annotations

import re
from typing import Dict, List


NON_WEAPON_CATEGORIES: Dict[str, List[str]] = {
    "healing_item": [
        "med kit",
        "medkit",
        "bandage",
        "med mist",
    ],
    "shield_item": [
        "shield potion",
        "small shield potion",
        "shield keg",
        "slurp juice",
    ],
    "mobility_item": [
        "shockwave grenade",
        "impulse grenade",
        "grappler",
        "launch pad",
    ],
    "vehicle": [
        "car",
        "truck",
        "boat",
        "bus",
        "quad",
        "motorcycle",
    ],
    "material": [
        "wood",
        "brick",
        "stone",
        "metal",
    ],
    "objective_item": [
        "key",
        "capture point",
        "quest item",
    ],
    "consumable": [
        "apple",
        "mushroom",
        "corn",
        "coconut",
    ],
    "device": [
        "campfire",
        "launch pad",
        "bouncer",
    ],
}


def normalize_name(name: str) -> str:
    """Normalize OCR text before matching."""
    return re.sub(r"\\s+", " ", name.casefold().strip())


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

    for category, names in NON_WEAPON_CATEGORIES.items():
        for item_name in names:
            if re.search(rf"\\b{re.escape(normalize_name(item_name))}\\b", normalized):
                result["category"] = category
                result[category] = True
                return result

    return result


def add_item(category: str, item_name: str) -> None:
    """Add a non-weapon item to a category at runtime."""
    if category not in NON_WEAPON_CATEGORIES:
        NON_WEAPON_CATEGORIES[category] = []

    item_name = item_name.strip()
    if item_name and item_name not in NON_WEAPON_CATEGORIES[category]:
        NON_WEAPON_CATEGORIES[category].append(item_name)
