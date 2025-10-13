#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🚨 Intelligent Alert Management System
======================================

Strategic Enhancement #4: Complete alert intelligence system that combines
adaptive thresholds, AI-assisted anomaly detection, and Lyrixa integration
for intelligent alert management.

This module:
- Orchestrates the complete alert intelligence workflow
- Manages alert lifecycle from detection to resolution
- Provides intelligent alert routing and escalation
- Integrates with homeostasis for closed-loop optimization

Author: Aetherra Labs
"""

import asyncio
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .alert_intelligence import (
    AlertSeverity,
    AlertStatus,
    IntelligentAlert,
    get_adaptive_threshold_engine,
)
from .lyrixa_integration import get_lyrixa_integration

logger = logging.getLogger(__name__)


class AlertEscalationRule:
    """Alert escalation rule definition."""
    
    def __init__(self, 
                 name: str,
                 condition: str,
                 target_severity: AlertSeverity,
                 escalation_delay: float,
                 max_escalations: int = 3):
        self.name = name
        self.condition = condition
        self.target_severity = target_severity
        self.escalation_delay = escalation_delay
        self.max_escalations = max_escalations


class AlertNotificationChannel:
    """Alert notification channel configuration."""
    
    def __init__(self,
                 name: str,
                 channel_type: str,  # "email", "webhook", "console", "homeostasis"
                 endpoint: str,
                 severity_filter: Set[AlertSeverity],
                 enabled: bool = True):
        self.name = name
        self.channel_type = channel_type
        self.endpoint = endpoint
        self.severity_filter = severity_filter
        self.enabled = enabled


class IntelligentAlertManager:
    """
    Intelligent Alert Management System.
    
    Orchestrates the complete alert intelligence workflow from anomaly detection
    through AI-assisted analysis to resolution and learning.
    """
    
    def __init__(self, db_path: str = "alert_management.db"):
        self.db_path = db_path
        
        # Component integration
        self.threshold_engine = get_adaptive_threshold_engine()
        self.lyrixa_integration = get_lyrixa_integration()
        
        # State
        self.manager_active = False
        self.active_alerts: Dict[str, IntelligentAlert] = {}
        self.alert_history: List[IntelligentAlert] = []
        
        # Configuration
        self.escalation_rules: List[AlertEscalationRule] = []
        self.notification_channels: List[AlertNotificationChannel] = []
        self.auto_resolve_timeout = 3600.0  # 1 hour
        self.max_active_alerts = 100
        
        # Background tasks
        self.management_task: Optional[asyncio.Task] = None
        self.escalation_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.alerts_created = 0
        self.alerts_resolved = 0
        self.alerts_escalated = 0
        self.notifications_sent = 0
        
        self._init_database()
        self._setup_default_configuration()
        
        logger.info("🚨 Intelligent Alert Manager initialized")
    
    def _init_database(self):
        """Initialize the alert management database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                
                # Intelligent alerts table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS intelligent_alerts (
                        alert_id TEXT PRIMARY KEY,
                        detection_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        category TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        root_cause_hypothesis TEXT NOT NULL,
                        remediation_suggestions TEXT NOT NULL,
                        impact_assessment TEXT NOT NULL,
                        triggered_at TEXT NOT NULL,
                        expires_at TEXT,
                        context_data TEXT NOT NULL,
                        status TEXT NOT NULL,
                        assignee TEXT,
                        escalation_level INTEGER NOT NULL,
                        reflection_analysis TEXT,
                        explanation_confidence REAL NOT NULL,
                        resolved_at TEXT,
                        resolution_notes TEXT
                    )
                """)
                
                # Alert events table (for audit trail)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alert_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_data TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (alert_id) REFERENCES intelligent_alerts (alert_id)
                    )
                """)
                
                # Alert metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alert_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize alert management database: {e}")
            raise
    
    def _setup_default_configuration(self):
        """Setup default escalation rules and notification channels."""
        # Default escalation rules
        self.escalation_rules = [
            AlertEscalationRule("critical_immediate", "severity == 'critical'", 
                              AlertSeverity.CRITICAL, 0.0),
            AlertEscalationRule("high_5min", "severity == 'high' and age > 300",
                              AlertSeverity.CRITICAL, 300.0),
            AlertEscalationRule("medium_15min", "severity == 'medium' and age > 900",
                              AlertSeverity.HIGH, 900.0),
            AlertEscalationRule("low_1hour", "severity == 'low' and age > 3600",
                              AlertSeverity.MEDIUM, 3600.0)
        ]
        
        # Default notification channels
        self.notification_channels = [
            AlertNotificationChannel("console", "console", "stdout",
                                   {AlertSeverity.LOW, AlertSeverity.MEDIUM, 
                                    AlertSeverity.HIGH, AlertSeverity.CRITICAL}),
            AlertNotificationChannel("homeostasis_feedback", "homeostasis", "system",
                                   {AlertSeverity.HIGH, AlertSeverity.CRITICAL})
        ]
    
    async def start_manager(self):
        """Start the intelligent alert manager."""
        if self.manager_active:
            logger.warning("Alert manager already active")
            return
        
        try:
            # Start component systems
            await self.threshold_engine.start_engine()
            await self.lyrixa_integration.start_integration()
            
            # Start background tasks
            self.manager_active = True
            self.management_task = asyncio.create_task(self._alert_management_loop())
            self.escalation_task = asyncio.create_task(self._escalation_loop())
            
            logger.info("🚨 Intelligent Alert Manager started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start alert manager: {e}")
            raise
    
    async def stop_manager(self):
        """Stop the intelligent alert manager."""
        if not self.manager_active:
            return
        
        self.manager_active = False
        
        # Stop background tasks
        if self.management_task:
            self.management_task.cancel()
        if self.escalation_task:
            self.escalation_task.cancel()
        
        # Stop component systems
        await self.threshold_engine.stop_engine()
        await self.lyrixa_integration.stop_integration()
        
        logger.info("🚨 Intelligent Alert Manager stopped")
    
    async def process_metric_sample(self, 
                                  metric_name: str,
                                  value: float,
                                  context: Optional[Dict[str, Any]] = None) -> Optional[IntelligentAlert]:
        """
        Process a metric sample and create intelligent alert if anomaly detected.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context data
            
        Returns:
            IntelligentAlert if anomaly detected and alert created, None otherwise
        """
        try:
            # Check for anomaly using adaptive thresholds
            detection = await self.threshold_engine.add_metric_sample(
                metric_name, value, context
            )
            
            if not detection:
                return None
            
            # Create intelligent alert with AI analysis
            alert = await self.lyrixa_integration.create_intelligent_alert(
                detection, context
            )
            
            # Register the alert
            await self._register_alert(alert)
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Record metrics
            await self._record_alert_metrics(alert)
            
            self.alerts_created += 1
            
            logger.info(f"🚨 Intelligent alert created: {alert.title} (ID: {alert.alert_id})")
            
            return alert
            
        except Exception as e:
            logger.error(f"❌ Error processing metric sample {metric_name}: {e}")
            return None
    
    async def acknowledge_alert(self, alert_id: str, acknowledger: str, notes: str = "") -> bool:
        """Acknowledge an alert."""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for acknowledgment")
                return False
            
            if alert.status != AlertStatus.ACTIVE:
                logger.warning(f"Alert {alert_id} is not active (status: {alert.status.value})")
                return False
            
            # Update alert
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.assignee = acknowledger
            
            # Record event
            await self._record_alert_event(alert_id, "acknowledged", {
                "acknowledger": acknowledger,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update database
            await self._update_alert_in_db(alert)
            
            logger.info(f"✅ Alert {alert_id} acknowledged by {acknowledger}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolver: str, notes: str = "") -> bool:
        """Resolve an alert."""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alert {alert_id} not found for resolution")
                return False
            
            # Update alert
            alert.status = AlertStatus.RESOLVED
            alert.assignee = resolver
            
            # Record event
            await self._record_alert_event(alert_id, "resolved", {
                "resolver": resolver,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update database
            await self._update_alert_in_db(alert)
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            self.alerts_resolved += 1
            
            logger.info(f"✅ Alert {alert_id} resolved by {resolver}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving alert {alert_id}: {e}")
            return False
    
    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[IntelligentAlert]:
        """Get currently active alerts."""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [alert for alert in alerts if alert.severity == severity_filter]
        
        # Sort by severity and age
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 3
        }
        
        alerts.sort(key=lambda a: (severity_order.get(a.severity, 99), a.triggered_at))
        return alerts
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert management statistics."""
        active_by_severity = {}
        for severity in AlertSeverity:
            count = len([a for a in self.active_alerts.values() if a.severity == severity])
            active_by_severity[severity.value] = count
        
        return {
            "manager_active": self.manager_active,
            "active_alerts_count": len(self.active_alerts),
            "active_by_severity": active_by_severity,
            "total_created": self.alerts_created,
            "total_resolved": self.alerts_resolved,
            "total_escalated": self.alerts_escalated,
            "notifications_sent": self.notifications_sent,
            "resolution_rate": self.alerts_resolved / max(self.alerts_created, 1),
            "threshold_engine_status": self.threshold_engine.get_engine_status(),
            "lyrixa_integration_status": self.lyrixa_integration.get_integration_status()
        }
    
    # Private methods
    
    async def _alert_management_loop(self):
        """Background loop for alert management tasks."""
        try:
            while self.manager_active:
                await self._check_auto_resolution()
                await self._cleanup_old_alerts()
                await self._update_alert_metrics()
                await asyncio.sleep(60.0)  # Run every minute
                
        except asyncio.CancelledError:
            logger.info("Alert management loop cancelled")
        except Exception as e:
            logger.error(f"❌ Alert management loop error: {e}")
    
    async def _escalation_loop(self):
        """Background loop for alert escalation."""
        try:
            while self.manager_active:
                await self._process_escalations()
                await asyncio.sleep(30.0)  # Check escalations every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Alert escalation loop cancelled")
        except Exception as e:
            logger.error(f"❌ Alert escalation loop error: {e}")
    
    async def _register_alert(self, alert: IntelligentAlert):
        """Register a new alert in the system."""
        try:
            # Add to active alerts
            self.active_alerts[alert.alert_id] = alert
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO intelligent_alerts (
                        alert_id, detection_id, title, description, severity, category,
                        explanation, root_cause_hypothesis, remediation_suggestions,
                        impact_assessment, triggered_at, expires_at, context_data,
                        status, assignee, escalation_level, reflection_analysis,
                        explanation_confidence, resolved_at, resolution_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id, alert.detection_id, alert.title, alert.description,
                    alert.severity.value, alert.category, alert.explanation,
                    alert.root_cause_hypothesis, "\n".join(alert.remediation_suggestions),
                    alert.impact_assessment, alert.triggered_at, alert.expires_at,
                    str(alert.context_data), alert.status.value, alert.assignee,
                    alert.escalation_level, str(alert.reflection_analysis),
                    alert.explanation_confidence, None, None
                ))
                conn.commit()
            
            # Record creation event
            await self._record_alert_event(alert.alert_id, "created", {
                "severity": alert.severity.value,
                "category": alert.category,
                "confidence": alert.explanation_confidence
            })
            
        except Exception as e:
            logger.error(f"❌ Error registering alert {alert.alert_id}: {e}")
    
    async def _send_notifications(self, alert: IntelligentAlert):
        """Send notifications for an alert."""
        try:
            for channel in self.notification_channels:
                if not channel.enabled:
                    continue
                
                if alert.severity not in channel.severity_filter:
                    continue
                
                await self._send_notification(channel, alert)
                self.notifications_sent += 1
                
        except Exception as e:
            logger.error(f"❌ Error sending notifications for alert {alert.alert_id}: {e}")
    
    async def _send_notification(self, channel: AlertNotificationChannel, alert: IntelligentAlert):
        """Send notification through a specific channel."""
        try:
            if channel.channel_type == "console":
                severity_emoji = {
                    AlertSeverity.LOW: "🟡",
                    AlertSeverity.MEDIUM: "🟠",
                    AlertSeverity.HIGH: "🔴", 
                    AlertSeverity.CRITICAL: "🚨"
                }
                emoji = severity_emoji.get(alert.severity, "⚠️")
                
                print(f"\n{emoji} ALERT: {alert.title}")
                print(f"Explanation: {alert.explanation}")
                print(f"Root Cause: {alert.root_cause_hypothesis}")
                print("Recommended Actions:")
                for i, action in enumerate(alert.remediation_suggestions, 1):
                    print(f"  {i}. {action}")
                print(f"Impact: {alert.impact_assessment}")
                print(f"Confidence: {alert.explanation_confidence:.1%}")
                print("-" * 60)
                
            elif channel.channel_type == "homeostasis":
                # In a real implementation, this would feedback to homeostasis
                # for closed-loop optimization
                logger.info(f"🔄 Homeostasis feedback: {alert.alert_id} - {alert.severity.value}")
                
            # Add other notification types as needed
            
        except Exception as e:
            logger.error(f"❌ Error sending notification via {channel.name}: {e}")
    
    async def _process_escalations(self):
        """Process alert escalations based on rules."""
        try:
            current_time = datetime.now()
            
            for _alert_id, alert in list(self.active_alerts.items()):
                if alert.status != AlertStatus.ACTIVE:
                    continue
                
                # Calculate alert age
                triggered_time = datetime.fromisoformat(alert.triggered_at)
                age_seconds = (current_time - triggered_time).total_seconds()
                
                # Check escalation rules
                for rule in self.escalation_rules:
                    if self._should_escalate(alert, age_seconds, rule):
                        await self._escalate_alert(alert, rule)
                        break
                        
        except Exception as e:
            logger.error(f"❌ Error processing escalations: {e}")
    
    def _should_escalate(self, alert: IntelligentAlert, age_seconds: float, rule: AlertEscalationRule) -> bool:
        """Check if an alert should be escalated according to a rule."""
        try:
            if alert.escalation_level >= rule.max_escalations:
                return False
            
            if age_seconds < rule.escalation_delay:
                return False
            
            # Simple rule evaluation - could be enhanced with proper expression parsing
            if rule.condition == "severity == 'critical'" and alert.severity != AlertSeverity.CRITICAL:
                return False
            elif rule.condition.startswith("severity == 'high' and age >"):
                delay = float(rule.condition.split(">")[1].strip())
                return alert.severity == AlertSeverity.HIGH and age_seconds > delay
            elif rule.condition.startswith("severity == 'medium' and age >"):
                delay = float(rule.condition.split(">")[1].strip())
                return alert.severity == AlertSeverity.MEDIUM and age_seconds > delay
            elif rule.condition.startswith("severity == 'low' and age >"):
                delay = float(rule.condition.split(">")[1].strip())
                return alert.severity == AlertSeverity.LOW and age_seconds > delay
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error evaluating escalation rule {rule.name}: {e}")
            return False
    
    async def _escalate_alert(self, alert: IntelligentAlert, rule: AlertEscalationRule):
        """Escalate an alert according to a rule."""
        try:
            old_severity = alert.severity
            alert.severity = rule.target_severity
            alert.escalation_level += 1
            
            # Record escalation event
            await self._record_alert_event(alert.alert_id, "escalated", {
                "rule": rule.name,
                "old_severity": old_severity.value,
                "new_severity": rule.target_severity.value,
                "escalation_level": alert.escalation_level
            })
            
            # Update database
            await self._update_alert_in_db(alert)
            
            # Send escalation notifications
            await self._send_notifications(alert)
            
            self.alerts_escalated += 1
            
            logger.warning(f"⬆️ Alert {alert.alert_id} escalated from {old_severity.value} to "
                          f"{rule.target_severity.value} (rule: {rule.name})")
            
        except Exception as e:
            logger.error(f"❌ Error escalating alert {alert.alert_id}: {e}")
    
    async def _check_auto_resolution(self):
        """Check for alerts that should be auto-resolved."""
        try:
            current_time = datetime.now()
            
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.status != AlertStatus.ACTIVE:
                    continue
                
                # Calculate alert age
                triggered_time = datetime.fromisoformat(alert.triggered_at)
                age_seconds = (current_time - triggered_time).total_seconds()
                
                # Auto-resolve old low-severity alerts
                if (alert.severity == AlertSeverity.LOW and 
                    age_seconds > self.auto_resolve_timeout):
                    
                    await self.resolve_alert(alert_id, "system", 
                                           "Auto-resolved due to timeout")
                    
        except Exception as e:
            logger.error(f"❌ Error checking auto-resolution: {e}")
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts from memory."""
        try:
            # Keep only recent alerts in history
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            self.alert_history = [
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert.triggered_at) > cutoff_time
            ]
            
            # Limit active alerts
            if len(self.active_alerts) > self.max_active_alerts:
                # Remove oldest low-severity alerts
                low_alerts = [
                    (aid, alert) for aid, alert in self.active_alerts.items()
                    if alert.severity == AlertSeverity.LOW
                ]
                
                low_alerts.sort(key=lambda x: x[1].triggered_at)
                
                for aid, _alert in low_alerts[:len(low_alerts)//2]:
                    await self.resolve_alert(aid, "system", "Cleaned up for capacity")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old alerts: {e}")
    
    async def _update_alert_metrics(self):
        """Update alert management metrics."""
        try:
            metrics = [
                ("active_alerts_total", len(self.active_alerts)),
                ("alerts_created_total", self.alerts_created),
                ("alerts_resolved_total", self.alerts_resolved),
                ("alerts_escalated_total", self.alerts_escalated),
                ("notifications_sent_total", self.notifications_sent)
            ]
            
            with sqlite3.connect(self.db_path) as conn:
                for metric_name, value in metrics:
                    conn.execute("""
                        INSERT INTO alert_metrics (metric_name, metric_value, timestamp)
                        VALUES (?, ?, ?)
                    """, (metric_name, value, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error updating alert metrics: {e}")
    
    async def _record_alert_event(self, alert_id: str, event_type: str, event_data: Dict[str, Any]):
        """Record an alert event for audit trail."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO alert_events (alert_id, event_type, event_data, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (alert_id, event_type, str(event_data), datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error recording alert event: {e}")
    
    async def _record_alert_metrics(self, alert: IntelligentAlert):
        """Record metrics for the created alert."""
        try:
            metrics = [
                (f"alert_created_{alert.severity.value}", 1),
                (f"alert_category_{alert.category.lower().replace(' ', '_')}", 1),
                ("alert_confidence", alert.explanation_confidence)
            ]
            
            with sqlite3.connect(self.db_path) as conn:
                for metric_name, value in metrics:
                    conn.execute("""
                        INSERT INTO alert_metrics (metric_name, metric_value, timestamp)
                        VALUES (?, ?, ?)
                    """, (metric_name, value, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error recording alert metrics: {e}")
    
    async def _update_alert_in_db(self, alert: IntelligentAlert):
        """Update an alert in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE intelligent_alerts 
                    SET status = ?, assignee = ?, escalation_level = ?,
                        resolved_at = ?
                    WHERE alert_id = ?
                """, (
                    alert.status.value, alert.assignee, alert.escalation_level,
                    datetime.now().isoformat() if alert.status == AlertStatus.RESOLVED else None,
                    alert.alert_id
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error updating alert in database: {e}")


# Global instance for easy access  
_alert_manager: Optional[IntelligentAlertManager] = None
_alert_manager_lock = threading.Lock()


def get_alert_manager() -> IntelligentAlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    
    if _alert_manager is None:
        with _alert_manager_lock:
            if _alert_manager is None:
                _alert_manager = IntelligentAlertManager()
    
    return _alert_manager