from src.screen.non_weapon_classifier import classify_non_weapon
from src.screen.perception import PerceptionResult, TextDetection
from src.screen.pipeline import ScreenPipeline


def test_non_weapon_classifier_matches_whole_words():
    result = classify_non_weapon("blue car")
    assert result["category"] == "vehicle"
    assert result["vehicle"] is True


def test_non_weapon_classifier_does_not_match_inside_words():
    result = classify_non_weapon("scarecrow")
    assert result["category"] == "unknown"


def test_perception_result_stores_item_classification():
    result = PerceptionResult(
        frame_width=1920,
        frame_height=1080,
        text=[],
        players=[],
        guns=[],
        crosshair=None,
        objects=[],
        item_category="vehicle",
        item_flags={"vehicle": True},
    )
    data = result.to_dict()
    assert data["item_category"] == "vehicle"
    assert data["item_flags"]["vehicle"] is True


def test_pipeline_attaches_non_weapon_ocr_classification():
    pipeline = ScreenPipeline(capture=object())

    pipeline.ocr.read = lambda frame: [
        TextDetection("Blue Car", 0, 0, 100, 20)
    ]
    pipeline.hud.parse = lambda detections: {}
    pipeline.crosshair.detect = lambda frame: None

    class FakeFrame:
        shape = (1080, 1920, 3)

    result, state = pipeline.process(FakeFrame())

    assert result.item_category == "vehicle"
    assert result.item_flags["vehicle"] is True
    assert state.item_category == "vehicle"
    assert state.item_flags["vehicle"] is True
