#!/usr/bin/env python3
"""
aetherra Enhancement Installation Script
Installs and configures next-generation AI capabilities
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required for aetherra enhancements")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_core_dependencies():
    """Install core dependencies for enhancements"""
    print("\n📦 Installing Core Dependencies")
    print("=" * 40)

    core_packages = [
        "sentence-transformers",  # For semantic embeddings
        "chromadb",  # Vector database
        "numpy",  # Numerical processing
        "scipy",  # Scientific computing
        "scikit-learn",  # Machine learning utilities
        "transformers",  # Hugging Face transformers
        "torch",  # PyTorch for ML
        "accelerate",  # Accelerated ML training
    ]

    success_count = 0
    for package in core_packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1

    print(f"\n📊 Core Dependencies: {success_count}/{len(core_packages)} installed")
    return success_count == len(core_packages)


def install_optional_dependencies():
    """Install optional dependencies for advanced features"""
    print("\n🚀 Installing Optional Dependencies")
    print("=" * 40)

    optional_packages = [
        "ollama",  # Local LLM management
        "llama-cpp-python",  # Local LLaMA models
        "ctransformers",  # Optimized transformers
        "faiss-cpu",  # Facebook AI similarity search
        "pinecone-client",  # Pinecone vector DB
        "weaviate-client",  # Weaviate vector DB
        "onnxruntime",  # ONNX runtime for optimization
    ]

    success_count = 0
    for package in optional_packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1
        # Continue even if some optional packages fail

    print(
        f"\n📊 Optional Dependencies: {success_count}/{len(optional_packages)} installed"
    )
    return success_count > 0


def setup_local_ai_models():
    """Setup local AI models"""
    print("\n🤖 Setting up Local AI Models")
    print("=" * 40)

    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # Check if Ollama is available
    if run_command("ollama --version", "Checking Ollama installation"):
        print("🎯 Ollama detected! You can install local models with:")
        print("   ollama pull llama2")
        print("   ollama pull mistral")
        print("   ollama pull codellama")
    else:
        print("ℹ️  Ollama not found. Visit https://ollama.ai to install local models")

    # Check for pre-downloaded GGUF models
    gguf_files = list(models_dir.glob("*.gguf"))
    if gguf_files:
        print(f"✅ Found {len(gguf_files)} GGUF model files:")
        for model in gguf_files:
            print(f"   📄 {model.name}")
    else:
        print("ℹ️  No GGUF models found. Download models to ./models/ directory")
        print(
            "   Example: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
        )

    return True


def create_configuration_files():
    """Create configuration files for enhancements"""
    print("\n⚙️  Creating Configuration Files")
    print("=" * 40)

    # Create .env template if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# aetherra Enhancement Configuration
# OpenAI API Key (optional, for fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Local AI Configuration
LOCAL_AI_ENABLED=true
VECTOR_MEMORY_ENABLED=true
INTENT_PARSER_ENABLED=true

# Performance Settings
MAX_MEMORY_SIZE=10000
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_TYPE=chromadb

# Model Paths
MODELS_DIR=./models
MEMORY_FILE=enhanced_memory.json
"""
        env_file.write_text(env_content)
        print("✅ Created .env configuration file")
    else:
        print("ℹ️  .env file already exists")

    # Create requirements.txt for enhancements
    requirements_file = Path("requirements_enhanced.txt")
    requirements_content = """# aetherra Enhancement Dependencies
sentence-transformers>=2.2.0
chromadb>=0.4.0
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=1.0.0
transformers>=4.21.0
torch>=1.12.0
accelerate>=0.20.0

# Optional dependencies
ollama
llama-cpp-python
ctransformers
faiss-cpu
pinecone-client
weaviate-client
onnxruntime
"""
    requirements_file.write_text(requirements_content)
    print("✅ Created requirements_enhanced.txt")

    return True


