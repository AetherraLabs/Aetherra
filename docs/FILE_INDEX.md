# Aetherra File Index

Generated from: D:\Aetherra Project

Note: This appendix focuses on key project files. Some generated or cache files are excluded.

```text
Aetherra/
  aetherra_core/
    agents/
      aetherra_grammar.py — AetherraCode Abstract Syntax Tree node"""
      aetherra_interpreter.py — Agent Interpreter (Modular Interface Wrapper)
      aetherra_parser.py — Base class for all Aetherra AST nodes"""
      agent.py — Initialize the Aetherra Agent"""
      agent_executor.py — SPDX-License-Identifier: GPL-3.0-or-later
      agent_orchestrator.py — Task priority levels for orchestration."""
      base.py — Main execution entry point - parses and executes a single line"""
      chat_router_old.py — Types of user intents"""
      cleanup_project.py — Main cleanup orchestrator for Aetherra project"""
      cognitive_adapters.py — SPDX-License-Identifier: GPL-3.0-or-later
      collaboration.py — Roles for different AI agents"""
      contradiction_detection_agent.py — Types of contradictions we can detect"""
      conversation.py — Current conversation state and context"""
      conversation_manager.py — Select the best available model from preferences with failure tracking"""
      core_agent.py — Initialize all sub-agents"""
      critique_agent.py — Analyze how well the response maintains conversation flow"""
      curiosity_agent.py — Represents an identified gap in understanding"""
      enhanced.py — Intelligent AI model selection and routing"""
      enhanced_conversation_manager.py — Initialize enhanced conversation manager with memory integration"""
      enhanced_interpreter.py — Base class for control flow exceptions"""
      enhanced_language.py — Parse .aether source code into AST"""
      enhanced_lyrixa.py — Initialize the Enhanced Lyrixa Window."""
      enhanced_parser.py — AetherraCode token types"""
      enhanced_self_evaluation_agent.py — Autonomous agent for continuous self-evaluation and improvement"""
      escalation_agent.py — Agent responsible for handling failed or stalled workflows"""
      goal_agent.py — Represents a goal or task"""
      goal_forecaster.py — Persistent database for forecast storage and retrieval"""
      goals.py — Goal status enumeration"""
      grammar.py — AetherraCode Abstract Syntax Tree node"""
      learning_loop_integration_agent.py — Represents an autonomous learning goal generated from memory analysis"""
      lyrixa_aetherra_integration.py — Simple mock of Aetherra engine for basic functionality"""
      lyrixa_assistant.py — Generate a fallback response when core is not available"""
      lyrixa_memory.json
      lyrixa_script_integration.py — Initialize the script integration system"""
      natural_compiler.py — Load patterns for recognizing human intent"""
      optimized_integration.py — Fallback minimal stub used when real engine isn't importable."""
      parser.py — Base class for all AetherraCode AST nodes"""
      reflexive_loop.py — Lyrixa's understanding of the current project"""
      self_evaluation_agent.py — Agent responsible for self-analysis and self-improvement logic"""
      self_question_generator_agent.py — Represents a self-generated question for exploration"""
    ai/
      llm_integration.py — Dynamically import the LLM manager to handle path setup"""
      README.md — ai
    cognitive/
      meta_reasoning.py — Types of decisions that can be tracked"""
      README.md — cognitive
      reasoning_engine.py — Context for reasoning operations"""
      reasoning_providers.py — Reasoning provider adapter interfaces (Wave A bootstrap).
    config/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      config_loader.py — Custom exception for configuration-related errors"""
      README.md — config
      system.json
    conversation/
      human_style.py — Return (styled_text, markers). If disabled, returns base_text unchanged.
    engine/
      intelligence/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        README.md — intelligence
      __init__.py — Mock AetherraEngine for development when actual engine isn't available."""
      aetherra_engine.py — Raised when an unavailable optional component is used."""
      assistant.py — Create unique session identifier with enhanced metadata"""
      lyrixa_engine.py — Main Lyrixa execution engine that coordinates all subsystems"""
      lyrixa_memory.json
      prompt_engine.py — Load memory from JSON file"""
      README.md — engine
      reasoning_engine.py — Compatibility shim for the relocated reasoning engine.
      self_improvement_engine.py — Types of improvements"""
    events/
      README.md — events
    file_system/
      __init__.py — Get the status of the file system.
      compression_analyzer.py — Memory type classification"""
      README.md — file_system
    intelligence/
      core_intelligence.py — Initialize the Lyrixa Intelligence system."""
      intelligence_integration.py — Initialize connections to modular components with graceful fallback"""
      README.md — intelligence
    kernel/
      __init__.py — Get the status of the kernel system.
      gui_generator.py — SPDX-License-Identifier: GPL-3.0-or-later
      memory_kernel.py — SPDX-License-Identifier: GPL-3.0-or-later
      narrator.py — SPDX-License-Identifier: GPL-3.0-or-later
      pulse.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_bridge.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — Kernel Subsystem
      reflector.py — Compatibility wrapper for the production reflector implementation.
      web_bridge.py — Bridge class for Qt-Web communication"""
    memory/
      QuantumEnhancedMemoryEngine/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        causal_brancher.py — SPDX-License-Identifier: GPL-3.0-or-later
        compression.py — SPDX-License-Identifier: GPL-3.0-or-later
        fractal_encoder.py — Compatibility shim for legacy quantum memory fractal encoder imports.
        observer_effects.py — SPDX-License-Identifier: GPL-3.0-or-later
        quantum_config.json
        quantum_memory_engine.py — Quantum-enhanced memory processing engine"""
        README.md — QuantumEnhancedMemoryEngine
      fractal_mesh/
        analogs/
          __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
          pattern_matcher.py — Represents an analogical pattern between memory fragments"""
          README.md — analogs
        concepts/
          __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
          concept_clusters.py — Tracks how a concept has evolved over time"""
          README.md — concepts
        timelines/
          __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
          episodic_timeline.py — Represents a recurring temporal pattern in memory"""
          README.md — timelines
          reflective_timeline_engine.py — Extended causal relationship tracking"""
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        base.py — Types of memory fragments in the fractal mesh"""
        README.md — fractal_mesh
      narrator/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        llm_narrator.py — Helper function to handle attribute compatibility between different MemoryFragment versions"""
        README.md — narrator
        story_model.py — A generated narrative from memory fragments"""
      pulse/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        deviation_checker.py — Alert about detected memory drift"""
        README.md — pulse
      qfac/
        __init__.py — Store content in QFAC.
        api.py — SPDX-License-Identifier: GPL-3.0-or-later
        codec_pq.py — Very small OPQ-like: center and compute PCA rotation via SVD.
        fractal_sig.py — SPDX-License-Identifier: GPL-3.0-or-later
        index_ivf_pq.py — IVF-PQ index with optional FAISS acceleration and NumPy fallback.
        materializer.py — Observer-dependent view materializer.
        models.py — QFAC core models and helper utilities.
        qfac_api.py — Minimal in-memory store and naive search for QFAC 2.5 scaffolding.
        rewrite_daemon.py — Background Fractal GC (self-healing + compaction) stub.
      quantum/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        qhash.py — Quantum-inspired hashing utilities (SimHash-style).
        qrng_service.py — QRNG service (simulated unless provider integrated).
        quantum_bridge.py — QuantumBridge (simulator-first)
        random_features.py — Random feature maps (simulator-first).
      quantum_dashboard/
        static/
          README.md — static
      reflector/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        README.md — reflector
        reflect_analyzer.py — An insight discovered through reflection"""
      storm/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        engine.py — Minimal STORM skeleton.
        metrics.py — STORM metrics stubs (Prometheus-style naming)
        ot_helpers.py — Generate a deterministic mock embedding for a string using SHA-256 seeding."""
        persistence.py — SQLite-backed persistence for STORM sheaf cells and overlaps.
        shadow_logger.py — Shadow mode logging for STORM Phase 0 validation.
        tda_sheaf_helpers.py — Compute a simple sheaf inconsistency proxy from embeddings.
        tt_compression.py — TT/MPS-style compression shim for cost matrices.
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      aetherra_memory_engine.py — Compat store: accept dicts with 'content' and optional 'metadata'.
      causal_branch_simulator.py — Represents a potential future memory state with probability weighting"""
      compression_metrics.py — Memory compression fidelity levels"""
      concept_clustering.py — Represents a semantic concept in the clustering system"""
      enhanced_memory.py — Enhanced memory system with advanced capabilities."""
      fractal_encoder.py — SPDX-License-Identifier: GPL-3.0-or-later
      fractal_hierarchies.py — Represents a fractal cluster in the hierarchy"""
      fractal_replay_engine.py — Represents a reconstructed memory episode"""
      lightweight_memory_core.py — Lightweight memory entry used for UI demos and core search logic."""
      lyrixa_memory_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      memory_core.py — Close the underlying SQLite connection if open.
      memory_core_adapter.py — SPDX-License-Identifier: GPL-3.0-or-later
      memory_kernel.py — Configuration for the integrated memory system"""
      memory_learning.py — Classify the type of interaction for learning purposes"""
      models.py — Canonical typed recall contract.
      observer_effect_simulator.py — Different types of observers with varying impact levels"""
      optimized_memory_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      optimized_storage.py — Represents a pending write operation"""
      qfac_dashboard.py — Start dashboard in 'interactive' (web) or 'text' mode."""
      qfac_integration.py — Automatically analyze and compress if beneficial"""
      qfac_launcher.py — Initialize QFAC components"""
      qfac_policy.py — !/usr/bin/env python3
      qfac_retrieval.py — Return list of dicts per node with base and boosted scores.
      qfac_state_tracker.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_memory_bridge.py — Compatibility wrapper for execute function"""
      quantum_memory_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_memory_integration.py — Quantum-specific memory metrics"""
      quantum_memory_state.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_web_dashboard.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — Memory subsystem (contributor guide)
      world_class_memory_core.py — Core memory data structure"""
    orchestration/
      __init__.py — Mock AetherraScheduler for development when actual scheduler isn't available."""
      agent_orchestrator.py
      data_manager.py — Initialize all available cognitive systems"""
      multi_agent_manager.py — SPDX-License-Identifier: GPL-3.0-or-later
      orchestration_bridge.py — Types of specialized agents"""
      README.md — orchestration
      scheduler.py — Task priority levels."""
    os_kernel/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      hmr_controller.py — Forwarder to the current HMR controller implementation.
      kernel_loop.py — Forwarder to the current OS kernel loop implementation.
      README.md — Aetherra Core OS Kernel (shim)
    personality/
      interfaces/
        README.md — interfaces
      integration.py — Determine the type of response for appropriate personality modulation"""
      multimodal_coordinator.py — Supported interaction modalities for Lyrixa"""
      personality_engine.py — Core personality traits that define Lyrixa's character"""
      README.md — personality
      response_critic.py — Analyze how natural vs robotic the response sounds"""
      response_quality_integration.py — Apply style recommendations to enhance the initial response"""
      social_learning.py — Handles privacy-preserving data collection and learning from community interactions"""
      social_learning_integration.py — Determine interaction context type"""
      text_personality.py — Adapt a specific trait for text interaction"""
    plugins/
      __init__.py — Mock PluginManager for development when actual manager isn't available."""
      advanced_plugins.py — Enhanced metadata for plugins"""
      memory_plugin_bridge.py — Store memory content with plugin metadata."""
      plugin_chain_executor.py — Plugin execution modes."""
      plugin_manager.py — Plugin state management."""
      plugin_manager_core.py — Whether to soft-load plugins with missing constructor args (default: on)."""
      plugin_registry.py — Returns a list of plugin names based on folder names."""
      README.md — plugins
    reflection/
      __init__.py — Get the status of the reflection system.
      introspection_controller.py — Levels of introspection depth"""
      README.md — reflection
      reflection_agent.py — Agent responsible for daily reflections and performance analysis"""
    reflection_engine/
      __init__.py — Get the status of the reflection engine.
      README.md — reflection_engine
    script_service/
      script_executor.py — Types of workflow steps supported."""
      script_service_logging.py — Script execution phases."""
      script_validator.py — Validation error severity levels."""
    self_metrics_dashboard/
      fidelity_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — self_metrics_dashboard
    system/
      __init__.py — Get the status of the system.
      agent_diagnostics.aether
      agent_sync.aether
      agents.aether
      bootstrap.aether
      coretools.py — Core utility tools for file access and common operations"""
      daily_maintenance.aether
      daily_reflector.aether
      goal_autopilot.aether
      goals.aether
      ignore_pattern_loader.py — A single ignore pattern with metadata."""
      logger.aether
      memory_cleanser.aether
      memory_ops.aether
      optimization_executor.py — Performance metrics for comparison."""
      plugin_watchdog.aether
      plugins.aether
      policy_manager.py — Ethical decision-making profile with weighted frameworks."""
      README.md — System Subsystem
      reflection_system.py — Analyze a single interaction for patterns and insights"""
      security_system.py — Return a deep-copied structure with secret-looking fields redacted.
      self_introspector.aether
      signature_verifier.py — Information about a file's signature."""
      system_bootstrap.py — Status of system components"""
      system_logger.aether
      system_logger.py — SPDX-License-Identifier: GPL-3.0-or-later
      test_enhanced_language.aether
      test_goal_autopilot.aether
      utils.aether
    __init__.py — Get the status of all core systems."""
    README.md — aetherra_core
  aetherra_hub/
    aetherra_hub/
      package-lock.json
      package.json
      README.md — aetherhub - The AI Package Manager
  ai_engine/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    coordinator.py — AI Coordinator stub for validation - delegates to actual AI runtime"""
  analysis/
    .aether_risk_static.py — SPDX-License-Identifier: GPL-3.0-or-later
    static_risk.py — SPDX-License-Identifier: GPL-3.0-or-later
  api/
    auth/
      __init__.py — Clean architecture component
      README.md — auth
    middleware/
      README.md — middleware
    rest/
      README.md — rest
      run_server.py — Main entry point for the API server
    websocket/
      README.md — websocket
    aether_server.py — Root endpoint with API information"""
    approvals.py — In-memory store for approval records.
    job_controller.py — Find a .aether script by name"""
    job_store.py — Job status enumeration"""
    models.py — Request model for running a .aether script"""
    README.md — Aetherra Script Execution API
    run_server.py — Main entry point for the API server
  cli/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    alerts.py — SPDX-License-Identifier: GPL-3.0-or-later
    basic.py — Show basic AetherraCode status"""
    main.py — CLI that demonstrates persona adaptation in real-time"""
    persona.py — Command-line interface for AetherraCode persona management"""
    plugin.py — Format plugin list for display"""
    policy_bootstrap.py — Create a minimal capabilities.json (deny-by-default unless explicitly granted).
    README.md — cli
  config/
    quantum/
      monitoring_config.json
      quantum_config.json
      quantum_ui_config.json
      README.md — quantum
      scaling_config.json
    README.md — config
  consciousness/
    agents/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      agent_integration_adapter.py — Types of agents that can be integrated."""
      agent_registry.py — Agent registration status"""
      phase2_integration_manager.py — Initialize the integration manager and its components."""
    core/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      config.py — SPDX-License-Identifier: GPL-3.0-or-later
      consciousness_bridge.py — Standard message format for consciousness layer communication"""
      consciousness_core.py — The always-on awareness engine.
      lyrixa_consciousness.py — Lyrixa's emotional states"""
      meta_layer_core.py — Possible states for an agent"""
      think_stream.py — Bridge for consciousness state to UI and telemetry systems.
      types.py — Subjective state vector representing felt experience.
    cosmic/
      cosmic_consciousness_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
    embodiment/
      __init__.py — Embodiment interfaces for sensors and actuators (MVP).
      base.py — Embodiment Base Interfaces (MVP)
    intelligence/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      collective_intelligence.py — SPDX-License-Identifier: GPL-3.0-or-later
      consciousness_integration.py — SPDX-License-Identifier: GPL-3.0-or-later
      emergent_behavior.py — SPDX-License-Identifier: GPL-3.0-or-later
      meta_cognition.py — Domains of self-knowledge for comprehensive meta-memory"""
      minimal_test.py — SPDX-License-Identifier: GPL-3.0-or-later
      simple_test.py — SPDX-License-Identifier: GPL-3.0-or-later
      test_phase3.py — SPDX-License-Identifier: GPL-3.0-or-later
    interfaces/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      agent_interaction.py — SPDX-License-Identifier: GPL-3.0-or-later
      consciousness_dashboard.py — SPDX-License-Identifier: GPL-3.0-or-later
      lyrixa_personality.py — SPDX-License-Identifier: GPL-3.0-or-later
    quantum/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      consciousness_singularity_engine.py — States of consciousness singularity"""
      evolutionary_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      final_phase5_demo.py — SPDX-License-Identifier: GPL-3.0-or-later
      meta_learning.py — Quantum-enhanced learning modes"""
      multidimensional_state_engine.py — Dimensional axes for consciousness processing"""
      parallel_reality_navigator.py — Types of parallel realities"""
      phase5_integration_test.py — SPDX-License-Identifier: GPL-3.0-or-later
      phase_7_3_integration.py — Unified consciousness state with memory and temporal components"""
      quantum_consciousness.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_consciousness_engine.py — Quantum consciousness states"""
      quantum_consciousness_integration.py — Complete result from quantum cognition process"""
      quantum_consciousness_tunneling.py — Quantum consciousness tunneling modes"""
      quantum_decision_engine.py — Quantum decision states"""
      quantum_interference_patterns.py — Types of quantum interference"""
      quantum_memory_system.py — Quantum memory states"""
      quantum_tunneling_logic.py — Types of logical barriers"""
      reality_synthesis_engine.py — Reality synthesis modes"""
      simple_phase5_test.py — SPDX-License-Identifier: GPL-3.0-or-later
      temporal_consciousness_system.py — Temporal consciousness states"""
      temporal_coordination.py — SPDX-License-Identifier: GPL-3.0-or-later
      test_phase_7_3_comprehensive.py — Comprehensive testing suite for Phase 7.3 components"""
      test_phase_7_4_integration.py — Phases of consciousness transcendence"""
      test_quantum_consciousness.py — Test the quantum decision engine"""
      transcendence_consolidation_engine.py — States of consciousness transcendence"""
    schemas/
      __init__.py — Schema definitions for Aetherra Consciousness module.
      affect_snapshot.py — Affect Snapshot Schema
      episodic_event.py — Episodic Event Schema
      ethics_incident.py — Ethics Incident Schema
      narrative_chapter.py — Narrative Chapter Schema
      self_model.py — Self-Model Schema
    sensors/
      base_sensor.py — Sensor Base Class (Phase 1)
      file_change_sensor.py — File Change Sensor Stub
      registry.py — Sensor Registry / Starter
      system_sensor.py — System Sensor Stub
    transcendence/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      beyond_transcendence_engine.py — Namespaced Beyond Transcendence Engine adapter.
    active_inference.py — Active Inference Wrapper (MVP)
    affect_engine.py — Affect Engine MVP
    autonomy_governor.py — Autonomy Governor.
    autopilot_manager.py — Simple heuristic evaluator for autopilot graduation.
    CONSCIOUSNESS_EVOLUTION_COMPLETE_SUMMARY.md — Aetherra Consciousness Evolution - Complete Journey Summary
    consciousness_orchestrator.py — Initialize all consciousness components"""
    consolidation.py — Memory consolidation and decay engine.
    continuity_memory.py — Single moment in consciousness stream.
    dashboards.py — Telemetry dashboard for Phase 3 & 4 consciousness metrics.
    decision_engine.py — Consciousness Decision Engine.
    demo.py — Run a demonstration of the consciousness orchestrator"""
    dream_cycle.py — Reflective offline learning engine.
    episodic_store.py — Episodic Store
    ethics_critic.py — Ethics Critic MVP
    event_bus.py — Unified Event Bus (Phase 1)
    explanation_engine.py — Structured explanation record.
    EXTENDED_ROADMAP.md — 🧠 AETHERRA EXTENDED ROADMAP
    health_checks.py — Probe chat system health via Hub API.
    learning_loop.py — Consciousness Learning Loop.
    metrics_exporter.py — Prometheus Metrics Exporter (Optional)
    narrator.py — Narrative Layer (Phase 1)
    phase2_demo.py — Initialize the full consciousness system with integrated agents."""
    PHASE_5_COMPLETION_SUMMARY.md
    PHASE_8_3_ACHIEVEMENT_REPORT.md — Phase 8.3: Beyond Transcendence Achievement Report
    policy_reasoner.py — Minimal changes to move a decision toward allowed.
    qualia_learning.py — Learned parameters for qualia update dynamics.
    ROADMAP.md — Aetherra Consciousness Orchestrator - Meta-Layer Roadmap
    self_model.py — Self-Model API (Phase 1)
    self_model_manager.py — Self-Model Manager
    self_trust.py — Trust metrics for a single subsystem."""
    semantic_resonance.py — Semantic resonance engine for focus selection.
    workspace_core.py — Global Workspace Core (Phase 1 Skeleton)
  core/
    utils/
      README.md — utils
    __init__.py — Get the status of this package.
    aether_runtime.py — SPDX-License-Identifier: GPL-3.0-or-later
    aetherra_grammar.py — AetherraCode Abstract Syntax Tree node"""
    aetherra_interpreter.py — Aetherra Interpreter (Modular Interface)
    aetherra_memory.py — Aetherra Memory System - Backward Compatibility Layer
    aetherra_parser.py — Base class for all Aetherra AST nodes"""
    aetherra_self_organizer.py — Comprehensive metadata for each file in the system."""
    agent.py — Placeholder for memory pattern analysis"""
    ai_runtime.py — Load environment variables from .env file"""
    chat_router.py — Types of user intents"""
    chat_router_new.py — Types of user intents"""
    chat_router_old.py — Types of user intents"""
    config.py — Global configuration for Aetherra"""
    disclosure_policy.py — Return a metadata-only representation suitable for the Free tier.
    enhanced_language.py — Parse .aether source code into AST"""
    lyrixa_memory.json
    memory_manager.py — Types of memory storage"""
    multi_llm_manager.py — Supported LLM providers"""
    os_interface.py — Initialize core AI services for the OS."""
    prompt_engine.py — Load memory from JSON file"""
    README.md — core
    syntax_tree.py — Calculate the maximum depth of a syntax tree (legacy function)
    webhook_manager.py — Manages webhook registration, triggering, and error handling."""
  data/
    contradiction_data/
      detected_contradictions.json
      README.md — contradiction_data
      resolution_strategies.json
    curiosity_data/
      curiosity_questions.json
      knowledge_gaps.json
      README.md — curiosity_data
    databases/
      core/
        README.md — core
      lyrixa/
        README.md — lyrixa
      shared/
        README.md — shared
    growth_trajectory_data/
      README.md — growth_trajectory_data
    learning_loop_data/
      current_cycle.json
      learning_cycles.json
      learning_goals.json
      README.md — learning_loop_data
    memory_continuity_data/
      README.md — memory_continuity_data
    meta_learning_data/
      current_cycle.json
      learning_cycles.json
      learning_goals.json
      README.md — meta_learning_data
    metrics_data/
      README.md — metrics_data
    operations/
      README.md — operations
    qfac_dashboard_data/
      README.md — qfac_dashboard_data
    question_generator_data/
      generated_questions.json
      question_clusters.json
      README.md — question_generator_data
    self_directed_learning_data/
      current_cycle.json
      learning_cycles.json
      learning_goals.json
      README.md — self_directed_learning_data
    self_metrics_data/
      README.md — self_metrics_data
    share/
      jupyter/
        labextensions/
          jupyterlab-plotly/
            static/
              README.md — static
            install.json
            package.json
            README.md — jupyterlab-plotly
      man/
        man1/
          README.md — man1
  db/
    README.md — db
  docs/
    aetherra_labs_vision.md — Aetherra Labs Vision
    AETHERRA_MANIFESTO.md — AETHERRA MANIFESTO (v6.0 – July 2025)
    AI_OS_MANIFESTO.md — 🧬 The AI Operating System Manifesto
    README.md — docs
    SELF_ORGANIZING_INTELLIGENCE.md — 🧠 Aetherra Self-Organizing Intelligence System
  growth_trajectory_data/
    README.md — growth_trajectory_data
  guardian/
    __init__.py — Aetherra Guardian System public API.
    approval.py — Approval request persistence for Guardian."""
    audit.py — Guardian audit integration with the signed Security audit ledger."""
    containment.py — Containment event persistence for Guardian."""
    core.py — Core evaluator for the Aetherra Guardian System."""
    mode.py — Guardian operating-mode state and controls."""
    models.py — Typed contracts for the Aetherra Guardian System."""
    paths.py — Filesystem path helpers for Guardian state and policy.
    policy.py — Guardian policy bridge to the existing Aetherra Security System."""
    preauthorization.py — Scoped preauthorization grants for low-risk Guardian decisions."""
    reversibility.py — Reversibility checks for Guardian intents."""
    risk.py — Risk scoring for Guardian intent declarations."""
    state.py — Small JSONL state helpers for Guardian approval and containment queues."""
    tiers.py — Decision-tier classification for Guardian intent declarations."""
  gui/
    __init__.py — Aetherra GUI compatibility surface.
    aetherra_os_gui.py — Publish a performance/status metric if event bus available.
    GUI_CURATION_PLAN.md
    launch_enhanced_neural_os.py — !/usr/bin/env python3
    README.md — Aetherra OS Monitor GUI
    run_aetherra_os.py — Launch the Enhanced Aetherra Neural OS Dashboard
  homeostasis/
    __init__.py — !/usr/bin/env python3
    alert_intelligence.py — Types of detected anomalies."""
    audit_trace_layer.py — Complete trace record for a homeostasis action."""
    autonomous_error_corrector.py — Pattern for detecting specific errors."""
    diagnosis.py — Read-only Homeostasis diagnosis reports.
    ethical_cognitive_integration.py — Ethical cognition metrics for stability analysis."""
    guard_policy_enforcer.py — Lightweight in-memory guard policy enforcer.
    homeostasis_actuators.py — Result of an actuator action."""
    homeostasis_core.py — Operating modes for the homeostasis controller."""
    homeostasis_integration.py — Start the persistent watchdog thread."""
    intelligent_alert_manager.py — Alert escalation rule definition."""
    learning.py — Read-only Homeostasis learning and effectiveness reports."""
    lyrixa_integration.py — Request for Lyrixa reflection analysis."""
    multi_node_coordination.py — States for cluster nodes."""
    multi_node_integration.py — Start multi-node homeostasis integration."""
    night_cycle_integration.py — System activity periods."""
    observation.py — Read-only Homeostasis observation reports.
    README.md — 🧬 Aetherra Homeostasis System
    recommendation.py — Read-only Homeostasis recommendation reports.
    self_improvement_metrics_bridge.py — Start the metrics bridge."""
    self_incorporation_metrics_bridge.py — Start the metrics bridge."""
    self_incorporation_security.py — Result of security validation."""
    stability_metrics.py — Single point-in-time snapshot of all system metrics."""
    system_supervisor.py — System runlevel states."""
  hub/
    federation.py — Simple peer registry and federated catalog cache."""
  integration/
    adapters/
      memory_adapter_impl.py — Real memory adapter connecting all migrated databases"""
      README.md — adapters
    bridges/
      aetherra_lyrixa_bridge.py — Standard message format for Aetherra-Lyrixa communication"""
      memory_adapter.py — Adapter for integrating Aetherra and Lyrixa memory systems"""
      memory_adapter_impl.py — Real implementation of memory adapter with your databases"""
      README.md — bridges
    monitoring/
      README.md — monitoring
    protocols/
      README.md — protocols
    __init__.py — Get current integration system status."""
    agent_registry.json
    README.md — integration
  interface/
    launch_aetherra_os.py — Check if required dependencies are installed"""
    main_window.py — Background thread for monitoring Aetherra OS state"""
    README.md — interface
    web_panels.py — Create enhanced dashboard panel HTML"""
  interface_bridge/
    memory_api.py — Clean memory interface for Lyrixa"""
    README.md — interface_bridge
  lyrixa/
    LyrixaCore/
      IdentityAgent/
        __init__.py — Initialize cross-system identity integration"""
        core_beliefs.py — Strength of conviction in a belief"""
        personal_history.py — Types of memories in personal history"""
        self_model.py — Levels of capability assessment"""
      __init__.py — Initialize all core Lyrixa systems"""
      interface_bridge.py — Bridge class for Qt-Web communication"""
    agents/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      agent_base.py — Get current agent status and metadata."""
      agent_collaboration_manager.py — Represents a collaborative task between agents."""
      contradiction_detection_agent.py — Agent that detects and resolves contradictions in system state and reasoning"""
      conversation_manager.py — Types of conversation interactions"""
      curiosity_agent.py — Agent that drives curiosity and exploration in the system"""
      data_agent.py — Process data analysis requests"""
      enhanced_conversation_manager.py — Initialize the enhanced conversation manager"""
      escalation_agent.py — Check if this agent can handle the request type."""
      goal_agent.py — Check if this agent can handle the request type."""
      learning_loop_integration_agent.py — Agent that manages learning loops and continuous improvement"""
      lyrixa_ai.py — Check if this agent can handle the request type."""
      README.md — agents
      security_agent.py — Process security monitoring requests"""
      self_question_generator_agent.py — Agent that generates self-reflective questions for system introspection"""
      support_agent.py — Process user support requests"""
      technical_agent.py — Process technical support requests"""
    awareness/
      context_analyzer.py — Detected intent with confidence and relevant systems"""
      README.md — Awareness Module - Lyrixa System Intelligence
      system_monitor.py — Tracks and reports Aetherra OS system state for Lyrixa"""
    chat/
      lyrixa_chat_service.py — Capture system metrics broadcasts so Lyrixa can surface them automatically.
    ethics_agent/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      bias_detector.py — Types of bias that can be detected."""
      moral_reasoning.py — Different moral reasoning frameworks."""
      README.md — ethics_agent
      value_alignment.py — Core human values for alignment."""
    gui/
      CHANGELOG.md — Lyrixa GUI Changelog
      consciousness_panel.py — Compatibility exports for legacy consciousness dashboard imports."""
      main_window.py — Minimal compatibility main window for the legacy Lyrixa GUI import path.
      package-lock.json
      package.json
      QUICKSTART.md — Lyrixa GUI
      README.md — Lyrixa GUI
      SETUP.md — Lyrixa GUI - Installation & Setup Guide
      STARTUP.md — 🚀 Lyrixa GUI - Startup Guide
      SUMMARY.md — 🎨 Lyrixa GUI - Complete Setup Summary
      tsconfig.json
      tsconfig.node.json
    integrations/
      aetherra_hub_connector.py — Connect to Aetherra Hub"""
      memory_adapter.py — Get comprehensive system status for plugin UI"""
      style_manager.py — Generate a unique style variable name"""
    intelligence/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      adaptive_orchestrator.py — !/usr/bin/env python3
      lyrixa_full_intelligence.py — Load intelligence configuration"""
      meta_reasoning.py — Types of decisions that can be tracked"""
    interactive/
      __init__.py — !/usr/bin/env python3
      expression_manager.py — Available expression states for Lyrixa."""
      integration.py — Initialize all components."""
      interactive_loop.py — Represents Lyrixa's current emotional state."""
      state_map.json
      state_mapper.py — Load and validate state_map.json."""
    memory/
      fractal_mesh/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        base.py — Represents a fractal cluster in the hierarchy"""
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      advanced_memory_integration.py — Initialize memory systems"""
      lyrixa_memory_engine.py — Represents a single memory entry."""
      multidimensional_memory.py — Store an interaction across the seven conceptual layers.
      quantum_memory_integration.py — Normalize quantum state probabilities."""
      README.md — memory
      simple_memory_adapter.py — Simple memory fragment for basic operations"""
    plugins/
      advanced-memory-system/
        aetherra-plugin.json
        README.md — advanced-memory-system
      interaction/
        voice_responder.py — Available audio cue types."""
      workflow_builder/
        manifest.json
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      advanced_memory_system_ui.py — Advanced Memory System Plugin UI with comprehensive memory management."""
      ai_plugin_generator_ui.py — AI Plugin Generator UI for intelligent plugin creation."""
      assistant_trainer_plugin_ui.py — Assistant Trainer Plugin UI for customizing AI behavior and training."""
      context_aware_surfacing_ui.py — Context Aware Surfacing Plugin UI for intelligent content recommendations."""
      installed_plugins.json
      introspector_plugin_ui.py — Introspector Plugin UI for system analysis and self-reflection."""
      memory_aware_plugin_router.py — Memory context provided to plugins for enhanced behavior"""
      plugin_analytics_ui.py — Plugin Analytics UI for monitoring plugin usage and performance."""
      plugin_creation_wizard_ui.py — Plugin Creation Wizard UI with step-by-step guidance."""
      plugin_manager.py — Plugin state management."""
      workflow_builder_ui.py — A visual node in the workflow builder."""
    proactive/
      proactive_consciousness.py — Start the background monitoring task and subscribe to events."""
    reflection_engine/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      shadow_state_forker.py — Agent responsible for daily reflections and performance analysis"""
      validation_engine.py — Analyze a single interaction for patterns and insights"""
    self_metrics_dashboard/
      __init__.py — Initialize the metrics dashboard."""
      main_dashboard.py — Get the main dashboard instance.
      memory_continuity_score.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — self_metrics_dashboard
    __init__.py — Enhanced intelligence stack with full AI capabilities"""
    analytics_dashboard.py — Initialize all dashboard components"""
    analytics_insights_engine.py — Data class for analytics metrics"""
    consciousness_integration.py — Standard message format for consciousness layer communication"""
    ethics.py — Ethics assessment levels."""
    intelligence_integration.py — Get the conversation manager instance"""
    launcher.py — Load environment variables from a .env file if present.
    README.md — lyrixa
  lyrixa_plugins/
    emotion_detector.py — Primary emotion categories"""
    emotional_intelligence.py — Represents a complex emotional state with multiple dimensions"""
    emotional_intelligence_integration.py — Update integration performance metrics"""
    mini_lyrixa_avatar.py — 🔥 AI Presence Projection - Dynamic cognitive avatar"""
    README.md — lyrixa_plugins
  memory/
    QuantumEnhancedMemoryEngine/
      __init__.py — Compatibility package for legacy quantum memory imports.
      fractal_encoder.py — Compatibility shim for legacy fractal encoder imports.
      observer_effects.py — Compatibility shim for legacy observer effect imports.
    advanced/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      orchestrator.py — Advanced Memory Orchestrator stub for validation"""
    core/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      store.py — Memory Store stub for validation - delegates to actual memory engine"""
    aetherra_memory_engine.py — Compatibility shim for legacy ``memory.aetherra_memory_engine`` imports.
    graph_optics.py — SPDX-License-Identifier: GPL-3.0-or-later
    observer_effects.py — Compatibility shim for legacy ``memory.observer_effects`` imports.
    qfac_dashboard.py — Compatibility shim for legacy ``memory.qfac_dashboard`` imports.
    quantum_web_dashboard.py — Compatibility shim for legacy ``memory.quantum_web_dashboard`` imports.
  memory_continuity_data/
    README.md — memory_continuity_data
  observability/
    metrics_service.py — Lightweight in-process metrics exposure service.
  perception_bus/
    adapters/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      common.py — Base class for perception adapters.
      linux.py — Linux process monitoring via /proc."""
      windows.py — Windows process monitoring via Get-Process."""
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    bus.py — Lock-free event bus for consciousness perception.
    event_types.py — SPDX-License-Identifier: GPL-3.0-or-later
  plugins/
    agent_adapters/
      __init__.py — Plugin package: agent_adapters
      agent_base.py — Standard response format for all agents"""
      agent_plugin.py — Perform AI agent reflection on a given topic"""
      collaborative_multi_agent_system.py — Different agent roles in the collaborative system"""
      comprehensive_agent_discovery.py — Comprehensive scan for ALL agents in the entire codebase"""
      curiosity_agent_8.py — Represents an identified gap in understanding"""
      lyrixa_agent_integration.py — Submit a task for execution"""
      multi_agent_system.py — Available agent roles"""
      plugin_agent.py — Agent responsible for plugin discovery, recommendation, and usage assistance"""
      README.md — agent_adapters
      real_agent_discovery.py — Find actual agents, not every file with 'agent' in the name"""
      smart_agent_migrator.py — Load the latest agent discovery report"""
    agent_components/
      agent_bridge.py — Bridge to manage agent integration in clean architecture"""
      agent_discovery_and_integration.py — Information about discovered components"""
      agent_orchestrator.py — Status of an agent"""
    core/
      __init__.py — Plugin package: core
      advanced-memory-system.py — Return basic plugin information"""
      agent_base.py — Standard response format for all agents"""
      AssistantTrainer.py — Return basic plugin information"""
      plugin_api.py — Clean plugin interface for Lyrixa"""
      plugin_chain_executor.py — Status of plugin chain execution"""
      plugin_creation_wizard.py — Plugin template for the wizard."""
      plugin_discovery.py — Plugin metadata container."""
      plugin_generator_plugin.py — Represents a plugin template for generation."""
      plugin_manager.py — Plugin state management."""
      plugin_metadata_registry.py — Rich plugin metadata record."""
      plugin_processors.py — Configuration for a processing operation."""
      plugin_quality_control.py — Quality metrics for plugin evaluation."""
      plugin_registry.py — Discover plugins by scanning plugins/ folder and manifests.
      plugin_sdk.py — Plugin metadata for enhanced discovery and transparency"""
      plugin_system.py — Fallback to regular file writing"""
      plugin_wizard_backend.py — Main plugin class for {name}."""
      PluginGenerator.py — Return basic plugin information"""
      README.md — core
      self_improvement_dashboard.py — SPDX-License-Identifier: GPL-3.0-or-later
      WorkflowBuilder.py — Return basic plugin information"""
    examples/
      advanced-memory-system/
        aetherra-plugin.json
        memory_plugin.aether
        README.md — advanced-memory-system
      hello_plugin/
        aetherra-plugin.json
        hello_plugin.py — A minimal example plugin demonstrating the PluginInterface contract.
        README.md — Hello Plugin Example
    extra_plugins/
      __init__.py — Fallback PluginManager when imports fail.
      assistant_trainer_plugin.py — Represents a training dataset for assistant training."""
      context_aware_surfacing.py — Represents a snapshot of current context."""
      data_visualization_gui.py — Model for displaying pandas DataFrames in QTableView."""
      data_visualization_plugin.py — Chart configuration structure."""
      document_generator_gui.py — Worker thread for document generation tasks."""
      document_generator_plugin.py — Document template structure."""
      email_integration_plugin.py — Email account configuration."""
      file_organizer_plugin.py — File information and metadata."""
      introspector_plugin.py — Plugin for autonomous code analysis and self-insight generation"""
      password_manager_plugin.py — Credential entry."""
      README.md — extra_plugins
      slack_discord_bot_plugin.py — Load optional Discord dependencies only when the bot is started."""
      twitch_bot_gui.py — Worker thread for Twitch bot operations."""
      twitch_bot_plugin.py — Twitch API client for authentication and data retrieval."""
      web_research_assistant_gui.py — Background worker for research operations."""
      web_research_assistant_plugin.py — Web source information structure."""
      workflow_builder_plugin.py — Represents a single step in a workflow."""
    lifecycle/
      plugin_analytics.py — Collects detailed metrics for plugin execution and usage."""
      plugin_lifecycle_memory.py — Represents a memory entry for plugin lifecycle events."""
      plugin_state_memory.py — Generate a unique session ID."""
      README.md — lifecycle
    memory_hooks/
      __init__.py — Plugin package: memory_hooks
      memory_aware_plugin_router.py — Memory context provided to plugins for enhanced behavior"""
      memory_plugin_bridge.py — Initialize the memory engine and concept manager"""
      plugin_manager_stubs.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — memory_hooks
    __init__.py — Get the status of this package.
    ai_plugin_generator_v2.py — Plugin template definition."""
    manager.py — Plugins Manager (Phase 3 roadmap module).
    manifest_schema.py — Map hub signing strictness and signature verification to trust zone label.
    plugin_registry.py — Compatibility shim for legacy ``plugins.plugin_registry`` imports.
    README.md — Plugins Subsystem
    reflector.py — Self-reflection and behavior analysis capabilities for AetherraCode"""
  quantum/
    chat_consciousness_bridge.py — Trigger a light sync and return a coherence snapshot if available."""
  runners/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    run_consciousness.py — Run the consciousness system.
  runtime/
    __init__.py — Get the status of this package.
    aether_executor.py — Initialize all enhanced autonomous intelligence agents"""
    aether_parser.py — Main execution entry point - parses and executes a single line"""
    aether_runtime.py — Register Lyrixa's components with the runtime."""
    README.md — runtime
    script_memory_integrator.py — Export script metadata to memory system"""
    script_registry_loader.py — Load the script registry from file"""
    script_router.py — Suggest scripts based on goal or intent"""
    script_runner.py — SPDX-License-Identifier: GPL-3.0-or-later
  safety_envelope/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    actuator.py — Execute plans with safety guarantees.
    capability_registry.py — Executable capability with safety guarantees.
    dry_run_registry.py — Non-destructive wrapper around an existing CapabilityRegistry."""
    policy_engine.py — Policy decision for an action request."""
  schedulers/
    night_cycle_runner.py — Execute night cycle (dream + consolidation).
  scripts/
    utilities/
      README.md — utilities
    audit_file_usage.py — Scan entire project for Python files and their relationships"""
    check_deployment_readiness.py — Comprehensive deployment readiness validation"""
    cleanup_project.py — Main cleanup orchestrator for Aetherra project"""
    conservative_cleanup.py — Move only obviously safe-to-move files"""
    fast_cleanup.py — Perform quick cleanup of obviously unused files"""
    organize_system.py — Main launcher for Aetherra self-organizing intelligence."""
    README.md — scripts
    self_organizer.aether
    simple_audit.py — Just count Python files quickly"""
  security/
    api_keys.py — Local API-key storage with encryption-at-rest and scoped retrieval."""
    audit_ledger.py — Tamper-evident append-only JSONL audit ledger."""
    capabilities.py — Resolve the capabilities policy path at call time.
    net_policy.py — Resolve the network policy path at call time.
    plugin_signing.py — Compute a deterministic SHA256 tree hash for a list of file paths."""
    prompt_defense.py — Heuristic scan for prompt-injection and jailbreak attempts.
    sandbox.py — Base sandbox violation."""
    script_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
  stdlib/
    __init__.py — Manages AetherraCode standard library plugins"""
    executor.py — Command scheduling and execution management for AetherraCode"""
    optimizer.py — Performance optimization capabilities for AetherraCode"""
    README.md — stdlib
    selfrepair.py — Self-repair and debugging capabilities for AetherraCode"""
    sysmon.py — System monitoring capabilities for AetherraCode"""
    whisper.py — Audio transcription capabilities for AetherraCode"""
  telemetry/
    optin.py — Enable/disable Differential Privacy and optionally set epsilon.
  tools/
    migration/
      component_migrator.py — Migrates existing components to clean architecture"""
      migration_plan.json
      README.md — migration
    AETHER_SCRIPT_DEMONSTRATION_SUMMARY.md — 🧠 AETHER SCRIPT DEMONSTRATION SUMMARY
    aether_script_executor.py — Initialize all enhanced autonomous intelligence agents"""
    aetherra_file_watcher.py — Determine if a file should be processed."""
    async_memory_integration.py — Decorator to convert async function to sync using event loop"""
    causal_branch_simulator.py — Represents a potential future memory state with probability weighting"""
    code_generator.py — Generates .aether code from natural language descriptions"""
    curiosity_conflict_resolution.aether
    memory_analyzer.py — Analyzes memory patterns and generates insights"""
    qfac_integration.py — Manages integration between QFAC phases with graceful degradation"""
    quantum_dashboard_launcher.py — Launch the quantum dashboard in specified mode"""
    quantum_memory_bridge.py — Compatibility wrapper for execute function"""
    README.md — tools
  utils/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    launch_utils.py — Check if a port is available for connection"""
    logging_utils.py — Setup file logging in addition to console logging"""
    README.md — utils
    unicode_logger.py — SPDX-License-Identifier: GPL-3.0-or-later
  web/
    components/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — components
    server/
      __init__.py — Get current server system status."""
      README.md — server
      web_adapter.py — Adapter for integrating web interface with clean architecture"""
      web_bridge.py — Bridge class for Qt-Web communication"""
    __init__.py — Get current web system status."""
    README.md — web
  __init__.py — Aetherra package public API.
  aetherra_file_router.py — SPDX-License-Identifier: GPL-3.0-or-later
  aetherra_hub_integration.py — Async context manager entry"""
  file_routing_log.json
  main.py — SPDX-License-Identifier: GPL-3.0-or-later
  README.md — Aetherra - AI-Native Development Platform
  verify_lyrixa_merge.py — !/usr/bin/env python3
docs/
  adr/
    ADR-0000-template.md — ADR-0000: SHORT TITLE PLACEHOLDER
    ADR-0001-coverage-delta-model.md — ADR-0001: Coverage Delta Data Model & Storage
    ADR-0002-test-selection-heuristic-v1.md — ADR-0002: Test Selection Heuristic v1
    ADR-0003-gating-reasons-schema.md — ADR-0003: Gating Reasons Schema
    ADR-0004-phase8-adapter-strategy.md — ADR-0004: Phase 8 Adapter Strategy (Namespaced Beyond Transcendence Engine)
    ADR-0005-exception-suppression-visibility.md — ADR-0005: Exception Suppression & Visibility Policy
  analysis/
    critical_modules/
      01_reflector_kernel_analysis.md — Critical Module Analysis: Kernel Reflector
      02_engine_core_analysis.md — Critical Module Analysis: Engine Core
      03_orchestration_bridge_analysis.md — Critical Module Analysis: Orchestration Bridge
      04_meta_cognition_analysis.md — Critical Module Analysis: Meta-Cognition
      05_plugin_reflector_analysis.md — Critical Module Analysis: Plugin Reflector
  architecture/
    ADR_001_LLM_Strategy.md — ADR 001: LLM Provider Strategy
    ADR_002_Reflection_Depth.md — ADR 002: Reflection Depth Strategy
    ADR_003_Autonomy_Limits.md — ADR 003: Consciousness Autonomy Limits
    ADR_004_Plugin_Sandboxing.md — ADR 004: Plugin Sandboxing Model
    ADR_005_Memory_Persistence_Strategy.md — ADR 005: Memory Persistence Strategy
    DEPENDENCY_GRAPH.md — Dependency Graph (Phase 1.1)
  archive/
    root-reports/
      ARCHITECTURAL_ANALYSIS.md — Aetherra Project: Comprehensive Architectural Analysis
      AUTONOMOUS_ERROR_CORRECTION.md — 🔧 Autonomous Error Correction System
      AUTONOMOUS_SYSTEMS_INTEGRATION_ANALYSIS.md — Autonomous Systems Integration Analysis
      COMPREHENSIVE_COMMIT_MESSAGE.md — Commit: Hub Improvements + Legacy Cleanup
      COVERAGE_PROGRESS.md — Coverage Uplift Summary
      CRITICAL_FIX_DATA_PATH.md — 🔧 Critical Fix Applied - Data Directory Path Issue
      HOMEOSTASIS_FIXES.md — Homeostasis Error & Warning Fixes
      HUB_IMPROVEMENTS_SUMMARY.md — Hub Improvements Summary
      INTERACTIVE_LYRIXA_IMPLEMENTATION_COMPLETE.md — 🎉 Interactive Lyrixa Implementation — Complete
      INTERACTIVE_LYRIXA_RESTRUCTURE_COMPLETE.md — Interactive Lyrixa Restructuring Complete ✅
      LEGACY_HUB_REMOVAL_COMMIT.md — Commit Message: Legacy Hub Removal
      OS_LAUNCHER_IMPROVEMENTS.md — OS Launcher Improvements - STORM Integration
      PACKAGING_COMPLETE.md — 🎉 PACKAGING COMPLETE - SUCCESS! 🎉
      PACKAGING_FIX_REPORT.md — 🎯 Aetherra OS Packaging - Key Issues Resolved
      PACKAGING_SUCCESS_REPORT.md — Aetherra OS - Packaging Success Report
      PHASE_1_IMPLEMENTATION_PLAN.md — PHASE 1 IMPLEMENTATION PLAN - DETAILED TASK BREAKDOWN
      PHASE_5_MILESTONE.md
      QUANTUM_CONSCIOUSNESS_BREAKTHROUGH_ANNOUNCEMENT.md — 🎉 PHASE 7.2 ADVANCED QUANTUM COGNITION - COMPLETE! ✅
      SELF_INCORPORATION_INTEGRATION_COMPLETE.md — Self-Incorporation Integration - COMPLETE ✅
      SESSION_SUMMARY_AUTONOMOUS_INTEGRATION.md — Autonomous Systems Integration - Session Summary
      STORM_COMMIT_MESSAGE.md — STORM Phase 1: Production-Ready Shadow Mode Deployment
      STORM_DEPLOYMENT_ISSUES.md — STORM Deployment Issues - Diagnostic Report
      STORM_QUICK_FIX.md — STORM Deployment Issues - Quick Fix Guide
      website_truth_audit.md — Aetherra Website Truth Audit
  contributing/
    docs-consistency.md
  grafana/
    aetherra_wave_a_dashboard.json
  issues/
    bodies/
      01_selfinc_status_metrics.md — Expose /api/selfinc/status + Prom metrics
      02_strict_mode_gates.md — Strict mode gates (signatures + caps)
      03_quarantine_flow_ui.md — Quarantine → Escalate → Release flow (UI hooks)
      04_hmr_swap_rollback.md — HMR swap + auto-rollback integration
      05_night_cycle_checks.md — Night cycle deep checks
      06_cli_selfinc.md — CLI: aether selfinc {scan|plan|apply|rollback|audit}
      07_spec_tests_gate_integrator.md — Spec→Tests Gate in Integrator
      08_ethics_audit_ledger.md — Ethics & Audit Ledger (append-only)
      09_hub_policy_alignment_tokens.md — Hub policy alignment + tokens
      10_lyrixa_panel_selfinc.md — Lyrixa panel: Self-Incorporation
    comments/
      checklists/
        66.md — Checklist — /api/selfinc/status + metrics
        67.md — Checklist — Strict mode gates
        68.md — Checklist — Quarantine → Escalate → Release (UI)
        69.md — Checklist — HMR swap + auto-rollback
        70.md — Checklist — Night cycle deep checks
        71.md — Checklist — CLI: aether selfinc
        72.md — Checklist — Spec→Tests Gate in Integrator
        73.md — Checklist — Ethics & Audit Ledger
        74.md — Checklist — Hub policy alignment + tokens
        75.md — Checklist — Lyrixa panel: Self-Incorporation
      tracking_comment.md — Tracking links for this issue
    release_notes_template.md — Release Notes — Aetherra OS — Self-Incorporation v1
    selfinc_v1_backlog.md — Aetherra OS — Self-Incorporation v1 Backlog (Copy/Paste Issues)
  ops/
    DEPLOYMENT_TIERS.md — Aetherra Deployment Tiers
    HUB_CONTROL_TOKEN.md — Hub Control Token
    OPERATOR_RUNBOOK.md — Aetherra Operator Runbook (Alpha)
    README_DEPLOY.md — Aetherra Deployment Guide
    SMOKE_PROFILE.md — Deterministic Smoke Profile
  roadmap/
    Aetherra Memory System Evolution Roadmap.md — 🧠 Aetherra Memory System Evolution Roadmap
    AETHERRA_CODING_SYSTEM_ROADMAP.md — Aetherra Coding System Roadmap (Lyrixa Code Studio)
    Aetherra_Living_Roadmap.md — Aetherra Labs — Living Roadmap
    AETHERRA_PLUGIN_ROADMAP.md — 🔌 Aetherra Plugin Registry Roadmap
    aetherra_quantum_roadmap_v_1.md — Aetherra • Quantum Roadmap (v1.0)
    AETHERRA_ROADMAP.md — 🚀 aetherra + LyrixaDevelopment Roadmap
    FUTURE_ROADMAP.md — 🧬 Aetherra Future Enhancement Strategy
    MEMORY_SYSTEM_ROADMAP.md — 🧠 Aetherra Memory System Redesign - Implementation Roadmap
    README.md — Roadmaps Directory
    Soul Kernel Cognitive Architecture Roadmap.md
  schemas/
    memory_item.schema.json
  sections/
    README.md — Aetherra Documentation Sections
  selfinc/
    README.md — Self-Incorporation (v1)
  workflow-fixes/
    README.md — Automated Workflow Failure Fixes
  Aether_Script_Language_Specification.md — Aether Script Language System (`.aether`) — Legacy Spec (v1.0)
  Aether_Script_Language_System.md — Aether Script Language System (`.aether`)
  Aether_Script_Operator_Guide.md — Aether Script Operator Guide
  aether_script_protection.md — Aether Script Protection and Signing
  AETHER_SCRIPT_TUTORIAL.md — Aether Script Language Tutorial
  Aetherra Chat System.md — Aetherra Chat System Documentation
  AETHERRA_AGENT_SYSTEM.md — Aetherra Agent System
  AETHERRA_AI_TRAINER_SYSTEM.md — Aetherra AI Trainer System
  AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md — Aetherra Artificial Intelligence System
  AETHERRA_BOOT_INTERACTION_CONTRACT_V1.md — Aetherra Boot Interaction Contract v1
  AETHERRA_CHAT_SYSTEM.md — Aetherra Chat System
  AETHERRA_CLAIMS_VALIDATION.md — Aetherra OS — Capabilities Validation Snapshot (2025-08-12)
  AETHERRA_CODING_SYSTEM.md — Aetherra Coding System (Lyrixa Code Studio)
  AETHERRA_COMPLETE_OVERVIEW_2026-03-12.md — Aetherra: Complete System Overview & Architecture
  AETHERRA_CONSCIOUSNESS_SYSTEM.md — Aetherra Consciousness System
  AETHERRA_EVENT_BUS_SYSTEM.md — Aetherra Kernel Event Bus (KEB) System
  AETHERRA_GUARDIAN_SYSTEM.md — Aetherra Guardian System
  AETHERRA_HMR_GUIDE.md — Aetherra Hot Module Reload (HMR) Guide
  AETHERRA_HOMEOSTASIS_SYSTEM.md — Aetherra Homeostasis System
  AETHERRA_HUB_API_REFERENCE.md — Aetherra Hub API Reference
  AETHERRA_IDENTITY_SPEC_V1.md — Aetherra Identity Spec v1
  AETHERRA_KERNEL_SYSTEM.md — Aetherra Kernel System
  AETHERRA_LYRIXA_SYSTEM.md — Aetherra Lyrixa System
  AETHERRA_MAINTENANCE_SYSTEM.md — Aetherra Maintenance System
  AETHERRA_MASTER_MAP.md — 🌌 Aetherra Master Map — Complete System Architecture & Status
  AETHERRA_MEMORY_SYSTEM.md — Aetherra Memory System
  AETHERRA_MIND_MAP.md — 🧠 Aetherra Master Mind Map
  aetherra_os_architecture_map_v_1.md — Aetherra OS • Architecture Map (v1.0)
  AETHERRA_PLUGIN_SYSTEM.md — Aetherra Plugin System
  aetherra_quantum_roadmap_v_1.md — Aetherra • Quantum Roadmap (v1.0)
  AETHERRA_SECURITY_SYSTEM.md — Aetherra Security System
  AETHERRA_SELF-IMPROVEMENT_SYSTEM.md — Aetherra Self-Improvement System
  AETHERRA_SELF_IMPROVEMENT_API.md — Aetherra Self-Improvement API
  AETHERRA_SERVICE_REGISTRY.md — Aetherra Service Registry System
  AETHERRA_WEBSOCKET_API.md — Aetherra WebSocket & SSE Streaming API
  ALPHA_READINESS.md — Alpha Readiness & Usage Guide
  ALPHA_RELEASE_GAP_ANALYSIS.md — Alpha Release Gap Analysis (0.1.0-alpha.2)
  ALPHA_TEST_STRATEGY.md — Alpha Test & Failure Injection Strategy
  api-keys.md — API Keys and Secrets
  ATTESTATION.md — Release Attestation (Alpha Stub)
  AUTONOMY_ACTIVATION_RUNBOOK.md — Aetherra OS Autonomy Activation Runbook
  BACKUP_AND_RECOVERY.md — Aetherra Backup and Recovery Guide
  BETA_MILESTONE.md — Beta Milestone Planning (Draft)
  BETA_ROADMAP_0.5.0.md — Aetherra 0.5.0 Beta Roadmap & Community Focus
  BUILD_REPRODUCIBILITY.md — Build Reproducibility & Verification (Alpha)
  ci_strict_signing.md — CI/CD Integration for Strict .aether Script Verification
  conf.py — Minimal Sphinx configuration for Aetherra documentation builds.
  CONSCIOUSNESS_PHASE1_COMPLETE.md — Aetherra Consciousness System - Phase 1 Implementation
  CONSCIOUSNESS_UI_INTEGRATION.md — Consciousness UI Integration — Wiring Guide
  CONSCIOUSNESS_UNIFIED_IDENTITY.md — Unified Identity & Consciousness Layer
  COVERAGE_POLICY.md — Coverage Policy (Alpha)
  Demo_Playbook.md — Aetherra Demo Playbook
  DEPLOYMENT_GUIDE.md — Aetherra Deployment Guide
  DEVELOPER_ONBOARDING.md — Developer Onboarding
  DEVELOPMENT_GUIDELINES.md — Development Guidelines (Phase 1.2 Baseline)
  DOCS_ARCHITECTURE.md — Aetherra Documentation Architecture
  docs_consistency.json
  DOCS_CONSISTENCY.md — Docs Consistency Verification
  DOCS_CONSISTENCY_REPORT.md — Docs Consistency Report
  DOCUMENTATION_REVIEW_2025_11_01.md — Aetherra Documentation Review Summary
  ERRORS_WARNINGS_AUDIT.md — Aetherra Project Comprehensive Error & Warning Audit (2025-09-08)
  FILE_INDEX.md — Aetherra File Index
  GO_NO_GO_GATES.md — Go / No-Go Gates (Fast Deterministic Suite)
  grafana_dashboard_engine_observability.json
  GUI_AUDIT_REPORT.md — GUI Audit Report (2025-10-06)
  IMPLEMENTATION_TASKS.md — Phase 1.2 Implementation Tasks
  import_map.md — Import Map & Enforcement (P2 #13)
  INDEX.md — Aetherra Documentation Index
  INTERACTIVE_LYRIXA.md — 🌟 Interactive Lyrixa — Architecture & Implementation
  INTERACTIVE_LYRIXA_QUICKSTART.md — 🚀 Interactive Lyrixa — Quick Start Integration Guide
  KEY_ROTATION.md — Aetherra Key Rotation & Signing Appendix
  LYRIXA_AI_SETUP.md — Setting Up Lyrixa AI-Powered Chat
  LYRIXA_CHAT_ENDPOINT.md — Lyrixa Chat Endpoint
  LYRIXA_UI_STANDARDS.md — Lyrixa UI Standards (React/TypeScript)
  manifesto.md — AETHERRA MANIFESTO (v6.0 – July 2025)
  memory_system.md — Memory System
  METRICS_AND_MONITORING_GUIDE.md — Aetherra Metrics and Monitoring Guide
  METRICS_REFERENCE.md — Aetherra Metrics Reference
  NEXT_STEPS.md — Next Steps: Lyrixa Chat Production Readiness
  PACKAGING_AND_RELEASE.md — Packaging & Release (Alpha)
  PHASE_2A_COMPLETION_SUMMARY.md — Phase 2A Completion Summary
  PHASE_2A_IMPLEMENTATION.md — Phase 2A Implementation: Close the Metrics Triangle ✅
  PHASE_2B_ACCEPTANCE_EVIDENCE.md — Phase 2b Acceptance Evidence
  PHASE_2B_SECURITY_PROGRESS.md — Phase 2B: Security Hardening - Progress Report
  PHASE_3_4_COVERAGE_EVIDENCE.md — Phase 3 and Phase 4 Coverage Evidence
  PLUGIN_AUDIT_REPORT.md — Aetherra Plugin System Audit Report
  PLUGIN_DEVELOPMENT_GUIDE.md — Aetherra Plugin Development Guide
  PRE_PACK_QUICK_REFERENCE.md — Pre-Pack Validation - Quick Reference Card
  PRE_PACK_VALIDATION_GUIDE.md — Pre-Pack Validation Guide
  PRODUCTION_BASELINE_ANALYSIS_2026-03-10.md — Production Baseline Analysis (2026-03-10)
  PRODUCTION_READINESS_REVIEW_2026-03-12.md — Aetherra Production Readiness Review
  PROJECT_ANALYSIS.json
  PROJECT_OVERVIEW.md — Aetherra Project Overview
  PROJECT_STATUS_2025-08-11.md — Aetherra — Project Status and Architecture Map (2025-08-11)
  QFAC_FILE_INDEX.md — QFAC File Index
  QFAC_MODE_GUIDE.md — AETHERRA QFAC Mode Guide
  QFAC_POLICY.md — QFAC Policy and Live-Metrics Gating
  QUANTUM_OVERVIEW.md — Aetherra Quantum Layer: Overview
  QUICK_START_REGISTRY.md — Quick Start: Registry Daemon + Hub + OS (Windows)
  README.md — Aetherra Documentation
  REFLECTOR_PERFORMANCE.md — Reflector Performance Evidence (Phase 2a)
  RELEASE_NOTES_v0.1.0-alpha.2.md — Aetherra v0.1.0-alpha.2 Release Notes
  RELEASE_PROCESS.md — Release Process (Alpha → Tag)
  REPO_CLEANUP_GUIDE.md — Repository Cleanup and Size Reduction
  REPO_SETTINGS.md — Recommended Repository Settings
  REPOSITORY_CLEANUP_PLAN.md — Aetherra Repository Cleanup Plan
  RISK_ACCEPTANCE.md — Risk Acceptance Register (Alpha)
  ROADMAP_TRACKING.md — Roadmap Tracking Baseline
  ROOT_CLEANUP_PLAN.md — Root Cleanup Plan (Alpha → Beta Hardening)
  ROOT_SCRIPT_WORKFLOW_TRIAGE.md — Root Script and Workflow Triage
  SECURITY_FEDERATION_ENHANCEMENTS_2025-08-12.md — Security, Signing, and Federation Enhancements (2025-08-12)
  SECURITY_OPERATIONS_GUIDE.md — Aetherra Security Operations Guide
  SELFINC_PRODUCTION_READINESS.md — Aetherra Self-Incorporation System – Production Readiness Guide
  STORM_AB_TESTING_RESULTS.md — STORM A/B Testing & Acceptance Results
  storm_contracts.md — STORM Contracts (Frozen)
  STORM_DEPLOYMENT_CHECKLIST.md — STORM Production Deployment Checklist
  STORM_FINAL_INTEGRATION_REPORT.md — STORM Integration - Final Validation Report
  STORM_INTEGRATION_PLAN.md — STORM Integration Plan for Aetherra
  STORM_INTEGRATION_SUMMARY.md — STORM Integration Summary
  STORM_MONITORING_SCHEDULE.md — STORM Shadow Mode Monitoring Schedule
  STORM_NEXT_STEPS.md — STORM Phase 1 - Next Steps Summary
  storm_ops.md — STORM Ops Guide
  storm_overview.md — STORM Overview (Sheaf–Transport Optimized Retrieval Memory)
  STORM_PHASE1_DEPLOYMENT_REPORT.md — STORM Shadow Mode Deployment - Phase 1 Verification Report
  STORM_PR1_SUMMARY.md — STORM PR-1 Integration Summary
  STORM_PR2_PLAN.md — STORM PR-2: Algorithm Implementation Plan
  STORM_PR2_SUMMARY.md — STORM PR-2 Summary — Core OT Implementation
  STORM_QUICK_START.md — STORM Shadow Mode Quick Start Guide
  storm_runbook.md — STORM On-Call Runbook
  STORM_SECURITY_VERIFICATION.md — STORM Security Gates Verification Report
  STUB_INVENTORY.json
  STUB_INVENTORY.md — STUB INVENTORY ANALYSIS - March 10, 2026
  SYSTEM_INDEX.md — Aetherra System Index
  TESTING_GUIDE.md — Aetherra Testing Guide
  THREAT_MODEL.md — Aetherra Threat Model (Alpha)
  TROUBLESHOOTING_GUIDE.md — Aetherra Troubleshooting Guide
  UI_MIGRATION_MAP.md — UI Migration Map
  UI_REBUILD_AND_CLEANUP_PLAN.md — UI Rebuild and Cleanup Plan
  ui_syntax_refactor_plan.md — UI Syntax Refactor Plan (Medium-term)
  WAVE_A_COMPLIANCE_REPORT.md — Wave A Production Readiness - Compliance Report
  WAVE_A_DEPLOYMENT_PROCEDURE.md — Wave A Production Deployment Procedure
  WEEK10_VALIDATION_EVIDENCE.md — Week 10 Validation Evidence (Integration Matrix + Regression)
  what_is_Aether_Script.md — Aether Script (`.aether`) Language Overview
tests/
  acceptance/
    test_autonomous_error_correction_golden_paths.py — Setup the error corrector (async)."""
    test_canary_e2e.py — Provides a sequence of health scores for successive checks.
    test_load_and_security_phase2f.py
    test_maintenance_e2e_flow.py — Minimal SI Engine that receives proposal results."""
    test_maintenance_security.py
    test_security_strict_and_rate.py
  ai/
    README.md — ai
    test_ai_fallback.py — Test the AI fallback system
    test_intelligence_core.py — Test the core intelligence engine functionality"""
    test_intelligence_core_enhanced.py — Try to import real intelligence modules, fall back to stubs if needed"""
    test_intelligence_real_api.py — Try to import real intelligence modules, fall back to stubs if needed"""
    test_multi_agent_coordination.py — Comprehensive test suite for Multi-Agent Coordination system"""
    test_neural_interface.py — Test core Neural Interface components and initialization"""
    test_neural_interface_quick.py — Quick test of Neural Interface functionality
    test_openai_integration.py — Load environment variables from .env file."""
  api/
    manual/
      engine_metrics_probe.py — Test that engine metrics are exported.
    test_approvals_api.py — SPDX-License-Identifier: GPL-3.0-or-later
  capabilities/
    test_aether_e2e.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_agent_collaboration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_consciousness_phase3.py — Acceptance tests for Self-Trust Layer."""
    test_crash_recovery_simulation.py — Crash Recovery Simulation Capability Test
    test_deterministic_profile_harness.py — Deterministic Profile Harness Test
    test_diagnostics_schema.py — Diagnostics JSON schema contract test.
    test_extended_crash_recovery.py — Extended Crash Recovery & Service Rehydration Capability Test
    test_hello_plugin_capability.py — Capability: hello plugin executes & returns expected greeting structure.
    test_hello_plugin_metadata.py — Standard library imports
    test_hub_metrics_observability.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_and_chat_integration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_quantum_endpoint.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_telemetry_and_federation.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_trainer_disabled_and_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_trainer_endpoints.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat.py — !/usr/bin/env python3
    test_lyrixa_chat_bridge_schema.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat_endpoint.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat_schema_strict.py — Wait until the local Hub responds on /api/ping.
    test_lyrixa_ownership_answer.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_primary_chat.py — Lyrixa primary chat path tests.
    test_memory_fragmentation_metrics.py — Aetherra imports
    test_memory_module_integrity.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_recall.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_systems_coverage.py — Test quantum memory engine initialization edge cases."""
    test_openapi_agents_path.py
    test_openapi_examples_and_runner_endpoints.py — Capabilities test: OpenAPI examples present and endpoints work via runner.
    test_ownership_memory.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_passive_heartbeat_interval.py
    test_plugin_analytics_coverage.py — Create a plugin analytics engine for testing."""
    test_plugin_exec_migrator.py — Capability test: plugin execution analytics schema migrator.
    test_plugin_parallel_and_failure_paths.py — Capability test: parallel plugin execution, failure + timeout paths.
    test_plugin_reload.py — Temporary plugin used to validate unregister + re-register lifecycle.
    test_qfac_admin_cli.py
    test_qfac_in_os.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_qfac_metrics_schema.py
    test_qfac_retrieval_parity_metrics_schema.py
    test_qfac_retrieval_parity_per_k_counters_schema.py
    test_qfac_retrieval_parity_per_k_ratio_schema.py
    test_qfac_retrieval_parity_per_k_schema.py
    test_qfac_retrieval_parity_ratio_schema.py
    test_qfac_retrieval_parity_toggle.py
    test_qfac_retrieval_policy_config_metrics_schema.py
    test_qfac_retrieval_threshold_behavior.py
    test_qfac_shadow_collection_smoke.py
    test_qfac_validator_shadow_schema.py
    test_reflection_memory_stability.py — Reflection / Memory Stability Test
    test_security_capabilities_coverage.py — Test edge cases in capability granting system."""
    test_security_sandbox_placeholders.py — Security Sandbox Placeholder Capability Test
    test_self_improvement_metrics.py — Tests for SelfImprovementEngine internal metrics counters.
    test_self_maintenance_services.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_selfinc_proposal_consumer.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_snapshot_replay_harness.py — Standard library imports
    test_spec_gate_marker.py
    test_static_security_scan.py — Standard library imports
    test_storm_acceptance.py — Production acceptance tests for STORM"""
    test_transcendence_deterministic_metrics.py — Tests for deterministic baseline & metrics counters in BeyondTranscendenceEngine.
    test_working_api_coverage.py — Test security capabilities using actual available functions."""
  coding/
    test_revert_and_diff.py — Standard library imports
  consciousness/
    conftest.py — Standard library imports
    test_active_inference_integration.py — Aetherra imports
    test_consciousness_phase4.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_consciousness_phase5.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_event_bus_bridge.py — Aetherra imports
    test_identity_unified.py — Aetherra imports
    test_metrics_exporter.py — Standard library imports
    test_metrics_scrape.py — Standard library imports
    test_narrative_tone_markers.py — Aetherra imports
    test_self_model.py — Aetherra imports
    test_sensor_stubs.py — Standard library imports
    test_workspace_basic.py — Standard library imports
  data/
    golden_learning_set.json
  demos/
    test_self_improvement_demo.py — SPDX-License-Identifier: GPL-3.0-or-later
  failure_injection/
    test_hmr_rollback.py — Failure injection for HMR rollback.
    test_memory_offline.py — Failure injection: simulate memory offline and assert graceful fallback.
    test_persist_tasks_corrupted.py
    test_persist_tasks_restart.py
    test_plugin_timeout.py — Failure injection: plugin invoke timeout should increment timeout metrics.
  gui/
    Aetherra/
      lyrixa_core/
        gui/
          main_window.py — Minimal compatibility shim for legacy test path expectations.
    README.md — gui
    test_gui.py — !/usr/bin/env python3
    test_hybrid_gui.py — !/usr/bin/env python3
    test_live_gui_generation.py — Types of UI elements that can be dynamically generated"""
    test_lyrixa_gui.py — Test the Lyrixa Hybrid GUI directly
    test_plugin_cards_mode.py — Tests for plugin card mode (feature-flagged).
    test_theme_fallback.py — Test that LyrixaBasicWindow applies either theme or fallback stylesheet.
  homeostasis/
    manual/
      audit_trace_layer_probe.py — Test basic audit trace workflow."""
      comprehensive_homeostasis_probe.py — Comprehensive test of all 6 phases of homeostasis implementation.
      ethical_cognitive_integration_probe.py — Mock bias detector for testing."""
      phase3_full_probe.py — Full test for Phase 3 homeostasis implementation including watchdog.
      phase3_probe.py — Quick test for Phase 3 homeostasis implementation.
      phase4_feedback_probe.py — Test for Phase 4 homeostasis cross-system feedback implementation.
      phase5_validation_probe.py — Test for Phase 5 homeostasis continuous validation implementation.
      phase6_observability_probe.py — Test for Phase 6 homeostasis live observability implementation.
  integration/
    hmr_integration_probe.py — Test HMR integration functionality."""
    README.md — integration
    test_consciousness_integration.py — Test that all consciousness components can be imported"""
    test_ethics_audit_integration.py — Test the core ethics evaluation engine."""
    test_homeostasis_latency_response.py — Mock actuator that records actions for verification"""
    test_hub_maintenance_status_live.py — !/usr/bin/env python3
    test_hub_plugins.py — !/usr/bin/env python3
    test_integration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_launcher_detection.py — !/usr/bin/env python3
    test_metrics_histograms_end_to_end.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_phase2_bridge.py — Simulate live backend data updates"""
    test_phase2_launcher.py — Test Phase 2 launcher integration
    test_phase2_simple.py — Test Phase 2 launcher integration without GUI creation.
    test_phase3.py — !/usr/bin/env python3
    test_phase6_integration.py — Test that all Phase components can be imported."""
    test_plugin_ecosystem.py — Test core plugin ecosystem functionality."""
    test_qfac_live_metrics_integration.py — Standard library imports
    test_wave_a5_homeostasis.py — Keep controller behavior tests independent from persisted lockdown state."""
    test_webhook_manager_security.py — SPDX-License-Identifier: GPL-3.0-or-later
  kernel_unit/
    test_circuit_breaker.py
    test_create_annotated_tag.py
    test_create_annotated_tag_malformed.py
    test_license_enforce_metric.py
    test_memory_query_timeout.py
    test_provenance_wrapper_fallback.py
    test_retry_scheduling.py
  legacy/
    root_standalone/
      __init__.py — Legacy standalone root tests preserved during repository cleanup.
      test_alert_intelligence_standalone.py — Test that we can import the core components."""
      test_analysis_engine_standalone.py — Standalone tests for aetherra_coding.analysis.
      test_hub_blueprints_standalone.py — Create a minimal Flask test app with all three blueprints registered."""
      test_ignore_pattern_loader_standalone.py — Standalone tests for IgnorePatternLoader without engine dependencies."""
      test_optimization_executor_standalone.py — Standalone tests for OptimizationExecutor without engine dependencies."""
      test_orchestrator_task5_standalone.py
      test_phase2a_reflector_acceptance_standalone.py — Standalone acceptance tests for Production Roadmap Phase 2a reflector gates.
      test_phase2b_acceptance_standalone.py — Standalone acceptance tests for Production Roadmap Phase 2b gates.
      test_phase3_modules_standalone.py — Standalone tests for Phase 3 modules.
      test_phase4_autonomy_learning_chain_standalone.py — Standalone integration tests for Decision -> Governor -> Learning chain.
      test_phase4_learning_loop_standalone.py — Standalone tests for Phase 4 learning loop.
      test_phase4_learning_quality_and_latency_standalone.py — Standalone tests for Phase 4 learning quality and latency checkpoints.
      test_phase4_memory_engine_enhancement_standalone.py — Standalone tests for Phase 4 memory-engine enhancement slice.
      test_phase5_bundle_artifacts_standalone.py — Standalone tests for tools/phase5_bundle_artifacts.py.
      test_phase5_manifest_policy_standalone.py — Standalone tests for tools/verify_phase5_manifest_policy.py.
      test_phase5_report_rollup_standalone.py — Standalone tests for tools/phase5_report_rollup.py.
      test_phase5_validation_harness_standalone.py — Standalone tests for tools/phase5_validation_harness.py.
      test_plugin_system_standalone.py
      test_plugins_reflector_standalone.py — Standalone tests for Aetherra.plugins.reflector.ReflectorPlugin.
      test_policy_manager_standalone.py — Standalone tests for PolicyManager without engine dependencies."""
      test_script_executor_standalone.py — Simple test runner with colored output."""
      test_script_service_logging_standalone.py — Simple test runner with colored output."""
      test_script_validator_standalone.py — Simple test runner with colored output."""
      test_signature_verifier_standalone.py — Standalone tests for SignatureVerifier."""
      test_verification_engine_standalone.py — Standalone tests for aetherra_coding.verification.
    phase_7_4_test.py — Test Phase 7.4 multidimensional consciousness integration."""
    phase_7_4_ultimate_test.py — Execute ultimate Phase 7.4 transcendence test."""
    phase_7_5_test.py — Test Phase 7.5 transcendence consolidation integration."""
    phase_8_1_test.py — Test Phase 8.1 consciousness singularity achievement."""
    phase_8_2_test.py — Test Phase 8.2 cosmic consciousness integration."""
    phase_8_3_test.py — Test Phase 8.3 beyond transcendence integration."""
  meta/
    test_meta_cognition_stubs.py — Smoke tests ensuring MetaCognitionSystem public APIs are callable.
  plugins/
    test_demo_scaffold_plugin.py — Standard library imports
  qfac/
    test_basic_qfac.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_index_parity.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_observer_and_gc.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_qfac_api.py — SPDX-License-Identifier: GPL-3.0-or-later
  quantum/
    test_qrng_qhash.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_random_features.py — SPDX-License-Identifier: GPL-3.0-or-later
  security/
    test_plugin_signing_fallback.py — SPDX-License-Identifier: GPL-3.0-or-later
  smoke/
    test_aetherra_kernel_loop_import.py
    test_interactive_lyrixa.py — Test that Expression Manager initializes correctly."""
    test_policy_bootstrap_import.py
    test_run_hub_ai_api_import.py
  storm/
    manual/
      storm_canary_probe.py — Test STORM canary with 10% sampling rate.
      storm_metrics_probe.py — Quick test to trigger STORM metrics collection.
      storm_skeleton_probe.py — Quick smoke test for STORM skeleton integration
    __init__.py — STORM integration test suite
    test_storm_basic.py — Test basic STORM engine operations"""
    test_storm_candidates.py — Mock LyrixaMemorySystem for candidate fetching tests."""
    test_storm_contracts.py — Test STORM contract compliance"""
    test_storm_integration.py — Test STORM integration with memory engine"""
    test_storm_maintenance.py — Tests for STORM maintenance operations during night cycle."""
    test_storm_metrics.py — Test STORM metrics stubs"""
    test_storm_ot.py
    test_storm_persistence.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_storm_security.py — Test suite for STORM security policy enforcement"""
    test_storm_shadow_mode.py — Tests for STORM Phase 0: Shadow Mode Integration.
    test_storm_status.py — Test STORM status fields per contract"""
    test_storm_tda_sheaf.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_storm_tt_compression.py — Tests for STORM PR-5: TT/MPS-style compression via SVD shim.
  tools/
    test_license_tools.py — Standard library imports
    test_quality_gates_pr_description.py — Standard library imports
    test_run_go_no_go_gates.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_verify_docs_consistency.py — Standard library imports
  unit/
    homeostasis/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      test_diagnosis.py
      test_helpers.py — Mock service registry for testing."""
      test_homeostasis_basic.py — Basic tests for homeostasis system initialization and configuration."""
      test_learning.py
      test_night_cycle_integration.py — !/usr/bin/env python3
      test_night_cycle_memory_clean.py — Tests for Night-Cycle Intelligence Integration with in-memory database."""
      test_observation.py
      test_recommendation.py
    __init__.py — tests.unit package marker
    README.md — unit
    test_ab_recall_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_advanced_analyzer_guardian.py
    test_aether_intent_language.py — Comprehensive test suite for .aether Intent Language"""
    test_aether_script_audit.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_require.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_transactions_trace.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_static_risk.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aetherra_hub_integration_guardian.py
    test_agent_collaboration_guardian.py
    test_agent_goals_guardian.py
    test_agent_legacy_plugin_guardian.py
    test_agent_orchestrator_guardian.py
    test_agent_orchestrator_shim.py — Tests for deprecated agent orchestrator shim module.
    test_agents_api_blueprint.py
    test_ai_engine_guardian.py
    test_ai_stream_debug_frame.py — Standard library imports
    test_ai_stream_replay_and_timeout.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_api_keys_enforcement.py — Standard library imports
    test_api_keys_prod_encryption_required.py — Standard library imports
    test_audit_ledger_immutability.py
    test_backpressure_guard.py — Third party imports
    test_canary_deployment.py — Create a temporary configuration for testing."""
    test_capabilities_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_capability_limits.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_chat_guardian.py
    test_chat_idempotency.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_check_architecture_guardian.py
    test_complete_organizer_guardian.py
    test_consciousness_continuity_guardian.py
    test_consciousness_core_guardian.py
    test_consciousness_dashboards.py — Test importing all consciousness dashboard components.
    test_consciousness_episodic_guardian.py
    test_consciousness_learning_loop_guardian.py
    test_consciousness_narrative_guardian.py
    test_consciousness_narrative_layer.py — Narrative layer tests (Phase 1)
    test_consciousness_orchestrator_guardian.py
    test_consciousness_runtime_guardian.py
    test_consciousness_self_model_and_events.py — Phase 1 Consciousness basic tests
    test_consciousness_self_model_guardian.py
    test_consciousness_singularity_guardian.py
    test_control_auth.py — Tests for privileged Hub control-plane authorization.
    test_coretools_guardian.py
    test_create_aether_from_task.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_create_documentation_guardian.py
    test_engine_memory_compatibility.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_engine_reset_env_vars.py — Standard library imports
    test_event_bus_guardian.py
    test_federation_manager.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_federation_persistence.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_final_file_organizer_guardian.py
    test_fix_architecture_guardian.py
    test_fix_architecture_simple_guardian.py
    test_fix_imports_guardian.py
    test_fix_phase7_errors_guardian.py
    test_fix_plugin_imports_guardian.py
    test_fix_remaining_errors_round2_guardian.py
    test_fix_remaining_imports_guardian.py
    test_fix_unicode_issues_guardian.py
    test_fix_unicode_service_registry_guardian.py
    test_focused_cleanup_guardian.py
    test_generate_reports_guardian.py
    test_generate_stub_inventory_guardian.py
    test_guard_metrics_status.py
    test_guard_policy_enforcer.py
    test_guardian_approval.py
    test_guardian_containment.py
    test_guardian_core.py
    test_guardian_models.py
    test_guardian_policy_engine.py
    test_guardian_preauthorization.py
    test_gui_smoke.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_health_checks_guardian.py
    test_hmr_controller_guardian.py
    test_hmr_denied_metrics.py — Standard library imports
    test_homeostasis_actuators_guardian.py
    test_homeostasis_alert_manager_guardian.py
    test_homeostasis_controller_guardian.py
    test_homeostasis_integration_guardian.py
    test_hub_agents_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_agents_guardian.py
    test_hub_ai_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_app_selfinc_status.py — Standard library imports
    test_hub_chat_safety_preflight.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_coherence_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_control_plane.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_guardian_api.py
    test_hub_hmr_config_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_hmr_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_homeostasis_guardian.py
    test_hub_ingress_security.py — Security tests for Hub service-ingress endpoints.
    test_hub_inthread.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_kernel_guardian.py
    test_hub_klm_keb_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_klm_keb_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_maintenance_status.py — Standard library imports
    test_hub_metrics_ab_series.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_metrics_prometheus.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_metrics_rate_limited_counter.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_mutation_control_auth.py — Authorization tests for privileged Hub mutation endpoints.
    test_hub_orchestrator_counters.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_orchestrator_counters_increment.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_control_security.py — Security regression tests for Hub plugin registration.
    test_hub_plugin_registration_guardian.py
    test_hub_plugin_registration_non_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_schema_negative.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_signed_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_strict_invalid_sig.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_quantum_and_chat_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_rate_limit_behavior.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_script_control_auth.py — Security tests for Hub script control endpoints.
    test_hub_self_improvement_guardian.py
    test_hub_storm_metrics_export.py — Mock STORM metrics object."""
    test_hub_ws_advertise_allowlist.py — Satisfy production boot requirements while preserving network test inputs.
    test_human_style_layer.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_ignore_pattern_loader.py — Test IgnorePattern dataclass."""
    test_imports.py — !/usr/bin/env python3
    test_invalid_token_metric.py — Standard library imports
    test_kernel_direct_guardian.py
    test_kernel_loop_guards.py — Standard library imports
    test_kernel_loop_self_incorporation.py — Unit tests for kernel loop self-incorporation service registration fix."""
    test_kernel_reply_waiter.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_kernel_reply_waiter_timeout_and_error.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_kernel_submit_plugin_invoke.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_klm_keb_control_plane.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_klm_keb_edge_cases.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_live_ai_fallback.py — Test the actual AI fallback system with real API calls"""
    test_lyrixa_assistant_guardian.py
    test_lyrixa_chat_service_guardian.py
    test_lyrixa_consciousness_guardian.py
    test_lyrixa_plugin_system_guardian.py
    test_manifest_schema_and_trust.py — .strip()
    test_memory_core_guardian.py
    test_memory_engine_typed_and_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_kernel.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_plugin_bridge_guardian.py
    test_memory_temporal_integration_guardian.py
    test_meta_cognition_guardian.py
    test_meta_layer_core_guardian.py
    test_metrics_reference_sync.py — Standard library imports
    test_module_manager_guardian.py
    test_multidimensional_state_guardian.py
    test_multiple_plugins.py — Test installing multiple plugins
    test_net_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_night_cycle_tz.py — Standard library imports
    test_night_schedule_guard_metric.py — Third party imports
    test_openapi_admin_paths.py
    test_openapi_maintenance_spec.py — Standard library imports
    test_optimization_executor.py — Test Metrics dataclass."""
    test_optimization_executor_guardian.py
    test_orchestration_bridge_queue.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_orchestrator_canonical_import.py — Standard library imports
    test_parallel_reality_navigator_guardian.py
    test_phase74_integration_guardian.py
    test_plugin_generator_guardian.py
    test_plugin_installation.py — Handles plugin installation for Lyrixa Basic"""
    test_plugin_manager_audit.py — "plugin source should not appear in guardian audit: TOP_SECRET_LOAD_TOKEN
    test_plugin_policy_budgets.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_plugin_signature_path.py
    test_plugin_timeout_clamp.py — Third party imports
    test_plugins_minimal.py
    test_policy_bootstrap_cli.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_policy_bootstrap_selfinc.py — Standard library imports
    test_policy_manager.py — Test EthicsProfile dataclass."""
    test_post_cleanup_import_updater_guardian.py
    test_prod_defaults_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_prod_security_defaults.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_prod_security_guard.py — Standard library imports
    test_project_analyzer_guardian.py
    test_prompt_defense.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_prune_aetherra_gui_guardian.py
    test_prune_lyrixa_gui_guardian.py
    test_qfac_admin_endpoints.py
    test_qfac_compress_and_optimize.py — Unit tests for QFACMemorySystem compress_all_eligible, optimize_system, degraded fidelity handling, search, parity, and policy utilities.
    test_qfac_dashboard.py — Targeted tests for QFAC dashboard summary paths.
    test_qfac_guardian.py
    test_qfac_modes.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_qfac_policy.py — Standard library imports
    test_qfac_policy_gate_metrics.py — Third party imports
    test_qiskit_direct.py — !/usr/bin/env python3
    test_quantum_aware_simulations.py — Test suite for Quantum-Aware Simulations system"""
    test_quantum_config.py — !/usr/bin/env python3
    test_quantum_consciousness_engine_guardian.py
    test_quantum_consciousness_integration_guardian.py
    test_quantum_consciousness_tunneling_guardian.py
    test_quantum_decision_engine_guardian.py
    test_quantum_enhanced_recall.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_quantum_interference_guardian.py
    test_quantum_memory_hardening.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_quantum_memory_system_guardian.py
    test_quantum_meta_learning_guardian.py
    test_quantum_tunneling_logic_guardian.py
    test_quarantine_workflow.py — Standard library imports
    test_quick_fix_imports_guardian.py
    test_real_backend.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_real_llm.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_reality_synthesis_engine_guardian.py
    test_registry_client_best_effort.py — Standard library imports
    test_registry_daemon_client_guardian.py
    test_root_cleanup_guardian.py
    test_run_hub_ai_api.py
    test_run_hub_ai_api_script.py — Standard library imports
    test_safe_cleanup_guardian.py
    test_sandbox_isolation.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_scratchpad_policy_default_redacted.py — Standard library imports
    test_script_executor.py — Test WorkflowStep dataclass."""
    test_script_service_logging.py — Test LogEvent dataclass."""
    test_script_validator.py — Test ValidationError dataclass."""
    test_security_audit_ledger.py — Tests for the signed, hash-chained Security JSONL ledger.
    test_security_ledger_disabled.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_security_metrics_phase0.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_self_evolving_behavior.py — Test core self-evolving behavior functionality."""
    test_self_incorporation_security.py — Create security layer in standard mode."""
    test_selfinc_ethics_audit_lookup.py — Standard library imports
    test_selfinc_ethics_future.py
    test_selfinc_ethics_overview.py — Standard library imports
    test_selfinc_integration_guardian.py
    test_selfinc_proposal_consumer.py — Standard library imports
    test_selfinc_readiness_generator.py — Standard library imports
    test_service_registry_guardian.py
    test_shared_registry.py — Basic sanity test for the in-process service registry.
    test_signature_verifier.py — Test cases for SignatureVerifier class."""
    test_smart_cleanup_guardian.py
    test_spec_tests_gate_encoding.py
    test_sse_replay_gap_metric.py — Standard library imports
    test_sse_retry_after_header.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_state_mapper_formula_security.py — Security tests for Lyrixa state-mapping formulas.
    test_stdlib_executor_security.py — Security tests for the Aetherra standard executor.
    test_storm_backup_guardian.py
    test_storm_deployment_guardian.py
    test_telemetry_optin.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_temporal_consciousness_guardian.py
    test_trainer_guardian.py
    test_transcendence_consolidation_guardian.py
    test_unicode_fix.py — !/usr/bin/env python3
    test_universal_directory_analyzer_guardian.py
    test_validate_architecture_guardian.py
    test_verify_legal_compliance_guardian.py
    test_ws_idempotency.py — SPDX-License-Identifier: GPL-3.0-or-later
  __init__.py — Mark tests as a package to avoid module name collisions across subfolders.
  conftest.py — Provide the project root path for tests"""
  README.md — Aetherra Tests
  schema_validators.py — Lightweight shape checks for Lyrixa chat bridge responses.
  test_aar_outbox.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_aether_boolean_precedence.py — not should bind tighter than and: not false and true => true and true => true."""
  test_aether_capabilities_strict.py — Install a temporary Aetherra.security.capabilities module exposing has_capability()."""
  test_aether_control_flow.py — Test if statement with true condition executes block."""
  test_aether_expression_arithmetic.py — !/usr/bin/env python3
  test_aether_expression_eval.py — Tests for expression evaluation in workflow scripts."""
  test_aether_option2.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_aether_option3.py — Synchronous wrapper for test convenience."""
  test_aether_policy_duration.py — Policy statement with timeout/duration keys should produce *_secs fields."""
  test_aether_rollback_plan.py — Transaction block should capture pre-transaction values in rollback_plan.
  test_aether_script_basic.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_aether_workflow_additional_paths.py — Additional runtime coverage: max-retries failure, tiny timeout fast-path,
  test_aether_workflow_backoff_and_schema.py — Additional coverage for workflow runtime: success-after-retry, backoff timing, and schema validation."""
  test_aether_workflow_kwargs.py — !/usr/bin/env python3
  test_aether_workflow_requires_inheritance.py — Workflow-level requires should merge into each step's requires field."""
  test_aether_workflow_retry_timeout.py — Workflow retry + timeout execution tests."""
  test_aether_workflow_step_execution.py — Tests for workflow step execution, parameter validation, and context management."""
  test_agent_pipeline_smoke.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_alert_intelligence.py — Test the adaptive threshold engine."""
  test_core_ai_runtime_baseline.py — Baseline tests for Aetherra.core.ai_runtime to seed coverage."""
  test_core_ai_runtime_errors.py — Deep tests for Aetherra.core.ai_runtime error handling and edge cases."""
  test_core_config_baseline.py — Baseline tests for Aetherra.core.config to seed coverage.
  test_core_integration.py — Integration tests for Aetherra core components working together."""
  test_core_interpreter_baseline.py — Baseline tests for Aetherra.core.aetherra_interpreter to seed coverage."""
  test_core_interpreter_execution.py — Deep tests for Aetherra.core.aetherra_interpreter execution paths."""
  test_core_parser_ast_construction.py — Tests for parser AST construction and tokenization flows."""
  test_core_parser_baseline.py — Baseline tests for Aetherra.core.aetherra_parser to seed coverage.
  test_core_parser_tokenization.py — Deep tests for Aetherra.core.aetherra_parser tokenization."""
  test_discovery_sanity.py
  test_discovery_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_headers_and_expiry.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_hmr_phase2.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_hub_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_multi_node_coordination.py — Test cluster discovery functionality."""
  test_os_kernel_imports.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_outbox_unit.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_phase9_metrics_bridge.py — Test Phase 9 metrics bridge functionality.
  test_quiesce_drain.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_sse_envelope_sanitizer.py — Verify that all internal keys defined in _INTERNAL_KEYS are stripped from final results."""
  test_sse_v2.py — SPDX-License-Identifier: GPL-3.0-or-later
tools/
  github/
    create_github_issues.py — !/usr/bin/env python3
    create_labels.py — !/usr/bin/env python3
    quick_fix_workflows.py — Set up Unicode environment variables
  maintenance/
    __init__.py — Maintenance utilities used by repository quality and Guardian checks.
    advanced_analyzer.py — Deep analysis of file content and purpose"""
    advanced_analyzer_fixed.py — Extract decorator name from AST node"""
    aetherra_core_analyzer.py — Calculate SHA256 hash of file content"""
    aetherra_core_cleaner.py — Remove exact duplicate files, keeping the one in the most appropriate directory"""
    aetherra_import_updater.py — Update import statements in a single file"""
    aetherra_lyrixa_cleaner.py — Safely move a file to new location"""
    aetherra_plugins_cleaner.py — Safely remove a file with backup info"""
    analyze_stubs.py
    check_architecture.py — Build a side-effect-free write plan for the compliance report."""
    check_unicode.py — Check for Unicode characters in a file.
    clean_hub_tmp.py — 🧩 Built-in Aetherra Hub Server"""
    clean_hub_tmp_utf8.py — 🧩 Built-in Aetherra Hub Server (UTF-8 cleaned copy)
    complete_organizer.py — Generate a comprehensive reorganization plan based on file analysis"""
    create_documentation.py — Load the updated project analysis"""
    debug_registry_connection.py — !/usr/bin/env python3
    final_file_organizer.py — Get the strategic file moves that make the most sense"""
    final_legal_check.py — Perform final legal compliance verification.
    fix_architecture.py — Auto-fixer for architectural violations"""
    fix_architecture_simple.py — Auto-fixer for architectural violations"""
    fix_imports.py — Utility class to fix import issues in an Aetherra repository."""
    fix_phase7_errors.py — Return basic plugin information."""
    fix_plugin_imports.py — Get plugin files that may contain known relative import errors."""
    fix_remaining_errors_round2.py — Safely get attribute from component objects or dictionaries."""
    fix_remaining_imports.py — Fix all remaining Lyrixa imports in selected core files.
    fix_unicode_issues.py — Quantum-enhanced memory processing engine."""
    fix_unicode_service_registry.py — !/usr/bin/env python3
    focused_cleanup.py — Perform targeted cleanup of identified issues
    generate_reports.py — Generate readable Markdown reports from project analysis JSON."""
    generate_stub_inventory.py — Generate a Phase 1.1 stub inventory JSON for production planning.
    launch_monitor.py — !/usr/bin/env python3
    post_cleanup_import_updater.py — !/usr/bin/env python3
    project_analyzer.py — Calculate SHA256 hash of file content"""
    quick_fix_imports.py — Check if Python version is compatible."""
    safe_cleanup.py — Load the project analysis"""
    smart_cleanup.py — Only the most obvious misplacements"""
    stub_finder.py
    universal_directory_analyzer.py — Calculate SHA256 hash of file content"""
    validate_architecture.py — Result of directory validation"""
    verify_imports.py — Return True if the import target should be considered valid.
    verify_legal_compliance.py — Check all installed packages for GPL-3.0 compatibility."""
  ops/
    check_agents.py — Quick script to check registered agents in orchestrator.
    check_metrics.py — Check what metrics are exposed
    force_homeostasis_active.py — Force the homeostasis system into active mode."""
    restart_aetherra.py — Perform pre-restart system checks"""
    start_aetherra_stack.py — Unified Aetherra Stack Starter
  __init__.py — Repository maintenance and developer tooling package.
  ab_recall_benchmark.py — A/B recall benchmark harness for classical vs quantum-enriched recall.
  agents_probe.py — Agent fabric probe utility (simplified placeholder)."""
  analyze_project.py — Detect key subsystems by presence of canonical files and dirs."""
  auto_fix_workflow_failures.py — Main class for fixing workflow failures"""
  auto_prune_unused_imports.py — Bulk prune unused imports reported by ruff F401.
  build_release_bundle.py — One-shot build + SBOM + manifest helper.
  chat_smoke.py — !/usr/bin/env python3
  check_license_consistency.py — !/usr/bin/env python3
  check_lyrixa_basic_ownership_guard.py — SPDX-License-Identifier: GPL-3.0-or-later
  ci_verify_no_discord_bot.py — CI Verification: ensure internal Discord bot artifacts are not present.
  ci_verify_no_website_artifacts.py — CI Guard: Prevent accidental website build artifacts from being committed.
  classify_aether_workflow_failures.py — Execute a workflow with structured interpreter integration.
  create_aether_from_task.py — .lstrip()
  create_annotated_tag.py — Create an annotated release tag embedding integrity manifest hash.
  create_plugin.py — Scaffold a new Aetherra plugin package.
  create_provenance_tag.py — Create a provenance tag (lightweight or annotated) referencing integrity manifest.
  daily_teacher.py — !/usr/bin/env python3
  debug_fallback_metrics.py — Standard library imports
  debug_live_edit_plan.py — Standard library imports
  dependency_lock.py — Generate a simple frozen dependency lock file (requirements.lock).
  deploy_storm_shadow.py — Print formatted header"""
  dev_quickstart.py — Developer ultra-quick start helper.
  diag_rate_limit_stream.py — Standard library imports
  diagnose_homeostasis.py — Run diagnostic checks on homeostasis vital systems.
  enforce_license_policy.py — Lightweight license policy enforcement / telemetry.
  enforce_lock_sync.py — Verify that current environment matches requirements.lock.
  engine_audit.py — SPDX-License-Identifier: GPL-3.0-or-later
  engine_inspector.py — Ranking heuristic to pick canonical implementation.
  engine_usage_matrix.py — SPDX-License-Identifier: GPL-3.0-or-later
  engine_usage_probe.py — SPDX-License-Identifier: GPL-3.0-or-later
  find_stubs.py — Find all stub/placeholder functions in the codebase.
  fix_duplicate_spdx.py — Fix duplicate SPDX blocks in a file, keeping only one."""
  fix_gui_exec_security.py — Quick script to add nosec comments to legitimate Qt GUI exec() calls."""
  fix_type_annotations.py — Automatically fix missing type annotations in Python files."""
  fix_verbose_readmes.py — Generate a concise README for a directory."""
  format_changelog.py — Normalize CHANGELOG.md formatting after semantic-release.
  format_lint.py — Unified formatter & linter runner for Aetherra.
  format_markdown.py — Lightweight Markdown formatter for line wrapping.
  generate_beta_readiness_report.py — Generate or update the Beta Readiness Report.
  generate_file_index.py — Return tracked repository files, or None when git is unavailable."""
  generate_integrity_manifest.py — Generate integrity manifest for release artifacts.
  generate_metrics_reference.py — Generate docs/METRICS_REFERENCE.md from live metrics_accum definitions.
  generate_parse_baseline.py — Generate a baseline parse status JSON for all .aether workflows.
  generate_qfac_file_index.py — SPDX-License-Identifier: GPL-3.0-or-later
  generate_risk_badge.py — Generate Shields.io endpoint JSON for total .aether static risk score.
  generate_sbom.py — Generate minimal SBOM (alpha) from license_report JSON.
  generate_selfinc_readiness_doc.py — Generate Self-Inc Production Readiness doc from metadata.
  guard_discord_exclusion.py — CI/packaging guard to ensure the internal Discord Bot directory is excluded.
  ingest_safe.py — !/usr/bin/env python3
  introspect_mock_counter.py — Third party imports
  introspect_mock_total.py — Third party imports
  learning_evaluator.py — Best-effort handle to a memory search function across available systems."""
  license_report.py — Generate a license report for Python dependencies.
  lyrixa_connectivity_test.py — SPDX-License-Identifier: GPL-3.0-or-later
  lyrixa_diagnostics.py — Return a structure with deterministic key ordering for JSON emission.
  memory_fragmentation_metrics.py — Memory Fragmentation / Compaction Metrics (Lightweight)
  migrate_legacy_aether.py — !/usr/bin/env python3
  monitor_storm_shadow.py — Monitor STORM shadow mode deployment"""
  nightly_hallucination_audit.py — !/usr/bin/env python3
  organize_directory_structure.py — Organize the Aetherra project directory structure.
  organize_repo.py — !/usr/bin/env python3
  os_smoke.py — Check if core services can be imported and initialized."""
  outbox_drain.py — !/usr/bin/env python3
  packaging_smoke.py — Packaging smoke test.
  parse_baseline_regression_gate.py — Parse Baseline Regression Gate
  phase5_bundle_artifacts.py — Phase 5 artifact bundler.
  phase5_report_rollup.py — Phase 5 report rollup utility.
  phase5_validation_harness.py — Phase 5 validation harness.
  pre_pack_validation.py — Result of a single validation check"""
  precommit_sign_aether.py — !/usr/bin/env python3
  prepare_release_bundle.py — Prepare a curated release bundle directory (and optional zip).
  probe_ai_endpoints.py — Read a few SSE lines safely with a time limit.
  probe_rate_limit_stream.py — Standard library imports
  provenance_tag_wrapper.py
  prune_aetherra_gui.py — !/usr/bin/env python3
  prune_license_overrides.py — Prune stale entries from license_overrides.yml.
  prune_lyrixa_gui.py — !/usr/bin/env python3
  qfac_admin.py — Attempt to obtain a QFACMemorySystem instance.
  quality_gates.py — Run a command and return (exit_code, stdout+stderr) decoded as UTF-8.
  quarantine_unused_engines.py — SPDX-License-Identifier: GPL-3.0-or-later
  quick_type_fix.py — Fix the most common missing type annotation patterns."""
  README_doctor.md — Project Doctor
  repo_security_scan.py — Lightweight repository security & hygiene scan.
  repro_3018_internal.py — Standard library imports
  repro_metrics_baseline.py — !/usr/bin/env python3
  repro_test_metrics_case.py — Standard library imports
  root_cleanup.py — Root cleanup orchestrator (non-destructive by default).
  run_go_no_go_gates.py — Launcher smoke: phased boot + registry core services.
  run_hub_ai_api.py — !/usr/bin/env python3
  run_plugin_discovery_sync.py — Fast reachability check using raw socket connect (avoids extra deps)."""
  run_regression_suite.py — Unified regression suite runner.
  run_week10_matrix_and_regression.py — Generate Week-10 integration matrix and regression evidence reports.
  sign_aether.py — !/usr/bin/env python3
  sign_release_manifest.py — Create and (optionally) sign a release manifest of built artifacts.
  smoke_test_hub_connector.py — !/usr/bin/env python3
  snapshot_replay_harness.py — Snapshot & Replay Harness
  spdx_verify.py — SPDX & Attribution Consistency Checker
  spec_tests_gate.py — !/usr/bin/env python3
  static_security_scan.py — Static Security Scan Tool
  storm_ab_test.py — Metrics for a single recall operation"""
  storm_backup.py — !/usr/bin/env python3
  storm_weekly_summary.py — Generate weekly monitoring summary"""
  test_selection_stub.py — Test Selection Stub
  update_spdx_ids.py — Fetch the current SPDX license list and store a simplified ID array.
  update_system_index.py — Return (emoji, label) reduced status from doc content.
  validate_engine_imports.py — SPDX-License-Identifier: GPL-3.0-or-later
  validate_import_map.py — !/usr/bin/env python3
  validate_license_overrides.py — Validate license_overrides.yml structure & SPDX expressions (basic heuristics).
  validate_maintenance_metrics.py — Minimal service registry for testing."""
  verify_aether_scripts.py — Return all .aether files under the repo, excluding transient/ignored dirs.
  verify_architecture_map.py — Validate hub compatibility layer + Lyrixa chat service.
  verify_docs_architecture.py — Verify documentation architecture structure and required files.
  verify_docs_consistency.py — Extract content under a markdown heading (any level >= 2) until the next heading of any level.
  verify_llm_setup.py — Attempt a minimal local round-trip if SDKs are installed and keys present.
  verify_phase5_manifest_policy.py — Verify Phase 5 bundle manifest policy constraints.
  verify_release_manifest.py — Verify release manifest integrity and optional signature.
  verify_ui_standards.py — !/usr/bin/env python3
  verify_version_badge.py — Verify README version badge matches declared version.
  vuln_scan.py — Lightweight vulnerability scan wrapper (alpha implementation).
.markdownlint.json
aether.py — Execute Aether Script content."""
aetherra_aar_broker.py — !/usr/bin/env python3
aetherra_adaptive_behavior.py — Represents a learned behavior pattern."""
aetherra_agent_daemon.py — !/usr/bin/env python3
aetherra_agent_fabric.py — Register Agent Fabric agents with the AgentOrchestrator for task management."""
aetherra_cognitive_task_manager.py — Initialize Flask app and routes."""
aetherra_cognitive_task_manager_simple.py — Simplified cognitive task manager that definitely works."""
aetherra_event_bus.py — !/usr/bin/env python3
aetherra_file_watcher.py — Determine if a file should be processed."""
aetherra_hmr_controller.py — Hot Module Reload controller service.
aetherra_kernel_loop.py — Evaluate production backpressure & plugin safety invariants.
aetherra_live_monitor.py — !/usr/bin/env python3
aetherra_meta_memory.py — Initialize the meta-memory database."""
aetherra_module_manager.py — Minimal, safe module manager with a clear contract."""
aetherra_os.py — Launch the designated Aetherra GUI interface and start OS backend"""
aetherra_os_launcher.py — Return the most recent launcher readiness snapshot, if available."""
aetherra_outbox.py — !/usr/bin/env python3
aetherra_persistent_memory.py — Individual memory node with cognitive metadata."""
aetherra_plugin_catalog.json
aetherra_plugin_discovery.py — Plugin metadata structure."""
aetherra_plugin_viewer.py — Simple GUI to view discovered plugins."""
aetherra_quantum_meta_learning.py — Calculate measurement probability for this state."""
aetherra_registry_client.py — SPDX-License-Identifier: GPL-3.0-or-later
aetherra_registry_daemon.py — !/usr/bin/env python3
aetherra_script_service.py — Minimal .aether interpreter with async interface."""
aetherra_self_incorporation.py — Track user activity patterns for night cycle scheduling."""
aetherra_self_organizer.py — Comprehensive metadata for each file in the system."""
aetherra_service_registry.py — Service health status enumeration."""
aetherra_shared_service_registry.py — Service health status enumeration."""
aetherra_startup.py — SPDX-License-Identifier: GPL-3.0-or-later
BETA_READINESS_REPORT.md — Aetherra Beta Readiness Report
beyond_transcendence_engine.py — Legacy import shim for BeyondTranscendenceEngine.
CHANGELOG.md — Changelog
CODE_OF_CONDUCT.md — Code of Conduct
config.autonomy.production.json
config.autonomy.staging.json
config.json
config.production.json
CONTRIBUTING.md — Contributing
copyright_header.py — !/usr/bin/env python3
ENGINE_CURATION_PROPOSAL.md — Engine Curation Proposal (Dry-Run Plan)
ENGINE_USAGE_MATRIX.md — Engine Usage Matrix
GOVERNANCE.md — Project Governance
INSTALL.md — Installation & Quickstart
intelligence_report_generator.py — Load analysis data from JSON file"""
launch_aetherra_unicode.py — Legacy shim retained for backward compatibility; delegates to aetherra_os."""
LEGAL_COMPLIANCE.md — Aetherra Project - Legal Compliance Documentation
LICENSE_POLICY.md — License Policy & Enforcement Gates
licenses_unknown_history.json
licenses_unknown_history.requirements-ci.lock.json
main.py — Convenience launcher alias for aetherra_os main entry point.
OWNERSHIP.md — Ownership & Release Authority
package-lock.json
package.json
PRE_PACK_CHECKLIST_TRACKING.md — Aetherra & Lyrixa — Pre-Pack Validation Tracking
PRE_PACK_SESSION_REPORT.md — Pre-Pack Validation Session Report
PRE_PACK_VALIDATION_SUMMARY.md — Aetherra & Lyrixa Pre-Pack Validation - Quick Summary
PRIVACY.md — Privacy Policy (Project Repository)
PRODUCTION_ROADMAP.md — Aetherra Production Roadmap
quantum_memory_bridge.py — Quantum memory bridge placeholder (alpha stub)."""
QUICK_START.md — Aetherra Turn-Key Development Quick Start
README.md — Aetherra
RELEASE_NOTES_0.5.0-beta.0.md — Aetherra 0.5.0-beta.0 Release Notes
ROADMAP.md — Aetherra Roadmap
sbom.json
SECURITY.md — Security Policy
setup.py — !/usr/bin/env python3
setup_dev.py — Print the Aetherra setup banner"""
STEWARDSHIP.md — Aetherra Stewardship Statement
STUB_INVENTORY.json
SUPPORT.md — Support
test_unicode_workflow_fix.py — Test that Unicode issues are resolved
unicode_logger.py — Unicode-Safe Logging Configuration for Aetherra OS.
```
