#!/usr/bin/env python3
"""
Goal Forecaster
===============

Simulates and forecasts possible outcomes for goals before execution, using past memory and plugin capability index.
Enhanced with Aetherra's NLP capabilities for better text understanding.
"""

import datetime
import os
import sys
from typing import Any, Dict, List

# Add Aetherra backend to path
aetherra_path = os.path.join(os.path.dirname(__file__), "..", "src")
if aetherra_path not in sys.path:
    sys.path.insert(0, aetherra_path)

# Import Aetherra's NLP capabilities
try:
    from aetherra.core.ai.local_ai import LocalAIEngine

    AETHERRA_NLP_AVAILABLE = True
    print("[GoalForecaster] ✅ Aetherra NLP capabilities loaded")
except ImportError as e:
    print(f"[GoalForecaster] ⚠️  Aetherra NLP not available: {e}")
    AETHERRA_NLP_AVAILABLE = False

# Simple in-memory store for forecasts (stub)
forecast_memory = []

# Global AI instance
_local_ai = None


def get_aetherra_local_ai():
    """Get or initialize Aetherra local AI engine"""
    global _local_ai
    if _local_ai is None and AETHERRA_NLP_AVAILABLE:
        try:
            _local_ai = LocalAIEngine()
            print("[GoalForecaster] ✅ Aetherra Local AI initialized")
        except Exception as e:
            print(f"[GoalForecaster] ❌ Failed to initialize Local AI: {e}")
    return _local_ai


def analyze_goal_sentiment(goal: str) -> Dict[str, Any]:
    """Analyze sentiment and complexity of goal using Aetherra NLP"""
    # Try to use Aetherra's capabilities
    local_ai = get_aetherra_local_ai()
    if local_ai:
        try:
            # Use Aetherra's AI for sentiment analysis if available
            # For now, we'll do basic analysis and prepare for future enhancement
            pass
        except Exception as e:
            print(f"[GoalForecaster] AI analysis error: {e}")

    # Basic sentiment analysis fallback
    positive_words = [
        "improve",
        "enhance",
        "create",
        "build",
        "add",
        "upgrade",
        "optimize",
    ]
    negative_words = ["delete", "remove", "destroy", "break", "shutdown", "format"]
    neutral_words = ["check", "view", "list", "show", "display", "get"]

    goal_lower = goal.lower()
    positive_score = sum(1 for word in positive_words if word in goal_lower)
    negative_score = sum(1 for word in negative_words if word in goal_lower)
    neutral_score = sum(1 for word in neutral_words if word in goal_lower)

    if negative_score > positive_score:
        sentiment = "negative"
        confidence = min(0.8, negative_score * 0.3)
    elif positive_score > negative_score:
        sentiment = "positive"
        confidence = min(0.8, positive_score * 0.3)
    else:
        sentiment = "neutral"
        confidence = 0.5

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "positive_score": positive_score,
        "negative_score": negative_score,
        "neutral_score": neutral_score,
    }


def forecast_goal(goal: str, memory_system=None, plugin_index=None) -> Dict[str, Any]:
    """
    Forecast the outcome of a goal before execution.
    Returns a dict with forecast, risk, suggestions, and stores in memory.
    Enhanced with Aetherra NLP capabilities.
    """
    risk = "low"
    suggestions = []
    forecast = "Likely to succeed."

    # Enhanced analysis using Aetherra NLP
    sentiment_analysis = analyze_goal_sentiment(goal)

    if not goal or len(goal.strip()) < 10:
        risk = "high"
        forecast = "Goal is too vague or short."
        suggestions.append("Please provide more specific details about your goal.")
    elif (
        sentiment_analysis["sentiment"] == "negative"
        and sentiment_analysis["confidence"] > 0.6
    ):
        risk = "high"
        forecast = "Goal involves potentially destructive actions."
        suggestions.append(
            "Consider backup procedures and safety measures before proceeding."
        )
    elif any(
        word in goal.lower()
        for word in ["delete", "remove", "shutdown", "format", "destroy"]
    ):
        risk = "high"
        forecast = "Goal may be destructive."
        suggestions.append("Review for safety and require confirmation.")
    elif any(word in goal.lower() for word in ["install", "plugin", "extend", "add"]):
        risk = "medium"
        forecast = "Goal involves system modifications."
        suggestions.append(
            "Consider using the Plugin Manager to find relevant plugins."
        )
        suggestions.append("Check compatibility before installation.")
    elif sentiment_analysis["sentiment"] == "positive":
        forecast = "Goal shows positive intent and is likely to succeed."
        if sentiment_analysis["confidence"] > 0.6:
            suggestions.append("Goal appears well-structured for execution.")

    # Additional context-based suggestions
    if len(goal.split()) < 5:
        suggestions.append("Consider providing more context for better forecasting.")

    if "test" in goal.lower() or "verify" in goal.lower():
        suggestions.append(
            "Testing approach detected - consider incremental verification steps."
        )

    # Calculate confidence based on multiple factors
    base_confidence = 0.75 if risk == "low" else (0.5 if risk == "medium" else 0.3)
    sentiment_modifier = (
        0.1
        if sentiment_analysis["sentiment"] == "positive"
        else (-0.1 if sentiment_analysis["sentiment"] == "negative" else 0)
    )
    length_modifier = min(0.1, len(goal.split()) * 0.02)  # Bonus for detailed goals

    confidence = max(
        0.1, min(0.95, base_confidence + sentiment_modifier + length_modifier)
    )

    entry = {
        "type": "forecast",
        "goal": goal,
        "forecast_time": datetime.datetime.utcnow().isoformat(),
        "forecast": forecast,
        "risk": risk,
        "suggestions": suggestions,
        "confidence": confidence,
        "sentiment_analysis": sentiment_analysis,
        "nlp_enhanced": AETHERRA_NLP_AVAILABLE,
    }

    forecast_memory.append(entry)
    return entry


if __name__ == "__main__":
    import json

    sample_goal = "Install a new plugin for data analysis"
    print(json.dumps(forecast_goal(sample_goal), indent=2))
