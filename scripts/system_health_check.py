#!/usr/bin/env python3
"""
🔍 NeuroCode System Health Check
Quick diagnostic tool to verify all major systems are operational
"""

import sys
import os
from pathlib import Path

def check_core_imports():
    """Test core system imports"""
    print("🧠 Testing Core Systems...")
    
    try:
        from core.interpreter import NeuroCodeInterpreter
        print("  ✅ Core interpreter: OK")
    except Exception as e:
        print(f"  ❌ Core interpreter: FAILED - {e}")
        return False
    
    try:
        from core.memory import MemorySystem
        print("  ✅ Memory system: OK")
    except Exception as e:
        print(f"  ⚠️ Memory system: WARNING - {e}")
    
    try:
        from core.goal_system import GoalSystem
        print("  ✅ Goal system: OK")
    except Exception as e:
        print(f"  ⚠️ Goal system: WARNING - {e}")
    
    return True

def check_file_structure():
    """Verify critical files exist"""
    print("\n📁 Checking File Structure...")
    
    critical_files = [
        "README.md",
        "core/interpreter.py",
        "core/neurocode_grammar.py",
        "src/neurocode/stdlib/__init__.py",
        "website/index.html",
        "docs/index.html",
        "CNAME"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking Dependencies...")
    
    required_modules = [
        "lark",
        "openai", 
        "streamlit",
        "requests",
        "pathlib"
    ]
    
    missing_deps = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
            missing_deps.append(module)
    
    return len(missing_deps) == 0

def check_git_status():
    """Check git repository status"""
    print("\n🔄 Checking Git Status...")
    
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("  ⚠️ Uncommitted changes found")
                print(f"     {result.stdout.strip()}")
            else:
                print("  ✅ Working tree clean")
            return True
        else:
            print("  ❌ Git not available or not a git repository")
            return False
    except Exception as e:
        print(f"  ❌ Git check failed: {e}")
        return False

def check_website_files():
    """Verify website deployment readiness"""
    print("\n🌐 Checking Website Deployment...")
    
    website_files = [
        "website/index.html",
        "website/styles.css", 
        "website/script.js",
        "docs/index.html",
        "CNAME"
    ]
    
    ready = True
    for file_path in website_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            ready = False
    
    return ready

def main():
    """Run comprehensive health check"""
    print("🚀 NeuroCode System Health Check")
    print("=" * 50)
    
    checks = [
        ("Core Systems", check_core_imports),
        ("File Structure", check_file_structure), 
        ("Dependencies", check_dependencies),
        ("Git Status", check_git_status),
        ("Website Files", check_website_files)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("NeuroCode is ready for production use.")
    else:
        print("⚠️ SOME ISSUES DETECTED")
        print("Please review failed checks above.")
    
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 50)

if __name__ == "__main__":
    main()
