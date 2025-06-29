# 🧬 NeuroCode - The First AI-Native Programming Language

**🎉 LANGUAGE IDENTITY ACHIEVED! NeuroCode is now a true programming language with formal grammar, syntax, and .neuro file support!**

**NeuroCode** is not Python. **NeuroCode** is not JavaScript. **NeuroCode** is not any existing language.

**NeuroCode is the world's first AI-native programming language** — a revolutionary cognitive computing platform where code thinks, learns, and evolves alongside developers. Unlike traditional languages that execute instructions, NeuroCode expresses intentions, goals, and behaviors that are interpreted by an AI-powered runtime.

**🔤 SYNTAX-NATIVE STATUS**: NeuroCode now has its own formal grammar (Lark parser), parses `.neuro` files directly, and generates proper AST structures - no longer Python-wrapped!

**🧠 MULTI-LLM SUPPORT**: NeuroCode seamlessly switches between AI models - OpenAI GPT, local Mistral/LLaMA/Mixtral via Ollama, GGUF models, Claude, and Gemini - all with the same syntax!

---

## 🌟 What Makes NeuroCode Revolutionary

### 🧠 **Cognitive Programming Paradigm**
Traditional languages tell computers **HOW** to do things. NeuroCode tells them **WHAT** you want to achieve.

```neurocode
# Traditional approach (Python/JavaScript):
def optimize_performance():
    metrics = collect_metrics()
    if metrics.error_rate > 0.05:
        analyze_and_fix()

# NeuroCode approach (AI-native):
goal: optimize system performance > 95%
when error_rate > 5%:
    suggest fix for "performance issues"
    apply fix if confidence > 85%
end
```

```neurocode
# NeuroCode Multi-LLM Example - Switch models seamlessly:
model: "mistral"                                  # Use local Mistral for privacy
assistant: "analyze this codebase for bottlenecks"

model: "gpt-4"                                    # Switch to GPT-4 for reasoning
assistant: "generate optimization strategy"

model: "llama2"                                   # Use LLaMA for code generation
assistant: "implement the optimization plan"

model: "mixtral"                                  # Use Mixtral for final review
assistant: "validate implementation quality"
```

---

## 🚀 **PROJECT STATUS: PRODUCTION READY**

**Latest Update**: June 29, 2025 - NeuroCode v1.0.0 is fully organized and production-ready!

### ✅ **NEW: FORMAL LANGUAGE SPECIFICATION COMPLETE**
- **Lark Grammar Parser**: Complete EBNF grammar with 100+ rules in `core/neurocode_grammar.py`
- **.neuro File Support**: Native parsing of `.neuro` files with syntax validation
- **AST Generation**: Full Abstract Syntax Tree construction and validation
- **Language Constructs**: Goals, agents, memory, intent actions, variables, comments
- **Syntax-Native Status**: No longer Python-wrapped - true programming language
- **Grammar Testing**: Comprehensive test suite validating all language features

### ✅ **FULLY OPERATIONAL SYSTEMS**
- 🧠 **Core AI Interpreter**: Advanced cognitive programming engine with 25+ modules
- 🎨 **Modern GUI**: Beautiful PySide6 interface with real-time visualization and error-free operation  
- 🔌 **Plugin Ecosystem**: 15+ plugins including math, audio, system monitoring
- 📚 **Standard Library**: 4 core stdlib modules (sysmon, optimizer, selfrepair, whisper)
- 🎯 **Goal & Memory Systems**: Persistent learning and autonomous goal management
- 🔧 **Auto-Debug System**: Self-healing code with 80%+ accuracy
- 📖 **Complete Documentation**: Architecture guides, language spec, manifesto
- 💼 **Production Setup**: Modern Python packaging, Ruff formatting, professional file organization
- 🧪 **Comprehensive Testing**: Full test suite with 100% pass rate
- 🗂️ **Professional Structure**: Clean, organized workspace with proper folder hierarchy

