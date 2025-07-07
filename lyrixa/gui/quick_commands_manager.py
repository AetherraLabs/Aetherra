"""
Quick Commands Manager for Lyrixa
=================================

Provides GUI buttons and shortcuts for common Lyrixa actions.
Enables rapid access to frequently used features and workflows.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class QuickCommandsManager:
    """Manages quick command buttons and shortcuts for Lyrixa."""
    
    def __init__(self, config_path: str = "lyrixa_quick_commands.json"):
        """Initialize the quick commands manager."""
        self.config_path = Path(config_path)
        self.commands = {}
        self.command_history = []
        self.favorites = []
        self.custom_commands = {}
        self._load_commands_config()
        
    def _load_commands_config(self):
        """Load quick commands configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.commands = config.get('commands', {})
                    self.favorites = config.get('favorites', [])
                    self.custom_commands = config.get('custom_commands', {})
            else:
                self._initialize_default_commands()
        except Exception as e:
            print(f"Error loading quick commands config: {e}")
            self._initialize_default_commands()
    
    def _initialize_default_commands(self):
        """Initialize default quick commands."""
        self.commands = {
            # Analysis Commands
            "analyze_code": {
                "label": "Analyze Code",
                "description": "Analyze current code for improvements",
                "category": "analysis",
                "icon": "🔍",
                "shortcut": "Ctrl+A",
                "action": "analyze_current_code"
            },
            "performance_check": {
                "label": "Performance Check",
                "description": "Check code performance metrics",
                "category": "analysis", 
                "icon": "⚡",
                "shortcut": "Ctrl+P",
                "action": "check_performance"
            },
            
            # Generation Commands
            "generate_docs": {
                "label": "Generate Docs",
                "description": "Generate documentation for code",
                "category": "generation",
                "icon": "📚",
                "shortcut": "Ctrl+D",
                "action": "generate_documentation"
            },
            "create_tests": {
                "label": "Create Tests",
                "description": "Generate unit tests for code",
                "category": "generation",
                "icon": "🧪",
                "shortcut": "Ctrl+T",
                "action": "create_unit_tests"
            },
            
            # Memory Commands
            "save_context": {
                "label": "Save Context",
                "description": "Save current conversation context",
                "category": "memory",
                "icon": "💾",
                "shortcut": "Ctrl+S",
                "action": "save_conversation_context"
            },
            "load_context": {
                "label": "Load Context",
                "description": "Load previous conversation context",
                "category": "memory",
                "icon": "📂",
                "shortcut": "Ctrl+L",
                "action": "load_conversation_context"
            },
            
            # Plugin Commands
            "plugin_manager": {
                "label": "Plugin Manager",
                "description": "Open plugin management interface",
                "category": "plugins",
                "icon": "🔌",
                "shortcut": "Ctrl+M",
                "action": "open_plugin_manager"
            },
            "refresh_plugins": {
                "label": "Refresh Plugins",
                "description": "Reload all active plugins",
                "category": "plugins",
                "icon": "🔄",
                "shortcut": "F5",
                "action": "refresh_all_plugins"
            },
            
            # Chat Commands
            "clear_chat": {
                "label": "Clear Chat",
                "description": "Clear current chat history",
                "category": "chat",
                "icon": "🗑️",
                "shortcut": "Ctrl+X",
                "action": "clear_chat_history"
            },
            "export_chat": {
                "label": "Export Chat",
                "description": "Export chat history to file",
                "category": "chat",
                "icon": "📤",
                "shortcut": "Ctrl+E",
                "action": "export_chat_history"
            },
            
            # Quick Actions
            "quick_help": {
                "label": "Quick Help",
                "description": "Show quick help and shortcuts",
                "category": "help",
                "icon": "❓",
                "shortcut": "F1",
                "action": "show_quick_help"
            },
            "toggle_intelligence": {
                "label": "Intelligence Panel",
                "description": "Toggle intelligence panel visibility",
                "category": "ui",
                "icon": "🧠",
                "shortcut": "Ctrl+I",
                "action": "toggle_intelligence_panel"
            }
        }
        
        self.favorites = [
            "analyze_code",
            "generate_docs", 
            "save_context",
            "plugin_manager"
        ]
        
    def save_commands_config(self):
        """Save commands configuration to file."""
        try:
            config = {
                'commands': self.commands,
                'favorites': self.favorites,
                'custom_commands': self.custom_commands,
                'last_updated': str(datetime.now())
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving quick commands config: {e}")
    
    def execute_command(self, command_id: str) -> bool:
        """Execute a quick command by ID."""
        if command_id in self.commands:
            command = self.commands[command_id]
            
            # Record command execution
            self.command_history.append({
                "command_id": command_id,
                "timestamp": str(datetime.now()),
                "label": command.get("label", command_id)
            })
            
            # Keep only last 100 command executions
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-100:]
            
            print(f"Executing command: {command.get('label', command_id)}")
            return True
        
        elif command_id in self.custom_commands:
            custom_command = self.custom_commands[command_id]
            print(f"Executing custom command: {custom_command.get('label', command_id)}")
            return True
        
        return False
    
    def add_custom_command(self, command_id: str, label: str, description: str, 
                          action: str, icon: str = "⚙️", shortcut: str = ""):
        """Add a custom quick command."""
        self.custom_commands[command_id] = {
            "label": label,
            "description": description,
            "action": action,
            "icon": icon,
            "shortcut": shortcut,
            "category": "custom",
            "created": str(datetime.now())
        }
        self.save_commands_config()
    
    def remove_custom_command(self, command_id: str) -> bool:
        """Remove a custom command."""
        if command_id in self.custom_commands:
            del self.custom_commands[command_id]
            if command_id in self.favorites:
                self.favorites.remove(command_id)
            self.save_commands_config()
            return True
        return False
    
    def add_to_favorites(self, command_id: str) -> bool:
        """Add a command to favorites."""
        if (command_id in self.commands or command_id in self.custom_commands) and command_id not in self.favorites:
            self.favorites.append(command_id)
            self.save_commands_config()
            return True
        return False
    
    def remove_from_favorites(self, command_id: str) -> bool:
        """Remove a command from favorites."""
        if command_id in self.favorites:
            self.favorites.remove(command_id)
            self.save_commands_config()
            return True
        return False
    
    def get_commands_by_category(self, category: str) -> Dict[str, Any]:
        """Get all commands in a specific category."""
        commands = {}
        
        # Check default commands
        for cmd_id, cmd_data in self.commands.items():
            if cmd_data.get("category") == category:
                commands[cmd_id] = cmd_data
                
        # Check custom commands
        for cmd_id, cmd_data in self.custom_commands.items():
            if cmd_data.get("category") == category:
                commands[cmd_id] = cmd_data
                
        return commands
    
    def get_favorite_commands(self) -> Dict[str, Any]:
        """Get all favorite commands."""
        favorites = {}
        
        for cmd_id in self.favorites:
            if cmd_id in self.commands:
                favorites[cmd_id] = self.commands[cmd_id]
            elif cmd_id in self.custom_commands:
                favorites[cmd_id] = self.custom_commands[cmd_id]
                
        return favorites
    
    def get_recent_commands(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recently executed commands."""
        return self.command_history[-count:] if self.command_history else []
    
    def search_commands(self, query: str) -> Dict[str, Any]:
        """Search commands by label or description."""
        results = {}
        query_lower = query.lower()
        
        # Search default commands
        for cmd_id, cmd_data in self.commands.items():
            label = cmd_data.get("label", "").lower()
            description = cmd_data.get("description", "").lower()
            
            if query_lower in label or query_lower in description:
                results[cmd_id] = cmd_data
        
        # Search custom commands
        for cmd_id, cmd_data in self.custom_commands.items():
            label = cmd_data.get("label", "").lower()
            description = cmd_data.get("description", "").lower()
            
            if query_lower in label or query_lower in description:
                results[cmd_id] = cmd_data
                
        return results
    
    def get_all_categories(self) -> List[str]:
        """Get all available command categories."""
        categories = set()
        
        for cmd_data in self.commands.values():
            categories.add(cmd_data.get("category", "general"))
            
        for cmd_data in self.custom_commands.values():
            categories.add(cmd_data.get("category", "custom"))
            
        return sorted(list(categories))
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get statistics about command usage."""
        total_commands = len(self.commands) + len(self.custom_commands)
        total_executions = len(self.command_history)
        
        # Count executions by command
        execution_counts = {}
        for execution in self.command_history:
            cmd_id = execution["command_id"]
            execution_counts[cmd_id] = execution_counts.get(cmd_id, 0) + 1
        
        most_used = max(execution_counts.items(), key=lambda x: x[1]) if execution_counts else ("none", 0)
        
        return {
            "total_commands": total_commands,
            "default_commands": len(self.commands),
            "custom_commands": len(self.custom_commands),
            "favorite_commands": len(self.favorites),
            "total_executions": total_executions,
            "most_used_command": most_used[0],
            "most_used_count": most_used[1],
            "categories": len(self.get_all_categories())
        }
