"""
Web and Mobile Support Module for Lyrixa AI Assistant

Provides cross-platform synchronization and smart notification capabilities:
- Real-time sync of suggestions and memory across devices
- Push notification system for reminders and insights
- Minimal mobile-friendly web UI
- Smart notification filtering and timing
- Offline support with sync queue
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications."""
    REMINDER = "reminder"
    SUGGESTION = "suggestion"
    ACHIEVEMENT = "achievement"
    INSIGHT = "insight"
    GOAL_UPDATE = "goal_update"
    BREAK_REMINDER = "break_reminder"
    FOCUS_ALERT = "focus_alert"

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class SmartNotification:
    """Smart notification data structure."""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    timestamp: datetime
    scheduled_time: Optional[datetime] = None
    device_targets: List[str] = None
    context: Dict[str, Any] = None
    actions: List[Dict[str, str]] = None
    delivered: bool = False
    dismissed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.scheduled_time:
            data['scheduled_time'] = self.scheduled_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SmartNotification':
        """Create from dictionary."""
        data['type'] = NotificationType(data['type'])
        data['priority'] = NotificationPriority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('scheduled_time'):
            data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])
        return cls(**data)

@dataclass
class SyncData:
    """Data structure for cross-device synchronization."""
    device_id: str
    user_id: str
    timestamp: datetime
    memory_updates: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    analytics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class SmartNotificationManager:
    """Manages smart notifications with context-aware filtering."""
    
    def __init__(self):
        self.notifications = []
        self.notification_queue = []
        self.user_preferences = {
            "quiet_hours": {"start": "22:00", "end": "08:00"},
            "max_notifications_per_hour": 3,
            "priority_threshold": NotificationPriority.NORMAL,
            "focus_mode": False,
            "notification_types": {
                NotificationType.REMINDER: True,
                NotificationType.SUGGESTION: True,
                NotificationType.ACHIEVEMENT: True,
                NotificationType.INSIGHT: True,
                NotificationType.GOAL_UPDATE: True,
                NotificationType.BREAK_REMINDER: True,
                NotificationType.FOCUS_ALERT: False
            }
        }
        self.notification_history = []
        
    def create_notification(self, 
                          notification_type: NotificationType,
                          title: str, 
                          message: str,
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          context: Optional[Dict[str, Any]] = None,
                          actions: Optional[List[Dict[str, str]]] = None,
                          scheduled_time: Optional[datetime] = None,
                          device_targets: Optional[List[str]] = None) -> SmartNotification:
        """Create a new smart notification."""
        
        notification = SmartNotification(
            id=str(uuid.uuid4()),
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            timestamp=datetime.now(),
            scheduled_time=scheduled_time,
            device_targets=device_targets or ["all"],
            context=context or {},
            actions=actions or []
        )
        
        if self._should_send_notification(notification):
            if scheduled_time and scheduled_time > datetime.now():
                self.notification_queue.append(notification)
                logger.info(f"Notification scheduled for {scheduled_time}: {title}")
            else:
                self._send_notification(notification)
        else:
            logger.info(f"Notification filtered: {title}")
            
        return notification
        
    def _should_send_notification(self, notification: SmartNotification) -> bool:
        """Determine if notification should be sent based on smart filtering."""
        
        # Check if notification type is enabled
        if not self.user_preferences["notification_types"].get(notification.type, True):
            return False
            
        # Check priority threshold
        priority_levels = {
            NotificationPriority.LOW: 0,
            NotificationPriority.NORMAL: 1,
            NotificationPriority.HIGH: 2,
            NotificationPriority.URGENT: 3
        }
        
        if priority_levels[notification.priority] < priority_levels[self.user_preferences["priority_threshold"]]:
            return False
            
        # Check quiet hours
        if self._is_quiet_hours():
            return notification.priority == NotificationPriority.URGENT
            
        # Check rate limiting
        if self._exceeds_rate_limit():
            return notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]
            
        # Check focus mode
        if self.user_preferences["focus_mode"]:
            return notification.type in [NotificationType.BREAK_REMINDER, NotificationType.FOCUS_ALERT]
            
        return True
        
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        now = datetime.now().time()
        quiet_start = datetime.strptime(self.user_preferences["quiet_hours"]["start"], "%H:%M").time()
        quiet_end = datetime.strptime(self.user_preferences["quiet_hours"]["end"], "%H:%M").time()
        
        if quiet_start <= quiet_end:
            return quiet_start <= now <= quiet_end
        else:
            return now >= quiet_start or now <= quiet_end
            
    def _exceeds_rate_limit(self) -> bool:
        """Check if notification rate limit is exceeded."""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_notifications = [n for n in self.notification_history 
                              if n.timestamp > one_hour_ago and n.delivered]
        
        return len(recent_notifications) >= self.user_preferences["max_notifications_per_hour"]
        
    def _send_notification(self, notification: SmartNotification):
        """Send notification to appropriate channels."""
        try:
            # In a real implementation, this would send to various channels:
            # - Web push notifications
            # - Mobile app notifications
            # - Desktop notifications
            # - Email notifications (for important items)
            
            logger.info(f"Sending notification: {notification.title}")
            
            # Mark as delivered
            notification.delivered = True
            notification.timestamp = datetime.now()
            
            # Add to history
            self.notifications.append(notification)
            self.notification_history.append(notification)
            
            # Simulate platform-specific delivery
            self._deliver_to_platforms(notification)
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            
    def _deliver_to_platforms(self, notification: SmartNotification):
        """Deliver notification to specific platforms."""
        
        for target in notification.device_targets:
            if target == "web" or target == "all":
                self._send_web_notification(notification)
            if target == "mobile" or target == "all":
                self._send_mobile_notification(notification)
            if target == "desktop" or target == "all":
                self._send_desktop_notification(notification)
                
    def _send_web_notification(self, notification: SmartNotification):
        """Send web push notification."""
        # Web Push API implementation would go here
        logger.info(f"Web notification: {notification.title}")
        
    def _send_mobile_notification(self, notification: SmartNotification):
        """Send mobile push notification."""
        # Mobile push notification implementation would go here
        logger.info(f"Mobile notification: {notification.title}")
        
    def _send_desktop_notification(self, notification: SmartNotification):
        """Send desktop notification."""
        # Desktop notification implementation would go here
        logger.info(f"Desktop notification: {notification.title}")
        
    def process_scheduled_notifications(self):
        """Process queued scheduled notifications."""
        now = datetime.now()
        due_notifications = [n for n in self.notification_queue 
                           if n.scheduled_time and n.scheduled_time <= now]
        
        for notification in due_notifications:
            self._send_notification(notification)
            self.notification_queue.remove(notification)
            
    def dismiss_notification(self, notification_id: str):
        """Dismiss a notification."""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.dismissed = True
                logger.info(f"Notification dismissed: {notification.title}")
                break
                
    def get_active_notifications(self) -> List[SmartNotification]:
        """Get all active (not dismissed) notifications."""
        return [n for n in self.notifications if not n.dismissed]
        
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update notification preferences."""
        self.user_preferences.update(preferences)
        logger.info("Notification preferences updated")

class CrossPlatformSyncManager:
    """Manages data synchronization across devices."""
    
    def __init__(self, device_id: str, user_id: str):
        self.device_id = device_id
        self.user_id = user_id
        self.sync_queue = []
        self.last_sync = datetime.now()
        self.sync_interval = timedelta(minutes=5)  # Sync every 5 minutes
        self.is_online = True
        
    async def sync_data(self, force: bool = False) -> bool:
        """Synchronize data with remote server."""
        
        if not self.is_online and not force:
            logger.info("Offline mode - queueing sync for later")
            return False
            
        try:
            # Get local changes since last sync
            local_changes = self._get_local_changes()
            
            # Send changes to server
            server_response = await self._upload_changes(local_changes)
            
            # Get remote changes
            remote_changes = await self._download_changes()
            
            # Apply remote changes locally
            await self._apply_remote_changes(remote_changes)
            
            # Update last sync time
            self.last_sync = datetime.now()
            
            logger.info(f"Sync completed successfully for device {self.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False
            
    def _get_local_changes(self) -> SyncData:
        """Get local changes since last sync."""
        # In a real implementation, this would collect changes from:
        # - Memory system updates
        # - New suggestions
        # - Goal progress
        # - User preferences
        # - Analytics data
        
        return SyncData(
            device_id=self.device_id,
            user_id=self.user_id,
            timestamp=datetime.now(),
            memory_updates=[],
            suggestions=[],
            goals=[],
            preferences={},
            analytics={}
        )
        
    async def _upload_changes(self, sync_data: SyncData) -> Dict[str, Any]:
        """Upload local changes to server."""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        logger.info(f"Uploaded {len(sync_data.memory_updates)} memory updates")
        return {"status": "success", "timestamp": datetime.now().isoformat()}
        
    async def _download_changes(self) -> List[SyncData]:
        """Download changes from other devices."""
        # Simulate API call
        await asyncio.sleep(0.1)
        
        # Return simulated remote changes
        return []
        
    async def _apply_remote_changes(self, remote_changes: List[SyncData]):
        """Apply remote changes to local data."""
        for change_set in remote_changes:
            if change_set.device_id != self.device_id:
                # Apply changes from other devices
                logger.info(f"Applying changes from device {change_set.device_id}")
                
                # In a real implementation, this would update:
                # - Local memory system
                # - Suggestion cache
                # - Goal states
                # - User preferences
                # - Analytics data
                
    def queue_offline_changes(self, changes: Dict[str, Any]):
        """Queue changes for sync when back online."""
        self.sync_queue.append({
            "timestamp": datetime.now(),
            "changes": changes
        })
        
    def set_online_status(self, is_online: bool):
        """Update online status."""
        was_offline = not self.is_online
        self.is_online = is_online
        
        if is_online and was_offline:
            logger.info("Back online - processing queued changes")
            asyncio.create_task(self._process_offline_queue())
            
    async def _process_offline_queue(self):
        """Process queued changes when back online."""
        if not self.sync_queue:
            return
            
        logger.info(f"Processing {len(self.sync_queue)} queued changes")
        
        for queued_item in self.sync_queue:
            # Process each queued change
            pass
            
        self.sync_queue.clear()
        await self.sync_data(force=True)

class WebMobileInterface:
    """Provides web and mobile interface capabilities."""
    
    def __init__(self):
        self.notification_manager = SmartNotificationManager()
        self.sync_manager = None
        self.web_session_active = False
        self.mobile_app_active = False
        
    def initialize_device(self, device_id: str, user_id: str):
        """Initialize device-specific sync manager."""
        self.sync_manager = CrossPlatformSyncManager(device_id, user_id)
        
    async def start_web_session(self, device_id: str, user_id: str):
        """Start a web session."""
        self.web_session_active = True
        self.initialize_device(device_id, user_id)
        
        # Send welcome notification
        self.notification_manager.create_notification(
            NotificationType.INSIGHT,
            "Welcome back!",
            "Your Lyrixa assistant is ready to help.",
            NotificationPriority.NORMAL
        )
        
        logger.info(f"Web session started for user {user_id}")
        
    async def start_mobile_session(self, device_id: str, user_id: str):
        """Start a mobile session."""
        self.mobile_app_active = True
        self.initialize_device(device_id, user_id)
        
        # Sync latest data
        if self.sync_manager:
            await self.sync_manager.sync_data()
            
        logger.info(f"Mobile session started for user {user_id}")
        
    def create_smart_reminder(self, 
                            title: str, 
                            message: str, 
                            scheduled_time: datetime,
                            priority: NotificationPriority = NotificationPriority.NORMAL):
        """Create a smart reminder notification."""
        return self.notification_manager.create_notification(
            NotificationType.REMINDER,
            title,
            message,
            priority,
            scheduled_time=scheduled_time
        )
        
    def send_achievement_notification(self, achievement: str, details: str):
        """Send achievement notification."""
        return self.notification_manager.create_notification(
            NotificationType.ACHIEVEMENT,
            f"🏆 Achievement Unlocked!",
            f"{achievement}: {details}",
            NotificationPriority.HIGH
        )
        
    def send_suggestion_notification(self, suggestion: str, context: Dict[str, Any]):
        """Send suggestion notification."""
        return self.notification_manager.create_notification(
            NotificationType.SUGGESTION,
            "💡 Smart Suggestion",
            suggestion,
            NotificationPriority.NORMAL,
            context=context
        )
        
    def get_minimal_ui_data(self) -> Dict[str, Any]:
        """Get data for minimal mobile/web UI."""
        return {
            "active_notifications": [n.to_dict() for n in self.notification_manager.get_active_notifications()],
            "current_goals": [],  # Would come from goal system
            "recent_suggestions": [],  # Would come from suggestion system
            "productivity_score": 75,  # Would come from analytics
            "focus_status": "focused",  # Would come from monitoring system
            "next_reminder": None,  # Next scheduled reminder
            "quick_actions": [
                {"id": "quick_note", "label": "Quick Note", "icon": "📝"},
                {"id": "break_reminder", "label": "Schedule Break", "icon": "☕"},
                {"id": "focus_mode", "label": "Focus Mode", "icon": "🎯"},
                {"id": "sync_now", "label": "Sync Now", "icon": "🔄"}
            ]
        }
        
    async def handle_quick_action(self, action_id: str, params: Dict[str, Any] = None):
        """Handle quick action from mobile/web UI."""
        
        if action_id == "quick_note":
            # Handle quick note creation
            note_content = params.get("content", "")
            logger.info(f"Quick note created: {note_content}")
            
        elif action_id == "break_reminder":
            # Schedule break reminder
            minutes = params.get("minutes", 30)
            scheduled_time = datetime.now() + timedelta(minutes=minutes)
            self.create_smart_reminder(
                "Break Time!",
                "Time for a well-deserved break.",
                scheduled_time,
                NotificationPriority.HIGH
            )
            
        elif action_id == "focus_mode":
            # Toggle focus mode
            self.notification_manager.user_preferences["focus_mode"] = not self.notification_manager.user_preferences["focus_mode"]
            status = "enabled" if self.notification_manager.user_preferences["focus_mode"] else "disabled"
            logger.info(f"Focus mode {status}")
            
        elif action_id == "sync_now":
            # Force sync
            if self.sync_manager:
                success = await self.sync_manager.sync_data(force=True)
                if success:
                    self.notification_manager.create_notification(
                        NotificationType.INSIGHT,
                        "Sync Complete",
                        "All your data is up to date across devices.",
                        NotificationPriority.LOW
                    )
        
        return {"status": "success", "action": action_id}

# Example usage and testing
async def demo_web_mobile_features():
    """Demonstrate web and mobile features."""
    
    # Initialize interface
    interface = WebMobileInterface()
    
    # Start sessions
    await interface.start_web_session("web-device-123", "user-456")
    await interface.start_mobile_session("mobile-device-789", "user-456")
    
    # Create various notifications
    interface.send_achievement_notification(
        "First Week Complete",
        "You've successfully used Lyrixa for a full week!"
    )
    
    interface.send_suggestion_notification(
        "Consider taking a 10-minute break to maintain focus.",
        {"current_focus_time": 90, "optimal_break_time": 10}
    )
    
    # Schedule reminder
    break_time = datetime.now() + timedelta(minutes=2)
    interface.create_smart_reminder(
        "Stretch Break",
        "Time to stand up and stretch your muscles!",
        break_time
    )
    
    # Get UI data
    ui_data = interface.get_minimal_ui_data()
    print("Minimal UI Data:", json.dumps(ui_data, indent=2, default=str))
    
    # Handle quick actions
    await interface.handle_quick_action("focus_mode")
    await interface.handle_quick_action("break_reminder", {"minutes": 15})
    
    # Process notifications
    for _ in range(3):
        await asyncio.sleep(1)
        interface.notification_manager.process_scheduled_notifications()

if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_web_mobile_features())
