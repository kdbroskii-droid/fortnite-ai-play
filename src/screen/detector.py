"""Object-detection adapter for recorded screen frames.

The detector returns observations only. It does not select targets or emit
keyboard/mouse/game actions.

A YOLO model can be supplied by the caller. A generic COCO model is useful
for validating the pipeline, but it does NOT contain Fortnite-specific classes.
For reliable Fortnite player/weapon recognition, provide a model trained on
Fortnite screenshots.
"""

from __future__ import annotations

from typing import Any, Optional

from .perception import BoundingBox, ObjectDetectorAdapter


class YoloDetector:
    """Run an Ultralytics YOLO model against screen frames."""

    def __init__(self, model_path: str = "yolo11n.pt", confidence: float = 0.35,
                 device: Optional[str] = None) -> None:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        self.model_path = model_path
        self.confidence = confidence
        self.device = device
        self._model = None
        self._normalizer = ObjectDetectorAdapter()

    def _load(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise RuntimeError(
                    "YOLO detection requires ultralytics. Install requirements.txt first."
                ) from exc
            self._model = YOLO(self.model_path)
        return self._model

    def detect(self, frame: Any) -> list[BoundingBox]:
        model = self._load()
        kwargs = {"conf": self.confidence, "verbose": False}
        if self.device:
            kwargs["device"] = self.device
        results = model.predict(frame, **kwargs)
        if not results:
            return []

        result = results[0]
        names = result.names
        detections: list[dict[str, Any]] = []
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return []

        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            cls = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = map(float, xyxy)
            detections.append({
                "x": x1,
                "y": y1,
                "width": max(0.0, x2 - x1),
                "height": max(0.0, y2 - y1),
                "confidence": conf,
                "label": str(names.get(cls, cls)),
            })
        return self._normalizer.normalize(detections)

    def detect_categories(self, frame: Any, labels: set[str]) -> list[BoundingBox]:
        return [d for d in self.detect(frame) if d.label.lower() in {x.lower() for x in labels}]