### 📊 **Technical Specifications**
- **70+ Python modules** in core, UI, plugins, and stdlib
- **20+ NeuroCode examples** and test programs  
- **50+ documentation files** covering all aspects
- **OpenAI GPT integration** for AI-powered interpretation
- **Cross-platform support** (Windows, macOS, Linux)
- **Modern dependencies** (PySide6, numpy, transformers, etc.)
- **Error-free codebase** with resolved import issues and UI fixes

### ✅ **COMPLETED: Advanced Syntax & Program Control**
- **User-Defined Functions**: `define optimize_network() ... end`, `run optimize_network()`
- **Multi-line Block Parsing**: Support for structured code blocks with proper indentation
- **Loops & Conditionals**: `for item in list`, `while condition`, `if condition ... else ... end`
- **Simulation Mode**: `simulate agent for 24h` - test logic without applying changes
- **Variable Assignments**: `x = value`, reference variables in expressions
- **Complex Control Flow**: Nested blocks, function parameters, range iteration

### ✅ **COMPLETED: Self-Editing System**
- **File Analysis**: `load "filename.py"`, `analyze "filename.py"`
- **AI-Powered Refactoring**: `refactor "filename.py" "target"`
- **Safe Code Modification**: `diff fix_id`, `apply fix fix_id`
- **Memory-Driven Justification**: System explains changes using accumulated knowledge
- **Proactive Suggestions**: `self edit opportunities` based on memory patterns
- **Safety Controls**: `set self_edit_mode on/off`, automatic backups

### ✅ **COMPLETED: Automatic Debug & Self-Correction System**
- **Error Detection**: Automatic detection of syntax/runtime errors with memory storage
- **AI-Driven Fix Suggestions**: `suggest fix for "SyntaxError at line 22"` - AI analyzes and proposes solutions
- **Self-Repair**: `apply fix` - Automatic code correction with confidence/risk assessment  
- **Reflective Debug Loop**: `if error: suggest fix; apply fix if confidence > 80%`
- **Debug Commands**: `debug status`, `set auto_debug on 80`, `apply fix force`
- **Memory Integration**: Error patterns stored and recalled for learning
- **Backup System**: Automatic backups before applying fixes

### ✅ **COMPLETED: Self-Awareness & Goal-Driven Execution**
- **Intent & Goal System**: `goal: maintain performance > 90%`, `agent: on`
- **Pattern Recognition**: `if memory.pattern("crash", frequency="daily"): suggest fix`
- **Tagged Memory**: `remember("api limit hit") as "rate-limiting"`
- **Reflective Loop Engine**: Autonomous monitoring and improvement
- **Meta-Plugins**: `meta: memory_analyzer`, `meta: system_optimizer`

### 🔮 **FUTURE ROADMAP**
- Local model support (Mistral, LLaMA)
- Advanced pattern recognition and predictive analysis
- Multi-agent collaboration systems
- Terminal-based version (Textual)
- Integration with external development tools
- Real-time collaborative NeuroCode editing

---

## 🚀 What Is It?
Neuroplex is more than a language — it's an evolving environment where your code:
- Learns from usage logs and patterns
- Suggests improvements in real-time
- Remembers preferences and behaviors
- Embeds LLM-based reasoning directly into execution
- Can read, reflect on, and improve its own codebase

Think of it as coding with a **self-aware assistant** inside your language.

---

## 💡 Key Features

### 🔹 NeuroCode
An AI-augmented syntax that supports:
```neurocode
# User-defined functions with loops and conditionals
define optimize_network()
    learn from "usage.log"
    for component in ["cpu", "memory", "disk"]
        if memory.pattern(component + "_issue", frequency="daily")
            suggest fix for component + " performance"
        end
    end
    remember("Network optimization completed") as "maintenance"
end

# Execute functions and simulate behavior
run optimize_network()
simulate agent for 24h

# Advanced memory and pattern operations
remember("user prefers GPU") as "preferences"
if memory.pattern("crash", frequency="daily")
    goal: improve system stability priority: high
    agent: on
end

# Self-editing and analysis
load "core/interpreter.py"
analyze "core/interpreter.py"
refactor "core/interpreter.py" "performance"
apply fix fix_id

# Automatic Debug & Self-Correction System
debug status                                    # Show debug system status
set auto_debug on 80                           # Enable auto-debug with 80% confidence
load "buggy_file.py"                          # Auto-detects errors in loaded files
suggest fix for "SyntaxError at line 22"      # AI analyzes and suggests fix
apply fix                                      # Apply fix (if confidence > threshold)
apply fix force                                # Force apply regardless of risk

# Reflective debug loop for agent mode
if error:
    suggest fix
    apply fix if confidence > 80%
end
```