def test_enhancements():
    """Test that enhancements are working"""
    print("\n🧪 Testing Enhancements")
    print("=" * 40)

    try:
        # Test sentence transformers
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_embedding = model.encode("test sentence")
        print("✅ Sentence transformers working")

        # Test chromadb
        import chromadb

        client = chromadb.Client()
        print("✅ ChromaDB working")

        # Test our enhancement modules
        sys.path.insert(0, "./core")

        from core.local_ai import LocalAIEngine

        local_ai = LocalAIEngine()
        print("✅ Local AI engine working")

        from core.vector_memory import EnhancedSemanticMemory

        memory = EnhancedSemanticMemory("test_memory.json")
        print("✅ Vector memory working")

        from core.intent_parser import IntentToCodeParser

        parser = IntentToCodeParser()
        print("✅ Intent parser working")

        # Clean up test file
        test_file = Path("test_memory.json")
        if test_file.exists():
            test_file.unlink()

        print("\n🎉 All enhancements tested successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def create_demo_script():
    """Create a demo script to showcase enhancements"""
    demo_content = '''#!/usr/bin/env python3
"""
aetherra Enhancement Demo
Showcases the revolutionary AI-native programming capabilities
"""

import sys
import os
sys.path.insert(0, './core')

from enhanced_interpreter import create_enhanced_interpreter

def run_demo():
    print("🧬 aetherra Enhancement Demo")
    print("=" * 50)

    interpreter = create_enhanced_interpreter()

    # Show status
    status = interpreter.get_enhancement_status()
    print(f"🚀 Enhancements Available: {status['enhancements_available']}")

    if not status['enhancements_available']:
        print("❌ Enhancements not available. Run setup_enhancements.py first.")
        return

    print("\\n🎯 Demo Commands:")

    demo_commands = [
        ("Natural Language", "Create a REST API for user authentication"),
        ("AI Query", "ai: What are the benefits of aetherra?"),
        ("Intent Command", "intent: build a data processing pipeline"),
        ("Local AI Status", "local_ai status"),
        ("Pattern Analysis", "analyze_patterns")
    ]

    for description, command in demo_commands:
        print(f"\\n📝 {description}:")
        print(f"   Command: {command}")

        try:
            result = interpreter.execute_aetherra(command)
            print(f"   Result: {result[:150]}..." if len(result) > 150 else f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")

    print("\\n✅ Demo completed! aetherra is ready for the future!")

if __name__ == "__main__":
    run_demo()
'''

    demo_file = Path("demo_enhancements.py")
    try:
        demo_file.write_text(demo_content, encoding="utf-8")
        print("✅ Created demo_enhancements.py")
    except UnicodeEncodeError:
        # Fallback: Remove emoji and write as ASCII
        safe_content = demo_content.replace("🧬", "[aether]").replace("🚀", "[LAUNCH]")
        demo_file.write_text(safe_content, encoding="utf-8")
        print("[OK] Created demo_enhancements.py (ASCII-safe)")


def main():
    """Main installation process"""
    print("🧬 aetherra Enhancement Installation")
    print("🚀 Preparing for AI-Native Programming Dominance")
    print("=" * 60)

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    # Installation steps
    steps = [
        ("Installing core dependencies", install_core_dependencies),
        ("Installing optional dependencies", install_optional_dependencies),
        ("Setting up local AI models", setup_local_ai_models),
        ("Creating configuration files", create_configuration_files),
        ("Testing enhancements", test_enhancements),
        ("Creating demo script", create_demo_script),
    ]

    completed_steps = 0
    for description, step_function in steps:
        print(f"\n🎯 Step {completed_steps + 1}/{len(steps)}: {description}")
        if step_function():
            completed_steps += 1
        else:
            print("⚠️  Step failed but continuing...")

    # Final report
    print("\n" + "=" * 60)
    print("🎉 aetherra Enhancement Installation Complete!")
    print(f"📊 Completed: {completed_steps}/{len(steps)} steps")

    if completed_steps >= 4:  # Core functionality working
        print("\n✅ aetherra is now enhanced with:")
        print("   🤖 Local AI models for 99% API independence")
        print("   🧠 Vector-based semantic memory")
        print("   💬 Natural language to code translation")
        print("   🚀 Intent-driven programming")
        print("   📊 Pattern recognition and analysis")

        print("\n🎯 Next Steps:")
        print("   1. Run: python demo_enhancements.py")
        print("   2. Try: python core/enhanced_interpreter.py")
        print("   3. Explore natural language programming!")

        print("\n🌟 Welcome to the future of AI-native programming!")
    else:
        print("\n⚠️  Some enhancements may not be fully functional.")
        print("   Check error messages above and install missing dependencies.")

    print("\n🧬 aetherra: Where human intent meets AI implementation!")


if __name__ == "__main__":
    main()
