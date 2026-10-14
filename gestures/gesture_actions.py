"""
gesture_actions.py
Central place that maps a gesture name -> a callback. main.py builds one
of these per "mode" (mouse mode, volume mode, media mode, drawing mode...)
so the same gesture can mean different things depending on context.
"""


class GestureActionMapper:
    def __init__(self):
        self._map = {}
        self._last_fired = None

    def bind(self, gesture_name, callback):
        """Register a callback (no-args or takes optional context dict)."""
        self._map[gesture_name] = callback

    def unbind(self, gesture_name):
        self._map.pop(gesture_name, None)

    def dispatch(self, gesture_name, context=None, fire_once=True):
        """Calls the bound callback for gesture_name if one exists.

        If fire_once is True, the same gesture won't repeatedly fire every
        frame while held -- only when it changes from the previous frame.
        Set fire_once=False for continuous actions like cursor movement
        or scroll-while-held.
        """
        if gesture_name not in self._map:
            self._last_fired = gesture_name
            return False

        if fire_once and gesture_name == self._last_fired:
            return False

        callback = self._map[gesture_name]
        try:
            if context is not None:
                callback(context)
            else:
                callback()
        finally:
            self._last_fired = gesture_name
        return True

    def bound_gestures(self):
        return list(self._map.keys())
