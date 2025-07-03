# core/agent.py
                            suggest_system_evolution, provide_adaptive_suggestions,
                            memory_driven_code_suggestion, justify_self_editing_decision)

class NeuroAgent:
    """Manages autonomous behavior, pattern detection, and long-term goals"""

    def __init__(self, memory, functions, command_history):
        self.memory = memory
        self.functions = functions
        self.command_history = command_history

    def detect_memory_patterns(self):
        """Detect patterns in stored memories and suggest behaviors"""
        if not self.memory.memory:
            return "[Pattern Detection] No memories to analyze"

        # Get all memories with metadata
        memories = self.memory.memory

        # Analyze tag patterns
        tag_frequency = {}
        category_frequency = {}

        for mem in memories:
            # Count tag frequencies
            for tag in mem.get('tags', []):
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

            # Count category frequencies
            category = mem.get('category', 'general')
            category_frequency[category] = category_frequency.get(category, 0) + 1

        # Generate pattern analysis
        patterns = []

        # Most frequent tags
        if tag_frequency:
            top_tags = sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.append(f"Most frequent tags: {', '.join([f'{tag}({count})' for tag, count in top_tags])}")

        # Dominant categories
        if category_frequency:
            top_categories = sorted(category_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns.append(f"Dominant categories: {', '.join([f'{cat}({count})' for cat, count in top_categories])}")

        # AI pattern analysis
        ai_analysis = analyze_memory_patterns(memories, tag_frequency, category_frequency)

        result = "[Pattern Detection] Analysis Results:\n"
        for pattern in patterns:
            result += f"  📊 {pattern}\n"
        result += f"\n[AI Pattern Analysis]\n{ai_analysis}"

        return result

    def analyze_behavior(self):
        """Analyze user behavior patterns and suggest optimizations"""
        # Analyze command usage patterns
        command_types = {}
        for cmd in self.command_history:
            cmd_type = cmd['command_type']
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1

        # Get recent command patterns
        recent_commands = [cmd['command'] for cmd in self.command_history[-10:]]

        # Get all memories
        all_memories = self.memory.recall()

        # AI behavior analysis
        behavior_analysis = analyze_user_behavior(
            command_types, recent_commands, self.functions.functions,
            all_memories, len(self.command_history)
        )

        result = "[Behavior Analysis]\n"
        result += f"📈 Total memories: {len(all_memories)}\n"
        result += f"🔧 Defined functions: {self.functions.get_function_count()}\n"
        result += f"📊 Command patterns: {dict(sorted(command_types.items(), key=lambda x: x[1], reverse=True))}\n"
        result += f"\n[AI Behavior Analysis]\n{behavior_analysis}"

        return result

    def suggest_evolution(self, context=""):
        """Suggest system evolution based on usage patterns"""
        memory_summary = self.memory.get_memory_summary()
        memory_summary['recent_memories'] = self.memory.recall()[-5:]  # Add recent memories
        function_count = self.functions.get_function_count()

        evolution_suggestions = suggest_system_evolution(memory_summary, function_count, context)

        result = "[System Evolution Suggestions]\n"
        result += f"🧠 System maturity: {memory_summary['total_memories']} memories, {function_count} functions\n"
        result += f"📊 Knowledge areas: {', '.join(memory_summary['categories'])}\n"
        result += f"\n[AI Evolution Analysis]\n{evolution_suggestions}"

        return result

    def adaptive_suggest(self, context=""):
        """Provide context-aware suggestions based on current state"""
        recent_memories = self.memory.recall()[-3:] if self.memory.recall() else []
        available_tags = self.memory.get_tags()
        function_names = self.functions.get_function_names()

        suggestions = provide_adaptive_suggestions(context, recent_memories, available_tags, function_names)

        result = "[Adaptive Suggestions]\n"
        if context:
            result += f"🎯 Context: {context}\n"
        result += f"📚 Recent activity: {len(recent_memories)} recent memories\n"
        result += f"🔧 Available tools: {len(function_names)} functions, {len(available_tags)} tag categories\n"
        result += f"\n[AI Adaptive Suggestions]\n{suggestions}"

        return result

    def get_command_type(self, line):
        """Categorize command type for pattern analysis"""
        if line.startswith("remember"):
            return "memory_store"
        elif line.startswith("recall"):
            return "memory_recall"
        elif line.startswith("reflect"):
            return "ai_reflection"
        elif line.startswith("define"):
            return "function_define"
        elif line.startswith("call"):
            return "function_call"
        elif line.startswith("memory"):
            return "memory_management"
        elif line.startswith("learn"):
            return "learning"
        elif line.startswith("assistant"):
            return "ai_query"
        elif line.startswith("detect") or line.startswith("analyze") or line.startswith("suggest"):
            return "pattern_analysis"
        elif line.startswith("load") \or
            line.startswith("refactor")
            line.startswith("apply")
            line.startswith("backup")
            line.startswith("diff"):
            return "self_editing"
        else:
            return "other"

    def suggest_self_editing_opportunities(self):
        """Analyze memory patterns to suggest proactive self-editing opportunities"""
        if not self.memory.memory:
            return "[Self-Edit Suggestions] No memory patterns to analyze"

        # Get memories related to errors, patterns, and code issues
        error_memories = self.memory.recall(tags=['error', 'bug', 'issue'])
        pattern_memories = self.memory.recall(tags=['pattern', 'recurring'])
        code_memories = self.memory.recall(category='code_management')

        # Combine for context
        all_memories = error_memories + pattern_memories + code_memories

        if not all_memories:
            return "[Self-Edit Suggestions] No relevant memory patterns found"

        # Use AI to analyze patterns and suggest self-editing
        pattern_summary = self.memory.get_memory_stats()
        suggestions = memory_driven_code_suggestion(all_memories, pattern_summary)

        # Store this analysis for future reference
        self.memory.remember(
            f"Self-editing analysis: {suggestions[:100]}...",
            tags=['self_edit_suggestion', 'proactive_analysis'],
            category='system_evolution'
        )

        return f"[Self-Edit Opportunities] {suggestions}"

    def justify_self_editing(self, filename, analysis_result):
        """Provide memory-driven justification for self-editing a specific file"""
        relevant_memories = self.memory.recall(tags=['code_analysis', 'error', 'pattern'])
        memory_context = "\n".join([m['text'] for m in relevant_memories[-5:]])

        justification = justify_self_editing_decision(filename, analysis_result, memory_context)

        # Remember this justification
        self.memory.remember(
            f"Justified self-editing {filename}: {justification[:100]}...",
            tags=['justification', 'self_editing', 'decision'],
            category='code_management'
        )

        return justification