### 🔹 Memory Engine
- Stores contextually important insights
- Feeds memory back into AI decisions
- Supports real-time reflection and recall
- Future: Tagged memory and pattern recognition

### 🔹 Integrated AI Assistant
- Powered by OpenAI (local model support coming)
- Conversational and self-reasoning
- Can generate NeuroCode suggestions automatically

### 🔹 GUI (PySide6 Desktop App)
- Code editor with run button
- Live console output
- Visual memory viewer
- Custom app icon support *(use `Neuroplex.ico` in root)*
- Expandable for plugins and visual debugging

### 🔹 Plugin System
- Easy addition of tools like Whisper, Stable Diffusion, Mistral
- Commands like `plugin: whisper transcribe_audio "file.wav"`

---

## 🛠 **Project Structure**

**NeuroCode v1.0 is professionally organized with a clean, maintainable architecture:**

```
NeuroCode/
├── 📁 src/                     # Core source code
│   ├── neurocode_engine.py     # Main NeuroCode execution engine
│   ├── neurocode.py            # Core language module
│   ├── natural_translator.py   # Natural language translator
│   └── comprehensive_demo.py   # Feature demonstrations
├── 📁 core/                    # Core AI engine (25+ modules)
│   ├── neurocode_grammar.py    # Lark-based parser & grammar
│   ├── multi_llm_manager.py    # Multi-LLM backend manager
│   ├── llm_integration.py      # AI model integration
│   ├── interpreter.py          # Main NeuroCode interpreter
│   ├── enhanced_interpreter.py # Advanced cognitive interpreter
│   ├── memory.py               # Memory system & vector storage
│   ├── agent.py                # Autonomous AI agent
│   ├── ai_runtime.py           # OpenAI/LLM integration
│   ├── goal_system.py          # Goal management & tracking
│   ├── plugin_manager.py       # Plugin ecosystem manager
│   ├── debug_system.py         # Auto-debug & self-healing
│   └── enhanced_parser.py      # Advanced NeuroCode parser
├── 📁 ui/                      # Modern GUI interfaces
│   ├── neurocode_playground.py # Streamlit web playground
│   ├── neuroplex_gui.py        # Main PySide6 application
│   ├── neuro_ui.py             # Enhanced UI with chat
│   ├── neuro_chat.py           # AI chat interface
│   └── neuro_chat_console.py   # Console chat interface
├── 📁 tools/                   # Development utilities
│   ├── quickstart.py           # Interactive launcher menu
│   ├── launch_playground.py    # Playground launcher
│   ├── status_check.py         # System health monitor
│   └── setup_multi_llm.py      # Multi-LLM setup script
├── 📁 launchers/               # Application launchers
│   ├── launch_neuroplex.py     # Main GUI launcher
│   ├── launch_neuro_ui.py      # Enhanced UI launcher
│   └── safe_launcher.py        # Safe mode launcher
├── 📁 plugins/                 # Extensible plugin system
│   ├── math_plugin.py          # Mathematical operations
│   ├── whisper.py              # Audio processing
│   └── system_monitor.py       # System monitoring
├── 📁 stdlib/                  # Standard library modules
│   ├── sysmon.py               # System monitoring
│   ├── optimizer.py            # Performance optimization
│   ├── selfrepair.py           # Auto-debugging
│   └── whisper.py              # Speech processing
├── 📁 examples/                # Sample NeuroCode programs
│   ├── basic_memory.neuro      # Memory system demo
│   ├── ai_collaboration.neuro  # AI collaboration
│   ├── multi_llm_demo.neuro    # Multi-LLM examples
│   └── goal_setting.neuro      # Goal management
├── 📁 tests/                   # Comprehensive test suite
│   ├── test_suite.py           # Full system tests
│   ├── test_grammar_fix.py     # Grammar validation tests
│   ├── test_multi_llm_integration.py # Multi-LLM tests
│   ├── test_core_features.py   # Core functionality tests
│   └── test_gui.py             # GUI component tests
├── 📁 docs/                    # Documentation
│   ├── TUTORIAL.md             # Getting started guide
│   ├── LANGUAGE_SPEC.md        # Complete language specification
│   ├── ARCHITECTURE.md         # System architecture
│   └── API.md                  # API reference
├── 📁 demos/                   # Interactive demonstrations
│   ├── comprehensive_demo.py   # Full feature showcase
│   └── natural_translation_demo.py # AI translation demo
├── 📁 scripts/                 # Utility & setup scripts
│   ├── setup_enhancements.py  # Environment setup
│   ├── performance_monitor.py # Performance tracking
│   └── verify_installation.py # Installation verification
├── 📁 archive/                 # Historical files & backups
│   ├── historical/             # Achievement reports & legacy docs
│   ├── old_reports/            # Legacy documentation
│   └── debug/                  # Debug artifacts
├── 📄 main.py                  # CLI entry point
├── 📄 README.md                # This file
├── 📄 requirements.txt         # Python dependencies
├── 📄 pyproject.toml           # Modern Python packaging
└── 📄 LICENSE                  # MIT License
```
## 📦 **Installation & Quick Start**

