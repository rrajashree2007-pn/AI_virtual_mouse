"""
analytics_manager.py
Tracks gesture usage frequency, session duration, and mode-switch counts,
persisting to the SQLite database (via database/db_manager.py) so trends
can be reviewed across sessions in the GUI.
"""

import time
from collections import Counter


class AnalyticsManager:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.session_start = time.time()
        self.gesture_counts = Counter()
        self.mode_switch_count = 0
        self.click_count = 0

    def log_gesture(self, gesture_name):
        if gesture_name in ("none", "unknown"):
            return
        self.gesture_counts[gesture_name] += 1
        if self.db_manager:
            self.db_manager.log_gesture_event(gesture_name)

    def log_mode_switch(self, mode_name):
        self.mode_switch_count += 1
        if self.db_manager:
            self.db_manager.log_mode_switch(mode_name)

    def log_click(self):
        self.click_count += 1

    def session_duration_seconds(self):
        return time.time() - self.session_start

    def summary(self):
        return {
            "duration_seconds": round(self.session_duration_seconds(), 1),
            "total_gestures": sum(self.gesture_counts.values()),
            "gesture_breakdown": dict(self.gesture_counts.most_common()),
            "mode_switches": self.mode_switch_count,
            "clicks": self.click_count,
        }

    def most_used_gesture(self):
        if not self.gesture_counts:
            return None
        return self.gesture_counts.most_common(1)[0]

    def end_session(self):
        summary = self.summary()
        if self.db_manager:
            self.db_manager.log_session_summary(summary)
        return summary
