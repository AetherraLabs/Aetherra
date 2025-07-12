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
    # Explicitly set plugins_dir to lyrixa/plugins for local development
    plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins"))
    if not os.path.exists(plugins_dir):
        print(f"[Lyrixa DEBUG] Plugins directory does not exist: {plugins_dir}")
    else:
        print(f"[Lyrixa DEBUG] Using plugins directory: {plugins_dir}")
    return EnhancedPluginManager(plugins_dir=plugins_dir)


@router.get("/api/plugins/discover")
async def discover_plugins():
    """Discover all available plugins using EnhancedPluginManager (Aetherhub)."""
    try:
        enhanced_manager = get_enhanced_plugin_manager()
        print(f"[Lyrixa DEBUG] Scanning for plugins in: {enhanced_manager.plugins_dir}")
        plugins = []
        errors = []
        for plugin in enhanced_manager.list_installed_plugins():
            try:
                plugins.append(plugin.manifest.name)
            except Exception as e:
                errors.append(f"Error loading plugin: {e}")
        registry_plugins = enhanced_manager.search_registry()
        registry_plugin_names = [p.manifest.name for p in registry_plugins]
        all_plugins = sorted(set(plugins + registry_plugin_names))
        debug_info = {
            "scanned_dir": str(enhanced_manager.plugins_dir),
            "plugin_count": len(plugins),
            "errors": errors,
        }
        print(f"[Lyrixa DEBUG] Plugin discovery debug info: {debug_info}")
        return {
            "plugins": all_plugins,
            "installed_plugins": plugins,
            "registry_plugins": registry_plugin_names,
            "count": len(all_plugins),
            "status": "success",
            "debug": debug_info,
        }
    except Exception as e:
        print(f"[Lyrixa DEBUG] Plugin discovery error: {e}")
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
        from Aetherra.core.engine.goal_forecaster import forecast_goal as forecast_goal_fn

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


from lyrixa.agent_collaboration_manager import (
    enable_agent_chaining,
    get_agent_status,
    suggest_agent_pairings,
)
from lyrixa.cognitive_monitor_dashboard import summarize_dashboard


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


@router.post("/api/agents/suggest_pairings")
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


@router.post("/api/agents/enable_chaining")
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
