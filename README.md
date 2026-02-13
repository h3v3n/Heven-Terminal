# 🚀 H3V3N TERMINAL v12.6

A professional, high-performance terminal emulator for Linux, built with Python and GTK+ 3. It features a unique blend of "eye-candy" aesthetics and essential developer tools.

## ✨ Key Features
* **Dynamic RGB Border:** Smooth, animated color transitions around the window.
* **Frosted Glass Support:** Optimized for background blur effects.
* **Integrated System HUD:** Real-time monitoring of CPU and RAM usage.
* **Advanced Theme Engine:** 18 built-in color profiles (Cyberpunk, Matrix, Dracula, Nord, and more).
* **Clean Context Menu:** Fast access to Copy, Paste, and a dedicated "Clear Terminal" function.
* **Highly Customizable:** Adjustable transparency, fonts, and UI elements via an intuitive settings panel.

---

## 📦 Installation

To run H3V3N Terminal, you need to install the following system dependencies (example for Ubuntu/Debian):

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91 python3-psutil


🏃 How to Run
Download the my_terminal.py file.

Grant execution permissions:
chmod +x my_terminal.py


Launch the terminal:
./my_terminal.py


🕯️ Enabling Background Blur (Glass Effect)
This terminal is designed to look best with a blurred background. Since GTK 3 does not handle blur natively on most window managers, you should use the Blur my Shell extension if you are on GNOME:

Install the Blur my Shell extension.

Open the extension settings.

Navigate to the Applications tab.

Add H3V3N Terminal to the list or ensure "Blur" is active for GTK applications.


⌨️ Shortcuts & InteractionShortcutActionCtrl + Shift + CCopy Selected TextCtrl + Shift + VPaste from ClipboardRight ClickContext Menu (Copy, Paste, 🧹 Clear)New Tab ButtonOpen a new terminal instance


⚙️ Configuration
Your preferences (theme, transparency, font, etc.) are automatically saved to:
~/.config/h3v3n-terminal/master_config.json


🛠️ Built With
Python 3

GTK 3 - User Interface

VTE - Terminal Emulation Engine

Psutil - System Monitoring


📝 License
This project is open-source and available under the MIT License.
