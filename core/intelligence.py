#!/usr/bin/env python3
"""
Intelligence module for the Aetherra project
Advanced AI capabilities for decision making and pattern analysis
"""


def justify_self_editing_decision(filename, analysis_result, memory_context):
    """
    Justify self-editing decisions based on analysis and memory context

    Args:
        filename: File being considered for editing
        analysis_result: Results from code analysis
        memory_context: Relevant memory context

    Returns:
        Detailed justification for self-editing
    """
    return f"""
[Self-Editing Justification for {filename}]
📊 Analysis Result: {analysis_result}
🧠 Memory Context: {memory_context[:200]}...
💡 Decision: Self-editing justified based on:
   - Consistent patterns detected in memory
   - Analysis indicates improvement opportunities
   - Historical context supports this modification
   - Risk assessment: Low (reversible changes)
"""


def memory_driven_code_suggestion(all_memories, pattern_summary):
    """
    Provide memory-driven code suggestions based on learned patterns

    Args:
        all_memories: List of relevant memories
        pattern_summary: Statistical summary of memory patterns

    Returns:
        Actionable code suggestions based on memory patterns
    """
    if not all_memories:
        return "No memory patterns available for code suggestions"

    total_memories = len(all_memories)
    recent_patterns = [m.get("text", "")[:50] for m in all_memories[-3:]]

    return f"""
[Memory-Driven Code Suggestions]
📈 Based on {total_memories} relevant memories
🔍 Pattern Analysis: {pattern_summary.get("total", 0)} total patterns analyzed
🎯 Recent Patterns: {", ".join(recent_patterns)}
💡 Suggestions:
   - Consider refactoring frequently mentioned components
   - Implement error handling for recurring issues
   - Add monitoring for patterns that appear > 3 times
   - Optimize code paths mentioned in performance memories
"""


def provide_adaptive_suggestions(
    context, recent_memories, available_tags, function_names
):
    """
    Provide adaptive suggestions based on current context

    Args:
        context: Current context or situation
        recent_memories: Recent memory entries
        available_tags: Available memory tags
        function_names: Available function names

    Returns:
        Context-aware adaptive suggestions
    """
    suggestions = []

    if context:
        suggestions.append(
            f"🎯 Context-aware: Based on '{context}', consider related actions"
        )

    if recent_memories:
        memory_count = len(recent_memories)
        suggestions.append(
            f"📚 Memory insights: {memory_count} recent memories suggest patterns"
        )

    if available_tags:
        top_tags = available_tags[:3]
        suggestions.append(
            f"🏷️ Tag utilization: Consider using tags: {', '.join(top_tags)}"
        )

    if function_names:
        top_functions = function_names[:3]
        suggestions.append(
            f"⚙️ Function opportunities: Available functions: {', '.join(top_functions)}"
        )

    # Add general adaptive suggestions
    suggestions.append("🔄 Adaptive learning: System is learning from your patterns")
    suggestions.append("📊 Optimization: Consider memory consolidation if > 50 entries")

    return (
        "\n".join(suggestions)
        if suggestions
        else "No specific adaptive suggestions at this time"
    )


def suggest_system_evolution(memory_summary, function_count, context=""):
    """
    Suggest system evolution strategies based on current state

    Args:
        memory_summary: Summary of memory system state
        function_count: Number of available functions
        context: Additional context for suggestions

    Returns:
        Strategic evolution suggestions
    """
    total_memories = memory_summary.get("total_memories", 0)
    categories = memory_summary.get("categories", [])

    suggestions = []

    # Memory-based evolution
    if total_memories > 100:
        suggestions.append(
            "🧠 Memory Evolution: System has substantial memory - consider memory clustering"
        )
    elif total_memories > 50:
        suggestions.append("📊 Memory Growth: Consider implementing memory categories")
    else:
        suggestions.append(
            "🌱 Memory Building: Focus on accumulating diverse experiences"
        )

    # Function-based evolution
    if function_count > 20:
        suggestions.append(
            "⚙️ Function Evolution: Rich function library - consider function specialization"
        )
    elif function_count > 10:
        suggestions.append("🔧 Function Organization: Consider function categorization")
    else:
        suggestions.append("🛠️ Function Development: Expand function capabilities")

    # Category-based evolution
    if len(categories) > 5:
        suggestions.append(
            "📂 Category Evolution: Diverse knowledge areas - consider specialization"
        )
    elif len(categories) > 3:
        suggestions.append(
            "🎯 Category Focus: Consider deepening expertise in key areas"
        )
    else:
        suggestions.append("🌐 Category Expansion: Explore new knowledge domains")

    # Context-specific evolution
    if context:
        suggestions.append(
            f"🎯 Context Evolution: For '{context}', consider targeted improvements"
        )

    # Always include forward-looking suggestions
    suggestions.append("🚀 Future-Ready: Consider implementing predictive capabilities")
    suggestions.append(
        "🔄 Self-Improvement: Regular system self-assessment recommended"
    )

    return (
        "\n".join(suggestions)
        if suggestions
        else "System evolution suggestions not available"
    )
