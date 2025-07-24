#!/usr/bin/env python3
"""
🛡️ LYRIXA CORRUPTION PREVENTION & RECOVERY SYSTEM
==================================================

This script provides comprehensive protection against file corruption:
1. Safe file operations for all critical writes
2. Automated backup system
3. Corruption detection and recovery
4. System health monitoring

Run this periodically to maintain system integrity.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def main():
    print("🛡️ LYRIXA CORRUPTION PREVENTION & RECOVERY SYSTEM")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    overall_health = True

    # Step 1: Run corruption detection
    print("🔍 STEP 1: CORRUPTION DETECTION")
    print("-" * 40)

    try:
        from corruption_detector import run_corruption_check

        corruption_healthy = run_corruption_check()

        if corruption_healthy:
            print("✅ Corruption check: PASSED")
        else:
            print("⚠️ Corruption check: ISSUES FOUND")
            overall_health = False

    except Exception as e:
        print(f"❌ Corruption check failed: {e}")
        overall_health = False

    print()

    # Step 2: Create backup
    print("🔄 STEP 2: SYSTEM BACKUP")
    print("-" * 40)

    try:
        from lyrixa_backup_system import run_automated_backup

        backup_success = run_automated_backup("automated")

        if backup_success:
            print("✅ Backup creation: SUCCESS")
        else:
            print("❌ Backup creation: FAILED")
            overall_health = False

    except Exception as e:
        print(f"❌ Backup failed: {e}")
        overall_health = False

    print()

    # Step 3: Test safe file operations
    print("🛡️ STEP 3: SAFE FILE OPERATIONS TEST")
    print("-" * 40)

    try:
        from safe_file_operations import check_for_corruption, get_safe_writer

        # Test safe writer
        safe_writer = get_safe_writer()
        test_content = f"Test file created at {datetime.now().isoformat()}"
        test_success = safe_writer.safe_write("test_safe_operations.txt", test_content)

        if test_success:
            print("✅ Safe file operations: WORKING")
            # Clean up test file
            try:
                os.remove("test_safe_operations.txt")
            except:
                pass
        else:
            print("❌ Safe file operations: FAILED")
            overall_health = False

        # Check for any corruption in safe operations
        corruption_report = check_for_corruption()
        if corruption_report.get("corruption_events", 0) > 0:
            print(
                f"⚠️ Previous corruption events: {corruption_report['corruption_events']}"
            )
            if corruption_report.get("recent_errors", []):
                print("   Recent errors detected in safe operations")
                overall_health = False

    except Exception as e:
        print(f"❌ Safe operations test failed: {e}")
        overall_health = False

    print()

    # Step 4: Integration test
    print("🔗 STEP 4: INTEGRATION HEALTH CHECK")
    print("-" * 40)

    try:
        # Test critical imports
        from lyrixa.core.multi_agent_system import LyrixaMultiAgentSystem
        from lyrixa.core.plugin_system import LyrixaPluginSystem
        from modern_lyrixa_gui import ModernLyrixaGUI

        print("✅ Critical imports: WORKING")

        # Quick initialization test
        try:
            ps = LyrixaPluginSystem()
            mas = LyrixaMultiAgentSystem()
            print(f"✅ System initialization: WORKING")
            print(f"   - Plugins found: {len(ps.installed_plugins)}")
            print(f"   - Agents created: {len(mas.agents)}")
        except Exception as e:
            print(f"⚠️ System initialization issues: {e}")
            overall_health = False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        overall_health = False

    print()

    # Step 5: Summary and recommendations
    print("📊 STEP 5: SYSTEM HEALTH SUMMARY")
    print("-" * 40)

    if overall_health:
        print("🎉 SYSTEM HEALTH: ✅ EXCELLENT")
        print()
        print("✅ All corruption prevention measures are working")
        print("✅ Backups are being created successfully")
        print("✅ Safe file operations are functional")
        print("✅ All core systems are integrated properly")
        print()
        print("🛡️ Your Lyrixa system is protected against corruption!")
    else:
        print("⚠️ SYSTEM HEALTH: ⚠️ NEEDS ATTENTION")
        print()
        print("🔧 RECOMMENDED ACTIONS:")
        print("1. Check error messages above for specific issues")
        print("2. Ensure all dependencies are installed")
        print("3. Run individual test scripts to isolate problems")
        print("4. Consider restoring from a recent backup if issues persist")

    print()
    print("🔄 AUTOMATION RECOMMENDATIONS:")
    print("- Run this script daily for optimal protection")
    print("- Set up hourly backups for active development")
    print("- Monitor the corruption logs regularly")
    print()
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return overall_health


def schedule_protection():
    """Set up automated protection (for future enhancement)"""
    print("🕐 SCHEDULING AUTOMATED PROTECTION")
    print("-" * 40)
    print("Future enhancement: Set up cron jobs or Windows Task Scheduler")
    print("Recommended schedule:")
    print("- Corruption scan: Every hour")
    print("- Full backup: Daily at 2 AM")
    print("- Critical backup: Every 4 hours")
    print("- Safe operation test: Weekly")


if __name__ == "__main__":
    success = main()

    print("\n🔧 ADDITIONAL TOOLS AVAILABLE:")
    print("- corruption_detector.py - Detailed corruption scanning")
    print("- lyrixa_backup_system.py - Manual backup creation")
    print("- safe_file_operations.py - Test safe file writing")

    if not success:
        print("\n⚠️ ATTENTION REQUIRED: System health issues detected")
        sys.exit(1)
    else:
        print("\n✅ ALL SYSTEMS HEALTHY: Corruption protection active")
        sys.exit(0)
