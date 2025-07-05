#!/usr/bin/env python3
"""
Lyrixa Backend Testing Suite
Tests server-side functionality and file integrity
"""

import json
import os


def test_file_existence():
    """Test if required files exist"""
    print("TEST 1: File Existence")
    print("=" * 40)

    required_files = ["index.html", "script.js", "styles.css", "favicon.ico"]

    results = {}

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
            results[file] = "PASS"
        else:
            print(f"❌ {file} missing")
            results[file] = "FAIL"

    return results


def test_script_js_content():
    """Analyze script.js for Lyrixa functionality"""
    print("\nTEST 2: Script.js Content Analysis")
    print("=" * 40)

    results = {}

    try:
        with open("script.js", "r", encoding="utf-8") as f:
            script_content = f.read()

        # Test for showLyrixaDemo function
        if "showLyrixaDemo" in script_content:
            print("✅ showLyrixaDemo function found in script.js")
            results["showLyrixaDemo_function"] = "PASS"
        else:
            print("❌ showLyrixaDemo function not found in script.js")
            results["showLyrixaDemo_function"] = "FAIL"

        # Test for highlight-demo animation
        if "highlight-demo" in script_content:
            print("✅ highlight-demo animation code found")
            results["highlight_animation"] = "PASS"
        else:
            print("❌ highlight-demo animation code not found")
            results["highlight_animation"] = "FAIL"

        # Test for smooth scrolling
        if "scrollIntoView" in script_content:
            print("✅ Smooth scrolling implementation found")
            results["smooth_scrolling"] = "PASS"
        else:
            print("❌ Smooth scrolling implementation not found")
            results["smooth_scrolling"] = "FAIL"

        # Test for function definition structure
        if (
            "function showLyrixaDemo()" in script_content
            or "const showLyrixaDemo" in script_content
        ):
            print("✅ Proper function definition structure found")
            results["function_structure"] = "PASS"
        else:
            print("❌ Proper function definition structure not found")
            results["function_structure"] = "FAIL"

    except FileNotFoundError:
        print("❌ Error: script.js file not found")
        results["file_readable"] = "FAIL"
    except Exception as e:
        print(f"❌ Error reading script.js: {e}")
        results["file_readable"] = "FAIL"

    return results


def test_html_structure():
    """Analyze HTML structure for Lyrixa integration"""
    print("\nTEST 3: HTML Structure Analysis")
    print("=" * 40)

    results = {}

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Test for Lyrixa button onclick handler
        if "showLyrixaDemo()" in html_content:
            print("✅ Lyrixa button onclick handler found in HTML")
            results["onclick_handler"] = "PASS"
        else:
            print("❌ Lyrixa button onclick handler not found in HTML")
            results["onclick_handler"] = "FAIL"

        # Test for Lyrixa references
        if "Lyrixa" in html_content:
            print("✅ Lyrixa references found in HTML")
            results["lyrixa_references"] = "PASS"
        else:
            print("❌ No Lyrixa references found in HTML")
            results["lyrixa_references"] = "FAIL"

        # Test for script.js link
        if "script.js" in html_content:
            print("✅ script.js properly linked in HTML")
            results["script_link"] = "PASS"
        else:
            print("❌ script.js not properly linked in HTML")
            results["script_link"] = "FAIL"

        # Test for target sections
        sections_to_check = ["demos", "features", "creative-brainstorm"]
        sections_found = 0
        for section in sections_to_check:
            if section in html_content:
                sections_found += 1

        if sections_found > 0:
            print(f"✅ Found {sections_found} target sections for scrolling")
            results["target_sections"] = "PASS"
        else:
            print("❌ No target sections found for scrolling")
            results["target_sections"] = "FAIL"

    except FileNotFoundError:
        print("❌ Error: index.html file not found")
        results["file_readable"] = "FAIL"
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        results["file_readable"] = "FAIL"

    return results


