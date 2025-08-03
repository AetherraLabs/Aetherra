# 🚀 VS Code Extensions Installation Guide
## Multiple Methods to Install Essential Extensions

Since the automated script had issues finding VS Code in PATH, here are alternative installation methods:

## 📋 **ESSENTIAL EXTENSIONS TO INSTALL**

**Must-Have Extensions:**
- `ms-python.python` - Python language support
- `ms-python.vscode-pylance` - Advanced IntelliSense
- `github.copilot` - AI coding assistant
- `eamodio.gitlens` - Enhanced Git integration
- `ms-toolsai.jupyter` - Jupyter notebook support
- `ms-python.black-formatter` - Code formatting
- `dracula-theme.theme-dracula` - Beautiful dark theme
- `vscode-icons-team.vscode-icons` - File icons

**Recommended Extensions:**
- `github.copilot-chat` - AI chat integration
- `continue.continue` - Local AI assistant
- `charliermarsh.ruff` - Fast Python linting
- `yzhang.markdown-all-in-one` - Markdown support
- `gruntfuggly.todo-tree` - TODO tracking

---

## [TOOL] **METHOD 1: VS Code UI Installation (Recommended)**

1. **Open VS Code in this project:**
   - Navigate to your Aetherra folder
   - Right-click → "Open with Code" (if available)
   - Or open VS Code and use File → Open Folder

2. **Extensions will be automatically recommended:**
   - VS Code will show a notification about recommended extensions
   - Click "Install All" or "Show Recommendations"
   - The extensions are already configured in `.vscode/extensions.json`

3. **Manual installation via Extensions panel:**
   - Press `Ctrl+Shift+X` to open Extensions
   - Search for each extension by name:
     - Search "Python" → Install "Python" by Microsoft
     - Search "Pylance" → Install "Pylance" by Microsoft
     - Search "GitHub Copilot" → Install "GitHub Copilot"
     - Search "GitLens" → Install "GitLens — Git supercharged"
     - Search "Jupyter" → Install "Jupyter" by Microsoft
     - Search "Black Formatter" → Install "Black Formatter" by Microsoft
     - Search "Dracula" → Install "Dracula Official"
     - Search "vscode-icons" → Install "vscode-icons"
     - Search "Copilot Chat" → Install "GitHub Copilot Chat"
     - Search "Continue" → Install "Continue"
     - Search "Ruff" → Install "Ruff"
     - Search "Markdown All in One" → Install "Markdown All in One"
     - Search "TODO Tree" → Install "Todo Tree"

---

## [TOOL] **METHOD 2: Command Line Installation**

If VS Code CLI is available, run these commands:

```bash
# Essential Extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension github.copilot
code --install-extension eamodio.gitlens
code --install-extension ms-toolsai.jupyter
code --install-extension ms-python.black-formatter
code --install-extension dracula-theme.theme-dracula
code --install-extension vscode-icons-team.vscode-icons

# Recommended Extensions
code --install-extension github.copilot-chat
code --install-extension continue.continue
code --install-extension charliermarsh.ruff
code --install-extension yzhang.markdown-all-in-one
code --install-extension gruntfuggly.todo-tree
```

---

## [TOOL] **METHOD 3: Fix VS Code PATH (Advanced)**

To enable the `code` command in terminal:

1. **Find VS Code installation:**
   - Usually located at: `C:\Users\[Username]\AppData\Local\Programs\Microsoft VS Code\bin`
   - Or: `C:\Program Files\Microsoft VS Code\bin`

2. **Add to PATH:**
   - Open Windows Settings → System → About → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add the VS Code bin directory
   - Restart terminal/PowerShell

---

## ✅ **VERIFICATION STEPS**

After installing extensions:

1. **Restart VS Code**
2. **Open this Aetherra project folder**
3. **Check that extensions are working:**
   - Python files show syntax highlighting
   - IntelliSense works (hover over variables)
   - GitHub Copilot suggests code (if signed in)
   - GitLens shows Git blame information
   - Dracula theme is applied

---

## 🎯 **IMMEDIATE NEXT STEPS**

1. **Install extensions using Method 1 (VS Code UI)**
2. **Sign in to GitHub Copilot:**
   - Press `Ctrl+Shift+P`
   - Type "GitHub Copilot: Sign In"
   - Follow authentication steps

3. **Configure Python interpreter:**
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose your Python installation

4. **Test Aetherra functionality:**
   ```bash
   python check_qt.py
   ```

---

## 🚀 **YOU'RE ALL SET!**

Once the extensions are installed, your Aetherra development environment will have:

✨ **AI-Powered Development** - Copilot + Continue.dev
[TOOL] **Professional Tooling** - Linting, formatting, debugging
🎨 **Beautiful Interface** - Dracula theme + icons
🧬 **Aetherra Optimized** - Custom settings for AI-native programming

The `.vscode/` folder already contains all the optimized settings - you just need the extensions installed!
