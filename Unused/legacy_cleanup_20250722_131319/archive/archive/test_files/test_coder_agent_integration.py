#!/usr/bin/env python3
"""
🤖 LYRIXA CODER AGENT INTEGRATION TEST
====================================

Test the integration between LyrixaCoderAgent and Natural Language → Aether Generator.
Verifies agent orchestration, task execution, and workflow generation.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyrixa.core.agents import AgentOrchestrator, AgentType, CoderAgent
from lyrixa.core.memory import LyrixaMemorySystem


class CoderAgentIntegrationTester:
    """Test CoderAgent integration with Natural Language → Aether Generator"""

    def __init__(self):
        self.memory_system = LyrixaMemorySystem()
        self.orchestrator = AgentOrchestrator()
        self.test_results = []
        self.successful_tests = 0
        self.total_tests = 0

    async def run_all_tests(self):
        """Run comprehensive integration test suite"""
        print("🤖 LYRIXA CODER AGENT INTEGRATION TEST SUITE")
        print("=" * 55)

        # Initialize orchestrator
        await self._initialize_system()

        # Test categories
        await self.test_agent_initialization()
        await self.test_task_creation()
        await self.test_aether_generation_tasks()
        await self.test_workflow_optimization_tasks()
        await self.test_parameter_suggestion_tasks()
        await self.test_complex_multi_step_workflows()
        await self.test_memory_integration()
        await self.test_agent_performance_metrics()

        # Summary
        self.print_test_summary()

    async def _initialize_system(self):
        """Initialize the agent orchestration system"""
        print("🔧 Initializing agent orchestration system...")

        orchestrator_context = {
            "workspace_path": os.getcwd(),
            "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "memory_system": self.memory_system,
        }

        await self.orchestrator.initialize(orchestrator_context)
        print("✅ System initialized")

    async def test_agent_initialization(self):
        """Test agent initialization and capability registration"""
        print("\n🚀 Testing Agent Initialization...")

        # Check if CoderAgent was initialized
        coder_agent = self.orchestrator.agents.get(AgentType.CODER)
        success = coder_agent is not None

        self._record_test_result(
            "Agent Initialization",
            "CoderAgent Registration",
            success,
            f"Agent available: {success}"
        )

        if coder_agent:
            capabilities = coder_agent.get_capabilities()
            expected_caps = ["aether_generation", "workflow_optimization", "parameter_suggestion"]

            for cap_name in expected_caps:
                has_capability = any(cap.name == cap_name for cap in capabilities)
                self._record_test_result(
                    "Agent Initialization",
                    f"Capability: {cap_name}",
                    has_capability,
                    f"Available: {has_capability}"
                )

    async def test_task_creation(self):
        """Test task creation and queuing"""
        print("\n📋 Testing Task Creation...")

        test_tasks = [
            {
                "agent_type": AgentType.CODER,
                "task_type": "aether_generation",
                "description": "Generate data processing workflow",
                "input_data": {"description": "Process CSV file and convert to JSON"}
            },
            {
                "agent_type": AgentType.CODER,
                "task_type": "workflow_optimization",
                "description": "Optimize existing workflow",
                "input_data": {"aether_code": "node input input\nnode output output\ninput -> output"}
            }
        ]

        for task_spec in test_tasks:
            try:
                task_id = await self.orchestrator.create_task(
                    task_spec["agent_type"],
                    task_spec["task_type"],
                    task_spec["description"],
                    task_spec["input_data"]
                )

                success = task_id is not None
                self._record_test_result(
                    "Task Creation",
                    task_spec["description"],
                    success,
                    f"Task ID: {task_id}"
                )

            except Exception as e:
                self._record_test_result(
                    "Task Creation",
                    task_spec["description"],
                    False,
                    f"Error: {str(e)}"
                )

    async def test_aether_generation_tasks(self):
        """Test .aether code generation through agent tasks"""
        print("\n⚡ Testing Aether Generation Tasks...")

        generation_tasks = [
            "Create a data processing pipeline that reads CSV and outputs JSON",
            "Build an API integration workflow for weather data",
            "Generate machine learning training pipeline with validation",
            "Create file organization workflow for photo management",
            "Build real-time analytics dashboard workflow"
        ]

        for description in generation_tasks:
            await self._test_aether_generation_task(description)

    async def _test_aether_generation_task(self, description: str):
        """Test individual aether generation task"""
        try:
            # Create task
            task_id = await self.orchestrator.create_task(
                AgentType.CODER,
                "aether_generation",
                f"Generate workflow: {description}",
                {"description": description}
            )

            # Execute task
            result = await self.orchestrator.execute_next_task()

            if result and result.get("status") == "completed":
                task_result = result.get("result", {})
                aether_code = task_result.get("aether_code", "")
                confidence = task_result.get("confidence", 0.0)

                # Check quality indicators
                has_nodes = "node " in aether_code
                has_connections = "->" in aether_code
                good_confidence = confidence > 0.5

                success = has_nodes and has_connections and good_confidence

                self._record_test_result(
                    "Aether Generation",
                    description[:40] + "...",
                    success,
                    f"Confidence: {confidence:.2f}, Nodes: {aether_code.count('node ')}"
                )
            else:
                self._record_test_result(
                    "Aether Generation",
                    description[:40] + "...",
                    False,
                    f"Task failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            self._record_test_result(
                "Aether Generation",
                description[:40] + "...",
                False,
                f"Error: {str(e)}"
            )

    async def test_workflow_optimization_tasks(self):
        """Test workflow optimization through agent tasks"""
        print("\n🔧 Testing Workflow Optimization Tasks...")

        base_workflows = [
            """node input input
  source: "data.csv"
