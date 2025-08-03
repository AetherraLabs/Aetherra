#!/usr/bin/env python3
"""
🚀🧠 LYRIXA SYSTEM BOOTSTRAP + AWARENESS
========================================

System status detection and startup awareness that provides Lyrixa with:
- Real-time system component status monitoring
- Startup summary with context about what's loaded and active
- Memory of previous sessions and progress
- Goal continuity and project context awareness
- Plugin ecosystem health monitoring
- Intelligent system diagnostics and recommendations

This enables Lyrixa to provide meaningful context at startup:
"Here's what I remember and where we left off."
"""

import json
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil


class SystemComponentStatus(Enum):
    """Status of system components"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class StartupContextType(Enum):
    """Types of startup context"""

    FIRST_LAUNCH = "first_launch"
    DAILY_RETURN = "daily_return"
    SESSION_CONTINUATION = "session_continuation"
    PROJECT_RESUMPTION = "project_resumption"
    RECOVERY_MODE = "recovery_mode"


@dataclass
class ComponentStatus:
    """Individual component status"""

    name: str
    status: SystemComponentStatus
    details: Dict[str, Any]
    last_check: datetime
    health_score: float  # 0.0 to 1.0
    error_message: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SystemSnapshot:
    """Complete system status snapshot"""

    timestamp: datetime
    components: Dict[str, ComponentStatus]
    memory_stats: Dict[str, Any]
    plugin_stats: Dict[str, Any]
    goal_stats: Dict[str, Any]
    session_info: Dict[str, Any]
    startup_context: StartupContextType
    overall_health: float
    key_insights: List[str]
    recommendations: List[str]


@dataclass
class StartupSummary:
    """Startup awareness summary for user"""

    greeting: str
    context_type: StartupContextType
    memory_summary: str
    active_goals: List[str]
    loaded_plugins: List[str]
    recent_activity: List[str]
    continuation_suggestions: List[str]
    system_health: str
    time_since_last_session: Optional[str] = None


class LyrixaSystemBootstrap:
    """
    🚀🧠 Lyrixa System Bootstrap + Awareness

    Provides comprehensive system status detection and startup awareness:
    - Monitors all system components (memory, plugins, goals, etc.)
    - Generates intelligent startup summaries
    - Maintains session continuity and context
    - Offers system health diagnostics and recommendations
    - Enables Lyrixa to be aware of her own state and capabilities
    """

    def __init__(
        self,
        workspace_path: str,
        memory_system: Any,
        plugin_manager: Any,
        goal_system: Any,
        feedback_system: Any,
    ):
        self.workspace_path = Path(workspace_path)
        self.memory_system = memory_system
        self.plugin_manager = plugin_manager
        self.goal_system = goal_system
        self.feedback_system = feedback_system

        # System status tracking
        self.components: Dict[str, ComponentStatus] = {}
        self.last_snapshot: Optional[SystemSnapshot] = None
        self.startup_history: List[SystemSnapshot] = []

        # Session tracking
        self.session_file = self.workspace_path / "lyrixa_session_history.json"
        self.last_session_data: Optional[Dict[str, Any]] = None

        # Status files
        self.status_file = self.workspace_path / "lyrixa_system_status.json"

        print("🚀🧠 Lyrixa System Bootstrap + Awareness initialized")
        print("   ✅ Component monitoring ready")
        print("   ✅ Session tracking active")
        print("   ✅ Startup awareness enabled")

    async def perform_system_bootstrap(self) -> StartupSummary:
        """
        Perform complete system bootstrap and generate startup summary
        """
        print("🔍 Performing system bootstrap and awareness check...")

        # Load previous session data
        await self._load_session_history()

        # Detect all system components
        await self._detect_system_components()

        # Create system snapshot
        snapshot = await self._create_system_snapshot()
        self.last_snapshot = snapshot

        # Determine startup context
        startup_context = await self._determine_startup_context()
        snapshot.startup_context = startup_context

        # Generate startup summary
        summary = await self._generate_startup_summary(snapshot)

        # Save current session
        await self._save_session_data(snapshot)

        print(f"✅ System bootstrap complete - Context: {startup_context.value}")

        return summary

    async def _detect_system_components(self):
        """Detect status of all system components"""

        # Memory System Status
        memory_status = await self._check_memory_system()
        self.components["memory_system"] = memory_status

        # Plugin Manager Status
        plugin_status = await self._check_plugin_manager()
        self.components["plugin_manager"] = plugin_status

        # Goal System Status
        goal_status = await self._check_goal_system()
        self.components["goal_system"] = goal_status

        # Feedback System Status
        feedback_status = await self._check_feedback_system()
        self.components["feedback_system"] = feedback_status

        # Database Connections
        db_status = await self._check_database_connections()
        self.components["databases"] = db_status

        # File System Status
        fs_status = await self._check_file_system()
        self.components["file_system"] = fs_status

        # System Resources
        resource_status = await self._check_system_resources()
        self.components["system_resources"] = resource_status

    async def _check_memory_system(self) -> ComponentStatus:
        """Check memory system status"""
        try:
            # Test memory system connection
            if hasattr(self.memory_system, "db_path"):
                db_path = Path(self.memory_system.db_path)
                db_exists = db_path.exists()

                # Test database connection
                if db_exists:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM enhanced_memories")
                    memory_count = cursor.fetchone()[0]
                    conn.close()

                    # Test memory operations
                    test_search = await self.memory_system.recall_memories("test", 1)

                    details = {
                        "database_path": str(db_path),
                        "database_size_mb": round(
                            db_path.stat().st_size / (1024 * 1024), 2
                        ),
                        "memory_count": memory_count,
                        "search_functional": len(test_search) >= 0,
                        "connection_active": True,
                    }

                    health_score = 1.0 if memory_count > 0 else 0.8

                    return ComponentStatus(
                        name="Memory System",
                        status=SystemComponentStatus.ACTIVE,
                        details=details,
                        last_check=datetime.now(),
                        health_score=health_score,
                        recommendations=[]
                        if memory_count > 0
                        else ["Consider adding some initial memories"],
                    )
                else:
                    return ComponentStatus(
                        name="Memory System",
                        status=SystemComponentStatus.INACTIVE,
                        details={
                            "database_exists": False,
                            "database_path": str(db_path),
                        },
                        last_check=datetime.now(),
                        health_score=0.0,
                        error_message="Memory database not found",
                        recommendations=["Initialize memory database"],
                    )
            else:
                return ComponentStatus(
                    name="Memory System",
                    status=SystemComponentStatus.ERROR,
                    details={"error": "Memory system has no database path"},
                    last_check=datetime.now(),
                    health_score=0.0,
                    error_message="Memory system configuration error",
                    recommendations=["Check memory system initialization"],
                )

        except Exception as e:
            return ComponentStatus(
                name="Memory System",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Memory system error: {e}",
                recommendations=[
                    "Check memory system configuration",
                    "Restart system if needed",
                ],
            )

    async def _check_plugin_manager(self) -> ComponentStatus:
        """Check plugin manager status"""
        try:
            if hasattr(self.plugin_manager, "plugins"):
                plugins = self.plugin_manager.plugins
                total_plugins = len(plugins)

                # Count active plugins
                active_plugins = sum(
                    1
                    for p in plugins.values()
                    if p.get("status") == "active"
                    or p.get("status", "").lower() == "active"
                )

                # Check plugin directory
                plugin_dir = getattr(self.plugin_manager, "plugin_directory", None)
                plugin_dir_exists = (
                    plugin_dir and Path(plugin_dir).exists() if plugin_dir else False
                )

                details = {
                    "total_plugins": total_plugins,
                    "active_plugins": active_plugins,
                    "plugin_directory": str(plugin_dir) if plugin_dir else "Unknown",
                    "plugin_directory_exists": plugin_dir_exists,
                    "loaded_plugins": list(plugins.keys()),
                }

                if total_plugins > 0:
                    status = SystemComponentStatus.ACTIVE
                    health_score = min(1.0, active_plugins / max(1, total_plugins))
                    recommendations = []
                    if active_plugins < total_plugins:
                        recommendations.append(
                            f"{total_plugins - active_plugins} plugins inactive"
                        )
                else:
                    status = SystemComponentStatus.INACTIVE
                    health_score = 0.3
                    recommendations = [
                        "No plugins loaded",
                        "Consider loading useful plugins",
                    ]

                return ComponentStatus(
                    name="Plugin Manager",
                    status=status,
                    details=details,
                    last_check=datetime.now(),
                    health_score=health_score,
                    recommendations=recommendations,
                )
            else:
                return ComponentStatus(
                    name="Plugin Manager",
                    status=SystemComponentStatus.ERROR,
                    details={"error": "Plugin manager has no plugins attribute"},
                    last_check=datetime.now(),
                    health_score=0.0,
                    error_message="Plugin manager configuration error",
                    recommendations=["Check plugin manager initialization"],
                )

        except Exception as e:
            return ComponentStatus(
                name="Plugin Manager",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Plugin manager error: {e}",
                recommendations=["Check plugin manager configuration"],
            )

    async def _check_goal_system(self) -> ComponentStatus:
        """Check goal system status"""
        try:
            # Get goal statistics
            active_goals = self.goal_system.get_active_goals()
            goal_stats = self.goal_system.get_goal_statistics()

            details = {
                "total_goals": goal_stats.get("total_goals", 0),
                "active_goals": len(active_goals),
                "completed_goals": goal_stats.get("completed_goals", 0),
                "overdue_goals": goal_stats.get("overdue_goals", 0),
                "average_progress": goal_stats.get("average_progress", 0.0),
                "goals_file": getattr(self.goal_system, "goals_file", "Unknown"),
                "goals_file_exists": Path(
                    getattr(self.goal_system, "goals_file", "")
                ).exists(),
            }

            total_goals = details["total_goals"]
            active_count = details["active_goals"]
            overdue_count = details["overdue_goals"]

            if total_goals > 0:
                status = SystemComponentStatus.ACTIVE
                health_score = max(
                    0.3, (active_count - overdue_count * 0.5) / max(1, total_goals)
                )
                recommendations = []

                if overdue_count > 0:
                    recommendations.append(f"{overdue_count} goals are overdue")
                if active_count == 0:
                    recommendations.append(
                        "No active goals - consider setting some objectives"
                    )
                elif active_count > 10:
                    recommendations.append("Many active goals - consider prioritizing")
            else:
                status = SystemComponentStatus.INACTIVE
                health_score = 0.2
                recommendations = [
                    "No goals defined",
                    "Consider setting development objectives",
                ]

            return ComponentStatus(
                name="Goal System",
                status=status,
                details=details,
                last_check=datetime.now(),
                health_score=health_score,
                recommendations=recommendations,
            )

        except Exception as e:
            return ComponentStatus(
                name="Goal System",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Goal system error: {e}",
                recommendations=["Check goal system configuration"],
            )

    async def _check_feedback_system(self) -> ComponentStatus:
        """Check feedback system status"""
        try:
            # Get feedback system metrics
            performance_report = await self.feedback_system.get_performance_report()

            feedback_count = performance_report["performance_metrics"][
                "total_feedback_count"
            ]
            response_satisfaction = performance_report["performance_metrics"][
                "response_satisfaction"
            ]
            improvement_count = len(performance_report["recent_improvements"])

            details = {
                "total_feedback": feedback_count,
                "response_satisfaction": response_satisfaction,
                "recent_improvements": improvement_count,
                "adaptive_parameters": performance_report["adaptive_parameters"],
                "learning_active": feedback_count
                >= self.feedback_system.min_feedback_for_learning,
            }

            if feedback_count > 0:
                status = SystemComponentStatus.ACTIVE
                health_score = min(1.0, response_satisfaction + 0.3)
                recommendations = []

                if response_satisfaction < 0.6:
                    recommendations.append(
                        "Low response satisfaction - system learning from feedback"
                    )
                if improvement_count > 0:
                    recommendations.append(
                        f"System made {improvement_count} recent improvements"
                    )
            else:
                status = SystemComponentStatus.INACTIVE
                health_score = 0.5
                recommendations = [
                    "No feedback collected yet",
                    "Feedback helps improve responses",
                ]

            return ComponentStatus(
                name="Feedback System",
                status=status,
                details=details,
                last_check=datetime.now(),
                health_score=health_score,
                recommendations=recommendations,
            )

        except Exception as e:
            return ComponentStatus(
                name="Feedback System",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Feedback system error: {e}",
                recommendations=["Check feedback system configuration"],
            )

    async def _check_database_connections(self) -> ComponentStatus:
        """Check database connection status"""
        try:
            db_info = []
            total_dbs = 0
            active_dbs = 0

            # Check memory database
            if hasattr(self.memory_system, "db_path"):
                db_path = Path(self.memory_system.db_path)
                if db_path.exists():
                    total_dbs += 1
                    try:
                        conn = sqlite3.connect(str(db_path))
                        conn.close()
                        active_dbs += 1
                        db_info.append(
                            {
                                "name": "Memory DB",
                                "status": "connected",
                                "path": str(db_path),
                            }
                        )
                    except Exception:
                        db_info.append(
                            {
                                "name": "Memory DB",
                                "status": "error",
                                "path": str(db_path),
                            }
                        )
                else:
                    total_dbs += 1
                    db_info.append(
                        {
                            "name": "Memory DB",
                            "status": "not_found",
                            "path": str(db_path),
                        }
                    )

            # Check goals file
            if hasattr(self.goal_system, "goals_file"):
                goals_file = Path(self.goal_system.goals_file)
                total_dbs += 1
                if goals_file.exists():
                    active_dbs += 1
                    db_info.append(
                        {
                            "name": "Goals File",
                            "status": "exists",
                            "path": str(goals_file),
                        }
                    )
                else:
                    db_info.append(
                        {
                            "name": "Goals File",
                            "status": "not_found",
                            "path": str(goals_file),
                        }
                    )

            details = {
                "total_databases": total_dbs,
                "active_connections": active_dbs,
                "database_info": db_info,
            }

            if total_dbs > 0:
                health_score = active_dbs / total_dbs
                if health_score >= 0.8:
                    status = SystemComponentStatus.ACTIVE
                elif health_score >= 0.5:
                    status = SystemComponentStatus.DEGRADED
                else:
                    status = SystemComponentStatus.ERROR
            else:
                status = SystemComponentStatus.INACTIVE
                health_score = 0.0

            recommendations = []
            if active_dbs < total_dbs:
                recommendations.append(
                    f"{total_dbs - active_dbs} database(s) unavailable"
                )

            return ComponentStatus(
                name="Database Connections",
                status=status,
                details=details,
                last_check=datetime.now(),
                health_score=health_score,
                recommendations=recommendations,
            )

        except Exception as e:
            return ComponentStatus(
                name="Database Connections",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Database check error: {e}",
                recommendations=["Check database configurations"],
            )

    async def _check_file_system(self) -> ComponentStatus:
        """Check file system status"""
        try:
            # Check workspace directory
            workspace_exists = self.workspace_path.exists()
            workspace_writable = (
                os.access(self.workspace_path, os.W_OK) if workspace_exists else False
            )

            # Check free space
            if workspace_exists:
                disk_usage = psutil.disk_usage(str(self.workspace_path))
                free_space_gb = disk_usage.free / (1024**3)
                total_space_gb = disk_usage.total / (1024**3)
                space_percent = (disk_usage.free / disk_usage.total) * 100
            else:
                free_space_gb = 0
                total_space_gb = 0
                space_percent = 0

            details = {
                "workspace_path": str(self.workspace_path),
                "workspace_exists": workspace_exists,
                "workspace_writable": workspace_writable,
                "free_space_gb": round(free_space_gb, 2),
                "total_space_gb": round(total_space_gb, 2),
                "free_space_percent": round(space_percent, 1),
            }

            if workspace_exists and workspace_writable:
                if space_percent > 10:
                    status = SystemComponentStatus.ACTIVE
                    health_score = min(
                        1.0, space_percent / 50
                    )  # Full health at 50%+ free space
                elif space_percent > 5:
                    status = SystemComponentStatus.DEGRADED
                    health_score = 0.5
                else:
                    status = SystemComponentStatus.ERROR
                    health_score = 0.2
            else:
                status = SystemComponentStatus.ERROR
                health_score = 0.0

            recommendations = []
            if not workspace_exists:
                recommendations.append("Workspace directory does not exist")
            elif not workspace_writable:
                recommendations.append("Workspace directory is not writable")
            if space_percent < 10:
                recommendations.append(f"Low disk space: {space_percent:.1f}% free")

            return ComponentStatus(
                name="File System",
                status=status,
                details=details,
                last_check=datetime.now(),
                health_score=health_score,
                recommendations=recommendations,
            )

        except Exception as e:
            return ComponentStatus(
                name="File System",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"File system check error: {e}",
                recommendations=["Check file system permissions"],
            )

    async def _check_system_resources(self) -> ComponentStatus:
        """Check system resource status"""
        try:
            # Get system resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)

            details = {
                "cpu_usage_percent": round(cpu_percent, 1),
                "memory_usage_percent": round(memory_percent, 1),
                "memory_available_gb": round(memory_available_gb, 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
            }

            # Determine status based on resource usage
            if cpu_percent < 80 and memory_percent < 85:
                status = SystemComponentStatus.ACTIVE
                health_score = max(0.5, (200 - cpu_percent - memory_percent) / 200)
            elif cpu_percent < 90 and memory_percent < 95:
                status = SystemComponentStatus.DEGRADED
                health_score = 0.3
            else:
                status = SystemComponentStatus.ERROR
                health_score = 0.1

            recommendations = []
            if cpu_percent > 80:
                recommendations.append(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 85:
                recommendations.append(f"High memory usage: {memory_percent}%")
            if memory_available_gb < 1:
                recommendations.append("Low available memory")

            return ComponentStatus(
                name="System Resources",
                status=status,
                details=details,
                last_check=datetime.now(),
                health_score=health_score,
                recommendations=recommendations,
            )

        except Exception as e:
            return ComponentStatus(
                name="System Resources",
                status=SystemComponentStatus.ERROR,
                details={"error": str(e)},
                last_check=datetime.now(),
                health_score=0.0,
                error_message=f"Resource check error: {e}",
                recommendations=["Check system resource monitoring"],
            )

    async def _create_system_snapshot(self) -> SystemSnapshot:
        """Create comprehensive system snapshot"""

        # Calculate overall health
        total_health = sum(comp.health_score for comp in self.components.values())
        overall_health = total_health / len(self.components) if self.components else 0.0

        # Gather statistics
        memory_stats = {}
        plugin_stats = {}
        goal_stats = {}

        if "memory_system" in self.components:
            memory_stats = self.components["memory_system"].details

        if "plugin_manager" in self.components:
            plugin_stats = self.components["plugin_manager"].details

        if "goal_system" in self.components:
            goal_stats = self.components["goal_system"].details

        # Generate insights
        key_insights = []
        recommendations = []

        for comp in self.components.values():
            if comp.health_score < 0.5:
                key_insights.append(
                    f"{comp.name} needs attention (health: {comp.health_score:.1%})"
                )
            recommendations.extend(comp.recommendations)

        # Remove duplicate recommendations
        recommendations = list(set(recommendations))

        session_info = {
            "session_start": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "component_count": len(self.components),
        }

        return SystemSnapshot(
            timestamp=datetime.now(),
            components=self.components.copy(),
            memory_stats=memory_stats,
            plugin_stats=plugin_stats,
            goal_stats=goal_stats,
            session_info=session_info,
            startup_context=StartupContextType.FIRST_LAUNCH,  # Will be updated
            overall_health=overall_health,
            key_insights=key_insights,
            recommendations=recommendations,
        )

    async def _determine_startup_context(self) -> StartupContextType:
        """Determine the startup context based on session history"""

        if not self.last_session_data:
            return StartupContextType.FIRST_LAUNCH

        last_session_time = datetime.fromisoformat(
            self.last_session_data.get("timestamp", "1970-01-01")
        )
        time_since_last = datetime.now() - last_session_time

        if time_since_last > timedelta(days=1):
            return StartupContextType.DAILY_RETURN
        elif time_since_last > timedelta(hours=4):
            return StartupContextType.PROJECT_RESUMPTION
        elif time_since_last > timedelta(minutes=30):
            return StartupContextType.SESSION_CONTINUATION
        else:
            return StartupContextType.SESSION_CONTINUATION

    async def _generate_startup_summary(
        self, snapshot: SystemSnapshot
    ) -> StartupSummary:
        """Generate user-friendly startup summary"""

        context_type = snapshot.startup_context

        # Generate greeting based on context
        greetings = {
            StartupContextType.FIRST_LAUNCH: "👋 Hello! I'm Lyrixa, your AI assistant. Let's get started!",
            StartupContextType.DAILY_RETURN: "🌅 Good to see you again! Ready to continue where we left off?",
            StartupContextType.SESSION_CONTINUATION: "👋 Welcome back! I'm ready to assist you.",
            StartupContextType.PROJECT_RESUMPTION: "🔄 Hello again! Let me catch you up on what's been happening.",
            StartupContextType.RECOVERY_MODE: "[TOOL] System recovered! Let me restore your context.",
        }

        greeting = greetings.get(context_type, "👋 Hello! I'm here to help.")

        # Memory summary
        memory_count = snapshot.memory_stats.get("memory_count", 0)
        if memory_count > 0:
            memory_summary = f"I remember {memory_count} interactions and can recall our conversation history."
        else:
            memory_summary = "This appears to be our first interaction - I'm ready to start learning!"

        # Active goals
        active_goals = []
        if snapshot.goal_stats.get("active_goals", 0) > 0:
            # Would need actual goal titles - for now use count
            goal_count = snapshot.goal_stats["active_goals"]
            active_goals = [f"{goal_count} active development goals"]

        # Loaded plugins
        loaded_plugins = snapshot.plugin_stats.get("loaded_plugins", [])

        # Recent activity (would be populated from memory system)
        recent_activity = []
        if self.last_session_data:
            if "recent_activity" in self.last_session_data:
                recent_activity = self.last_session_data["recent_activity"][
                    :3
                ]  # Last 3 activities

        # Continuation suggestions
        continuation_suggestions = []
        if active_goals:
            continuation_suggestions.append("Review and update your active goals")
        if loaded_plugins:
            continuation_suggestions.append("Explore available plugin capabilities")
        if memory_count > 0:
            continuation_suggestions.append("Ask me about our previous conversations")
        if not continuation_suggestions:
            continuation_suggestions = [
                "Set some development goals",
                "Explore what I can help you with",
                "Start a new project or conversation",
            ]

        # System health summary
        health_score = snapshot.overall_health
        if health_score >= 0.8:
            system_health = "🟢 All systems running optimally"
        elif health_score >= 0.6:
            system_health = "🟡 Systems running with minor issues"
        elif health_score >= 0.4:
            system_health = "🟠 Some system components need attention"
        else:
            system_health = "🔴 Multiple system issues detected"

        # Time since last session
        time_since_last = None
        if self.last_session_data:
            last_time = datetime.fromisoformat(
                self.last_session_data.get("timestamp", "1970-01-01")
            )
            delta = datetime.now() - last_time
            if delta.days > 0:
                time_since_last = f"{delta.days} day(s) ago"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                time_since_last = f"{hours} hour(s) ago"
            else:
                minutes = delta.seconds // 60
                time_since_last = f"{minutes} minute(s) ago"

        return StartupSummary(
            greeting=greeting,
            context_type=context_type,
            memory_summary=memory_summary,
            active_goals=active_goals,
            loaded_plugins=loaded_plugins,
            recent_activity=recent_activity,
            continuation_suggestions=continuation_suggestions,
            system_health=system_health,
            time_since_last_session=time_since_last,
        )

    async def _load_session_history(self):
        """Load previous session data"""
        try:
            if self.session_file.exists():
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_session_data = data.get("last_session")
                    # Load recent snapshots
                    if "recent_snapshots" in data:
                        # Would load and deserialize snapshots if needed
                        pass
        except Exception as e:
            print(f"⚠️ Could not load session history: {e}")
            self.last_session_data = None

    async def _save_session_data(self, snapshot: SystemSnapshot):
        """Save current session data"""
        try:
            session_data = {
                "last_session": {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "overall_health": snapshot.overall_health,
                    "component_count": len(snapshot.components),
                    "memory_count": snapshot.memory_stats.get("memory_count", 0),
                    "active_goals": snapshot.goal_stats.get("active_goals", 0),
                    "loaded_plugins": len(
                        snapshot.plugin_stats.get("loaded_plugins", [])
                    ),
                    "recent_activity": [],  # Would be populated with actual recent activities
                    "startup_context": snapshot.startup_context.value,
                },
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Could not save session data: {e}")

    def format_startup_message(self, summary: StartupSummary) -> str:
        """Format startup summary into a user-friendly message"""

        message_parts = [
            summary.greeting,
            "",
            "📋 **System Status:**",
            f"   {summary.system_health}",
        ]

        if summary.time_since_last_session:
            message_parts.extend(
                ["", f"⏰ **Last session:** {summary.time_since_last_session}"]
            )

        message_parts.extend(
            ["", "🧠 **Memory & Context:**", f"   {summary.memory_summary}"]
        )

        if summary.active_goals:
            message_parts.extend(["", "🎯 **Active Goals:**"])
            for goal in summary.active_goals:
                message_parts.append(f"   • {goal}")

        if summary.loaded_plugins:
            message_parts.extend(
                [
                    "",
                    f"🧩 **Available Tools:** {len(summary.loaded_plugins)} plugins loaded",
                ]
            )

        if summary.recent_activity:
            message_parts.extend(["", "📈 **Recent Activity:**"])
            for activity in summary.recent_activity:
                message_parts.append(f"   • {activity}")

        if summary.continuation_suggestions:
            message_parts.extend(["", "💡 **Suggestions:**"])
            for suggestion in summary.continuation_suggestions[:3]:  # Limit to 3
                message_parts.append(f"   • {suggestion}")

        message_parts.extend(["", "What would you like to work on today?"])

        return "\n".join(message_parts)

    async def get_current_system_status(self) -> Dict[str, Any]:
        """Get current system status (quick check)"""
        await self._detect_system_components()

        status_summary = {}
        for name, component in self.components.items():
            status_summary[name] = {
                "status": component.status.value,
                "health_score": component.health_score,
                "error_message": component.error_message,
                "recommendations": component.recommendations,
            }

        overall_health = sum(
            comp.health_score for comp in self.components.values()
        ) / len(self.components)

        return {
            "overall_health": overall_health,
            "components": status_summary,
            "timestamp": datetime.now().isoformat(),
            "issues_detected": any(
                comp.status == SystemComponentStatus.ERROR
                for comp in self.components.values()
            ),
            "recommendations": list(
                set(
                    rec
                    for comp in self.components.values()
                    for rec in comp.recommendations
                )
            ),
        }

    async def generate_health_report(self) -> str:
        """Generate detailed system health report"""
        status = await self.get_current_system_status()

        report_parts = [
            "🔍 **LYRIXA SYSTEM HEALTH REPORT**",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"🌡️ **Overall Health:** {status['overall_health']:.1%}",
            "",
        ]

        # Component status
        report_parts.append("📊 **Component Status:**")
        for name, comp in status["components"].items():
            status_emoji = {
                "active": "🟢",
                "inactive": "🟡",
                "error": "🔴",
                "degraded": "🟠",
                "loading": "🔵",
            }
            emoji = status_emoji.get(comp["status"], "⚪")
            report_parts.append(
                f"   {emoji} {name}: {comp['status']} (Health: {comp['health_score']:.1%})"
            )

            if comp["error_message"]:
                report_parts.append(f"      ⚠️ {comp['error_message']}")

        # Recommendations
        if status["recommendations"]:
            report_parts.extend(["", "💡 **Recommendations:**"])
            for rec in status["recommendations"]:
                report_parts.append(f"   • {rec}")

        return "\n".join(report_parts)
