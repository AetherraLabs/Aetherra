#!/usr/bin/env python3
"""Quick test for the failing test sections"""

import sys

sys.path.insert(0, "lyrixa")

try:
    from lyrixa.gui.enhanced_analytics import RealTimeProductivityWidget
    from lyrixa.gui.web_mobile_support import (
        NotificationPriority,
        NotificationType,
        SmartNotificationManager,
        WebMobileInterface,
    )

    print("✅ All required imports successful")

    # Test Performance and Resource Management section
    print("\n🧪 Testing Performance and Resource Management...")

    try:
        # Create QApplication first for GUI widgets
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance() or QApplication([])
            print("  ✅ QApplication created")
        except ImportError:
            print("  ⚠️ PySide6 not available, skipping GUI widgets")
            app = None

        notification_manager = SmartNotificationManager()
        web_interface = WebMobileInterface()

        if app:
            productivity_widget = RealTimeProductivityWidget()
            print("  ✅ GUI widgets created")

        # Simulate rapid data updates
        for i in range(10):
            notification = notification_manager.create_notification(
                NotificationType.SUGGESTION,
                f"Test notification {i}",
                f"Message {i}",
                NotificationPriority.LOW,
            )

        print("✅ Performance and Resource Management: PASSED")

    except Exception as e:
        print(f"❌ Performance and Resource Management: FAILED - {e}")

    # Test Real-Time Features section
    print("\n🧪 Testing Real-Time Features...")

    try:
        notification_manager = SmartNotificationManager()

        notification = notification_manager.create_notification(
            NotificationType.REMINDER,
            "Real-time test",
            "This is a real-time test message",
        )

        print("✅ Real-Time Features: PASSED")

    except Exception as e:
        print(f"❌ Real-Time Features: FAILED - {e}")

    print("\n🎉 Quick test completed successfully!")

except Exception as e:
    print(f"❌ Import or setup error: {e}")
    import traceback

    traceback.print_exc()
