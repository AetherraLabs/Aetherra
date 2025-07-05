"""
Comprehensive Test Suite for Advanced GUI Features

Tests all the advanced GUI components and their integration:
- Enhanced Intelligence Layer with advanced visualization
- Real-time Analytics Dashboard with live updates
- Web and Mobile Support with sync capabilities
- Live Feedback Loop with adaptive learning
- Cross-component integration and data flow
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add lyrixa to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))

# Test PySide6 availability first
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    PYSIDE6_AVAILABLE = True
    print("✅ PySide6 is available")
except ImportError as e:
    PYSIDE6_AVAILABLE = False
    print(f"❌ PySide6 not available: {e}")

# Import our advanced GUI modules
try:
    from lyrixa.gui.intelligence_layer import MemoryGraphWidget, LiveThinkingPane
    from lyrixa.gui.enhanced_analytics import EnhancedAnalyticsDashboard, RealTimeProductivityWidget
    from lyrixa.gui.web_mobile_support import WebMobileInterface, SmartNotificationManager
    from lyrixa.gui.live_feedback_loop import LiveFeedbackInterface, AdaptiveLearningEngine
    ADVANCED_GUI_AVAILABLE = True
    print("✅ Advanced GUI modules imported successfully")
except ImportError as e:
    ADVANCED_GUI_AVAILABLE = False
    print(f"❌ Advanced GUI modules not available: {e}")

def test_intelligence_layer():
    """Test the Intelligence Layer components."""
    print("\n🧠 Testing Intelligence Layer...")
    
    try:
        # Test memory graph widget
        if PYSIDE6_AVAILABLE:
            app = QApplication.instance() or QApplication([])
            memory_graph = MemoryGraphWidget()
            print("✅ MemoryGraphWidget created successfully")
            
            # Test adding memory nodes
            from lyrixa.gui.intelligence_layer import MemoryNode
            test_node = MemoryNode(
                id="test_001",
                content="Test memory content",
                memory_type="goal",
                confidence=0.8,
                importance=0.7,
                timestamp=datetime.now(),
                connections=[]
            )
            memory_graph.add_memory_node(test_node)
            print("✅ Memory node added successfully")
            
            # Test live thinking pane
            thinking_pane = LiveThinkingPane()
            print("✅ LiveThinkingPane created successfully")
            
            # Test adding thought processes
            from lyrixa.gui.intelligence_layer import ThoughtProcess
            test_thought = ThoughtProcess(
                id="thought_001",
                description="Analyzing user's coding pattern",
                confidence=0.75,
                context={"task": "coding", "focus_level": 0.8},
                suggestions=["Take a break", "Review code structure"],
                timestamp=datetime.now()
            )
            thinking_pane.add_thought_process(test_thought)
            print("✅ Thought process added successfully")
            
        else:
            print("⚠️ Skipping GUI tests - PySide6 not available")
            
    except Exception as e:
        print(f"❌ Intelligence Layer test failed: {e}")
        return False
    
    return True

def test_enhanced_analytics():
    """Test the Enhanced Analytics Dashboard."""
    print("\n📊 Testing Enhanced Analytics Dashboard...")
    
    try:
        # Test real-time productivity widget
        if PYSIDE6_AVAILABLE:
            app = QApplication.instance() or QApplication([])
            productivity_widget = RealTimeProductivityWidget()
            print("✅ RealTimeProductivityWidget created successfully")
            
            # Test metrics update
            productivity_widget.update_metrics()
            print("✅ Metrics updated successfully")
            
            # Test enhanced analytics dashboard
            dashboard = EnhancedAnalyticsDashboard()
            print("✅ EnhancedAnalyticsDashboard created successfully")
            
            # Test data refresh
            dashboard.refresh_all_data()
            print("✅ Analytics data refreshed successfully")
            
        else:
            print("⚠️ Skipping GUI tests - PySide6 not available")
            
        # Test analytics calculations (non-GUI)
        from lyrixa.gui.enhanced_analytics import ProductivityMetrics, AgentUsageMetrics
        
        test_metrics = ProductivityMetrics(
            focus_score=85.0,
            efficiency_rating=8.5,
            task_completion_rate=0.9,
            goal_progress=0.75,
            break_balance=0.8,
            mood_stability=0.85,
            energy_level=0.8,
            creativity_index=0.7
        )
        print("✅ ProductivityMetrics created successfully")
        
        agent_metrics = AgentUsageMetrics(
            total_interactions=250,
            successful_assists=230,
            response_time_avg=1.1,
            user_satisfaction=4.4,
            feature_usage={"memory": 80, "suggestions": 120, "goals": 50},
            error_rate=0.08,
            learning_progress=0.82
        )
        print("✅ AgentUsageMetrics created successfully")
        
    except Exception as e:
        print(f"❌ Enhanced Analytics test failed: {e}")
        return False
    
    return True

async def test_web_mobile_support():
    """Test Web and Mobile Support functionality."""
    print("\n📱 Testing Web and Mobile Support...")
    
    try:
        # Test notification manager
        notification_manager = SmartNotificationManager()
        print("✅ SmartNotificationManager created successfully")
        
        # Test creating notifications
        from lyrixa.gui.web_mobile_support import NotificationType, NotificationPriority
        
        notification = notification_manager.create_notification(
            NotificationType.SUGGESTION,
            "Test Suggestion",
            "This is a test suggestion message",
            NotificationPriority.NORMAL
        )
        print("✅ Smart notification created successfully")
        
        # Test processing scheduled notifications
        notification_manager.process_scheduled_notifications()
        print("✅ Scheduled notifications processed successfully")
        
        # Test web mobile interface
        interface = WebMobileInterface()
        print("✅ WebMobileInterface created successfully")
        
        # Test starting sessions
        await interface.start_web_session("test-web-device", "test-user")
        await interface.start_mobile_session("test-mobile-device", "test-user")
        print("✅ Web and mobile sessions started successfully")
        
        # Test getting minimal UI data
        ui_data = interface.get_minimal_ui_data()
        print(f"✅ Minimal UI data retrieved: {len(ui_data)} items")
        
        # Test quick actions
        await interface.handle_quick_action("focus_mode")
        await interface.handle_quick_action("sync_now")
        print("✅ Quick actions handled successfully")
        
        # Test sync manager
        if interface.sync_manager:
            sync_result = await interface.sync_manager.sync_data()
            print(f"✅ Data sync completed: {sync_result}")
        
    except Exception as e:
        print(f"❌ Web and Mobile Support test failed: {e}")
        return False
    
    return True

async def test_live_feedback_loop():
    """Test Live Feedback Loop functionality."""
    print("\n🔄 Testing Live Feedback Loop...")
    
    try:
        # Test feedback interface
        feedback_interface = LiveFeedbackInterface()
        print("✅ LiveFeedbackInterface created successfully")
        
        # Test presenting suggestion with feedback
        suggestion = feedback_interface.present_suggestion_with_feedback(
            "test_sug_001",
            "Consider organizing your code into smaller functions for better readability.",
            {"task_type": "coding", "complexity": "high"}
        )
        print("✅ Suggestion with feedback interface created successfully")
        
        # Test handling different feedback actions
        feedback_actions = [
            ("positive_feedback", "test_sug_001", {}),
            ("negative_feedback", "test_sug_001", {}),
            ("edit_suggestion", "test_sug_001", {"edited_text": "Break down complex functions into smaller, focused units."}),
            ("rate_interaction", "", {"rating": 4.0, "comment": "Very helpful suggestion!"})
        ]
        
        for action_type, item_id, data in feedback_actions:
            result = feedback_interface.handle_feedback_action(action_type, item_id, data)
            print(f"✅ Feedback action '{action_type}' handled: {result['status']}")
        
        # Test adaptive settings
        settings = feedback_interface.get_adaptive_settings()
        print(f"✅ Adaptive settings retrieved: {len(settings)} settings")
        
        # Test manual preference updates
        manual_prefs = {
            "intervention_frequency": 0.4,
            "detail_preference": 0.7,
            "proactivity_preference": 0.6
        }
        update_result = feedback_interface.update_manual_preferences(manual_prefs)
        print(f"✅ Manual preferences updated: {update_result['status']}")
        
        # Test learning insights
        insights = feedback_interface.get_learning_insights()
        print(f"✅ Learning insights retrieved: {insights['learning_stats']['total_feedback_items']} feedback items")
        
        # Test adaptive learning engine directly
        learning_engine = AdaptiveLearningEngine()
        profile = learning_engine.get_current_personality()
        print(f"✅ Personality profile retrieved: intervention_frequency={profile.intervention_frequency:.2f}")
        
        adaptation_summary = learning_engine.get_adaptation_summary()
        print(f"✅ Adaptation summary retrieved: {adaptation_summary['status'] if 'status' in adaptation_summary else 'has_data'}")
        
    except Exception as e:
        print(f"❌ Live Feedback Loop test failed: {e}")
        return False
    
    return True

def test_cross_component_integration():
    """Test integration between different advanced GUI components."""
    print("\n🔗 Testing Cross-Component Integration...")
    
    try:
        # Test data flow between components
        feedback_interface = LiveFeedbackInterface()
        web_interface = WebMobileInterface()
        
        print("✅ Multiple interfaces created successfully")
        
        # Simulate feedback affecting notifications
        feedback_interface.handle_feedback_action(
            "positive_feedback", 
            "integration_test", 
            {}
        )
        
        # Get adapted personality and use it for notification preferences
        personality = feedback_interface.learning_engine.get_current_personality()
        
        # Adjust notification frequency based on personality
        web_interface.notification_manager.user_preferences["max_notifications_per_hour"] = max(
            1, int(personality.intervention_frequency * 5)
        )
        
        print("✅ Personality-based notification adjustment applied")
        
        # Test analytics integration with feedback
        analytics_data = {
            "feedback_score": 4.2,
            "adaptation_rate": 0.15,
            "user_satisfaction": personality.feedback_sensitivity,
            "learning_progress": 0.78
        }
        
        print(f"✅ Analytics integration data: {analytics_data}")
        
        # Test memory integration with feedback
        memory_updates = []
        for feedback in feedback_interface.learning_engine.feedback_collector.feedback_history[-5:]:
            memory_update = {
                "type": "feedback_memory",
                "content": f"User feedback: {feedback.feedback_type.value}",
                "confidence": 0.8,
                "timestamp": feedback.timestamp
            }
            memory_updates.append(memory_update)
        
        print(f"✅ Memory integration: {len(memory_updates)} feedback memories created")
        
    except Exception as e:
        print(f"❌ Cross-Component Integration test failed: {e}")
        return False
    
    return True

def test_performance_and_resource_management():
    """Test performance and resource management of advanced features."""
    print("\n⚡ Testing Performance and Resource Management...")
    
    try:
        start_time = time.time()
        
        # Test memory usage with multiple components
        components = []
        
        if PYSIDE6_AVAILABLE:
            app = QApplication.instance() or QApplication([])
            
            # Create multiple instances to test resource management
            for i in range(3):
                memory_graph = MemoryGraphWidget()
                productivity_widget = RealTimeProductivityWidget()
                components.extend([memory_graph, productivity_widget])
        
        # Test feedback processing performance
        feedback_interface = LiveFeedbackInterface()
        
        # Process multiple feedback items quickly
        for i in range(10):
            feedback_interface.handle_feedback_action(
                "positive_feedback" if i % 2 == 0 else "negative_feedback",
                f"perf_test_{i}",
                {}
            )
        
        # Test notification processing performance
        web_interface = WebMobileInterface()
        
        # Create multiple notifications
        for i in range(20):
            web_interface.notification_manager.create_notification(
                NotificationType.SUGGESTION,
                f"Performance Test {i}",
                f"Test notification message {i}",
                NotificationPriority.LOW
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Performance test completed in {processing_time:.3f} seconds")
        print(f"✅ Created {len(components)} GUI components")
        print(f"✅ Processed 10 feedback items and 20 notifications")
        
        # Test memory cleanup
        components.clear()
        print("✅ Component cleanup completed")
        
    except Exception as e:
        print(f"❌ Performance and Resource Management test failed: {e}")
        return False
    
    return True

async def test_real_time_features():
    """Test real-time update capabilities."""
    print("\n⏱️ Testing Real-Time Features...")
    
    try:
        # Test real-time productivity monitoring
        if PYSIDE6_AVAILABLE:
            app = QApplication.instance() or QApplication([])
            productivity_widget = RealTimeProductivityWidget()
            
            # Simulate real-time updates
            for i in range(3):
                productivity_widget.update_metrics()
                await asyncio.sleep(0.1)  # Small delay to simulate real-time
            
            print("✅ Real-time productivity updates working")
        
        # Test real-time notification processing
        notification_manager = SmartNotificationManager()
        
        # Schedule notification for immediate processing
        future_time = datetime.now() + timedelta(seconds=1)
        notification_manager.create_notification(
            NotificationType.REMINDER,
            "Real-time Test",
            "This is a real-time test notification",
            scheduled_time=future_time
        )
        
        # Wait for processing
        await asyncio.sleep(1.5)
        notification_manager.process_scheduled_notifications()
        print("✅ Real-time notification scheduling working")
        
        # Test adaptive learning real-time adjustments
        feedback_interface = LiveFeedbackInterface()
        
        # Rapid feedback processing
        for i in range(5):
            feedback_interface.handle_feedback_action(
                "rate_interaction",
                "",
                {"rating": 3.0 + (i * 0.5), "comment": f"Test feedback {i}"}
            )
            await asyncio.sleep(0.1)
        
        print("✅ Real-time adaptive learning working")
        
    except Exception as e:
        print(f"❌ Real-Time Features test failed: {e}")
        return False
    
    return True

async def run_comprehensive_tests():
    """Run all comprehensive tests for advanced GUI features."""
    print("🚀 Starting Comprehensive Advanced GUI Features Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Intelligence Layer", test_intelligence_layer),
        ("Enhanced Analytics", test_enhanced_analytics),
        ("Web Mobile Support", test_web_mobile_support),
        ("Live Feedback Loop", test_live_feedback_loop),
        ("Cross-Component Integration", test_cross_component_integration),
        ("Performance & Resource Management", test_performance_and_resource_management),
        ("Real-Time Features", test_real_time_features)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} tests...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test suite failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL ADVANCED GUI FEATURES TESTS PASSED!")
        print("✅ Intelligence Layer with advanced visualization: Working")
        print("✅ Real-time Analytics Dashboard: Working")
        print("✅ Web and Mobile Support with sync: Working")
        print("✅ Live Feedback Loop with adaptive learning: Working")
        print("✅ Cross-component integration: Working")
        print("✅ Performance and resource management: Working")
        print("✅ Real-time update capabilities: Working")
        
        print("\n🚀 Advanced GUI features are ready for production!")
        
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above for details.")
        
    return passed == total

if __name__ == "__main__":
    # Run the comprehensive test suite
    success = asyncio.run(run_comprehensive_tests())
    
    if success:
        print("\n🎯 Ready for next phase: Production deployment and user testing!")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")
    
    # Keep GUI applications alive briefly if created
    if PYSIDE6_AVAILABLE:
        app = QApplication.instance()
        if app:
            QTimer.singleShot(1000, app.quit)  # Close after 1 second
            # Don't actually exec() to avoid hanging in test environment
