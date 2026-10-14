"""
application_controller.py
Launches and closes common desktop applications. Extend KNOWN_APPS with
any executables you want gesture/voice shortcuts for.
"""

import os
import subprocess

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False

KNOWN_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "browser": "msedge.exe",
    "chrome": "chrome.exe",
    "cmd": "cmd.exe",
    "task_manager": "taskmgr.exe",
}


class ApplicationController:
    def __init__(self):
        self._processes = {}

    def open_app(self, name):
        """name is a key from KNOWN_APPS, or a full path/command."""
        target = KNOWN_APPS.get(name.lower(), name)
        try:
            proc = subprocess.Popen(target, shell=True)
            self._processes[name.lower()] = proc
            return True
        except Exception:
            return False

    def open_path(self, path):
        """Open a file or folder with the OS default handler."""
        try:
            os.startfile(path)
            return True
        except Exception:
            return False

    def close_app(self, name):
        """Closes all processes whose name matches (case-insensitive)."""
        if not _PSUTIL_AVAILABLE:
            return False
        target = KNOWN_APPS.get(name.lower(), name)
        closed_any = False
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] and target.lower() in proc.info["name"].lower():
                    proc.terminate()
                    closed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return closed_any

    def is_running(self, name):
        if not _PSUTIL_AVAILABLE:
            return False
        target = KNOWN_APPS.get(name.lower(), name)
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] and target.lower() in proc.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def list_running_apps(self):
        if not _PSUTIL_AVAILABLE:
            return []
        names = set()
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"]:
                    names.add(proc.info["name"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(names)
