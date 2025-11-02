# Aetherra AI Operating System - Windows Distribution

**Version:** 1.0.0-beta.1
**Platform:** Windows 10/11 (64-bit)
**Build Date:** October 31, 2025

---

## 🚀 Quick Start

### Step 1: Extract
Extract this **entire folder** to your desired location.
⚠️ **Do not extract just the .exe file!** The `_internal` folder contains required dependencies.

### Step 2: Launch
**Double-click** `START_AETHERRA.bat`

OR open Command Prompt in this folder and run:
```cmd
AetherraOS.exe --mode full --gui
```

### Step 3: Keep Window Open
⚠️ **IMPORTANT:** Keep the console window open while using Aetherra OS!
- The console shows system status and logs
- Closing it will stop the entire system
- Press `Ctrl+C` to shutdown gracefully

### Step 4: Access
Once started, access the system at:
- **Hub API:** http://localhost:3012
- **Lyrixa UI:** http://localhost:5173 (requires separate frontend)

---

## 📁 Package Contents

```
AetherraOS-1.0.0-beta.1-Windows-x64/
├── AetherraOS.exe              Main executable (79 MB)
├── _internal/                  Dependencies (1.27 GB) - REQUIRED!
├── START_AETHERRA.bat          Quick start launcher
├── START_AETHERRA.ps1          PowerShell launcher (advanced)
├── INSTALLATION.txt            Detailed installation guide
├── README.md                   This file
├── LICENSE                     Apache 2.0 license
├── CHANGELOG.md                Version history
├── config.json                 Configuration file
├── .env.example                Environment template
└── (documentation files)
```

---

## ⚙️ System Requirements

- **OS:** Windows 10 or Windows 11 (64-bit)
- **RAM:** 4 GB minimum (8 GB recommended)
- **Disk Space:** 2 GB free
- **Internet:** Required for AI features
- **Ports:** 3012 (Hub API), 5173 (Lyrixa UI if used)

---

## 🎯 Launch Options

### Launch Modes
```cmd
AetherraOS.exe --mode full      # Full AI Operating System (default)
AetherraOS.exe --mode minimal   # Minimal systems only
AetherraOS.exe --mode test      # Test mode with mocks
```

### Additional Options
```cmd
--gui           Enable GUI interface
--no-gui        Disable GUI (terminal only)
--verbose       Verbose logging
--boot-menu     Show interactive boot menu
--help          Show all options
```

---

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:
- API keys for AI services
- Network settings
- Security options

### Configuration File
Edit `config.json` to customize:
- Service endpoints
- Module settings
- Performance tuning

---

## 🐛 Troubleshooting

### Executable Won't Start
1. **Run as Administrator** - Right-click AetherraOS.exe → "Run as administrator"
2. **Check Windows Defender** - Add folder to exclusions if needed
3. **Verify all files extracted** - Make sure `_internal` folder is present
4. **Check logs** - Look in `aetherra_os.log` for errors

### Console Closes Immediately
- This is normal if there's an error during startup
- Look at `aetherra_os.log` for the error message
- Try running with `--verbose` flag to see more output

### "Missing DLL" Errors
- Make sure you extracted the **entire folder**, not just the `.exe`
- The `_internal` folder must be in the same directory as `AetherraOS.exe`

### Port Already in Use
- Another process is using port 3012
- Stop other services or change port in config.json

### No GUI Appears
- Aetherra OS runs in the console window
- The Lyrixa GUI is a separate web application
- Access Hub API at http://localhost:3012
- For Lyrixa UI, you need to run the frontend separately

---

## 📖 Documentation

Included documentation:
- **INSTALLATION.txt** - Detailed installation steps
- **CHANGELOG.md** - Version history and changes
- **PRE_PACK_VALIDATION_GUIDE.md** - System validation procedures
- **PRE_PACK_QUICK_REFERENCE.md** - Quick reference card

---

## 🌐 Online Resources

- **Repository:** https://github.com/AetherraLabs/Aetherra
- **Issues:** https://github.com/AetherraLabs/Aetherra/issues
- **Documentation:** See included markdown files

---

## 📜 License

Apache License 2.0 - See LICENSE file for details

Copyright (c) 2024-2025 Aetherra Labs

---

## ⚠️ Important Notes

### File Organization
- **NEVER** separate the `.exe` from the `_internal` folder
- They are a matched pair and must stay together
- Think of it as a portable application bundle

### Running the System
- The console window is your control center
- It shows real-time system status
- Don't close it while the system is running
- Use `Ctrl+C` for graceful shutdown

### First Launch
- Initial startup takes 30-60 seconds
- Watch the console for system initialization
- Wait for "AETHERRA AI OPERATING SYSTEM IS NOW ONLINE!" message

---

## 💡 Tips

- **Run in full-screen console** for better log visibility
- **Check the logs** (`aetherra_os.log`) if something goes wrong
- **Use --verbose** during troubleshooting
- **Keep backups** of your config files before updating

---

**Questions?** Open an issue at https://github.com/AetherraLabs/Aetherra/issues

**Enjoy Aetherra OS!** 🎉
