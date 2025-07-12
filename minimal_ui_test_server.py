#!/usr/bin/env python3
"""
Minimal Working API Server for UI Testing
This is a simplified version that should definitely work
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/goals/forecast")
async def forecast_goal(request: Request):
    try:
        data = await request.json()
        goal = data.get("goal", "")
        return {
            "forecast": {
                "type": "forecast",
                "goal": goal,
                "forecast": "UI connection test successful!",
                "risk": "low",
                "confidence": 0.9,
                "suggestions": ["UI is properly connected to API"],
            },
            "status": "success",
        }
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.post("/api/goals/reasoning_context")
async def reasoning_context(request: Request):
    try:
        data = await request.json()
        goal = data.get("goal", "")
        return {
            "context": {
                "goal": goal,
                "similar_patterns": ["UI testing pattern"],
                "confidence": 0.95,
                "recommendations": ["Continue with UI integration"],
            },
            "status": "success",
        }
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@app.get("/api/agents/list")
async def list_agents():
    return {
        "agents": [
            {"id": "ui_test_agent", "capabilities": ["testing"], "status": "active"}
        ],
        "status": "success",
    }


@app.get("/api/cognitive_monitor/dashboard")
async def cognitive_dashboard():
    return {
        "summary": "UI connection test mode",
        "system_health": "good",
        "intelligence_modules": ["goal_forecaster", "reasoning_layer"],
        "status": "success",
    }


@app.post("/api/agents/suggest_pairings")
async def suggest_pairings(request: Request):
    try:
        data = await request.json()
        task = data.get("task", "")
        return {
            "pairings": [{"agents": ["ui_test_agent", "api_test_agent"], "score": 0.9}],
            "status": "success",
        }
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


if __name__ == "__main__":
    print("🚀 Starting minimal API server for UI testing...")
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
