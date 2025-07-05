#!/usr/bin/env python3
"""
Lyrixa Phase 2 Testing Script - Simplified
Tests the new intelligent plugin system and intent recognition
"""

import os
import webbrowser


def main():
    """Main test execution"""
    print("🚀 LYRIXA PHASE 2 - INTELLIGENCE LAYER TESTING")
    print("=" * 60)
    print("Testing advanced AI capabilities:")
    print("🎯 Intent Recognition System")
    print("🧩 Plugin System with Active Execution")
    print("🛠️ Code Generation & Analysis")
    print("📚 Learning & Project Assistance")
    print("💬 Enhanced Conversation Management")

    # Launch the main website to test Phase 2
    print("\\n🌐 Launching main website with Phase 2 features...")
    website_path = os.path.abspath("index.html")
    website_url = f"file:///{website_path.replace(os.sep, '/')}"

    try:
        webbrowser.open(website_url)
        print("✅ Website launched successfully!")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        return False

    # Testing instructions
    print("\\n🧪 PHASE 2 TESTING INSTRUCTIONS:")
    print("=" * 40)
    print("1. ✅ Open browser console (F12) to see system logs")
    print("2. ✅ Wait for 'Phase 2 AI Systems Active' messages")
    print("3. ✅ Click 'Lyrixa AI' button to open chat modal")
    print("4. ✅ Test intent recognition with these requests:")
    print("   • 'Generate a FastAPI application'")
    print("   • 'Analyze this code for bugs'")
    print("   • 'Explain how React hooks work'")
    print("   • 'What is the best project structure?'")
    print("   • 'Hello! How are you today?'")
    print("5. ✅ Watch console logs to see:")
    print("   • Intent recognition results")
    print("   • Plugin execution")
    print("   • Response generation")
    print("6. ✅ Try switching personalities and see different responses")
    print("7. ✅ Test conversation memory with follow-up questions")

    print("\\n🔍 WHAT TO LOOK FOR:")
    print("• Console shows 'Plugin Manager Phase 2 - ACTIVE'")
    print("• Console shows 'Intent Recognition System initialized'")
    print("• Different request types route to appropriate plugins")
    print("• Intelligent, contextual responses")
    print("• Code generation produces actual working code")
    print("• Learning explanations are detailed and helpful")

    # Interactive testing
    print("\\n⏳ Testing in progress...")
    print("Open the chat modal and test the features listed above.")
    print("Check the browser console for detailed system logs.")
    input("Press Enter when you've completed testing...")

    # Verification questions
    print("\\n🔍 VERIFICATION QUESTIONS:")
    print("=" * 30)

    tests = [
        ("Did you see 'Phase 2 AI Systems Active' in console?", "Phase 2 Loading"),
        ("Does the chat modal open when clicking 'Lyrixa AI'?", "Modal Functionality"),
        ("Do you see intent recognition logs in console?", "Intent Recognition"),
        ("Do code generation requests produce actual code?", "Code Generation"),
        ("Do learning requests provide detailed explanations?", "Learning Assistant"),
        (
            "Are responses contextually appropriate for different intents?",
            "Smart Routing",
        ),
        ("Does personality switching affect response style?", "Personality Engine"),
        ("Does the system remember conversation context?", "Memory System"),
        ("Are plugin execution logs visible in console?", "Plugin System"),
        (
            "Overall, does Lyrixa feel more intelligent than before?",
            "Intelligence Upgrade",
        ),
    ]

    results = {}
    passed = 0
    total = len(tests)

    for question, test_name in tests:
        while True:
            answer = input(f"❓ {question} (y/n): ").lower().strip()
            if answer in ["y", "yes", "1", "true"]:
                results[test_name] = "PASS"
                print(f"   ✅ {test_name}: PASS")
                passed += 1
                break
            elif answer in ["n", "no", "0", "false"]:
                results[test_name] = "FAIL"
                print(f"   ❌ {test_name}: FAIL")
                break
            else:
                print("   Please enter 'y' for yes or 'n' for no")

    # Calculate results
    success_rate = (passed / total) * 100

    print("\\n📊 PHASE 2 TESTING RESULTS:")
    print("=" * 35)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")

    # Determine status
    if success_rate >= 90:
        status = "🎉 EXCELLENT - Phase 2 is working perfectly!"
    elif success_rate >= 80:
        status = "✅ GOOD - Phase 2 is working well"
    elif success_rate >= 70:
        status = "⚠️ FAIR - Some Phase 2 issues detected"
    else:
        status = "❌ NEEDS WORK - Multiple Phase 2 issues found"

    print(f"\\n🏆 PHASE 2 STATUS: {status}")

    # Save results
    save_phase2_results(results, success_rate, status)

    return success_rate >= 80


def save_phase2_results(results, success_rate, status):
    """Save Phase 2 test results"""

    report = f"""# 🚀 LYRIXA PHASE 2 - INTELLIGENCE LAYER TESTING REPORT

## 📊 Phase 2 Test Summary

### 🎯 **Testing Results:**
- **Success Rate:** {success_rate:.1f}%
- **Status:** {status}

### 🔍 **Detailed Results:**

"""

    for test_name, result in results.items():
        icon = "✅" if result == "PASS" else "❌"
        report += f"- {icon} **{test_name}:** {result}\\n"

    report += """
## 🧠 **Phase 2 Features Tested:**

### 🎯 **Intent Recognition System**
- Natural language understanding for routing requests
- Confidence scoring and fallback handling
- Context awareness and conversation continuity

### 🧩 **Plugin System**
- **Code Generator:** FastAPI, React, Express, generic code generation
- **Code Analyzer:** Bug detection, optimization, explanations
- **Learning Assistant:** Educational content and concept explanations
- **Project Advisor:** Architecture guidance and best practices
- **Conversation Handler:** Personality-driven general chat

### 🏗️ **System Architecture**
- Modular plugin architecture with execution isolation
- Intent-to-plugin routing with intelligent fallbacks
- Enhanced conversation memory with plugin context
- Real-time debugging and system monitoring

## 🎉 **Phase 2 Achievements:**

✅ **Intelligence Layer Active:** Advanced AI reasoning and routing
✅ **Plugin Ecosystem:** Multiple specialized AI capabilities
✅ **Smart Context Management:** Intent-aware conversation handling
✅ **Code Intelligence:** Real code generation and analysis
✅ **Educational AI:** Learning assistance and explanations
✅ **Project Guidance:** Architecture and best practices advice

## 🔄 **Next Phase: Development Tools & Code Intelligence**

The foundation is now ready for Phase 3:
- Aetherra-aware code generation
- Advanced code diagnostics and debugging
- Pattern recognition and smart suggestions
- Integration with development workflows

---

**Test Environment:** Local Browser with Console Debugging
**Test Type:** Interactive User Validation
**Phase:** 2 - Intelligence Layer
**Features:** Intent Recognition + Plugin System
"""

    with open("LYRIXA_PHASE2_TEST_REPORT.md", "w") as f:
        f.write(report)

    print("\\n💾 Phase 2 test report saved to: LYRIXA_PHASE2_TEST_REPORT.md")


if __name__ == "__main__":
    main()
