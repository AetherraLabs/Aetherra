#!/usr/bin/env python3
"""
🔧 LYRIXA ARCHITECTURE CORRECTION
Move Lyrixa to correct location as Aetherra's interface (Aetherra_v2/lyrixa)
"""

import json
import os
import shutil
from datetime import datetime


def create_backup():
    """Create backup before architecture correction"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"Architecture_Correction_Backup_{timestamp}"

    print(f"📦 Creating backup: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)

    # Backup current state
    if os.path.exists("Lyrixa"):
        shutil.copytree("Lyrixa", f"{backup_dir}/Lyrixa_toplevel")

    if os.path.exists("Aetherra_v2/lyrixa"):
        shutil.copytree(
            "Aetherra_v2/lyrixa", f"{backup_dir}/Aetherra_v2_lyrixa_original"
        )

    return backup_dir


def analyze_current_state():
    """Analyze current Lyrixa locations"""
    print("\n🔍 ANALYZING CURRENT LYRIXA LOCATIONS:")
    print("=" * 50)

    locations = [
        ("Lyrixa", "TOP-LEVEL (INCORRECT)"),
        ("Aetherra_v2/lyrixa", "AETHERRA V2 INTERFACE (CORRECT)"),
        ("Aetherra/lyrixa", "OLD AETHERRA LOCATION"),
    ]

    analysis = {}

    for location, label in locations:
        if os.path.exists(location):
            py_files = []
            dirs = []

            for root, directories, filenames in os.walk(location):
                dirs.extend(
                    [
                        os.path.relpath(os.path.join(root, d), location)
                        for d in directories
                    ]
                )
                py_files.extend(
                    [
                        os.path.relpath(os.path.join(root, f), location)
                        for f in filenames
                        if f.endswith(".py")
                    ]
                )

            analysis[location] = {
                "label": label,
                "python_files": len(py_files),
                "directories": len(dirs),
                "exists": True,
            }

            print(f"📁 {label}: {location}")
            print(f"   Python files: {len(py_files)}")
            print(f"   Directories: {len(dirs)}")
        else:
            analysis[location] = {"label": label, "exists": False}
            print(f"❌ {label}: {location} (NOT FOUND)")

    return analysis


def move_lyrixa_to_correct_location():
    """Move top-level Lyrixa to Aetherra_v2/lyrixa (correct architecture)"""
    print(f"\n🔄 CORRECTING LYRIXA ARCHITECTURE:")
    print("=" * 50)

    source = "Lyrixa"
    target = "Aetherra_v2/lyrixa"

    if not os.path.exists(source):
        print(f"❌ Source {source} not found!")
        return False

    # Ensure Aetherra_v2 exists
    os.makedirs("Aetherra_v2", exist_ok=True)

    # If target already exists, merge content
    if os.path.exists(target):
        print(f"📥 Merging {source} into existing {target}")

        # Merge directories and files
        for item in os.listdir(source):
            source_item = f"{source}/{item}"
            target_item = f"{target}/{item}"

            try:
                if os.path.isdir(source_item):
                    if os.path.exists(target_item):
                        # Merge directory contents
                        for sub_item in os.listdir(source_item):
                            sub_source = f"{source_item}/{sub_item}"
                            sub_target = f"{target_item}/{sub_item}"
                            if not os.path.exists(sub_target):
                                if os.path.isdir(sub_source):
                                    shutil.copytree(sub_source, sub_target)
                                else:
                                    shutil.copy2(sub_source, sub_target)
                                print(f"  ✅ Merged {item}/{sub_item}")
                    else:
                        shutil.copytree(source_item, target_item)
                        print(f"  ✅ Moved {item}/")
                else:
                    if not os.path.exists(target_item):
                        shutil.copy2(source_item, target_item)
                        print(f"  ✅ Moved {item}")
            except Exception as e:
                print(f"  ❌ Failed to move {item}: {e}")
    else:
        # Move entire directory
        print(f"📁 Moving {source} to {target}")
        shutil.move(source, target)
        print(f"  ✅ Moved complete directory")

    return True


def cleanup_old_locations():
    """Clean up old/incorrect Lyrixa locations"""
    print(f"\n🧹 CLEANING UP OLD LOCATIONS:")
    print("=" * 40)

    # Remove top-level Lyrixa if it still exists (after moving)
    if os.path.exists("Lyrixa"):
        try:
            shutil.rmtree("Lyrixa")
            print("  ✅ Removed top-level Lyrixa/ (incorrect location)")
        except Exception as e:
            print(f"  ❌ Failed to remove Lyrixa/: {e}")

    # Note about other cleanup
    print("  📝 Manual review recommended:")
    print("     - Aetherra/lyrixa (old content - archive if needed)")
    print("     - Empty lyrixa directories elsewhere")


def update_verification_script():
    """Update the verification script to check correct location"""
    print(f"\n📝 UPDATING VERIFICATION SCRIPT:")

    # Read current verification script
    if os.path.exists("verify_reorganization.py"):
        with open("verify_reorganization.py", "r") as f:
            content = f.read()

        # Update to check Aetherra_v2/lyrixa instead of Lyrixa
        updated_content = (
            content.replace(
                "lyrixa_engine = os.path.exists('Lyrixa/engine')",
                "lyrixa_engine = os.path.exists('Aetherra_v2/lyrixa/engine')",
            )
            .replace(
                "('Lyrixa/engine/prompt_engine.py', 'Prompt Engine')",
                "('Aetherra_v2/lyrixa/engine/prompt_engine.py', 'Prompt Engine')",
            )
            .replace(
                "'🧠 Lyrixa/ = Personality & Cognitive Systems'",
                "'🧠 Aetherra_v2/lyrixa/ = Aetherra Interface & Personality'",
            )
        )

        with open("verify_reorganization.py", "w") as f:
            f.write(updated_content)

        print("  ✅ Updated verification script")


def generate_correction_report(analysis, backup_dir):
    """Generate architecture correction report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "backup_location": backup_dir,
        "correction": "Moved Lyrixa from top-level to Aetherra_v2/lyrixa",
        "architecture_understanding": {
            "before": "Lyrixa as separate system",
            "after": "Lyrixa as Aetherra's interface/personality layer",
        },
        "analysis": analysis,
    }

    report_file = f"architecture_correction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 CORRECTION REPORT: {report_file}")
    return report_file


def main():
    print("🔧 LYRIXA ARCHITECTURE CORRECTION")
    print("=" * 60)
    print(
        "Correcting architecture: Lyrixa is Aetherra's interface, not separate system"
    )

    # Step 1: Create backup
    backup_dir = create_backup()

    # Step 2: Analyze current state
    analysis = analyze_current_state()

    # Step 3: Move Lyrixa to correct location
    success = move_lyrixa_to_correct_location()

    if success:
        # Step 4: Cleanup
        cleanup_old_locations()

        # Step 5: Update verification
        update_verification_script()

        # Step 6: Generate report
        report_file = generate_correction_report(analysis, backup_dir)

        print(f"\n🎉 ARCHITECTURE CORRECTED!")
        print(f"   ✅ Lyrixa now properly located at: Aetherra_v2/lyrixa")
        print(f"   ✅ Understanding: Lyrixa = Aetherra's interface/personality")
        print(f"   📦 Backup: {backup_dir}")
        print(f"   📊 Report: {report_file}")
    else:
        print(f"\n❌ CORRECTION FAILED!")


if __name__ == "__main__":
    main()
