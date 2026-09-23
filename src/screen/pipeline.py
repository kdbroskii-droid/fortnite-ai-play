"""End-to-end observation pipeline: capture -> OCR -> vision -> state.

Observation only. No keyboard, mouse, aiming, or firing commands are produced.
"""
from __future__ import annotations

from typing import Any, Optional
from .capture import WindowsScreenCapture
from .detector import YoloDetector
from .perception import OCRReader, HudTextInterpreter, CrosshairDetector, PerceptionResult, BoundingBox
from .recorder import FrameRecorder, ScreenState
from .hud import HudParser
from .tracker import ObjectTracker
from .non_weapon_classifier import classify_non_weapon


class ScreenPipeline:
    def __init__(self, capture: WindowsScreenCapture, detector: Optional[YoloDetector] = None,
                 recorder: Optional[FrameRecorder] = None) -> None:
        self.capture = capture
        self.detector = detector
        self.recorder = recorder or FrameRecorder()
        self.ocr = OCRReader()
        self.hud_text = HudTextInterpreter()
        self.hud = HudParser()
        self.crosshair = CrosshairDetector()
        self.tracker = ObjectTracker()

    def process(self, frame: Any) -> tuple[PerceptionResult, ScreenState]:
        height, width = frame.shape[:2]
        text = self.ocr.read(frame)
        hud_values = self.hud.parse(text)

        # Classify visible OCR text using the non-weapon item classifier.
        item_classification = {"category": "unknown"}
        for detection in text:
            candidate = classify_non_weapon(detection.text)
            if candidate["category"] != "unknown":
                item_classification = candidate
                break
        detections = self.detector.detect(frame) if self.detector else []
        players = [d for d in detections if d.label.lower() in {"person", "player"}]
        guns = [d for d in detections if d.label.lower() in {"gun", "weapon"}]
        crosshair = self.crosshair.detect(frame)
        tracked = self.tracker.update(detections)
        result = PerceptionResult(
            frame_width=width,
            frame_height=height,
            text=text,
            players=players,
            guns=guns,
            crosshair=crosshair,
            objects=tracked,
            item_category=item_classification["category"],
            item_flags={
                key: value
                for key, value in item_classification.items()
                if key not in {"name", "normalized_name", "category"}
            },
        )
        state = ScreenState(
            players_visible=len(players),
            crosshair_center_x=crosshair.center[0] if crosshair else None,
            crosshair_center_y=crosshair.center[1] if crosshair else None,
            current_weapon=hud_values.get("current_weapon"),
            weapon_slots=hud_values.get("weapon_slots", []),
            ammo_reserve=hud_values.get("ammo_reserve"),
            ammo_in_magazine=hud_values.get("ammo_in_magazine"),
            wood=hud_values.get("wood"), brick=hud_values.get("brick"), metal=hud_values.get("metal"),
            health=hud_values.get("health"), shield=hud_values.get("shield"),
            sprinting=hud_values.get("sprinting"), build_mode=hud_values.get("build_mode"),
            editing=hud_values.get("editing"), reloading=hud_values.get("reloading"),
            interaction_prompt=hud_values.get("interaction_prompt"),
            storm_phase=hud_values.get("storm_phase"),
            storm_time_remaining=hud_values.get("storm_time_remaining"),
            match_time=hud_values.get("match_time"),
            eliminations=hud_values.get("eliminations"),
            item_category=item_classification["category"],
            item_flags={
                key: value
                for key, value in item_classification.items()
                if key not in {"name", "normalized_name", "category"}
            },
        )
        self.recorder.add_frame(frame, state)
        return result, state

    def run(self, fps: float = 10.0):
        for frame in self.capture.frames(fps):
            yield self.process(frame)
