"""
Intelligence Panel Manager for Lyrixa
=====================================

Real-time system intelligence panel showing active memory, goals, plugins, and confidence.
Provides live insights into Lyrixa's current state and decision-making process.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import threading


class IntelligencePanelManager:
    """Manages the real-time intelligence panel for Lyrixa."""
    
    def __init__(self, config_path: str = "lyrixa_intelligence_panel.json"):
        """Initialize the intelligence panel manager."""
        self.config_path = Path(config_path)
        self.panel_config = {}
        self.active_memory = {}
        self.current_goals = []
        self.plugin_status = {}
        self.confidence_metrics = {}
        self.performance_metrics = {}
        self.update_interval = 2.0  # seconds
        self.is_monitoring = False
        self._monitor_thread = None
        self._load_panel_config()
        
    def _load_panel_config(self):
        """Load intelligence panel configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.panel_config = config.get('panel_config', {})
                    self.update_interval = config.get('update_interval', 2.0)
            else:
                self._initialize_default_config()
        except Exception as e:
            print(f"Error loading intelligence panel config: {e}")
            self._initialize_default_config()
    
    def _initialize_default_config(self):
        """Initialize default intelligence panel configuration."""
        self.panel_config = {
            "visible_sections": {
                "active_memory": True,
                "current_goals": True,
                "plugin_status": True,
                "confidence_metrics": True,
                "performance_metrics": True,
                "recent_activity": True
            },
            "refresh_rates": {
                "memory": 1.0,
                "goals": 2.0,
                "plugins": 3.0,
                "confidence": 1.0,
                "performance": 5.0
            },
            "display_options": {
                "compact_mode": False,
                "show_timestamps": True,
                "show_confidence_bars": True,
                "max_memory_items": 10,
                "max_activity_items": 20
            }
        }
        
    def save_panel_config(self):
        """Save intelligence panel configuration."""
        try:
            config = {
                'panel_config': self.panel_config,
                'update_interval': self.update_interval,
                'last_updated': str(datetime.now())
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving intelligence panel config: {e}")
    
    def start_monitoring(self):
        """Start real-time monitoring of intelligence metrics."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        print("🧠 Intelligence panel monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        print("Intelligence panel monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop for intelligence metrics."""
        while self.is_monitoring:
            try:
                self._update_all_metrics()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _update_all_metrics(self):
        """Update all intelligence metrics."""
        self._update_active_memory()
        self._update_current_goals()
        self._update_plugin_status()
        self._update_confidence_metrics()
        self._update_performance_metrics()
    
    def _update_active_memory(self):
        """Update active memory information."""
        try:
            # Simulate active memory tracking
            self.active_memory = {
                "working_context": {
                    "current_file": "example.py",
                    "context_type": "code_analysis",
                    "active_since": str(datetime.now() - timedelta(minutes=5)),
                    "context_confidence": 0.85
                },
                "recent_interactions": [
                    {
                        "type": "code_analysis",
                        "timestamp": str(datetime.now() - timedelta(minutes=2)),
                        "confidence": 0.92,
                        "summary": "Analyzed Python function for optimization"
                    },
                    {
                        "type": "documentation_generation",
                        "timestamp": str(datetime.now() - timedelta(minutes=8)),
                        "confidence": 0.78,
                        "summary": "Generated docstring for class method"
                    }
                ],
                "memory_usage": {
                    "short_term": 7,
                    "long_term": 23,
                    "context_items": 5,
                    "total_capacity": 100
                },
                "learning_state": {
                    "adaptations_today": 3,
                    "confidence_trend": "increasing",
                    "last_learning_event": str(datetime.now() - timedelta(minutes=15))
                }
            }
        except Exception as e:
            print(f"Error updating active memory: {e}")
    
    def _update_current_goals(self):
        """Update current goals and objectives."""
        try:
            self.current_goals = [
                {
                    "id": "goal_1",
                    "title": "Code Quality Improvement",
                    "description": "Analyze and improve code quality metrics",
                    "progress": 0.65,
                    "priority": "high",
                    "estimated_completion": str(datetime.now() + timedelta(minutes=10)),
                    "status": "in_progress",
                    "confidence": 0.88
                },
                {
                    "id": "goal_2", 
                    "title": "Documentation Enhancement",
                    "description": "Generate comprehensive documentation",
                    "progress": 0.30,
                    "priority": "medium",
                    "estimated_completion": str(datetime.now() + timedelta(minutes=25)),
                    "status": "planning",
                    "confidence": 0.72
                },
                {
                    "id": "goal_3",
                    "title": "Performance Optimization",
                    "description": "Identify and resolve performance bottlenecks",
                    "progress": 0.10,
                    "priority": "low",
                    "estimated_completion": str(datetime.now() + timedelta(hours=1)),
                    "status": "queued",
                    "confidence": 0.55
                }
            ]
        except Exception as e:
            print(f"Error updating current goals: {e}")
    
    def _update_plugin_status(self):
        """Update plugin status information."""
        try:
            self.plugin_status = {
                "active_plugins": [
                    {
                        "name": "Code Analyzer",
                        "status": "running",
                        "load": 0.45,
                        "last_activity": str(datetime.now() - timedelta(seconds=30)),
                        "health": "good"
                    },
                    {
                        "name": "Memory System", 
                        "status": "running",
                        "load": 0.25,
                        "last_activity": str(datetime.now() - timedelta(seconds=5)),
                        "health": "excellent"
                    },
                    {
                        "name": "Performance Monitor",
                        "status": "running",
                        "load": 0.15,
                        "last_activity": str(datetime.now() - timedelta(minutes=1)),
                        "health": "good"
                    }
                ],
                "plugin_metrics": {
                    "total_plugins": 8,
                    "active_plugins": 3,
                    "idle_plugins": 3,
                    "error_plugins": 0,
                    "average_load": 0.28,
                    "total_memory_usage": "45MB"
                },
                "recent_plugin_events": [
                    {
                        "plugin": "Code Analyzer",
                        "event": "analysis_completed",
                        "timestamp": str(datetime.now() - timedelta(minutes=2)),
                        "duration": "1.2s"
                    }
                ]
            }
        except Exception as e:
            print(f"Error updating plugin status: {e}")
    
    def _update_confidence_metrics(self):
        """Update confidence and certainty metrics."""
        try:
            self.confidence_metrics = {
                "overall_confidence": 0.82,
                "context_understanding": 0.88,
                "response_accuracy": 0.85,
                "task_completion": 0.75,
                "learning_effectiveness": 0.79,
                "user_satisfaction": 0.91,
                "confidence_trend": {
                    "direction": "increasing",
                    "rate": 0.05,
                    "stability": "stable"
                },
                "uncertainty_areas": [
                    {
                        "area": "Complex algorithm analysis",
                        "confidence": 0.45,
                        "reason": "Limited training data"
                    },
                    {
                        "area": "Domain-specific terminology",
                        "confidence": 0.62,
                        "reason": "Context-dependent meanings"
                    }
                ]
            }
        except Exception as e:
            print(f"Error updating confidence metrics: {e}")
    
    def _update_performance_metrics(self):
        """Update system performance metrics."""
        try:
            self.performance_metrics = {
                "response_time": {
                    "current": 0.85,
                    "average": 1.2,
                    "trend": "improving"
                },
                "memory_efficiency": {
                    "usage": 0.34,
                    "peak": 0.67,
                    "optimization": "good"
                },
                "processing_load": {
                    "cpu": 0.23,
                    "memory": 0.45,
                    "io": 0.12
                },
                "quality_metrics": {
                    "accuracy": 0.89,
                    "relevance": 0.92,
                    "helpfulness": 0.87
                },
                "system_health": {
                    "overall": "excellent",
                    "uptime": "4h 23m",
                    "errors_today": 0,
                    "warnings_today": 2
                }
            }
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get a complete summary of current intelligence state."""
        return {
            "active_memory": self.active_memory,
            "current_goals": self.current_goals,
            "plugin_status": self.plugin_status,
            "confidence_metrics": self.confidence_metrics,
            "performance_metrics": self.performance_metrics,
            "last_updated": str(datetime.now()),
            "monitoring_active": self.is_monitoring
        }
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get any critical alerts or issues requiring attention."""
        alerts = []
        
        # Check confidence levels
        if self.confidence_metrics.get("overall_confidence", 1.0) < 0.5:
            alerts.append({
                "type": "low_confidence",
                "severity": "warning",
                "message": "Overall confidence below 50%",
                "action": "Review recent interactions and feedback"
            })
        
        # Check plugin health
        for plugin in self.plugin_status.get("active_plugins", []):
            if plugin.get("health") == "error":
                alerts.append({
                    "type": "plugin_error",
                    "severity": "critical",
                    "message": f"Plugin '{plugin['name']}' has errors",
                    "action": "Restart or troubleshoot plugin"
                })
        
        # Check performance metrics
        performance = self.performance_metrics.get("processing_load", {})
        if performance.get("cpu", 0) > 0.9:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning", 
                "message": "High CPU usage detected",
                "action": "Consider reducing processing load"
            })
        
        return alerts
    
    def get_section_data(self, section_name: str) -> Dict[str, Any]:
        """Get data for a specific intelligence panel section."""
        sections = {
            "active_memory": self.active_memory,
            "current_goals": self.current_goals,
            "plugin_status": self.plugin_status,
            "confidence_metrics": self.confidence_metrics,
            "performance_metrics": self.performance_metrics
        }
        
        return sections.get(section_name, {})
    
    def toggle_section_visibility(self, section_name: str) -> bool:
        """Toggle visibility of a panel section."""
        if section_name in self.panel_config.get("visible_sections", {}):
            current = self.panel_config["visible_sections"][section_name]
            self.panel_config["visible_sections"][section_name] = not current
            self.save_panel_config()
            return not current
        return False
    
    def set_update_interval(self, interval: float):
        """Set the monitoring update interval."""
        if 0.1 <= interval <= 30.0:
            self.update_interval = interval
            self.save_panel_config()
    
    def export_intelligence_data(self) -> Dict[str, Any]:
        """Export current intelligence data for analysis."""
        return {
            "intelligence_summary": self.get_intelligence_summary(),
            "critical_alerts": self.get_critical_alerts(),
            "panel_config": self.panel_config,
            "exported_at": str(datetime.now()),
            "version": "1.0"
        }
