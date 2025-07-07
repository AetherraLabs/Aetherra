"""
Response Style Memory Manager for Lyrixa
========================================

Learns from user feedback to adapt response styles and remember preferences.
Implements feedback-driven response optimization and style memory.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import statistics


class ResponseStyleMemoryManager:
    """Manages response style learning and adaptation based on user feedback."""
    
    def __init__(self, db_path: str = "lyrixa_response_memory.db"):
        """Initialize the response style memory manager."""
        self.db_path = Path(db_path)
        self.style_preferences = {}
        self.feedback_patterns = {}
        self.adaptation_rules = {}
        self._init_database()
        self._load_adaptation_rules()
        
    def _init_database(self):
        """Initialize the response style memory database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id TEXT NOT NULL,
                context_type TEXT NOT NULL,
                response_style TEXT NOT NULL,
                user_rating INTEGER NOT NULL,
                feedback_type TEXT,
                feedback_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                personality_mode TEXT,
                response_length INTEGER,
                technical_level INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS style_adaptations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                style_aspect TEXT NOT NULL,
                context_type TEXT NOT NULL,
                adaptation_value REAL NOT NULL,
                confidence_score REAL DEFAULT 0.5,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                sample_count INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                context TEXT,
                strength REAL DEFAULT 1.0,
                last_reinforced DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
    def _load_adaptation_rules(self):
        """Load adaptation rules for response style learning."""
        self.adaptation_rules = {
            "formality": {
                "too_formal": -0.2,
                "too_casual": 0.2,
                "perfect_tone": 0.0,
                "slightly_formal": -0.1,
                "slightly_casual": 0.1
            },
            "technical_depth": {
                "too_technical": -0.3,
                "not_technical_enough": 0.3,
                "perfect_level": 0.0,
                "slightly_technical": -0.1,
                "needs_more_detail": 0.2
            },
            "verbosity": {
                "too_long": -0.2,
                "too_short": 0.2,
                "perfect_length": 0.0,
                "slightly_verbose": -0.1,
                "needs_more_explanation": 0.1
            },
            "empathy": {
                "too_cold": 0.3,
                "too_emotional": -0.2,
                "perfect_empathy": 0.0,
                "more_understanding": 0.2,
                "less_personal": -0.1
            }
        }
    
    def record_feedback(self, response_id: str, context_type: str, response_style: Dict[str, Any],
                       user_rating: int, feedback_type: str = "", feedback_details: str = "",
                       personality_mode: str = "balanced") -> bool:
        """Record user feedback for a response."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO response_feedback 
                (response_id, context_type, response_style, user_rating, feedback_type, 
                 feedback_details, personality_mode, response_length, technical_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                response_id,
                context_type,
                json.dumps(response_style),
                user_rating,
                feedback_type,
                feedback_details,
                personality_mode,
                response_style.get("length", 0),
                response_style.get("technical_level", 5)
            ))
            
            conn.commit()
            conn.close()
            
            # Process feedback for style adaptation
            self._process_feedback_for_adaptation(context_type, feedback_type, user_rating)
            return True
            
        except Exception as e:
            print(f"Error recording feedback: {e}")
            return False
    
    def _process_feedback_for_adaptation(self, context_type: str, feedback_type: str, rating: int):
        """Process feedback to update style adaptations."""
        if feedback_type not in self.adaptation_rules:
            return
        
        # Get adaptation value from rules
        adaptation_value = self.adaptation_rules.get(feedback_type, {}).get("default", 0.0)
        
        # Adjust based on rating (1-5 scale)
        if rating <= 2:  # Poor rating - strong adaptation
            adaptation_value *= 1.5
        elif rating >= 4:  # Good rating - moderate adaptation
            adaptation_value *= 0.5
        
        # Update database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if adaptation exists
            cursor.execute("""
                SELECT id, adaptation_value, sample_count FROM style_adaptations
                WHERE style_aspect = ? AND context_type = ?
            """, (feedback_type, context_type))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing adaptation
                current_value = result[1]
                sample_count = result[2]
                new_value = (current_value * sample_count + adaptation_value) / (sample_count + 1)
                
                cursor.execute("""
                    UPDATE style_adaptations 
                    SET adaptation_value = ?, sample_count = ?, last_updated = ?
                    WHERE id = ?
                """, (new_value, sample_count + 1, datetime.now(), result[0]))
            else:
                # Create new adaptation
                cursor.execute("""
                    INSERT INTO style_adaptations 
                    (style_aspect, context_type, adaptation_value)
                    VALUES (?, ?, ?)
                """, (feedback_type, context_type, adaptation_value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error processing adaptation: {e}")
    
    def get_style_recommendations(self, context_type: str) -> Dict[str, float]:
        """Get style recommendations based on learned preferences."""
        recommendations = {
            "formality": 0.5,
            "technical_depth": 0.5,
            "verbosity": 0.5,
            "empathy": 0.5,
            "enthusiasm": 0.5,
            "humor": 0.5,
            "creativity": 0.5
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT style_aspect, adaptation_value, confidence_score
                FROM style_adaptations
                WHERE context_type = ? OR context_type = 'general'
                ORDER BY last_updated DESC
            """, (context_type,))
            
            adaptations = cursor.fetchall()
            conn.close()
            
            # Apply adaptations to recommendations
            for aspect, value, confidence in adaptations:
                if aspect in recommendations:
                    # Apply weighted adaptation based on confidence
                    current = recommendations[aspect]
                    adapted = max(0.0, min(1.0, current + value * confidence))
                    recommendations[aspect] = adapted
            
        except Exception as e:
            print(f"Error getting style recommendations: {e}")
        
        return recommendations
    
    def learn_from_conversation(self, conversation_data: List[Dict[str, Any]]):
        """Learn patterns from an entire conversation."""
        if len(conversation_data) < 2:
            return
        
        # Analyze conversation flow and user satisfaction
        user_messages = [msg for msg in conversation_data if msg.get("sender") == "user"]
        
        # Extract patterns
        patterns = {
            "average_user_message_length": statistics.mean([len(msg.get("content", "")) for msg in user_messages]),
            "conversation_duration": len(conversation_data),
            "user_engagement": self._calculate_engagement(user_messages),
            "response_timing": self._analyze_response_timing(conversation_data)
        }
        
        # Store conversation patterns
        self._store_conversation_patterns(patterns)
    
    def _calculate_engagement(self, user_messages: List[Dict[str, Any]]) -> float:
        """Calculate user engagement score from messages."""
        if not user_messages:
            return 0.0
        
        engagement_indicators = {
            "questions": 0,
            "follow_ups": 0,
            "positive_words": 0,
            "total_length": 0
        }
        
        positive_words = {"thanks", "great", "perfect", "excellent", "good", "helpful", "awesome"}
        
        for msg in user_messages:
            content = msg.get("content", "").lower()
            engagement_indicators["total_length"] += len(content)
            
            if "?" in content:
                engagement_indicators["questions"] += 1
            if any(word in content for word in ["also", "additionally", "furthermore"]):
                engagement_indicators["follow_ups"] += 1
            if any(word in content for word in positive_words):
                engagement_indicators["positive_words"] += 1
        
        # Calculate engagement score (0-1)
        score = 0.0
        score += min(1.0, engagement_indicators["questions"] / len(user_messages))
        score += min(1.0, engagement_indicators["follow_ups"] / len(user_messages))
        score += min(1.0, engagement_indicators["positive_words"] / len(user_messages))
        score += min(1.0, engagement_indicators["total_length"] / (len(user_messages) * 50))
        
        return score / 4.0
    
    def _analyze_response_timing(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze response timing patterns."""
        if len(conversation_data) < 2:
            return {}
        
        response_gaps = []
        user_response_times = []
        
        for i in range(1, len(conversation_data)):
            prev_msg = conversation_data[i-1]
            curr_msg = conversation_data[i]
            
            try:
                prev_time = datetime.fromisoformat(prev_msg.get("timestamp", ""))
                curr_time = datetime.fromisoformat(curr_msg.get("timestamp", ""))
                gap = (curr_time - prev_time).total_seconds()
                
                if curr_msg.get("sender") == "user":
                    user_response_times.append(gap)
                else:
                    response_gaps.append(gap)
                    
            except Exception:
                continue
        
        return {
            "average_response_gap": statistics.mean(response_gaps) if response_gaps else 0,
            "average_user_response": statistics.mean(user_response_times) if user_response_times else 0,
            "quick_responses": len([t for t in user_response_times if t < 10]),
            "delayed_responses": len([t for t in user_response_times if t > 60])
        }
    
    def _store_conversation_patterns(self, patterns: Dict[str, Any]):
        """Store conversation patterns for future learning."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_preferences 
                (preference_type, preference_value, context, strength)
                VALUES (?, ?, ?, ?)
            """, (
                "conversation_pattern",
                json.dumps(patterns),
                "general",
                1.0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing conversation patterns: {e}")
    
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get a summary of recent feedback and adaptations."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get feedback summary
            cursor.execute("""
                SELECT AVG(user_rating), COUNT(*), feedback_type
                FROM response_feedback
                WHERE timestamp > ?
                GROUP BY feedback_type
            """, (cutoff_date,))
            
            feedback_data = cursor.fetchall()
            
            # Get adaptation summary
            cursor.execute("""
                SELECT style_aspect, AVG(adaptation_value), COUNT(*)
                FROM style_adaptations
                WHERE last_updated > ?
                GROUP BY style_aspect
            """, (cutoff_date,))
            
            adaptation_data = cursor.fetchall()
            conn.close()
            
            return {
                "feedback_summary": [
                    {"type": fb[2], "avg_rating": fb[0], "count": fb[1]}
                    for fb in feedback_data
                ],
                "adaptation_summary": [
                    {"aspect": ad[0], "avg_adaptation": ad[1], "count": ad[2]}
                    for ad in adaptation_data
                ],
                "total_feedback_entries": sum([fb[1] for fb in feedback_data]),
                "active_adaptations": len(adaptation_data)
            }
            
        except Exception as e:
            print(f"Error getting feedback summary: {e}")
            return {}
    
    def export_learned_preferences(self) -> Dict[str, Any]:
        """Export learned preferences for backup or sharing."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM style_adaptations")
            adaptations = cursor.fetchall()
            
            cursor.execute("SELECT * FROM user_preferences")
            preferences = cursor.fetchall()
            
            conn.close()
            
            return {
                "adaptations": adaptations,
                "preferences": preferences,
                "exported_at": str(datetime.now()),
                "version": "1.0"
            }
            
        except Exception as e:
            print(f"Error exporting preferences: {e}")
            return {}
    
    def reset_learning_data(self, confirm: bool = False):
        """Reset all learned preferences and adaptations."""
        if not confirm:
            print("Warning: This will delete all learned preferences. Call with confirm=True to proceed.")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM response_feedback")
            cursor.execute("DELETE FROM style_adaptations")
            cursor.execute("DELETE FROM user_preferences")
            
            conn.commit()
            conn.close()
            
            print("All learning data has been reset.")
            return True
            
        except Exception as e:
            print(f"Error resetting learning data: {e}")
            return False
