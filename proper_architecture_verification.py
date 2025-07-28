#!/usr/bin/env python3
"""
🎯 PROPER ARCHITECTURE VERIFICATION
Verify compliance with correct Aetherra Core vs Lyrixa separation
"""

import os


def verify_aetherra_core_responsibilities():
    """Verify Aetherra contains only core OS systems"""
    print("🧠 VERIFYING AETHERRA CORE RESPONSIBILITIES:")
    print("=" * 60)

    # Expected Aetherra Core systems per architecture spec
    expected_systems = {
        "kernel/": "🧩 Plugin System (Kernel-Level Integration)",
        "runtime/": "📜 .aether Language Engine",
        "interface_bridge/": "🧠 Lyrixa Bridge (Interface Layer Only)",
        "integrations/": "🔌 Integration Interfaces",
        "security/": "🔒 Security & Access Control (optional)",
        "monitoring/": "📊 System Monitoring & Diagnostics (optional)",
    }

    found_systems = []

    for system, description in expected_systems.items():
        path = f"Aetherra/{system}"
        exists = os.path.exists(path)

        if exists:
            py_count = 0
            for root, dirs, files in os.walk(path):
                py_count += len([f for f in files if f.endswith(".py")])
            found_systems.append(system)
            print(f"  ✅ {description}")
            print(f"      📁 {system} ({py_count} Python files)")
        else:
            status = "⚠️" if "optional" in description else "❌"
            print(f"  {status} {description}")
            print(f"      📁 {system} (not found)")

    return found_systems


def verify_no_personality_in_aetherra():
    """Verify no personality/cognitive systems in Aetherra"""
    print("\n🚫 VERIFYING NO PERSONALITY SYSTEMS IN AETHERRA:")
    print("=" * 60)

    # Things that should NOT be in Aetherra Core
    forbidden_patterns = [
        "identity",
        "personality",
        "emotional",
        "self_model",
        "reflection",
        "curiosity",
        "empathy",
        "narrative",
        "contradiction",
        "social_learning",
        "thought_graph",
    ]

    violations = []

    for root, dirs, files in os.walk("Aetherra"):
        for item in dirs + files:
            item_lower = item.lower()
            for pattern in forbidden_patterns:
                if pattern in item_lower and "backup" not in root.lower():
                    violations.append(os.path.join(root, item))
                    break

    if violations:
        print(f"❌ FOUND {len(violations)} PERSONALITY VIOLATIONS:")
        for violation in violations[:10]:  # Show first 10
            print(f"  - {violation}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more")
        return False
    else:
        print("✅ NO PERSONALITY SYSTEMS FOUND IN AETHERRA CORE")
        return True


def verify_lyrixa_as_interface():
    """Verify Lyrixa is properly positioned as Aetherra's interface"""
    print("\n🧠 VERIFYING LYRIXA AS AETHERRA'S INTERFACE:")
    print("=" * 60)

    lyrixa_path = "Aetherra_v2/lyrixa"

    if not os.path.exists(lyrixa_path):
        print("❌ LYRIXA NOT FOUND AT EXPECTED LOCATION")
        return False

    # Check Lyrixa components
    expected_lyrixa_components = [
        "engine/",
        "personality/",
        "memory/",
        "agents/",
        "emotions/",
        "reflection/",
        "gui/",
        "plugins/",
    ]

    found_components = []
    for component in expected_lyrixa_components:
        component_path = f"{lyrixa_path}/{component}"
        if os.path.exists(component_path):
            py_count = 0
            for root, dirs, files in os.walk(component_path):
                py_count += len([f for f in files if f.endswith(".py")])
            found_components.append(component)
            print(f"  ✅ {component} ({py_count} Python files)")
        else:
            print(f"  ❌ {component} (not found)")

    # Count total content
    total_py = 0
    total_dirs = 0
    for root, dirs, files in os.walk(lyrixa_path):
        total_dirs += len(dirs)
        total_py += len([f for f in files if f.endswith(".py")])

    print(f"\n📊 LYRIXA SUMMARY:")
    print(f"  📁 Location: {lyrixa_path}")
    print(f"  🐍 Python files: {total_py}")
    print(f"  📂 Directories: {total_dirs}")
    print(f"  🧩 Components: {len(found_components)}/{len(expected_lyrixa_components)}")

    return len(found_components) >= 6  # Most components should exist


