"""
Remote Keyboard Server
-----------------------
Run this on the LAPTOP whose keyboard is broken.

It serves a small webpage. Open that page in your PHONE's browser
(phone must be on the same Wi-Fi network as the laptop, or the laptop
connected to the phone's hotspot). Plug your external keyboard into the
phone via USB-C/OTG, tap the page to focus it, and start typing -- every
keystroke is streamed to the laptop and replayed here with pynput.

Setup:
    pip install flask flask-socketio pynput eventlet

Run:
    python server.py

Then on the laptop, find its local IP (see instructions printed on start),
and open  http://<that-ip>:5000/?token=YOUR_TOKEN  in the phone's browser.
"""

import secrets
import socket

from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO
from pynput.keyboard import Controller, Key

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
keyboard = Controller()

# Simple shared secret so a random device on the same network can't type on
# your laptop. Change this or pass --token on the command line.
TOKEN = secrets.token_urlsafe(8)

# Map JavaScript KeyboardEvent.key values to pynput Key members.
# Anything not in this map is treated as a literal character.
SPECIAL_KEYS = {
    "Enter": Key.enter,
    "Backspace": Key.backspace,
    "Tab": Key.tab,
    "Escape": Key.esc,
    " ": Key.space,
    "Shift": Key.shift,
    "Control": Key.ctrl,
    "Alt": Key.alt,
    "Meta": Key.cmd,
    "CapsLock": Key.caps_lock,
    "ArrowUp": Key.up,
    "ArrowDown": Key.down,
    "ArrowLeft": Key.left,
    "ArrowRight": Key.right,
    "Home": Key.home,
    "End": Key.end,
    "PageUp": Key.page_up,
    "PageDown": Key.page_down,
    "Delete": Key.delete,
    "Insert": Key.insert,
    "F1": Key.f1, "F2": Key.f2, "F3": Key.f3, "F4": Key.f4,
    "F5": Key.f5, "F6": Key.f6, "F7": Key.f7, "F8": Key.f8,
    "F9": Key.f9, "F10": Key.f10, "F11": Key.f11, "F12": Key.f12,
}


def resolve_key(js_key: str):
    """Translate a JS key name into something pynput can press/release."""
    if js_key in SPECIAL_KEYS:
        return SPECIAL_KEYS[js_key]
    if len(js_key) == 1:
        return js_key
    # Unknown multi-char key name (e.g. "Dead", "Unidentified") -> ignore
    return None


def check_token():
    token = request.args.get("token")
    if token != TOKEN:
        abort(403)


@app.route("/")
def index():
    check_token()
    return render_template("index.html", token=TOKEN)


@socketio.on("keydown")
def on_keydown(data):
    key = resolve_key(data.get("key", ""))
    if key is not None:
        try:
            keyboard.press(key)
        except Exception:
            pass


@socketio.on("keyup")
def on_keyup(data):
    key = resolve_key(data.get("key", ""))
    if key is not None:
        try:
            keyboard.release(key)
        except Exception:
            pass


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    ip = local_ip()
    print("=" * 60)
    print("Remote Keyboard Server")
    print("=" * 60)
    print(f"On your PHONE's browser, open:\n")
    print(f"    http://{ip}:5000/?token={TOKEN}\n")
    print("Make sure the phone is on the same Wi-Fi network as this")
    print("laptop (or this laptop is connected to the phone's hotspot).")
    print("=" * 60)
    socketio.run(app, host="0.0.0.0", port=5000)
