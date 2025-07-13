# Lyrixa Self-Improvement Dashboard API
# UPDATED: This file now redirects to the Enhanced API Server for better reliability
# The enhanced server has all the latest features and proper import handling

import json
import os
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("🔄 Self-Improvement Dashboard API")
print("   Redirecting to Enhanced API Server...")

# Check if we should redirect to enhanced server
enhanced_server_path = project_root / "enhanced_api_server.py"
if enhanced_server_path.exists():
    print("✅ Using Enhanced API Server with full features")
    print("   📍 Location: enhanced_api_server.py")
    print("   🌐 Port: 8007")
    print()
    print("💡 To start the server, use:")
    print("   python enhanced_api_server.py")
    print("   OR")
    print("   python run_self_improvement_api.py")
    print()

    # Import the enhanced server app for compatibility
    try:
        from enhanced_api_server import app
        print("✅ Enhanced API server imported successfully")
    except Exception as e:
        print(f"⚠️ Import note: {e}")
        print("   Server can still be started directly with the files above")
else:
    print("⚠️ Enhanced API server not found, using fallback implementation")

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

# Import plugin managers for discovery
try:
    from Aetherra.lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager
except ImportError:
    print("⚠️ LyrixaAdvancedPluginManager not available - using fallback")
    LyrixaAdvancedPluginManager = None

# Fix import for memory system
try:
    from Aetherra.lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
except ImportError:
    print("⚠️ LyrixaEnhancedMemorySystem not available - using fallback")
    LyrixaEnhancedMemorySystem = None

try:
    from Aetherra.lyrixa.core.enhanced_self_evaluation_agent import EnhancedSelfEvaluationAgent
except ImportError:
    print("⚠️ EnhancedSelfEvaluationAgent not available - using fallback")
    EnhancedSelfEvaluationAgent = None

# Import collaboration and monitoring components
try:
    from Aetherra.lyrixa.agent_collaboration_manager import (
        enable_agent_chaining,
        get_agent_status,
        suggest_agent_pairings,
    )
except ImportError:
    # Fallback functions if module not available
    def enable_agent_chaining(agents, task) -> str:
        return "agent_collaboration_manager not available - using fallback"

    def get_agent_status():
        return []

    def suggest_agent_pairings(task, n=2):
        return []


try:
    from Aetherra.lyrixa.cognitive_monitor_dashboard import summarize_dashboard
except ImportError:
    # Fallback function if module not available
    def summarize_dashboard():
        return {"status": "cognitive_monitor_dashboard not available"}


# Enhanced Plugin Manager import with fallback
try:
    plugins_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "Aetherra", "plugins")
    )
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)
    from Aetherra.lyrixa.plugins.enhanced_plugin_manager import EnhancedPluginManager
except ImportError:
    # Fallback class if EnhancedPluginManager not available
    class EnhancedPluginManager:
        def __init__(self, plugins_dir=None):
            self.plugins_dir = plugins_dir or "plugins"

        def list_installed_plugins(self):
            return []

        def search_registry(self):
            return []

        def install_plugin(self, plugin_name):
            return False


router = APIRouter()

# FastAPI app object
app = FastAPI()
app.include_router(router)


# Dependency injection or global instance as appropriate
def get_agent():
    if LyrixaEnhancedMemorySystem and EnhancedSelfEvaluationAgent:
        memory_system = LyrixaEnhancedMemorySystem()
        return EnhancedSelfEvaluationAgent(memory_system)
    else:
        print("⚠️ Memory system or evaluation agent not available")
        return None


def get_plugin_manager():
    """Get the advanced plugin manager instance"""
    if LyrixaAdvancedPluginManager:
        return LyrixaAdvancedPluginManager()
    else:
        print("⚠️ Advanced plugin manager not available")
        return None


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
        from Aetherra.lyrixa.plugin_intelligence_indexer import get_plugin_capability_index

        index = get_plugin_capability_index()
        return {"plugins": index, "count": len(index), "status": "success"}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "plugins": [], "status": "error"},
            status_code=500,
        )


@router.get("/api/plugins/enhanced_capabilities")
async def get_enhanced_plugin_capabilities():
    """Get enhanced plugin capabilities with detailed metadata, confidence scores, and AI recommendations."""
    try:
        # Import the capability extractor
        import sys
        import os

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from enhanced_plugin_capabilities import PluginCapabilityExtractor

        extractor = PluginCapabilityExtractor()

        # Check multiple plugin directories
        plugins_dirs = [
            os.path.join(os.path.dirname(__file__), "..", "plugins"),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "Aetherra",
                "plugins",
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "src",
                "aetherra",
                "plugins",
            ),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "plugins"),
        ]

        all_plugins = []

        for plugins_dir in plugins_dirs:
            if os.path.exists(plugins_dir):
                print(f"[Enhanced Capabilities] Scanning: {plugins_dir}")
                plugins_in_dir = extractor.bulk_extract_plugins(plugins_dir)
                all_plugins.extend(plugins_in_dir)

        # Remove duplicates based on plugin name
        seen_names = set()
        unique_plugins = []
        for plugin in all_plugins:
            if plugin["name"] not in seen_names:
                seen_names.add(plugin["name"])
                unique_plugins.append(plugin)

        # Sort by confidence score
        unique_plugins.sort(
            key=lambda x: x.get("confidence_score", 0), reverse=True
        )

        # Add summary statistics
        summary = {
            "total_plugins": len(unique_plugins),
            "high_confidence": len(
                [p for p in unique_plugins if p.get("confidence_score", 0) > 0.8]
            ),
            "categories": {},
            "top_capabilities": {},
        }

        # Calculate category distribution
        for plugin in unique_plugins:
            category = plugin.get("category", "unknown")
            summary["categories"][category] = summary["categories"].get(category, 0) + 1

        # Calculate capability frequency
        for plugin in unique_plugins:
            for capability in plugin.get("capabilities", []):
                summary["top_capabilities"][capability] = summary["top_capabilities"].get(
                    capability, 0
                ) + 1

        return {
            "plugins": unique_plugins,
            "summary": summary,
            "status": "success",
            "extraction_method": "enhanced_capability_extractor",
        }

    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"}, status_code=500
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
        from Aetherra.core.engine.goal_forecaster import (
            forecast_goal as forecast_goal_fn,
        )

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
        from Aetherra.lyrixa.reasoning_memory_layer import reasoning_context_for_goal

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


# Main execution block
if __name__ == "__main__":
    print("\n🚀 Starting Lyrixa Self-Improvement Dashboard API...")

    # Try to start the enhanced server if available
    enhanced_server_path = project_root / "enhanced_api_server.py"

    if enhanced_server_path.exists():
        print("✅ Starting Enhanced API Server with full features...")
        print("   🔗 Port: 8007")
        print("   📱 Features: Plugin Intelligence, Meta-Reasoning, Goals, Plugin Editor")

        try:
            # Import and start enhanced server
            import uvicorn
            from enhanced_api_server import app as enhanced_app

            uvicorn.run(enhanced_app, host="127.0.0.1", port=8007, log_level="info")

        except Exception as e:
            print(f"❌ Failed to start enhanced server: {e}")
            print("\n🔄 Falling back to local server...")

            # Fallback to local app
            import uvicorn
            uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
    else:
        print("⚠️ Enhanced server not found, starting local server...")
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8005, log_level="info")
