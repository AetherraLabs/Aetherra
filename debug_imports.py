"""Debug imports to find pyqtSignal issue"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing individual imports...")

try:
    print("Importing analytics_dashboard...")
    from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
    print("✅ analytics_dashboard imported")
except Exception as e:
    print(f"❌ analytics_dashboard failed: {e}")

try:
    print("Importing suggestion_notifications...")
    from lyrixa.gui.suggestion_notifications import SuggestionNotificationSystem
    print("✅ suggestion_notifications imported")
except Exception as e:
    print(f"❌ suggestion_notifications failed: {e}")

try:
    print("Importing configuration_manager...")
    from lyrixa.gui.configuration_manager import ConfigurationManager
    print("✅ configuration_manager imported")
except Exception as e:
    print(f"❌ configuration_manager failed: {e}")

try:
    print("Importing performance_monitor...")
    from lyrixa.gui.performance_monitor import PerformanceMonitor
    print("✅ performance_monitor imported")
except Exception as e:
    print(f"❌ performance_monitor failed: {e}")

try:
    print("Importing anticipation_engine...")
    from lyrixa.core.anticipation_engine import AnticipationEngine
    print("✅ anticipation_engine imported")
except Exception as e:
    print(f"❌ anticipation_engine failed: {e}")

print("Done testing imports.")
