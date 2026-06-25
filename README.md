🎮 Wireless Virtual Xbox Controller & Smooth Trackpad
Transform your smartphone into a low-latency, wireless Xbox controller and precision trackpad for your PC.

This project uses a lightweight Python server to accept inputs over your local Wi-Fi network and injects them directly into Windows using the ViGEmBus kernel driver. Games see your phone exactly as a physical Xbox 360 controller! No mobile apps to install—everything runs natively inside your phone's web browser.

✨ Features
True Gamepad Emulation (Windows): Emulates a genuine hardware Xbox 360 controller. Games like FIFA, Rocket League, Cyberpunk, and emulators will see it instantly without any extra key-mapping software.

Dual-Mode System Architecture: * Gamepad Mode: Provides joysticks, triggers (LT/RT), bumpers (LB/RB), D-pad, and face buttons (A/B/X/Y).

Precision Trackpad Mode: Controls your laptop mouse cursor with premium, sub-pixel micro-precision algorithms and kinetic velocity acceleration.

Built-in Scroll Strip: A dedicated tactile strip allows you to scroll vertically through pages and menus effortlessly.

Zero Mobile App Installation: Uses modern WebSockets. Simply scan the generated QR code to open the controller interface on any Android or iOS device instantly.

Persistent Screen Wake-Lock: Includes background script triggers that prevent your phone's screen from dimming or sleeping mid-game.

Automatic OS Fallback: If running on macOS/Linux (or on Windows without the driver installed), the script gracefully steps back to mouse/keyboard simulation mode using pynput.

⚠️ Crucial Rules for New Users (Read Before Setup!)
Most setup issues happen because files are in the wrong place, or the command prompt is looking at the wrong folder. Please read these rules carefully:

The Same-Folder Rule: The files server.py and controller.html MUST be kept inside the exact same folder. If they are separated, your laptop will give a 404 Error when your phone tries to connect.

The Terminal Location Rule: When you open your Command Prompt (cmd) or Terminal, you MUST navigate (cd) into the folder where your files are located before running the python command.

Correct Folder Architecture Example:
Plaintext
📂 MyProjectFolder/
   ├── server.py          <-- The backend server script
   └── controller.html    <-- The user interface loaded by your phone
🚀 Step-by-Step Installation
Step 1: Install the Windows Controller Driver (ViGEmBus)
To let Python simulate a real controller, Windows needs a specific driver.

Go to the official driver repository: ViGEmBus Releases

Download and run the ViGEmBus_Setup.msi file.

Complete the setup wizard and restart your PC to finish installation.

Step 2: Open Terminal in the Correct Location
Open the folder where you saved server.py and controller.html.

Click the folder's address bar at the top of your Windows File Explorer window, type cmd, and hit Enter. This opens the command prompt inside the correct directory automatically.

Step 3: Install Python Dependencies
Paste this command into your terminal and press Enter to install the network and controller packages:

Bash
pip install aiohttp pynput qrcode[pil] vgamepad
🎮 How to Connect and Play
1. Launch the Server
Inside your correctly located terminal window, run:

Bash
python server.py
If configured properly, the window will read: ✅ High-Precision Mouse Engine Initialized and generate a large visual QR Code right in your text window.

2. Connect Your Phone
Make sure your PC and your phone are connected to the exact same Wi-Fi network.

Open your smartphone camera and scan the QR code (or type the http://192.168.x.x:7070 address shown in your terminal into Chrome or Safari).

The interface will instantly connect, and the status bar will light up green!

💡 Pro-Tip for Mobile: Once the page opens on your mobile device, tap the browser settings button and select "Add to Home Screen". This installs the layout as a web app, making it completely full-screen and hiding the standard URL search bar for a much better gaming experience!

🛠️ Troubleshooting Common Mistakes
Error: controller.html missing! or 404 Status:

Reason: Your terminal is running server.py from a different path, or you didn't keep both files in the same folder. Close the terminal, go into the folder containing both files, type cmd into the folder's address bar, and start the script again.

The phone screen remains stuck on "OFFLINE":

Reason: Your Windows Firewall is blocking the phone. When you first ran the script, Windows should have asked for permission. Make sure your Wi-Fi network profile on Windows is set to Private instead of Public so devices can discover your laptop.

Inputs work on my desktop, but freeze when I open a specific game:

Reason: Competitive games using heavy kernel-level anti-cheats (like Riot Vanguard inside Valorant, or Ricochet inside Call of Duty) systematically block all virtual and software-injected inputs to prevent competitive cheating. This project is meant for single-player games, emulators, sandbox titles, and remote control access.