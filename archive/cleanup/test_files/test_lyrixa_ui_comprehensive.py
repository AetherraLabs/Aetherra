#!/usr/bin/env python3
"""
Comprehensive Lyrixa UI/GUI Testing Suite
Tests visual elements, interactions, styling, and responsiveness
"""

import json
import os
import re
from datetime import datetime


class LyrixaUITester:
    def __init__(self):
        self.results = {
            "visual_elements": {},
            "css_styling": {},
            "responsiveness": {},
            "interactions": {},
            "accessibility": {},
            "animations": {},
            "browser_compatibility": {},
        }
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def log_test(self, test_name, status, details=""):
        """Log test result"""
        self.test_count += 1
        if status == "PASS":
            self.passed_count += 1
            print(f"✅ {test_name}: {status}")
        elif status == "FAIL":
            self.failed_count += 1
            print(f"❌ {test_name}: {status}")
        else:
            print(f"ℹ️ {test_name}: {status}")

        if details:
            print(f"   📝 {details}")

    def test_visual_elements(self):
        """Test visual UI elements"""
        print("\n🎨 TESTING VISUAL ELEMENTS")
        print("=" * 40)

        # Test HTML structure for Lyrixa elements
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                html_content = f.read()

            # Test navigation button presence
            nav_patterns = [
                r"Lyrixa\s*AI",
                r'onclick="showLyrixaDemo',
                r'class="nav-link"',
            ]

            nav_found = all(
                re.search(pattern, html_content, re.IGNORECASE)
                for pattern in nav_patterns
            )
            self.results["visual_elements"]["navigation_button"] = (
                "PASS" if nav_found else "FAIL"
            )
            self.log_test(
                "Navigation button structure", "PASS" if nav_found else "FAIL"
            )

            # Test for Lyrixa section/demo area
            demo_patterns = [
                r'id="lyrixa"',
                r'class=".*demo.*"',
                r"ai.*assistant",
                r"interactive.*demo",
            ]

            demo_elements = sum(
                1
                for pattern in demo_patterns
                if re.search(pattern, html_content, re.IGNORECASE)
            )
            self.results["visual_elements"]["demo_section"] = (
                "PASS" if demo_elements >= 1 else "FAIL"
            )
            self.log_test(
                "Demo section elements",
                "PASS" if demo_elements >= 1 else "FAIL",
                f"Found {demo_elements} demo-related elements",
            )

            # Test for proper HTML structure
            structure_tests = {
                "head_section": r"<head>.*</head>",
                "body_section": r"<body>.*</body>",
                "nav_section": r"<nav>.*</nav>",
                "script_tags": r"<script.*src.*script\.js",
            }

            for test_name, pattern in structure_tests.items():
                found = bool(
                    re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                )
                self.results["visual_elements"][test_name] = "PASS" if found else "FAIL"
                self.log_test(f"HTML {test_name}", "PASS" if found else "FAIL")

        else:
            self.log_test("HTML file existence", "FAIL", "index.html not found")

    def test_css_styling(self):
        """Test CSS styling and visual design"""
        print("\n🎨 TESTING CSS STYLING")
        print("=" * 40)

        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                css_content = f.read()

            # Test Lyrixa-specific CSS classes
            css_tests = {
                "highlight_demo_class": r"\.highlight-demo",
                "animation_keyframes": r"@keyframes\s+highlight-pulse",
                "gradient_background": r"linear-gradient",
                "animation_duration": r"3s",
                "border_radius": r"border-radius",
                "opacity_transitions": r"opacity.*0.*1|opacity.*1.*0",
                "box_shadow": r"box-shadow",
                "position_absolute": r"position:\s*absolute",
            }

            for test_name, pattern in css_tests.items():
                found = bool(re.search(pattern, css_content, re.IGNORECASE))
                self.results["css_styling"][test_name] = "PASS" if found else "FAIL"
                self.log_test(f"CSS {test_name}", "PASS" if found else "FAIL")

            # Test color scheme variables
            color_vars = [r"--crystal-blue", r"--jade-green", r"--intelligence-purple"]

            color_count = sum(1 for var in color_vars if re.search(var, css_content))
            self.results["css_styling"]["color_variables"] = (
                "PASS" if color_count >= 2 else "PARTIAL"
            )
            self.log_test(
                "Color scheme variables",
                "PASS" if color_count >= 2 else "PARTIAL",
                f"Found {color_count}/3 color variables",
            )

            # Test responsive design elements
            responsive_tests = {
                "media_queries": r"@media.*screen",
                "flexible_units": r"(rem|em|%|vw|vh)",
                "max_width": r"max-width",
                "min_width": r"min-width",
            }

            for test_name, pattern in responsive_tests.items():
                found = bool(re.search(pattern, css_content, re.IGNORECASE))
                self.results["responsiveness"][test_name] = "PASS" if found else "INFO"
                self.log_test(f"Responsive {test_name}", "PASS" if found else "INFO")

        else:
            self.log_test("CSS file existence", "FAIL", "styles.css not found")

    def test_javascript_interactions(self):
        """Test JavaScript interactions and functionality"""
        print("\n⚡ TESTING JAVASCRIPT INTERACTIONS")
        print("=" * 40)

        if os.path.exists("script.js"):
            with open("script.js", "r", encoding="utf-8") as f:
                js_content = f.read()

            # Test showLyrixaDemo function
            function_tests = {
                "function_declaration": r"function\s+showLyrixaDemo\s*\(",
                "element_selection": r"getElementById\(.*lyrixa",
                "querySelector_fallback": r"querySelector\(",
                "smooth_scroll": r"scrollIntoView.*smooth",
                "class_manipulation": r"classList\.(add|remove)",
                "timeout_cleanup": r"setTimeout",
                "return_statement": r"return\s*(false|true)",
                "error_handling": r"if\s*\(\s*demo\s*\)",
            }

            for test_name, pattern in function_tests.items():
                found = bool(re.search(pattern, js_content, re.IGNORECASE))
                self.results["interactions"][test_name] = "PASS" if found else "FAIL"
                self.log_test(f"JS {test_name}", "PASS" if found else "FAIL")

            # Test function robustness
            fallback_count = len(re.findall(r"querySelector\(", js_content))
            self.results["interactions"]["fallback_selectors"] = (
                "PASS" if fallback_count >= 3 else "PARTIAL"
            )
            self.log_test(
                "Fallback selectors",
                "PASS" if fallback_count >= 3 else "PARTIAL",
                f"Found {fallback_count} fallback selectors",
            )

        else:
            self.log_test("JavaScript file existence", "FAIL", "script.js not found")

    def test_animations(self):
        """Test animation implementation and timing"""
        print("\n🎬 TESTING ANIMATIONS")
        print("=" * 40)

        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                css_content = f.read()

            # Extract keyframe animation details
            keyframe_match = re.search(
                r"@keyframes\s+highlight-pulse\s*{([^}]+)}", css_content, re.DOTALL
            )
            if keyframe_match:
                keyframe_content = keyframe_match.group(1)

                animation_tests = {
                    "0_percent_keyframe": r"0%.*{",
                    "50_percent_keyframe": r"50%.*{",
                    "100_percent_keyframe": r"100%.*{",
                    "opacity_animation": r"opacity.*0",
                    "box_shadow_animation": r"box-shadow.*rgba",
                }

                for test_name, pattern in animation_tests.items():
                    found = bool(re.search(pattern, keyframe_content, re.IGNORECASE))
                    self.results["animations"][test_name] = "PASS" if found else "FAIL"
                    self.log_test(f"Animation {test_name}", "PASS" if found else "FAIL")

            # Test animation properties
            highlight_demo_match = re.search(
                r"\.highlight-demo[^{]*{([^}]+)}", css_content, re.DOTALL
            )
            if highlight_demo_match:
                demo_css = highlight_demo_match.group(1)

                demo_tests = {
                    "position_relative": r"position:\s*relative",
                    "z_index": r"z-index:\s*\d+",
                    "pseudo_element": r"::before" in css_content,
                }

                for test_name, pattern in demo_tests.items():
                    if test_name == "pseudo_element":
                        found = pattern
                    else:
                        found = bool(re.search(pattern, demo_css, re.IGNORECASE))
                    self.results["animations"][test_name] = "PASS" if found else "FAIL"
                    self.log_test(f"Animation {test_name}", "PASS" if found else "FAIL")

        # Test animation timing from JavaScript
        if os.path.exists("script.js"):
            with open("script.js", "r", encoding="utf-8") as f:
                js_content = f.read()

            timeout_match = re.search(r"setTimeout.*(\d+)", js_content)
            if timeout_match:
                timeout_value = int(timeout_match.group(1))
                timing_correct = timeout_value == 3000
                self.results["animations"]["timing_sync"] = (
                    "PASS" if timing_correct else "FAIL"
                )
                self.log_test(
                    "Animation timing sync",
                    "PASS" if timing_correct else "FAIL",
                    f"Timeout: {timeout_value}ms (expected: 3000ms)",
                )

    def test_accessibility(self):
        """Test accessibility features"""
        print("\n♿ TESTING ACCESSIBILITY")
        print("=" * 40)

        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                html_content = f.read()

            accessibility_tests = {
                "alt_attributes": r"alt=",
                "aria_labels": r"aria-label",
                "lang_attribute": r"<html.*lang=",
                "meta_viewport": r"<meta.*viewport",
                "heading_structure": r"<h[1-6]",
                "semantic_nav": r"<nav>",
                "keyboard_navigation": r"tabindex|onclick.*return\s+false",
            }

            for test_name, pattern in accessibility_tests.items():
                found = bool(re.search(pattern, html_content, re.IGNORECASE))
                self.results["accessibility"][test_name] = "PASS" if found else "INFO"
                self.log_test(f"Accessibility {test_name}", "PASS" if found else "INFO")

    def test_browser_compatibility(self):
        """Test browser compatibility features"""
        print("\n🌐 TESTING BROWSER COMPATIBILITY")
        print("=" * 40)

        if os.path.exists("script.js"):
            with open("script.js", "r", encoding="utf-8") as f:
                js_content = f.read()

            compatibility_tests = {
                "modern_js_methods": r"(querySelector|addEventListener|classList)",
                "fallback_logic": r"getElementById.*querySelector",
                "cross_browser_scroll": r"scrollIntoView",
                "es6_features": r"(const|let|=>|\.\.\.)",
            }

            for test_name, pattern in compatibility_tests.items():
                found = bool(re.search(pattern, js_content, re.IGNORECASE))
                self.results["browser_compatibility"][test_name] = (
                    "PASS" if found else "INFO"
                )
                self.log_test(f"Compatibility {test_name}", "PASS" if found else "INFO")

        if os.path.exists("styles.css"):
            with open("styles.css", "r", encoding="utf-8") as f:
                css_content = f.read()

            css_compatibility_tests = {
                "vendor_prefixes": r"(-webkit-|-moz-|-ms-|-o-)",
                "css3_features": r"(transform|transition|animation|gradient)",
                "flexbox": r"(display:\s*flex|flex-)",
                "grid": r"(display:\s*grid|grid-)",
            }

            for test_name, pattern in css_compatibility_tests.items():
                found = bool(re.search(pattern, css_content, re.IGNORECASE))
                self.results["browser_compatibility"][test_name] = (
                    "PASS" if found else "INFO"
                )
                self.log_test(f"CSS {test_name}", "PASS" if found else "INFO")

    def run_all_tests(self):
        """Run all UI tests"""
        print("🖥️ LYRIXA UI/GUI COMPREHENSIVE TESTING SUITE")
        print("=" * 60)
        print("Testing visual elements, styling, interactions, and user experience...")

        self.test_visual_elements()
        self.test_css_styling()
        self.test_javascript_interactions()
        self.test_animations()
        self.test_accessibility()
        self.test_browser_compatibility()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🖥️ LYRIXA UI/GUI TEST SUMMARY")
        print("=" * 60)

        success_rate = (
            (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        )

        print("📊 RESULTS:")
        print(f"  Total Tests: {self.test_count}")
        print(f"  Passed: {self.passed_count} ✅")
        print(f"  Failed: {self.failed_count} ❌")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Category breakdown
        print("\n📋 CATEGORY BREAKDOWN:")
        for category, tests in self.results.items():
            category_pass = sum(1 for result in tests.values() if result == "PASS")
            category_total = len(tests)
            category_rate = (
                (category_pass / category_total * 100) if category_total > 0 else 0
            )
            print(
                f"  {category.replace('_', ' ').title()}: {category_pass}/{category_total} ({category_rate:.1f}%)"
            )

        # Overall status
        if success_rate >= 90:
            status = "🎉 EXCELLENT - UI is production ready!"
        elif success_rate >= 80:
            status = "✅ GOOD - Minor improvements recommended"
        elif success_rate >= 70:
            status = "⚠️ FAIR - Some issues need attention"
        else:
            status = "❌ NEEDS WORK - Significant improvements required"

        print(f"\n🚀 OVERALL STATUS: {status}")

        # Save results
        self.save_results()
        print("\n💾 Results saved to: lyrixa_ui_test_results.json")
        print("🎯 UI testing complete!")

    def save_results(self):
        """Save test results to JSON file"""
        output = {
            "test_summary": {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": self.test_count,
                "passed": self.passed_count,
                "failed": self.failed_count,
                "success_rate": round(
                    (self.passed_count / self.test_count * 100)
                    if self.test_count > 0
                    else 0,
                    2,
                ),
            },
            "detailed_results": self.results,
            "status": "UI testing completed",
        }

        with open("lyrixa_ui_test_results.json", "w") as f:
            json.dump(output, f, indent=2)


def main():
    """Main test execution"""
    tester = LyrixaUITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
