from src.screen.hud import HudParser
from src.screen.perception import TextDetection
from src.screen.tracker import ObjectTracker


def test_hud_parser_materials_and_ammo():
    detections = [
        TextDetection("WOOD 450", 0, 0, 80, 20),
        TextDetection("AMMO 28 120", 0, 0, 100, 20),
    ]
    state = HudParser().parse(detections)
    assert state["wood"] == 450
    assert state["ammo_in_magazine"] == 28
    assert state["ammo_reserve"] == 120


def test_tracker_keeps_nearby_objects():
    tracker = ObjectTracker(max_distance=100)
    first = tracker.update([{"x": 100, "y": 100, "width": 20, "height": 20, "confidence": .9, "label": "player"}])
    assert first[0].label.endswith("#1")


def test_hud_parser_health_and_shield():
    state = HudParser().parse([
        TextDetection("HEALTH 100", 0, 0, 80, 20),
        TextDetection("SHIELD 50", 0, 0, 80, 20),
    ])
    assert state["health"] == 100
    assert state["shield"] == 50
