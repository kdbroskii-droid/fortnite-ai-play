"""Windows screen capture for the observation pipeline.

Uses MSS when installed. Frames are returned as OpenCV BGR numpy arrays.
No keyboard/mouse/game-input functionality is included.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional
import time


@dataclass(frozen=True)
class CaptureRegion:
    left: int = 0
    top: int = 0
    width: Optional[int] = None
    height: Optional[int] = None


class WindowsScreenCapture:
    """Capture the desktop or a selected monitor/region."""

    def __init__(self, region: Optional[CaptureRegion] = None, monitor: int = 1) -> None:
        self.region = region
        self.monitor = monitor
        self._mss = None

    def _client(self):
        if self._mss is None:
            try:
                import mss
            except ImportError as exc:
                raise RuntimeError("Screen capture requires mss. Install requirements.txt first.") from exc
            self._mss = mss.mss()
        return self._mss

    def grab(self):
        """Capture one frame as an OpenCV-compatible BGR array."""
        import numpy as np
        frame = self._client()
        if self.region is None:
            monitor = frame.monitors[self.monitor]
        else:
            monitor_info = frame.monitors[self.monitor]
            monitor = {
                "left": monitor_info["left"] + self.region.left,
                "top": monitor_info["top"] + self.region.top,
                "width": self.region.width or monitor_info["width"],
                "height": self.region.height or monitor_info["height"],
            }
        raw = np.asarray(frame.grab(monitor))
        return raw[:, :, :3].copy()

    def frames(self, fps: float = 10.0) -> Iterator:
        """Yield frames at approximately the requested rate."""
        if fps <= 0:
            raise ValueError("fps must be > 0")
        delay = 1.0 / fps
        while True:
            started = time.monotonic()
            yield self.grab()
            remaining = delay - (time.monotonic() - started)
            if remaining > 0:
                time.sleep(remaining)
