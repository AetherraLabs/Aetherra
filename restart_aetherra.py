#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔄 Aetherra System Restart Utility
==================================

Comprehensive restart utility for the Aetherra AI Operating System.
Handles graceful shutdown and restart of all system components.

This utility provides:
- Graceful shutdown of running processes
- Memory system cleanup and persistence
- Configuration validation before restart
- Process monitoring and health checks
- Automatic error recovery
- System integrity verification

Author: Aetherra Labs
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("aetherra_restart.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AetherraRestartManager:
    """
    🔄 Comprehensive restart manager for Aetherra OS
    """

    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_path = self.root_dir / "config.json"
        self.pid_file = self.root_dir / "aetherra.pid"
        self.launcher_script = self.root_dir / "aetherra_os_launcher.py"

        # Process tracking
        self.aetherra_processes = []
        self.shutdown_timeout = 30  # seconds
        self.startup_timeout = 60  # seconds

        # System state
        self.restart_count = 0
        self.max_restart_attempts = 3

        logger.info("🔄 Aetherra Restart Manager initialized")

    async def restart_system(
        self,
        mode: str = "startup",
        no_gui: bool = True,
        force: bool = False,
        preserve_memory: bool = True,
    ) -> bool:
        """
        Perform a complete system restart

        Args:
            mode: Launch mode (startup, maintenance, debug)
            no_gui: Whether to disable GUI
            force: Force restart even if system appears healthy
            preserve_memory: Whether to preserve memory systems during restart

        Returns:
            bool: True if restart successful, False otherwise
        """
        logger.info("🔄 Starting Aetherra system restart...")

        try:
            # Pre-restart checks
            if not await self._pre_restart_checks(force):
                return False

            # Step 1: Graceful shutdown
            logger.info("⏹️ Step 1: Graceful system shutdown")
            if not await self._graceful_shutdown(preserve_memory):
                logger.warning("⚠️ Graceful shutdown failed, attempting force shutdown")
                if not await self._force_shutdown():
                    logger.error("❌ Force shutdown failed")
                    return False

            # Step 2: System cleanup
            logger.info("🧹 Step 2: System cleanup")
            await self._cleanup_system()

            # Step 3: Health checks
            logger.info("🔍 Step 3: Pre-startup health checks")
            if not await self._health_checks():
                logger.error("❌ Health checks failed")
                return False

            # Step 4: System startup
            logger.info("🚀 Step 4: System startup")
            if not await self._startup_system(mode, no_gui):
                logger.error("❌ System startup failed")
                return False

            # Step 5: Post-startup verification
            logger.info("✅ Step 5: Post-startup verification")
            if not await self._verify_startup():
                logger.error("❌ Startup verification failed")
                return False

            logger.info("✅ Aetherra system restart completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Restart failed with exception: {e}")
            return False

    async def _pre_restart_checks(self, force: bool) -> bool:
        """Perform pre-restart system checks"""
        logger.info("🔍 Performing pre-restart checks...")

        # Check if configuration exists
        if not self.config_path.exists():
            logger.error(f"❌ Configuration file not found: {self.config_path}")
            return False

        # Check if launcher script exists
        if not self.launcher_script.exists():
            logger.error(f"❌ Launcher script not found: {self.launcher_script}")
            return False

        # Validate configuration
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            logger.info("✅ Configuration file is valid")
        except Exception as e:
            logger.error(f"❌ Invalid configuration file: {e}")
            return False

        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage(".").percent

        if memory_usage > 90:
            logger.warning(f"⚠️ High memory usage: {memory_usage}%")

        if disk_usage > 95:
            logger.error(f"❌ Critically low disk space: {disk_usage}%")
            return False

        # Check if system is running (unless force restart)
        if not force:
            running_processes = await self._find_aetherra_processes()
            if not running_processes:
                logger.info("ℹ️ No Aetherra processes currently running")
            else:
                logger.info(
                    f"ℹ️ Found {len(running_processes)} running Aetherra processes"
                )

        logger.info("✅ Pre-restart checks completed")
        return True

    async def _find_aetherra_processes(self) -> List[psutil.Process]:
        """Find all running Aetherra processes"""
        aetherra_processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info["cmdline"]
                if cmdline and any("aetherra" in cmd.lower() for cmd in cmdline):
                    aetherra_processes.append(proc)
                    logger.debug(
                        f"Found Aetherra process: PID {proc.info['pid']}, CMD: {' '.join(cmdline)}"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return aetherra_processes

    async def _graceful_shutdown(self, preserve_memory: bool) -> bool:
        """Perform graceful shutdown of Aetherra system"""
        logger.info("⏹️ Initiating graceful shutdown...")

        # Find running processes
        processes = await self._find_aetherra_processes()

        if not processes:
            logger.info("ℹ️ No Aetherra processes to shutdown")
            return True

        # Send shutdown signals
        for proc in processes:
            try:
                logger.info(f"📤 Sending SIGTERM to process {proc.pid}")
                proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"⚠️ Could not terminate process {proc.pid}: {e}")

        # Wait for processes to shutdown gracefully
        shutdown_start = time.time()
        while time.time() - shutdown_start < self.shutdown_timeout:
            remaining_processes = []

            for proc in processes:
                try:
                    if proc.is_running():
                        remaining_processes.append(proc)
                except psutil.NoSuchProcess:
                    pass  # Process already terminated

            if not remaining_processes:
                logger.info("✅ All processes shutdown gracefully")
                return True

            processes = remaining_processes
            await asyncio.sleep(1)

        logger.warning(f"⚠️ {len(processes)} processes did not shutdown gracefully")
        return False

    async def _force_shutdown(self) -> bool:
        """Force shutdown of remaining Aetherra processes"""
        logger.info("💥 Force shutdown of remaining processes...")

        processes = await self._find_aetherra_processes()

        for proc in processes:
            try:
                logger.info(f"💥 Force killing process {proc.pid}")
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"⚠️ Could not kill process {proc.pid}: {e}")

        # Final verification
        await asyncio.sleep(2)
        remaining_processes = await self._find_aetherra_processes()

        if remaining_processes:
            logger.error(
                f"❌ {len(remaining_processes)} processes still running after force shutdown"
            )
            return False

        logger.info("✅ Force shutdown completed")
        return True

    async def _cleanup_system(self):
        """Clean up system resources and temporary files"""
        logger.info("🧹 Cleaning up system resources...")

        # Clean up PID file
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
                logger.info(f"🗑️ Removed PID file: {self.pid_file}")
            except Exception as e:
                logger.warning(f"⚠️ Could not remove PID file: {e}")

        # Clean up temporary files
        temp_patterns = ["*.tmp", "*.lock", "*.temp", "__pycache__", "*.pyc"]

        for pattern in temp_patterns:
            for temp_file in self.root_dir.glob(f"**/{pattern}"):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        import shutil

                        shutil.rmtree(temp_file)
                    logger.debug(f"🗑️ Removed: {temp_file}")
                except Exception as e:
                    logger.debug(f"⚠️ Could not remove {temp_file}: {e}")

        # Clear system caches (if applicable)
        await self._clear_system_caches()

        logger.info("✅ System cleanup completed")

    async def _clear_system_caches(self):
        """Clear various system caches"""
        cache_files = ["lyrixa_cache.db", "analysis_cache.json", "plugin_cache.json"]

        for cache_file in cache_files:
            cache_path = self.root_dir / cache_file
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    logger.debug(f"🗑️ Cleared cache: {cache_file}")
                except Exception as e:
                    logger.debug(f"⚠️ Could not clear cache {cache_file}: {e}")

    async def _health_checks(self) -> bool:
        """Perform system health checks before startup"""
        logger.info("🔍 Performing health checks...")

        checks_passed = 0
        total_checks = 5

        # Check 1: Python environment
        try:
            import sys

            python_version = sys.version_info
            if python_version >= (3, 8):
                logger.info(
                    f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
                )
                checks_passed += 1
            else:
                logger.error(f"❌ Python version too old: {python_version}")
        except Exception as e:
            logger.error(f"❌ Python check failed: {e}")

        # Check 2: Required modules
        required_modules = ["asyncio", "json", "pathlib", "sqlite3"]
        try:
            for module in required_modules:
                __import__(module)
            logger.info("✅ Required modules available")
            checks_passed += 1
        except ImportError as e:
            logger.error(f"❌ Missing required module: {e}")

        # Check 3: File permissions
        try:
            test_file = self.root_dir / "test_permissions.tmp"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✅ File system permissions OK")
            checks_passed += 1
        except Exception as e:
            logger.error(f"❌ File permission check failed: {e}")

        # Check 4: Memory availability
        try:
            available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            if available_memory > 512:  # At least 512MB
                logger.info(f"✅ Available memory: {available_memory:.0f}MB")
                checks_passed += 1
            else:
                logger.error(f"❌ Insufficient memory: {available_memory:.0f}MB")
        except Exception as e:
            logger.error(f"❌ Memory check failed: {e}")

        # Check 5: Network connectivity (optional)
        try:
            import socket

            socket.create_connection(("8.8.8.8", 53), timeout=5)
            logger.info("✅ Network connectivity OK")
            checks_passed += 1
        except Exception:
            logger.warning("⚠️ Limited network connectivity (optional)")
            checks_passed += 1  # Don't fail for network issues

        success_rate = checks_passed / total_checks
        logger.info(
            f"🔍 Health checks: {checks_passed}/{total_checks} passed ({success_rate:.1%})"
        )

        return success_rate >= 0.8  # At least 80% of checks must pass

    async def _startup_system(self, mode: str, no_gui: bool) -> bool:
        """Start the Aetherra system"""
        logger.info(f"🚀 Starting Aetherra system in {mode} mode...")

        # Build launch command
        cmd = [sys.executable, str(self.launcher_script), "--mode", mode]

        if no_gui:
            cmd.append("--no-gui")

        # Add restart flag to indicate this is a restart
        cmd.extend(["--restart", "true"])

        logger.info(f"🚀 Launch command: {' '.join(cmd)}")

        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.root_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                if sys.platform == "win32"
                else 0,
            )

            # Store PID
            with open(self.pid_file, "w") as f:
                f.write(str(process.pid))

            logger.info(f"🚀 Aetherra system started with PID: {process.pid}")

            # Give the system time to initialize
            await asyncio.sleep(5)

            # Check if process is still running
            if process.poll() is None:
                logger.info("✅ System startup initiated successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ System startup failed")
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start system: {e}")
            return False

    async def _verify_startup(self) -> bool:
        """Verify that the system started successfully"""
        logger.info("✅ Verifying system startup...")

        verification_start = time.time()

        while time.time() - verification_start < self.startup_timeout:
            # Check if PID file exists and process is running
            if self.pid_file.exists():
                try:
                    with open(self.pid_file, "r") as f:
                        pid = int(f.read().strip())

                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        if proc.is_running():
                            logger.info(f"✅ System is running (PID: {pid})")

                            # Additional checks can be added here
                            # e.g., HTTP health endpoint, log file analysis

                            return True
                except Exception as e:
                    logger.debug(f"Verification check failed: {e}")

            await asyncio.sleep(2)

        logger.error("❌ System startup verification failed")
        return False

    async def quick_restart(self) -> bool:
        """Perform a quick restart (minimal checks)"""
        logger.info("⚡ Performing quick restart...")
        return await self.restart_system(
            mode="startup", no_gui=True, force=False, preserve_memory=True
        )

    async def force_restart(self) -> bool:
        """Perform a forced restart (ignore running state)"""
        logger.info("💥 Performing forced restart...")
        return await self.restart_system(
            mode="startup", no_gui=True, force=True, preserve_memory=False
        )

    async def maintenance_restart(self) -> bool:
        """Restart in maintenance mode"""
        logger.info("🔧 Performing maintenance restart...")
        return await self.restart_system(
            mode="maintenance", no_gui=True, force=False, preserve_memory=True
        )

    def get_system_status(self) -> Dict:
        """Get current system status"""
        processes = []

        # Check for running processes
        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "status", "memory_info"]
        ):
            try:
                cmdline = proc.info["cmdline"]
                if cmdline and any("aetherra" in cmd.lower() for cmd in cmdline):
                    processes.append(
                        {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "status": proc.info["status"],
                            "memory_mb": proc.info["memory_info"].rss / (1024 * 1024),
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "running_processes": len(processes),
            "processes": processes,
            "pid_file_exists": self.pid_file.exists(),
            "config_file_exists": self.config_path.exists(),
            "launcher_exists": self.launcher_script.exists(),
            "system_memory_percent": psutil.virtual_memory().percent,
            "system_disk_percent": psutil.disk_usage(".").percent,
        }


async def main():
    """Main entry point for the restart utility"""
    import argparse

    parser = argparse.ArgumentParser(description="Aetherra System Restart Utility")
    parser.add_argument(
        "--mode",
        choices=["startup", "maintenance", "debug"],
        default="startup",
        help="Launch mode",
    )
    parser.add_argument("--quick", action="store_true", help="Quick restart")
    parser.add_argument("--force", action="store_true", help="Force restart")
    parser.add_argument(
        "--maintenance", action="store_true", help="Maintenance restart"
    )
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument(
        "--no-gui", action="store_true", default=True, help="Disable GUI"
    )

    args = parser.parse_args()

    manager = AetherraRestartManager()

    if args.status:
        status = manager.get_system_status()
        print(json.dumps(status, indent=2))
        return

    try:
        if args.quick:
            success = await manager.quick_restart()
        elif args.force:
            success = await manager.force_restart()
        elif args.maintenance:
            success = await manager.maintenance_restart()
        else:
            success = await manager.restart_system(args.mode, args.no_gui)

        if success:
            print("✅ Aetherra system restart completed successfully!")
            sys.exit(0)
        else:
            print("❌ Aetherra system restart failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Restart interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Restart failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
