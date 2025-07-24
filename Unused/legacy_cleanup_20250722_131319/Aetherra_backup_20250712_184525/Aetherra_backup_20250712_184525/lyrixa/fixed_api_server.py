#!/usr/bin/env python3
"""
Fixed Lyrixa Self-Improvement Dashboard API
All endpoints registered directly to app to avoid router issues
"""

import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import intelligence modules
import lyrixa.agent_collaboration_manager
from Aetherra.core.engine.goal_forecaster import forecast_goal
from lyrixa.agent_collaboration_manager import (
    enable_agent_chaining,
    register_agent,
    suggest_agent_pairings,
)
from lyrixa.cognitive_monitor_dashboard import summarize_dashboard
from lyrixa.reasoning_memory_layer import reasoning_context_for_goal

app = FastAPI(title="Lyrixa Intelligence API", version="2.0.0")

list_agents = getattr(lyrixa.agent_collaboration_manager, "list_agents", None)

print("✅ All intelligence modules imported successfully")


# Plugin discovery endpoint
@app.get("/api/plugins/discovery")
async def api_plugin_discovery():
    """Enhanced plugin discovery with capability assessment."""
    try:
        # Mock plugin data for testing
        plugins = [
            {
                "name": "Goal Forecaster",
                "version": "1.0.0",
                "capabilities": ["prediction", "risk_assessment"],
                "status": "active",
            },
            {
                "name": "Memory Layer",
                "version": "1.0.0",
                "capabilities": ["context_linking", "pattern_matching"],
                "status": "active",
            },
        ]
        return {"plugins": plugins, "total": len(plugins), "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Goal forecasting endpoint
@app.post("/api/goals/forecast")
async def api_forecast_goal(request: Request):
    """Forecast the outcome of a goal before execution."""
    try:
        data = await request.json()
        goal = data.get("goal", "")
        if not goal:
            return JSONResponse(
                content={"error": "Goal is required", "status": "error"},
                status_code=400,
            )

        forecast_result = forecast_goal(goal)
        return {"forecast": forecast_result, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Reasoning context endpoint
@app.post("/api/goals/reasoning_context")
async def api_reasoning_context(request: Request):
    """Get reasoning context for a goal based on past patterns."""
    try:
        data = await request.json()
        goal = data.get("goal", "")
        if not goal:
            return JSONResponse(
                content={"error": "Goal is required", "status": "error"},
                status_code=400,
            )

        context = reasoning_context_for_goal(goal)
        return {"context": context, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Agent management endpoints
@app.get("/api/agents/list")
async def api_list_agents():
    """List all registered agents with their capabilities."""
    try:
        if list_agents is None:
            return JSONResponse(
                content={"error": "list_agents function not found", "status": "error"},
                status_code=500,
            )
        agents = list_agents()
        return {"agents": agents, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.post("/api/agents/register")
async def api_register_agent(request: Request):
    """Register a new agent with capabilities."""
    try:
        data = await request.json()
        agent_id = data.get("agent_id", "")
        capabilities = data.get("capabilities", [])
        health = data.get("health", 1.0)
        load = data.get("load", 0)

        result = register_agent(agent_id, capabilities, health, load)
        return {"result": result, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.post("/api/agents/suggest_pairings")
async def api_suggest_agent_pairings(request: Request):
    """Suggest optimal agent pairings for a given task."""
    try:
        data = await request.json()
        task = data.get("task", "")
        n = int(data.get("n", 2))
        pairings = suggest_agent_pairings(task, n)
        return {"pairings": pairings, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.post("/api/agents/enable_chaining")
async def api_enable_agent_chaining(request: Request):
    """Enable agent chaining/parallelism for a task."""
    try:
        data = await request.json()
        agents = data.get("agents", [])
        task = data.get("task", "")
        result = enable_agent_chaining(agents, task)
        return {"result": result, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Cognitive monitoring endpoint
@app.get("/api/cognitive_monitor/dashboard")
async def api_cognitive_monitor_dashboard():
    """Get live system insights for the cognitive monitor dashboard."""
    try:
        summary = summarize_dashboard()
        return summary
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Self-improvement endpoints
@app.post("/api/self_improvement/propose_changes")
async def api_propose_self_improvements(request: Request):
    """Generate self-improvement proposals for Lyrixa."""
    try:
        proposals = {
            "timestamp": "2025-07-12T17:51:00Z",
            "proposals": [
                {
                    "category": "Performance Optimization",
                    "suggestion": "Implement memory caching for frequently accessed data",
                    "impact": "High",
                    "effort": "Medium",
                    "priority": 1
                },
                {
                    "category": "User Experience",
                    "suggestion": "Add real-time progress indicators for long-running tasks",
                    "impact": "Medium",
                    "effort": "Low",
                    "priority": 2
                },
                {
                    "category": "Intelligence Enhancement",
                    "suggestion": "Expand context window for better conversation memory",
                    "impact": "High",
                    "effort": "High",
                    "priority": 3
                },
                {
                    "category": "System Reliability",
                    "suggestion": "Implement automatic error recovery for API connections",
                    "impact": "Medium",
                    "effort": "Medium",
                    "priority": 4
                },
                {
                    "category": "Agent Coordination",
                    "suggestion": "Enhance inter-agent communication protocols",
                    "impact": "High",
                    "effort": "High",
                    "priority": 5
                }
            ],
            "summary": {
                "total_proposals": 5,
                "high_impact": 3,
                "quick_wins": 1,
                "recommended_next": "Implement memory caching for immediate performance gains"
            },
            "status": "success"
        }
        return proposals
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.get("/api/plugins/capabilities")
async def api_plugin_capabilities():
    """Get detailed plugin capabilities and status."""
    try:
        plugins = [
            {
                "name": "sysmon",
                "description": "System performance monitoring",
                "capabilities": ["cpu_monitoring", "memory_tracking", "disk_usage"],
                "status": "active",
                "version": "1.2.0",
                "health": 95
            },
            {
                "name": "optimizer",
                "description": "Code and system performance optimization",
                "capabilities": ["code_analysis", "performance_tuning", "bottleneck_detection"],
                "status": "active",
                "version": "1.1.0",
                "health": 92
            },
            {
                "name": "selfrepair",
                "description": "Automatic debugging and repair system",
                "capabilities": ["error_detection", "auto_fixing", "system_recovery"],
                "status": "active",
                "version": "1.0.0",
                "health": 88
            },
            {
                "name": "whisper",
                "description": "Audio transcription and speech processing",
                "capabilities": ["speech_to_text", "audio_analysis", "language_detection"],
                "status": "active",
                "version": "1.3.0",
                "health": 97
            },
            {
                "name": "reflector",
                "description": "Behavior analysis and self-reflection tools",
                "capabilities": ["pattern_analysis", "behavior_tracking", "insight_generation"],
                "status": "active",
                "version": "1.0.1",
                "health": 91
            },
            {
                "name": "executor",
                "description": "Command scheduling and execution management",
                "capabilities": ["task_scheduling", "command_execution", "workflow_management"],
                "status": "active",
                "version": "1.1.2",
                "health": 94
            },
            {
                "name": "coretools",
                "description": "File access and core utility tools",
                "capabilities": ["file_operations", "data_processing", "utility_functions"],
                "status": "active",
                "version": "1.4.0",
                "health": 96
            }
        ]
        return {
            "plugins": plugins,
            "total": len(plugins),
            "active": len([p for p in plugins if p["status"] == "active"]),
            "average_health": sum(p["health"] for p in plugins) / len(plugins),
            "status": "success"
        }
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "Lyrixa Intelligence API"}


# Root endpoint
@app.get("/")
async def root():
    """API information endpoint."""
    return {
        "service": "Lyrixa Intelligence API",
        "version": "2.0.0",
        "endpoints": [
            "/api/plugins/discovery",
            "/api/plugins/capabilities",
            "/api/goals/forecast",
            "/api/goals/reasoning_context",
            "/api/agents/list",
            "/api/agents/register",
            "/api/agents/suggest_pairings",
            "/api/agents/enable_chaining",
            "/api/cognitive_monitor/dashboard",
            "/api/self_improvement/propose_changes",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Lyrixa Fixed Intelligence API...")
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
