#!/usr/bin/env python3
"""
🧹 AETHERRA CORE CLEANUP
Remove personality/cognitive systems from Aetherra Core per proper architecture
"""

import json
import os
import shutil
from datetime import datetime


def create_backup():
    """Create backup before cleanup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"Aetherra_Core_Cleanup_Backup_{timestamp}"

    print(f"📦 Creating backup: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)

    # Backup what we're about to remove
    items_to_backup = [
        "Aetherra/lyrixa",
        "Aetherra/lyrixa_intelligence.json",
        "Aetherra/lyrixa_aetherra_integration.py",
        "Aetherra/lyrixa_memory",
        "Aetherra/lyrixa_enhanced_memory.db",
        "Aetherra/lyrixa_memory.db",
        "Aetherra/lyrixacore_memory.db",
        "Aetherra/.lyrixa_last_introspection",
    ]

    for item in items_to_backup:
        if os.path.exists(item):
            backup_path = f"{backup_dir}/{os.path.basename(item)}"
            try:
                if os.path.isdir(item):
                    shutil.copytree(item, backup_path)
                else:
                    shutil.copy2(item, backup_path)
                print(f"  ✅ Backed up: {item}")
            except Exception as e:
                print(f"  ❌ Failed to backup {item}: {e}")

    return backup_dir


def analyze_aetherra_violations():
    """Analyze what's incorrectly in Aetherra per architecture rules"""
    print("\\n🔍 ANALYZING AETHERRA CORE VIOLATIONS:")
    print("=" * 60)

    # Items that should NOT be in Aetherra Core
    violations = []

    # Check for personality/cognitive content
    personality_items = [
        "Aetherra/lyrixa",  # Entire personality system
        "Aetherra/lyrixa_intelligence.json",
        "Aetherra/lyrixa_aetherra_integration.py",
        "Aetherra/lyrixa_memory",
        "Aetherra/lyrixa_enhanced_memory.db",
        "Aetherra/lyrixa_memory.db",
        "Aetherra/lyrixacore_memory.db",
        "Aetherra/.lyrixa_last_introspection",
    ]

    for item in personality_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                # Count content
                py_files = 0
                for root, dirs, files in os.walk(item):
                    py_files += len([f for f in files if f.endswith(".py")])
                violations.append(
                    (
                        item,
                        f"Directory with {py_files} Python files",
                        "PERSONALITY_SYSTEM",
                    )
                )
            else:
                violations.append((item, "File", "PERSONALITY_DATA"))

    print(f"🚨 FOUND {len(violations)} ARCHITECTURE VIOLATIONS:")
    for item, desc, category in violations:
        print(f"  ❌ {category}: {item} ({desc})")

    return violations


def remove_violations(violations, backup_dir):
    """Remove items that violate Aetherra Core architecture"""
    print(f"\\n🧹 REMOVING ARCHITECTURE VIOLATIONS:")
    print("=" * 50)

    removed = []
    failed = []

    for item, desc, category in violations:
        try:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                removed.append(item)
                print(f"  ✅ Removed: {item}")
            else:
                print(f"  ⚠️  Already gone: {item}")
        except Exception as e:
            failed.append((item, str(e)))
            print(f"  ❌ Failed to remove {item}: {e}")

    return removed, failed


def verify_aetherra_core_compliance():
    """Verify Aetherra contains only core OS systems"""
    print(f"\\n✅ VERIFYING AETHERRA CORE COMPLIANCE:")
    print("=" * 50)

    # What SHOULD be in Aetherra Core
    expected_core_systems = [
        "kernel/",  # Plugin system, memory kernel
        "runtime/",  # .aether engine, execution
        "interface_bridge/",  # Bridge to Lyrixa
        "security/",  # (if exists)
        "integrations/",  # Discord, webhooks, etc
        "monitoring/",  # (if exists)
        "docs/",  # Documentation
    ]

    print("🧠 EXPECTED AETHERRA CORE SYSTEMS:")
    for system in expected_core_systems:
        path = f"Aetherra/{system}"
        exists = os.path.exists(path)
        status = "✅" if exists else "⚠️"
        print(f"  {status} {system} {'(exists)' if exists else '(missing)'}")

    # Check for any remaining violations
    print(f"\\n🔍 CHECKING FOR REMAINING VIOLATIONS:")
    remaining_lyrixa = []

    for root, dirs, files in os.walk("Aetherra"):
        for item in dirs + files:
            if "lyrixa" in item.lower():
                full_path = os.path.join(root, item)
                remaining_lyrixa.append(full_path)

    if remaining_lyrixa:
        print("  ❌ REMAINING VIOLATIONS:")
        for item in remaining_lyrixa[:10]:  # Show first 10
            print(f"    - {item}")
        if len(remaining_lyrixa) > 10:
            print(f"    ... and {len(remaining_lyrixa) - 10} more")
    else:
        print("  ✅ NO REMAINING VIOLATIONS FOUND")

    return len(remaining_lyrixa) == 0