def test_css_styles():
    """Analyze CSS for Lyrixa animations"""
    print("\nTEST 4: CSS Analysis")
    print("=" * 40)

    results = {}

    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        # Test for highlight-demo CSS class
        if "highlight-demo" in css_content:
            print("✅ highlight-demo CSS class found")
            results["highlight_demo_css"] = "PASS"
        else:
            print("❌ highlight-demo CSS class not found")
            results["highlight_demo_css"] = "FAIL"

        # Test for animations
        if "@keyframes" in css_content or "animation" in css_content:
            print("✅ Animation styles found in CSS")
            results["animation_styles"] = "PASS"
        else:
            print("❌ No animation styles found in CSS")
            results["animation_styles"] = "FAIL"

        # Test for smooth scroll
        if "scroll-behavior" in css_content:
            print("✅ Smooth scroll behavior found in CSS")
            results["smooth_scroll_css"] = "PASS"
        else:
            print("ℹ️ No CSS smooth scroll (may be handled by JavaScript)")
            results["smooth_scroll_css"] = "INFO"

    except FileNotFoundError:
        print("❌ Error: styles.css file not found")
        results["file_readable"] = "FAIL"
    except Exception as e:
        print(f"❌ Error reading styles.css: {e}")
        results["file_readable"] = "FAIL"

    return results


def test_file_sizes():
    """Check file sizes for reasonable content"""
    print("\nTEST 5: File Size Analysis")
    print("=" * 40)

    results = {}
    files_to_check = ["index.html", "script.js", "styles.css"]

    for file in files_to_check:
        try:
            stats = os.stat(file)
            size_kb = stats.st_size / 1024
            print(f"ℹ️ {file}: {stats.st_size} bytes ({size_kb:.2f} KB)")

            if file == "script.js" and stats.st_size < 100:
                print(f"⚠️ {file} seems unusually small")
                results[f"{file}_size"] = "WARNING"
            else:
                results[f"{file}_size"] = "PASS"

        except FileNotFoundError:
            print(f"❌ Cannot read {file} stats: File not found")
            results[f"{file}_size"] = "FAIL"
        except Exception as e:
            print(f"❌ Cannot read {file} stats: {e}")
            results[f"{file}_size"] = "FAIL"

    return results


def generate_test_report(all_results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("🧪 LYRIXA COMPREHENSIVE TEST REPORT")
    print("=" * 60)

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0

    for test_category, results in all_results.items():
        print(f"\n📋 {test_category.upper()}:")
        for test_name, result in results.items():
            total_tests += 1
            if result == "PASS":
                passed_tests += 1
                print(f"  ✅ {test_name}: PASS")
            elif result == "FAIL":
                failed_tests += 1
                print(f"  ❌ {test_name}: FAIL")
            elif result == "WARNING":
                warnings += 1
                print(f"  ⚠️ {test_name}: WARNING")
            else:
                print(f"  ℹ️ {test_name}: {result}")

    print(f"\n📊 SUMMARY:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Warnings: {warnings} ⚠️")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if failed_tests == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED! Lyrixa is ready to function!")
    elif failed_tests <= 2:
        print("\n⚠️ Minor issues found. Lyrixa may have limited functionality.")
    else:
        print("\n❌ Major issues found. Lyrixa requires fixes before deployment.")

    return {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "warnings": warnings,
        "success_rate": success_rate,
    }


if __name__ == "__main__":
    print("🧪 LYRIXA BACKEND TESTING SUITE")
    print("Testing Lyrixa functionality and file integrity...\n")

    # Run all tests
    all_results = {}
    all_results["file_existence"] = test_file_existence()
    all_results["script_content"] = test_script_js_content()
    all_results["html_structure"] = test_html_structure()
    all_results["css_styles"] = test_css_styles()
    all_results["file_sizes"] = test_file_sizes()

    # Generate comprehensive report
    summary = generate_test_report(all_results)

    # Save results to JSON for further analysis
    with open("lyrixa_test_results.json", "w") as f:
        json.dump(
            {
                "test_results": all_results,
                "summary": summary,
                "timestamp": "2025-07-04",
            },
            f,
            indent=2,
        )

    print(f"\n💾 Test results saved to: lyrixa_test_results.json")
    print("🚀 Backend testing complete!")
