#!/usr/bin/env python3
"""
🔍 LYRIXA CORRUPTION DETECTOR
=============================

Detects and reports file corruption issues in the Lyrixa system.
Monitors critical files and attempts recovery when possible.
"""

import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class CorruptionDetector:
    """Detects and monitors file corruption in Lyrixa"""

    def __init__(self, monitor_dir: str = "."):
        self.monitor_dir = Path(monitor_dir)
        self.corruption_log = Path("backups/corruption_detector.json")
        self.corruption_log.parent.mkdir(exist_ok=True)

        # Critical files to monitor
        self.critical_files = [
            "modern_lyrixa_gui.py",
            "lyrixa/core/plugin_system.py",
            "lyrixa/core/multi_agent_system.py",
            "lyrixa/core/advanced_vector_memory.py",
            "safe_file_operations.py",
            "lyrixa_backup_system.py",
        ]

        # File signatures to detect empty/corrupted files
        self.expected_signatures = {
            "modern_lyrixa_gui.py": [
                "class ModernLyrixaGUI",
                "class PluginManagerDialog",
            ],
            "lyrixa/core/plugin_system.py": [
                "class LyrixaPluginSystem",
                "def install_plugin",
            ],
            "lyrixa/core/multi_agent_system.py": [
                "class LyrixaMultiAgentSystem",
                "class AgentRole",
            ],
        }

    def scan_for_corruption(self) -> Dict[str, Any]:
        """Scan all critical files for corruption"""
        print("🔍 SCANNING FOR FILE CORRUPTION")
        print("=" * 40)

        corruption_report = {
            "scan_time": datetime.now().isoformat(),
            "files_scanned": 0,
            "corrupted_files": [],
            "empty_files": [],
            "missing_files": [],
            "suspicious_files": [],
            "total_issues": 0,
        }

        for file_path_str in self.critical_files:
            file_path = Path(file_path_str)
            corruption_report["files_scanned"] += 1

            print(f"📄 Checking {file_path}...")

            if not file_path.exists():
                print(f"   [ERROR] MISSING: File not found")
                corruption_report["missing_files"].append(str(file_path))
                corruption_report["total_issues"] += 1
                continue

            # Check if file is empty
            try:
                file_size = file_path.stat().st_size
                if file_size == 0:
                    print(f"   [ERROR] EMPTY: File is completely empty")
                    corruption_report["empty_files"].append(str(file_path))
                    corruption_report["total_issues"] += 1
                    continue

                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for expected signatures
                if str(file_path) in self.expected_signatures:
                    missing_signatures = []
                    for signature in self.expected_signatures[str(file_path)]:
                        if signature not in content:
                            missing_signatures.append(signature)

                    if missing_signatures:
                        print(f"   [WARN] SUSPICIOUS: Missing expected content")
                        corruption_report["suspicious_files"].append(
                            {
                                "file": str(file_path),
                                "missing_signatures": missing_signatures,
                                "file_size": file_size,
                            }
                        )
                        corruption_report["total_issues"] += 1
                        continue

                # Check for signs of corruption
                corruption_indicators = self._detect_corruption_indicators(content)
                if corruption_indicators:
                    print(f"   [ERROR] CORRUPTED: {', '.join(corruption_indicators)}")
                    corruption_report["corrupted_files"].append(
                        {
                            "file": str(file_path),
                            "indicators": corruption_indicators,
                            "file_size": file_size,
                        }
                    )
                    corruption_report["total_issues"] += 1
                    continue

                print(f"   ✅ OK: File appears healthy")

            except Exception as e:
                print(f"   [ERROR] ERROR: Could not read file - {e}")
                corruption_report["corrupted_files"].append(
                    {"file": str(file_path), "error": str(e)}
                )
                corruption_report["total_issues"] += 1

        # Log the corruption report
        self._log_corruption_report(corruption_report)

        # Print summary
        print(f"\n📊 CORRUPTION SCAN SUMMARY:")
        print(f"   Files scanned: {corruption_report['files_scanned']}")
        print(f"   Issues found: {corruption_report['total_issues']}")
        print(f"   Missing files: {len(corruption_report['missing_files'])}")
        print(f"   Empty files: {len(corruption_report['empty_files'])}")
        print(f"   Corrupted files: {len(corruption_report['corrupted_files'])}")
        print(f"   Suspicious files: {len(corruption_report['suspicious_files'])}")

        return corruption_report

    def attempt_recovery(self, corruption_report: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover corrupted files from backups"""
        print("\n🛠️ ATTEMPTING FILE RECOVERY")
        print("=" * 40)

        recovery_report = {
            "recovery_time": datetime.now().isoformat(),
            "attempted_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": [],
            "recovery_details": [],
        }

        # Try to recover empty and missing files
        problematic_files = (
            corruption_report["empty_files"]
            + corruption_report["missing_files"]
            + [item["file"] for item in corruption_report["corrupted_files"]]
        )

        for file_path_str in problematic_files:
            file_path = Path(file_path_str)
            recovery_report["attempted_recoveries"] += 1

            print(f"[TOOL] Attempting to recover {file_path}...")

            # Look for backup files
            backup_found = self._find_and_restore_backup(file_path)

            if backup_found:
                print(f"   ✅ Recovered from backup")
                recovery_report["successful_recoveries"] += 1
                recovery_report["recovery_details"].append(
                    {
                        "file": str(file_path),
                        "status": "recovered",
                        "method": "backup_restore",
                    }
                )
            else:
                print(f"   [ERROR] No backup found")
                recovery_report["failed_recoveries"].append(str(file_path))
                recovery_report["recovery_details"].append(
                    {
                        "file": str(file_path),
                        "status": "failed",
                        "reason": "no_backup_available",
                    }
                )

        print(f"\n📊 RECOVERY SUMMARY:")
        print(f"   Recovery attempts: {recovery_report['attempted_recoveries']}")
        print(f"   Successful: {recovery_report['successful_recoveries']}")
        print(f"   Failed: {len(recovery_report['failed_recoveries'])}")

        return recovery_report

    def _detect_corruption_indicators(self, content: str) -> List[str]:
        """Detect indicators of file corruption"""
        indicators = []

        # Check for null bytes (binary corruption)
        if "\x00" in content:
            indicators.append("null_bytes")

        # Check for extremely short content
        if len(content.strip()) < 10:
            indicators.append("too_short")

        # Check for repeated characters (common corruption pattern)
        if len(set(content.replace("\n", "").replace(" ", ""))) < 5:
            indicators.append("repeated_characters")

        # Check for invalid encoding patterns
        try:
            content.encode("utf-8").decode("utf-8")
        except UnicodeError:
            indicators.append("encoding_error")

        return indicators

    def _find_and_restore_backup(self, file_path: Path) -> bool:
        """Find and restore a file from backup"""
        backup_locations = [
            Path("backups/safe_writes"),
            Path("backups/daily"),
            Path("backups/hourly"),
            Path("backups/critical"),
        ]

        # Look for .bak files first
        backup_pattern = f"{file_path.stem}_*.bak"
        for backup_dir in backup_locations:
            if backup_dir.exists():
                for backup_file in backup_dir.glob(backup_pattern):
                    try:
                        # Verify backup file is valid
                        with open(backup_file, "r", encoding="utf-8") as f:
                            backup_content = f.read()

                        if len(backup_content.strip()) > 10:  # Basic validity check
                            # Restore the file
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(backup_content)
                            return True
                    except Exception:
                        continue

        # Look in ZIP backups
        import zipfile

        for backup_dir in backup_locations:
            if backup_dir.exists():
                for zip_file in backup_dir.glob("*.zip"):
                    try:
                        with zipfile.ZipFile(zip_file, "r") as zipf:
                            if str(file_path) in zipf.namelist():
                                # Extract and restore
                                backup_content = zipf.read(str(file_path)).decode(
                                    "utf-8"
                                )
                                if len(backup_content.strip()) > 10:
                                    file_path.parent.mkdir(parents=True, exist_ok=True)
                                    with open(file_path, "w", encoding="utf-8") as f:
                                        f.write(backup_content)
                                    return True
                    except Exception:
                        continue

        return False

    def _log_corruption_report(self, report: Dict[str, Any]):
        """Log corruption report to file"""
        try:
            reports = []
            if self.corruption_log.exists():
                with open(self.corruption_log, "r", encoding="utf-8") as f:
                    reports = json.load(f)

            reports.append(report)

            # Keep only last 20 reports
            if len(reports) > 20:
                reports = reports[-20:]

            with open(self.corruption_log, "w", encoding="utf-8") as f:
                json.dump(reports, f, indent=2)

        except Exception as e:
            print(f"[WARN] Failed to log corruption report: {e}")

    def get_corruption_history(self) -> Dict[str, Any]:
        """Get historical corruption data"""
        try:
            if not self.corruption_log.exists():
                return {"reports": [], "summary": "No corruption history found"}

            with open(self.corruption_log, "r", encoding="utf-8") as f:
                reports = json.load(f)

            # Calculate summary statistics
            total_scans = len(reports)
            total_issues = sum(report.get("total_issues", 0) for report in reports)
            recent_issues = sum(
                report.get("total_issues", 0)
                for report in reports[-5:]
                if report.get("total_issues", 0) > 0
            )

            return {
                "reports": reports[-10:],  # Last 10 reports
                "summary": {
                    "total_scans": total_scans,
                    "total_issues_found": total_issues,
                    "recent_issues": recent_issues,
                    "average_issues_per_scan": total_issues / total_scans
                    if total_scans > 0
                    else 0,
                },
            }

        except Exception as e:
            return {"error": f"Failed to read corruption history: {e}"}


def run_corruption_check() -> bool:
    """Run a complete corruption check and recovery"""
    detector = CorruptionDetector()

    # Scan for corruption
    corruption_report = detector.scan_for_corruption()

    # If issues found, attempt recovery
    if corruption_report["total_issues"] > 0:
        recovery_report = detector.attempt_recovery(corruption_report)

        # Re-scan after recovery
        print("\n🔄 Re-scanning after recovery...")
        post_recovery_report = detector.scan_for_corruption()

        if post_recovery_report["total_issues"] == 0:
            print("🎉 All issues resolved!")
            return True
        else:
            print(f"[WARN] {post_recovery_report['total_issues']} issues remain")
            return False
    else:
        print("🎉 No corruption detected!")
        return True


if __name__ == "__main__":
    print("🔍 LYRIXA CORRUPTION DETECTOR")
    print("=" * 40)

    # Run corruption check
    success = run_corruption_check()

    # Show corruption history
    detector = CorruptionDetector()
    history = detector.get_corruption_history()

    if "summary" in history:
        print(f"\n📈 CORRUPTION HISTORY:")
        summary = history["summary"]
        print(f"   Total scans: {summary['total_scans']}")
        print(f"   Total issues found: {summary['total_issues_found']}")
        print(f"   Recent issues: {summary['recent_issues']}")
        print(f"   Average issues per scan: {summary['average_issues_per_scan']:.1f}")

    print(f"\n🎯 OVERALL STATUS: {'✅ HEALTHY' if success else '[WARN] NEEDS ATTENTION'}")
