"""
Entry point for the PyInstaller-bundled Windows .exe.
Starts Flask silently then opens the browser.
"""
import sys
import os
import threading
import time
import webbrowser

# When frozen as .exe, tell App.py where to find templates/static
if getattr(sys, 'frozen', False):
    os.environ['WEAZZAR_BASE_DIR'] = sys._MEIPASS  # type: ignore[attr-defined]

from App import app  # noqa: E402 — must come after env var is set


def _open_browser() -> None:
    time.sleep(1.8)  # give Flask time to start
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    threading.Thread(target=_open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
