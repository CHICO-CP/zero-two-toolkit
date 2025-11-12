# 💠 ZERO TWO - APKs Toolkit for Termux

<div align="center">

![ZERO TWO Logo](https://raw.githubusercontent.com/CHICO-CP/zero-two-toolkit/main/img/zero_two.png)

A powerful, feature-rich Android APK manipulation toolkit optimized for **Termux**

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Termux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-3.0.0-orange.svg)

</div>

---

## 🚀 Features

### 🧩 Core Functionality

- 🔄 **APKS to APK Conversion** – Extract and convert Android App Bundles (.apks) to installable APK files  
- 📁 **Batch Processing** – Convert multiple `.apks` files in a directory automatically  
- 🔍 **APK Decompilation** – Full APK decompilation using apktool with real-time progress  
- 🏗️ **APK Rebuilding** – Recompile modified APK projects back to installable packages  
- 🛡️ **APK Signing** – Automatic signing with `apksigner` (primary) and `jarsigner` (fallback)  
- 📊 **APK Analysis** – Extract package info, permissions, and manifest data  

### ⚙️ Advanced Features

- 🎨 **Beautiful TUI** – Colorful, responsive terminal interface with ANSI colors  
- ⚡ **Auto Mode** – Smart directory scanning and automatic processing  
- 🔧 **Dependency Management** – Automatic tool installation and verification  
- 🔄 **Self-Updating System** – Built-in update system with one-click upgrades  
- 📝 **Comprehensive Logging** – Detailed operation logs with timestamps  
- 🎯 **CLI & Interactive Modes** – Both command-line and interactive menu interfaces  

---

## 📦 Installation

### 🧱 Prerequisites

- Termux (Android terminal emulator)  
- Python 3.7+  
- Basic Termux packages  

### ⚡ Quick Install

```bash
# Clone the repository
git clone https://github.com/CHICO-CP/zero-two-toolkit.git
cd zero-two-toolkit

# Make script executable
chmod +x zero_two.py

# Run the tool
python zero_two.py
```

### 🧩 Automatic Dependency Installation

The tool can automatically install required dependencies:

```bash
# Run the tool and select option 9 "Install missing dependencies"
python zero_two.py
```

---

## 🛠️ Usage

### 💻 Interactive Mode (Recommended)

```bash
python zero_two.py
```

Navigate through the beautiful menu interface to access all features.

### 🧠 Command Line Mode

```bash
# Convert APKS to APK
python zero_two.py --convert app.bundle.apks

# Decompile APK
python zero_two.py --decompile app.apk

# Rebuild APK from decompiled directory
python zero_two.py --rebuild ./app_decompiled

# Sign APK
python zero_two.py --sign app.apk

# Show APK information
python zero_two.py --info app.apk

# Check for updates
python zero_two.py --update

# Headless mode (no prompts)
python zero_two.py --headless --convert app.bundle.apks
```

---

## 📋 Menu Options

| #  | Option Description |
|----|--------------------|
| 1  | Convert single `.apks` → `.apk` - Extract main APK from bundle |
| 2  | Process directory (batch `.apks`) - Convert all `.apks` files in a folder |
| 3  | Decompile APK - Full decompilation with apktool |
| 4  | Rebuild APK - Recompile modified project |
| 5  | Sign APK - Sign APK with debug or custom certificate |
| 6  | Show APK Info - Display package info and permissions |
| 7  | Check for Updates - Auto-update to latest version |
| 8  | Auto Mode - Smart scan and process directory |
| 9  | Install Dependencies - Auto-install required tools |
| 10 | System Info & Credits - Show environment and developer info |
| 11 | Exit - Close the application |

---

## 🔧 Required Tools

The toolkit automatically detects and can install these dependencies:

- apktool – APK decompilation and rebuilding  
- openjdk-17 – Java runtime for Android tools  
- apksigner – APK signing (Android SDK)  
- zipalign – APK optimization  
- aapt/aapt2 – Android Asset Packaging Tool  
- curl – Network operations and updates  

---

## 🎯 Use Cases

### 👨‍💻 For Developers
- Analyze APK structure and resources  
- Debug and modify existing applications  
- Learn Android app architecture  
- Extract resources from APK files  

### 🧠 For Security Researchers
- Reverse engineer Android applications  
- Analyze app permissions and capabilities  
- Perform security assessment and penetration testing  

### 💡 For Enthusiasts
- Convert APKS bundles for installation  
- Customize APK files (themes, icons, etc.)  
- Educational and learning purposes  

---

## 📁 Project Structure

```
zero-two-toolkit/
├── zero_two.py             # Main toolkit script
├── img/
│   └── zero_two.png        # Project logo
├── logs/
│   └── conversion_log.txt  # Operation logs
└── README.md               # This file
```

---

## 🔄 Update System

ZERO TWO includes a sophisticated **self-update mechanism**:

- Automatic version checking against GitHub releases  
- Secure download with progress indicators  
- Backup creation before updates  
- Multiple download methods (`requests` + `curl` fallback)  
- One-click updates from within the application  

To update manually:

```bash
python zero_two.py --update
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|----------|-----------|
| **apktool not found** | Run option 9 to install dependencies automatically, or manually: `pkg install apktool` |
| **Storage permission denied** | Run: `termux-setup-storage` |
| **Cannot decompile large APK** | Be patient – large apps can take 5+ minutes. Ensure sufficient storage space. |
| **Signing failed** | Tool will automatically create debug keystore. Manual signing also supported. |

---

## 🤝 Contributing

We welcome contributions! 💪  
Please feel free to submit pull requests, report bugs, or suggest new features.

1. Fork the repository  
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)  
4. Push to the branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request  

---

## 📄 License

This project is licensed under the **MIT License** — see the LICENSE file for details.

---

## 👨‍💻 Developer

**Ghost Developer**

- GitHub: [@CHICO-CP](https://github.com/CHICO-CP)  
- Telegram: [@GhostDeve](https://t.me/GhostDeve)

---

## 🙏 Acknowledgments

- **APKTool** team for the amazing decompilation tool  
- **Termux** community for the excellent Android terminal environment  
- **Python** community for the robust ecosystem  

---

<div align="center">

⭐ **If you find this tool useful, please give it a star on GitHub!**  
Made with ❤️ for the Android development and security community.

</div>

---

## 📞 Support

If you need help or have questions:

1. Check the troubleshooting section above  
2. Open an issue on GitHub  
3. Contact the developer via Telegram  
