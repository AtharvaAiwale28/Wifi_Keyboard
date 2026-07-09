# Remote Keyboard (phone keyboard passthrough → laptop)

Turns a keyboard plugged into your phone (via USB-C/OTG) into a working
keyboard for a laptop whose built-in keyboard is broken. No Bluetooth HID
pairing needed — it works over Wi-Fi using a tiny local web app.

## How it works

1. External keyboard → phone via USB-C (OTG). The phone's OS treats it as
   a normal keyboard input device.
2. Laptop runs `server.py`, a Flask + WebSocket server, and simulates
   keystrokes locally using `pynput`.
3. Phone's browser opens a page served by the laptop. That page listens
   for `keydown`/`keyup` events (which fire from the external keyboard
   like any other keyboard) and streams them to the laptop over a
   WebSocket.
4. The laptop replays each keystroke as if you'd typed it directly.

## Requirements

- Laptop: Python 3.8+, and this project's files.
- Phone: a modern browser (Chrome/Safari), OTG adapter if needed, and the
  external keyboard.
- Both devices on the **same Wi-Fi network**. If you don't have a router
  handy, turn on the laptop's mobile hotspot from... wait, laptop keyboard
  is broken, so instead: turn on the **phone's Wi-Fi hotspot** and connect
  the laptop to it (this only needs the laptop's mouse/trackpad, which
  presumably still works).

## Setup

On the laptop:

```bash
pip install -r requirements.txt
python server.py
```

The terminal will print something like:

```
On your PHONE's browser, open:

    http://192.168.1.23:5000/?token=AbCdEf123

```

## Using it

1. On the phone, plug in the external keyboard via OTG.
2. Open the printed URL in the phone's browser (must include the
   `?token=...` part — this is a shared secret so random devices on the
   network can't type on your laptop).
3. Tap the on-screen box once to focus it.
4. Type on the external keyboard — keystrokes appear on the laptop.

## Notes & limitations

- Keep the phone's browser tab in the foreground and the box focused;
  if the phone locks or the tab loses focus, keystrokes stop being
  captured until you tap it again.
- Modifier combos (Ctrl+C, Alt+Tab, etc.) work because keydown/keyup are
  sent separately and replayed the same way, but the *phone's browser*
  may intercept a few browser-level shortcuts before they reach the page
  — this is a browser limitation, not something the app can bypass.
- This sends keystrokes unencrypted over your local network. Only use it
  on a network you trust (e.g., your own hotspot), and don't share the
  token.
- If typing feels laggy, move the laptop and phone closer to the router,
  or use the phone's hotspot directly instead of a shared router.

## Files

- `server.py` — run this on the laptop.
- `templates/index.html` — served automatically to the phone, no need to
  open it manually.
- `requirements.txt` — Python dependencies.
