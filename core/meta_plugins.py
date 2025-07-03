# core/meta_plugins.py
import os
from datetime import datetime, timedelta
from core.ai_runtime import ask_ai

class MetaPluginSystem:
    """Meta-plugins that can manipulate files, memory, and other plugins"""

    def __init__(self, memory, interpreter, goal_system):
        self.memory = memory
        self.interpreter = interpreter
        self.goal_system = goal_system
        self.meta_plugins = {
            "memory_analyzer": self.memory_analyzer,
            "file_monitor": self.file_monitor,
            "system_optimizer": self.system_optimizer,
            "goal_tracker": self.goal_tracker,
            "autonomous_improver": self.autonomous_improver
        }

    def execute_meta_plugin(self, plugin_name, *args):
        """Execute a meta-plugin"""
        if plugin_name in self.meta_plugins:
            return self.meta_plugins[plugin_name](*args)
        else:
            return f"[Meta-Plugin] Unknown plugin: {plugin_name}"

    def list_meta_plugins(self):
        """List all available meta-plugins"""
        result = "[Meta-Plugins] Available plugins:\n"
        for name, func in self.meta_plugins.items():
            result += f"  • {name}: {func.__doc__ or 'No description'}\n"
        return result

    def memory_analyzer(self, *args):
        """Analyze memory for anomalies, patterns, and insights"""
        timeframe = int(args[0]) if args else 30

        # Get recent memories
        recent_memories = self.memory.get_memories_by_timeframe(timeframe * 24)  # Convert days to hours

        if not recent_memories:
            return f"[Memory Analyzer] No memories in the last {timeframe} days"

        # Detect anomalies
        anomalies = []

        # Check for sudden spikes in activity
        daily_counts = {}
        for mem in recent_memories:
            try:
                date = datetime.fromisoformat(mem["timestamp"]).date()
                daily_counts[date] = daily_counts.get(date, 0) + 1
            except:
                continue

        if daily_counts:
            avg_daily = sum(daily_counts.values()) / len(daily_counts)
            for date, count in daily_counts.items():
                if count > avg_daily * 2:  # More than 2x average
                    anomalies.append(f"High activity on {date}: {count} memories")

        # Check for error patterns
        error_memories = [m for m in recent_memories if "error" in m["text"].lower() or "failed" in m["text"].lower()]
        if len(error_memories) > len(recent_memories) * 0.1:  # More than 10% errors
            anomalies.append(f"High error rate: {len(error_memories)} errors out of {len(recent_memories)} memories")

        # Detect recurring patterns
        patterns = self.memory.detect_recurring_patterns(min_frequency=3, timeframe_days=timeframe)

        # Generate AI analysis
        memory_summary = "\n".join([m["text"] for m in recent_memories[-20:]])
        ai_analysis = ask_ai(f"""Analyze these recent memories for insights and recommendations:

{memory_summary}

Detected anomalies: {anomalies}
Recurring patterns: {list(patterns['phrases'].keys())[:5]}

Provide insights on:
1. System health and performance
2. User behavior patterns
3. Potential issues or concerns
4. Recommended actions

Be concise but thorough.""")

        result = f"[Memory Analyzer] Analysis for last {timeframe} days:\n"
        result += f"Total memories: {len(recent_memories)}\n"

        if anomalies:
            result += f"Anomalies detected:\n"
            for anomaly in anomalies:
                result += f"  • {anomaly}\n"

        result += f"Recurring patterns: {len(patterns['phrases'])}\n"
        result += f"\nAI Analysis:\n{ai_analysis}"

        # Remember this analysis
        self.memory.remember(
            f"Memory analysis completed: {len(recent_memories)} memories, {len(anomalies)} anomalies",
            tags=["memory_analysis", "meta_plugin", "system_health"],
            category="system_analysis"
        )

        return result

    def file_monitor(self, *args):
        """Monitor file system for changes and patterns"""
        target_dir = args[0] if args else "."

        if not os.path.exists(target_dir):
            return f"[File Monitor] Directory not found: {target_dir}"

        # Get file modification times
        file_info = []
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith(('.py', '.md', '.json', '.txt')):
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        file_info.append({
                            "path": filepath,
                            "modified": datetime.fromtimestamp(mtime),
                            "size": os.path.getsize(filepath)
                        })
                    except:
                        continue

        # Find recently modified files (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_files = [f for f in file_info if f["modified"] > recent_cutoff]

        # Analyze patterns
        analysis = ask_ai(f"""Analyze these file system patterns:

Recently modified files ({len(recent_files)}):
{chr(10).join([f['path'] + ' - ' + str(f['modified']) for f in recent_files[:10]])}

Total monitored files: {len(file_info)}

Identify:
1. Development activity patterns
2. Potential issues or concerns
3. Optimization opportunities
4. Recommended monitoring actions""")

        result = f"[File Monitor] Directory: {target_dir}\n"
        result += f"Total files: {len(file_info)}\n"
        result += f"Recently modified: {len(recent_files)}\n"

        if recent_files:
            result += "Recent changes:\n"
            for f in recent_files[:5]:
                result += f"  • {f['path']} ({f['modified'].strftime('%H:%M')})\n"

        result += f"\nAnalysis:\n{analysis}"

        return result

    def system_optimizer(self, *args):
        """Analyze system performance and suggest optimizations"""
        focus_area = args[0] if args else "general"

        # Gather system metrics from memory
        performance_memories = self.memory.recall(tags=["performance", "optimization", "system"])
        error_memories = self.memory.recall(tags=["error", "failed", "issue"])

        # Analyze current goals
        goal_status = self.goal_system.get_goal_status()

        # Get system statistics
        memory_stats = self.memory.get_memory_stats()

        # Generate optimization recommendations
        context = f"""System Context:
Performance memories: {len(performance_memories)}
Error memories: {len(error_memories)}
Goal status: {goal_status}
Memory stats: {memory_stats}
Focus area: {focus_area}

Recent performance indicators:
{chr(10).join([m["text"] for m in performance_memories[-5:]])}

Recent errors:
{chr(10).join([m["text"] for m in error_memories[-3:]])}"""

        optimization_advice = ask_ai(f"""Based on this system analysis, provide optimization recommendations:

{context}

Focus on {focus_area} optimization.

Suggest:
1. Immediate performance improvements
2. Long-term optimization strategies
3. Specific NeuroCode commands to run
4. System configuration changes
5. Monitoring recommendations

Be specific and actionable.""")

        # Remember this optimization analysis
        self.memory.remember(
            f"System optimization analysis for {focus_area}: {optimization_advice[:100]}...",
            tags=["optimization", "meta_plugin", "system_analysis", focus_area],
            category="system_optimization"
        )

        return f"[System Optimizer] Focus: {focus_area}\n{optimization_advice}"

    def goal_tracker(self, *args):
        """Advanced goal tracking and progress analysis"""
        action = args[0] if args else "status"

        if action == "analyze":
            # Deep analysis of goal progress
            goals = self.goal_system.goals
            if not goals:
                return "[Goal Tracker] No goals to analyze"

            analysis_prompt = f"""Analyze goal progress and effectiveness:

Goals: {[g['text'] for g in goals]}
Active goals: {len(self.goal_system.active_goals)}
Agent mode: {self.goal_system.agent_mode}

Recent goal-related memories:
{chr(10).join([m["text"] for m in self.memory.recall(tags=["goal"], limit=10)])}

Provide analysis on:
1. Goal achievement patterns
2. Effectiveness of current goals
3. Suggested goal adjustments
4. Optimization recommendations"""

            analysis = ask_ai(analysis_prompt)
            return f"[Goal Tracker] Analysis:\n{analysis}"

        elif action == "optimize":
            # Suggest goal optimizations
            return self.goal_system.reflective_loop()

        else:
            # Return status
            return self.goal_system.get_goal_status()

    def autonomous_improver(self, *args):
        """Autonomous system improvement based on accumulated knowledge"""
        target = args[0] if args else "general"

        # Analyze entire system state
        system_context = f"""
Memory: {len(self.memory.memory)} total memories
Goals: {len(self.goal_system.active_goals)} active goals
Agent mode: {self.goal_system.agent_mode}
Target improvement: {target}

Recent system activity:
{chr(10).join([m["text"] for m in self.memory.get_memories_by_timeframe(48)[-10:]])}

Detected patterns:
{list(self.memory.detect_recurring_patterns()['phrases'].keys())[:5]}"""

        improvement_plan = ask_ai(f"""Create an autonomous improvement plan:

{system_context}

Generate a plan to improve {target} including:
1. Specific NeuroCode commands to execute
2. Goals to set or modify
3. System configuration changes
4. Monitoring strategies

Provide actionable commands that can be executed autonomously.""")

        # If in agent mode, execute some improvements
        if self.goal_system.agent_mode:
            # Extract actionable commands from the plan
            lines = improvement_plan.split('\n')
            executed_actions = []

            for line in lines:
                if any(cmd in line.lower() for cmd in ['remember(', 'goal:', 'set ', 'analyze']):
                    try:
                        # Extract and execute the command
                        if 'remember(' in line:
                            start = line.find('remember(')
                            end = line.find(')', start) + 1
                            command = line[start:end]
                            result = self.interpreter.execute(command)
                            executed_actions.append(f"Executed: {command}")
                    except:
                        continue

            if executed_actions:
                improvement_plan += f"\n\nAutonomous actions taken:\n" + "\n".join(executed_actions)

        self.memory.remember(
            f"Autonomous improvement plan for {target}: {improvement_plan[:100]}...",
            tags=["autonomous_improvement", "meta_plugin", target],
            category="system_optimization"
        )

        return f"[Autonomous Improver] Target: {target}\n{improvement_plan}"