node output output
  destination: "results.json"
input -> output""",
            """node api_call api_call
  url: "https://api.example.com"
node processor transform
  operation: "parse_json"
api_call -> processor""",
            """node data_loader input
  source: "training.csv"
node model_trainer model
  algorithm: "linear_regression"
data_loader -> model_trainer"""
        ]

        for i, workflow in enumerate(base_workflows):
            await self._test_workflow_optimization_task(f"Workflow {i+1}", workflow)

    async def _test_workflow_optimization_task(self, name: str, aether_code: str):
        """Test individual workflow optimization task"""
        try:
            # Create optimization task
            task_id = await self.orchestrator.create_task(
                AgentType.CODER,
                "workflow_optimization",
                f"Optimize {name}",
                {
                    "aether_code": aether_code,
                    "optimization_goals": ["performance", "reliability"]
                }
            )

            # Execute task
            result = await self.orchestrator.execute_next_task()

            if result and result.get("status") == "completed":
                task_result = result.get("result", {})
                optimized_code = task_result.get("optimized_code", "")
                improvements = task_result.get("improvements", [])

                # Check if optimization was applied
                has_improvements = len(improvements) > 0
                code_changed = optimized_code != aether_code

                success = has_improvements or code_changed

                self._record_test_result(
                    "Workflow Optimization",
                    name,
                    success,
                    f"Improvements: {len(improvements)}, Code changed: {code_changed}"
                )
            else:
                self._record_test_result(
                    "Workflow Optimization",
                    name,
                    False,
                    f"Task failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            self._record_test_result(
                "Workflow Optimization",
                name,
                False,
                f"Error: {str(e)}"
            )

    async def test_parameter_suggestion_tasks(self):
        """Test parameter suggestion through agent tasks"""
        print("\n⚙️ Testing Parameter Suggestion Tasks...")

        workflows_with_params = [
            """node input input
  source: "<input_source>"
  format: "<format>"
node output output
  destination: "<output_destination>"
input -> output""",
            """node api_call api_call
  url: "<api_url>"
  method: "<method>"
node processor transform
  operation: "<operation>"
