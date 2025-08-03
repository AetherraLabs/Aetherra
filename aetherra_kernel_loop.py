#!/usr/bin/env python3
"""
🌌 Aetherra OS Kernel Loop
==========================
The core heartbeat and orchestration engine for the AI-native Operating System.

This is the living brain of Aetherra - continuously processing, learning, and evolving.
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AetherraKernelLoop:
    """
    🧠 The Core AI OS Kernel Loop

    Orchestrates all system operations:
    - Memory processing and optimization
    - Plugin execution and coordination
    - Scheduled maintenance tasks
    - Real-time event handling
    - System health monitoring
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.running = False
        self.start_time = None
        self.cycle_count = 0
        self.last_night_cycle = None

        # Core systems (will be injected by startup)
        self.memory_system = None
        self.plugin_manager = None
        self.lyrixa_engine = None
        self.scheduler = None
        self.service_registry = None

        # Performance metrics
        self.metrics = {
            "total_cycles": 0,
            "avg_cycle_time": 0.0,
            "last_cycle_time": 0.0,
            "errors_count": 0,
            "night_cycles_count": 0,
        }

        # Task queues
        self.high_priority_queue = asyncio.Queue()
        self.normal_priority_queue = asyncio.Queue()
        self.background_queue = asyncio.Queue()

    def inject_systems(
        self, memory_system, plugin_manager, lyrixa_engine, scheduler, service_registry
    ):
        """🔌 Inject core system references for orchestration."""
        self.memory_system = memory_system
        self.plugin_manager = plugin_manager
        self.lyrixa_engine = lyrixa_engine
        self.scheduler = scheduler
        self.service_registry = service_registry
        logger.info("🔗 Core systems injected into kernel loop")

    async def start_kernel_loop(self):
        """🚀 Start the main OS kernel loop."""
        logger.info("🌌 Starting Aetherra OS Kernel Loop...")
        self.running = True
        self.start_time = datetime.now()

        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self._main_processing_loop()),
            asyncio.create_task(self._background_maintenance_loop()),
            asyncio.create_task(self._health_monitoring_loop()),
            asyncio.create_task(self._memory_optimization_loop()),
            asyncio.create_task(self._plugin_orchestration_loop()),
            asyncio.create_task(self._heartbeat_loop()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Kernel loop error: {e}")
            await self.shutdown()

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat to service registry."""
        while self.running:
            try:
                if self.service_registry:
                    await self.service_registry.update_heartbeat("kernel_loop")
                await asyncio.sleep(60)  # Heartbeat every minute
            except Exception as e:
                logger.error(f"❌ Kernel heartbeat error: {e}")
                await asyncio.sleep(60)

    async def _main_processing_loop(self):
        """🔄 Main processing cycle - handles events and orchestration."""
        while self.running:
            cycle_start = time.time()

            try:
                # Process high priority tasks first
                await self._process_task_queue(self.high_priority_queue, max_tasks=5)

                # Process normal priority tasks
                await self._process_task_queue(self.normal_priority_queue, max_tasks=3)

                # Process background tasks
                await self._process_task_queue(self.background_queue, max_tasks=1)

                # Check for night cycle
                await self._check_night_cycle()

                # Update metrics
                cycle_time = time.time() - cycle_start
                self._update_metrics(cycle_time)

                # Adaptive sleep based on load
                sleep_time = max(0.1, 1.0 - cycle_time)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"❌ Main processing loop error: {e}")
                self.metrics["errors_count"] += 1
                await asyncio.sleep(1.0)

    async def _background_maintenance_loop(self):
        """🛠️ Background system maintenance and optimization."""
        while self.running:
            try:
                # Every 5 minutes: System health check
                if self.cycle_count % 300 == 0:
                    await self._perform_health_check()

                # Every 30 minutes: Memory optimization
                if self.cycle_count % 1800 == 0 and self.memory_system:
                    await self._optimize_memory()

                # Every hour: Plugin health check
                if self.cycle_count % 3600 == 0 and self.plugin_manager:
                    await self._check_plugin_health()

                await asyncio.sleep(60)  # Run every minute

            except Exception as e:
                logger.error(f"❌ Background maintenance error: {e}")
                await asyncio.sleep(60)

    async def _health_monitoring_loop(self):
        """💓 Continuous system health monitoring."""
        while self.running:
            try:
                # Monitor system vitals
                health_status = await self._gather_health_metrics()

                # Log health status
                logger.debug(f"🩺 System Health: {health_status}")

                # Alert on critical issues
                if health_status.get("critical_issues"):
                    logger.warning(
                        f"[WARN] Critical issues detected: {health_status['critical_issues']}"
                    )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(30)

    async def _memory_optimization_loop(self):
        """🧠 Continuous memory system optimization."""
        while self.running:
            try:
                if self.memory_system:
                    # Light memory optimization every 10 minutes
                    await self.memory_system.light_optimization()

                await asyncio.sleep(600)  # Every 10 minutes

            except Exception as e:
                logger.error(f"❌ Memory optimization error: {e}")
                await asyncio.sleep(600)

    async def _plugin_orchestration_loop(self):
        """🔌 Plugin coordination and execution."""
        while self.running:
            try:
                if self.plugin_manager:
                    # Execute scheduled plugin tasks
                    await self.plugin_manager.execute_scheduled_tasks()

                await asyncio.sleep(120)  # Every 2 minutes

            except Exception as e:
                logger.error(f"❌ Plugin orchestration error: {e}")
                await asyncio.sleep(120)

    async def _check_night_cycle(self):
        """🌙 Check if we should perform night cycle processing."""
        now = datetime.now()

        # Night cycle between 2 AM and 4 AM, once per day
        if 2 <= now.hour <= 4 and (
            self.last_night_cycle is None or (now - self.last_night_cycle).days >= 1
        ):
            logger.info("🌙 Initiating Night Cycle...")
            await self._perform_night_cycle()
            self.last_night_cycle = now
            self.metrics["night_cycles_count"] += 1

    async def _perform_night_cycle(self):
        """🌙 Deep system optimization and reflection during night cycle."""
        try:
            logger.info("🌙 Night Cycle: Deep Memory Consolidation...")
            if self.memory_system:
                await self.memory_system.deep_consolidation()

            logger.info("🌙 Night Cycle: Plugin Optimization...")
            if self.plugin_manager:
                await self.plugin_manager.optimize_plugins()

            logger.info("🌙 Night Cycle: System Reflection...")
            if self.lyrixa_engine:
                await self.lyrixa_engine.reflect_on_day()

            logger.info("🌙 Night Cycle: Cleanup and Maintenance...")
            await self._cleanup_temporary_files()

            logger.info("[OK] Night Cycle completed successfully")

        except Exception as e:
            logger.error(f"❌ Night cycle error: {e}")

    async def _process_task_queue(self, queue: asyncio.Queue, max_tasks: int = 5):
        """📋 Process tasks from a priority queue."""
        processed = 0
        while not queue.empty() and processed < max_tasks:
            try:
                task = await asyncio.wait_for(queue.get(), timeout=0.1)
                await self._execute_task(task)
                processed += 1
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"❌ Task processing error: {e}")

    async def _execute_task(self, task: Dict[str, Any]):
        """⚡ Execute a single task."""
        try:
            task_type = task.get("type")
            task_data = task.get("data", {})

            if task_type == "memory_query":
                if self.memory_system:
                    await self.memory_system.process_query(task_data)
            elif task_type == "plugin_invoke":
                if self.plugin_manager:
                    await self.plugin_manager.invoke_plugin(task_data)
            elif task_type == "lyrixa_thought":
                if self.lyrixa_engine:
                    await self.lyrixa_engine.process_thought(task_data)
            else:
                logger.warning(f"[WARN] Unknown task type: {task_type}")

        except Exception as e:
            logger.error(f"❌ Task execution error: {e}")

    async def _gather_health_metrics(self) -> Dict[str, Any]:
        """🩺 Gather comprehensive system health metrics."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "kernel_uptime": (datetime.now() - self.start_time).total_seconds()
            if self.start_time
            else 0,
            "cycle_count": self.cycle_count,
            "memory_status": "unknown",
            "plugin_status": "unknown",
            "lyrixa_status": "unknown",
            "critical_issues": [],
        }

        try:
            # Check memory system health
            if self.memory_system and hasattr(self.memory_system, "get_health_status"):
                health["memory_status"] = await self.memory_system.get_health_status()

            # Check plugin system health
            if self.plugin_manager and hasattr(
                self.plugin_manager, "get_health_status"
            ):
                health["plugin_status"] = await self.plugin_manager.get_health_status()

            # Check Lyrixa health
            if self.lyrixa_engine and hasattr(self.lyrixa_engine, "get_health_status"):
                health["lyrixa_status"] = await self.lyrixa_engine.get_health_status()

        except Exception as e:
            logger.error(f"❌ Health metrics gathering error: {e}")
            health["critical_issues"].append(f"Health check error: {str(e)}")

        return health

    async def _perform_health_check(self):
        """🩺 Perform comprehensive system health check."""
        logger.info("🩺 Performing system health check...")
        health = await self._gather_health_metrics()

        # Log health summary
        logger.info(
            f"📊 Health Summary: Memory={health['memory_status']}, "
            f"Plugins={health['plugin_status']}, Lyrixa={health['lyrixa_status']}"
        )

    async def _optimize_memory(self):
        """🧠 Perform memory optimization."""
        if self.memory_system:
            logger.info("🧠 Performing memory optimization...")
            await self.memory_system.optimize()

    async def _check_plugin_health(self):
        """🔌 Check plugin system health."""
        if self.plugin_manager:
            logger.info("🔌 Checking plugin health...")
            await self.plugin_manager.health_check()

    async def _cleanup_temporary_files(self):
        """🧹 Clean up temporary files and logs."""
        try:
            # Clean up old log files (older than 7 days)
            log_dir = Path("logs")
            if log_dir.exists():
                cutoff = datetime.now() - timedelta(days=7)
                for log_file in log_dir.glob("*.log"):
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                        log_file.unlink()
                        logger.debug(f"🗑️ Cleaned up old log: {log_file}")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

    def _update_metrics(self, cycle_time: float):
        """📊 Update kernel performance metrics."""
        self.cycle_count += 1
        self.metrics["total_cycles"] = self.cycle_count
        self.metrics["last_cycle_time"] = cycle_time

        # Calculate rolling average
        if self.metrics["avg_cycle_time"] == 0:
            self.metrics["avg_cycle_time"] = cycle_time
        else:
            alpha = 0.1  # Smoothing factor
            self.metrics["avg_cycle_time"] = (
                alpha * cycle_time + (1 - alpha) * self.metrics["avg_cycle_time"]
            )

    async def add_task(self, task: Dict[str, Any], priority: str = "normal"):
        """📝 Add a task to the appropriate priority queue."""
        if priority == "high":
            await self.high_priority_queue.put(task)
        elif priority == "background":
            await self.background_queue.put(task)
        else:
            await self.normal_priority_queue.put(task)

    async def shutdown(self):
        """🛑 Gracefully shutdown the kernel loop."""
        logger.info("🛑 Shutting down Aetherra OS Kernel Loop...")
        self.running = False

        # Save final metrics
        await self._save_metrics()

        logger.info("[OK] Kernel loop shutdown complete")

    async def _save_metrics(self):
        """💾 Save kernel metrics to file."""
        try:
            metrics_file = Path("aetherra_kernel_metrics.json")
            self.metrics["shutdown_time"] = datetime.now().isoformat()

            with open(metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2)

            logger.info(f"📊 Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save metrics: {e}")

    def get_status(self) -> Dict[str, Any]:
        """📋 Get current kernel status."""
        return {
            "running": self.running,
            "uptime": (datetime.now() - self.start_time).total_seconds()
            if self.start_time
            else 0,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics.copy(),
            "queue_sizes": {
                "high_priority": self.high_priority_queue.qsize(),
                "normal_priority": self.normal_priority_queue.qsize(),
                "background": self.background_queue.qsize(),
            },
        }


