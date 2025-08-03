#!/usr/bin/env python3
"""
🌉 Phase 2: Live Context Bridge Demo
===================================

Demonstrates the real-time bidirectional communication between
Python backend and web panels with live data updates.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "Aetherra"))

try:
    from lyrixa_core.gui.main_window import LyrixaHybridWindow
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer

    def simulate_backend_data(window):
        """Simulate live backend data updates"""
        print("🔄 Starting Phase 2 live data simulation...")

        # Simulate memory system updates
        memory_data = {
            'total_memories': 1847,
            'recent_memories': 23,
            'memory_load': 67,
            'status': 'active'
        }
        window.web_bridge.data_cache['memory'] = memory_data
        window.web_bridge.memory_updated.emit(
            __import__('json').dumps(memory_data)
        )
        print("🧠 Memory data updated")

        # Simulate plugin updates
        plugin_data = {
            'loaded_plugins': [
                {'name': 'Memory Manager', 'status': 'active', 'version': '2.1.0'},
                {'name': 'Neural Chat', 'status': 'active', 'version': '1.8.3'},
                {'name': 'Analytics Engine', 'status': 'loaded', 'version': '3.0.1'},
                {'name': 'File Watcher', 'status': 'active', 'version': '1.2.5'},
            ],
            'active_count': 3,
            'total_count': 4,
            'status': 'operational'
        }
        window.web_bridge.data_cache['plugins'] = plugin_data
        window.web_bridge.plugin_updated.emit(
            __import__('json').dumps(plugin_data)
        )
        print("🔌 Plugin data updated")

        # Simulate agent updates
        agent_data = {
            'active_agents': 5,
            'current_goals': [
                'Analyze recent conversations',
                'Update knowledge base',
                'Monitor system performance',
                'Process pending tasks',
                'Self-improvement analysis'
            ],
            'recent_thoughts': [
                'User seems interested in Phase 2 features',
                'GUI performance is excellent',
                'Need to optimize memory usage'
            ],
            'status': 'thinking'
        }
        window.web_bridge.data_cache['agents'] = agent_data
        window.web_bridge.agent_updated.emit(
            __import__('json').dumps(agent_data)
        )
        print("🤖 Agent data updated")

        # Send a test notification
        notification = {
            'level': 'success',
            'message': 'Phase 2 Live Context Bridge is operational!',
            'timestamp': int(time.time())
        }
        window.web_bridge.notification_sent.emit(
            __import__('json').dumps(notification)
        )
        print("🔔 Test notification sent")

    def create_live_updates(window):
        """Create timer for live updates"""
        update_timer = QTimer()

        def update_metrics():
            import random

            # Generate realistic system metrics
            metrics_data = {
                'cpu_usage': random.randint(15, 85),
                'memory_usage': random.randint(40, 75),
                'process_count': random.randint(180, 220),
                'uptime': time.time() % 86400,
                'timestamp': int(time.time())
            }

            window.web_bridge.data_cache['metrics'] = metrics_data
            window.web_bridge.metrics_updated.emit(
                __import__('json').dumps(metrics_data)
            )
            print(f"📊 Live metrics: CPU {metrics_data['cpu_usage']}% | RAM {metrics_data['memory_usage']}%")

        update_timer.timeout.connect(update_metrics)
        update_timer.start(3000)  # Update every 3 seconds
        return update_timer

    def test_phase2_bridge():
        """Test Phase 2 Live Context Bridge"""
        print("🚀 Phase 2: Live Context Bridge Demo")
        print("=" * 50)

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Lyrixa Phase 2 Demo")

        # Create hybrid window
        window = LyrixaHybridWindow()

        # Mock backend services
        mock_services = {
            'memory_system': type('MockMemory', (), {
                'total_memories': 1847,
                'recent_count': 23
            })(),
            'plugin_manager': type('MockPluginManager', (), {
                'get_all_plugins': lambda: {
                    'memory_manager': {'loaded': True, 'version': '2.1.0'},
                    'neural_chat': {'loaded': True, 'version': '1.8.3'},
                    'analytics': {'loaded': False, 'version': '3.0.1'}
                }
            })(),
            'agent_orchestrator': type('MockAgents', (), {
                'agents': ['Agent1', 'Agent2', 'Agent3', 'Agent4', 'Agent5'],
                'current_goals': [
                    'Analyze conversations',
                    'Update knowledge',
                    'Monitor performance'
                ]
            })()
        }

        # Connect mock services
        window.web_bridge.connect_backend_services(mock_services)

        # Show window
        window.show()

        print("✅ Phase 2 GUI launched with live context bridge")
        print("[TOOL] Features active:")
        print("   • Real-time memory system updates")
        print("   • Live plugin status monitoring")
        print("   • Agent goal and thought streaming")
        print("   • System metrics with live updates")
        print("   • Bidirectional command system")
        print("   • In-app notification system")
        print("")
        print("🎯 Demo Actions:")
        print("   • Watch live metrics update every 3 seconds")
        print("   • Click buttons to send commands to Python")
        print("   • See real-time data synchronization")
        print("   • View notifications for system events")

        # Start live data simulation after a delay
        QTimer.singleShot(2000, lambda: simulate_backend_data(window))

        # Start live metrics updates
        live_timer = create_live_updates(window)

        # Start the Qt event loop
        exit_code = app.exec()

        live_timer.stop()
        return exit_code

    if __name__ == "__main__":
        exit_code = test_phase2_bridge()
        sys.exit(exit_code)

except Exception as e:
    print(f"[ERROR] Error testing Phase 2 bridge: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
