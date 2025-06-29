# core/goal_system.py
import json
import os
from datetime import datetime, timedelta
from core.ai_runtime import ask_ai

GOALS_FILE = "goals_store.json"

class GoalSystem:
    """Manages goals, intents, and autonomous agent behavior"""
    
    def __init__(self, memory, interpreter):
        self.memory = memory
        self.interpreter = interpreter
        self.goals = []
        self.agent_mode = False
        self.active_goals = []
        self.goal_history = []
        self.load_goals()
    
    def load_goals(self):
        """Load goals from persistent storage"""
        if os.path.exists(GOALS_FILE):
            with open(GOALS_FILE, "r") as f:
                data = json.load(f)
                self.goals = data.get("goals", [])
                self.agent_mode = data.get("agent_mode", False)
                self.active_goals = data.get("active_goals", [])
                self.goal_history = data.get("goal_history", [])
    
    def save_goals(self):
        """Save goals to persistent storage"""
        data = {
            "goals": self.goals,
            "agent_mode": self.agent_mode,
            "active_goals": self.active_goals,
            "goal_history": self.goal_history,
            "last_updated": str(datetime.now())
        }
        with open(GOALS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def set_goal(self, goal_text, priority="medium", metrics=None):
        """Set a new goal for the system"""
        goal = {
            "id": f"goal_{len(self.goals) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "text": goal_text,
            "priority": priority,
            "metrics": metrics or {},
            "status": "active",
            "created": str(datetime.now()),
            "last_checked": None,
            "progress": []
        }
        
        self.goals.append(goal)
        self.active_goals.append(goal["id"])
        self.save_goals()
        
        # Remember this goal setting
        self.memory.remember(
            f"Set goal: {goal_text}",
            tags=["goal", "intent", priority],
            category="system_goals"
        )
        
        return f"[Goal System] Set goal: {goal_text} (ID: {goal['id']})"
    
    def set_agent_mode(self, enabled):
        """Enable or disable autonomous agent mode"""
        self.agent_mode = enabled
        self.save_goals()
        
        mode_str = "enabled" if enabled else "disabled"
        self.memory.remember(
            f"Agent mode {mode_str}",
            tags=["agent_mode", "system_control"],
            category="system_settings"
        )
        
        if enabled:
            return "[Agent] Autonomous mode ENABLED - System will monitor and act on goals"
        else:
            return "[Agent] Autonomous mode DISABLED - Manual control restored"
    
    def check_goal_progress(self, goal_id):
        """Check progress on a specific goal"""
        goal = next((g for g in self.goals if g["id"] == goal_id), None)
        if not goal:
            return f"[Goal] Goal not found: {goal_id}"
        
        # Get relevant memories for context
        goal_memories = self.memory.recall(tags=["goal", goal["priority"]], limit=10)
        memory_context = "\n".join(goal_memories)
        
        # Use AI to assess progress
        prompt = f"""Assess progress on this goal:
Goal: {goal['text']}
Priority: {goal['priority']}
Metrics: {goal.get('metrics', {})}
Created: {goal['created']}

Recent relevant memories:
{memory_context}

Evaluate:
1. Current progress toward the goal
2. Obstacles or blockers
3. Suggested next actions
4. Estimated completion timeline

Provide a concise assessment."""
        
        assessment = ask_ai(prompt)
        
        # Update goal progress
        progress_entry = {
            "timestamp": str(datetime.now()),
            "assessment": assessment,
            "context": "ai_evaluation"
        }
        goal["progress"].append(progress_entry)
        goal["last_checked"] = str(datetime.now())
        self.save_goals()
        
        # Remember this assessment
        self.memory.remember(
            f"Goal progress check: {goal['text'][:50]}... - {assessment[:100]}...",
            tags=["goal_progress", "assessment", goal["priority"]],
            category="system_goals"
        )
        
        return f"[Goal Progress] {goal['text']}\n{assessment}"
    
    def autonomous_goal_monitoring(self):
        """Autonomous monitoring and action on active goals"""
        if not self.agent_mode or not self.active_goals:
            return "[Agent] Not in agent mode or no active goals"
        
        results = []
        
        for goal_id in self.active_goals:
            goal = next((g for g in self.goals if g["id"] == goal_id), None)
            if not goal:
                continue
            
            # Check if goal needs attention (hasn't been checked recently)
            if goal.get("last_checked"):
                last_check = datetime.fromisoformat(goal["last_checked"])
                if datetime.now() - last_check < timedelta(hours=1):
                    continue  # Skip recently checked goals
            
            # Perform autonomous assessment and action
            assessment = self.check_goal_progress(goal_id)
            
            # Determine if action is needed
            action_prompt = f"""Based on this goal assessment, should the system take action?

{assessment}

Consider:
1. Is the goal being met?
2. Are there clear action items?
3. Would autonomous action be beneficial?

Respond with:
- "ACTION_NEEDED: [specific action]" if action should be taken
- "MONITOR: [reason]" if only monitoring is needed
- "GOAL_MET: [confirmation]" if goal is achieved"""
            
            action_decision = ask_ai(action_prompt)
            
            if action_decision.startswith("ACTION_NEEDED:"):
                action = action_decision.replace("ACTION_NEEDED:", "").strip()
                # Execute the suggested action
                try:
                    result = self.interpreter.execute(action)
                    results.append(f"[Autonomous Action] Goal: {goal['text'][:30]}... Action: {action} Result: {result}")
                    
                    # Remember this autonomous action
                    self.memory.remember(
                        f"Autonomous action for goal '{goal['text']}': {action}",
                        tags=["autonomous_action", "goal_driven", goal["priority"]],
                        category="system_goals"
                    )
                    
                except Exception as e:
                    results.append(f"[Autonomous Action] Failed for goal {goal['text'][:30]}...: {str(e)}")
            
            elif action_decision.startswith("GOAL_MET:"):
                # Mark goal as completed
                goal["status"] = "completed"
                goal["completed"] = str(datetime.now())
                self.active_goals.remove(goal_id)
                self.goal_history.append(goal_id)
                self.save_goals()
                
                results.append(f"[Goal Completed] {goal['text']}")
                
                self.memory.remember(
                    f"Goal completed: {goal['text']}",
                    tags=["goal_completed", "success", goal["priority"]],
                    category="system_goals"
                )
        
        return "\n".join(results) if results else "[Agent] All goals monitored - no actions needed"
    
    def reflective_loop(self):
        """Periodic reflective analysis and goal adjustment"""
        if not self.agent_mode:
            return "[Reflective Loop] Agent mode disabled"
        
        # Summarize recent memory
        recent_memories = self.memory.get_memories_by_timeframe(24)  # Last 24 hours
        if not recent_memories:
            return "[Reflective Loop] No recent activity to analyze"
        
        memory_summary = "\n".join([m["text"] for m in recent_memories[-10:]])
        
        # Analyze if action is needed
        reflection_prompt = f"""Analyze recent system activity and determine if action is needed:

Recent Activity (last 24 hours):
{memory_summary}

Current Goals:
{[g['text'] for g in self.goals if g['id'] in self.active_goals]}

Consider:
1. Are there recurring issues or patterns?
2. Do current goals need adjustment?
3. Should new goals be created?
4. Is the system operating optimally?

Respond with one of:
- "CREATE_GOAL: [goal description]" if a new goal should be created
- "ADJUST_GOAL: [goal_id] [adjustment]" if existing goal needs modification
- "TAKE_ACTION: [specific action]" if immediate action is needed
- "CONTINUE_MONITORING" if system is operating well"""
        
        reflection_result = ask_ai(reflection_prompt)
        
        # Remember this reflection
        self.memory.remember(
            f"Reflective loop analysis: {reflection_result}",
            tags=["reflective_loop", "system_analysis", "autonomous"],
            category="system_goals"
        )
        
        # Act on reflection results
        if reflection_result.startswith("CREATE_GOAL:"):
            goal_text = reflection_result.replace("CREATE_GOAL:", "").strip()
            return self.set_goal(goal_text, "high")
        
        elif reflection_result.startswith("TAKE_ACTION:"):
            action = reflection_result.replace("TAKE_ACTION:", "").strip()
            try:
                result = self.interpreter.execute(action)
                return f"[Reflective Action] {action}\nResult: {result}"
            except Exception as e:
                return f"[Reflective Action] Failed: {str(e)}"
        
        return f"[Reflective Loop] {reflection_result}"
    
    def get_goal_status(self):
        """Get status of all goals"""
        if not self.goals:
            return "[Goals] No goals set"
        
        active = [g for g in self.goals if g["id"] in self.active_goals]
        completed = [g for g in self.goals if g["status"] == "completed"]
        
        result = f"[Goal Status] Agent Mode: {'ON' if self.agent_mode else 'OFF'}\n"
        result += f"Active Goals ({len(active)}):\n"
        
        for goal in active:
            result += f"  • {goal['text']} (Priority: {goal['priority']})\n"
        
        if completed:
            result += f"\nCompleted Goals ({len(completed)}):\n"
            for goal in completed[-3:]:  # Show last 3 completed
                result += f"  ✓ {goal['text']}\n"
        
        return result
