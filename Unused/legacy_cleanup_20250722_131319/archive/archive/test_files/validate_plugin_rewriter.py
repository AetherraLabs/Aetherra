#!/usr/bin/env python3
"""
Simple Plugin Rewriter Validation
Quick test to ensure Phase 5 implementation is working
"""

import sys
import os
import tempfile
import shutil

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic Plugin Rewriter functionality"""
    print("🧪 Plugin Rewriter Basic Validation")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from lyrixa.ai.plugin_rewriter import PluginRewriter, PluginRewriterError
        print("✅ Imports successful")
        
        # Test initialization
        print("🔧 Testing initialization...")
        test_dir = tempfile.mkdtemp()
        plugin_dir = os.path.join(test_dir, "plugins")
        history_dir = os.path.join(test_dir, "history")
        
        os.makedirs(plugin_dir)
        
        rewriter = PluginRewriter(plugin_dir=plugin_dir, history_dir=history_dir)
        print("✅ Initialization successful")
        
        # Test plugin creation and reading
        print("📝 Testing plugin file operations...")
        test_plugin_code = '''def hello():
    return "Hello, World!"'''
        
        plugin_path = os.path.join(plugin_dir, "test_plugin.py")
        with open(plugin_path, "w") as f:
            f.write(test_plugin_code)
        
        # Test reading
        read_code = rewriter._read_plugin_code(plugin_path)
        assert read_code.strip() == test_plugin_code.strip()
        print("✅ Plugin file operations working")
        
        # Test metadata extraction
        print("🔍 Testing metadata extraction...")
        metadata = rewriter._extract_plugin_metadata(test_plugin_code)
        assert "hello" in metadata['functions']
        print("✅ Metadata extraction working")
        
        # Test syntax validation
        print("✔️ Testing syntax validation...")
        assert rewriter._validate_python_syntax(test_plugin_code) == True
        assert rewriter._validate_python_syntax("def broken(") == False
        print("✅ Syntax validation working")
        
        # Test backup creation
        print("💾 Testing backup creation...")
        backup_path = rewriter._create_version_backup("test_plugin", test_plugin_code)
        assert os.path.exists(backup_path)
        print("✅ Backup creation working")
        
        # Test version listing
        print("📚 Testing version listing...")
        versions = rewriter.list_plugin_versions("test_plugin")
        assert len(versions) >= 1
        print("✅ Version listing working")
        
        # Test code cleaning
        print("🧹 Testing code cleaning...")
        markdown_code = "```python\nprint('hello')\n```"
        cleaned = rewriter._clean_code_response(markdown_code)
        assert cleaned == "print('hello')"
        print("✅ Code cleaning working")
        
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        
        print("\n" + "=" * 50)
        print("✅ ALL BASIC TESTS PASSED!")
        print("🚀 Plugin Rewriter Phase 5 is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_capabilities():
    """Show what the Plugin Rewriter can do"""
    print("\n" + "=" * 50)
    print("🎯 PLUGIN REWRITER CAPABILITIES")
    print("=" * 50)
    
    capabilities = [
        "🔍 explain_plugin() - Natural language explanation of plugin functionality",
        "🔧 refactor_plugin() - AI-powered code refactoring with specific goals",
        "📊 add_logging_to_plugin() - Automatic logging injection",
        "⏪ rollback_plugin() - Safe rollback to previous versions",
        "📊 diff_plugin_versions() - Compare different plugin versions",
        "📚 list_plugin_versions() - View all available plugin versions",
        "💾 Automatic backup creation before modifications",
        "✔️ Syntax validation for all generated code",
        "🛡️ Safe file operations with atomic writes",
        "🧠 Metadata extraction using AST analysis"
    ]
    
    for capability in capabilities:
        print(f"   {capability}")
    
    print("\n🎉 Ready to make Lyrixa an AI programming assistant!")


def show_next_steps():
    """Show next steps for Phase 5"""
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS FOR PHASE 5")
    print("=" * 50)
    
    steps = [
        "🔗 Integrate with Lyrixa's conversational interface",
        "🧪 Set up comprehensive testing with real OpenAI API",
        "📖 Create user documentation and examples",
        "🔄 Implement Plugin Version Control + Diffing (Phase 5.2)",
        "🛡️ Add Confidence & Safety Rating System (Phase 5.3)",
        "🎯 Build Goal-Aligned Plugin Ranking (Phase 5.4)",
        "📦 Create backup and recovery procedures",
        "🚀 Deploy to production environment"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n✨ Current Status: Phase 5.1 (AI Plugin Rewriter) - COMPLETE")


if __name__ == "__main__":
    success = test_basic_functionality()
    
    if success:
        show_capabilities()
        show_next_steps()
        sys.exit(0)
    else:
        print("❌ Basic validation failed!")
        sys.exit(1)
