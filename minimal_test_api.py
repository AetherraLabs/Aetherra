"""
Minimal test API server
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "API is working", "status": "success"}


@app.post("/api/goals/forecast")
async def api_forecast_goal(request: Request):
    """Forecast the outcome of a goal before execution."""
    try:
        data = await request.json()
        goal = data.get("goal")
        if not goal:
            return JSONResponse(
                content={"error": "Missing 'goal' in request."}, status_code=400
            )

        # Simple forecast without imports
        forecast = {
            "type": "forecast",
            "goal": goal,
            "forecast": "Likely to succeed (test response)",
            "risk": "low",
            "suggestions": ["This is a test response"],
            "confidence": 0.8,
        }
        return {"forecast": forecast, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8005)