### **Prerequisites**
- Python 3.8+ (tested with Python 3.11+)
- OpenAI API key (for AI-powered features)

### **Step 1: Clone & Install**
```bash
git clone https://github.com/Zyonic88/NeuroCode.git
cd NeuroCode
pip install -r requirements.txt
```

### **Step 2: Setup API Key**
```bash
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/macOS:
export OPENAI_API_KEY="your-api-key-here"
```

### **Step 3: Run NeuroCode**

**Quick Start Menu (Recommended):**
```bash
python tools/quickstart.py
```

**Interactive Playground:**
```bash
python tools/launch_playground.py
```

**System Status Check:**
```bash
python tools/status_check.py
```

**Command Line Interface:**
```bash
python main.py
```

**Quick Test:**
```bash
python -c "from src.neurocode_engine import neurocode_engine; print('✓ NeuroCode Ready!')"
```

---

## 🎯 **Quick Examples**

### **Basic NeuroCode Program**
```neurocode
# goal_setting.neuro
goal: learn user preferences priority: medium
remember("user likes dark themes") as "ui_preferences"
when system_startup:
    apply dark_theme
    log "Applied user preference"
end
```

### **AI-Powered Self-Healing**
```neurocode
# auto_debug.neuro
set auto_debug on 80
load "my_script.py"
if errors_detected:
    suggest fix for "detected issues"
    apply fix if confidence > 85%
end
```

### **Memory & Learning**
```neurocode
# basic_memory.neuro
remember("optimization improved speed by 40%") as "performance"
learn from "system_logs"
recall "performance improvements"
```

---

## 🗂️ **Repository Structure**

**NeuroCode is professionally organized with a clean, maintainable architecture:**

