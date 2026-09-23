# Fortnite AI Play

External AI play-testing project.

## Input layer

The first module defines a complete keyboard/mouse input vocabulary and a macro format for controlled testing.

**Important:** this project does not implement stealth, device impersonation, anti-cheat bypass, or attempts to conceal automated input. The input layer is designed to be explicit and controllable.

### Keyboard coverage

The key map includes:
- A-Z
- 0-9
- F1-F24
- arrows
- modifiers
- navigation keys
- punctuation
- numpad keys
- media/system keys where the host supports them

### Macro format

Macros are sequences of actions such as key down/up, mouse movement, mouse button down/up, wheel events, and delays.

Example:

```json
{
  "name": "movement_test",
  "actions": [
    {"type": "key_down", "key": "W"},
    {"type": "delay", "ms": 500},
    {"type": "key_up", "key": "W"},
    {"type": "mouse_move", "dx": 20, "dy": 0}
  ]
}
```

The implementation is intentionally separated from the AI decision layer so the AI can later produce validated actions without directly controlling the OS.


## Chromebook / Linux (x86_64)

The repository includes a Linux/Chromebook launcher for the observation pipeline. It uses Python, MSS screen capture, OpenCV, and OCR. The Linux launcher is observation-only: it captures and analyzes the desktop but does not send keyboard or mouse input.

### Install

From the repository directory:

```bash
bash install_linux.sh
```

### Run

```bash
bash run_linux.sh
```

You can lower or raise the capture rate:

```bash
bash run_linux.sh --fps 3
```

The default is 5 FPS to keep CPU usage reasonable on a Chromebook.

### Tests

```bash
source .venv/bin/activate
```

```bash
pytest -q
```
