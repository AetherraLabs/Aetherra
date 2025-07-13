"""
Test API server for goal forecast and other endpoints
"""

import json

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from lyrixa.agent_collaboration_manager import (
    enable_agent_chaining,
    get_agent_status,
    suggest_agent_pairings,
)
from lyrixa.cognitive_monitor_dashboard import summarize_dashboard

# Import the Phase 2 modules directly
from lyrixa.goal_forecaster import forecast_goal as forecast_goal_fn
from lyrixa.reasoning_memory_layer import reasoning_context_for_goal

router = APIRouter()
app = FastAPI()
app.include_router(router)


@router.post("/api/goals/forecast")
async def api_forecast_goal(request: Request):
    """Forecast the outcome of a goal before execution."""
    try:
        data = await request.json()
        goal = data.get("goal")
        if not goal:
            return JSONResponse(
                content={"error": "Missing 'goal' in request."}, status_code=400
            )
        forecast = forecast_goal_fn(goal)
        return {"forecast": forecast, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@router.post("/api/goals/reasoning_context")
async def api_get_reasoning_context(request: Request):
    """Return reasoning context for a goal, including related past cases and outcomes."""
    try:
        data = await request.json()
        goal = data.get("goal")
        if not goal:
            return JSONResponse(
                content={"error": "Missing 'goal' in request."}, status_code=400
            )
        context = reasoning_context_for_goal(goal)
        return {"reasoning_context": context, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@router.get("/api/agents/status")
async def api_get_agent_status():
    """Get the status of all registered agents."""
    try:
        status = get_agent_status()
        return {"agents": status, "count": len(status), "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@router.get("/api/cognitive_monitor/dashboard")
async def api_cognitive_monitor_dashboard():
    """Get live system insights for the cognitive monitor dashboard."""
    try:
        summary = summarize_dashboard()
        return summary
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)
