# AI Virtual Mouse

Control your Windows PC — cursor, clicks, volume, brightness, media,
presentations, and freehand drawing — using nothing but your webcam and
hand gestures. Includes optional voice commands and accessibility
features (dwell click, blink click, sensitivity scaling).

## Features

- **Mouse mode** — move the cursor with your index finger, pinch to
  click, peace-sign to right-click, open palm to scroll.
- **Volume / Brightness modes** — thumbs-up / pinky-out to raise/lower,
  fist to mute.
- **Media control** — play/pause, next/previous track, all via the OS
  media keys (works with any player).
- **Presentation mode** — advance/rewind slides, toggle a laser pointer,
  black out the screen.
- **Air drawing** — draw on a transparent canvas overlaid on the video
  feed; switch colors, use an eraser, save your sketch as a PNG.
- **Custom gestures** — record your own hand shapes and bind them to
  actions (`gestures/gesture_training.py`).
- **Voice commands** — optional background speech-recognition listener
  for hands-free control (`voice/voice_controller.py`).
- **Accessibility** — dwell-to-click, blink-to-click, and adjustable
  cursor sensitivity for users with limited hand mobility.
- **Security** — auto-lock the workstation if no face is detected for a
  configurable timeout; optional gesture "PIN" sequences.
- **Analytics** — tracks gesture usage and session stats, persisted to a
  local SQLite database, viewable in the settings GUI.
- **Settings GUI** — a lightweight Tkinter panel to tweak sensitivity and
  toggle features live, without editing code.

## Requirements

- Windows 10/11 (uses `pycaw`, `screen-brightness-control`, `pywin32`,
  and raw `user32.dll` calls for cursor/window control)
- Python 3.9+
- A webcam
- A microphone (only needed for voice commands)

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `pyaudio` (used by SpeechRecognition) can be tricky to pip
> install on Windows. If it fails, download a matching wheel from
> https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio or install via
> `pip install pipwin && pipwin install pyaudio`.

## Running

```bash
python main.py
```

A window titled **"AI Virtual Mouse"** will open showing your webcam
feed with hand landmarks and a live overlay of the current mode, FPS,
and detected gesture. A Tkinter settings panel opens alongside it.

### Keyboard shortcuts (focus the video window first)

| Key | Action                        |
|-----|-------------------------------|
| q   | Quit                          |
| m   | Switch to Mouse mode          |
| v   | Switch to Volume mode         |
| b   | Switch to Brightness mode     |
| p   | Switch to Presentation mode   |
| d   | Switch to Drawing mode        |
| a   | Toggle accessibility mode     |
| l   | Toggle auto-lock on absence   |
| c   | Clear drawing canvas          |
| s   | Save drawing canvas to PNG    |

### Default gestures

| Gesture              | Mouse mode      | Volume mode | Brightness mode | Presentation mode | Drawing mode     |
|-----------------------|-----------------|-------------|------------------|--------------------|------------------|
| Point (index only)    | Move cursor     | —           | —                | Next slide         | Draw stroke      |
| Pinch (thumb+index)   | Click / drag    | —           | —                | —                  | —                |
| Open palm             | Scroll          | —           | —                | Toggle black screen| Lift pen         |
| Peace (index+middle)  | Right click     | —           | —                | Previous slide     | Cycle color      |
| Fist                  | Play/pause media| Mute        | —                | Toggle pointer     | Toggle eraser    |
| Thumbs up             | —               | Volume up   | Brightness up    | —                  | —                |
| Pinky out             | —               | Volume down | Brightness down  | —                  | —                |

## Project structure

```
AI_Virtual_Mouse/
├── main.py                    # Entry point / app loop
├── config.py                  # All tunable settings
├── requirements.txt
├── detectors/                 # MediaPipe-based vision: hands, face, eyes, objects
├── controllers/                # OS control: mouse, volume, brightness, keyboard, apps, windows, media
├── gestures/                   # Gesture classification, action mapping, custom gesture training
├── ai_models/                  # Optional trainable KNN gesture classifier
├── voice/                      # Background speech-recognition command listener
├── accessibility/              # Dwell click, blink click, sensitivity scaling
├── presentation/                # Slide-control mode
├── drawing/                     # Air-drawing canvas
├── security/                    # Presence-based auto-lock, gesture PIN
├── analytics/                   # Session/gesture usage tracking
├── database/                    # SQLite persistence layer
├── gui/                         # Tkinter settings panel
├── utils/                       # Smoothing filters, coordinate mapping, FPS counter
├── assets/                      # Static resources (icons, optional DNN model files)
└── tests/                       # Unit tests for pure-logic modules
```

## Training a custom gesture

```python
from gestures.custom_gestures import CustomGestureStore
from gestures.gesture_training import GestureTrainer

store = CustomGestureStore("gestures/custom_gestures.json")
trainer = GestureTrainer(store, samples_required=30)
trainer.start("my_gesture")

# In your capture loop, once per frame while holding the new gesture:
# trainer.feed_frame(landmark_list)
```

## Running tests

Pure-logic tests (no camera/mic/Windows APIs required) live in `tests/`:

```bash
python -m unittest discover tests
```

## Extending object detection

`detectors/object_detector.py` runs a simple motion-based fallback out
of the box. For real object classification, drop a MobileNet-SSD Caffe
model into `ai_models/`:

- `ai_models/MobileNetSSD_deploy.prototxt`
- `ai_models/MobileNetSSD_deploy.caffemodel`

The detector will automatically switch to using it.

## Safety notes

- `security.SecurityManager.lock_workstation()` calls the real Windows
  `LockWorkStation()` API — test the timeout value before relying on it.
- Voice recognition sends audio to Google's speech-recognition API via
  the `SpeechRecognition` package; nothing is sent anywhere else.
