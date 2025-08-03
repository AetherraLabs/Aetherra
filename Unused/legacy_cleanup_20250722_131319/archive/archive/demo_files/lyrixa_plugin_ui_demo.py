#!/usr/bin/env python3
"""
🎙️ LYRIXA PLUGIN UI DEMO
========================

Text-based demonstration of the Lyrixa Plugin UI system.
Shows the plugin architecture, zones, themes, and functionality.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class LyrixaPluginUIDemo:
    """Text-based demonstration of the Plugin UI system"""

    def __init__(self):
        self.plugin_manager = None
        self.config_manager = None
        self.current_theme = "light"
        self.current_mode = "Simple"

        print("🎙️ LYRIXA PLUGIN UI SYSTEM DEMO")
        print("=" * 60)

        self.init_managers()
        self.load_sample_plugins()

    def init_managers(self):
        """Initialize the plugin and configuration managers"""
        try:
            from lyrixa.gui.configuration_manager import ConfigurationManager
            from lyrixa.gui.plugin_ui_loader import PluginUIManager

            self.plugin_manager = PluginUIManager()
            self.config_manager = ConfigurationManager()
            print("✅ Plugin and Configuration managers initialized")
        except Exception as e:
            print(f"❌ Failed to initialize managers: {e}")
            return False
        return True

    def load_sample_plugins(self):
        """Load and demonstrate sample plugins"""
        if not self.plugin_manager:
            return

        try:
            # Load sample plugin data
            from lyrixa.plugins import sample_plugin_1, sample_plugin_2

            plugin1_data = sample_plugin_1.plugin_data
            plugin2_data = sample_plugin_2.plugin_data

            self.plugin_manager.register_plugin(plugin1_data)
            self.plugin_manager.register_plugin(plugin2_data)

            # Assign to zones
            self.plugin_manager.set_zone("plugin_slot_left", plugin1_data)
            self.plugin_manager.set_zone("analytics_panel", plugin2_data)

            print("✅ Sample plugins loaded and assigned to zones")
        except Exception as e:
            print(f"[WARN] Could not load sample plugins: {e}")

    def show_ui_layout(self):
        """Display the current UI layout"""
        print("\n" + "=" * 60)
        print("🎨 CURRENT UI LAYOUT")
        print("=" * 60)

        # Header
        print("┌" + "─" * 58 + "┐")
        print(
            f"│ 🎙️ Lyrixa AI Assistant    Theme: {self.current_theme:>6} | Mode: {self.current_mode:>10} │"
        )
        print("├" + "─" * 19 + "┬" + "─" * 19 + "┬" + "─" * 19 + "┤")

        # Content area
        left_plugin = (
            self.plugin_manager.zones.get("plugin_slot_left", {})
            if self.plugin_manager
            else {}
        )
        center_content = "💬 Main Chat Area"
        right_plugin = (
            self.plugin_manager.zones.get("analytics_panel", {})
            if self.plugin_manager
            else {}
        )

        left_name = left_plugin.get("name", "Empty") if left_plugin else "Empty"
        right_name = right_plugin.get("name", "Empty") if right_plugin else "Empty"

        print(f"│ 🧩 Plugin Zone L   │ {center_content:^17} │ 📊 Analytics Zone │")
        print(f"│ {left_name:^17} │                   │ {right_name:^17} │")
        print("│                   │                   │                   │")
        print("│ • Basic UI Comp   │ Chat conversation │ • System Metrics  │")
        print("│ • Theme-aware     │ displays here     │ • Plugin Stats    │")
        print("│ • Dynamic content │                   │ • Performance     │")
        print("├" + "─" * 19 + "┼" + "─" * 19 + "┼" + "─" * 19 + "┤")
        print("│ Suggestion Panel  │ [Type message...] │ Plugin Controls   │")
        print("└" + "─" * 19 + "┴" + "─" * 19 + "┴" + "─" * 19 + "┘")

        # Footer
        plugin_count = len(self.plugin_manager.plugins) if self.plugin_manager else 0
        print(
            f"Status: ✅ Plugin UI Ready | Plugins: {plugin_count} loaded | Zones: 4 available"
        )

    def show_plugin_info(self):
        """Display detailed plugin information"""
        print("\n" + "=" * 60)
        print("🧩 PLUGIN SYSTEM STATUS")
        print("=" * 60)

        if not self.plugin_manager:
            print("❌ Plugin manager not available")
            return

        print(f"📊 Loaded Plugins: {len(self.plugin_manager.plugins)}")
        print(f"🎨 Current Theme: {self.plugin_manager.theme}")
        print(f"[TOOL] Current Mode: {self.plugin_manager.mode}")

        print("\n🗂️ Plugin Zones:")
        for zone_name, plugin in self.plugin_manager.zones.items():
            if plugin:
                plugin_name = (
                    plugin.get("name", "Unknown")
                    if isinstance(plugin, dict)
                    else "Unknown"
                )
                print(f"  • {zone_name}: {plugin_name}")
            else:
                print(f"  • {zone_name}: [Empty]")

        print("\n[DISC] Registered Plugins:")
        for i, plugin in enumerate(self.plugin_manager.plugins, 1):
            if isinstance(plugin, dict):
                name = plugin.get("name", "Unknown")
                version = plugin.get("version", "Unknown")
                author = plugin.get("author", "Unknown")
                description = plugin.get("description", "No description")
                print(f"  {i}. {name} v{version}")
                print(f"     Author: {author}")
                print(f"     Description: {description}")
            else:
                print(f"  {i}. Unknown plugin format")

    def show_configuration(self):
        """Display configuration information"""
        print("\n" + "=" * 60)
        print("⚙️ CONFIGURATION MANAGER STATUS")
        print("=" * 60)

        if not self.config_manager:
            print("❌ Configuration manager not available")
            return

        try:
            prefs = self.config_manager.get_preferences()
            print(f"👤 User Preferences:")
            print(f"  • Language: {prefs.language}")
            print(f"  • Theme: {prefs.theme}")
            print(f"  • Font: {prefs.font_family} ({prefs.font_size}pt)")
            print(f"  • Notifications: {prefs.enable_notifications}")

            anticipation = self.config_manager.get_anticipation_settings()
            print(f"\n🧠 Anticipation Settings:")
            print(
                f"  • Detection Sensitivity: {anticipation.pattern_detection_sensitivity}"
            )
            print(f"  • Min Occurrences: {anticipation.minimum_pattern_occurrences}")
            print(
                f"  • Confidence Threshold: {anticipation.pattern_confidence_threshold}"
            )
            print(f"  • Max Suggestions: {anticipation.max_concurrent_suggestions}")

        except Exception as e:
            print(f"❌ Error reading configuration: {e}")

    def demonstrate_theme_switching(self):
        """Demonstrate theme switching functionality"""
        print("\n" + "=" * 60)
        print("🎨 THEME SWITCHING DEMONSTRATION")
        print("=" * 60)

        themes = ["light", "dark"]

        for theme in themes:
            print(f"\n🔄 Switching to {theme} theme...")
            self.current_theme = theme

            if self.plugin_manager:
                self.plugin_manager.theme = theme
                self.plugin_manager.notify_plugins_of_theme_change()

            time.sleep(1)

            # Show theme-specific styling
            if theme == "dark":
                print("🌙 Dark Theme Active:")
                print("  • Background: Dark (#2b2b2b)")
                print("  • Text: Light (#ffffff)")
                print("  • Accents: Blue/Purple")
                print("  • Plugin areas: Dark with colored borders")
            else:
                print("☀️ Light Theme Active:")
                print("  • Background: Light (#ffffff)")
                print("  • Text: Dark (#000000)")
                print("  • Accents: Blue/Green")
                print("  • Plugin areas: Light with subtle borders")

            print(f"  ✅ All plugins notified of theme change")

    def demonstrate_mode_switching(self):
        """Demonstrate mode switching functionality"""
        print("\n" + "=" * 60)
        print("[TOOL] MODE SWITCHING DEMONSTRATION")
        print("=" * 60)

        modes = ["Simple", "Developer", "Live Agent"]

        for mode in modes:
            print(f"\n🔄 Switching to {mode} mode...")
            self.current_mode = mode

            if self.plugin_manager:
                self.plugin_manager.switch_mode(mode)

            time.sleep(1)

            # Show mode-specific features
            if mode == "Simple":
                print("👤 Simple Mode Features:")
                print("  • Clean, minimal interface")
                print("  • Essential functions only")
                print("  • User-friendly layout")
                print("  • Suggestion panel active")
            elif mode == "Developer":
                print("💻 Developer Mode Features:")
                print("  • Advanced debugging tools")
                print("  • Code analysis panels")
                print("  • Performance metrics")
                print("  • Analytics panel disabled for focus")
            else:  # Live Agent
                print("🤖 Live Agent Mode Features:")
                print("  • Real-time assistance")
                print("  • Proactive suggestions")
                print("  • Context awareness")
                print("  • Left plugin slot optimized")

            print(f"  ✅ Layout updated for {mode} mode")

    def run_interactive_demo(self):
        """Run the interactive demonstration"""
        while True:
            print("\n" + "=" * 60)
            print("🎮 INTERACTIVE DEMO MENU")
            print("=" * 60)
            print("1. Show UI Layout")
            print("2. Show Plugin Information")
            print("3. Show Configuration")
            print("4. Demonstrate Theme Switching")
            print("5. Demonstrate Mode Switching")
            print("6. Show All Information")
            print("0. Exit")

            try:
                choice = input("\nEnter your choice (0-6): ").strip()

                if choice == "0":
                    print("\n👋 Thanks for exploring the Lyrixa Plugin UI system!")
                    break
                elif choice == "1":
                    self.show_ui_layout()
                elif choice == "2":
                    self.show_plugin_info()
                elif choice == "3":
                    self.show_configuration()
                elif choice == "4":
                    self.demonstrate_theme_switching()
                elif choice == "5":
                    self.demonstrate_mode_switching()
                elif choice == "6":
                    self.show_ui_layout()
                    self.show_plugin_info()
                    self.show_configuration()
                else:
                    print("❌ Invalid choice. Please enter 0-6.")

                input("\n📍 Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Run the Lyrixa Plugin UI demonstration"""
    try:
        demo = LyrixaPluginUIDemo()

        print("\n🎉 Plugin UI system initialized successfully!")
        print("\nThis demo shows the visual structure and functionality")
        print("of the new Lyrixa Plugin UI system without requiring Qt.")

        # Show initial state
        demo.show_ui_layout()

        print("\n" + "=" * 60)
        print("Ready to explore the Plugin UI system!")
        print("You can see the layout, plugin zones, and functionality.")
        print("=" * 60)

        # Run interactive demo
        demo.run_interactive_demo()

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
