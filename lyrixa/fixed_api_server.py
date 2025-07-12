#!/usr/bin/env python3
"""
Fixed Lyrixa Self-Improvement Dashboard API
All endpoints registered directly to app to avoid router issues
"""

import json
import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(title="Lyrixa Intelligence API", version="2.0.0")

# Import intelligence modules
import lyrixa.agent_collaboration_manager
from lyrixa.agent_collaboration_manager import (
    enable_agent_chaining,
    register_agent,
    suggest_agent_pairings,
)

list_agents = getattr(lyrixa.agent_collaboration_manager, "list_agents", None)
from lyrixa.cognitive_monitor_dashboard import summarize_dashboard
from Aetherra.core.engine.goal_forecaster import forecast_goal
from lyrixa.reasoning_memory_layer import reasoning_context_for_goal

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
            "/api/goals/forecast",
            "/api/goals/reasoning_context",
            "/api/agents/list",
            "/api/agents/register",
            "/api/agents/suggest_pairings",
            "/api/agents/enable_chaining",
            "/api/cognitive_monitor/dashboard",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Lyrixa Fixed Intelligence API...")
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
