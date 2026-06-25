# 🎮 Wireless Virtual Xbox Controller & Smooth Trackpad

Transform your smartphone into a low-latency, wireless Xbox controller and precision trackpad for your PC.

This project uses a lightweight **Python server** to accept inputs over your local Wi-Fi network and injects them directly into Windows using the **ViGEmBus** kernel driver. Games see your phone exactly as a physical Xbox 360 controller! No mobile apps to install—everything runs natively inside your phone's web browser.

---

## ✨ Features

* **True Gamepad Emulation (Windows):** Emulates a genuine hardware Xbox 360 controller. Games like FIFA, Rocket League, Cyberpunk, and emulators will see it instantly without any extra key-mapping software.
* **Dual-Mode System Architecture:** * **Gamepad Mode:** Provides joysticks, triggers (LT/RT), bumpers (LB/RB), D-pad, and face buttons (A/B/X/Y).
  * **Precision Trackpad Mode:** Controls your laptop mouse cursor with premium, sub-pixel micro-precision algorithms and kinetic velocity acceleration.
* **Zero Mobile App Installation:** Uses modern WebSockets. Simply scan the generated QR code to open the controller interface on any Android or iOS device instantly.
* **Persistent Screen Wake-Lock:** Includes background script triggers that prevent your phone's screen from dimming or sleeping mid-game.
* **Automatic OS Fallback:** If running on macOS/Linux (or on Windows without the driver installed), the script gracefully steps back to mouse/keyboard simulation mode using `pynput`.

---

## ⚠️ Crucial Rules for New Users (Read Before Setup!)

Most setup issues happen because files are in the wrong place, or the command prompt is looking at the wrong folder. Please read these rules carefully:

* **The Same-Folder Rule:** The files `server.py` and `controller.html` **MUST be kept inside the exact same folder**. If they are separated, your laptop will give a `404 Error` when your phone tries to connect.
* **The Terminal Location Rule:** When you open your Command Prompt (`cmd`) or Terminal, you **MUST navigate (`cd`) into the folder where your files are located** before running the python command.

### Correct Folder Architecture Example:
```text
📂 MyProjectFolder/
   ├── server.py          <-- The backend server script
   └── controller.html    <-- The user interface loaded by your phone
```
## 🚀 Step-by-Step Installation

### Step 1: Install the Windows Controller Driver (ViGEmBus)
To let Python simulate a real hardware controller, Windows needs a specific driver.
1. Go to the official driver repository: **[ViGEmBus Releases](https://github.com/ViGEm/ViGEmBus/releases/latest)**
2. Download and run the `ViGEmBus_Setup.msi` file.
3. Complete the setup wizard installer and **restart your PC** to finish the driver setup.

---

### Step 2: Open Terminal in the Correct Location
1. Open the folder on your laptop where you saved both `server.py` and `controller.html`.
2. Click the folder's address path bar at the very top of your Windows File Explorer window.
3. Type `cmd` directly into that top bar and hit **Enter**. This forces the command prompt to open inside your project directory automatically.

---

### Step 3: Install Python Dependencies
Paste this exact command into your command prompt window and press **Enter** to install the network and controller packages:

```bash
pip install aiohttp pynput qrcode[pil] vgamepad

