# 📦 NeuroCode Dependencies Guide

This guide explains the different dependency files and installation options for NeuroCode v1.0.0.

## 🎯 **Quick Start - Choose Your Installation**

### **Minimal Installation** (Basic NeuroCode functionality)
```bash
pip install -r requirements_minimal.txt
```
**Includes:** Core language features, playground, OpenAI integration

### **Standard Installation** (Recommended for most users)
```bash
pip install -r requirements.txt
```
**Includes:** All core features plus optional enhancements

### **Enhanced Installation** (AI researchers, enterprise use)
```bash
pip install -r requirements_enhanced.txt
```
**Includes:** Machine learning, local AI models, vector databases, GUI frameworks

### **Development Installation** (Contributors)
```bash
pip install -r requirements_dev.txt
```
**Includes:** All dependencies plus development tools, testing, profiling

---

## 📋 **Dependency Files Overview**

| File | Purpose | Use Case |
|------|---------|----------|
| `requirements_minimal.txt` | Core functionality only | Quick testing, minimal installs |
| `requirements.txt` | Standard installation | Most users, production deployment |
| `requirements_enhanced.txt` | Advanced features | AI research, enterprise development |
| `requirements_dev.txt` | Development tools | Contributors, maintainers |
| `playground_requirements.txt` | Playground only | Streamlit demo, educational use |

---

## 🔧 **Installation by Use Case**

### **🎮 Playground Only**
Just want to try the interactive playground?
```bash
pip install -r playground_requirements.txt
python tools/launch_playground.py
```

### **🧠 AI Research & Development**
Need advanced AI features and local models?
```bash
pip install -r requirements_enhanced.txt
# Optionally install Ollama for local models
pip install ollama
```

### **🏢 Enterprise Deployment**
Production-ready installation with monitoring:
```bash
pip install -r requirements.txt
# Add monitoring tools
pip install prometheus-client grafana-api
```

### **👨‍💻 Contributing to NeuroCode**
Setting up a development environment:
```bash
pip install -r requirements_dev.txt
pre-commit install  # Set up git hooks
```

---

## 🤖 **AI Provider Setup**

NeuroCode supports multiple AI providers. Choose based on your needs:

### **OpenAI (Recommended for beginners)**
```bash
pip install openai>=1.0.0
export OPENAI_API_KEY="your-api-key"
```

### **Local Models with Ollama**
```bash
pip install ollama
# Install and run Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral  # or llama2, codellama, etc.
```

### **Anthropic Claude**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

### **Google Gemini**
```bash
pip install google-generativeai
export GOOGLE_API_KEY="your-api-key"
```

---

## ⚙️ **Optional Components**

### **Vector Databases** (for advanced memory features)
```bash
# ChromaDB (recommended)
pip install chromadb

# Or Pinecone
pip install pinecone-client

# Or Weaviate
pip install weaviate-client
```

### **GUI Applications**
```bash
# For desktop GUI applications
pip install PySide6 qdarkstyle

# Alternative Qt backend
pip install PyQt6
```

### **Speech & Audio** (experimental)
```bash
# Warning: Large downloads
pip install openai-whisper  # ~1GB download
pip install pyttsx3 speechrecognition
```

---

## 🐍 **Python Version Compatibility**

- **Minimum:** Python 3.8
- **Recommended:** Python 3.10 or 3.11
- **Latest:** Python 3.12 (fully supported)

### **Version-specific Notes**
- Python 3.8: Basic functionality
- Python 3.9+: Better type hinting support
- Python 3.10+: Improved error messages
- Python 3.11+: Faster performance
- Python 3.12+: Latest optimizations

---

## 🚀 **Performance Optimization**

### **CPU-Optimized Installation**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers accelerate
```

### **GPU-Accelerated (CUDA)**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate
```

### **Apple Silicon (M1/M2)**
```bash
pip install torch torchvision torchaudio
pip install transformers accelerate
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Import Errors**
   ```bash
   # Clear pip cache and reinstall
   pip cache purge
   pip install --force-reinstall -r requirements.txt
   ```

2. **Version Conflicts**
   ```bash
   # Use the fixed requirements file
   pip install -r requirements_fixed.txt
   ```

3. **Local Model Issues**
   ```bash
   # Reinstall llama-cpp-python with specific options
   CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
   ```

### **Environment Management**
```bash
# Create virtual environment
python -m venv neurocode-env
source neurocode-env/bin/activate  # Linux/Mac
# or
neurocode-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 📊 **Installation Size Estimates**

| Installation Type | Disk Space | Download Size |
|------------------|------------|---------------|
| Minimal | ~50 MB | ~20 MB |
| Standard | ~200 MB | ~80 MB |
| Enhanced | ~2-5 GB | ~1-2 GB |
| Full (with models) | ~10+ GB | ~5+ GB |

---

## 🔗 **Related Documentation**

- [Installation Guide](docs/INSTALLATION.md)
- [Getting Started Tutorial](docs/TUTORIAL.md)
- [AI Provider Setup](docs/AI_SETUP.md)
- [Development Setup](CONTRIBUTING.md)

---

**Need Help?** Check our [troubleshooting guide](docs/TROUBLESHOOTING.md) or open an issue on GitHub.
