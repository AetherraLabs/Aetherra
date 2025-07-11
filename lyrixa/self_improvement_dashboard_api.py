# Lyrixa Self-Improvement Dashboard API
# This file exposes dashboard data to the UI (Flask/FastAPI style, adjust as needed)

import json
import os
import sys

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

# Import plugin managers for discovery
from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager

# Fix import for memory system
from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
from lyrixa.core.enhanced_self_evaluation_agent import EnhancedSelfEvaluationAgent

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src", "aetherra", "plugins")
    ),
)
from manager import EnhancedPluginManager

router = APIRouter()

# FastAPI app object
app = FastAPI()
app.include_router(router)


# Dependency injection or global instance as appropriate
def get_agent():
    memory_system = LyrixaEnhancedMemorySystem()
    return EnhancedSelfEvaluationAgent(memory_system)


def get_plugin_manager():
    """Get the advanced plugin manager instance"""
    return LyrixaAdvancedPluginManager()


def get_enhanced_plugin_manager():
    """Get the enhanced plugin manager instance (Aetherhub-integrated)"""
    # You can set plugins_dir to your canonical plugin directory if needed
    return EnhancedPluginManager()


@router.get("/api/plugins/discover")
async def discover_plugins():
    """Discover all available plugins using EnhancedPluginManager (Aetherhub)."""
    try:
        enhanced_manager = get_enhanced_plugin_manager()
        plugins = [p.manifest.name for p in enhanced_manager.list_installed_plugins()]
        registry_plugins = enhanced_manager.search_registry()
        registry_plugin_names = [p.manifest.name for p in registry_plugins]
        all_plugins = sorted(set(plugins + registry_plugin_names))
        return {
            "plugins": all_plugins,
            "installed_plugins": plugins,
            "registry_plugins": registry_plugin_names,
            "count": len(all_plugins),
            "status": "success",
        }
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "plugins": [], "count": 0, "status": "error"},
            status_code=500,
        )


@router.get("/api/plugins/status")
async def get_plugin_status():
    """Get the status of all plugins (Aetherhub-integrated)."""
    try:
        enhanced_manager = get_enhanced_plugin_manager()
        installed_plugins = enhanced_manager.list_installed_plugins()
        status_info = {
            "installed_plugins": [p.manifest.name for p in installed_plugins],
            "plugin_details": [p.manifest.__dict__ for p in installed_plugins],
            "status": "success",
        }
        return status_info
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@router.post("/api/plugins/install/{plugin_name}")
async def install_plugin(plugin_name: str):
    """Install a plugin from Aetherhub registry."""
    try:
        enhanced_manager = get_enhanced_plugin_manager()
        success = enhanced_manager.install_plugin(plugin_name)
        return {
            "plugin_name": plugin_name,
            "installed": success,
            "status": "success" if success else "failed",
        }
    except Exception as e:
        return JSONResponse(
            content={
                "plugin_name": plugin_name,
                "installed": False,
                "error": str(e),
                "status": "error",
            },
            status_code=500,
        )


@router.get("/api/self_improvement/metrics")
async def get_dashboard_metrics():
    try:
        agent = get_agent()
        metrics = await agent.get_evaluation_metrics()
        return metrics
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/self_improvement/latest")
async def get_latest_evaluation():
    try:
        agent = get_agent()
        results = await agent.run_immediate_evaluation()
        return results
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/self_improvement/mutation_log")
async def get_mutation_log():
    log_path = os.path.join(os.getcwd(), "mutation_log.json")
    if not os.path.exists(log_path):
        return JSONResponse(content={"log": []})
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    log = [json.loads(line) for line in lines if line.strip()]
    return {"log": log}


@router.post("/api/self_improvement/propose_changes")
async def propose_changes():
    """Trigger the agent to propose actionable changes and store them as memories."""
    try:
        agent = get_agent()
        results = await agent.propose_changes()
        return results
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/plugins/capabilities")
async def get_plugin_capabilities():
    """Return indexed plugin metadata (capabilities, schemas, dependencies, etc)."""
    try:
        from lyrixa.plugin_intelligence_indexer import get_plugin_capability_index

        index = get_plugin_capability_index()
        return {"plugins": index, "count": len(index), "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "plugins": [], "status": "error"},
            status_code=500,
        )


@router.post("/api/goals/forecast")
async def forecast_goal(request: Request):
    """Forecast the outcome of a goal before execution."""
    try:
        data = await request.json()
        goal = data.get("goal")
        if not goal:
            return JSONResponse(
                content={"error": "Missing 'goal' in request."}, status_code=400
            )
        from lyrixa.goal_forecaster import forecast_goal as forecast_goal_fn

        forecast = forecast_goal_fn(goal)
        return {"forecast": forecast, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )


@router.post("/api/goals/reasoning_context")
async def get_reasoning_context(request: Request):
    """Return reasoning context for a goal, including related past cases and outcomes."""
    try:
        data = await request.json()
        goal = data.get("goal")
        if not goal:
            return JSONResponse(
                content={"error": "Missing 'goal' in request."}, status_code=400
            )
        from lyrixa.reasoning_memory_layer import reasoning_context_for_goal

        context = reasoning_context_for_goal(goal)
        return {"reasoning_context": context, "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
        )
