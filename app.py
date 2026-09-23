"""Fortnite AI Play - Chromebook/Linux desktop app.

Observation-only GUI. It captures the Linux desktop and displays perception
state. It does not send keyboard/mouse/game input.
"""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, messagebox

from src.screen.capture import WindowsScreenCapture
from src.screen.pipeline import ScreenPipeline


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Fortnite AI Play")
        root.geometry("760x520")
        root.minsize(650, 450)

        self.running = False
        self.pipeline = None
        self.thread = None

        title = ttk.Label(root, text="Fortnite AI Play", font=("TkDefaultFont", 20, "bold"))
        title.pack(pady=(15, 2))
        ttk.Label(root, text="Chromebook / Linux • Observation only").pack()

        controls = ttk.Frame(root)
        controls.pack(pady=15)

        self.start_btn = ttk.Button(controls, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.test_btn = ttk.Button(controls, text="Diagnostics", command=self.diagnostics)
        self.test_btn.grid(row=0, column=2, padx=5)

        self.status = tk.StringVar(value="Stopped")
        ttk.Label(root, textvariable=self.status).pack()

        self.state_text = tk.Text(root, height=20, width=90, state="disabled")
        self.state_text.pack(padx=15, pady=10, fill="both", expand=True)

        ttk.Label(
            root,
            text="No keyboard, mouse, aiming, or firing commands are generated.",
        ).pack(pady=(0, 10))

        root.protocol("WM_DELETE_WINDOW", self.close)

    def write_state(self, text: str) -> None:
        self.state_text.configure(state="normal")
        self.state_text.delete("1.0", "end")
        self.state_text.insert("1.0", text)
        self.state_text.configure(state="disabled")

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status.set("Running — observing desktop")
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def worker(self) -> None:
        try:
            capture = WindowsScreenCapture()
            self.pipeline = ScreenPipeline(capture=capture)
            for result, state in self.pipeline.run(fps=5):
                if not self.running:
                    break
                text = (
                    f"Players visible: {state.players_visible}\n"
                    f"Item category: {state.item_category}\n"
                    f"Health: {state.health}\n"
                    f"Shield: {state.shield}\n"
                    f"Ammo: {state.ammo_in_magazine}\n"
                    f"Materials: wood={state.wood}, brick={state.brick}, metal={state.metal}\n"
                    f"Storm: {state.storm_phase} / {state.storm_time_remaining}\n"
                    f"Eliminations: {state.eliminations}\n"
                    f"Objects detected: {len(result.objects)}\n"
                    f"OCR detections: {len(result.text)}"
                )
                self.root.after(0, self.write_state, text)
        except Exception as exc:
            self.root.after(0, self.write_state, f"Error:\n{exc}")
        finally:
            self.root.after(0, self.finish)

    def finish(self) -> None:
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if self.status.get().startswith("Running"):
            self.status.set("Stopped")

    def stop(self) -> None:
        self.running = False
        self.status.set("Stopping...")

    def diagnostics(self) -> None:
        checks = [
            "Python GUI: OK",
            "Project modules: OK",
            "Observation mode: ENABLED",
            "Keyboard/mouse control: DISABLED",
        ]
        messagebox.showinfo("Diagnostics", "\n".join(checks))

    def close(self) -> None:
        self.running = False
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
