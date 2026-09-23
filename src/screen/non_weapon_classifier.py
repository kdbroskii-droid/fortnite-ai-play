"""Generic Fortnite item name classifier optimized for high-FPS OCR.

This module uses pre-compiled regex patterns for performance and includes
basic OCR artifact sanitization.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


# Dictionaries in Python preserve order. Categories at the top are checked first.
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    # --- Exceptions & Non-Weapons (Checked First) ---
    "mobility_item": ["shockwave", "impulse", "grappler", "launch pad", "crash pad", "rift"],
    "healing_item": ["med kit", "medkit", "bandage", "med mist", "chug", "flopper"],
    "shield_item": ["shield", "slurp", "keg", "flowberry"],
    "vehicle": ["car", "truck", "boat", "bus", "quad", "motorcycle", "bike"],
    "material": ["wood", "brick", "stone", "metal"],
    "objective_item": ["key", "capture point", "quest", "medallion"],
    "device": ["campfire", "bouncer"],
    
    # --- Melee & Traps ---
    "melee": ["pickaxe", "blade", "hammer", "chains of hades"],
    "trap": ["trap", "dynamo"],

    # --- Weapons (Checked Last for Catch-Alls) ---
    "shotgun": ["shotgun"],
    "smg": ["smg", "submachine gun"],
    "sniper": ["sniper", "hunting rifle"],
    "pistol": ["pistol", "hand cannon", "revolver", "flint-knock"],
    "explosive": ["launcher", "grenade", "clinger"], 
    "assault_rifle": ["assault rifle", "scar", "ar", "rifle"],
}


# Pre-compile regex patterns to avoid rebuilding them during high-frequency OCR loops.
# Stores tuples of (category, compiled_regex)
COMPILED_PATTERNS: List[Tuple[str, re.Pattern]] = [
    (category, re.compile(rf"\b{re.escape(keyword)}\b"))
    for category, keywords in CATEGORY_KEYWORDS.items()
    for keyword in keywords
]

# Translation table for common OCR misreads (e.g., "sh1eld" -> "shield")
OCR_TYPOS = str.maketrans("105", "ios")


def normalize_name(name: str) -> str:
    """Normalize OCR text, fix common number-to-letter typos, and stabilize boundaries."""
    # Convert to lowercase and fix basic OCR number/letter confusion
    normalized = name.casefold().translate(OCR_TYPOS)
    
    # Replace non-word characters (except hyphens) with spaces to ensure \b works predictably
    normalized = re.sub(r"[^\w\s-]", " ", normalized)
    
    return re.sub(r"\s+", " ", normalized).strip()


def classify_item(name: str) -> dict:
    """Return the first matching category and boolean flags using pre-compiled regex."""
    normalized = normalize_name(name)

    result = {
        "name": name,
        "normalized_name": normalized,
        "category": "unknown",
    }

    # Initialize all category flags to False
    for category in CATEGORY_KEYWORDS:
        result[category] = False

    # Check against pre-compiled patterns
    for category, pattern in COMPILED_PATTERNS:
        if pattern.search(normalized):
            result["category"] = category
            result[category] = True
            break  # Stop checking once we find the highest priority match

    return result


def add_keyword(category: str, keyword: str) -> None:
    """Add a matching keyword and compile its regex at runtime."""
    if category not in CATEGORY_KEYWORDS:
        CATEGORY_KEYWORDS[category] = []

    keyword = keyword.casefold().strip()
    if keyword and keyword not in CATEGORY_KEYWORDS[category]:
        CATEGORY_KEYWORDS[category].append(keyword)
        # Immediately compile and append the new pattern so it works in the very next frame
        COMPILED_PATTERNS.append((category, re.compile(rf"\b{re.escape(keyword)}\b")))
