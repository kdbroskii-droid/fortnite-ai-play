"""Generic non-weapon item classifier for screen/OCR input.

Observation only: this module classifies text and does not control keyboard,
mouse, aiming, firing, or any game input.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "healing_item": [
        "med kit", "medkit", "bandage", "med mist", "med mist",
        "slurp", "flopper", "fish",
    ],
    "shield_item": [
        "shield potion", "small shield potion", "big shield potion",
        "mini shield", "mini shields", "minis", "shield keg",
        "shield", "flowberry",
    ],
    "mobility_item": [
        "shockwave", "impulse", "grappler", "launch pad",
        "crash pad", "rift",
    ],
    "vehicle": [
        "car", "truck", "boat", "bus", "quad", "motorcycle", "bike",
    ],
    "material": ["wood", "brick", "stone", "metal"],
    "objective_item": ["key", "capture point", "quest", "medallion"],
    "consumable": ["apple", "mushroom", "corn", "coconut"],
    "device": ["campfire", "bouncer"],
}

COMPILED_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    (category, re.compile(rf"\b{re.escape(keyword)}\b"))
    for category, keywords in CATEGORY_KEYWORDS.items()
    for keyword in keywords
]

OCR_TYPOS = str.maketrans({
    "0": "o",
    "1": "i",
    "5": "s",
})


def normalize_name(name: str) -> str:
    normalized = str(name).casefold().translate(OCR_TYPOS)
    normalized = re.sub(r"[^\w\s-]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def classify_non_weapon(name: str) -> dict:
    normalized = normalize_name(name)
    result = {
        "name": name,
        "normalized_name": normalized,
        "category": "unknown",
    }

    for category in CATEGORY_KEYWORDS:
        result[category] = False

    for category, pattern in COMPILED_PATTERNS:
        if pattern.search(normalized):
            result["category"] = category
            result[category] = True
            break

    return result


# Backwards-compatible name used by earlier code.
def classify_item(name: str) -> dict:
    return classify_non_weapon(name)


def add_item(category: str, item_name: str) -> None:
    if category not in CATEGORY_KEYWORDS:
        CATEGORY_KEYWORDS[category] = []

    item_name = item_name.casefold().strip()
    if not item_name or item_name in CATEGORY_KEYWORDS[category]:
        return

    CATEGORY_KEYWORDS[category].append(item_name)
    COMPILED_PATTERNS.append(
        (category, re.compile(rf"\b{re.escape(item_name)}\b"))
    )


def add_keyword(category: str, keyword: str) -> None:
    add_item(category, keyword)
