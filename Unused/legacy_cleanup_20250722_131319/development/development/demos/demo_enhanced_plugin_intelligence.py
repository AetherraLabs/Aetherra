#!/usr/bin/env python3
"""
🎮 Enhanced Plugin Intelligence System Demo
==========================================

This script demonstrates the complete enhanced plugin intelligence system
with all the implemented features working together.
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any


class EnhancedPluginDemo:
    """Demo the enhanced plugin intelligence system"""

    def __init__(self):
        self.api_base = "http://127.0.0.1:8006"
        print("🧩 Enhanced Plugin Intelligence System Demo")
        print("=" * 50)

    def test_api_connectivity(self) -> bool:
        """Test if the enhanced API server is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Enhanced API Server: CONNECTED")
                return True
            else:
                print("[WARN] Enhanced API Server: RESPONDING BUT UNHEALTHY")
                return False
        except Exception as e:
            print(f"❌ Enhanced API Server: OFFLINE ({e})")
            return False

    def demo_enhanced_capabilities(self) -> Dict[str, Any]:
        """Demonstrate the enhanced plugin capabilities endpoint"""
        print("\n🔍 Testing Enhanced Plugin Capabilities...")

        try:
            response = requests.get(f"{self.api_base}/api/plugins/enhanced_capabilities")
            if response.status_code == 200:
                data = response.json()

                plugins = data.get("plugins", [])
                summary = data.get("summary", {})

                print(f"✅ Enhanced Capabilities Response:")
                print(f"   [DISC] Total Plugins: {summary.get('total_plugins', 0)}")
                print(f"   ⭐ High Confidence: {summary.get('high_confidence', 0)}")

                # Show category distribution
                categories = summary.get("categories", {})
                print(f"   📂 Categories:")
                for category, count in categories.items():
                    print(f"      {category.title()}: {count}")

                # Show top plugins by confidence
                print(f"\n🏆 Top Plugins by Confidence:")
                for i, plugin in enumerate(plugins[:5], 1):
                    name = plugin.get("name", "Unknown")
                    confidence = plugin.get("confidence_score", 0)
                    category = plugin.get("category", "unknown")
                    capabilities = plugin.get("capabilities", [])
                    is_recommended = plugin.get("lyrixa_recommended", False)

                    icon = "🌟" if is_recommended else "[DISC]"
                    print(f"   {i}. {icon} {name}")
                    print(f"      Confidence: {confidence:.2f}")
                    print(f"      Category: {category.title()}")
                    print(f"      Capabilities: {', '.join(capabilities[:3])}")
                    if is_recommended:
                        print(f"      ⭐ LYRIXA RECOMMENDED")
                    print()

                return data
            else:
                print(f"❌ API Error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {}

    def demo_plugin_filtering(self, plugins_data: Dict[str, Any]):
        """Demonstrate plugin filtering capabilities"""
        print("🔍 Plugin Filtering Demo...")

        plugins = plugins_data.get("plugins", [])
        if not plugins:
            print("❌ No plugins to filter")
            return

        # Filter by confidence
        high_confidence = [p for p in plugins if p.get("confidence_score", 0) > 0.8]
        print(f"   High Confidence (>0.8): {len(high_confidence)} plugins")

        # Filter by category
        categories = {}
        for plugin in plugins:
            cat = plugin.get("category", "unknown")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(plugin)

        print(f"   Category Breakdown:")
        for category, cat_plugins in categories.items():
            print(f"      {category.title()}: {len(cat_plugins)} plugins")

        # Filter by capabilities
        capability_counts = {}
        for plugin in plugins:
            for capability in plugin.get("capabilities", []):
                capability_counts[capability] = capability_counts.get(capability, 0) + 1

        print(f"   Top Capabilities:")
        sorted_caps = sorted(capability_counts.items(), key=lambda x: x[1], reverse=True)
        for capability, count in sorted_caps[:5]:
            print(f"      {capability.replace('_', ' ').title()}: {count} plugins")

    def demo_ai_recommendations(self, plugins_data: Dict[str, Any]):
        """Demonstrate AI recommendation features"""
        print("\n🧠 AI Recommendation Demo...")

        plugins = plugins_data.get("plugins", [])

        # Lyrixa recommended plugins
        recommended = [p for p in plugins if p.get("lyrixa_recommended", False)]
        print(f"   ⭐ Lyrixa Recommended: {len(recommended)} plugins")

        for plugin in recommended[:3]:
            name = plugin.get("name", "Unknown")
            confidence = plugin.get("confidence_score", 0)
            collab = plugin.get("collaboration_potential", 0)
            complexity = plugin.get("complexity_level", "unknown")

            print(f"      🌟 {name}")
            print(f"         Confidence: {confidence:.2f}")
            print(f"         Collaboration Potential: {collab:.2f}")
            print(f"         Complexity: {complexity.title()}")

        # Collaboration potential analysis
        high_collab = [p for p in plugins if p.get("collaboration_potential", 0) > 0.15]
        print(f"\n   🤝 High Collaboration Potential: {len(high_collab)} plugins")
        print(f"      These plugins work well with others in workflows")

    def demo_plugin_details(self, plugins_data: Dict[str, Any]):
        """Demonstrate detailed plugin analysis"""
        print("\n📊 Detailed Plugin Analysis Demo...")

        plugins = plugins_data.get("plugins", [])
        if not plugins:
            return

        # Take the first high-confidence plugin for detailed analysis
        top_plugin = plugins[0]

        print(f"   🔍 Analyzing: {top_plugin.get('name', 'Unknown')}")
        print(f"   " + "=" * 40)

        # Basic info
        print(f"   📂 Category: {top_plugin.get('category', 'unknown').title()}")
        print(f"   📊 Confidence: {top_plugin.get('confidence_score', 0):.2f}")
        print(f"   [TOOL] Complexity: {top_plugin.get('complexity_level', 'unknown').title()}")
        print(f"   📝 Description: {top_plugin.get('description', 'No description')[:60]}...")

        # Capabilities and tags
        capabilities = top_plugin.get("capabilities", [])
        tags = top_plugin.get("tags", [])

        if capabilities:
            print(f"   ⚡ Capabilities: {', '.join(capabilities)}")
        if tags:
            print(f"   🏷️ Tags: {', '.join(tags[:5])}")

        # Technical details
        functions = top_plugin.get("functions", [])
        line_count = top_plugin.get("line_count", 0)

        print(f"   [TOOL] Technical Details:")
        print(f"      Functions: {len(functions)}")
        print(f"      Lines of Code: {line_count}")

        # Show function details
        if functions:
            print(f"      Sample Functions:")
            for func in functions[:3]:
                name = func.get("name", "unknown")
                has_docs = func.get("has_docstring", False)
                docs_icon = "📚" if has_docs else "❓"
                print(f"         {docs_icon} {name}()")

    def run_demo(self):
        """Run the complete demo"""
        # Test connectivity
        if not self.test_api_connectivity():
            print("\n❌ Cannot proceed without API server")
            print("   Start the server with: python enhanced_api_server.py")
            return

        # Get enhanced capabilities
        plugins_data = self.demo_enhanced_capabilities()
        if not plugins_data:
            print("\n❌ Could not retrieve plugin data")
            return

        # Demo filtering
        self.demo_plugin_filtering(plugins_data)

        # Demo AI recommendations
        self.demo_ai_recommendations(plugins_data)

        # Demo detailed analysis
        self.demo_plugin_details(plugins_data)

        print("\n🎉 Enhanced Plugin Intelligence Demo Complete!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Real-time plugin capability analysis")
        print("   ✅ AI-powered confidence scoring")
        print("   ✅ Intelligent categorization and tagging")
        print("   ✅ Collaboration potential assessment")
        print("   ✅ Lyrixa recommendation system")
        print("   ✅ Advanced filtering and search capabilities")
        print("\n🚀 Ready for UI integration and user testing!")


if __name__ == "__main__":
    demo = EnhancedPluginDemo()
    demo.run_demo()
