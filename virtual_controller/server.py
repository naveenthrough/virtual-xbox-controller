#!/usr/bin/env python3
"""
Virtual PS4 Controller — Laptop Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serves the controller page to your phone over WiFi and processes
all inputs (buttons, sticks, triggers, trackpad mouse) on your laptop.

SETUP (run once):
  pip install aiohttp pynput qrcode[pil]

  Windows — for a REAL virtual gamepad (games will see it as Xbox 360):
    pip install vgamepad
    Install ViGEmBus: https://github.com/ViGEm/ViGEmBus/releases/latest

  Linux — for a REAL virtual gamepad:
    pip install evdev   (then run as sudo, or add uinput udev rules)

RUN:
  python server.py
  → Scan the QR code or open the URL on your phone (same WiFi)

FALLBACK:
  If vgamepad/evdev are unavailable, buttons map to keyboard keys
  and the trackpad controls your mouse via pynput.
"""

import asyncio
import json
import socket
import sys
from pathlib import Path

try:
    import aiohttp
    from aiohttp import web
except ImportError:
    print("ERROR: aiohttp not found.\n  Run: pip install aiohttp")
    sys.exit(1)

PORT = 7070

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BACKEND 1 — vgamepad  (Windows: true Xbox 360 virtual controller)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VGAMEPAD_OK = False
gamepad = None
BTN = {}

try:
    import vgamepad as vg
    gamepad = vg.VX360Gamepad()
    VGAMEPAD_OK = True
    BTN = {
        # PS button   →   Xbox 360 equivalent
        "CROSS":    vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "CIRCLE":   vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "SQUARE":   vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "TRIANGLE": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "L1":       vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "R1":       vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "SHARE":    vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "OPTIONS":  vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "PS":       vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
        "L3":       vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        "R3":       vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        "DU":       vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "DD":       vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "DL":       vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "DR":       vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }
    print("✅  vgamepad  — Virtual Xbox 360 controller created")
    print("    (Requires ViGEmBus: https://github.com/ViGEm/ViGEmBus/releases)")
except Exception as e:
    print(f"⚠️  vgamepad unavailable ({type(e).__name__}: {e})")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BACKEND 2 — pynput  (keyboard/mouse simulation, all platforms)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PYNPUT_OK = False
kb = None
ms = None
MsBtn = None
KB_MAP: dict = {}

try:
    from pynput.keyboard import Key, Controller as KbCtrl
    from pynput.mouse import Button as MsBtn, Controller as MsCtrl  # noqa: F401

    kb = KbCtrl()
    ms = MsCtrl()
    PYNPUT_OK = True
    KB_MAP = {
        # PS button   →   keyboard key
        "CROSS":    "z",
        "CIRCLE":   "x",
        "SQUARE":   "a",
        "TRIANGLE": "s",
        "L1":       "q",
        "R1":       "e",
        "L2":       "r",
        "R2":       "f",
        "DU":       Key.up,
        "DD":       Key.down,
        "DL":       Key.left,
        "DR":       Key.right,
        "SHARE":    Key.tab,
        "OPTIONS":  Key.esc,
        "PS":       Key.home,
        "L3":       Key.f9,
        "R3":       Key.f10,
    }
    print("✅  pynput   — Keyboard / mouse simulation ready")
except Exception as e:
    print(f"⚠️  pynput unavailable ({type(e).__name__}: {e})")
    print("    Install: pip install pynput")

