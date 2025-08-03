"""
🛡️ Aetherra Security Integration Example
========================================

This example demonstrates how to integrate the Aetherra security system
into your applications for comprehensive protection.

Author: Aetherra Security Team
Date: July 16, 2025
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Aetherra.security.security_system import (
    AetherraSecuritySystem,
    SecurityConfig,
    secure_api_call,
    get_security_system,
    initialize_aetherra_security
)

def example_ai_chat_application():
    """Example of using security system in an AI chat application"""

    print("🤖 Aetherra AI Chat Application with Security")
    print("=" * 50)

    # Initialize security system
    config = SecurityConfig(
        api_key_rotation_days=30,
        memory_monitoring_enabled=True,
        leak_detection_enabled=True,
        auto_cleanup_enabled=True
    )

    security_system = initialize_aetherra_security(config=config)

    # Store API keys securely
    print("🔐 Storing API keys securely...")

    # Example API keys (in real app, these would come from user input or secure storage)
    api_keys = {
        "openai": "sk-fake-openai-key-for-demo",
        "anthropic": "sk-ant-fake-anthropic-key-for-demo",
        "google": "AIza-fake-google-key-for-demo"
    }

    for provider, key in api_keys.items():
        security_system.api_key_manager.store_api_key(provider, key)
        print(f"  ✅ {provider} API key stored securely")

    # Monitor memory usage
    print(f"\n📊 Memory monitoring enabled")
    memory_report = security_system.memory_manager.get_memory_report()
    print(f"  Current memory usage: {memory_report['current_usage']['percent']:.1f}%")

    # Example secure API calls
    print(f"\n🔄 Making secure API calls...")

    def mock_openai_call(*args, **kwargs):
        """Mock OpenAI API call"""
        return {
            "response": "Hello! This is a secure AI response.",
            "model": "gpt-4",
            "tokens": 42,
            "api_key_used": kwargs.get("api_key", "")[:10] + "..."
        }

    def mock_anthropic_call(*args, **kwargs):
        """Mock Anthropic API call"""
        return {
            "response": "Hi there! This is a secure Claude response.",
            "model": "claude-3",
            "tokens": 38,
            "api_key_used": kwargs.get("api_key", "")[:10] + "..."
        }

    # Make secure API calls
    with security_system.memory_manager.memory_context("ai_chat_session"):
        # OpenAI call
        openai_result = secure_api_call("openai", mock_openai_call, prompt="Hello!")
        print(f"  🤖 OpenAI: {openai_result['response']}")
        print(f"    Model: {openai_result['model']}, Tokens: {openai_result['tokens']}")

        # Anthropic call
        anthropic_result = secure_api_call("anthropic", mock_anthropic_call, prompt="Hi!")
        print(f"  🤖 Anthropic: {anthropic_result['response']}")
        print(f"    Model: {anthropic_result['model']}, Tokens: {anthropic_result['tokens']}")

    # Security status
    print(f"\n🛡️ Security Status:")
    status = security_system.get_security_status()
    print(f"  API Keys stored: {status['api_keys']['stored_keys']}")
    print(f"  Memory usage: {status['memory']['current_usage']['percent']:.1f}%")
    print(f"  Security alerts: {status['alerts']}")
    print(f"  Monitoring active: {status['monitoring_active']}")

    # Force security scan
    print(f"\n🔍 Running security scan...")
    security_system.force_security_scan()

    # Show updated status
    updated_status = security_system.get_security_status()
    print(f"  Security scan completed at: {time.ctime(updated_status['last_scan'])}")

    # Cleanup
    print(f"\n🧹 Cleaning up...")
    security_system.cleanup_all()
    print("  ✅ Security cleanup completed")

def example_plugin_system():
    """Example of using security system in a plugin system"""

    print("\n🔌 Aetherra Plugin System with Security")
    print("=" * 50)

    security_system = get_security_system()

    # Simulate plugin execution with memory monitoring
    plugins = [
        {"name": "Weather Plugin", "memory_intensive": False},
        {"name": "Image Generator", "memory_intensive": True},
        {"name": "Code Analyzer", "memory_intensive": True},
        {"name": "Simple Calculator", "memory_intensive": False}
    ]

    print("🚀 Executing plugins with security monitoring...")

    for plugin in plugins:
        print(f"\n  [DISC] Running {plugin['name']}...")

        # Use memory context for each plugin
        with security_system.memory_manager.memory_context(f"plugin_{plugin['name']}"):
            # Simulate plugin work
            if plugin['memory_intensive']:
                # Simulate memory-intensive operation
                data = [i * i for i in range(10000)]
                print(f"    💾 Memory-intensive operation completed")
            else:
                # Simulate simple operation
                result = 2 + 2
                print(f"    ⚡ Simple operation completed: {result}")

            # Check memory usage
            memory_report = security_system.memory_manager.get_memory_report()
            print(f"    📊 Memory usage: {memory_report['current_usage']['percent']:.1f}%")

    # Check for memory leaks
    print(f"\n🔍 Checking for memory leaks...")
    leaks = security_system.memory_manager.check_memory_leaks()
    if leaks:
        print(f"  [WARN]  {len(leaks)} potential memory leaks detected")
    else:
        print(f"  ✅ No memory leaks detected")

def example_security_monitoring():
    """Example of continuous security monitoring"""

    print("\n🔍 Aetherra Security Monitoring Example")
    print("=" * 50)

    security_system = get_security_system()

    # Show current security status
    status = security_system.get_security_status()

    print("📊 Current Security Status:")
    print(f"  API Keys: {status['api_keys']['stored_keys']} stored")
    print(f"  Memory Usage: {status['memory']['current_usage']['percent']:.1f}%")
    print(f"  Security Alerts: {status['alerts']}")
    print(f"  Monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")

    # Show configuration
    print(f"\n⚙️  Security Configuration:")
    print(f"  API Key Rotation: {status['config']['api_key_rotation_days']} days")
    print(f"  Memory Monitoring: {status['config']['memory_monitoring_enabled']}")
    print(f"  Leak Detection: {status['config']['leak_detection_enabled']}")
    print(f"  Auto Cleanup: {status['config']['auto_cleanup_enabled']}")

    # Show security alerts if any
    if hasattr(security_system, 'security_alerts') and security_system.security_alerts:
        print(f"\n🚨 Recent Security Alerts:")
        for alert in security_system.security_alerts[-3:]:  # Show last 3 alerts
            print(f"  {time.ctime(alert['timestamp'])}: {alert['alert']}")

def main():
    """Main demonstration"""
    print("🛡️ Aetherra Security System Integration Examples")
    print("=" * 60)

    try:
        # Example 1: AI Chat Application
        example_ai_chat_application()

        # Example 2: Plugin System
        example_plugin_system()

        # Example 3: Security Monitoring
        example_security_monitoring()

        print(f"\n✅ All security examples completed successfully!")
        print(f"🛡️ Your Aetherra application is now secured with:")
        print(f"  • Encrypted API key storage")
        print(f"  • Memory leak detection")
        print(f"  • Continuous security monitoring")
        print(f"  • Automatic cleanup and optimization")

    except Exception as e:
        print(f"\n❌ Error in security demonstration: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Ensure cleanup
        try:
            security_system = get_security_system()
            security_system.cleanup_all()
            print(f"\n🧹 Security system cleaned up successfully")
        except:
            pass

if __name__ == "__main__":
    main()
