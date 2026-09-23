"""Screen recording and perception helpers.

This package only observes/records frames and extracts non-targeting game state.
"""

from .recorder import FrameRecorder, ScreenState, HudPerception

__all__ = ["FrameRecorder", "ScreenState", "HudPerception"]
