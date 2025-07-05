#!/usr/bin/env python3
"""
Test script to verify all Lyrixa component imports are working correctly.
"""

print("🔍 TESTING ALL LYRIXA COMPONENT IMPORTS")
print("=" * 60)

# Test Phase 1 - Advanced Memory System
print("\n📋 Phase 1 - Advanced Memory System:")
try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
    from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

    print("   ✅ LyrixaEnhancedMemorySystem")
    print("   ✅ AdvancedMemorySystem")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Phase 2 - Anticipation Engine
print("\n📋 Phase 2 - Anticipation Engine:")
try:
    from lyrixa.anticipation.context_analyzer import ContextAnalyzer
    from lyrixa.anticipation.proactive_assistant import ProactiveAssistant
    from lyrixa.anticipation.suggestion_generator import SuggestionGenerator
    from lyrixa.core.anticipation_engine import AnticipationEngine

    print("   ✅ AnticipationEngine")
    print("   ✅ ContextAnalyzer")
    print("   ✅ ProactiveAssistant")
    print("   ✅ SuggestionGenerator")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Phase 3 - GUI Components
print("\n📋 Phase 3 - GUI Components:")
try:
    from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
    from lyrixa.gui.configuration_manager import ConfigurationManager
    from lyrixa.gui.performance_monitor import PerformanceMonitor

    print("   ✅ AnalyticsDashboard")
    print("   ✅ ConfigurationManager")
    print("   ✅ PerformanceMonitor")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Phase 4 - Advanced GUI
print("\n📋 Phase 4 - Advanced GUI:")
try:
    from lyrixa.gui.enhanced_analytics import EnhancedAnalyticsDashboard
    from lyrixa.gui.intelligence_layer import IntelligenceLayerWidget
    from lyrixa.gui.live_feedback_loop import LiveFeedbackInterface
    from lyrixa.gui.web_mobile_support import WebMobileInterface

    print("   ✅ EnhancedAnalyticsDashboard")
    print("   ✅ IntelligenceLayerWidget")
    print("   ✅ LiveFeedbackInterface")
    print("   ✅ WebMobileInterface")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Main GUI
print("\n📋 Main Enhanced Lyrixa GUI:")
try:
    from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

    print("   ✅ EnhancedLyrixaWindow")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n🎯 IMPORT TEST SUMMARY:")
print("✅ All Phase 1-4 components and main GUI imports tested")
print("📋 Check results above for any missing components")
print("\n🚀 NEXT STEPS:")
print("1. If all imports successful: Run unified launcher")
print("2. If errors found: Fix missing module paths")
print("3. Verify GUI integration and functionality")
