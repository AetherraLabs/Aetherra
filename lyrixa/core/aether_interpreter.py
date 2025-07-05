#!/usr/bin/env python3
"""
🧠 AETHER INTERPRETER
===================

Lyrixa's core capability to understand, parse, and execute .aether code.
This interpreter allows Lyrixa to work with .aether workflows naturally.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from lyrixa.core.memory import LyrixaMemorySystem


@dataclass
class AetherNode:
    """Represents a node in an .aether workflow"""

    name: str
    type: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]
    position: Tuple[int, int] = (0, 0)


@dataclass
class AetherWorkflow:
    """Represents a complete .aether workflow"""

    name: str
    nodes: List[AetherNode]
    connections: List[Dict[str, str]]
    metadata: Dict[str, Any]
    created_at: datetime


class AetherInterpreter:
    """
    Lyrixa's .aether code interpreter

    Parses, validates, and executes .aether workflows.
    Provides natural language generation and debugging capabilities.
    """

    def __init__(self):
        self.supported_node_types = {
            "input",
            "output",
            "transform",
            "filter",
            "aggregate",
            "branch",
            "loop",
            "function",
            "api_call",
            "data_source",
            "model",
            "analyzer",
            "generator",
            "validator",
        }
        self.active_workflows = {}
        self.execution_history = []

    async def parse_aether_code(self, aether_code: str) -> AetherWorkflow:
        """
        Parse .aether code into a structured workflow
        """
        try:
            # Simple parser for .aether syntax
            # In a real implementation, this would be more sophisticated
            lines = aether_code.strip().split("\n")
            nodes = []
            connections = []
            workflow_metadata = {}

            current_node = None

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Parse node definition
                if line.startswith("node "):
                    if current_node:
                        nodes.append(current_node)

                    # Extract node name and type
                    parts = line.split()
                    node_name = parts[1]
                    node_type = parts[2] if len(parts) > 2 else "transform"

                    current_node = AetherNode(
                        name=node_name,
                        type=node_type,
                        inputs={},
                        outputs={},
                        metadata={},
                    )

                # Parse connections
                elif "->" in line:
                    connection_parts = line.split("->")
                    source = connection_parts[0].strip()
                    target = connection_parts[1].strip()
                    connections.append({"source": source, "target": target})

                # Parse node properties
                elif current_node and ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    try:
                        # Try to parse as JSON
                        parsed_value = json.loads(value)
                        current_node.inputs[key] = parsed_value
                    except json.JSONDecodeError:
                        # Store as string
                        current_node.inputs[key] = value

            # Add last node
            if current_node:
                nodes.append(current_node)

            workflow = AetherWorkflow(
                name=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                nodes=nodes,
                connections=connections,
                metadata=workflow_metadata,
                created_at=datetime.now(),
            )

            return workflow

        except Exception as e:
            raise Exception(f"Failed to parse .aether code: {str(e)}")

    async def generate_aether_from_intent(
        self, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate .aether code from natural language intent

        This is where Lyrixa's intelligence shines - converting human intent
        into executable .aether workflows.
        """
        context = context or {}

        # Simple intent-to-aether generation
        # In a real implementation, this would use AI/ML models

        if "data analysis" in intent.lower():
            return self._generate_data_analysis_workflow(intent, context)
        elif "api" in intent.lower():
            return self._generate_api_workflow(intent, context)
        elif "process" in intent.lower() or "transform" in intent.lower():
            return self._generate_transform_workflow(intent, context)
        else:
            return self._generate_basic_workflow(intent, context)

    def _generate_data_analysis_workflow(
        self, intent: str, context: Dict[str, Any]
    ) -> str:
        """Generate a data analysis .aether workflow"""
        return """# Data Analysis Workflow
node data_input input
  source: "data/input.csv"
  format: "csv"

node analyzer analyzer
  analysis_type: "descriptive_stats"
  columns: ["all"]

node visualizer generator
  chart_type: "histogram"
  output_format: "png"

node results output
  destination: "analysis_results.json"

data_input -> analyzer
analyzer -> visualizer
analyzer -> results"""

    def _generate_api_workflow(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate an API interaction .aether workflow"""
        return """# API Interaction Workflow
node api_call api_call
  url: "https://api.example.com/data"
  method: "GET"
  headers: {"Authorization": "Bearer TOKEN"}

node response_processor transform
  operation: "json_parse"
  extract_fields: ["data", "status"]

node output_handler output
  format: "json"
  destination: "api_response.json"

api_call -> response_processor
response_processor -> output_handler"""

    def _generate_transform_workflow(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate a data transformation .aether workflow"""
        return """# Data Transformation Workflow
node input_data input
  source: "input_data"

node transformer transform
  operation: "clean_and_normalize"
  rules: ["remove_nulls", "standardize_format"]

node validator validator
  schema: "output_schema.json"
  strict: true

node output_data output
  destination: "transformed_data"

input_data -> transformer
transformer -> validator
validator -> output_data"""

    def _generate_basic_workflow(self, intent: str, context: Dict[str, Any]) -> str:
        """Generate a basic .aether workflow"""
        return f"""# Generated from: {intent}
node input input
  description: "Input for {intent}"

node processor transform
  operation: "process"

node output output
  description: "Output for {intent}"

input -> processor
processor -> output"""

    async def execute_workflow(
        self,
        workflow: AetherWorkflow,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an .aether workflow
        """
        execution_context = execution_context or {}

        execution_result = {
            "workflow_name": workflow.name,
            "start_time": datetime.now().isoformat(),
            "nodes_executed": [],
            "outputs": {},
            "status": "running",
            "errors": [],
        }

        try:
            # Simulate workflow execution
            # In a real implementation, this would execute each node
            for node in workflow.nodes:
                print(f"🔄 Executing node: {node.name} ({node.type})")

                # Simulate node execution
                node_result = await self._execute_node(node, execution_context)
                execution_result["nodes_executed"].append(
                    {
                        "node": node.name,
                        "type": node.type,
                        "result": node_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            execution_result["status"] = "completed"
            execution_result["end_time"] = datetime.now().isoformat()

        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["errors"].append(str(e))
            execution_result["end_time"] = datetime.now().isoformat()

        # Store in execution history
        self.execution_history.append(execution_result)

        return execution_result

    async def _execute_node(
        self, node: AetherNode, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single .aether node"""
        # Simulate node execution based on type
        if node.type == "input":
            return {
                "status": "success",
                "data": f"Input from {node.inputs.get('source', 'unknown')}",
            }
        elif node.type == "transform":
            return {
                "status": "success",
                "data": f"Transformed data using {node.inputs.get('operation', 'default')}",
            }
        elif node.type == "output":
            return {
                "status": "success",
                "data": f"Output to {node.inputs.get('destination', 'unknown')}",
            }
        else:
            return {"status": "success", "data": f"Executed {node.type} node"}

    async def explain_workflow(self, workflow: AetherWorkflow) -> str:
        """
        Generate a natural language explanation of an .aether workflow
        """
        explanation = f"This .aether workflow '{workflow.name}' contains {len(workflow.nodes)} nodes:\n\n"

        for i, node in enumerate(workflow.nodes, 1):
            explanation += f"{i}. **{node.name}** ({node.type}): "

            if node.type == "input":
                source = node.inputs.get("source", "unknown source")
                explanation += f"Reads data from {source}\n"
            elif node.type == "transform":
                operation = node.inputs.get("operation", "processes")
                explanation += f"Applies {operation} transformation\n"
            elif node.type == "output":
                dest = node.inputs.get("destination", "unknown destination")
                explanation += f"Writes results to {dest}\n"
            else:
                explanation += f"Performs {node.type} operation\n"

        # Add connection flow
        if workflow.connections:
            explanation += "\n**Data Flow:**\n"
            for conn in workflow.connections:
                explanation += f"• {conn['source']} → {conn['target']}\n"

        return explanation

    def validate_workflow(self, workflow: AetherWorkflow) -> Dict[str, Any]:
        """
        Validate an .aether workflow for correctness
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }

        # Check for unknown node types
        for node in workflow.nodes:
            if node.type not in self.supported_node_types:
                validation_result["errors"].append(f"Unknown node type: {node.type}")
                validation_result["valid"] = False

        # Check for disconnected nodes
        connected_nodes = set()
        for conn in workflow.connections:
            connected_nodes.add(conn["source"])
            connected_nodes.add(conn["target"])

        for node in workflow.nodes:
            if node.name not in connected_nodes and len(workflow.nodes) > 1:
                validation_result["warnings"].append(
                    f"Node '{node.name}' is not connected to the workflow"
                )

        return validation_result

    async def execute_trigger(self, trigger: Dict[str, Any]) -> bool:
        """
        Execute a trigger condition (e.g., schedule or memory condition).
        """
        if "schedule" in trigger:
            # Simulate schedule handling (e.g., daily at "22:00")
            print(f"⏰ Trigger scheduled: {trigger['schedule']}")
            return True

        if "if" in trigger:
            # Simulate condition handling (e.g., memory.has("new_logs"))
            condition = trigger["if"]
            print(f"🔍 Evaluating condition: {condition}")
            return True  # Assume condition is met for now

        return False

    async def execute_memory_operations(
        self, memory_ops: Dict[str, Any], memory_system: LyrixaMemorySystem
    ) -> Dict[str, Any]:
        """
        Execute memory operations (retrieve and store) using Lyrixa's memory system.
        """
        results = {}

        if "retrieve" in memory_ops:
            retrieve_config = memory_ops["retrieve"]
            print(f"📥 Retrieving from memory: {retrieve_config}")
            results["retrieved"] = await memory_system.recall_memories(
                query_text=retrieve_config.get("from", ""),
                limit=retrieve_config.get("limit", 5),
                memory_type=retrieve_config.get("type", None),
            )

        if "store" in memory_ops:
            store_config = memory_ops["store"]
            print(f"📤 Storing into memory: {store_config}")
            memory_id = await memory_system.store_memory(
                content=store_config.get("content", {}),
                context=store_config.get("context", {}),
                tags=store_config.get("tags", []),
                importance=store_config.get("importance", 0.5),
                memory_type=store_config.get("type", "general"),
            )
            results["stored"] = memory_id

        return results

    async def execute_ai_goal(self, ai_goal: Dict[str, Any]) -> str:
        """
        Execute an AI goal with constraints and return the output.
        """
        print(f"🤖 Executing AI goal: {ai_goal['goal']}")
        print(f"🔒 Constraints: {ai_goal.get('constraints', [])}")
        return "summary_text"  # Simulated output

    async def execute_actions(self, actions: List[str]) -> None:
        """
        Execute a list of actions (e.g., memory.save, notify).
        """
        for action in actions:
            print(f"⚡ Executing action: {action}")

    async def execute_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Handle feedback loops (e.g., user confirmation, escalation).
        """
        print(f"📢 Expecting feedback: {feedback['expect']}")
        if "if no_response" in feedback:
            print(f"🚨 Escalating: {feedback['if no_response']}")

    async def execute(
        self, code: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute .aether code directly

        This is the main execution method called by Lyrixa GUI.
        It parses the code and executes the resulting workflow.

        Args:
            code: The .aether code to execute
            context: Optional execution context

        Returns:
            Dictionary containing execution results and status
        """
        try:
            # Parse the .aether code into a workflow
            workflow = await self.parse_aether_code(code)

            # Execute the parsed workflow
            result = await self.execute_workflow(workflow, context)

            return {
                "success": True,
                "result": result,
                "message": "Code executed successfully",
                "workflow_name": workflow.name,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Execution failed: {str(e)}",
                "code": code[:100] + "..." if len(code) > 100 else code,
            }

    def execute_sync(
        self, code: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for execute method

        For compatibility with GUI components that can't handle async calls.
        """
        import asyncio

        try:
            # Run the async execute method
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a new one in a thread
                import concurrent.futures

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(self.execute(code, context))
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(self.execute(code, context))

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Sync execution failed: {str(e)}",
                "code": code[:100] + "..." if len(code) > 100 else code,
            }