api_call -> processor""",
        ]

        for i, workflow in enumerate(workflows_with_params):
            await self._test_parameter_suggestion_task(f"Parameterized workflow {i+1}", workflow)

    async def _test_parameter_suggestion_task(self, name: str, aether_code: str):
        """Test individual parameter suggestion task"""
        try:
            # Create parameter suggestion task
            task_id = await self.orchestrator.create_task(
                AgentType.CODER,
                "parameter_suggestion",
                f"Suggest parameters for {name}",
                {"aether_code": aether_code}
            )

            # Execute task
            result = await self.orchestrator.execute_next_task()

            if result and result.get("status") == "completed":
                task_result = result.get("result", {})
                filled_code = task_result.get("filled_code", "")
                suggestions = task_result.get("parameter_suggestions", [])

                # Check if parameters were suggested
                has_suggestions = len(suggestions) > 0
                placeholders_reduced = filled_code.count("<") < aether_code.count("<")

                success = has_suggestions and placeholders_reduced

                self._record_test_result(
                    "Parameter Suggestion",
                    name,
                    success,
                    f"Suggestions: {len(suggestions)}, Placeholders filled: {placeholders_reduced}"
                )
            else:
                self._record_test_result(
                    "Parameter Suggestion",
                    name,
                    False,
                    f"Task failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            self._record_test_result(
                "Parameter Suggestion",
                name,
                False,
                f"Error: {str(e)}"
            )

    async def test_complex_multi_step_workflows(self):
        """Test complex multi-step workflow generation"""
        print("\n🎯 Testing Complex Multi-Step Workflows...")

        complex_descriptions = [
            "Create end-to-end ML pipeline: load data, preprocess, train model, validate, deploy",
            "Build data quality monitoring: ingest streams, validate schemas, detect anomalies, alert",
            "Implement ETL process: extract from database, transform format, load to warehouse"
        ]

        for description in complex_descriptions:
            await self._test_complex_workflow(description)

    async def _test_complex_workflow(self, description: str):
        """Test complex workflow generation"""
        try:
            # Create complex generation task
            task_id = await self.orchestrator.create_task(
                AgentType.CODER,
                "aether_generation",
                f"Complex workflow: {description}",
                {
                    "description": description,
                    "complexity": "high",
                    "multi_step": True
                }
            )

            # Execute task
            result = await self.orchestrator.execute_next_task()

            if result and result.get("status") == "completed":
                task_result = result.get("result", {})
                aether_code = task_result.get("aether_code", "")
                complexity = task_result.get("metadata", {}).get("complexity_score", 0.0)

                # Complex workflows should have multiple nodes and high complexity
                node_count = aether_code.count("node ")
                connection_count = aether_code.count("->")

                success = node_count >= 4 and connection_count >= 3 and complexity > 0.6

                self._record_test_result(
                    "Complex Workflows",
                    description[:40] + "...",
                    success,
                    f"Nodes: {node_count}, Connections: {connection_count}, Complexity: {complexity:.2f}"
                )
            else:
                self._record_test_result(
                    "Complex Workflows",
                    description[:40] + "...",
                    False,
                    f"Task failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            self._record_test_result(
                "Complex Workflows",
                description[:40] + "...",
                False,
                f"Error: {str(e)}"
            )

    async def test_memory_integration(self):
        """Test memory system integration with agent tasks"""
        print("\n🧠 Testing Memory Integration...")

        try:
            # Store some preferences in memory
            await self.memory_system.store_memory(
                content={
                    "preferred_format": "parquet",
                    "default_output_dir": "processed_data",
                    "api_timeout": 60
                },
                context={"type": "user_preferences"},
                tags=["preferences", "defaults"],
                importance=0.9
            )

            # Create task that should use memory
            task_id = await self.orchestrator.create_task(
                AgentType.CODER,
                "aether_generation",
                "Generate workflow using my preferences",
                {"description": "Process data using my preferred settings"}
            )

            # Execute task
            result = await self.orchestrator.execute_next_task()

            if result and result.get("status") == "completed":
                task_result = result.get("result", {})
                aether_code = task_result.get("aether_code", "")

                # Check if preferences were applied (this is a simple check)
                uses_preferences = any(pref in aether_code.lower() for pref in
                                     ["parquet", "processed_data", "timeout"])

                self._record_test_result(
                    "Memory Integration",
                    "Using stored preferences",
                    uses_preferences,
                    f"Preferences applied: {uses_preferences}"
                )
            else:
                self._record_test_result(
                    "Memory Integration",
                    "Using stored preferences",
                    False,
                    f"Task failed: {result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            self._record_test_result(
                "Memory Integration",
                "Using stored preferences",
                False,
                f"Error: {str(e)}"
            )

    async def test_agent_performance_metrics(self):
        """Test agent performance tracking"""
        print("\n📊 Testing Agent Performance Metrics...")

        coder_agent = self.orchestrator.agents.get(AgentType.CODER)
        if coder_agent:
            metrics = coder_agent.performance_metrics

            # Check if metrics are being tracked
            has_completion_count = "tasks_completed" in metrics
            has_success_rate = "success_rate" in metrics

            success = has_completion_count and has_success_rate

            self._record_test_result(
                "Performance Metrics",
                "Metrics tracking",
                success,
                f"Completed: {metrics.get('tasks_completed', 0)}, Rate: {metrics.get('success_rate', 0):.2f}"
            )
        else:
            self._record_test_result(
                "Performance Metrics",
                "Metrics tracking",
                False,
                "CoderAgent not available"
            )

    def _record_test_result(self, category: str, test_name: str, success: bool, details: str):
        """Record test result"""
        self.total_tests += 1
        if success:
            self.successful_tests += 1

        self.test_results.append({
            "category": category,
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        status = "✅" if success else "❌"
        print(f"  {status} {test_name}: {details}")

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*55)
        print("🤖 CODER AGENT INTEGRATION TEST SUMMARY")
        print("="*55)

        success_rate = (self.successful_tests / self.total_tests) * 100 if self.total_tests > 0 else 0

        print(f"📊 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Successful: {self.successful_tests}")
        print(f"   Failed: {self.total_tests - self.successful_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")

        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["success"] += 1

        print(f"\n📋 Results by Category:")
        for category, stats in categories.items():
            cat_success_rate = (stats["success"] / stats["total"]) * 100
            print(f"   {category}: {stats['success']}/{stats['total']} ({cat_success_rate:.1f}%)")

        # Overall assessment
        print(f"\n🎯 Assessment:")
        if success_rate >= 90:
            print("   🌟 EXCELLENT - CoderAgent integration is working exceptionally well!")
        elif success_rate >= 75:
            print("   ✅ GOOD - Integration is working well with minor areas for improvement")
        elif success_rate >= 60:
            print("   ⚠️ FAIR - Integration needs some improvements")
        else:
            print("   ❌ NEEDS WORK - Integration requires significant improvements")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"coder_agent_integration_test_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "successful_tests": self.successful_tests,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "categories": categories,
                "detailed_results": self.test_results
            }, f, indent=2)

        print(f"\n💾 Detailed results saved to: {results_file}")


async def main():
    """Run the comprehensive integration test suite"""
    print("🚀 Starting CoderAgent Integration Test Suite...")

    tester = CoderAgentIntegrationTester()
    await tester.run_all_tests()

    print("\n🎉 Integration test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())