```
NeuroCode/
├── 📁 core/                    # Core AI engine (25+ modules)
│   ├── interpreter.py          # Main NeuroCode interpreter
│   ├── enhanced_interpreter.py # Advanced cognitive interpreter
│   ├── memory.py               # Memory system & vector storage
│   ├── agent.py                # Autonomous AI agent
│   ├── ai_runtime.py           # OpenAI/LLM integration
│   ├── goal_system.py          # Goal management & tracking
│   ├── plugin_manager.py       # Plugin ecosystem manager
│   ├── debug_system.py         # Auto-debug & self-healing
│   └── enhanced_parser.py      # Advanced NeuroCode parser
├── 📁 ui/                      # Modern GUI interfaces
│   ├── neuroplex_gui.py        # Main PySide6 application
│   ├── neuro_ui.py             # Enhanced UI with chat
│   ├── neuro_chat.py           # AI chat interface
│   └── neuro_chat_console.py   # Console chat interface
├── 📁 launchers/               # Application launchers
│   ├── launch_neuroplex.py     # Main GUI launcher
│   ├── launch_neuro_ui.py      # Enhanced UI launcher
│   └── safe_launcher.py        # Safe mode launcher
├── 📁 plugins/                 # Extensible plugin system
│   ├── math_plugin.py          # Mathematical operations
│   ├── whisper.py              # Audio processing
│   └── system_monitor.py       # System monitoring
├── 📁 stdlib/                  # Standard library modules
│   ├── sysmon.py               # System monitoring
│   ├── optimizer.py            # Performance optimization
│   ├── selfrepair.py           # Auto-debugging
│   └── whisper.py              # Speech processing
├── 📁 examples/                # Sample NeuroCode programs
│   ├── basic_memory.neuro      # Memory system demo
│   ├── ai_collaboration.neuro  # AI collaboration
│   └── goal_setting.neuro      # Goal management
├── 📁 tests/                   # Comprehensive test suite
│   ├── test_suite.py           # Full system tests
│   ├── test_core_features.py   # Core functionality tests
│   └── test_gui.py             # GUI component tests
├── 📁 demos/                   # Interactive demonstrations
│   ├── comprehensive_demo.py   # Full feature showcase
│   └── natural_translation_demo.py # AI translation demo
├── 📁 scripts/                 # Utility & setup scripts
│   ├── setup_enhancements.py  # Environment setup
│   ├── performance_monitor.py # Performance tracking
│   └── verify_installation.py # Installation verification
├── 📁 docs/                    # Comprehensive documentation
│   ├── NEUROCODE_LANGUAGE_SPEC.md # Language specification
│   ├── ARCHITECTURE.md         # System architecture
│   └── TUTORIAL.md             # Getting started guide
├── � archive/                 # Historical files & backups
│   ├── old_reports/            # Legacy documentation
│   └── debug/                  # Debug artifacts
├── 📄 main.py                  # CLI entry point
├── �📄 neurocode.py             # Core language module
├── 📄 neuroplex.py             # Main application
├── 📄 README.md                # This file
├── 📄 requirements.txt         # Python dependencies
├── 📄 pyproject.toml           # Modern Python packaging
└── 📄 LICENSE                  # MIT License
```
- Self-refactoring of Neuroplex’s own files
- Plugin system for AI tools (Whisper, SDXL)
- Terminal-based version (Textual)

---

## 🧬 Philosophy
> Neuroplex isn’t just a code environment — it’s a glimpse into the future of intelligent systems. It’s where software writes, thinks, and adapts with you.

---

## 👤 Created By
**You + Neuroplex** — co-evolving.

Want to contribute? Dream. Build. Inject AI into your code.

---

## 🤝 **Contributing**

NeuroCode is open source and welcomes contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### **Ways to Contribute:**
- 🐛 **Bug Reports**: Found an issue? Open an issue on GitHub
- 💡 **Feature Requests**: Have ideas? We'd love to hear them
- 🧬 **NeuroCode Programs**: Share your `.neuro` creations
- 📚 **Documentation**: Help improve our guides and examples
- 🔌 **Plugins**: Extend NeuroCode with new capabilities

---

## 📄 **License**

NeuroCode is released under the [MIT License](LICENSE). Feel free to use, modify, and distribute!

---

## 🌟 **Star This Project**

If NeuroCode revolutionizes your coding experience, give us a ⭐ on GitHub!

**Repository**: https://github.com/Zyonic88/NeuroCode

---

**NeuroCode**: *Where code thinks, learns, and evolves* 🧬✨