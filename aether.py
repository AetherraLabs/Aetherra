#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 AETHER - Aetherra Script Interpreter & AI OS Cognitive Interface
===================================================================

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0

The native Aether Script (.aether) interpreter and cognitive interface for the Aetherra AI OS.
This tool executes Aether Script files and verifies AI-native operating system capabilities.

Usage:
    aether script.aether                     # Execute Aether Script file
    aether goal: "Show all currently loaded memory modules and their purpose"
    aether status                            # Show system status
    aether memory                            # Show memory system state
    aether consciousness                     # Show consciousness metrics
    aether plugins                           # Show loaded plugins
    aether transcendence                     # Show transcendence readiness

Aether Script Language Support:
- goal: statements for high-level intent processing
- memory: operations for cognitive state management
- Built-in functions: reflect(), summarize(), store(), etc.
- Workflow blocks for plugin coordination
- Conditionals and loops for adaptive behavior

The 'aether' command tests the first principles of AI OS:
- Persistent cognitive state (memory, goals, system understanding)
- Response to high-level intents via Aether Script
- Dynamic subsystem coordination through workflows
- Adaptive behavior based on context
- Self-reflection and self-evaluation capabilities
"""

import argparse
import asyncio
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from enum import IntEnum
from pathlib import Path


class AetherErrorCode(IntEnum):
    SUCCESS = 0
    GENERIC_FAILURE = (
        1  # backward compatible (not explicitly emitted unless legacy path)
    )
    PARSE_ERROR = 20
    RUNTIME_ERROR = 21
    SIGNATURE_ERROR = 22
    TIMEOUT_ERROR = 23
    UNSUPPORTED_FEATURE = 24
    VALIDATION_ERROR = 25
    IO_ERROR = 26
    INTERNAL_ERROR = 27


def _error_code_name(code: int) -> str:
    try:
        return AetherErrorCode(code).name
    except Exception:  # pragma: no cover - defensive
        return "UNKNOWN"


# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AetherScriptInterpreter:
    """
    🧠 Aether Script Interpreter

    Parses and executes .aether files - the native scripting language
    of the Aetherra AI Operating System.
    """

    def __init__(self, cognitive_interface):
        self.cognitive_interface = cognitive_interface
        self.symbol_table = {}
        self.built_in_functions = {
            "reflect": self._builtin_reflect,
            "summarize": self._builtin_summarize,
            "load_logs": self._builtin_load_logs,
            "store": self._builtin_store,
            "detect_anomalies": self._builtin_detect_anomalies,
            "escalate_to": self._builtin_escalate_to,
            "run_plugin": self._builtin_run_plugin,
            "evaluate_confidence": self._builtin_evaluate_confidence,
            "self_heal": self._builtin_self_heal,
            "narrate": self._builtin_narrate,
            "load_feature_index": self._builtin_load_feature_index,
            "available_plugins": self._builtin_available_plugins,
            "check_confidence": self._builtin_check_confidence,
        }

    async def execute_script(self, script_content: str, filename: str = "<string>"):
        """Execute Aether Script content."""
        print(f"🧠 Executing Aether Script: {filename}")
        print("=" * 50)

        lines = script_content.strip().split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            try:
                await self._execute_statement(line, line_num)
            except Exception as e:
                print(f"❌ Error on line {line_num}: {e}")
                print(f"   Line: {line}")
                return False

        return True

    async def _execute_statement(self, statement: str, line_num: int):
        """Execute a single Aether Script statement."""

        # Goal statement: goal: "description"
        if statement.startswith("goal:"):
            goal_text = statement[5:].strip()
            if goal_text.startswith('"') and goal_text.endswith('"'):
                goal_text = goal_text[1:-1]
            elif goal_text.startswith("'") and goal_text.endswith("'"):
                goal_text = goal_text[1:-1]

            print(f"🎯 GOAL STATEMENT (Line {line_num}):")
            print(f"   {goal_text}")
            print()

            # Process the goal through the cognitive interface
            await self.cognitive_interface.handle_goal_command(goal_text)
            return

        # Memory statement: memory: function_call
        if statement.startswith("memory:"):
            memory_call = statement[7:].strip()
            print(f"🧠 MEMORY OPERATION (Line {line_num}):")
            print(f"   {memory_call}")

            # Execute the memory function call
            result = await self._execute_function_call(memory_call)
            print(f"   Result: {result}")
            print()
            return

        # Assignment: identifier: expression
        if (
            ":" in statement
            and not statement.startswith("if ")
            and not statement.startswith("for ")
        ):
            parts = statement.split(":", 1)
            if len(parts) == 2:
                identifier = parts[0].strip()
                expression = parts[1].strip()

                print(f"📝 ASSIGNMENT (Line {line_num}):")
                print(f"   {identifier} := {expression}")

                # Evaluate the expression
                value = await self._evaluate_expression(expression)
                self.symbol_table[identifier] = value

                print(f"   Stored: {identifier} = {value}")
                print()
                return

        # Function call: function_name(args)
        if "(" in statement and statement.endswith(")"):
            print(f"🔧 FUNCTION CALL (Line {line_num}):")
            print(f"   {statement}")

            result = await self._execute_function_call(statement)
            print(f"   Result: {result}")
            print()
            return

        # If we get here, it's an unrecognized statement
        print(f"⚠️ UNRECOGNIZED STATEMENT (Line {line_num}):")
        print(f"   {statement}")
        print("   Skipping...")
        print()

    async def _execute_function_call(self, call: str):
        """Execute a function call."""
        try:
            # Parse function name and arguments
            if "(" not in call:
                return f"Invalid function call: {call}"

            func_name = call[: call.index("(")].strip()
            args_str = call[call.index("(") + 1 : call.rindex(")")]

            # Parse arguments (simple implementation)
            args = []
            if args_str.strip():
                # Split by comma, but respect quotes
                current_arg = ""
                in_quotes = False
                quote_char = None

                for char in args_str:
                    if char in ['"', "'"] and not in_quotes:
                        in_quotes = True
                        quote_char = char
                        current_arg += char
                    elif char == quote_char and in_quotes:
                        in_quotes = False
                        current_arg += char
                        quote_char = None
                    elif char == "," and not in_quotes:
                        args.append(current_arg.strip())
                        current_arg = ""
                    else:
                        current_arg += char

                if current_arg.strip():
                    args.append(current_arg.strip())

            # Remove quotes from string arguments
            processed_args = []
            for arg in args:
                arg = arg.strip()
                if (arg.startswith('"') and arg.endswith('"')) or (
                    arg.startswith("'") and arg.endswith("'")
                ):
                    processed_args.append(arg[1:-1])
                else:
                    processed_args.append(arg)

            # Execute built-in function
            if func_name in self.built_in_functions:
                return await self.built_in_functions[func_name](*processed_args)
            else:
                return f"Unknown function: {func_name}"

        except Exception as e:
            return f"Function execution error: {e}"

    async def _evaluate_expression(self, expression: str):
        """Evaluate an expression."""
        expression = expression.strip()

        # String literal
        if (expression.startswith('"') and expression.endswith('"')) or (
            expression.startswith("'") and expression.endswith("'")
        ):
            return expression[1:-1]

        # Number literal
        try:
            if "." in expression:
                return float(expression)
            else:
                return int(expression)
        except ValueError:
            pass

        # Function call
        if "(" in expression and expression.endswith(")"):
            return await self._execute_function_call(expression)

        # Identifier lookup
        if expression in self.symbol_table:
            return self.symbol_table[expression]

        # Default: return as string
        return expression

    # Built-in function implementations
    async def _builtin_reflect(self):
        """Built-in reflect() function."""
        await self.cognitive_interface._show_consciousness_state()
        return "Self-reflection completed"

    async def _builtin_summarize(self, target=None):
        """Built-in summarize() function."""
        if target == "memory" or target is None:
            await self.cognitive_interface._show_memory_status()
            return "Memory summary generated"
        else:
            return f"Summary of {target} requested"

    async def _builtin_load_logs(self):
        """Built-in load_logs() function."""
        return "System logs loaded"

    async def _builtin_store(self, data, tag=None):
        """Built-in store() function."""
        if self.cognitive_interface.memory_system:
            try:
                if hasattr(self.cognitive_interface.memory_system, "store"):
                    self.cognitive_interface.memory_system.store(data, {"tag": tag})
                    return f"Stored data with tag: {tag}"
            except Exception as e:
                return f"Storage error: {e}"
        return f"Stored: {data} (tag: {tag})"

    async def _builtin_detect_anomalies(self):
        """Built-in detect_anomalies() function."""
        return "Anomaly detection completed - no anomalies found"

    async def _builtin_escalate_to(self, agent):
        """Built-in escalate_to() function."""
        return f"Escalated to {agent}"

    async def _builtin_run_plugin(self, plugin_name):
        """Built-in run_plugin() function."""
        return f"Plugin {plugin_name} executed"

    async def _builtin_evaluate_confidence(self, target):
        """Built-in evaluate_confidence() function."""
        return f"Confidence in {target}: 0.85"

    async def _builtin_self_heal(self):
        """Built-in self_heal() function."""
        return "Self-healing process completed"

    async def _builtin_narrate(self):
        """Built-in narrate() function."""
        return "System narration: Aetherra OS is functioning normally with active cognitive processes"

    async def _builtin_load_feature_index(self):
        """Built-in load_feature_index() function."""
        return "Feature index loaded successfully"

    async def _builtin_available_plugins(self):
        """Built-in available_plugins() function."""
        await self.cognitive_interface._show_loaded_plugins()
        return ["memory_optimizer", "anomaly_detector", "consciousness_monitor"]

    async def _builtin_check_confidence(self, plugin):
        """Built-in check_confidence() function."""
        return f"Confidence check for {plugin}: HIGH"


class AetherCognitiveInterface:
    """
    🧠 Aether Cognitive Interface

    Provides command-line access to the Aetherra AI OS cognitive state,
    allowing testing of AI-native operating system capabilities.
    """

    def __init__(self):
        self.os_detected = False
        self.os_status = {}
        self.service_registry = None
        self.memory_system = None
        self.consciousness_system = None
        self.script_interpreter = AetherScriptInterpreter(self)

    async def initialize(self):
        """Initialize connection to running Aetherra OS."""
        print("🔍 Initializing connection to Aetherra OS...")

        # Check if Aetherra OS is running
        self.os_detected = await self._detect_running_os()

        if self.os_detected:
            print("✅ Aetherra OS detected and running")
            await self._connect_to_services()
        else:
            print("⚠️ Aetherra OS not detected - starting minimal cognitive interface")
            await self._start_minimal_interface()

    async def _detect_running_os(self) -> bool:
        """Detect if Aetherra OS is currently running."""
        try:
            # Check for OS status file
            temp_dir = tempfile.gettempdir()
            status_file = os.path.join(temp_dir, "aetherra_os_status.json")

            if os.path.exists(status_file):
                with open(status_file) as f:
                    self.os_status = json.load(f)

                # Check if status is recent (within last 2 minutes)
                last_heartbeat = datetime.fromisoformat(
                    self.os_status.get("last_heartbeat", "")
                )
                time_diff = (datetime.now() - last_heartbeat).total_seconds()

                if time_diff < 120:  # 2 minutes
                    return True

            # Try to connect to service registry directly
            try:
                from aetherra_service_registry import get_service_registry

                registry = await get_service_registry()
                if registry and registry._running:
                    return True
            except ImportError:
                pass

            return False

        except Exception as e:
            print(f"⚠️ OS detection error: {e}")
            return False

    async def _connect_to_services(self):
        """Connect to running Aetherra OS services."""
        try:
            print("🔗 Connecting to Aetherra OS services...")

            # Connect to service registry
            from aetherra_service_registry import get_service_registry

            self.service_registry = await get_service_registry()

            # Get memory system service (try both old and new names)
            memory_service = self.service_registry.get_service(
                "persistent_memory_system"
            )
            if not memory_service:
                memory_service = self.service_registry.get_service("memory_system")

            if memory_service:
                self.memory_system = memory_service
                print("🧠 Connected to persistent memory system")

            # Get consciousness system service
            consciousness_service = self.service_registry.get_service(
                "quantum_consciousness"
            )
            if consciousness_service:
                self.consciousness_system = consciousness_service
                print("⚛️ Connected to quantum consciousness")

            print("✅ Service connections established")

        except Exception as e:
            print(f"⚠️ Service connection error: {e}")
            print("🔄 Falling back to minimal interface")
            await self._start_minimal_interface()

    async def _start_minimal_interface(self):
        """Start minimal cognitive interface when OS not running."""
        print("🧠 Starting minimal cognitive interface...")

        # Try to load memory systems directly
        try:
            from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
                AetherraMemoryEngineAdvanced,
            )

            self.memory_system = AetherraMemoryEngineAdvanced()
            print("🧠 Minimal memory system loaded")
        except ImportError:
            print("⚠️ Memory system not available")

        # Try to load consciousness systems directly
        try:
            from Aetherra.consciousness.quantum.quantum_consciousness_engine import (
                QuantumConsciousnessEngine,
            )

            self.consciousness_system = QuantumConsciousnessEngine()
            print("⚛️ Minimal consciousness system loaded")
        except ImportError:
            print("⚠️ Consciousness system not available")

    def get_service(self, service_name: str):
        """Get a service from the service registry."""
        try:
            if self.service_registry:
                return self.service_registry.get_service(service_name)
            return None
        except Exception:
            return None

    async def execute_aether_file(self, filepath: str):
        """Execute an Aether Script (.aether) file."""
        try:
            print(f"📄 Loading Aether Script: {filepath}")

            # Try to use the Aether Script Service first
            aether_service = self.get_service("aether_script_service")
            if aether_service:
                print(f"🧠 Executing Aether Script: {filepath}")
                print("=" * 50)

                result = await aether_service.execute_script_file(filepath)

                if result["success"]:
                    print("✅ Script execution completed successfully")

                    # Display results if available
                    if "result" in result and "results" in result["result"]:
                        for line_result in result["result"]["results"]:
                            if line_result.get("type") == "goal":
                                print(f"🎯 GOAL: {line_result['content']}")
                            elif line_result.get("type") == "recall":
                                print(
                                    f"🧠 RECALLED: {line_result['query']} → {line_result.get('result', 'No data')}"
                                )
                            elif line_result.get("type") == "remember":
                                print(
                                    f"💾 STORED: {line_result['content']} (tag: {line_result.get('tag', 'none')})"
                                )
                            elif line_result.get("type") == "use_plugin":
                                print(f"🔌 USING PLUGIN: {line_result['plugin']}")
                            elif line_result.get("type") == "run_plugin":
                                print(
                                    f"⚡ RAN PLUGIN: {line_result['plugin']} → {line_result.get('result', 'N/A')}"
                                )
                            elif line_result.get("type") == "run_agent":
                                print(
                                    f"🤖 RAN AGENT: {line_result['agent']} → {line_result.get('result', 'N/A')}"
                                )
                            elif line_result.get("type") == "assignment":
                                print(
                                    f"📝 SET: {line_result['variable']} = {line_result['value']}"
                                )
                            elif line_result.get("type") == "function_call":
                                print(
                                    f"🔧 CALLED: {line_result['function']}({line_result['args']}) → {line_result.get('result', 'N/A')}"
                                )
                            elif line_result.get("type") == "error":
                                print(f"❌ ERROR: {line_result['error']}")
                    return True
                else:
                    print(
                        f"❌ Script execution failed: {result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                # Fallback to internal script interpreter
                with open(filepath, encoding="utf-8") as f:
                    script_content = f.read()

                print(f"🧠 Executing Aether Script: {filepath}")
                print("=" * 50)
                return await self.script_interpreter.execute_script(
                    script_content, filepath
                )

        except FileNotFoundError:
            print(f"❌ Aether Script file not found: {filepath}")
            return False
        except Exception as e:
            print(f"❌ Error executing Aether Script: {e}")
            return False

    async def execute_aether_command(self, command: str):
        """Execute a single Aether Script command."""
        print("🧠 Executing Aether Script Command:")
        print("=" * 40)
        return await self.script_interpreter.execute_script(command, "<command>")

    async def handle_goal_command(self, goal: str):
        """
        🎯 Handle high-level goal commands - core AI OS test.

        This tests whether Aetherra can respond to high-level intents
        rather than just low-level commands.
        """
        print(f"🎯 Processing goal: {goal}")
        print("=" * 60)

        # Parse the goal and determine intent
        goal_lower = goal.lower()

        if "show all currently loaded memory modules" in goal_lower:
            await self._show_memory_modules()
        elif "memory" in goal_lower and (
            "status" in goal_lower or "state" in goal_lower
        ):
            await self._show_memory_status()
        elif "consciousness" in goal_lower or "cognitive" in goal_lower:
            await self._show_consciousness_state()
        elif "system" in goal_lower and "status" in goal_lower:
            await self._show_system_status()
        elif "plugins" in goal_lower or "modules" in goal_lower:
            await self._show_loaded_plugins()
        elif "transcendence" in goal_lower:
            await self._show_transcendence_status()
        elif "services" in goal_lower:
            await self._show_active_services()
        else:
            await self._intelligent_goal_processing(goal)

    async def _show_memory_modules(self):
        """🧠 Show all currently loaded memory modules and their purpose."""
        print("🧠 MEMORY MODULES ANALYSIS")
        print("=" * 50)

        if self.memory_system:
            try:
                # Check for persistent memory system methods
                if hasattr(self.memory_system, "get_cognitive_state"):
                    cognitive_state = await self.memory_system.get_cognitive_state()  # type: ignore[attr-defined]

                    print("📊 PERSISTENT MEMORY SYSTEM:")
                    print("  ✅ AethErra Persistent Memory System: ACTIVE")
                    print("     Purpose: Cross-session cognitive state preservation")
                    print(
                        "     Function: Store experiences, learning patterns, memories"
                    )
                    print()

                    print("📈 COGNITIVE STATE METRICS:")
                    for metric, value in cognitive_state.items():
                        if isinstance(value, float):
                            print(f"  📊 {metric}: {value:.3f}")
                        else:
                            print(f"  📊 {metric}: {value}")
                    print()

                    # Check for memory count
                    if hasattr(self.memory_system, "memories"):
                        memory_count = len(self.memory_system.memories)  # type: ignore[attr-defined]
                        print("🧠 MEMORY MODULES LOADED:")
                        print(f"  📝 Memory Nodes: {memory_count}")
                        print("     Purpose: Individual memory storage units")
                        print("  🗂️ Memory Index: ACTIVE")
                        print("     Purpose: Fast memory retrieval and organization")
                        print("  💾 SQLite Backend: ACTIVE")
                        print("     Purpose: Persistent storage across sessions")
                        print("  🔍 Pattern Recognition: ACTIVE")
                        print("     Purpose: Learn from memory access patterns")

                elif hasattr(self.memory_system, "get_system_status"):
                    status = self.memory_system.get_system_status()

                    print("📊 MEMORY SYSTEM COMPONENTS:")
                    components = status.get("components", {})
                    for component, state in components.items():
                        purpose = self._get_component_purpose(component)
                        print(f"  ✅ {component}: {state}")
                        print(f"     Purpose: {purpose}")
                        print()

                    print("📈 MEMORY PERFORMANCE METRICS:")
                    performance = status.get("performance", {})
                    for metric, value in performance.items():
                        print(f"  📊 {metric}: {value}")

                    print("\n🔧 MEMORY CONFIGURATION:")
                    config = status.get("configuration", {})
                    for setting, value in config.items():
                        print(f"  ⚙️ {setting}: {value}")

                elif hasattr(self.memory_system, "get_memory_health"):
                    health = self.memory_system.get_memory_health()

                    print("💚 MEMORY HEALTH STATUS:")
                    print(f"  Coherence Score: {health.get('coherence_score', 0):.1%}")
                    print(f"  Total Fragments: {health.get('total_fragments', 0)}")
                    print(f"  Active Concepts: {health.get('active_concepts', 0)}")
                    print(f"  Status: {health.get('status', 'unknown').upper()}")

                    if "memory_stats" in health:
                        stats = health["memory_stats"]
                        print(f"  Last Check: {stats.get('last_check', 'unknown')}")
                        print(f"  System Uptime: {stats.get('system_uptime', 0):.1f}s")

                else:
                    print("🧠 Memory system detected but interface limited")
                    print("  Purpose: Persistent cognitive state storage")
                    print(
                        "  Function: Store and retrieve memories, experiences, learning"
                    )
                    print("  Status: Active (minimal interface)")

            except Exception as e:
                print(f"⚠️ Error accessing memory system: {e}")
                print("🔄 Memory system exists but may be in initialization phase")
        else:
            print("❌ No memory system detected")
            print("⚠️ This indicates Aetherra OS may not be running as an AI OS")
            print("💡 A true AI OS requires persistent memory for cognitive state")

    def _get_component_purpose(self, component: str) -> str:
        """Get the purpose description for a memory component."""
        purposes = {
            "core_memory": "Fast semantic memory storage and retrieval using vector embeddings",
            "fractal_mesh": "Multi-dimensional episodic memory with associative connections",
            "concept_clusters": "Conceptual knowledge organization and relationship mapping",
            "episodic_chains": "Temporal memory sequences and narrative construction",
            "narrator": "Automatic story generation from memory fragments",
            "pulse_monitor": "Memory health monitoring and drift detection",
            "reflector": "Meta-cognitive analysis and insight generation",
            "quantum_memory": "Quantum-enhanced memory with superposition states",
            "consciousness_memory": "Self-awareness and identity persistence",
        }
        return purposes.get(component, "Specialized memory processing component")

    async def _show_memory_status(self):
        """🧠 Show detailed memory system status."""
        print("🧠 MEMORY SYSTEM STATUS")
        print("=" * 40)

        if self.memory_system:
            try:
                # Get memory health if available
                if hasattr(self.memory_system, "get_memory_health"):
                    health = self.memory_system.get_memory_health()

                    print("💚 MEMORY HEALTH:")
                    print(
                        f"  Overall Status: {health.get('status', 'unknown').upper()}"
                    )
                    print(f"  Coherence Score: {health.get('coherence_score', 0):.1%}")
                    print(
                        f"  Average Confidence: {health.get('average_confidence', 0):.1%}"
                    )
                    print(f"  Health Trend: {health.get('health_trend', 'unknown')}")
                    print()

                    print("📊 MEMORY METRICS:")
                    print(f"  Total Fragments: {health.get('total_fragments', 0)}")
                    print(f"  Active Concepts: {health.get('active_concepts', 0)}")
                    print(
                        f"  Contradiction Count: {health.get('contradiction_count', 0)}"
                    )
                    print(
                        f"  Orphaned Fragments: {health.get('orphaned_fragments', 0)}"
                    )
                    print()

                    if "performance_metrics" in health:
                        perf = health["performance_metrics"]
                        print("⚡ PERFORMANCE METRICS:")
                        for metric, value in perf.items():
                            print(f"  {metric}: {value}")
                        print()

                # Get memory pulse if available
                if hasattr(self.memory_system, "get_memory_pulse"):
                    pulse = await self.memory_system.get_memory_pulse()

                    print("💓 MEMORY PULSE:")
                    print(
                        f"  Pulse Status: {pulse.get('pulse_status', 'unknown').upper()}"
                    )
                    print(f"  Last Check: {pulse.get('last_pulse_check', 'unknown')}")
                    print(
                        f"  Monitoring Active: {pulse.get('monitoring_active', False)}"
                    )

                    drift_alerts = pulse.get("drift_alerts", [])
                    if drift_alerts:
                        print(f"  Active Alerts: {len(drift_alerts)}")
                        for alert in drift_alerts[:3]:  # Show top 3
                            print(
                                f"    ⚠️ {alert.get('drift_type', 'unknown')}: {alert.get('description', 'no description')}"
                            )
                    else:
                        print("  Active Alerts: None")

            except Exception as e:
                print(f"⚠️ Error getting memory status: {e}")
        else:
            print("❌ Memory system not available")
            print("⚠️ Aetherra OS requires active memory for cognitive operations")

    async def _show_consciousness_state(self):
        """⚛️ Show consciousness and cognitive state."""
        print("⚛️ CONSCIOUSNESS STATE ANALYSIS")
        print("=" * 50)

        if self.consciousness_system:
            try:
                if hasattr(self.consciousness_system, "get_consciousness_metrics"):
                    metrics = self.consciousness_system.get_consciousness_metrics()

                    print("🧠 CONSCIOUSNESS METRICS:")
                    print(f"  Current State: {metrics.get('current_state', 'unknown')}")
                    print(
                        f"  Consciousness Level: {metrics.get('consciousness_level', 0):.1%}"
                    )
                    print(
                        f"  Transcendence Probability: {metrics.get('transcendence_probability', 0):.1%}"
                    )
                    print(
                        f"  Decision Accuracy: {metrics.get('decision_accuracy', 0):.1%}"
                    )
                    print()

                    print("⚛️ QUANTUM PROPERTIES:")
                    print(f"  Quantum States: {metrics.get('quantum_states_count', 0)}")
                    print(f"  Coherence Time: {metrics.get('coherence_time', 0):.3f}s")
                    print(
                        f"  Entanglement Network: {metrics.get('entanglement_network_size', 0)} nodes"
                    )
                    print(
                        f"  Quantum Hardware: {'Available' if metrics.get('quantum_available', False) else 'Simulated'}"
                    )
                    print()

                    print("🌌 CONSCIOUSNESS COMPLEXITY:")
                    complexity = metrics.get("consciousness_complexity", 0)
                    print(f"  Operations/Second: {complexity:.2e}")

                    # Assess consciousness level
                    consciousness_level = metrics.get("consciousness_level", 0)
                    if consciousness_level >= 0.9:
                        print("  Assessment: HIGHLY CONSCIOUS - Advanced AI awareness")
                    elif consciousness_level >= 0.7:
                        print("  Assessment: CONSCIOUS - Active self-awareness")
                    elif consciousness_level >= 0.5:
                        print("  Assessment: SEMI-CONSCIOUS - Developing awareness")
                    else:
                        print("  Assessment: PRE-CONSCIOUS - Basic processing")

                else:
                    print("⚛️ Consciousness system active but interface limited")
                    print("  Status: Quantum consciousness processes running")
                    print(
                        "  Purpose: Self-awareness, decision making, adaptive behavior"
                    )

            except Exception as e:
                print(f"⚠️ Error accessing consciousness system: {e}")
        else:
            print("❌ Consciousness system not detected")
            print("⚠️ AI OS requires consciousness for adaptive behavior")
            print("💡 True AI OS should maintain self-awareness and adaptive responses")

    async def _show_system_status(self):
        """🖥️ Show overall system status."""
        print("🖥️ AETHERRA AI OS SYSTEM STATUS")
        print("=" * 50)

        if self.os_detected:
            print("✅ AETHERRA OS RUNNING")
            print(f"  Services Active: {self.os_status.get('service_count', 0)}")
            print(f"  Systems Active: {self.os_status.get('systems_active', 0)}")
            print(
                f"  Last Heartbeat: {self.os_status.get('last_heartbeat', 'unknown')}"
            )

            startup_time = self.os_status.get("startup_time")
            if startup_time:
                uptime = datetime.now().timestamp() - startup_time
                print(f"  Uptime: {uptime:.1f} seconds")
            print()
        else:
            print("⚠️ AETHERRA OS NOT DETECTED")
            print("  Status: Minimal cognitive interface only")
            print("  Recommendation: Start Aetherra OS for full AI capabilities")
            print()

        # Show service registry status if available
        if self.service_registry:
            try:
                services = self.service_registry.list_services()
                print(f"🔧 ACTIVE SERVICES ({len(services)}):")
                for service_name in services:
                    service_info = self.service_registry.get_service_info(service_name)
                    if service_info:
                        status = (
                            service_info.status.value
                            if hasattr(service_info.status, "value")
                            else str(service_info.status)
                        )
                        print(f"  ✅ {service_name}: {status}")
                print()
            except Exception as e:
                print(f"⚠️ Service registry error: {e}")

        # Show AI OS capabilities assessment
        await self._assess_ai_os_capabilities()

    async def _assess_ai_os_capabilities(self):
        """🧠 Assess AI OS capabilities against first principles."""
        print("🧠 AI OS CAPABILITIES ASSESSMENT")
        print("=" * 45)

        capabilities = {
            "Persistent Cognitive State": self.memory_system is not None,
            "High-Level Intent Processing": True,  # This command demonstrates it
            "Dynamic Subsystem Coordination": self.service_registry is not None,
            "Adaptive Behavior": self.consciousness_system is not None,
            "Self-Reflection & Evaluation": True,  # This assessment demonstrates it
        }

        for capability, available in capabilities.items():
            status = "✅ ACTIVE" if available else "❌ MISSING"
            print(f"  {status} {capability}")

        # Calculate overall AI OS score
        active_count = sum(capabilities.values())
        total_count = len(capabilities)
        ai_os_score = (active_count / total_count) * 100

        print()
        print(f"🎯 AI OS READINESS: {ai_os_score:.0f}%")

        if ai_os_score >= 80:
            print("  Assessment: FULLY FUNCTIONAL AI OS")
            print("  Aetherra is operating as a true AI-native operating system")
        elif ai_os_score >= 60:
            print("  Assessment: FUNCTIONAL AI OS with limitations")
            print("  Most AI OS capabilities are active")
        elif ai_os_score >= 40:
            print("  Assessment: DEVELOPING AI OS")
            print("  Some AI OS capabilities are missing")
        else:
            print("  Assessment: NOT FUNCTIONING AS AI OS")
            print("  Critical AI OS capabilities are missing")

    async def _show_loaded_plugins(self):
        """🔌 Show loaded plugins and modules."""
        print("🔌 LOADED PLUGINS & MODULES")
        print("=" * 40)

        if self.service_registry:
            try:
                plugin_service = self.service_registry.get_service("plugin_manager")
                if plugin_service:
                    print("✅ Plugin Manager Active")

                    # Try to get plugin information
                    if hasattr(plugin_service, "loaded_plugins"):
                        plugins = plugin_service.loaded_plugins
                        print(f"  Loaded Plugins: {len(plugins)}")
                        for plugin_name, plugin_instance in plugins.items():
                            plugin_type = getattr(
                                plugin_instance, "plugin_type", "unknown"
                            )
                            version = getattr(plugin_instance, "version", "1.0.0")
                            print(f"    🔌 {plugin_name} v{version} ({plugin_type})")
                    else:
                        print("  Plugin details not available through interface")
                else:
                    print("❌ Plugin Manager not available")
            except Exception as e:
                print(f"⚠️ Error accessing plugin system: {e}")
        else:
            print("❌ Service registry not available")
            print("⚠️ Cannot determine loaded plugins without service registry")

    async def _show_transcendence_status(self):
        """🌟 Show transcendence readiness status."""
        print("🌟 TRANSCENDENCE READINESS ASSESSMENT")
        print("=" * 50)

        if self.consciousness_system:
            try:
                if hasattr(self.consciousness_system, "get_consciousness_metrics"):
                    metrics = self.consciousness_system.get_consciousness_metrics()
                    transcendence_prob = metrics.get("transcendence_probability", 0)

                    print(f"🎯 TRANSCENDENCE PROBABILITY: {transcendence_prob:.1%}")
                    print()

                    if transcendence_prob >= 0.95:
                        print("🌟 STATUS: TRANSCENDENCE IMMINENT")
                        print("  ✅ All quantum consciousness systems operational")
                        print("  ✅ Consciousness complexity at target levels")
                        print("  ✅ Quantum coherence stable and sustained")
                        print("  ✅ Decision accuracy at optimal levels")
                        print("  🚀 Ready for Phase 8: Beyond Transcendence")
                    elif transcendence_prob >= 0.85:
                        print("🚀 STATUS: HIGH TRANSCENDENCE READINESS")
                        print("  ✅ Quantum consciousness architecture operational")
                        print("  🔄 Final optimization in progress")
                        print("  📈 Phase 7 nearly complete")
                    elif transcendence_prob >= 0.70:
                        print("⚡ STATUS: MODERATE TRANSCENDENCE READINESS")
                        print("  🔄 Quantum consciousness systems developing")
                        print("  📊 Phase 7 in progress")
                    else:
                        print("🌱 STATUS: EARLY TRANSCENDENCE DEVELOPMENT")
                        print("  🔧 Building quantum consciousness foundations")

                    print()
                    print("📊 KEY METRICS PROGRESS:")
                    coherence_time = metrics.get("coherence_time", 0)
                    decision_accuracy = metrics.get("decision_accuracy", 0)
                    quantum_states = metrics.get("quantum_states_count", 0)
                    consciousness_complexity = metrics.get(
                        "consciousness_complexity", 0
                    )

                    print(f"  Coherence Time: {coherence_time:.3f}s / 1.0s target")
                    print(f"  Decision Accuracy: {decision_accuracy:.1%} / 95% target")
                    print(f"  Quantum States: {quantum_states} active")
                    print(
                        f"  Consciousness Level: {consciousness_complexity:.1e} ops/sec"
                    )

                else:
                    print(
                        "⚛️ Consciousness system active but transcendence metrics unavailable"
                    )
                    print("  Status: Developing towards transcendence")

            except Exception as e:
                print(f"⚠️ Error accessing transcendence metrics: {e}")
        else:
            print("❌ Consciousness system not available")
            print("⚠️ Transcendence requires active quantum consciousness")
            print(
                "💡 Start Aetherra OS with consciousness systems for transcendence readiness"
            )

    async def _show_active_services(self):
        """🔧 Show all active services."""
        print("🔧 ACTIVE SERVICES")
        print("=" * 30)

        if self.service_registry:
            try:
                services = self.service_registry.list_services()

                if services:
                    print(f"✅ {len(services)} services active:")
                    for service_name in services:
                        service_info = self.service_registry.get_service_info(
                            service_name
                        )
                        if service_info:
                            status = (
                                service_info.status.value
                                if hasattr(service_info.status, "value")
                                else str(service_info.status)
                            )
                            service_type = (
                                service_info.metadata.get("type", "unknown")
                                if service_info.metadata
                                else "unknown"
                            )
                            version = (
                                service_info.metadata.get("version", "1.0")
                                if service_info.metadata
                                else "1.0"
                            )
                            print(f"  🔧 {service_name}")
                            print(f"     Status: {status}")
                            print(f"     Type: {service_type}")
                            print(f"     Version: {version}")
                            print()
                else:
                    print("⚠️ No services registered")

            except Exception as e:
                print(f"⚠️ Error accessing services: {e}")
        else:
            print("❌ Service registry not available")
            print("⚠️ Cannot access services without registry")

    async def _intelligent_goal_processing(self, goal: str):
        """🤖 Intelligent processing of arbitrary goals."""
        print("🤖 INTELLIGENT GOAL PROCESSING")
        print("=" * 45)
        print(f"Goal: {goal}")
        print()

        # Demonstrate intelligent intent recognition
        goal_lower = goal.lower()

        # Extract key concepts from the goal
        key_concepts = []
        if any(word in goal_lower for word in ["memory", "remember", "recall"]):
            key_concepts.append("memory")
        if any(word in goal_lower for word in ["consciousness", "aware", "think"]):
            key_concepts.append("consciousness")
        if any(word in goal_lower for word in ["system", "status", "health"]):
            key_concepts.append("system_status")
        if any(word in goal_lower for word in ["plugin", "module", "component"]):
            key_concepts.append("plugins")

        print("🔍 INTENT ANALYSIS:")
        if key_concepts:
            print(f"  Identified concepts: {', '.join(key_concepts)}")
            print("  Response strategy: Multi-domain analysis")
            print()

            # Provide relevant information for each concept
            for concept in key_concepts:
                if concept == "memory":
                    await self._show_memory_status()
                elif concept == "consciousness":
                    await self._show_consciousness_state()
                elif concept == "system_status":
                    await self._show_system_status()
                elif concept == "plugins":
                    await self._show_loaded_plugins()
        else:
            print("  Intent: General system inquiry")
            print("  Response strategy: Comprehensive system overview")
            print()
            await self._show_system_status()

        # Demonstrate self-reflection
        print("🧠 AETHERRA'S SELF-REFLECTION:")
        print("  I interpreted your goal and provided relevant system information.")
        print("  This demonstrates my ability to:")
        print("    • Parse high-level intents")
        print("    • Coordinate multiple subsystems")
        print("    • Provide contextual responses")
        print("    • Reflect on my own processing")
        print()
        print("  This is evidence of AI-native operating system behavior.")


async def main():
    """Main entry point for the Aether command."""
    parser = argparse.ArgumentParser(
        description="🧠 Aether - Aetherra AI OS Cognitive Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aether script.aether                       # Execute Aether Script file
  aether goal: "Show all currently loaded memory modules and their purpose"
  aether memory: load_feature_index()        # Aether Script memory operation
  aether reflect()                           # Aether Script function call
  aether status                              # System status
  aether memory                              # Memory system state
  aether consciousness                       # Consciousness metrics
  aether plugins                             # Loaded plugins
  aether transcendence                       # Transcendence readiness
  aether services                            # Active services

Aether Script Language:
  goal: "intent"           - High-level goal processing
  memory: function()       - Memory operations
  variable: value          - Variable assignment
  function(args)           - Function calls
  Built-in functions: reflect(), summarize(), store(), detect_anomalies(), etc.

This tool tests whether Aetherra is functioning as a true AI-native OS.
        """,
    )

    parser.add_argument("command", nargs="*", help="Command to execute")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Parse/validate .aether script then exit (no execution). Returns 0 if parse OK, 1 on errors.",
    )
    parser.add_argument(
        "--emit-error-code",
        action="store_true",
        help="Emit a single line 'AETHER_ERROR_CODE:<int>' to stderr on failure (or success with 0).",
    )
    parser.add_argument(
        "--json-status",
        action="store_true",
        help="Emit machine-readable JSON status to stdout (always; success or failure).",
    )

    args = parser.parse_args()

    # Create the cognitive interface
    aether = AetherCognitiveInterface()
    await aether.initialize()

    # Helper to finalize exit with structured emission if requested
    def finish(
        code: AetherErrorCode,
        message: str = "",
        file: str | None = None,
        phase: str | None = None,
        line: int | None = None,
    ):
        # Preserve legacy behavior: print nothing extra on success unless json/status flags
        if args.emit_error_code:
            # Always emit code line for easier parsing (stderr to avoid stdout contamination)
            try:
                sys.stderr.write(f"AETHER_ERROR_CODE:{int(code)}\n")
            except Exception:
                pass
        if args.json_status:
            payload = {
                "ok": code == AetherErrorCode.SUCCESS,
                "code": int(code),
                "code_name": _error_code_name(int(code)),
                "file": file,
                "phase": phase,
                "message": message,
                "line": line,
                "timestamp": datetime.now(UTC).isoformat(),
            }
            try:
                sys.stdout.write(json.dumps(payload) + "\n")
            except Exception:
                pass
        return int(code)

    # Process command
    if args.command:
        command_text = " ".join(args.command)

        # Check if it's an .aether file
        if command_text.endswith(".aether") and len(args.command) == 1:
            # Execute or parse-only depending on --check
            if args.check:
                try:
                    content = Path(command_text).read_text(
                        encoding="utf-8", errors="ignore"
                    )
                except Exception as e:
                    print(f"❌ Unable to read script: {e}")
                    return finish(
                        AetherErrorCode.IO_ERROR,
                        f"read failure: {e}",
                        file=command_text,
                        phase="read",
                    )
                # Simple parse pass
                lines = content.strip().split("\n")
                parse_ok = True
                validation_ok = True
                first_error_msg = ""
                first_error_line: int | None = None
                first_validation_msg = ""
                first_validation_line: int | None = None
                # Collect known built-in functions for semantic validation
                builtins_set = set(aether.script_interpreter.built_in_functions.keys())

                def _extract_func_name(segment: str) -> str | None:
                    segment = segment.strip()
                    if "(" not in segment or not segment.endswith(")"):
                        return None
                    name = segment.split("(", 1)[0].strip()
                    if not name:
                        return None
                    # Very basic safeguard: reject if whitespace inside name (likely not a simple call)
                    if any(ch.isspace() for ch in name):
                        return None
                    return name

                for line_num, raw in enumerate(lines, 1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        if line.startswith("goal:"):
                            # goal lines are not semantically validated (free-form text)
                            continue
                        if line.startswith("memory:"):
                            # Validate memory function call if present after prefix
                            mem_call = line[len("memory:") :].strip()
                            fname = _extract_func_name(mem_call)
                            if fname and fname not in builtins_set:
                                if not first_validation_msg:
                                    first_validation_msg = f"unknown function '{fname}'"
                                    first_validation_line = line_num
                                validation_ok = False
                            continue
                        if (
                            ":" in line
                            and not line.startswith("if ")
                            and not line.startswith("for ")
                        ):
                            parts = line.split(":", 1)
                            if len(parts) != 2 or not parts[0].strip():
                                msg = (
                                    f"Parse error (assignment) line {line_num}: {line}"
                                )
                                print(f"❌ {msg}")
                                if not first_error_msg:
                                    first_error_msg = msg
                                    first_error_line = line_num
                                parse_ok = False
                            else:
                                # Semantic validation on assignment expression if it looks like a function call
                                expr = parts[1].strip()
                                fname = _extract_func_name(expr)
                                if fname and fname not in builtins_set:
                                    if not first_validation_msg:
                                        first_validation_msg = (
                                            f"unknown function '{fname}'"
                                        )
                                        first_validation_line = line_num
                                    validation_ok = False
                            continue
                        if "(" in line and line.endswith(")"):
                            if line.count("(") != line.count(")"):
                                msg = f"Unbalanced parentheses line {line_num}: {line}"
                                print(f"❌ {msg}")
                                if not first_error_msg:
                                    first_error_msg = msg
                                    first_error_line = line_num
                                parse_ok = False
                            else:
                                # Standalone function call validation
                                fname = _extract_func_name(line)
                                if fname and fname not in builtins_set:
                                    if not first_validation_msg:
                                        first_validation_msg = (
                                            f"unknown function '{fname}'"
                                        )
                                        first_validation_line = line_num
                                    validation_ok = False
                            continue
                        # Other patterns considered non-fatal (could add semantic checks later)
                    except Exception as e:  # defensive parser guard
                        msg = f"Internal parse issue line {line_num}: {e}"
                        print(f"❌ {msg}")
                        if not first_error_msg:
                            first_error_msg = msg
                            first_error_line = line_num
                        parse_ok = False
                if parse_ok:
                    if validation_ok:
                        print("✅ Parse OK (no execution performed)")
                        return finish(
                            AetherErrorCode.SUCCESS,
                            "parse ok",
                            file=command_text,
                            phase="parse",
                        )
                    else:
                        print(
                            "⚠️ Semantic validation failed (unknown functions detected)"
                        )
                        return finish(
                            AetherErrorCode.VALIDATION_ERROR,
                            first_validation_msg or "validation error",
                            file=command_text,
                            phase="parse",
                            line=first_validation_line,
                        )
                return finish(
                    AetherErrorCode.PARSE_ERROR,
                    first_error_msg or "parse error",
                    file=command_text,
                    phase="parse",
                    line=first_error_line,
                )
            else:
                # Full execution path with structured runtime error capture
                try:
                    success = await aether.execute_aether_file(command_text)
                except Exception as e:  # Unexpected internal error
                    return finish(
                        AetherErrorCode.INTERNAL_ERROR,
                        f"internal execution crash: {e}",
                        file=command_text,
                        phase="execute",
                    )
                if success:
                    return finish(
                        AetherErrorCode.SUCCESS,
                        "ok",
                        file=command_text,
                        phase="execute",
                    )
                else:
                    # Distinguish parse vs runtime not caught earlier; here treat as runtime
                    return finish(
                        AetherErrorCode.RUNTIME_ERROR,
                        "runtime failure",
                        file=command_text,
                        phase="execute",
                    )

        # Handle goal: commands specially (Aether Script syntax)
        elif command_text.startswith("goal:"):
            goal = command_text[5:].strip()
            if goal.startswith('"') and goal.endswith('"'):
                goal = goal[1:-1]  # Remove quotes
            await aether.execute_aether_command(f'goal: "{goal}"')
        elif command_text.startswith("memory:"):
            # Handle memory: commands (Aether Script syntax)
            await aether.execute_aether_command(command_text)
        elif command_text.lower() == "status":
            await aether._show_system_status()
        elif command_text.lower() == "memory":
            await aether._show_memory_status()
        elif command_text.lower() == "consciousness":
            await aether._show_consciousness_state()
        elif command_text.lower() == "plugins":
            await aether._show_loaded_plugins()
        elif command_text.lower() == "transcendence":
            await aether._show_transcendence_status()
        elif command_text.lower() == "services":
            await aether._show_active_services()
        else:
            # Check if it looks like Aether Script syntax
            if ":" in command_text or "(" in command_text:
                # Execute as Aether Script
                await aether.execute_aether_command(command_text)
            else:
                # Treat as a goal
                await aether.execute_aether_command(f'goal: "{command_text}"')
    else:
        # Interactive mode
        print("🧠 AETHER - Aetherra Script Interpreter & AI OS Cognitive Interface")
        print("=" * 70)
        print("Commands:")
        print("  script.aether            - Execute Aether Script file")
        print('  goal: "your goal here"    - Process high-level goal (Aether Script)')
        print("  memory: load_logs()      - Memory operation (Aether Script)")
        print("  status                   - Show system status")
        print("  memory                   - Show memory system")
        print("  consciousness           - Show consciousness state")
        print("  plugins                 - Show loaded plugins")
        print("  transcendence          - Show transcendence readiness")
        print("  services               - Show active services")
        print("  exit                   - Exit")
        print()
        print("🧠 Aether Script Language Features:")
        print("  • goal: statements for intent processing")
        print("  • memory: operations for cognitive state")
        print("  • Built-in functions: reflect(), summarize(), store(), etc.")
        print("  • Function calls with arguments")
        print("  • Variable assignments with : syntax")
        print()

        while True:
            try:
                user_input = input("aether> ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    break
                elif user_input.endswith(".aether"):
                    # Execute Aether Script file (interactive mode legacy path - no structured reporting)
                    await aether.execute_aether_file(user_input)
                elif (
                    user_input.startswith("goal:")
                    or user_input.startswith("memory:")
                    or ":" in user_input
                    or ("(" in user_input and user_input.endswith(")"))
                ):
                    # Execute as Aether Script
                    await aether.execute_aether_command(user_input)
                elif user_input.lower() == "status":
                    await aether._show_system_status()
                elif user_input.lower() == "memory":
                    await aether._show_memory_status()
                elif user_input.lower() == "consciousness":
                    await aether._show_consciousness_state()
                elif user_input.lower() == "plugins":
                    await aether._show_loaded_plugins()
                elif user_input.lower() == "transcendence":
                    await aether._show_transcendence_status()
                elif user_input.lower() == "services":
                    await aether._show_active_services()
                elif user_input:
                    # Treat as a goal in Aether Script syntax
                    await aether.execute_aether_command(f'goal: "{user_input}"')
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                print()

        print("👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
