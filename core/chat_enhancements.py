#!/usr/bin/env python3
"""
💫 NeuroCode Chat Enhancement System
==================================

Advanced chat features including streaming responses, rich formatting,
chat memory, and interactive conversation elements.

Features:
- Real-time streaming responses with typing indicators
- Comprehensive chat memory and session management
- Rich markdown support with syntax highlighting
- Interactive chat elements (buttons, forms, media)
- Export and search capabilities
- Conversation continuity and context preservation

Author: NeuroCode Development Team
Date: June 30, 2025
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    import markdown

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    markdown = None

try:
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import get_lexer_by_name

    RICH_FORMATTING_AVAILABLE = True
except ImportError:
    RICH_FORMATTING_AVAILABLE = False

try:
    from core.memory.logger import MemoryLogger

    MEMORY_LOGGER_AVAILABLE = True
except (ImportError, PermissionError):
    MEMORY_LOGGER_AVAILABLE = False


class ChatMessageType(Enum):
    """Types of chat messages"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    NOTIFICATION = "notification"
    ERROR = "error"
    STREAMING = "streaming"


class ResponseStatus(Enum):
    """Response generation status"""

    STARTING = "starting"
    STREAMING = "streaming"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class ChatMessage:
    """Represents a single chat message"""

    content: str
    message_type: ChatMessageType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    formatting: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for storage"""
        return {
            "content": self.content,
            "type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "attachments": self.attachments,
            "formatting": self.formatting,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create message from dictionary"""
        return cls(
            content=data["content"],
            message_type=ChatMessageType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            attachments=data.get("attachments", []),
            formatting=data.get("formatting", {}),
        )


