"""Visual perception utilities for recorded/captured frames.

This module observes frames only. Text is returned as text; visual objects are
represented by image coordinates. No coordinates are converted into input,
aiming, or firing commands.

Optional dependencies:
    opencv-python
    pytesseract
    mss (for live Windows screen capture)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Optional
import re


@dataclass
class BoundingBox:
    """Pixel-space rectangle for something visible in a frame."""

    x: float
    y: float
    width: float
    height: float
    confidence: float = 0.0
    label: str = "unknown"

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self) | {"center_x": self.center[0], "center_y": self.center[1]}


@dataclass
class TextDetection:
    text: str
    x: float
    y: float
    width: float
    height: float
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PerceptionResult:
    """Everything observed in one frame."""

    frame_width: int
    frame_height: int
    text: list[TextDetection]
    players: list[BoundingBox]
    guns: list[BoundingBox]
    crosshair: Optional[BoundingBox]
    objects: list[BoundingBox]
    item_category: str = "unknown"
    item_flags: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "text": [x.to_dict() for x in self.text],
            "players": [x.to_dict() for x in self.players],
            "guns": [x.to_dict() for x in self.guns],
            "crosshair": self.crosshair.to_dict() if self.crosshair else None,
            "objects": [x.to_dict() for x in self.objects],
            "item_category": self.item_category,
            "item_flags": self.item_flags,
        }


class OCRReader:
    """OCR adapter. Importing the package does not require Tesseract."""

    def read(self, frame: Any) -> list[TextDetection]:
        try:
            import pytesseract
            import cv2
        except ImportError as exc:
            raise RuntimeError(
                "OCR requires opencv-python and pytesseract."
            ) from exc

        data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
        result: list[TextDetection] = []
        for i, raw in enumerate(data["text"]):
            text = raw.strip()
            if not text:
                continue
            try:
                confidence = float(data["conf"][i]) / 100.0
            except (ValueError, TypeError):
                confidence = 0.0
            result.append(TextDetection(
                text=text,
                x=float(data["left"][i]),
                y=float(data["top"][i]),
                width=float(data["width"][i]),
                height=float(data["height"][i]),
                confidence=max(0.0, confidence),
            ))
        return result


class HudTextInterpreter:
    """Turns OCR text into useful HUD values without relying on fixed pixels."""

    INTEGER_RE = re.compile(r"\b(\d{1,5})\b")

    def interpret(self, detections: list[TextDetection]) -> dict[str, Any]:
        joined = " ".join(d.text for d in detections)
        numbers = [int(x) for x in self.INTEGER_RE.findall(joined)]
        lower = joined.lower()

        result: dict[str, Any] = {"raw_text": joined, "numbers": numbers}

        # These are intentionally conservative. A real HUD layout can be
        # configured later instead of guessing from arbitrary screen text.
        if any(word in lower for word in ("wood", "brick", "metal")):
            result["materials_text"] = [d.text for d in detections
                                         if any(w in d.text.lower() for w in ("wood", "brick", "metal"))]
        if "ammo" in lower or "reload" in lower:
            result["ammo_text"] = joined
        if "health" in lower or "shield" in lower:
            result["health_shield_text"] = joined
        return result


class ObjectDetectorAdapter:
    """Adapter for an external object detector.

    Pass detections returned by a detector/model as BoundingBox instances.
    This keeps model choice separate from the recorder and perception code.
    """

    def normalize(self, detections: list[dict[str, Any]]) -> list[BoundingBox]:
        result: list[BoundingBox] = []
        for item in detections:
            try:
                result.append(BoundingBox(
                    x=float(item["x"]),
                    y=float(item["y"]),
                    width=float(item["width"]),
                    height=float(item["height"]),
                    confidence=float(item.get("confidence", 0.0)),
                    label=str(item.get("label", "unknown")),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        return result


class CrosshairDetector:
    """Find a likely crosshair center using image processing."""

    def detect(self, frame: Any) -> Optional[BoundingBox]:
        try:
            import cv2
        except ImportError as exc:
            raise RuntimeError("Crosshair detection requires opencv-python.") from exc

        height, width = frame.shape[:2]
        # Search only the central region to avoid mistaking HUD elements for
        # the crosshair. This is observation-only and returns pixel coordinates.
        cx, cy = width / 2, height / 2
        radius = max(80, int(min(width, height) * 0.12))
        x1, y1 = max(0, int(cx - radius)), max(0, int(cy - radius))
        x2, y2 = min(width, int(cx + radius)), min(height, int(cy + radius))
        crop = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
        moments = cv2.moments(threshold)
        if moments["m00"] <= 0:
            return None
        px = x1 + moments["m10"] / moments["m00"]
        py = y1 + moments["m01"] / moments["m00"]
        return BoundingBox(px - 2, py - 2, 4, 4, 0.2, "crosshair")
