#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Context Analyzer - Lyrixa's System Awareness Engine

This module analyzes user messages to detect intent patterns and surfaces
relevant Aetherra OS capabilities proactively. It allows Lyrixa to be
constantly aware of available systems and naturally integrate them into
responses.

Key capabilities:
- Intent detection (coding, memory ops, plugin use, system queries)
- System capability mapping
- Contextual hint generation for AI prompts
- Service registry integration for real-time system status
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ContextualIntent:
    """Detected intent with confidence and relevant systems"""

    primary_intent: str  # coding, memory, system_query, plugin_request, etc.
    confidence: float
    relevant_systems: list[str]
    contextual_hints: list[str]
    suggested_capabilities: list[str]


class ContextAnalyzer:
    """Analyzes user messages and maps them to Aetherra OS capabilities"""

    # Intent patterns with associated systems
    INTENT_PATTERNS = {
        "coding": {
            "patterns": [
                r"\b(write|code|program|script|function|class|implement|develop|build)\b",
                r"\b(python|javascript|typescript|java|c\+\+|rust|go)\b",
                r"\b(algorithm|data structure|api|library|framework)\b",
                r"\b(debug|fix|refactor|optimize|test)\b",
            ],
            "systems": [
                "aetherra_engine",
                "plugin_manager",
                "aether_script_service",
                "self_repair_service",
            ],
            "hints": [
                "I can access the Aetherra execution engine for code generation",
                "Plugin system available for extending functionality",
                "Self-repair service can detect and fix code issues",
                "Aether script service can execute .aether workflows",
            ],
        },
        "memory_ops": {
            "patterns": [
                r"\b(remember|recall|memory|memorize|store|retrieve|forget)\b",
                r"\b(save|persist|keep track|history|past|previous)\b",
                r"\b(what did|earlier|before|last time)\b",
            ],
            "systems": [
                "memory_system",
                "persistent_memory_system",
                "qfac_memory_system",
                "multidimensional_memory",
            ],
            "hints": [
                "I have access to quantum-enhanced memory systems (QFAC)",
                "Multidimensional memory stores episodic, conceptual, and core memories",
                "Persistent memory preserves interactions across sessions",
                "Can query memories by semantic similarity or time-based retrieval",
            ],
        },
        "plugin_request": {
            "patterns": [
                r"\b(plugin|extension|addon|tool|utility)\b",
                r"\b(install|load|enable|use|activate)\b.*\b(plugin|tool)\b",
                r"\b(available plugins|list plugins|what plugins)\b",
            ],
            "systems": ["plugin_manager", "aetherra_hub"],
            "hints": [
                "Plugin manager can discover and load available plugins",
                "Aetherra Hub serves as the plugin marketplace",
                "Can execute plugin chains for complex workflows",
            ],
        },
        "system_query": {
            "patterns": [
                r"\b(status|health|performance|metrics|system)\b",
                r"\b(how (is|are)|what's|whats)\b.*(running|working|status)",
                r"\b(services|components|subsystems|modules)\b",
                r"\b(homeostasis|stability|kernel|os)\b",
            ],
            "systems": [
                "service_registry",
                "homeostasis_system",
                "kernel",
                "aetherra_engine",
            ],
            "hints": [
                "Service registry tracks all active Aetherra components",
                "Homeostasis system monitors and maintains system stability",
                "Kernel metrics show cycle times, queue depths, and health",
                "Can query detailed status from any registered service",
            ],
        },
        "consciousness_query": {
            "patterns": [
                r"\b(conscious|awareness|sentient|self-aware|think|feel)\b",
                r"\b(quantum|entangle|coherence|superposition)\b",
                r"\b(emotional|mood|state|consciousness)\b",
            ],
            "systems": [
                "quantum_cognition",
                "universal_cognition",
                "meta_cognition",
                "consciousness_bridge",
            ],
            "hints": [
                "Quantum consciousness engine tracks coherence and entanglement",
                "Consciousness bridge integrates quantum states into responses",
                "Emotional modeling and personality traits shape my interactions",
            ],
        },
        "learning_request": {
            "patterns": [
                r"\b(learn|teach|train|improve|adapt|evolve)\b",
                r"\b(self-improve|self-repair|autonomous)\b",
                r"\b(feedback|suggestion|better way)\b",
            ],
            "systems": [
                "self_improvement_engine",
                "self_incorporation",
                "adaptive_behavior_system",
            ],
            "hints": [
                "Self-improvement engine tracks performance metrics and proposes enhancements",
                "Adaptive behavior system learns from interactions",
                "Self-incorporation service analyzes and integrates new code autonomously",
            ],
        },
        "workspace_ops": {
            "patterns": [
                r"\b(file|folder|directory|workspace|project|repository)\b",
                r"\b(search|find|locate|list|scan)\b",
                r"\b(edit|modify|change|update|create)\b.*(file|code)",
            ],
            "systems": ["workspace_scanner", "file_watcher", "lyrixa_chat"],
            "hints": [
                "Can scan workspace for Python files and key components",
                "File watcher tracks changes in real-time",
                "Safe edit capabilities with scope enforcement",
            ],
        },
        "aether_workflow": {
            "patterns": [
                r"\b(workflow|pipeline|chain|sequence|automation)\b",
                r"\.aether\b",
                r"\b(parallel|sequential|conditional)\b.*\b(task|step|action)\b",
            ],
            "systems": ["aether_script_service", "plugin_manager", "scheduler"],
            "hints": [
                "Aether script service executes .aether workflow files",
                "Support for parallel execution and error handling chains",
                "Scheduler can run tasks on intervals or triggers",
            ],
        },
    }

    @classmethod
    def analyze(
        cls, message: str, available_services: dict[str, Any] | None = None
    ) -> ContextualIntent:
        """
        Analyze message and detect intent with relevant systems.

        Args:
            message: User message to analyze
            available_services: Optional dict of service_name -> service_info from registry

        Returns:
            ContextualIntent with detected patterns and system suggestions
        """
        message_lower = message.lower()
        intent_scores: dict[str, float] = {}

        # Score each intent based on pattern matches
        for intent_name, intent_data in cls.INTENT_PATTERNS.items():
            score = 0.0
            pattern_count = len(intent_data["patterns"])

            for pattern in intent_data["patterns"]:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    score += 1.0 / pattern_count

            if score > 0:
                intent_scores[intent_name] = score

        # Determine primary intent (highest score)
        if not intent_scores:
            # Default to general system query for awareness
            return ContextualIntent(
                primary_intent="general",
                confidence=0.3,
                relevant_systems=["lyrixa_chat", "service_registry"],
                contextual_hints=["I'm here to help with Aetherra OS tasks"],
                suggested_capabilities=[],
            )

        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = primary_intent

        intent_config = cls.INTENT_PATTERNS[intent_name]

        # Filter systems to only those actually available
        relevant_systems = intent_config["systems"]
        if available_services:
            relevant_systems = [svc for svc in relevant_systems if svc in available_services]

        # Add status info for available systems
        system_hints = list(intent_config["hints"])
        if available_services and relevant_systems:
            status_hints = []
            for svc in relevant_systems:
                info = available_services.get(svc)
                if info:
                    status = getattr(info, "status", None)
                    if status:
                        status_hints.append(
                            f"{svc.replace('_', ' ').title()} is {status.value if hasattr(status, 'value') else status}"
                        )
            system_hints.extend(status_hints)

        # Generate capability suggestions
        capabilities = cls._suggest_capabilities(intent_name, message, relevant_systems)

        return ContextualIntent(
            primary_intent=intent_name,
            confidence=min(1.0, confidence),
            relevant_systems=relevant_systems,
            contextual_hints=system_hints,
            suggested_capabilities=capabilities,
        )

    @classmethod
    def _suggest_capabilities(cls, intent: str, message: str, systems: list[str]) -> list[str]:
        """Generate specific capability suggestions based on intent and message"""
        suggestions = []

        if intent == "coding":
            if "python" in message.lower():
                suggestions.append("Execute Python code via Aetherra engine")
            if "test" in message.lower() or "debug" in message.lower():
                suggestions.append("Use self-repair service to detect issues")
            suggestions.append("Store implementation in memory for future reference")

        elif intent == "memory_ops":
            if "remember" in message.lower() or "store" in message.lower():
                suggestions.append("Store across episodic, conceptual, and core memory layers")
            if "recall" in message.lower() or "what did" in message.lower():
                suggestions.append("Query memories by semantic similarity")
            if "qfac_memory_system" in systems:
                suggestions.append("Use QFAC quantum-enhanced compression for large data")

        elif intent == "plugin_request":
            suggestions.append("Discover available plugins via Plugin Manager")
            suggestions.append("Browse plugin marketplace via Aetherra Hub")

        elif intent == "system_query":
            suggestions.append("Query service registry for comprehensive status")
            if "homeostasis_system" in systems:
                suggestions.append("Check autonomous stability control metrics")
            suggestions.append("Review kernel cycle times and queue depths")

        elif intent == "workspace_ops":
            suggestions.append("Scan workspace for relevant files")
            if "edit" in message.lower() or "change" in message.lower():
                suggestions.append("Propose safe, scoped edits with rationale")

        return suggestions

    @classmethod
    def build_awareness_prompt_section(cls, intent: ContextualIntent) -> str:
        """Build a prompt section that makes Lyrixa aware of relevant systems"""
        if intent.confidence < 0.3:
            return ""

        sections = []
        sections.append(f"DETECTED CONTEXT: {intent.primary_intent.replace('_', ' ').title()}")

        if intent.relevant_systems:
            sections.append(f"AVAILABLE SYSTEMS: {', '.join(intent.relevant_systems)}")

        if intent.contextual_hints:
            sections.append("CAPABILITIES:")
            for hint in intent.contextual_hints[:4]:  # Limit to top 4 to avoid bloat
                sections.append(f"  - {hint}")

        if intent.suggested_capabilities:
            sections.append("YOU CAN:")
            for cap in intent.suggested_capabilities[:3]:
                sections.append(f"  - {cap}")

        return "\n".join(sections)
