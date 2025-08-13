#!/usr/bin/env python3
"""
Aetherra Script Service
=======================

Service for integrating Aether Script (.aether) interpretation and execution
into the Aetherra AI Operating System.

This service:
- Loads and executes .aether scripts
- Provides runtime integration with OS services
- Manages script lifecycle and dependencies
- Enables cognitive workflow orchestration
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AetherScriptService:
    """
    Aether Script Service for the Aetherra AI OS

    Integrates the native .aether script interpreter with the OS services,
    providing cognitive workflow orchestration and script execution.
    """

    def __init__(self, service_registry=None):
        self.service_registry = service_registry
        self.interpreter = None
        self.running_scripts = {}
        self.bootstrap_scripts = []
        self.startup_scripts = []
        self.running = False

    async def initialize(self):
        """Initialize the Aether Script service."""
        try:
            logger.info("[AETHER] Initializing Aether Script Service...")

            # Import the enhanced Aetherra interpreter
            from Aetherra.aetherra_core.agents.enhanced_interpreter import AetherraEnhancedInterpreter
            from Aetherra.aetherra_core.agents.aetherra_interpreter import AetherraInterpreter

            # Create base interpreter
            base_interpreter = AetherraInterpreter()

            # Create enhanced interpreter with base interpreter
            self.interpreter = AetherraEnhancedInterpreter(base_interpreter)

            # Discover bootstrap and startup scripts
            await self._discover_scripts()

            logger.info("[AETHER] Aether Script Service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"[AETHER] Failed to initialize Aether Script Service: {e}")
            return False

    async def start(self):
        """Start the Aether Script service."""
        if not self.interpreter:
            logger.error("[AETHER] Cannot start service - interpreter not initialized")
            return False

        logger.info("[AETHER] Starting Aether Script Service...")
        self.running = True

        # Execute bootstrap scripts first
        await self._execute_bootstrap_scripts()

        # Execute startup scripts
        await self._execute_startup_scripts()

        logger.info("[AETHER] Aether Script Service started successfully")
        return True

    async def stop(self):
        """Stop the Aether Script service."""
        logger.info("[AETHER] Stopping Aether Script Service...")
        self.running = False

        # Cancel running scripts
        for script_id, task in self.running_scripts.items():
            if not task.done():
                task.cancel()
                logger.info(f"[AETHER] Cancelled running script: {script_id}")

        self.running_scripts.clear()
        logger.info("[AETHER] Aether Script Service stopped")

    async def execute_script_file(self, script_path: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute an .aether script file."""
        try:
            script_path = Path(script_path)

            if not script_path.exists():
                raise FileNotFoundError(f"Script file not found: {script_path}")

            if not script_path.suffix == '.aether':
                raise ValueError(f"File is not an .aether script: {script_path}")

            logger.info(f"[AETHER] Executing script: {script_path}")

            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Parse and execute script
            result = await self._execute_script_content(script_content, str(script_path), context)

            logger.info(f"[AETHER] Script execution completed: {script_path}")
            return {
                "success": True,
                "script_path": str(script_path),
                "result": result,
                "execution_time": result.get("execution_time", 0)
            }

        except Exception as e:
            logger.error(f"[AETHER] Script execution failed: {e}")
            return {
                "success": False,
                "script_path": str(script_path) if 'script_path' in locals() else None,
                "error": str(e)
            }

    async def execute_script_content(self, script_content: str, filename: str = "<string>", context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute Aether script content directly."""
        try:
            logger.info(f"[AETHER] Executing script content: {filename}")

            result = await self._execute_script_content(script_content, filename, context)

            return {
                "success": True,
                "filename": filename,
                "result": result
            }

        except Exception as e:
            logger.error(f"[AETHER] Script content execution failed: {e}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e)
            }

    async def _execute_script_content(self, script_content: str, filename: str, context: Optional[Dict] = None) -> Any:
        """Internal method to execute script content."""
        import time

        start_time = time.time()

        try:
            # Parse the script content into AST (simplified for now)
            # In a full implementation, this would use the Aetherra grammar parser
            lines = script_content.strip().split('\n')

            # Prepare execution context
            execution_context = context or {}

            # Add OS services to context if available
            if self.service_registry:
                execution_context.update({
                    'memory_system': self.service_registry.get_service('memory_system'),
                    'plugin_manager': self.service_registry.get_service('plugin_manager'),
                    'aetherra_engine': self.service_registry.get_service('aetherra_engine'),
                    'service_registry': self.service_registry
                })

            # Execute script line by line (simplified execution)
            results = []
            current_goal = None

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                try:
                    # Parse and execute statement
                    result = await self._execute_statement(line, execution_context, line_num)
                    if result:
                        results.append(result)

                    # Track goals
                    if line.startswith('goal'):
                        current_goal = line

                except Exception as e:
                    logger.warning(f"[AETHER] Error on line {line_num}: {e}")
                    results.append({"error": str(e), "line": line_num})

            execution_time = time.time() - start_time

            return {
                "results": results,
                "execution_time": execution_time,
                "filename": filename,
                "goal": current_goal,
                "context": execution_context
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[AETHER] Script execution error: {e}")
            return {
                "error": str(e),
                "execution_time": execution_time,
                "filename": filename
            }

    async def _execute_statement(self, statement: str, context: Dict, line_num: int) -> Any:
        """Execute a single Aether script statement."""

        # Goal statement
        if statement.startswith('goal'):
            goal_text = statement[4:].strip()
            if goal_text.startswith('"') and goal_text.endswith('"'):
                goal_text = goal_text[1:-1]
            elif goal_text.startswith("'") and goal_text.endswith("'"):
                goal_text = goal_text[1:-1]

            logger.info(f"[AETHER] Goal: {goal_text}")

            # Process goal through cognitive system if available
            if 'aetherra_engine' in context and context['aetherra_engine']:
                try:
                    # Send goal to Aetherra engine for processing
                    await context['aetherra_engine'].process_thought({
                        'type': 'goal',
                        'content': goal_text,
                        'source': 'aether_script'
                    })
                except Exception as e:
                    logger.warning(f"[AETHER] Goal processing error: {e}")

            return {"type": "goal", "content": goal_text, "line": line_num}

        # Memory operations
        if statement.startswith('memory:') or statement.startswith('recall') or statement.startswith('remember') or statement.startswith('store'):
            return await self._execute_memory_operation(statement, context, line_num)

        # Plugin operations
        if statement.startswith('use plugin') or statement.startswith('run plugin'):
            return await self._execute_plugin_operation(statement, context, line_num)

        # Agent operations
        if statement.startswith('run agent'):
            return await self._execute_agent_operation(statement, context, line_num)

        # Variable assignment
        if '=' in statement and not statement.startswith('$'):
            return await self._execute_assignment(statement, context, line_num)

        # Function calls
        if '(' in statement and statement.endswith(')'):
            return await self._execute_function_call(statement, context, line_num)

        # Default: treat as informational
        return {"type": "info", "content": statement, "line": line_num}

    async def _execute_memory_operation(self, statement: str, context: Dict, line_num: int) -> Dict:
        """Execute memory-related operations."""
        try:
            memory_system = context.get('memory_system')

            if statement.startswith('recall'):
                # Extract what to recall
                parts = statement.split(' ', 1)
                if len(parts) > 1:
                    query = parts[1].strip('"\'')

                    if memory_system and hasattr(memory_system, 'retrieve'):
                        result = memory_system.retrieve(query)
                        logger.info(f"[AETHER] Recalled: {query}")
                        return {"type": "recall", "query": query, "result": result, "line": line_num}
                    else:
                        logger.info(f"[AETHER] Recall simulation: {query}")
                        return {"type": "recall", "query": query, "result": f"Simulated recall for: {query}", "line": line_num}

            elif statement.startswith('remember'):
                # Extract what to remember
                if 'as' in statement:
                    parts = statement.split(' as ')
                    content = parts[0].replace('remember', '').strip().strip('"\'')
                    tag = parts[1].strip().strip('"\'')
                else:
                    content = statement.replace('remember', '').strip().strip('"\'')
                    tag = "general"

                if memory_system and hasattr(memory_system, 'store'):
                    memory_system.store(content, {"tag": tag})
                    logger.info(f"[AETHER] Remembered: {content} (tag: {tag})")
                    return {"type": "remember", "content": content, "tag": tag, "line": line_num}
                else:
                    logger.info(f"[AETHER] Remember simulation: {content} (tag: {tag})")
                    return {"type": "remember", "content": content, "tag": tag, "line": line_num}

            elif statement.startswith('store'):
                # Extract what to store
                content = statement.replace('store', '').strip()

                if memory_system and hasattr(memory_system, 'store'):
                    memory_system.store(content, {"source": "aether_script"})
                    logger.info(f"[AETHER] Stored: {content}")
                    return {"type": "store", "content": content, "line": line_num}
                else:
                    logger.info(f"[AETHER] Store simulation: {content}")
                    return {"type": "store", "content": content, "line": line_num}

            return {"type": "memory_operation", "statement": statement, "line": line_num}

        except Exception as e:
            logger.error(f"[AETHER] Memory operation error: {e}")
            return {"type": "error", "error": str(e), "line": line_num}

    async def _execute_plugin_operation(self, statement: str, context: Dict, line_num: int) -> Dict:
        """Execute plugin-related operations."""
        try:
            plugin_manager = context.get('plugin_manager')

            if statement.startswith('use plugin'):
                plugin_name = statement.replace('use plugin', '').strip().strip('"\'')
                logger.info(f"[AETHER] Using plugin: {plugin_name}")
                return {"type": "use_plugin", "plugin": plugin_name, "line": line_num}

            elif statement.startswith('run plugin'):
                plugin_name = statement.replace('run plugin', '').strip().strip('"\'')

                if plugin_manager and hasattr(plugin_manager, 'invoke_plugin'):
                    try:
                        result = await plugin_manager.invoke_plugin({"plugin": plugin_name})
                        logger.info(f"[AETHER] Ran plugin: {plugin_name}")
                        return {"type": "run_plugin", "plugin": plugin_name, "result": result, "line": line_num}
                    except Exception as e:
                        logger.warning(f"[AETHER] Plugin execution error: {e}")
                        return {"type": "run_plugin", "plugin": plugin_name, "error": str(e), "line": line_num}
                else:
                    logger.info(f"[AETHER] Plugin simulation: {plugin_name}")
                    return {"type": "run_plugin", "plugin": plugin_name, "result": f"Simulated execution of {plugin_name}", "line": line_num}

            return {"type": "plugin_operation", "statement": statement, "line": line_num}

        except Exception as e:
            logger.error(f"[AETHER] Plugin operation error: {e}")
            return {"type": "error", "error": str(e), "line": line_num}

    async def _execute_agent_operation(self, statement: str, context: Dict, line_num: int) -> Dict:
        """Execute agent-related operations."""
        try:
            # Extract agent name and parameters
            parts = statement.replace('run agent', '').strip().split(' with ')
            agent_name = parts[0].strip().strip('"\'')
            parameters = parts[1] if len(parts) > 1 else None

            logger.info(f"[AETHER] Running agent: {agent_name}")

            # Simulate agent execution
            result = f"Agent {agent_name} executed with parameters: {parameters}"

            return {"type": "run_agent", "agent": agent_name, "parameters": parameters, "result": result, "line": line_num}

        except Exception as e:
            logger.error(f"[AETHER] Agent operation error: {e}")
            return {"type": "error", "error": str(e), "line": line_num}

    async def _execute_assignment(self, statement: str, context: Dict, line_num: int) -> Dict:
        """Execute variable assignment."""
        try:
            parts = statement.split('=', 1)
            if len(parts) == 2:
                var_name = parts[0].strip().lstrip('$')  # Remove $ prefix if present
                var_value = parts[1].strip().strip('"\'')

                # Store in context
                context[var_name] = var_value

                logger.info(f"[AETHER] Assignment: {var_name} = {var_value}")
                return {"type": "assignment", "variable": var_name, "value": var_value, "line": line_num}

            return {"type": "assignment_error", "statement": statement, "line": line_num}

        except Exception as e:
            logger.error(f"[AETHER] Assignment error: {e}")
            return {"type": "error", "error": str(e), "line": line_num}

    async def _execute_function_call(self, statement: str, context: Dict, line_num: int) -> Dict:
        """Execute function call."""
        try:
            # Parse function name and arguments
            func_name = statement[:statement.index('(')]
            args_str = statement[statement.index('(')+1:statement.rindex(')')]

            logger.info(f"[AETHER] Function call: {func_name}({args_str})")

            # Simulate function execution
            result = f"Function {func_name} called with args: {args_str}"

            return {"type": "function_call", "function": func_name, "args": args_str, "result": result, "line": line_num}

        except Exception as e:
            logger.error(f"[AETHER] Function call error: {e}")
            return {"type": "error", "error": str(e), "line": line_num}

    async def _discover_scripts(self):
        """Discover bootstrap and startup .aether scripts."""
        try:
            project_root = Path(__file__).parent.parent.parent

            # Look for bootstrap scripts
            bootstrap_locations = [
                project_root / "Aetherra" / "aetherra_core" / "system" / "bootstrap.aether",
                project_root / "bootstrap.aether",
                project_root / "scripts" / "bootstrap.aether"
            ]

            for script_path in bootstrap_locations:
                if script_path.exists():
                    self.bootstrap_scripts.append(script_path)
                    logger.info(f"[AETHER] Found bootstrap script: {script_path}")

            # Look for startup scripts
            startup_locations = [
                project_root / "Aetherra" / "aetherra_core" / "system" / "startup.aether",
                project_root / "startup.aether",
                project_root / "scripts" / "startup.aether"
            ]

            for script_path in startup_locations:
                if script_path.exists():
                    self.startup_scripts.append(script_path)
                    logger.info(f"[AETHER] Found startup script: {script_path}")

            # Also look for evolution_history.aether
            evolution_script = project_root / "evolution_history.aether"
            if evolution_script.exists():
                self.startup_scripts.append(evolution_script)
                logger.info(f"[AETHER] Found evolution history script: {evolution_script}")

        except Exception as e:
            logger.error(f"[AETHER] Script discovery error: {e}")

    async def _execute_bootstrap_scripts(self):
        """Execute bootstrap scripts."""
        for script_path in self.bootstrap_scripts:
            try:
                logger.info(f"[AETHER] Executing bootstrap script: {script_path}")
                result = await self.execute_script_file(str(script_path))

                if result["success"]:
                    logger.info(f"[AETHER] Bootstrap script completed: {script_path}")
                else:
                    logger.error(f"[AETHER] Bootstrap script failed: {script_path} - {result.get('error')}")

            except Exception as e:
                logger.error(f"[AETHER] Bootstrap script execution error: {e}")

    async def _execute_startup_scripts(self):
        """Execute startup scripts."""
        for script_path in self.startup_scripts:
            try:
                logger.info(f"[AETHER] Executing startup script: {script_path}")
                result = await self.execute_script_file(str(script_path))

                if result["success"]:
                    logger.info(f"[AETHER] Startup script completed: {script_path}")
                else:
                    logger.error(f"[AETHER] Startup script failed: {script_path} - {result.get('error')}")

            except Exception as e:
                logger.error(f"[AETHER] Startup script execution error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "running": self.running,
            "interpreter_available": self.interpreter is not None,
            "bootstrap_scripts": [str(p) for p in self.bootstrap_scripts],
            "startup_scripts": [str(p) for p in self.startup_scripts],
            "running_scripts": list(self.running_scripts.keys())
        }


# Service factory function
async def get_aether_script_service(service_registry=None):
    """Factory function to create and initialize the Aether Script service."""
    service = AetherScriptService(service_registry)
    await service.initialize()
    return service
