"""
Chat History Manager for Lyrixa
===============================

Manages conversation history, provides replay functionality,
and enables context-aware conversation references.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class ChatHistoryManager:
    """Manages chat history and conversation context for Lyrixa."""

    def __init__(self, db_path: str = "lyrixa_chat_history.db"):
        """Initialize the chat history manager."""
        self.db_path = Path(db_path)
        self.current_session_id = self._generate_session_id()
        self.max_display_messages = 100
        self._init_database()

    def _init_database(self):
        """Initialize the chat history database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                total_messages INTEGER DEFAULT 0,
                topics TEXT,
                context_tags TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sender TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                content TEXT NOT NULL,
                context_data TEXT,
                message_hash TEXT UNIQUE,
                thread_id TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                first_mention DATETIME DEFAULT CURRENT_TIMESTAMP,
                mention_count INTEGER DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                reaction_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES chat_messages (id)
            )
        """)

        conn.commit()
        conn.close()

        # Create current session
        self._create_session()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def _create_session(self):
        """Create a new chat session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO chat_sessions (session_id)
            VALUES (?)
        """,
            (self.current_session_id,),
        )

        conn.commit()
        conn.close()

    def add_message(
        self,
        sender: str,
        content: str,
        message_type: str = "text",
        context_data: Optional[Dict] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        """Add a message to the current session."""
        message_hash = hashlib.md5(
            f"{sender}:{content}:{datetime.now().isoformat()}".encode()
        ).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO chat_messages
            (session_id, sender, message_type, content, context_data, message_hash, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                self.current_session_id,
                sender,
                message_type,
                content,
                json.dumps(context_data or {}),
                message_hash,
                thread_id,
            ),
        )

        # Update session message count
        cursor.execute(
            """
            UPDATE chat_sessions
            SET total_messages = total_messages + 1
            WHERE session_id = ?
        """,
            (self.current_session_id,),
        )

        conn.commit()
        conn.close()

        # Extract and store topics
        self._extract_topics(content)

        return message_hash

    def _extract_topics(self, content: str):
        """Extract topics from message content for categorization."""
        # Simple keyword-based topic extraction
        topic_keywords = {
            "plugin_development": [
                "plugin",
                "create plugin",
                "plugin system",
                "extension",
            ],
            "code_debugging": ["debug", "error", "bug", "fix", "issue", "problem"],
            "code_generation": ["generate", "create code", "write code", "implement"],
            "project_setup": ["setup", "configure", "install", "initialize"],
            "documentation": ["document", "docs", "readme", "comment", "explain"],
            "optimization": [
                "optimize",
                "performance",
                "speed",
                "efficiency",
                "improve",
            ],
            "ai_assistance": ["help", "assist", "guide", "tutorial", "how to"],
        }

        content_lower = content.lower()
        detected_topics = []

        for topic, keywords in topic_keywords.items():
            confidence = sum(
                1 for keyword in keywords if keyword in content_lower
            ) / len(keywords)
            if confidence > 0:
                detected_topics.append((topic, confidence))

        # Store detected topics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for topic, confidence in detected_topics:
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversation_topics
                (session_id, topic, confidence, mention_count)
                VALUES (?, ?, ?,
                    COALESCE((SELECT mention_count FROM conversation_topics
                             WHERE session_id = ? AND topic = ?), 0) + 1)
            """,
                (
                    self.current_session_id,
                    topic,
                    confidence,
                    self.current_session_id,
                    topic,
                ),
            )

        conn.commit()
        conn.close()

    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """Get recent messages from the current session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT sender, content, message_type, timestamp, context_data, message_hash
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (self.current_session_id, limit),
        )

        messages = []
        for row in cursor.fetchall():
            sender, content, msg_type, timestamp, context_data, msg_hash = row
            messages.append(
                {
                    "sender": sender,
                    "content": content,
                    "type": msg_type,
                    "timestamp": timestamp,
                    "context": json.loads(context_data or "{}"),
                    "hash": msg_hash,
                }
            )

        conn.close()
        return list(reversed(messages))  # Return in chronological order

    def search_history(self, query: str, days_back: int = 7) -> List[Dict]:
        """Search chat history for specific content."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_date = datetime.now() - timedelta(days=days_back)

        cursor.execute(
            """
            SELECT cm.sender, cm.content, cm.timestamp, cm.session_id,
                   cs.topics, cm.context_data
            FROM chat_messages cm
            JOIN chat_sessions cs ON cm.session_id = cs.session_id
            WHERE cm.content LIKE ? AND cm.timestamp > ?
            ORDER BY cm.timestamp DESC
            LIMIT 50
        """,
            (f"%{query}%", since_date.isoformat()),
        )

        results = []
        for row in cursor.fetchall():
            sender, content, timestamp, session_id, topics, context_data = row
            results.append(
                {
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp,
                    "session_id": session_id,
                    "topics": json.loads(topics or "[]"),
                    "context": json.loads(context_data or "{}"),
                }
            )

        conn.close()
        return results

    def get_conversation_summary(self, session_id: Optional[str] = None) -> Dict:
        """Get a summary of a conversation session."""
        if not session_id:
            session_id = self.current_session_id

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get session info
        cursor.execute(
            """
            SELECT start_time, total_messages, topics, context_tags
            FROM chat_sessions
            WHERE session_id = ?
        """,
            (session_id,),
        )

        session_info = cursor.fetchone()

        # Get top topics
        cursor.execute(
            """
            SELECT topic, confidence, mention_count
            FROM conversation_topics
            WHERE session_id = ?
            ORDER BY mention_count DESC, confidence DESC
            LIMIT 5
        """,
            (session_id,),
        )

        topics = cursor.fetchall()

        # Get message types distribution
        cursor.execute(
            """
            SELECT message_type, COUNT(*) as count
            FROM chat_messages
            WHERE session_id = ?
            GROUP BY message_type
        """,
            (session_id,),
        )

        message_types = dict(cursor.fetchall())

        conn.close()

        if not session_info:
            return {}

        start_time, total_messages, session_topics, context_tags = session_info

        return {
            "session_id": session_id,
            "start_time": start_time,
            "total_messages": total_messages,
            "topics": [
                {"topic": t[0], "confidence": t[1], "mentions": t[2]} for t in topics
            ],
            "message_types": message_types,
            "session_topics": json.loads(session_topics or "[]"),
            "context_tags": json.loads(context_tags or "[]"),
        }

    def get_session_list(self, limit: int = 20) -> List[Dict]:
        """Get a list of recent chat sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT session_id, start_time, total_messages, topics
            FROM chat_sessions
            ORDER BY start_time DESC
            LIMIT ?
        """,
            (limit,),
        )

        sessions = []
        for row in cursor.fetchall():
            session_id, start_time, total_messages, topics = row
            sessions.append(
                {
                    "session_id": session_id,
                    "start_time": start_time,
                    "total_messages": total_messages,
                    "preview_topics": json.loads(topics or "[]")[:3],  # First 3 topics
                }
            )

        conn.close()
        return sessions

    def add_message_reaction(self, message_hash: str, reaction_type: str):
        """Add a reaction to a message (thumbs up, down, etc.)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get message ID from hash
        cursor.execute(
            """
            SELECT id FROM chat_messages WHERE message_hash = ?
        """,
            (message_hash,),
        )

        result = cursor.fetchone()
        if result:
            message_id = result[0]
            cursor.execute(
                """
                INSERT INTO message_reactions (message_id, reaction_type)
                VALUES (?, ?)
            """,
                (message_id, reaction_type),
            )

        conn.commit()
        conn.close()

    def export_session(
        self, session_id: Optional[str] = None, format: str = "json"
    ) -> str:
        """Export a session's chat history."""
        if not session_id:
            session_id = self.current_session_id

        messages = self.get_recent_messages(1000)  # Get all messages
        summary = self.get_conversation_summary(session_id)

        export_data = {
            "session_summary": summary,
            "messages": messages,
            "export_timestamp": datetime.now().isoformat(),
        }

        if format == "json":
            return json.dumps(export_data, indent=2)
        elif format == "text":
            lines = [
                f"Chat Session: {session_id}",
                f"Started: {summary.get('start_time', 'Unknown')}",
                "=" * 50,
                "",
            ]
            for msg in messages:
                timestamp = msg["timestamp"]
                sender = msg["sender"]
                content = msg["content"]
                lines.append(f"[{timestamp}] {sender}: {content}")
            return "\n".join(lines)

        return json.dumps(export_data, indent=2)
