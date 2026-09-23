"""Linux/Chromebook launcher for the observation-only screen pipeline.

This launcher captures the Linux desktop and prints basic perception state.
It does not send keyboard or mouse input and does not control a game.
"""

from __future__ import annotations

import argparse
import time

from src.screen.capture import WindowsScreenCapture
from src.screen.pipeline import ScreenPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the observation pipeline on Linux/Chromebook.")
    parser.add_argument("--fps", type=float, default=5.0, help="Capture rate (default: 5 FPS)")
    args = parser.parse_args()

    if args.fps <= 0:
        raise SystemExit("--fps must be greater than 0")

    capture = WindowsScreenCapture()
    pipeline = ScreenPipeline(capture=capture)

    print("Chromebook/Linux observation pipeline started.")
    print("Press Ctrl+C to stop.")
    print("No keyboard/mouse/game-input commands are generated.")

    try:
        for result, state in pipeline.run(fps=args.fps):
            print(
                f"players={state.players_visible} "
                f"item={state.item_category} "
                f"health={state.health} "
                f"shield={state.shield} "
                f"ammo={state.ammo_in_magazine}",
                flush=True,
            )
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
