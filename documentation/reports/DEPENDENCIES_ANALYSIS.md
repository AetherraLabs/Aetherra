# NeuroCode Dependencies Analysis & Update Report

## Analysis Summary

I analyzed the entire NeuroCode workspace to understand which dependencies are actually used in the codebase versus what was listed in the original requirements.txt.

### Key Findings

**Actually Used Dependencies:**
- `lark` - Essential grammar parser used in multiple files (grammar.py files)
- `psutil` - System monitoring used in performance modules
- `openai` - AI integration used in ai_runtime.py and multi_llm_manager.py
- `numpy` - Used in enhanced_memory_system.py
- `streamlit` - Only used in src/neurocode/ui/neurocode_playground.py
- `requests` - Used in plugin managers

**Dependencies Analysis:**
- Most AI providers (anthropic, google-generativeai, ollama, llama-cpp-python) are conditionally imported
- Many dependencies in the original requirements.txt were commented out or not actually used
- The multi_llm_manager.py uses dynamic imports to check for available AI providers

## Changes Made

### 1. Updated requirements.txt
- **Restructured** to clearly separate required vs optional dependencies
- **Made most AI providers optional** since they're conditionally imported
- **Added comprehensive documentation** explaining each dependency
- **Added installation guides** for different use cases
- **Moved numpy to optional** since it's only used in one enhanced feature

### 2. Updated requirements_minimal.txt  
- **Stripped down to absolute essentials:** `lark` and `psutil`
- **Made all AI providers optional** with clear instructions
- **Added quick start guide** for new users
- **Removed streamlit** from minimal requirements

### 3. Maintained requirements_dev.txt
- **References requirements.txt** via `-r requirements.txt`
- **Contains proper development tools** (pytest, black, flake8, etc.)
- **No changes needed** - well structured

## New Requirements Structure

### Core (Always Required)
- `lark>=1.1.7` - Grammar parser for .neuro files
- `psutil>=5.9.0` - System resource monitoring

### AI Providers (Optional - Choose One)
- `openai>=1.0.0,<2.0.0` - OpenAI GPT models
- `anthropic>=0.5.0` - Claude AI (commented)
- `google-generativeai>=0.3.0` - Gemini AI (commented)
- `ollama>=0.1.0` - Local models (commented)
- `llama-cpp-python>=0.2.0` - GGUF models (commented)

### Optional Features
- `streamlit>=1.28.0` - Web playground interface (commented)
- `requests>=2.31.0` - Plugin registry (commented)
- `numpy>=1.24.0` - Enhanced memory systems (commented)

## Installation Options

### Minimal Install (2 packages)
```bash
pip install lark psutil
```

### Recommended Install (3 packages)
```bash
pip install lark psutil openai
```

### Development Install
```bash
pip install -r requirements_dev.txt
```

## Benefits of This Update

1. **Faster Installation** - Users only install what they need
2. **Clear Documentation** - Each dependency is explained
3. **Flexible AI Providers** - Users can choose their preferred AI backend
4. **Better Organization** - Core vs optional dependencies clearly separated
5. **Future-Proof** - Easy to add new optional dependencies

## Files Updated

- `requirements.txt` - Complete rewrite with better organization
- `requirements_minimal.txt` - Streamlined to absolute essentials
- This report: `DEPENDENCIES_ANALYSIS.md`

The requirements are now much cleaner, more flexible, and better documented for both new users and contributors.
