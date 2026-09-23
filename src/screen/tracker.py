"""Lightweight frame-to-frame object tracking by nearest center."""
from __future__ import annotations
from dataclasses import replace
from math import hypot
from .perception import BoundingBox


class ObjectTracker:
    def __init__(self, max_distance: float = 120.0, max_missing: int = 8) -> None:
        self.max_distance = max_distance
        self.max_missing = max_missing
        self._tracks: dict[int, tuple[BoundingBox, int]] = {}
        self._next_id = 1

    def update(self, detections: list[BoundingBox]) -> list[BoundingBox]:
        old = self._tracks
        used: set[int] = set()
        new: dict[int, tuple[BoundingBox, int]] = {}
        result: list[BoundingBox] = []
        for det in detections:
            best_id = None
            best_dist = self.max_distance
            dc = det.center
            for tid, (prev, missing) in old.items():
                if tid in used or prev.label != det.label:
                    continue
                pc = prev.center
                dist = hypot(dc[0] - pc[0], dc[1] - pc[1])
                if dist < best_dist:
                    best_dist, best_id = dist, tid
            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
            used.add(best_id)
            tracked = replace(det, label=f"{det.label}#{best_id}")
            new[best_id] = (det, 0)
            result.append(tracked)
        for tid, (prev, missing) in old.items():
            if tid not in used and missing + 1 <= self.max_missing:
                new[tid] = (prev, missing + 1)
        self._tracks = new
        return result
