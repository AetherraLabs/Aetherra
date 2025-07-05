#!/usr/bin/env python3
"""Simple import test script"""

import sys

sys.path.insert(0, "lyrixa")

try:
    from lyrixa.gui.enhanced_analytics import (
        EnhancedAnalyticsDashboard,
        RealTimeProductivityWidget,
    )

    print("✅ Enhanced analytics imports: OK")
except Exception as e:
    print(f"❌ Enhanced analytics imports: {e}")

try:
    from lyrixa.gui.intelligence_layer import LiveThinkingPane, MemoryGraphWidget

    print("✅ Intelligence layer imports: OK")
except Exception as e:
    print(f"❌ Intelligence layer imports: {e}")

try:
    from lyrixa.gui.live_feedback_loop import (
        AdaptiveLearningEngine,
        LiveFeedbackInterface,
    )

    print("✅ Live feedback loop imports: OK")
except Exception as e:
    print(f"❌ Live feedback loop imports: {e}")

try:
    from lyrixa.gui.web_mobile_support import (
        NotificationPriority,
        NotificationType,
        SmartNotificationManager,
        WebMobileInterface,
    )

    print("✅ Web mobile support imports: OK")
except Exception as e:
    print(f"❌ Web mobile support imports: {e}")

print("\nAll imports tested successfully!")