# Global kernel instance
kernel_loop = AetherraKernelLoop()


async def start_kernel(config: Optional[Dict] = None):
    """🚀 Start the Aetherra OS kernel loop."""
    global kernel_loop
    if config:
        kernel_loop.config.update(config)
    await kernel_loop.start_kernel_loop()


async def shutdown_kernel():
    """🛑 Shutdown the kernel loop."""
    global kernel_loop
    await kernel_loop.shutdown()


def get_kernel() -> AetherraKernelLoop:
    """🔗 Get the global kernel instance."""
    return kernel_loop


if __name__ == "__main__":
    # Test the kernel loop
    async def test_kernel():
        kernel = AetherraKernelLoop()

        # Mock system injection
        class MockSystem:
            async def light_optimization(self):
                pass

            async def deep_consolidation(self):
                pass

            async def optimize(self):
                pass

            async def get_health_status(self):
                return "healthy"

            async def process_query(self, data):
                pass

            async def execute_scheduled_tasks(self):
                pass

            async def invoke_plugin(self, data):
                pass

            async def optimize_plugins(self):
                pass

            async def health_check(self):
                pass

            async def process_thought(self, data):
                pass

            async def reflect_on_day(self):
                pass

        mock_system = MockSystem()
        kernel.inject_systems(
            mock_system, mock_system, mock_system, mock_system, mock_system
        )

        # Run for a short test
        try:
            await asyncio.wait_for(kernel.start_kernel_loop(), timeout=5.0)
        except asyncio.TimeoutError:
            await kernel.shutdown()
            print("[OK] Kernel loop test completed successfully")

    asyncio.run(test_kernel())