BACKEND = "vgamepad" if VGAMEPAD_OK else ("pynput" if PYNPUT_OK else "none")
if BACKEND == "none":
    print("\n⛔  No input backend available — inputs will be logged only.\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Input handlers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def on_button(btn_id: str, pressed: bool):
    """Digital button press/release."""
    if VGAMEPAD_OK and btn_id in BTN:
        fn = gamepad.press_button if pressed else gamepad.release_button
        fn(button=BTN[btn_id])
        gamepad.update()
    elif PYNPUT_OK and btn_id in KB_MAP:
        key = KB_MAP[btn_id]
        try:
            kb.press(key) if pressed else kb.release(key)
        except Exception:
            pass


def on_stick(stick_id: str, x: float, y: float):
    """Analog stick — x/y in -1.0 .. 1.0"""
    if VGAMEPAD_OK:
        # Xbox 360 axes: -32768 .. 32767, Y inverted
        ix = _clamp(int(x * 32767), -32768, 32767)
        iy = _clamp(int(-y * 32767), -32768, 32767)
        if stick_id == "LEFT":
            gamepad.left_joystick(x_value=ix, y_value=iy)
        else:
            gamepad.right_joystick(x_value=ix, y_value=iy)
        gamepad.update()
    # pynput has no analog stick equivalent — silently ignore


def on_trigger(trig_id: str, value: float):
    """Analog trigger — value in 0.0 .. 1.0"""
    if VGAMEPAD_OK:
        bv = _clamp(int(value * 255), 0, 255)
        if trig_id == "L2":
            gamepad.left_trigger(value=bv)
        else:
            gamepad.right_trigger(value=bv)
        gamepad.update()
    elif PYNPUT_OK:
        # Threshold-based keyboard fallback
        key = KB_MAP.get(trig_id)
        if key:
            try:
                kb.press(key) if value > 0.15 else kb.release(key)
            except Exception:
                pass


def on_mouse_move(dx: float, dy: float):
    """Relative mouse movement from trackpad."""
    if PYNPUT_OK and ms:
        ms.move(int(dx), int(dy))


def on_mouse_click(button: str, pressed: bool):
    """Mouse button press/release from trackpad tap."""
    if PYNPUT_OK and ms and MsBtn:
        btn = MsBtn.left if button == "left" else MsBtn.right
        try:
            ms.press(btn) if pressed else ms.release(btn)
        except Exception:
            pass


def on_mouse_scroll(dx: float, dy: float):
    """Scroll wheel from trackpad two-finger gesture."""
    if PYNPUT_OK and ms:
        ms.scroll(int(dx), int(-dy))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  WebSocket server
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
clients: set = set()

EVENT_HANDLERS = {
    "button":      lambda d: on_button(d["id"], d["pressed"]),
    "stick":       lambda d: on_stick(d["id"], d["x"], d["y"]),
    "trigger":     lambda d: on_trigger(d["id"], d["value"]),
    "mouse_move":  lambda d: on_mouse_move(d["dx"], d["dy"]),
    "mouse_click": lambda d: on_mouse_click(d["button"], d["pressed"]),
    "mouse_scroll":lambda d: on_mouse_scroll(d.get("dx", 0), d["dy"]),
}


async def ws_handler(request: web.Request):
    ws = web.WebSocketResponse(heartbeat=10)
    await ws.prepare(request)
    clients.add(ws)
    ip = request.headers.get("X-Real-IP", request.remote)
    print(f"\n📱  Phone connected    [{ip}]")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    t = data.get("type")
                    if t == "ping":
                        await ws.send_str('{"type":"pong"}')
                    elif t in EVENT_HANDLERS:
                        EVENT_HANDLERS[t](data)
                except (json.JSONDecodeError, KeyError, TypeError):
                    pass
            elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
                break
    finally:
        clients.discard(ws)
        print(f"📴  Phone disconnected [{ip}]")

    return ws


async def index_handler(request: web.Request):
    html = Path(__file__).parent / "controller.html"
    if html.exists():
        return web.FileResponse(html, headers={"Cache-Control": "no-cache"})
    return web.Response(
        text="controller.html not found — place it next to server.py",
        status=404,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_local_ip() -> str:
    """Return the machine's LAN IP address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"


def print_qr(url: str):
    """Print an ASCII QR code if qrcode is installed."""
    try:
        import qrcode  # noqa: F401
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        print()
        qr.print_ascii(invert=True)
        print()
    except ImportError:
        print("\n  (Install 'qrcode[pil]' to display a QR code here)\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main():
    ip  = get_local_ip()
    url = f"http://{ip}:{PORT}"

    app = web.Application()
    app.router.add_get("/",   index_handler)
    app.router.add_get("/ws", ws_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    print(f"""
╔══════════════════════════════════════════════════════╗
║          Virtual PS4 Controller  —  Server           ║
╠══════════════════════════════════════════════════════╣
║  Input backend : {BACKEND:<36}║
║  Server URL    : {url:<36}║
╠══════════════════════════════════════════════════════╣
║  📱 Open on your phone (must be on same WiFi):       ║
║                                                      ║
║    {url:<50}║
║                                                      ║
╚══════════════════════════════════════════════════════╝
  Ctrl+C to stop
""")

    print_qr(url)

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋  Server stopped.")