@dataclass
class ChatSession:
    """Represents a chat conversation session"""

    session_id: str
    title: str
    messages: List[ChatMessage] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: ChatMessage):
        """Add a message to the session"""
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_context_window(self, max_messages: int = 20) -> List[ChatMessage]:
        """Get recent messages for context"""
        return self.messages[-max_messages:] if self.messages else []

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Create session from dictionary"""
        session = cls(
            session_id=data["session_id"],
            title=data["title"],
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            metadata=data.get("metadata", {}),
        )
        session.messages = [ChatMessage.from_dict(msg) for msg in data.get("messages", [])]
        return session


class StreamingResponseHandler:
    """Handles real-time streaming responses"""

    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
        self.status = ResponseStatus.STARTING
        self.accumulated_response = ""
        self.start_time = time.time()
        self.cancelled = False

    def update(self, chunk: str):
        """Update with new response chunk"""
        if self.cancelled:
            return

        self.accumulated_response += chunk
        self.status = ResponseStatus.STREAMING

        if self.callback:
            self.callback(chunk)

    def complete(self):
        """Mark response as complete"""
        self.status = ResponseStatus.COMPLETE
        if self.callback:
            self.callback("")  # Signal completion

    def cancel(self):
        """Cancel the streaming response"""
        self.cancelled = True
        self.status = ResponseStatus.CANCELLED

    def get_response_time(self) -> float:
        """Get total response time"""
        return time.time() - self.start_time


class RichFormatter:
    """Handles rich formatting for chat messages"""

    def __init__(self):
        self.markdown_available = RICH_FORMATTING_AVAILABLE

    def format_message(self, content: str, message_type: ChatMessageType) -> str:
        """Apply rich formatting to message content"""
        if not self.markdown_available:
            return content

        try:
            # Apply markdown formatting
            if message_type in [ChatMessageType.ASSISTANT, ChatMessageType.USER]:
                return self._apply_markdown(content)
            return content
        except Exception:
            return content  # Fallback to plain text

    def _apply_markdown(self, content: str) -> str:
        """Apply markdown formatting"""
        if not MARKDOWN_AVAILABLE:
            return content

        try:
            # Convert markdown to formatted text
            html = (
                markdown.markdown(content, extensions=["codehilite", "fenced_code"])
                if markdown
                else content
            )
            # Convert to terminal-friendly format
            return self._html_to_terminal(html)
        except Exception:
            return content

    def _html_to_terminal(self, html: str) -> str:
        """Convert HTML to terminal-friendly format"""
        # Simple HTML to terminal conversion
        # In a real implementation, this would be more sophisticated
        text = re.sub(r"<[^>]+>", "", html)  # Remove HTML tags
        return text

    def highlight_code(self, code: str, language: str = "python") -> str:
        """Apply syntax highlighting to code"""
        if not RICH_FORMATTING_AVAILABLE:
            return code

        try:
            lexer = get_lexer_by_name(language, stripall=True)
            formatter = TerminalFormatter()
            return highlight(code, lexer, formatter)
        except Exception:
            return code


class ChatMemoryManager:
    """Manages chat history and memory"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/chat_history.json")
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None

        # Try to connect to memory logger if available
        self.memory_logger = None
        if MEMORY_LOGGER_AVAILABLE:
            try:
                self.memory_logger = MemoryLogger()
            except Exception:
                pass  # Graceful fallback

        self._load_sessions()

    def create_session(self, title: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """Create a new chat session"""
        session_id = f"session_{int(time.time() * 1000)}"

        if not title:
            title = f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        session = ChatSession(session_id=session_id, title=title, tags=tags or [])

        self.sessions[session_id] = session
        self.current_session_id = session_id
        self._save_sessions()

        # Log to memory system if available
        if self.memory_logger:
            try:
                self.memory_logger.log_memory(
                    f"Chat session created: {title} [session:{session_id}]"
                )
            except Exception:
                pass  # Graceful fallback

        return session_id

    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current active session"""
        if self.current_session_id and self.current_session_id in self.sessions:
            return self.sessions[self.current_session_id]
        return None

    def add_message(
        self, content: str, message_type: ChatMessageType, metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to the current session"""
        if not self.current_session_id:
            self.create_session()

        session = self.get_current_session()
        if session:
            message = ChatMessage(
                content=content, message_type=message_type, metadata=metadata or {}
            )
            session.add_message(message)
            self._save_sessions()

            # Log important messages to memory system
            if self.memory_logger and message_type == ChatMessageType.ASSISTANT:
                try:
                    truncated_content = content[:200] + "..." if len(content) > 200 else content
                    self.memory_logger.log_memory(
                        f"Chat response: {truncated_content} [session:{self.current_session_id}]"
                    )
                except Exception:
                    pass  # Graceful fallback

    def search_messages(self, query: str, max_results: int = 20) -> List[ChatMessage]:
        """Search through chat history"""
        results = []
        query_lower = query.lower()

        for session in self.sessions.values():
            for message in session.messages:
                if query_lower in message.content.lower():
                    results.append(message)
                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break

        return results

    def get_session_list(self) -> List[Dict[str, Any]]:
        """Get list of all sessions with summary info"""
        session_list = []
        for session in sorted(self.sessions.values(), key=lambda s: s.last_activity, reverse=True):
            session_list.append(
                {
                    "session_id": session.session_id,
                    "title": session.title,
                    "message_count": len(session.messages),
                    "last_activity": session.last_activity.isoformat(),
                    "tags": session.tags,
                }
            )
        return session_list

    def export_session(self, session_id: str, format: str = "json") -> str:
        """Export a session in specified format"""
        session = self.sessions.get(session_id)
        if not session:
            return ""

        if format == "json":
            return json.dumps(session.to_dict(), indent=2)
        elif format == "markdown":
            return self._export_as_markdown(session)
        elif format == "txt":
            return self._export_as_text(session)
        else:
            return ""

    def _export_as_markdown(self, session: ChatSession) -> str:
        """Export session as markdown"""
        lines = [f"# {session.title}\n"]
        lines.append(f"**Created**: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Messages**: {len(session.messages)}")
        if session.tags:
            lines.append(f"**Tags**: {', '.join(session.tags)}")
        lines.append("\n---\n")

        for message in session.messages:
            speaker = (
                "🤖 **AI**" if message.message_type == ChatMessageType.ASSISTANT else "👤 **User**"
            )
            timestamp = message.timestamp.strftime("%H:%M:%S")
            lines.append(f"## {speaker} ({timestamp})\n")
            lines.append(f"{message.content}\n")

        return "\n".join(lines)

    def _export_as_text(self, session: ChatSession) -> str:
        """Export session as plain text"""
        lines = [f"Chat Session: {session.title}"]
        lines.append(f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 50)

        for message in session.messages:
            speaker = "AI" if message.message_type == ChatMessageType.ASSISTANT else "User"
            timestamp = message.timestamp.strftime("%H:%M:%S")
            lines.append(f"[{timestamp}] {speaker}: {message.content}")
            lines.append("")

        return "\n".join(lines)

    def _load_sessions(self):
        """Load sessions from storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for session_data in data.get("sessions", []):
                        session = ChatSession.from_dict(session_data)
                        self.sessions[session.session_id] = session
                    self.current_session_id = data.get("current_session_id")
        except Exception:
            pass  # Graceful fallback for file access issues

    def _save_sessions(self):
        """Save sessions to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "current_session_id": self.current_session_id,
                "sessions": [session.to_dict() for session in self.sessions.values()],
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Graceful fallback for file access issues


class ChatEnhancementSystem:
    """Main chat enhancement system coordinator"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.memory_manager = ChatMemoryManager(storage_path)
        self.formatter = RichFormatter()
        self.active_streams: Dict[str, StreamingResponseHandler] = {}

        # Initialize current session if none exists
        if not self.memory_manager.get_current_session():
            self.memory_manager.create_session("Welcome Chat")

    def start_streaming_response(
        self, message_id: str, callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """Start a streaming response"""
        handler = StreamingResponseHandler(callback)
        self.active_streams[message_id] = handler
        return message_id

    def update_streaming_response(self, message_id: str, chunk: str):
        """Update a streaming response with new content"""
        if message_id in self.active_streams:
            self.active_streams[message_id].update(chunk)

    def complete_streaming_response(self, message_id: str) -> str:
        """Complete a streaming response and return full content"""
        if message_id in self.active_streams:
            handler = self.active_streams[message_id]
            handler.complete()

            # Save the complete response to memory
            self.memory_manager.add_message(
                handler.accumulated_response,
                ChatMessageType.ASSISTANT,
                {"response_time": handler.get_response_time(), "streamed": True},
            )

            # Clean up
            del self.active_streams[message_id]
            return handler.accumulated_response
        return ""

    def cancel_streaming_response(self, message_id: str):
        """Cancel a streaming response"""
        if message_id in self.active_streams:
            self.active_streams[message_id].cancel()
            del self.active_streams[message_id]

    def send_message(
        self,
        content: str,
        message_type: ChatMessageType = ChatMessageType.USER,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Send a message and apply formatting"""
        formatted_content = self.formatter.format_message(content, message_type)

        self.memory_manager.add_message(formatted_content, message_type, metadata)

        # Return the message object
        session = self.memory_manager.get_current_session()
        if session and session.messages:
            return session.messages[-1]

        return ChatMessage(formatted_content, message_type, metadata=metadata or {})

    def get_conversation_context(self, max_messages: int = 20) -> List[ChatMessage]:
        """Get recent conversation context"""
        session = self.memory_manager.get_current_session()
        if session:
            return session.get_context_window(max_messages)
        return []

    def create_new_session(
        self, title: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> str:
        """Create a new chat session"""
        return self.memory_manager.create_session(title, tags)

    def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        if session_id in self.memory_manager.sessions:
            self.memory_manager.current_session_id = session_id
            return True
        return False

    def search_conversations(self, query: str, max_results: int = 20) -> List[ChatMessage]:
        """Search through conversation history"""
        return self.memory_manager.search_messages(query, max_results)

    def export_current_session(self, format: str = "json") -> str:
        """Export current session"""
        session = self.memory_manager.get_current_session()
        if session:
            return self.memory_manager.export_session(session.session_id, format)
        return ""

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        session = self.memory_manager.get_current_session()
        if session:
            return {
                "session_id": session.session_id,
                "title": session.title,
                "message_count": len(session.messages),
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "tags": session.tags,
                "active_streams": len(self.active_streams),
            }
        return {}

    def get_activity_stats(self) -> Dict[str, Any]:
        """Get chat activity statistics"""
        total_sessions = len(self.memory_manager.sessions)
        total_messages = sum(len(s.messages) for s in self.memory_manager.sessions.values())

        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_sessions = sum(
            1 for s in self.memory_manager.sessions.values() if s.last_activity > recent_cutoff
        )

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "recent_sessions_24h": recent_sessions,
            "current_session": self.get_session_summary(),
            "formatting_available": RICH_FORMATTING_AVAILABLE,
            "memory_integration": MEMORY_LOGGER_AVAILABLE,
        }


# Example usage and testing
if __name__ == "__main__":

    def example_streaming_callback(chunk: str):
        """Example callback for streaming responses"""
        if chunk:
            print(chunk, end="", flush=True)
        else:
            print("\n[Response Complete]")

    def demonstrate_chat_enhancements():
        """Demonstrate the chat enhancement system"""
        print("🎭 Chat Enhancement System Demo")
        print("=" * 50)

        # Initialize the system
        chat_system = ChatEnhancementSystem()

        # Send a user message
        print("\n📝 Sending user message...")
        user_msg = chat_system.send_message(
            "Hello, can you help me with Python?", ChatMessageType.USER
        )
        print(f"User: {user_msg.content}")

        # Simulate streaming response
        print("\n🤖 Streaming AI response...")
        response_id = "resp_001"
        chat_system.start_streaming_response(response_id, example_streaming_callback)

        # Simulate chunks of response
        response_chunks = [
            "Hello! I'd be happy to help you with Python. ",
            "What specific topic or problem would you like to work on? ",
            "I can assist with syntax, libraries, debugging, or best practices.",
        ]

        for chunk in response_chunks:
            time.sleep(0.5)  # Simulate streaming delay
            chat_system.update_streaming_response(response_id, chunk)

        # Complete the response
        chat_system.complete_streaming_response(response_id)

        # Show conversation context
        print("\n📚 Conversation Context:")
        context = chat_system.get_conversation_context()
        for i, msg in enumerate(context[-2:], 1):  # Show last 2 messages
            speaker = "User" if msg.message_type == ChatMessageType.USER else "AI"
            print(f"{i}. {speaker}: {msg.content[:50]}...")

        # Show session summary
        print("\n📊 Session Summary:")
        summary = chat_system.get_session_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # Show activity stats
        print("\n📈 Activity Statistics:")
        stats = chat_system.get_activity_stats()
        for key, value in stats.items():
            if key != "current_session":  # Skip nested dict
                print(f"  {key}: {value}")

        # Test export functionality
        print("\n💾 Export Test:")
        exported = chat_system.export_current_session("markdown")
        print(f"Exported {len(exported)} characters of conversation data")

        print("\n✅ Chat Enhancement System demonstration complete!")

    # Run the demonstration
    demonstrate_chat_enhancements()
