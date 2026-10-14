"""
settings_gui.py
A simple Tkinter control panel that runs alongside the OpenCV camera
window, letting the user toggle features, tune sensitivity, and view
live analytics without touching config.py directly. Runs in its own
thread so it doesn't block the vision/gesture loop in main.py.
"""

import threading
import tkinter as tk
from tkinter import ttk


class SettingsGUI:
    def __init__(self, config, on_change=None, analytics_manager=None):
        """config: a mutable dict of live settings shared with main.py.
        on_change: optional callback(key, value) fired whenever a control changes.
        analytics_manager: optional AnalyticsManager to display live stats.
        """
        self.config = config
        self.on_change = on_change
        self.analytics_manager = analytics_manager
        self._root = None
        self._thread = None
        self._stats_labels = {}

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self._root = tk.Tk()
        self._root.title("AI Virtual Mouse - Settings")
        self._root.geometry("360x480")

        notebook = ttk.Notebook(self._root)
        notebook.pack(fill="both", expand=True)

        self._build_general_tab(notebook)
        self._build_sensitivity_tab(notebook)
        self._build_stats_tab(notebook)

        self._poll_stats()
        self._root.mainloop()

    # ------------------------------------------------------------------
    def _build_general_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Features")

        toggles = [
            ("voice_control", "Voice Control"),
            ("accessibility_mode", "Accessibility Mode"),
            ("analytics", "Analytics"),
            ("auto_lock", "Auto-lock on absence"),
        ]

        for key, label in toggles:
            var = tk.BooleanVar(value=self.config.get(key, False))

            def make_cmd(k=key, v=var):
                return lambda: self._emit(k, v.get())

            chk = ttk.Checkbutton(frame, text=label, variable=var, command=make_cmd())
            chk.pack(anchor="w", padx=12, pady=8)

    def _build_sensitivity_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Sensitivity")

        sliders = [
            ("mouse_smoothening", "Mouse smoothing", 1, 15),
            ("click_distance_threshold", "Pinch click distance", 10, 80),
            ("cursor_sensitivity", "Cursor sensitivity", 5, 30),
        ]

        for key, label, lo, hi in sliders:
            ttk.Label(frame, text=label).pack(anchor="w", padx=12, pady=(10, 0))
            var = tk.DoubleVar(value=self.config.get(key, (lo + hi) / 2))

            def make_cmd(k=key, v=var):
                return lambda val: self._emit(k, float(val))

            scale = ttk.Scale(frame, from_=lo, to=hi, variable=var,
                               orient="horizontal", command=make_cmd())
            scale.pack(fill="x", padx=12)

    def _build_stats_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Live Stats")

        for label in ["Session duration", "Total gestures", "Most used gesture", "Clicks"]:
            row = ttk.Frame(frame)
            row.pack(fill="x", padx=12, pady=6)
            ttk.Label(row, text=label + ":").pack(side="left")
            value_lbl = ttk.Label(row, text="-")
            value_lbl.pack(side="right")
            self._stats_labels[label] = value_lbl

    def _poll_stats(self):
        if self.analytics_manager:
            summary = self.analytics_manager.summary()
            most_used = self.analytics_manager.most_used_gesture()
            self._stats_labels["Session duration"].config(text=f"{summary['duration_seconds']}s")
            self._stats_labels["Total gestures"].config(text=str(summary["total_gestures"]))
            self._stats_labels["Most used gesture"].config(
                text=f"{most_used[0]} ({most_used[1]})" if most_used else "-"
            )
            self._stats_labels["Clicks"].config(text=str(summary["clicks"]))

        if self._root:
            self._root.after(1000, self._poll_stats)

    def _emit(self, key, value):
        self.config[key] = value
        if self.on_change:
            self.on_change(key, value)