def verify_interface_bridge():
    """Verify clean interface bridge exists"""
    print("\n🌉 VERIFYING INTERFACE BRIDGE:")
    print("=" * 40)

    bridge_path = "Aetherra/interface_bridge"

    if not os.path.exists(bridge_path):
        print("❌ INTERFACE BRIDGE NOT FOUND")
        return False

    bridge_files = [f for f in os.listdir(bridge_path) if f.endswith(".py")]

    for bridge_file in bridge_files:
        print(f"  ✅ {bridge_file}")

    print(f"  📊 Bridge APIs: {len(bridge_files)}")

    return len(bridge_files) > 0


def check_directory_count():
    """Check we have only one lyrixa directory (as Aetherra's interface)"""
    print("\n📊 VERIFYING SINGLE LYRIXA DIRECTORY:")
    print("=" * 50)

    lyrixa_dirs = []
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if "lyrixa" in d.lower() and not any(
                x in root.lower() for x in ["backup", "archive", "unused"]
            ):
                full_path = os.path.join(root, d).replace(".\\\\", "")
                lyrixa_dirs.append(full_path)

    print(f"📈 TOTAL LYRIXA DIRECTORIES: {len(lyrixa_dirs)}")

    correct_location = "Aetherra_v2\\\\lyrixa"

    for i, location in enumerate(sorted(lyrixa_dirs), 1):
        if location == correct_location:
            print(f"  ✅ {i}. {location} (CORRECT - Aetherra's interface)")
        else:
            print(f"  ⚠️  {i}. {location} (legacy/cleanup needed)")

    active_locations = len([loc for loc in lyrixa_dirs if loc == correct_location])
    return active_locations == 1


def main():
    print("🎯 PROPER ARCHITECTURE VERIFICATION")
    print("=" * 70)
    print("✅ GOAL: Verify Lyrixa is Aetherra's interface, not separate system")

    # Step 1: Verify Aetherra Core
    aetherra_systems = verify_aetherra_core_responsibilities()

    # Step 2: Verify no personality in Aetherra
    no_personality = verify_no_personality_in_aetherra()

    # Step 3: Verify Lyrixa as interface
    lyrixa_ok = verify_lyrixa_as_interface()

    # Step 4: Verify interface bridge
    bridge_ok = verify_interface_bridge()

    # Step 5: Check directory count
    single_lyrixa = check_directory_count()

    # Final assessment
    print("\n🏆 FINAL ARCHITECTURE ASSESSMENT:")
    print("=" * 50)

    core_score = len(aetherra_systems)
    max_core = 6  # Expected core systems

    checks = [
        ("Aetherra Core Systems", f"{core_score}/{max_core}", core_score >= 3),
        ("No Personality in Aetherra", "Clean", no_personality),
        ("Lyrixa as Interface", "Positioned", lyrixa_ok),
        ("Interface Bridge", "Present", bridge_ok),
        ("Single Lyrixa Directory", "Achieved", single_lyrixa),
    ]

    passed = 0
    for check_name, status, result in checks:
        icon = "✅" if result else "❌"
        print(f"  {icon} {check_name}: {status}")
        if result:
            passed += 1

    total_checks = len(checks)
    success_rate = (passed / total_checks) * 100

    print(
        f"\n📊 ARCHITECTURE COMPLIANCE: {passed}/{total_checks} ({success_rate:.0f}%)"
    )

    if success_rate >= 80:
        print("🎉 EXCELLENT! Proper architecture achieved!")
        print("   🧠 Lyrixa correctly positioned as Aetherra's interface")
        print("   📁 Clean separation between core OS and personality systems")
    else:
        print("⚠️  Architecture needs refinement")


if __name__ == "__main__":
    main()
