#!/usr/bin/env python3
"""Quick test for NotificationType and NotificationPriority"""

import sys

sys.path.insert(0, "lyrixa")

try:
    from lyrixa.gui.web_mobile_support import (
        NotificationPriority,
        NotificationType,
        SmartNotificationManager,
        WebMobileInterface,
    )

    print("✅ All web mobile support imports successful")

    # Test creating notification manager
    notification_manager = SmartNotificationManager()
    print("✅ SmartNotificationManager created")

    # Test creating notification with enum values
    notification = notification_manager.create_notification(
        NotificationType.SUGGESTION,
        "Test Suggestion",
        "This is a test suggestion message",
        NotificationPriority.NORMAL,
    )
    print("✅ Notification created with enum values")
    print(f"   Type: {notification.type}")
    print(f"   Priority: {notification.priority}")

    print("\n✅ NotificationType and NotificationPriority working correctly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
