#!/usr/bin/env python3
"""
Test the enhanced plugin system
"""

from core.plugin_manager import discover_plugins_by_intent, execute_plugin_command

# Test plugin command execution
print("🧪 Testing Plugin System")
print("=" * 50)

# Test math plugin
print("\n🔢 Testing Math Plugin:")
result = execute_plugin_command('plugin: calculate "2 + 3 * 4"')
print(f"Result: {result}")

# Test file operations
print("\n📄 Testing File Tools:")
result = execute_plugin_command('plugin: create_file "test_output.txt" "Hello from plugin system!"')
print(f"Create result: {result}")

result = execute_plugin_command('plugin: read_file "test_output.txt"')
print(f"Read result: {result}")

# Test git status (if in git repo)
print("\n📦 Testing Git Plugin:")
result = execute_plugin_command('plugin: git_status')
print(f"Git status: {result}")

# Test plugin discovery
print("\n🔍 Testing Plugin Discovery:")
suggestions = discover_plugins_by_intent("I want to calculate some math")
print(f"Found {len(suggestions)} relevant plugins:")
for suggestion in suggestions[:3]:
    print(f"  - {suggestion['name']}: {suggestion['reason']}")

# Test voice command processing
print("\n🎤 Testing Voice Plugin:")
result = execute_plugin_command('plugin: whisper_voice_command "remember to commit my changes"')
print(f"Voice result: {result}")

print("\n✅ Plugin system tests completed!")
