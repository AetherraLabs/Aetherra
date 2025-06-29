# 🚀 NeuroCode Installation & Quick Start Guide

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **Git** for cloning the repository
- **Virtual environment** (recommended)

## ⚡ Quick Installation

### Option 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/neurocode.git
cd neurocode

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Download ZIP

1. Download the ZIP file from GitHub
2. Extract to your desired location
3. Follow the virtual environment steps above

## 🧪 Verify Installation

Run the verification script to ensure everything is working:

```bash
python test_core_features.py
```

You should see output like:
```
✅ NeuroCode core interpreter: Working
✅ Memory system: Operational
✅ Function system: Ready
✅ Agent system: Active
```

## 🎨 Launch the GUI

Start the NeuroCode GUI interface:

```bash
python ui/neuroplex_gui.py
```

Or use the launcher:

```bash
python simple_gui_launcher.py
```

## 📝 Your First NeuroCode Program

Create a file called `hello.neuro`:

```neurocode
# Your first AI-native program
remember("Hello, NeuroCode!") as "greeting"
recall tag: "greeting"

# Set a goal for the AI
goal: learn user preferences priority: medium
agent: on

# AI-powered optimization
optimize for "user_experience"
```

Run it with:

```bash
python main.py hello.neuro
```

## 🧠 Interactive Mode

Start the NeuroCode interpreter in interactive mode:

```bash
python main.py
```

Try these commands:
```neurocode
remember("AI is the future") as "philosophy"
recall tag: "philosophy"
goal: improve coding efficiency
agent: on
suggest next actions
```

## 📚 Example Programs

Check out the example NeuroCode programs:

- `examples/basic_memory.neuro` - Memory system basics
- `examples/goal_setting.neuro` - AI goal management
- `examples/self_editing.neuro` - Code self-modification
- `examples/pattern_recognition.neuro` - Learning patterns

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file for AI API configuration:

```env
# Optional: For enhanced AI features
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
```

### VS Code Integration

Install the recommended VS Code extensions:

1. Open the project in VS Code
2. Accept the prompt to install recommended extensions
3. Extensions will be installed automatically

## 🐛 Troubleshooting

### Common Issues

**Import Error: No module named 'PySide6'**
```bash
pip install PySide6
```

**Permission denied on scripts**
```bash
# On Windows, run as administrator
# On macOS/Linux:
chmod +x venv/bin/activate
```

**GUI won't start**
```bash
# Install additional GUI dependencies
pip install PySide6 qtawesome
```

### Getting Help

- **Documentation**: Check the `docs/` folder
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Examples**: Look in the `examples/` directory

## 🎯 Next Steps

1. **Read the Documentation**: Check out `NEUROCODE_LANGUAGE_SPEC.md`
2. **Try Examples**: Run the example programs
3. **Join the Community**: Participate in GitHub Discussions
4. **Contribute**: See `CONTRIBUTING.md` for how to help

## 🌟 Advanced Features

### Plugin Development

Create custom plugins in the `plugins/` directory. See the plugin development guide.

### Self-Editing Mode

Enable code self-modification (use with caution):

```neurocode
set self_edit_mode on
load "my_program.py"
analyze "my_program.py"
refactor "my_program.py" "performance optimization"
```

### AI Agent Mode

Let NeuroCode autonomously improve your code:

```neurocode
goal: optimize performance > 95%
agent: on
autonomous monitoring
```

---

**Welcome to the future of programming! 🧬**

Start coding with intentions, not instructions. Let NeuroCode think, learn, and evolve with you!