def verify_lyrixa_location():
    """Verify Lyrixa is properly located as Aetherra's interface"""
    print(f"\\n🧠 VERIFYING LYRIXA LOCATION:")
    print("=" * 40)

    correct_location = "Aetherra_v2/lyrixa"
    exists = os.path.exists(correct_location)

    if exists:
        # Count content
        py_files = 0
        dirs = []
        for root, directories, files in os.walk(correct_location):
            dirs.extend([d for d in directories if d != "__pycache__"])
            py_files += len([f for f in files if f.endswith(".py")])

        print(f"  ✅ Lyrixa properly located at: {correct_location}")
        print(
            f"  📊 Content: {py_files} Python files, {len(set(dirs))} unique directories"
        )

        # Show key components
        main_dirs = [
            d
            for d in os.listdir(correct_location)
            if os.path.isdir(f"{correct_location}/{d}")
        ]
        print(f"  📁 Components: {', '.join(sorted(main_dirs))}")

        return True
    else:
        print(f"  ❌ Lyrixa NOT found at expected location: {correct_location}")
        return False


def generate_cleanup_report(violations, removed, failed, backup_dir):
    """Generate cleanup report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "backup_location": backup_dir,
        "architecture_goal": "Remove personality/cognitive systems from Aetherra Core",
        "violations_found": len(violations),
        "items_removed": len(removed),
        "items_failed": len(failed),
        "removed_items": removed,
        "failed_items": failed,
        "architecture_compliance": {
            "aetherra_core_responsibilities": [
                "Plugin System (Kernel-Level Integration)",
                ".aether Language Engine",
                "Memory Kernel",
                "QFAC Quantum Memory Engine",
                "Goal Scheduler & Runtime Orchestration",
                "Security & Access Control",
                "System Monitoring & Diagnostics",
                "Integration Interfaces",
                "Lyrixa Bridge (Interface Layer Only)",
            ],
            "not_aetherra_responsibilities": [
                "IdentityAgent, SelfModel, Personality, Emotional State",
                "Reflective memory systems",
                "Daily logs, thought graphs, self-coherence loops",
                "Memory introspection, curiosity engines",
                "Social learning patterns and empathy modeling",
            ],
        },
    }

    report_file = (
        f"aetherra_core_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\\n📊 CLEANUP REPORT: {report_file}")
    return report_file


def main():
    print("🧹 AETHERRA CORE CLEANUP")
    print("=" * 60)
    print("🎯 Goal: Remove personality/cognitive systems from Aetherra Core")
    print("📋 Based on proper architecture separation")

    # Step 1: Create backup
    backup_dir = create_backup()

    # Step 2: Analyze violations
    violations = analyze_aetherra_violations()

    if not violations:
        print("\\n🎉 NO VIOLATIONS FOUND - Aetherra Core is already clean!")
        return

    # Step 3: Remove violations
    removed, failed = remove_violations(violations, backup_dir)

    # Step 4: Verify compliance
    compliance = verify_aetherra_core_compliance()

    # Step 5: Verify Lyrixa location
    lyrixa_ok = verify_lyrixa_location()

    # Step 6: Generate report
    report_file = generate_cleanup_report(violations, removed, failed, backup_dir)

    print(f"\\n🎉 AETHERRA CORE CLEANUP COMPLETE!")
    print(f"   📦 Backup: {backup_dir}")
    print(f"   📊 Report: {report_file}")
    print(f"   🧹 Removed: {len(removed)} violations")
    print(f"   ❌ Failed: {len(failed)} items")
    print(f"   ✅ Compliance: {'YES' if compliance else 'NO'}")
    print(f"   🧠 Lyrixa Location: {'CORRECT' if lyrixa_ok else 'INCORRECT'}")


if __name__ == "__main__":
    main()
