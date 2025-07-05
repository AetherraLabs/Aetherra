#!/usr/bin/env python3
"""
🤖 PROACTIVE ASSISTANT - PHASE 2
=================================

Main proactive assistant that coordinates context analysis,
suggestion generation, and user interaction for anticipatory AI.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .context_analyzer import ContextAnalyzer, ContextInfo
from .suggestion_generator import SuggestionGenerator


class ProactiveAssistant:
    """Main proactive assistant coordinator"""
    
    def __init__(
        self,
        anticipation_engine=None,
        update_interval: int = 30,
        max_active_suggestions: int = 5
    ):
        self.anticipation_engine = anticipation_engine
        self.context_analyzer = ContextAnalyzer()
        self.suggestion_generator = SuggestionGenerator()
        
        # Configuration
        self.update_interval = update_interval  # seconds
        self.max_active_suggestions = max_active_suggestions
        
        # State tracking
        self.current_context: Optional[ContextInfo] = None
        self.active_suggestions: List[Dict[str, Any]] = []
        self.user_session_data: Dict[str, Any] = {}
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            "suggestions_generated": 0,
            "suggestions_accepted": 0,
            "suggestions_dismissed": 0,
            "context_updates": 0,
            "user_interactions": 0
        }
        
    async def start_proactive_monitoring(self) -> None:
        """Start proactive monitoring and suggestion generation"""
        
        if self.is_running:
            logging.warning("Proactive monitoring is already running")
            return
            
        self.is_running = True
        logging.info("Starting proactive monitoring...")
        
        try:
            while self.is_running:
                await self._update_cycle()
                await asyncio.sleep(self.update_interval)
                
        except Exception as e:
            logging.error(f"Error in proactive monitoring: {e}")
            self.is_running = False
            
    def stop_proactive_monitoring(self) -> None:
        """Stop proactive monitoring"""
        
        self.is_running = False
        logging.info("Stopped proactive monitoring")
        
    async def _update_cycle(self) -> None:
        """Main update cycle for proactive assistance"""
        
        try:
            # Get recent activity data
            activity_history = await self._get_recent_activities()
            
            if not activity_history:
                return
                
            # Analyze current context
            context_dict = self._convert_activities_to_context(activity_history)
            self.current_context = self.context_analyzer.analyze_context(
                activity_history, datetime.now()
            )
            
            # Update context in anticipation engine
            if self.anticipation_engine:
                await self.anticipation_engine.track_activity(
                    activity_type=self.current_context.primary_activity,
                    context={
                        "focus_level": self.current_context.focus_level,
                        "productivity_score": self.current_context.productivity_score,
                        "time_in_state": self.current_context.time_in_state
                    },
                    intensity=self.current_context.focus_level
                )
                
            # Generate new suggestions
            new_suggestions = self.suggestion_generator.generate_suggestions(
                context=context_dict,
                activity_history=activity_history,
                max_suggestions=3
            )
            
            # Update active suggestions
            await self._update_active_suggestions(new_suggestions)
            
            # Update metrics
            self.metrics["context_updates"] += 1
            
        except Exception as e:
            logging.error(f"Error in update cycle: {e}")
            
    async def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent user activities from anticipation engine"""
        
        if not self.anticipation_engine:
            # Return mock data for testing
            return self._get_mock_activities()
            
        # Get activities from anticipation engine
        try:
            # This would interface with the anticipation engine's activity history
            return self.anticipation_engine.activity_history[-10:]  # Last 10 activities
        except Exception as e:
            logging.error(f"Error getting activities: {e}")
            return []
            
    def _get_mock_activities(self) -> List[Dict[str, Any]]:
        """Generate mock activities for testing"""
        
        now = datetime.now()
        mock_activities = []
        
        for i in range(5):
            activity_time = now - timedelta(minutes=i * 15)
            mock_activities.append({
                "activity_type": "coding" if i % 2 == 0 else "research",
                "timestamp": activity_time.isoformat(),
                "duration": 900,  # 15 minutes
                "intensity": 0.7 if i % 2 == 0 else 0.5,
                "context": {
                    "project": "ai_assistant",
                    "language": "python" if i % 2 == 0 else None
                }
            })
            
        return list(reversed(mock_activities))  # Chronological order
        
    def _convert_activities_to_context(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert activity list to context dictionary for suggestion generator"""
        
        if not activities:
            return {}
            
        latest_activity = activities[-1]
        
        # Calculate metrics from activities
        total_duration = sum(a.get("duration", 0) for a in activities)
        avg_intensity = sum(a.get("intensity", 0.5) for a in activities) / len(activities)
        
        # Determine focus level (consistency of activity types)
        activity_types = [a.get("activity_type", "") for a in activities]
        unique_types = len(set(activity_types))
        focus_level = 1.0 - (unique_types / len(activities)) if activities else 0.0
        
        # Determine productivity score (based on activity types and intensity)
        productive_activities = {"coding", "writing", "designing", "research", "planning"}
        productive_count = sum(
            1 for a in activities 
            if a.get("activity_type", "").lower() in productive_activities
        )
        productivity_score = (productive_count / len(activities)) * avg_intensity
        
        # Time in current state
        time_in_state = total_duration / len(activities) if activities else 0
        
        return {
            "primary_activity": latest_activity.get("activity_type", "unknown"),
            "focus_level": focus_level,
            "productivity_score": productivity_score,
            "time_in_state": time_in_state,
            "activity_count": len(activities),
            "avg_intensity": avg_intensity
        }
        
    async def _update_active_suggestions(self, new_suggestions: List[Dict[str, Any]]) -> None:
        """Update the list of active suggestions"""
        
        # Remove expired or old suggestions
        current_time = datetime.now()
        self.active_suggestions = [
            s for s in self.active_suggestions
            if self._is_suggestion_still_relevant(s, current_time)
        ]
        
        # Add new suggestions
        for suggestion in new_suggestions:
            if not self._is_duplicate_suggestion(suggestion):
                self.active_suggestions.append(suggestion)
                self.suggestion_generator.record_suggestion_shown(suggestion)
                self.metrics["suggestions_generated"] += 1
                
        # Limit active suggestions
        if len(self.active_suggestions) > self.max_active_suggestions:
            # Keep highest confidence suggestions
            self.active_suggestions.sort(
                key=lambda x: x.get("final_score", x.get("confidence", 0)), 
                reverse=True
            )
            self.active_suggestions = self.active_suggestions[:self.max_active_suggestions]
            
    def _is_suggestion_still_relevant(self, suggestion: Dict[str, Any], current_time: datetime) -> bool:
        """Check if a suggestion is still relevant"""
        
        # Check age (suggestions expire after 30 minutes)
        created_at_str = suggestion.get("created_at", "")
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                age = (current_time - created_at).total_seconds()
                if age > 1800:  # 30 minutes
                    return False
            except (ValueError, AttributeError):
                pass
                
        # Check if suggestion type is still applicable
        suggestion_category = suggestion.get("category", "")
        if self.current_context:
            if (suggestion_category == "wellbeing" and 
                self.current_context.focus_level < 0.5):
                return False  # Don't suggest breaks when not focused
                
        return True
        
    def _is_duplicate_suggestion(self, new_suggestion: Dict[str, Any]) -> bool:
        """Check if suggestion is a duplicate of existing ones"""
        
        new_category = new_suggestion.get("category", "")
        new_title = new_suggestion.get("title", "")
        
        for existing in self.active_suggestions:
            if (existing.get("category") == new_category and 
                existing.get("title") == new_title):
                return True
                
        return False
        
    async def get_current_suggestions(self) -> List[Dict[str, Any]]:
        """Get current active suggestions for the user"""
        
        # Update suggestions before returning
        if self.is_running:
            await self._update_cycle()
            
        return self.active_suggestions.copy()
        
    async def handle_user_response(
        self, 
        suggestion_id: str, 
        response: str,
        feedback_score: Optional[float] = None
    ) -> None:
        """Handle user response to a suggestion"""
        
        # Find the suggestion
        suggestion = None
        for s in self.active_suggestions:
            if s.get("id") == suggestion_id:
                suggestion = s
                break
                
        if not suggestion:
            logging.warning(f"Suggestion {suggestion_id} not found")
            return
            
        # Update metrics
        if response.lower() in ["accepted", "yes", "ok"]:
            self.metrics["suggestions_accepted"] += 1
            was_helpful = True
        else:
            self.metrics["suggestions_dismissed"] += 1
            was_helpful = False
            
        self.metrics["user_interactions"] += 1
        
        # Update suggestion generator preferences
        category = suggestion.get("category", "")
        if feedback_score is not None:
            self.suggestion_generator.update_user_preferences(category, feedback_score)
        elif was_helpful:
            self.suggestion_generator.update_user_preferences(category, 0.1)
        else:
            self.suggestion_generator.update_user_preferences(category, -0.1)
            
        # Forward to anticipation engine if available
        if self.anticipation_engine:
            await self.anticipation_engine.respond_to_suggestion(
                suggestion_id, response, was_helpful
            )
            
        # Remove suggestion from active list
        self.active_suggestions = [
            s for s in self.active_suggestions if s.get("id") != suggestion_id
        ]
        
    def get_current_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        
        if not self.current_context:
            return {"status": "no_context"}
            
        return {
            "primary_activity": self.current_context.primary_activity,
            "focus_level": round(self.current_context.focus_level, 2),
            "productivity_score": round(self.current_context.productivity_score, 2),
            "time_in_state": self.current_context.time_in_state,
            "suggested_actions": self.current_context.suggested_actions,
            "active_suggestions_count": len(self.active_suggestions),
            "monitoring_active": self.is_running
        }
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the proactive assistant"""
        
        total_suggestions = self.metrics["suggestions_generated"]
        acceptance_rate = 0.0
        if total_suggestions > 0:
            acceptance_rate = self.metrics["suggestions_accepted"] / total_suggestions
            
        return {
            "suggestions_generated": total_suggestions,
            "suggestions_accepted": self.metrics["suggestions_accepted"],
            "suggestions_dismissed": self.metrics["suggestions_dismissed"],
            "acceptance_rate": round(acceptance_rate, 2),
            "context_updates": self.metrics["context_updates"],
            "user_interactions": self.metrics["user_interactions"],
            "is_monitoring": self.is_running,
            "active_suggestions": len(self.active_suggestions)
        }
        
    async def simulate_user_session(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Simulate a user session for testing purposes"""
        
        logging.info(f"Starting simulated user session ({duration_minutes} minutes)")
        
        # Start monitoring
        monitoring_task = asyncio.create_task(self.start_proactive_monitoring())
        
        # Simulate user activities
        session_results = {
            "duration_minutes": duration_minutes,
            "activities_simulated": 0,
            "suggestions_generated": 0,
            "context_changes": 0
        }
        
        try:
            for minute in range(duration_minutes):
                # Simulate different activity patterns
                if minute % 15 == 0:  # Every 15 minutes, change activity
                    activity_type = ["coding", "research", "writing", "break"][minute // 15 % 4]
                    
                    if self.anticipation_engine:
                        await self.anticipation_engine.track_activity(
                            activity_type=activity_type,
                            context={"session_minute": minute},
                            duration=900,  # 15 minutes
                            intensity=0.8 if activity_type != "break" else 0.2
                        )
                        
                    session_results["activities_simulated"] += 1
                    
                # Get suggestions periodically
                if minute % 5 == 0:  # Every 5 minutes
                    suggestions = await self.get_current_suggestions()
                    session_results["suggestions_generated"] += len(suggestions)
                    
                    # Simulate user responses (70% acceptance rate)
                    for suggestion in suggestions[:1]:  # Respond to first suggestion
                        import random
                        response = "accepted" if random.random() < 0.7 else "dismissed"
                        await self.handle_user_response(
                            suggestion["id"], response, 
                            0.8 if response == "accepted" else 0.2
                        )
                        
                await asyncio.sleep(0.1)  # Small delay for simulation
                
        except Exception as e:
            logging.error(f"Error in simulation: {e}")
        finally:
            # Stop monitoring
            self.stop_proactive_monitoring()
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
                
        # Get final metrics
        final_metrics = self.get_performance_metrics()
        session_results.update(final_metrics)
        
        logging.info("Simulated session completed")
        return session_results


# Test and demonstration functions
async def test_proactive_assistant():
    """Test the proactive assistant functionality"""
    
    print("🤖 Testing Lyrixa Proactive Assistant...")
    
    # Initialize assistant
    assistant = ProactiveAssistant()
    
    # Test context analysis
    print("\n1. Testing context analysis...")
    mock_activities = assistant._get_mock_activities()
    context_dict = assistant._convert_activities_to_context(mock_activities)
    
    print(f"   📊 Primary activity: {context_dict.get('primary_activity', 'unknown')}")
    print(f"   📊 Focus level: {context_dict.get('focus_level', 0):.2f}")
    print(f"   📊 Productivity score: {context_dict.get('productivity_score', 0):.2f}")
    
    # Test suggestion generation
    print("\n2. Testing suggestion generation...")
    suggestions = assistant.suggestion_generator.generate_suggestions(
        context=context_dict,
        activity_history=mock_activities,
        max_suggestions=3
    )
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   💡 Suggestion {i}: {suggestion['title']}")
        print(f"      Category: {suggestion['category']}")
        print(f"      Confidence: {suggestion.get('confidence', 0):.2f}")
        
    # Test user response handling
    print("\n3. Testing user response handling...")
    if suggestions:
        await assistant.handle_user_response(
            suggestions[0]["id"], "accepted", feedback_score=0.8
        )
        print("   ✅ User response recorded")
        
    # Test performance metrics
    print("\n4. Performance metrics...")
    metrics = assistant.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   📊 {key}: {value}")
        
    # Test short simulation
    print("\n5. Running short simulation (5 minutes)...")
    simulation_results = await assistant.simulate_user_session(duration_minutes=5)
    
    print("   📈 Simulation results:")
    for key, value in simulation_results.items():
        if isinstance(value, (int, float)):
            print(f"      {key}: {value}")
            
    print("\n✅ Proactive Assistant test complete!")
    return assistant


if __name__ == "__main__":
    asyncio.run(test_proactive_assistant())
