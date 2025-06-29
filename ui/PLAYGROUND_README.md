# 🧬 NeuroCode Playground

**Interactive web environment for the NeuroCode programming language**

The NeuroCode Playground provides an instant, no-installation-required way to learn, experiment with, and share NeuroCode programs. Experience NeuroCode's unique syntax and powerful standard library through an intuitive web interface.

## 🚀 Quick Start

### Option 1: Simple Launch
```bash
python launch_playground.py
```

### Option 2: Direct Streamlit
```bash
streamlit run neurocode_playground.py
```

The playground will automatically open in your web browser at `http://localhost:8501`

## 🎮 Features

### 🎯 **Quick Start Page**
- **Introduction to NeuroCode**: Learn the language basics
- **Interactive Examples**: Run sample code instantly
- **Live Metrics**: See NeuroCode's status and capabilities
- **First Program**: Try your first NeuroCode script

### 📚 **Standard Library Explorer**
- **7 Core Plugins**: Explore sysmon, coretools, executor, reflector, optimizer, selfrepair, whisper
- **Plugin Details**: See available actions and descriptions
- **Live Testing**: Test plugin functions interactively
- **Real-time Results**: See plugin execution results

### 🎓 **Interactive Tutorials**
1. **Basic Syntax**: Goals, agents, variables, and memory
2. **Memory Operations**: Store, recall, and manage data
3. **Plugin Usage**: Harness the standard library power
4. **System Monitoring**: Build real monitoring scripts
5. **File Processing**: Create data processing pipelines
6. **AI Behavior Analysis**: Self-reflection and pattern analysis

### 🧪 **Code Editor**
- **Syntax Highlighting**: NeuroCode syntax support
- **Live Validation**: Real-time syntax checking
- **Code Execution**: Run NeuroCode programs safely
- **Save & Share**: Store your examples (simulated)
- **Quick Reference**: Built-in syntax guide

### 📖 **Example Gallery**
- **System Health Monitor**: Complete monitoring solution
- **Automated File Organizer**: Smart file management
- **AI Behavior Tracker**: Self-analysis and improvement
- **Performance Optimizer**: System tuning automation

### ℹ️ **About & Documentation**
- **Language Overview**: NeuroCode's design and philosophy
- **Technical Specs**: Grammar, plugins, and architecture
- **Use Cases**: Real-world applications
- **Evolution Story**: From framework to true language

## 🛠️ Technical Requirements

### Dependencies
- **Python 3.7+**
- **Streamlit 1.28+**
- **Lark 1.1.7+** (for NeuroCode parsing)

### Installation
```bash
pip install streamlit lark
```

Or use the provided requirements:
```bash
pip install -r playground_requirements.txt
```

## 🎨 Playground Architecture

### Frontend (Streamlit)
- **Modern UI**: Clean, responsive web interface
- **Interactive Components**: Code editors, examples, tutorials
- **Real-time Feedback**: Live syntax validation and execution
- **Multi-page Navigation**: Organized learning experience

### Backend Integration
- **NeuroCode Parser**: Real syntax validation using Lark grammar
- **Standard Library**: Live plugin execution and testing
- **Safe Execution**: Sandboxed environment for code testing
- **Error Handling**: Graceful error reporting and recovery

### Security & Safety
- **Simulated Execution**: Safe code testing without system access
- **Read-only Operations**: No file system modifications
- **Plugin Sandboxing**: Controlled plugin function testing
- **Error Isolation**: Contained error handling

## 🌟 Key Benefits

### 📈 **Learning Acceleration**
- **Instant Access**: No installation or setup required
- **Interactive Learning**: Hands-on experience with immediate feedback
- **Progressive Tutorials**: Step-by-step skill building
- **Real Examples**: Practical, working NeuroCode programs

### 🔄 **Development Workflow**
- **Rapid Prototyping**: Test NeuroCode concepts quickly
- **Syntax Validation**: Immediate grammar checking
- **Plugin Testing**: Explore standard library capabilities
- **Code Sharing**: Easy example distribution

### 🎯 **User Experience**
- **Browser-Based**: Works on any device with a web browser
- **No Setup**: Zero configuration required
- **Intuitive Interface**: Clean, modern design
- **Comprehensive**: All NeuroCode features accessible

## 🚀 Usage Examples

### Basic NeuroCode Program
```neuro
# System monitoring with NeuroCode
goal: "monitor_system" priority: high
agent: "sys_monitor"

# Check system health
status = plugin("sysmon.check_health")
files = plugin("coretools.list_files")

# Remember results
remember("monitoring_complete") as "session_data"
```

### Standard Library Usage
```neuro
# File processing pipeline
goal: "process_data" priority: medium
agent: "data_processor"

# Read, transform, and save data
data = plugin("coretools.read_csv", "input.csv")
processed = plugin("coretools.transform_data", data)
plugin("coretools.write_json", "output.json", processed)
```

### AI Behavior Analysis
```neuro
# Self-reflection and improvement
goal: "analyze_behavior" priority: high
agent: "self_analyst"

# Analyze patterns and performance
patterns = plugin("reflector.analyze_behavior")
performance = plugin("reflector.reflect_on_performance")

# Apply improvements
if performance.efficiency < 0.8:
    plugin("optimizer.suggest_optimizations")
```

## 🎉 Playground Impact

The NeuroCode Playground transforms how people interact with NeuroCode:

### ✅ **Instant Access**
- No installation barriers
- Web-based convenience
- Cross-platform compatibility

### ✅ **Learning Acceleration**
- Interactive tutorials
- Immediate feedback
- Real working examples

### ✅ **Community Building**
- Shareable code examples
- Easy collaboration
- Accessible to all skill levels

### ✅ **Language Adoption**
- Lower entry barriers
- Professional presentation
- Real-world demonstration

---

🧬 **The NeuroCode Playground makes NeuroCode accessible to everyone, instantly!**

Experience the future of AI-driven programming in your browser. No setup, no installation, just pure NeuroCode innovation.

*Ready to explore? Run `python launch_playground.py` and start your NeuroCode journey!*
