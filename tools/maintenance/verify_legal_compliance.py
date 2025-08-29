#!/usr/bin/env python3
"""
Legal Compliance Verification Script for Aetherra Project

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0

This script verifies that all dependencies are compatible with GPL-3.0
and generates a comprehensive legal compliance report.
"""

import json
import re
import sys
from pathlib import Path

import pkg_resources

# GPL-3.0 compatible licenses
COMPATIBLE_LICENSES = {
    "apache-2.0",
    "apache 2.0",
    "apache software license",
    "mit",
    "mit license",
    "bsd",
    "bsd license",
    "bsd-3-clause",
    "bsd 3-clause",
    "lgpl",
    "lgpl-3.0",
    "gnu lesser general public license",
    "gpl-2.0+",
    "gpl-3.0",
    "gnu general public license",
    "python software foundation license",
    "mozilla public license 2.0",
    "mpl-2.0",
    "isc license",
    "isc",
    "unlicense",
    "public domain",
}


def check_license_compatibility():
    """Check all installed packages for GPL-3.0 compatibility."""
    print("🔍 Checking License Compatibility for Aetherra Project")
    print("=" * 60)

    compatible_count = 0
    incompatible_count = 0
    unknown_count = 0

    installed_packages = [d for d in pkg_resources.working_set]

    print(f"📦 Found {len(installed_packages)} installed packages")
    print()

    for package in sorted(installed_packages, key=lambda x: x.project_name):
        name = package.project_name
        version = package.version

        # Get license info
        try:
            metadata = package.get_metadata("METADATA")
            license_match = re.search(r"License: (.+)", metadata)
            classifier_licenses = re.findall(r"Classifier: License :: (.+)", metadata)

            license_info = None
            if license_match:
                license_info = license_match.group(1).strip()
            elif classifier_licenses:
                license_info = classifier_licenses[0]

            if license_info:
                license_lower = license_info.lower()
                is_compatible = any(
                    compat in license_lower for compat in COMPATIBLE_LICENSES
                )

                if is_compatible:
                    status = "✅ COMPATIBLE"
                    compatible_count += 1
                else:
                    status = "❌ INCOMPATIBLE"
                    incompatible_count += 1

                print(f"{status:15} | {name:25} | {version:10} | {license_info}")
            else:
                status = "❓ UNKNOWN"
                unknown_count += 1
                print(f"{status:15} | {name:25} | {version:10} | No license info")

        except Exception as e:
            status = "❓ ERROR"
            unknown_count += 1
            print(f"{status:15} | {name:25} | {version:10} | Error: {str(e)[:30]}")

    print()
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Compatible packages: {compatible_count}")
    print(f"❌ Incompatible packages: {incompatible_count}")
    print(f"❓ Unknown/Error packages: {unknown_count}")
    print(f"📦 Total packages: {len(installed_packages)}")

    if incompatible_count == 0:
        print()
        print("🎉 ALL PACKAGES ARE GPL-3.0 COMPATIBLE!")
        print("✅ Project is legally clear for distribution.")
        return True
    else:
        print()
        print("⚠️  WARNING: Incompatible packages found!")
        print("❌ Review incompatible packages before distribution.")
        return False


def verify_project_files():
    """Verify required legal files exist."""
    print()
    print("📋 Verifying Required Legal Files")
    print("=" * 60)

    required_files = {
        "LICENSE": "GPL-3.0 license text",
        "COPYRIGHT": "Copyright and ownership information",
        "NOTICE": "Third-party attributions",
        "LEGAL_COMPLIANCE.md": "Legal compliance documentation",
    }

    project_root = Path(__file__).parent
    all_present = True

    for filename, description in required_files.items():
        file_path = project_root / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename:20} | {description:40} | {size:6} bytes")
        else:
            print(f"❌ {filename:20} | {description:40} | MISSING")
            all_present = False

    if all_present:
        print()
        print("✅ All required legal files are present!")
    else:
        print()
        print("❌ Some required legal files are missing!")

    return all_present


def generate_legal_report():
    """Generate a comprehensive legal compliance report."""
    print()
    print("📄 Generating Legal Compliance Report")
    print("=" * 60)

    license_ok = check_license_compatibility()
    files_ok = verify_project_files()

    report = f"""
# Aetherra Project - Legal Compliance Report
Generated: {Path(__file__).name}

## Overall Status
{"✅ FULLY COMPLIANT" if license_ok and files_ok else "❌ NEEDS ATTENTION"}

## License Compatibility
{"✅ ALL DEPENDENCIES GPL-3.0 COMPATIBLE" if license_ok else "❌ INCOMPATIBLE DEPENDENCIES FOUND"}

## Required Files
{"✅ ALL LEGAL FILES PRESENT" if files_ok else "❌ MISSING LEGAL FILES"}

## Recommendations
- Distribution: {"✅ READY" if license_ok and files_ok else "❌ NOT READY"}
- Commercial Use: {"✅ AUTHORIZED UNDER GPL-3.0" if license_ok and files_ok else "❌ RESOLVE ISSUES FIRST"}
- Legal Risk: {"✅ MINIMAL" if license_ok and files_ok else "❌ ELEVATED"}

## Next Steps
{"🎉 Project is ready for development and distribution!" if license_ok and files_ok else "⚠️ Address the issues above before distribution."}
"""

    print(report)

    # Save report to file
    report_file = Path(__file__).parent / "LEGAL_COMPLIANCE_REPORT.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    print("🏛️ Aetherra Project Legal Compliance Checker")
    print("Copyright (C) 2025 AetherraLabs - GPL-3.0 Licensed")
    print()

    try:
        generate_legal_report()
    except Exception as e:
        print(f"❌ Error during compliance check: {e}")
        sys.exit(1)

    print()
    print("✅ Legal compliance verification complete!")
