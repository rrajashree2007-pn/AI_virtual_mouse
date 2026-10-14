"""
voice_controller.py
Background voice-command listener. Runs speech recognition on a separate
thread (so it never blocks the video loop) and maps recognized phrases to
callbacks registered by main.py. Also provides text-to-speech feedback
for accessibility.
"""

import threading
import queue

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

try:
    import pyttsx3
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False


class VoiceController:
    def __init__(self, wake_word=None, energy_threshold=300):
        self.available = _SR_AVAILABLE
        self.wake_word = wake_word.lower() if wake_word else None
        self._commands = {}
        self._running = False
        self._thread = None
        self._command_queue = queue.Queue()

        if self.available:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = energy_threshold
            self.microphone = sr.Microphone()

        self._tts_engine = pyttsx3.init() if _TTS_AVAILABLE else None

    # ------------------------------------------------------------------
    def register_command(self, phrase, callback):
        """phrase is matched as a substring of the recognized text (case
        insensitive), e.g. 'open browser', 'increase volume'."""
        self._commands[phrase.lower()] = callback

    def speak(self, text):
        if self._tts_engine:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()

    # ------------------------------------------------------------------
    def start(self):
        if not self.available or self._running:
            return False
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._running = False

    def _listen_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        while self._running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=4)
                text = self.recognizer.recognize_google(audio).lower()
                self._command_queue.put(text)
            except Exception:
                continue

    def poll_and_dispatch(self):
        """Call once per main-loop iteration (non-blocking). Executes any
        commands recognized since the last call."""
        matched_any = False
        while not self._command_queue.empty():
            text = self._command_queue.get_nowait()

            if self.wake_word and self.wake_word not in text:
                continue

            for phrase, callback in self._commands.items():
                if phrase in text:
                    callback()
                    matched_any = True
        return matched_any
