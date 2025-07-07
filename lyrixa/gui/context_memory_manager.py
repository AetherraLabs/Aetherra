"""
Context Memory Awareness System for Lyrixa
==========================================

Tracks user context switches and adapts Lyrixa's responses accordingly.
Provides intelligent context-aware assistance based on user activity.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List


class ContextMemoryManager:
    """Manages context-aware memory and adaptation for Lyrixa."""
    
    def __init__(self, db_path: str = "lyrixa_context_memory.db"):
        """Initialize the context memory system."""
        self.db_path = Path(db_path)
        self.current_context = "general_chat"
        self.context_history = []
        self.user_preferences = {}
        self._init_database()
        
    def _init_database(self):
        """Initialize the context memory database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER DEFAULT 0,
                actions_taken TEXT,
                user_satisfaction INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_context_preferences (
                context_type TEXT PRIMARY KEY,
                preferred_response_style TEXT,
                common_requests TEXT,
                assistance_level INTEGER DEFAULT 3
            )
        """)
        
        conn.commit()
        conn.close()
        
    def switch_context(self, new_context: str, metadata: Dict | None = None):
        """Switch to a new context and adapt Lyrixa's behavior."""
        old_context = self.current_context
        self.current_context = new_context
        
        # Record context switch
        self._record_context_switch(old_context, new_context, metadata or {})
        
        # Update context-specific suggestions
        suggestions = self._get_context_suggestions(new_context)
        
        return {
            "context": new_context,
            "suggestions": suggestions,
            "adaptive_message": self._generate_adaptive_message(new_context),
            "quick_actions": self._get_quick_actions(new_context)
        }
        
    def _record_context_switch(self, old_context: str, new_context: str, metadata: Dict):
        """Record a context switch for learning purposes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO context_sessions (context_type, actions_taken)
            VALUES (?, ?)
        """, (new_context, json.dumps(metadata)))
        
        conn.commit()
        conn.close()
        
        # Update pattern tracking
        self._update_context_patterns(new_context, metadata)
        
    def _update_context_patterns(self, context: str, metadata: Dict):
        """Update pattern recognition for context switches."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pattern_key = f"{context}_{metadata.get('trigger', 'manual')}"
        
        # Check if pattern exists
        cursor.execute("""
            SELECT frequency FROM context_patterns 
            WHERE context_type = ? AND pattern_data LIKE ?
        """, (context, f"%{pattern_key}%"))
        
        result = cursor.fetchone()
        
        if result:
            # Update frequency
            cursor.execute("""
                UPDATE context_patterns 
                SET frequency = frequency + 1, last_seen = CURRENT_TIMESTAMP
                WHERE context_type = ? AND pattern_data LIKE ?
            """, (context, f"%{pattern_key}%"))
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO context_patterns (context_type, pattern_data)
                VALUES (?, ?)
            """, (context, json.dumps({pattern_key: metadata})))
            
        conn.commit()
        conn.close()
        
    def _get_context_suggestions(self, context: str) -> List[str]:
        """Get context-specific suggestions based on history."""
        suggestions_map = {
            "plugin_mode": [
                "Browse our plugin marketplace for new capabilities",
                "Create a custom plugin for your specific needs",
                "Check plugin compatibility and performance",
                "View plugin analytics and usage patterns"
            ],
            "chat_mode": [
                "Ask me anything about your Aetherra project",
                "Get help with debugging or optimization",
                "Generate code or documentation",
                "Discuss project architecture and design"
            ],
            "code_editor": [
                "I can help analyze your code structure",
                "Want me to suggest optimizations?",
                "Need help with debugging this section?",
                "Shall I generate documentation for this code?"
            ],
            "file_browser": [
                "I can help organize your project files",
                "Want me to analyze file dependencies?",
                "Need help finding specific functionality?",
                "Shall I suggest file structure improvements?"
            ],
            "settings_mode": [
                "I can help optimize your configuration",
                "Want to set up custom preferences?",
                "Need help with plugin settings?",
                "Shall I explain configuration options?"
            ]
        }
        
        return suggestions_map.get(context, [
            "How can I assist you today?",
            "What would you like to work on?",
            "I'm here to help with your project!"
        ])
        
    def _generate_adaptive_message(self, context: str) -> str:
        """Generate a context-aware greeting or message."""
        messages = {
            "plugin_mode": "🔌 I see you're exploring plugins! I can help you find the perfect tools or create custom ones.",
            "chat_mode": "💬 Ready to chat! What's on your mind about your Aetherra project?",
            "code_editor": "📝 Looks like you're coding! I'm here to help with analysis, debugging, or suggestions.",
            "file_browser": "📁 Browsing files? I can help you navigate, organize, or understand your project structure.",
            "settings_mode": "⚙️ Configuring settings? I can help you optimize your setup for better productivity."
        }
        
        return messages.get(context, "👋 Hi there! How can I help you today?")
        
    def _get_quick_actions(self, context: str) -> List[Dict[str, str]]:
        """Get context-specific quick actions."""
        actions_map = {
            "plugin_mode": [
                {"label": "Create Plugin", "action": "create_plugin"},
                {"label": "Browse Marketplace", "action": "browse_plugins"},
                {"label": "Plugin Analytics", "action": "show_plugin_analytics"},
                {"label": "Plugin Settings", "action": "configure_plugins"}
            ],
            "chat_mode": [
                {"label": "Code Help", "action": "code_assistance"},
                {"label": "Debug Issue", "action": "debug_help"},
                {"label": "Generate Code", "action": "code_generation"},
                {"label": "Project Overview", "action": "show_overview"}
            ],
            "code_editor": [
                {"label": "Analyze Code", "action": "analyze_code"},
                {"label": "Suggest Optimizations", "action": "optimize_code"},
                {"label": "Generate Docs", "action": "generate_docs"},
                {"label": "Find Issues", "action": "code_review"}
            ]
        }
        
        return actions_map.get(context, [
            {"label": "Help", "action": "show_help"},
            {"label": "Tips", "action": "show_tips"}
        ])
        
    def learn_from_interaction(self, context: str, action: str, satisfaction: int):
        """Learn from user interactions to improve future suggestions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update user preferences for this context
        cursor.execute("""
            INSERT OR REPLACE INTO user_context_preferences 
            (context_type, preferred_response_style, assistance_level)
            VALUES (?, ?, ?)
        """, (context, action, satisfaction))
        
        conn.commit()
        conn.close()
        
    def get_context_intelligence(self) -> Dict:
        """Get intelligence about current context and patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get context statistics
        cursor.execute("""
            SELECT context_type, COUNT(*), AVG(user_satisfaction)
            FROM context_sessions 
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY context_type
            ORDER BY COUNT(*) DESC
        """)
        
        recent_contexts = cursor.fetchall()
        
        # Get most common patterns
        cursor.execute("""
            SELECT context_type, pattern_data, frequency
            FROM context_patterns
            ORDER BY frequency DESC
            LIMIT 10
        """)
        
        common_patterns = cursor.fetchall()
        
        conn.close()
        
        return {
            "current_context": self.current_context,
            "recent_contexts": recent_contexts,
            "common_patterns": common_patterns,
            "context_suggestions": self._get_context_suggestions(self.current_context),
            "adaptive_message": self._generate_adaptive_message(self.current_context)
        }
