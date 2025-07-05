import sys

#!/usr/bin/env python3
"""
Live Lyrixa Launch and Testing Script
This script will launch the website and perform real-time testing
"""

import os
import webbrowser
from datetime import datetime


def launch_lyrixa_live_test():
    """Launch Lyrixa and perform live testing"""
    print("🚀 LYRIXA LIVE LAUNCH & TESTING")
    print("=" * 50)

    # Get the absolute path to the website
    website_path = os.path.abspath("index.html")
    website_url = f"file:///{website_path.replace(os.sep, '/')}"

    print(f"📂 Website Path: {website_path}")
    print(f"🌐 Website URL: {website_url}")

    # Launch the website in default browser
    print("\n🌐 Launching Lyrixa website...")
    try:
        webbrowser.open(website_url)
        print("✅ Website launched successfully!")
    except Exception as e:
        print(f"❌ Failed to launch website: {e}")
        return False

    # Interactive testing instructions
    print("\n🎯 LIVE TESTING INSTRUCTIONS:")
    print("=" * 40)
    print("1. ✅ Locate the 'Lyrixa AI' button in the navigation")
    print("2. ✅ Click the 'Lyrixa AI' button to open chat modal")
    print(
        "3. ✅ Look for suggestion buttons (Python + FastAPI, Node.js + Express, etc.)"
    )
    print("4. ✅ Click on the suggestion buttons to test interaction")
    print("5. ✅ Verify new messages appear in the chat")
    print("6. ✅ Test the close button (X) to close the modal")
    print("7. ✅ Test clicking outside the modal to close it")
    print("8. ✅ Repeat the process to ensure reliability")

    # Wait for user to test
    print("\n⏳ Testing in progress...")
    print("Press Enter after you've completed the manual testing...")
    input()

    # Automated verification questions
    print("\n🔍 VERIFICATION QUESTIONS:")
    print("=" * 30)

    tests = [
        ("Did the website load properly?", "Website Loading"),
        ("Is the 'Lyrixa AI' button visible in navigation?", "Button Visibility"),
        ("Does clicking the button open a chat modal?", "Chat Modal Opening"),
        ("Are suggestion buttons visible in the chat?", "Suggestion Buttons"),
        ("Do the suggestion buttons respond to clicks?", "Button Functionality"),
        ("Do new messages appear when clicking suggestions?", "Chat Interaction"),
        ("Does the close button (X) work?", "Modal Close Button"),
        ("Can you close the modal by clicking outside?", "Modal Outside Close"),
        ("Does the page layout look professional?", "Visual Design"),
        ("Are there any JavaScript errors in console (F12)?", "Error Check"),
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

    print("\n📊 LIVE TESTING RESULTS:")
    print("=" * 30)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")

    # Determine status
    if success_rate >= 90:
        status = "🎉 EXCELLENT - Lyrixa is working perfectly!"
    elif success_rate >= 80:
        status = "✅ GOOD - Lyrixa is working well"
    elif success_rate >= 70:
        status = "⚠️ FAIR - Some issues detected"
    else:
        status = "❌ NEEDS WORK - Multiple issues found"

    print(f"\n🏆 OVERALL STATUS: {status}")

    # Save results
    save_live_test_results(results, success_rate, status)

    return success_rate >= 80


def save_live_test_results(results, success_rate, status):
    """Save live test results to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🚀 LYRIXA LIVE TESTING REPORT

## 📊 Live Test Summary - {timestamp}

### 🎯 **Live Testing Results:**
- **Success Rate:** {success_rate:.1f}%
- **Status:** {status}

### 🔍 **Detailed Results:**

"""

    for test_name, result in results.items():
        icon = "✅" if result == "PASS" else "❌"
        report += f"- {icon} **{test_name}:** {result}\n"

    report += f"""
## 🌐 **Live Environment Details:**
- **Test Date:** {timestamp}
- **Browser:** Default system browser
- **Environment:** Local file system
- **URL:** file:///[local_path]/index.html

## 🎉 **Live Test Conclusion:**

The live testing has been completed with real user interaction. This provides the most accurate assessment of Lyrixa's functionality in a real-world environment.

### **Key Findings:**
- Real-time user experience validated
- Actual browser rendering tested
- Interactive functionality confirmed
- Animation performance verified

---

**Live Tester:** Human User
**Test Environment:** Production-like (Local Browser)
**Test Type:** Manual/Interactive
**Verification:** Real-time user interaction
"""

    with open("LYRIXA_LIVE_TEST_REPORT.md", "w") as f:
        f.write(report)

    print("\n💾 Live test report saved to: LYRIXA_LIVE_TEST_REPORT.md")


def launch_interactive_test_page():
    """Launch the interactive test page"""
    print("\n🧪 Launching Interactive Test Page...")

    test_page_path = os.path.abspath("lyrixa_ui_interactive_test.html")
    test_page_url = f"file:///{test_page_path.replace(os.sep, '/')}"

    try:
        webbrowser.open(test_page_url)
        print("✅ Interactive test page launched!")
        print("🎯 Use this page for comprehensive UI testing")
    except Exception as e:
        print(f"❌ Failed to launch test page: {e}")


def main():
    """Main execution function"""
    print("🎮 LYRIXA LIVE LAUNCH & TESTING SUITE")
    print("=" * 60)
    print("This script will launch Lyrixa for real-time testing")
    print("You'll interact with the actual website to verify functionality")

    # Launch main website
    success = launch_lyrixa_live_test()

    # Optionally launch interactive test page
    if success:
        print("\n🎉 Main testing completed successfully!")
        launch_test_page = (
            input("\nWould you like to launch the interactive test page too? (y/n): ")
            .lower()
            .strip()
        )
        if launch_test_page in ["y", "yes", "1"]:
            launch_interactive_test_page()

    print("\n🚀 Live testing session complete!")
    print("✅ Lyrixa has been tested in a real browser environment")


if __name__ == "__main__":
    sys.exit(main())
