"""Screen recording and perception helpers.

This package only observes/records frames and extracts non-targeting game state.
"""

from .recorder import FrameRecorder, ScreenState, HudPerception
from .capture import CaptureRegion, WindowsScreenCapture
from .perception import BoundingBox, TextDetection, PerceptionResult, OCRReader, HudTextInterpreter
from .detector import YoloDetector

__all__ = [
    "FrameRecorder", "ScreenState", "HudPerception",
    "CaptureRegion", "WindowsScreenCapture",
    "BoundingBox", "TextDetection", "PerceptionResult",
    "OCRReader", "HudTextInterpreter", "YoloDetector",
]
