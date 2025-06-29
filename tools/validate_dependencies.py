#!/usr/bin/env python3
"""
🔍 NeuroCode Dependency Validator
Validates that all required dependencies are available and working
"""

import sys
from pathlib import Path

def validate_core_dependencies():
    """Validate core required dependencies"""
    print("🔍 Validating Core Dependencies...")
    
    # Test lark (grammar parser)
    try:
        from lark import Lark, Transformer
        print("✅ lark: Available")
    except ImportError as e:
        print(f"❌ lark: Missing - {e}")
        return False
        
    # Test streamlit (playground)
    try:
        import streamlit
        print(f"✅ streamlit: v{streamlit.__version__}")
    except ImportError as e:
        print(f"❌ streamlit: Missing - {e}")
        return False
        
    # Test psutil (performance monitoring)
    try:
        import psutil
        print(f"✅ psutil: v{psutil.__version__}")
    except ImportError as e:
        print(f"❌ psutil: Missing - {e}")
        return False
        
    # Test at least one AI provider
    ai_available = False
    
    try:
        import openai
        print(f"✅ openai: v{openai.__version__}")
        ai_available = True
    except ImportError:
        print("⚠️ openai: Not available")
    
    try:
        import anthropic
        print("✅ anthropic: Available")
        ai_available = True
    except ImportError:
        print("⚠️ anthropic: Not available")
        
    try:
        import google.generativeai
        print("✅ google-generativeai: Available") 
        ai_available = True
    except ImportError:
        print("⚠️ google-generativeai: Not available")
        
    try:
        import ollama
        print("✅ ollama: Available")
        ai_available = True
    except ImportError:
        print("⚠️ ollama: Not available")
    
    if not ai_available:
        print("❌ No AI providers available - install at least one (openai, anthropic, ollama, etc.)")
        return False
        
    return True

def validate_optional_dependencies():
    """Validate optional dependencies"""
    print("\n🎨 Validating Optional Dependencies...")
    
    # GUI frameworks
    gui_available = False
    try:
        import PySide6
        print("✅ PySide6: Available")
        gui_available = True
    except ImportError:
        print("⚠️ PySide6: Not available")
        
    try:
        import PyQt6
        print("✅ PyQt6: Available")
        gui_available = True
    except ImportError:
        print("⚠️ PyQt6: Not available")
        
    if not gui_available:
        print("ℹ️ No GUI frameworks available - install PySide6 or PyQt6 for GUI features")
    
    # Local AI models
    try:
        import llama_cpp
        print("✅ llama-cpp-python: Available")
    except ImportError:
        print("⚠️ llama-cpp-python: Not available")

def validate_imports():
    """Validate that our core modules can be imported"""
    print("\n🧬 Validating NeuroCode Modules...")
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from core.neurocode_grammar import create_neurocode_parser
        parser = create_neurocode_parser()
        print("✅ NeuroCode Grammar Parser: Working")
    except Exception as e:
        print(f"❌ NeuroCode Grammar Parser: Error - {e}")
        return False
        
    try:
        from core.multi_llm_manager import llm_manager
        print("✅ Multi-LLM Manager: Working")
    except Exception as e:
        print(f"❌ Multi-LLM Manager: Error - {e}")
        return False
        
    return True

def main():
    """Main validation function"""
    print("🔍 NeuroCode v1.0.0 - Dependency Validation")
    print("=" * 50)
    
    core_valid = validate_core_dependencies()
    validate_optional_dependencies()
    modules_valid = validate_imports()
    
    print("\n" + "=" * 50)
    
    if core_valid and modules_valid:
        print("🎯 All core dependencies validated successfully!")
        print("✅ NeuroCode is ready to use")
        return 0
    else:
        print("❌ Some core dependencies are missing")
        print("🔧 Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
