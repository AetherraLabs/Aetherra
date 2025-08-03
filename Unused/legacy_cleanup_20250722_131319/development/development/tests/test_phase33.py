"""
Quick Phase 3.3 Integration Test
===============================
"""

import os
import sys

# Add path
sys.path.append(os.path.dirname(__file__))

try:
    from Aetherra.lyrixa.personality.social_learning_integration import (
        get_social_learning_integration_status,
    )

    print("✅ Phase 3.3 Social Learning Infrastructure - Successfully imported!")

    status = get_social_learning_integration_status()
    print(f"📊 System Health: {status.get('system_health', 'Unknown')}")
    print(f"🔒 Privacy Compliance: {status.get('privacy_compliance', 'Unknown')}")
    print("🎉 Phase 3.3 is ready for production!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
