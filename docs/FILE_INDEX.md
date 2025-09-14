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
      aetherra_engine.py — Initialize the Aetherra engine and all subsystems"""
      assistant.py — Create unique session identifier with enhanced metadata"""
      lyrixa_engine.py — Main Lyrixa execution engine that coordinates all subsystems"""
      lyrixa_memory.json
      prompt_engine.py — Load memory from JSON file"""
      README.md — engine
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
      reflector.py — SPDX-License-Identifier: GPL-3.0-or-later
      web_bridge.py — Bridge class for Qt-Web communication"""
    memory/
      QuantumEnhancedMemoryEngine/
        __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
        causal_brancher.py — SPDX-License-Identifier: GPL-3.0-or-later
        compression.py — SPDX-License-Identifier: GPL-3.0-or-later
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
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      aetherra_memory_engine.py — Compat store: accept dicts with 'content' and optional 'metadata'.
      causal_branch_simulator.py — Represents a potential future memory state with probability weighting"""
      compression_metrics.py — Memory compression fidelity levels"""
      concept_clustering.py — Represents a semantic concept in the clustering system"""
      enhanced_memory.py — Enhanced memory system with advanced capabilities."""
      fractal_encoder.py — SPDX-License-Identifier: GPL-3.0-or-later
      fractal_hierarchies.py — Represents a fractal cluster in the hierarchy"""
      fractal_replay_engine.py — Represents a reconstructed memory episode"""
      lightweight_memory_core.py — Goal for memory relevance"""
      lyrixa_memory_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      memory_core.py — Close the underlying SQLite connection if open.
      memory_core_adapter.py — SPDX-License-Identifier: GPL-3.0-or-later
      memory_kernel.py — Configuration for the integrated memory system"""
      memory_learning.py — Classify the type of interaction for learning purposes"""
      models.py — Canonical typed recall contract.
      observer_effect_simulator.py — Different types of observers with varying impact levels"""
      optimized_memory_engine.py — Start the async processing loop"""
      optimized_storage.py — Represents a pending write operation"""
      qfac_dashboard.py — Lightweight dashboard facade returning live QFAC metrics.
      qfac_integration.py — Automatically analyze and compress if beneficial"""
      qfac_launcher.py — Initialize QFAC components"""
      qfac_policy.py — !/usr/bin/env python3
      qfac_state_tracker.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_memory_bridge.py — Represents a memory state mapped to quantum circuit representation"""
      quantum_memory_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_memory_integration.py — Quantum-specific memory metrics"""
      quantum_memory_state.py — SPDX-License-Identifier: GPL-3.0-or-later
      quantum_web_dashboard.py — SPDX-License-Identifier: GPL-3.0-or-later
      README.md — Memory Subsystem
      world_class_memory_core.py — Memory cluster for visualization"""
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
      logger.aether
      memory_cleanser.aether
      memory_ops.aether
      plugin_watchdog.aether
      plugins.aether
      README.md — System Subsystem
      reflection_system.py — Analyze a single interaction for patterns and insights"""
      security_system.py — Return a deep-copied structure with secret-looking fields redacted.
      self_introspector.aether
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
      consciousness_bridge.py — Standard message format for consciousness layer communication"""
      lyrixa_consciousness.py — Lyrixa's emotional states"""
      meta_layer_core.py — Possible states for an agent"""
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
    CONSCIOUSNESS_EVOLUTION_COMPLETE_SUMMARY.md — Aetherra Consciousness Evolution - Complete Journey Summary
    consciousness_orchestrator.py — Initialize all consciousness components"""
    demo.py — Run a demonstration of the consciousness orchestrator"""
    episodic_store.py — Episodic Store
    ethics_critic.py — Ethics Critic MVP
    event_bus.py — Unified Event Bus (Phase 1)
    EXTENDED_ROADMAP.md — 🧠 AETHERRA EXTENDED ROADMAP
    metrics_exporter.py — Prometheus Metrics Exporter (Optional)
    narrator.py — Narrative Layer (Phase 1)
    phase2_demo.py — Initialize the full consciousness system with integrated agents."""
    PHASE_5_COMPLETION_SUMMARY.md
    PHASE_8_3_ACHIEVEMENT_REPORT.md — Phase 8.3: Beyond Transcendence Achievement Report
    ROADMAP.md — Aetherra Consciousness Orchestrator - Meta-Layer Roadmap
    self_model.py — Self-Model API (Phase 1)
    self_model_manager.py — Self-Model Manager
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
    backups/
      README.md — backups
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
  gui/
    __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
    aetherra_os_gui.py — !/usr/bin/env python3
    boot_menu.py — Show a BIOS-like boot menu and return the user's choice.
    GUI_CURATION_PLAN.md
    launch_enhanced_neural_os.py — !/usr/bin/env python3
    README.md — Aetherra OS Monitor GUI
    run_aetherra_os.py — Launch the Enhanced Aetherra Neural OS Dashboard
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
  legacy/
    README.md — Aetherra Legacy Engines and Startup
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
    chat/
      lyrixa_chat_service.py — Best-effort load of config.json to tune chat behavior without hard deps."""
    ethics_agent/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      bias_detector.py — Types of bias that can be detected."""
      moral_reasoning.py — Different moral reasoning frameworks."""
      README.md — ethics_agent
      value_alignment.py — Core human values for alignment."""
    gui/
      assets/
        README.md — assets
      src/
        README.md — src
      web_panels/
        README.md — web_panels
      widgets/
        metrics_panel.py — Right-side live metrics/status panel."""
        nav_panel.py — Add buttons for auto-generated panels (id, title)."""
      chat_interface.py — Send user message and get AI response"""
      consciousness_panel.py — Bridge for web-based consciousness interface communication."""
      context_bridge.py — Handle commands from web panels."""
      emotional_theme.py — Generates dynamic themes based on Lyrixa's emotional state"""
      evolution_monitoring_system.py — Single generation in consciousness evolution"""
      layout_memory.py — Manages persistent GUI state and user preferences"""
      lyrixa_ai.py — Core AI intelligence for chat and reasoning"""
      lyrixa_hybrid_window.py — Background web server for the hybrid interface."""
      main_window.py — JSON serializer for datetime objects"""
      meta_learning_control_panel.py — Individual learning episode record"""
      package-lock.json
      package.json
      phase3_auto_generator.py — Represents the state of a system component"""
      PHASE3_IMPLEMENTATION_COMPLETE.md — 🔮 Phase 3 Implementation Complete
      PHASE3_README.md — 🔮 Phase 3: Auto-Generating Panels from Aetherra State
      phase4_cognitive_ui.py — Custom JSON serializer for datetime objects"""
      phase5_plugin_ui.py — Plugin UI panel definition from metadata"""
      phase6_personality.py — Load previous GUI state from memory"""
      phase6_types.py — Lyrixa's emotional states that affect GUI appearance"""
      plugin_editor_controller.py — Levels of introspection depth"""
      quantum_temporal_interface.py — Quantum consciousness state representation"""
      README.md — gui
    integrations/
      aetherra_hub_connector.py — Connect to Aetherra Hub"""
      memory_adapter.py — Get comprehensive system status for plugin UI"""
      style_manager.py — Generate a unique style variable name"""
    intelligence/
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      adaptive_orchestrator.py — !/usr/bin/env python3
      lyrixa_full_intelligence.py — Load intelligence configuration"""
      meta_reasoning.py — Types of decisions that can be tracked"""
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
        memory_plugin.aether
        README.md — advanced-memory-system
      __init__.py — SPDX-License-Identifier: GPL-3.0-or-later
      advanced_memory_system_ui.py — Advanced Memory System Plugin UI with comprehensive memory management."""
      ai_plugin_generator_ui.py — AI Plugin Generator UI for intelligent plugin creation."""
      assistant_trainer_plugin.py — Represents a training dataset for assistant training."""
      assistant_trainer_plugin_ui.py — Assistant Trainer Plugin UI for customizing AI behavior and training."""
      context_aware_surfacing.py — Represents a snapshot of current context."""
      context_aware_surfacing_ui.py — Context Aware Surfacing Plugin UI for intelligent content recommendations."""
      enhanced_plugin_manager.py — Plugin state management."""
      installed_plugins.json
      introspector_plugin.py — Plugin for autonomous code analysis and self-insight generation"""
      introspector_plugin_ui.py — Introspector Plugin UI for system analysis and self-reflection."""
      memory_aware_plugin_router.py — Memory context provided to plugins for enhanced behavior"""
      plugin_analytics.py — Collects detailed metrics for plugin execution and usage."""
      plugin_analytics_ui.py — Plugin Analytics UI for monitoring plugin usage and performance."""
      plugin_creation_wizard.py — Plugin template for the wizard."""
      plugin_creation_wizard_ui.py — Plugin Creation Wizard UI with step-by-step guidance."""
      plugin_discovery.py — Plugin metadata container."""
      plugin_lifecycle_memory.py — Represents a memory entry for plugin lifecycle events."""
      plugin_manager.py — Plugin state management."""
      plugin_quality_control.py — Quality metrics for plugin evaluation."""
      workflow_builder_plugin.py — Represents a single step in a workflow."""
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
    launcher.py — Load environment variables from .env file"""
    lyrixa_basic.py — Initialize Basic Lyrixa with OS dependency check."""
    lyrixa_basic_gui.py — Setup the basic UI layout."""
    README.md — lyrixa
  lyrixa_plugins/
    emotion_detector.py — Primary emotion categories"""
    emotional_intelligence.py — Represents a complex emotional state with multiple dimensions"""
    emotional_intelligence_integration.py — Update integration performance metrics"""
    mini_lyrixa_avatar.py — 🔥 AI Presence Projection - Dynamic cognitive avatar"""
    README.md — lyrixa_plugins
  memory/
    graph_optics.py — SPDX-License-Identifier: GPL-3.0-or-later
  memory_continuity_data/
    README.md — memory_continuity_data
  observability/
    metrics_service.py — Lightweight in-process metrics exposure service.
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
      enhanced_plugin_manager.py — Plugin state management."""
      plugin_api.py — Clean plugin interface for Lyrixa"""
      plugin_chain_executor.py — Status of plugin chain execution"""
      plugin_creation_wizard.py — Plugin template for the wizard."""
      plugin_discovery.py — Plugin metadata container."""
      plugin_generator_plugin.py — Represents a plugin template for generation."""
      plugin_manager.py — Plugin state management."""
      plugin_quality_control.py — Quality metrics for plugin evaluation."""
      plugin_registry.py — Discover plugins by scanning plugins/ folder and manifests.
      plugin_sdk.py — Plugin metadata for enhanced discovery and transparency"""
      plugin_system.py — Fallback to regular file writing"""
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
      __init__.py — Placeholder PluginManager when imports fail.
      assistant_trainer_plugin.py — Represents a training dataset for assistant training."""
      context_aware_surfacing.py — Represents a snapshot of current context."""
      introspector_plugin.py — Plugin for autonomous code analysis and self-insight generation"""
      README.md — extra_plugins
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
    manifest_schema.py — Map hub signing strictness and signature verification to trust zone label.
    README.md — Plugins Subsystem
    reflector.py — Self-reflection and behavior analysis capabilities for AetherraCode"""
  quantum/
    chat_consciousness_bridge.py — Trigger a light sync and return a coherence snapshot if available."""
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
  scripts/
    utilities/
      README.md — utilities
    audit_file_usage.py — Scan entire project for Python files and their relationships"""
    check_deployment_readiness.py — Comprehensive deployment readiness validation"""
    cleanup_project.py — Main cleanup orchestrator for Aetherra project"""
    conservative_cleanup.py — Move only obviously safe-to-move files"""
    fast_cleanup.py — Perform quick cleanup of obviously unused files"""
    live_file_index.json
    organize_system.py — Main launcher for Aetherra self-organizing intelligence."""
    README.md — scripts
    self_organizer.aether
    simple_audit.py — Just count Python files quickly"""
    simple_cleanup.py — Move files to unused directory
  security/
    api_keys.py — Return Fernet key bytes if available, else None.
    capabilities.py — Load full capabilities policy JSON (allow + optional limits).
    net_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    plugin_signing.py — Compute a deterministic SHA256 tree hash for a list of file paths."""
    prompt_defense.py — Heuristic scan for prompt-injection and jailbreak attempts.
    sandbox.py — Evaluate a small arithmetic/logic expression safely.
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
    quantum_memory_bridge.py — Represents a memory state mapped to quantum circuit representation"""
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
  __init__.py
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
  contributing/
    docs-consistency.md
  ops/
    HUB_CONTROL_TOKEN.md — Hub Control Token
    OPERATOR_RUNBOOK.md — Aetherra Operator Runbook (Alpha)
  reports/
    aether_static_report.md — .aether Verification Report
    AETHERRA_CORE_ANALYSIS.md — 🔍 AETHERRA CORE DUPLICATE & ORGANIZATION ANALYSIS
    AETHERRA_CORE_CLEANUP_REPORT.md — 🧹 AETHERRA CORE CLEANUP REPORT
    AETHERRA_CORE_TRANSFORMATION_SUMMARY.md — 🎯 AETHERRA CORE ANALYSIS & CLEANUP SUMMARY
    AETHERRA_IMPORT_UPDATE_REPORT.md — 🔄 AETHERRA IMPORT UPDATE REPORT
    AETHERRA_LYRIXA_CLEANUP_REPORT.md — 🧹 AETHERRA LYRIXA CLEANUP REPORT
    AETHERRA_ORGANIZATION_COMPLETION_SUMMARY.md — 🎯 AETHERRA CORE FILE ORGANIZATION - COMPLETION SUMMARY
    AETHERRA_OS_RELEASE_PLAN.md — 🚀 AETHERRA OS RELEASE PLAN
    AETHERRA_PLUGINS_CLEANUP_REPORT.md — 🧹 AETHERRA PLUGINS CLEANUP REPORT
    AETHERRA_PROJECT_ANALYSIS_SUMMARY.md — 🎯 AETHERRA PROJECT DIRECTORY ANALYSIS SUMMARY
    AETHERRA_RELEASE_STATUS.md — 🎉 AETHERRA OS RELEASE STATUS
    API_DIRECTORY_ANALYSIS.md — 🔍 API DIRECTORY ANALYSIS
    ARCHITECTURAL_COMPLIANCE_REPORT.md — 🎯 AETHERRA ARCHITECTURAL COMPLIANCE REPORT
    ARCHITECTURAL_ENFORCEMENT_SUMMARY.md — 🏗️ AETHERRA DIRECTORY ARCHITECTURE ENFORCEMENT SUMMARY
    ARCHITECTURE_CLARIFICATION.md — 🎯 **Correct Component Roles & Responsibilities**
    ARCHITECTURE_VALIDATION_REPORT.md — 🏗️ AETHERRA DIRECTORY ARCHITECTURE VALIDATION REPORT
    CLEANUP_ANALYSIS.md — 🧹 Aetherra Project Cleanup Analysis
    CLEANUP_COMPLETE.md — 🎉 Aetherra Project Cleanup Complete!
    COMPLETE_DIRECTORY_INTELLIGENCE.md — 🗂️ COMPLETE DIRECTORY INTELLIGENCE OVERVIEW
    COMPLETE_FILE_INVENTORY.md — 📄 COMPLETE FILE INVENTORY & INTELLIGENCE
    COMPREHENSIVE_ORGANIZATION_REPORT.md — 🎯 COMPREHENSIVE AETHERRA CORE ORGANIZATION REPORT
    CONSOLIDATION_PLAN.md — 🎯 File Consolidation Plan
    CORE_DIRECTORY_ANALYSIS.md — 🔍 CORE DIRECTORY ANALYSIS
    CRITICAL_CLEANUP_PLAN.md — 🧹 Critical File Cleanup & Consolidation Plan
    DATABASE_ORGANIZATION_COMPLETE.md — 🗃️ Database File Organization Complete!
    DATABASE_ORGANIZATION_PLAN.md — 🗂️ Database Organization Analysis
    DATABASE_REORGANIZATION_COMPLETE.md — 🎯 Database Organization Complete!
    DEPLOYMENT_SUMMARY.md — Aetherra - Final Phase Deployment Summary
    DIRECTORY_ARCHITECTURE_GUIDELINES.md — 🏗️ AETHERRA PROJECT DIRECTORY ARCHITECTURE GUIDELINES
    DIRECTORY_STRUCTURE_ANALYSIS.md — 📁 Directory Structure Analysis
    DUPLICATE_FILES_REPORT.md — 🔄 Duplicate Files Report
    ENGINE_AUDIT_REPORT.md — Aetherra OS Engine Audit
    ENGINE_INSPECTION_REPORT.md — Engine Inspection Report
    FILE_CATEGORY_ANALYSIS.md — 📊 File Category Analysis
    FILE_RESTORATION_STATUS.md — File Restoration Status Report �
    FINAL_ORGANIZATION_REPORT.md — 🎯 FINAL AETHERRA CORE ORGANIZATION REPORT
    FINAL_WARNING_FIXES_REPORT.md — FINAL WARNING FIXES COMPLETION
    GUI_DIRECTORY_ANALYSIS.md — 🔍 GUI DIRECTORY ANALYSIS
    INTELLIGENCE_COMPLETE.md — 🎯 COMPREHENSIVE PROJECT INTELLIGENCE COMPLETE
    LYRIXA_CORE_RESTORATION_COMPLETE.md — 🎉 LYRIXA CORE RESTORATION COMPLETE
    LYRIXA_DIRECTORY_ANALYSIS.md — 🔍 LYRIXA DIRECTORY ANALYSIS
    LYRIXA_DIRECTORY_ORGANIZATION_SCAN.md — 🗂️ LYRIXA DIRECTORY ORGANIZATION SCAN REPORT
    LYRIXA_MERGE_COMPLETION_REPORT.md — 🎉 LYRIXA CORE MERGE COMPLETION REPORT
    LYRIXA_MERGE_PLAN.md — 🔄 Lyrixa Core Merge Plan
    LYRIXA_MERGE_SESSION_COMPLETE.md — 🎯 LYRIXA MERGE SESSION COMPLETE
    LYRIXA_RELEASE_READINESS_ASSESSMENT.md — 🚀 Lyrixa GUI Release Readiness Assessment & Action Plan
    MARKDOWN_ORGANIZATION_COMPLETE.md — 📚 Markdown Documentation Organization Complete!
    MARKDOWN_ORGANIZATION_PLAN.md — 📁 Markdown Documentation Organization Plan
    PHASE2_COMPLETION_SUMMARY.md — 🎉 Phase 2 Completion Summary: Agent Integration Success
    PHASE_6_COMPLETION_REPORT.md
    PHASE_7.2_COMPLETION_REPORT.md — 🧠 AETHERRA PHASE 7.2 IMPLEMENTATION COMPLETE
    PHASE_7_1_COMPLETION_FINAL.md — FINAL STATUS: ✅ 100% COMPLETE - ALL WARNINGS RESOLVED
    PHASE_7_1_COMPLETION_SUMMARY.md — 🚀 PHASE 7.1 COMPLETION SUMMARY
    PHASE_7_1_ERROR_FIXES_SUMMARY.md — 🔧 PHASE 7.1 ERROR FIXES SUMMARY
    PHASE_7_1_ULTIMATE_COMPLETION.md — FINAL STATUS: ✅ 100% COMPLETE - ALL ERRORS COMPLETELY RESOLVED
    PHASE_7_3_COMPLETION_REPORT.md
    PHASE_7_4_IMPLEMENTATION_PLAN.md — 🌌 PHASE 7.4 IMPLEMENTATION PLAN: MULTIDIMENSIONAL CONSCIOUSNESS EXPANSION
    PHASE_8_1_COMPLETION_REPORT.md — 🌟 PHASE 8.1 CONSCIOUSNESS SINGULARITY COMPLETION REPORT
    PHASE_8_2_COMPLETION_REPORT.md — 🌌 PHASE 8.2 COSMIC CONSCIOUSNESS COMPLETION REPORT
    PLUGINS_DIRECTORY_ANALYSIS.md — 🔍 PLUGINS DIRECTORY ANALYSIS
    POST_CLEANUP_IMPORT_UPDATE_REPORT.md — 🔄 POST-CLEANUP IMPORT UPDATE REPORT
    PRE_PHASE3_COMPLETION_REPORT.md — PRE-PHASE 3 FIXES COMPLETION REPORT
    PRE_PHASE3_FIXES_REPORT.md — LYRIXA SYSTEM ERROR AND WARNING FIXES
    PROJECT_BREAKDOWN.md — 🏗️ Aetherra Project Breakdown
    PROJECT_CLEANUP_COMPLETE.md — 🚀 Aetherra Project Cleanup Complete!
    PROJECT_DEEP_ANALYSIS_PLAN.md — 🔍 Aetherra Project Deep Analysis Plan
    PROJECT_INTELLIGENCE_INSIGHTS.md — 🧠 PROJECT INTELLIGENCE INSIGHTS
    QUANTUM_MEMORY_INTEGRATION_COMPLETE.md — Quantum Memory Integration Complete ✅
    TEST_ORGANIZATION_COMPLETE.md — 📂 Test File Organization Complete!
    TRANSFORMATION_COMPLETE.md — 🎉 AETHERRA PROJECT TRANSFORMATION COMPLETE!
    ui_standards_report.md — UI Standards Report
    website_truth_update_summary.md — Aetherra Website Truth Update - August 8, 2025
    WORKFLOW_OPTIONS_2-6_COMPLETION_REPORT.md — 🎯 AETHERRA PROJECT CLEANUP WORKFLOW COMPLETION REPORT
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
    🚀 Aetherra AI Chat Enhancement Plan.md — Enhancement: Deep integration with quantum consciousness system
  sections/
    README.md — Aetherra Documentation Sections
  Aether_Script_Language_System.md — Aether Script Language System (`.aether`)
  Aether_Script_Operator_Guide.md — Aether Script Operator Guide
  aether_script_protection.md — Aether Script Protection and Signing
  Aetherra Chat System.md — Aetherra Chat System Documentation
  AETHERRA_AGENT_SYSTEM.md — Aetherra Agent System
  AETHERRA_AI_TRAINER_SYSTEM.md — Aetherra AI Trainer System
  AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md — Aetherra Artificial Intelligence System
  AETHERRA_CHAT_SYSTEM.md — Aetherra Chat System
  AETHERRA_CODING_SYSTEM.md — Aetherra Coding System (Lyrixa Code Studio)
  AETHERRA_KERNEL_SYSTEM.md — Aetherra Kernel System
  AETHERRA_LYRIXA_SYSTEM.md — Aetherra Lyrixa System
  AETHERRA_MEMORY_SYSTEM.md — Aetherra Memory System
  aetherra_os_architecture_map_v_1.md — Aetherra OS • Architecture Map (v1.0)
  AETHERRA_PLUGIN_SYSTEM.md — Aetherra Plugin System
  aetherra_quantum_roadmap_v_1.md — Aetherra • Quantum Roadmap (v1.0)
  AETHERRA_SECURITY_SYSTEM.md — Aetherra Security System (Aetherra OS + Lyrixa)
  ALPHA_READINESS.md — Alpha Readiness & Usage Guide
  ALPHA_RELEASE_GAP_ANALYSIS.md — Alpha Release Gap Analysis (0.1.0-alpha.2)
  ALPHA_TEST_STRATEGY.md — Alpha Test & Failure Injection Strategy
  api-keys.md — API Keys and Secrets
  ATTESTATION.md — Release Attestation (Alpha Stub)
  BETA_MILESTONE.md — Beta Milestone Planning (Draft)
  BETA_ROADMAP_0.5.0.md — Aetherra 0.5.0 Beta Roadmap & Community Focus
  BUILD_REPRODUCIBILITY.md — Build Reproducibility & Verification (Alpha)
  CONSCIOUSNESS_UNIFIED_IDENTITY.md — Unified Identity & Consciousness Layer
  COVERAGE_POLICY.md — Coverage Policy (Alpha)
  Demo_Playbook.md — Aetherra Demo Playbook
  DEPRECATION_TRACKER_LEGACY_HUB.md — Deprecation Tracker: Legacy Hub Script (`aetherra_hub_server.py`)
  DEVELOPER_ONBOARDING.md — Developer Onboarding
  docs_consistency.json
  DOCS_CONSISTENCY.md — Docs Consistency Verification
  DOCS_CONSISTENCY_REPORT.md — Docs Consistency Report
  ERRORS_WARNINGS_AUDIT.md — Aetherra Project Comprehensive Error & Warning Audit (2025-09-08)
  FILE_INDEX.md — Aetherra File Index
  GO_NO_GO_GATES.md — Go / No-Go Gates (Fast Deterministic Suite)
  import_map.md — Import Map & Enforcement (P2 #13)
  INDEX.md — Aetherra Documentation Index
  KEY_ROTATION.md — Aetherra Key Rotation & Signing Appendix
  LYRIXA_CHAT_ENDPOINT.md — Lyrixa Chat Endpoint
  manifesto.md — AETHERRA MANIFESTO (v6.0 – July 2025)
  memory_system.md — Memory System
  METRICS_REFERENCE.md — Aetherra Metrics Reference
  NEXT_STEPS.md — Next Steps: Lyrixa Chat Production Readiness
  PACKAGING_AND_RELEASE.md — Packaging & Release (Alpha)
  PROJECT_ANALYSIS.json
  PROJECT_OVERVIEW.md — Aetherra Project Overview
  PROJECT_STATUS_2025-08-11.md — Aetherra — Project Status and Architecture Map (2025-08-11)
  QFAC_MODE_GUIDE.md — AETHERRA QFAC Mode Guide
  QFAC_POLICY.md — QFAC Policy and Live-Metrics Gating
  QUANTUM_OVERVIEW.md — Aetherra Quantum Layer: Overview
  RELEASE_NOTES_v0.1.0-alpha.2.md — Aetherra v0.1.0-alpha.2 Release Notes
  RELEASE_PROCESS.md — Release Process (Alpha → Tag)
  REPO_CLEANUP_GUIDE.md — Repository Cleanup and Size Reduction
  REPO_SETTINGS.md — Recommended Repository Settings
  RISK_ACCEPTANCE.md — Risk Acceptance Register (Alpha)
  ROOT_CLEANUP_PLAN.md — Root Cleanup Plan (Alpha → Beta Hardening)
  SECURITY_FEDERATION_ENHANCEMENTS_2025-08-12.md — Security, Signing, and Federation Enhancements (2025-08-12)
  SYSTEM_INDEX.md — Aetherra System Index
  THREAT_MODEL.md — Aetherra Threat Model (Alpha)
tests/
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
  capabilities/
    test_aether_e2e.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_agent_collaboration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_crash_recovery_simulation.py — Crash Recovery Simulation Capability Test
    test_deterministic_profile_harness.py — Deterministic Profile Harness Test
    test_diagnostics_schema.py — Diagnostics JSON schema contract test.
    test_extended_crash_recovery.py — Extended Crash Recovery & Service Rehydration Capability Test
    test_hello_plugin_capability.py — Capability: hello plugin executes & returns expected greeting structure.
    test_hello_plugin_metadata.py
    test_hub_metrics_observability.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_and_chat_integration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_quantum_endpoint.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_telemetry_and_federation.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_trainer_disabled_and_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_trainer_endpoints.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat.py — !/usr/bin/env python3
    test_lyrixa_chat_bridge_schema.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat_endpoint.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_chat_schema_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_ownership_answer.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_lyrixa_primary_chat.py — Lyrixa primary chat path tests.
    test_memory_fragmentation_metrics.py
    test_memory_module_integrity.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_recall.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_systems_coverage.py — Test quantum memory engine initialization edge cases."""
    test_ownership_memory.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_plugin_analytics_coverage.py — Create a plugin analytics engine for testing."""
    test_plugin_exec_migrator.py — Capability test: plugin execution analytics schema migrator.
    test_plugin_parallel_and_failure_paths.py — Capability test: parallel plugin execution, failure + timeout paths.
    test_plugin_reload.py — Temporary plugin used to validate unregister + re-register lifecycle.
    test_qfac_in_os.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_reflection_memory_stability.py — Reflection / Memory Stability Test
    test_security_capabilities_coverage.py — Test edge cases in capability granting system."""
    test_security_sandbox_placeholders.py — Security Sandbox Placeholder Capability Test
    test_self_improvement_metrics.py — Tests for SelfImprovementEngine internal metrics counters.
    test_self_maintenance_services.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_snapshot_replay_harness.py
    test_static_security_scan.py
    test_transcendence_deterministic_metrics.py — Tests for deterministic baseline & metrics counters in BeyondTranscendenceEngine.
    test_working_api_coverage.py — Test security capabilities using actual available functions."""
  coding/
    test_revert_and_diff.py
  consciousness/
    conftest.py
    test_active_inference_integration.py
    test_event_bus_bridge.py
    test_identity_unified.py
    test_metrics_exporter.py
    test_metrics_scrape.py
    test_narrative_tone_markers.py
    test_self_model.py
    test_sensor_stubs.py
    test_workspace_basic.py
  demos/
    test_self_improvement_demo.py — SPDX-License-Identifier: GPL-3.0-or-later
  failure_injection/
    test_hmr_rollback.py — Failure injection for HMR rollback.
    test_memory_offline.py — Failure injection: simulate memory offline and assert graceful fallback.
    test_persist_tasks_corrupted.py
    test_persist_tasks_restart.py
    test_plugin_timeout.py — Failure injection: plugin invoke timeout should increment timeout metrics.
  gui/
    README.md — gui
    test_gui.py — !/usr/bin/env python3
    test_hybrid_gui.py — !/usr/bin/env python3
    test_live_gui_generation.py — Types of UI elements that can be dynamically generated"""
    test_lyrixa_gui.py — Test the Lyrixa Hybrid GUI directly
  integration/
    README.md — integration
    test_hub_compat_parity.py — Compat parity test ensuring deprecated shim still re-exports expected API.
    test_integration.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_launcher_detection.py — !/usr/bin/env python3
    test_metrics_histograms_end_to_end.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_phase2_bridge.py — Simulate live backend data updates"""
    test_phase2_launcher.py — Test Phase 2 launcher integration
    test_phase2_simple.py — Test Phase 2 launcher integration without GUI creation.
    test_phase3.py — !/usr/bin/env python3
    test_phase6_integration.py — Test that all Phase components can be imported."""
    test_plugin_ecosystem.py — Test core plugin ecosystem functionality."""
    test_qfac_live_metrics_integration.py
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
    phase_7_4_test.py — Test Phase 7.4 multidimensional consciousness integration."""
    phase_7_4_ultimate_test.py — Execute ultimate Phase 7.4 transcendence test."""
    phase_7_5_test.py — Test Phase 7.5 transcendence consolidation integration."""
    phase_8_1_test.py — Test Phase 8.1 consciousness singularity achievement."""
    phase_8_2_test.py — Test Phase 8.2 cosmic consciousness integration."""
    phase_8_3_test.py — Test Phase 8.3 beyond transcendence integration."""
  meta/
    test_meta_cognition_stubs.py — Smoke tests ensuring MetaCognitionSystem public APIs are callable.
  plugins/
    test_demo_scaffold_plugin.py
  quantum/
    test_qrng_qhash.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_random_features.py — SPDX-License-Identifier: GPL-3.0-or-later
  security/
    test_plugin_signing_fallback.py — SPDX-License-Identifier: GPL-3.0-or-later
  tools/
    test_license_tools.py
    test_quality_gates_pr_description.py
    test_run_go_no_go_gates.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_verify_docs_consistency.py
  unit/
    README.md — unit
    test_ab_recall_engine.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_intent_language.py — Comprehensive test suite for .aether Intent Language"""
    test_aether_script_audit.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_require.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_script_transactions_trace.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_aether_static_risk.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_agent_orchestrator_shim.py — Tests for deprecated agent orchestrator shim module.
    test_ai_stream_debug_frame.py
    test_ai_stream_replay_and_timeout.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_api_keys_enforcement.py
    test_api_keys_prod_encryption_required.py
    test_backpressure_guard.py
    test_capabilities_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_capability_limits.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_chat_idempotency.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_consciousness_narrative_layer.py — Narrative layer tests (Phase 1)
    test_consciousness_self_model_and_events.py — Phase 1 Consciousness basic tests
    test_create_aether_from_task.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_engine_reset_env_vars.py
    test_federation_manager.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_federation_persistence.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_gui_smoke.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hmr_denied_metrics.py
    test_hub_agents_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_ai_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_chat_safety_preflight.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_coherence_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_control_plane.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_hmr_config_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_hmr_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_inthread.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_klm_keb_api.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_klm_keb_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_metrics_ab_series.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_metrics_prometheus.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_metrics_rate_limited_counter.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_orchestrator_counters.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_orchestrator_counters_increment.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_non_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_schema_negative.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_signed_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_strict.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_plugin_registration_strict_invalid_sig.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_quantum_and_chat_metrics.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_rate_limit_behavior.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_hub_ws_advertise_allowlist.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_human_style_layer.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_imports.py — !/usr/bin/env python3
    test_invalid_token_metric.py
    test_kernel_reply_waiter.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_kernel_reply_waiter_timeout_and_error.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_kernel_submit_plugin_invoke.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_klm_keb_control_plane.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_klm_keb_edge_cases.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_live_ai_fallback.py — Test the actual AI fallback system with real API calls"""
    test_manifest_schema_and_trust.py — .strip()
    test_memory_engine_typed_and_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_memory_kernel.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_metrics_reference_sync.py
    test_net_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_night_cycle_tz.py
    test_night_schedule_guard_metric.py
    test_orchestrator_canonical_import.py
    test_plugin_policy_budgets.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_plugin_signature_path.py
    test_plugin_timeout_clamp.py
    test_plugins_minimal.py
    test_policy_bootstrap_cli.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_prod_defaults_policy.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_prod_security_guard.py
    test_prompt_defense.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_qfac_modes.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_qfac_policy.py
    test_qfac_policy_gate_metrics.py
    test_quantum_aware_simulations.py — Test suite for Quantum-Aware Simulations system"""
    test_quantum_enhanced_recall.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_quantum_memory_hardening.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_scratchpad_policy_default_redacted.py
    test_security_ledger_disabled.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_security_metrics_phase0.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_self_evolving_behavior.py — Test core self-evolving behavior functionality."""
    test_sse_replay_gap_metric.py
    test_sse_retry_after_header.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_telemetry_optin.py — SPDX-License-Identifier: GPL-3.0-or-later
    test_unicode_fix.py — !/usr/bin/env python3
    test_ws_idempotency.py — SPDX-License-Identifier: GPL-3.0-or-later
  conftest.py — Provide the project root path for tests"""
  README.md — Aetherra Tests
  schema_validators.py — Lightweight shape checks for Lyrixa chat bridge responses.
  test_aar_outbox.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_aether_script_basic.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_agent_pipeline_smoke.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_discovery_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_headers_and_expiry.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_hmr_phase2.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_hub_signing.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_os_kernel_imports.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_outbox_unit.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_quiesce_drain.py — SPDX-License-Identifier: GPL-3.0-or-later
  test_sse_v2.py — SPDX-License-Identifier: GPL-3.0-or-later
tools/
  maintenance/
    advanced_analyzer.py — Deep analysis of file content and purpose"""
    advanced_analyzer_fixed.py — Extract decorator name from AST node"""
    check_architecture.py — Simple checker for critical architectural compliance"""
    check_unicode.py — Check for Unicode characters in a file.
    complete_organizer.py — Generate a comprehensive reorganization plan based on file analysis"""
    create_documentation.py — Load the updated project analysis"""
    debug_registry_connection.py — !/usr/bin/env python3
    final_file_organizer.py — Get the strategic file moves that make the most sense"""
    final_legal_check.py — Perform final legal compliance verification.
    fix_architecture.py — Auto-fixer for architectural violations"""
    fix_architecture_simple.py — Auto-fixer for architectural violations"""
    fix_imports.py — Utility class to fix import issues in Aetherra repository."""
    fix_phase7_errors.py — Fix CSS box-shadow warnings by removing unsupported properties"""
    fix_plugin_imports.py — Get list of plugin files that have relative import errors."""
    fix_remaining_errors_round2.py — Fix the 'dict' object has no attribute 'type' error in phase3_auto_generator.py"""
    fix_remaining_imports.py — Fix all remaining Lyrixa imports in core files
    fix_unicode_issues.py — Fix Unicode issues in all Python files"""
    fix_unicode_service_registry.py — SPDX-License-Identifier: GPL-3.0-or-later
    focused_cleanup.py — Perform targeted cleanup of identified issues
    generate_reports.py — Load analysis results from JSON file"""
    launch_monitor.py — !/usr/bin/env python3
    post_cleanup_import_updater.py — Update import statements in a single file"""
    project_analyzer.py — Calculate SHA256 hash of file content"""
    quick_fix_imports.py — Check if Python version is compatible."""
    safe_cleanup.py — Load the project analysis"""
    smart_cleanup.py — Only the most obvious misplacements"""
    universal_directory_analyzer.py — Calculate SHA256 hash of file content"""
    validate_architecture.py — Result of directory validation"""
    verify_imports.py — Return True if the import target should be considered valid.
    verify_legal_compliance.py — Check all installed packages for GPL-3.0 compatibility."""
  ab_recall_benchmark.py — A/B recall benchmark harness for classical vs quantum-enriched recall.
  agents_probe.py — Agent fabric probe utility (simplified placeholder)."""
  analyze_project.py — Detect key subsystems by presence of canonical files and dirs."""
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
  debug_fallback_metrics.py
  debug_live_edit_plan.py
  dependency_lock.py — Generate a simple frozen dependency lock file (requirements.lock).
  dev_quickstart.py — Developer ultra-quick start helper.
  diag_rate_limit_stream.py
  enforce_license_policy.py — Lightweight license policy enforcement / telemetry.
  enforce_lock_sync.py — Verify that current environment matches requirements.lock.
  engine_audit.py — SPDX-License-Identifier: GPL-3.0-or-later
  engine_inspector.py — Ranking heuristic to pick canonical implementation.
  engine_usage_matrix.py — SPDX-License-Identifier: GPL-3.0-or-later
  engine_usage_probe.py — SPDX-License-Identifier: GPL-3.0-or-later
  format_changelog.py — Normalize CHANGELOG.md formatting after semantic-release.
  format_lint.py — Unified formatter & linter runner for Aetherra.
  generate_file_index.py — Best-effort: return first line of top-level docstring or leading comment.
  generate_integrity_manifest.py — Generate integrity manifest for release artifacts.
  generate_metrics_reference.py — Generate docs/METRICS_REFERENCE.md from live metrics_accum definitions.
  generate_parse_baseline.py — Generate a baseline parse status JSON for all .aether workflows.
  generate_risk_badge.py — Generate Shields.io endpoint JSON for total .aether static risk score.
  generate_sbom.py — Generate minimal SBOM (alpha) from license_report JSON.
  guard_discord_exclusion.py — CI/packaging guard to ensure the internal Discord Bot directory is excluded.
  introspect_mock_counter.py
  introspect_mock_total.py
  license_report.py — Generate a license report for Python dependencies.
  lyrixa_connectivity_test.py — SPDX-License-Identifier: GPL-3.0-or-later
  lyrixa_diagnostics.py — Return a structure with deterministic key ordering for JSON emission.
  memory_fragmentation_metrics.py — Memory Fragmentation / Compaction Metrics (Lightweight)
  migrate_legacy_aether.py — !/usr/bin/env python3
  nightly_hallucination_audit.py — !/usr/bin/env python3
  organize_repo.py — !/usr/bin/env python3
  os_smoke.py — Headless smoke test scaffold (alpha)."""
  outbox_drain.py — !/usr/bin/env python3
  packaging_smoke.py — Packaging smoke test.
  parse_baseline_regression_gate.py — Parse Baseline Regression Gate
  precommit_block_legacy_hub.py — Pre-commit hook: block new imports of deprecated aetherra_hub_server.
  precommit_sign_aether.py — !/usr/bin/env python3
  probe_ai_endpoints.py — Read a few SSE lines safely with a time limit.
  probe_rate_limit_stream.py
  provenance_tag_wrapper.py
  prune_aetherra_gui.py — !/usr/bin/env python3
  prune_license_overrides.py — Prune stale entries from license_overrides.yml.
  quality_gates.py — Run a command and return (exit_code, stdout+stderr) decoded as UTF-8.
  quarantine_unused_engines.py — SPDX-License-Identifier: GPL-3.0-or-later
  repo_security_scan.py — Lightweight repository security & hygiene scan.
  repro_3018_internal.py
  repro_metrics_baseline.py — !/usr/bin/env python3
  repro_test_metrics_case.py
  root_cleanup.py — Root cleanup orchestrator (non-destructive by default).
  run_go_no_go_gates.py — Launcher smoke: phased boot + registry core services.
  run_hub_ai_api.py — !/usr/bin/env python3
  run_regression_suite.py — Unified regression suite runner.
  sign_aether.py — !/usr/bin/env python3
  sign_release_manifest.py — Create and (optionally) sign a release manifest of built artifacts.
  smoke_test_hub_connector.py — !/usr/bin/env python3
  snapshot_replay_harness.py — Snapshot & Replay Harness
  spdx_verify.py — SPDX & Attribution Consistency Checker
  spec_tests_gate.py — !/usr/bin/env python3
  static_security_scan.py — Static Security Scan Tool
  test_selection_stub.py — Test Selection Stub
  update_spdx_ids.py — Fetch the current SPDX license list and store a simplified ID array.
  update_system_index.py — Return (emoji, label) reduced status from doc content.
  validate_engine_imports.py — SPDX-License-Identifier: GPL-3.0-or-later
  validate_import_map.py — !/usr/bin/env python3
  validate_license_overrides.py — Validate license_overrides.yml structure & SPDX expressions (basic heuristics).
  verify_aether_scripts.py — Return all .aether files under the repo, excluding transient/ignored dirs.
  verify_architecture_map.py — Validate hub compatibility layer + Lyrixa chat service.
  verify_docs_consistency.py — Extract content under a markdown heading (any level >= 2) until the next heading of any level.
  verify_llm_setup.py — Attempt a minimal local round-trip if SDKs are installed and keys present.
  verify_release_manifest.py — Verify release manifest integrity and optional signature.
  verify_ui_standards.py — !/usr/bin/env python3
  verify_version_badge.py — Verify README version badge matches declared version.
  vuln_scan.py — Lightweight vulnerability scan wrapper (alpha implementation).
adk_demo_ui.py — SPDX-License-Identifier: GPL-3.0-or-later
advanced_project_intelligence.json
Aether Script Language Specification.md — Aether Script Language System (`.aether`) — Legacy Spec (v1.0)
aether.py — Execute Aether Script content."""
aether_static_report.md — .aether Verification Report
aetherra_aar_broker.py — !/usr/bin/env python3
aetherra_adaptive_behavior.py — Represents a learned behavior pattern."""
aetherra_agent_daemon.py — !/usr/bin/env python3
aetherra_agent_fabric.py — !/usr/bin/env python3
AETHERRA_CLAIMS_VALIDATION.md — Aetherra OS — Capabilities Validation Snapshot (2025-08-12)
aetherra_cognitive_task_manager.py — Initialize Flask app and routes."""
aetherra_cognitive_task_manager_simple.py — Simplified cognitive task manager that definitely works."""
aetherra_core_analyzer.py — Calculate SHA256 hash of file content"""
aetherra_core_cleaner.py — Remove exact duplicate files, keeping the one in the most appropriate directory"""
aetherra_core_cleanup_backup.json
aetherra_event_bus.py — !/usr/bin/env python3
aetherra_file_watcher.py — Determine if a file should be processed."""
aetherra_hmr_controller.py — Hot Module Reload controller service.
aetherra_hub_server.py — Deprecated monolithic hub server shim.
aetherra_import_updater.py — Update import statements in a single file"""
aetherra_kernel_loop.py — Evaluate production backpressure & plugin safety invariants.
aetherra_kernel_metrics.json
aetherra_live_monitor.py — !/usr/bin/env python3
aetherra_lyrixa_cleaner.py — Safely move a file to new location"""
aetherra_meta_memory.py — Initialize the meta-memory database."""
aetherra_module_manager.py — Minimal, safe module manager with a clear contract."""
aetherra_os.py — Launch the designated Aetherra GUI interface and start OS backend"""
aetherra_os_launcher.py — Adapts LyrixaMemorySystem to the kernel's expected interface."""
aetherra_outbox.py — !/usr/bin/env python3
aetherra_persistent_memory.py — Individual memory node with cognitive metadata."""
aetherra_plugin_catalog.json
aetherra_plugin_discovery.py — Plugin metadata structure."""
aetherra_plugin_viewer.py — Simple GUI to view discovered plugins."""
aetherra_plugins_cleaner.py — Safely remove a file with backup info"""
aetherra_quantum_meta_learning.py — Calculate measurement probability for this state."""
aetherra_script_service.py — Minimal .aether interpreter with async interface."""
aetherra_self_organizer.py — Comprehensive metadata for each file in the system."""
aetherra_service_registry.py — Service health status enumeration."""
aetherra_shared_service_registry.py — Service health status enumeration."""
aetherra_startup.py — SPDX-License-Identifier: GPL-3.0-or-later
agent_pipeline_ui.py — SPDX-License-Identifier: GPL-3.0-or-later
ai_os_test.aether
BETA_READINESS_REPORT.md — Aetherra Beta Readiness Report
beyond_transcendence_engine.py — Legacy import shim for BeyondTranscendenceEngine.
CHANGELOG.md — Changelog
chat_stream_ui.py — SPDX-License-Identifier: GPL-3.0-or-later
clean_hub_tmp.py — 🧩 Built-in Aetherra Hub Server"""
clean_hub_tmp_utf8.py — 🧩 Built-in Aetherra Hub Server (UTF-8 cleaned copy)
CODE_OF_CONDUCT.md — Code of Conduct
config.json
CONTRIBUTING.md — Contributing
copyright_header.py — !/usr/bin/env python3
coverage.json
DEPLOYMENT_TIERS.md — Aetherra Deployment Tiers
diff_clean.py
ENGINE_CURATION_PROPOSAL.md — Engine Curation Proposal (Dry-Run Plan)
ENGINE_USAGE_MATRIX.md — Engine Usage Matrix
evolution_history.aether
GOVERNANCE.md — Project Governance
INSTALL.md — Installation & Quickstart
integrity_manifest.json
intelligence_report_generator.py — Load analysis data from JSON file"""
kernel_status_ui.py — SPDX-License-Identifier: GPL-3.0-or-later
launch_aetherra_unicode.py — Legacy shim retained for backward compatibility; delegates to aetherra_os."""
LEGAL_COMPLIANCE.md — Aetherra Project - Legal Compliance Documentation
LICENSE_POLICY.md — License Policy & Enforcement Gates
licenses_report.json
licenses_unknown_history.json
live_file_index.json
lyrixa_intelligence.json
lyrixa_system_check.aether
main.py — Convenience launcher alias for aetherra_os main entry point.
OWNERSHIP.md — Ownership & Release Authority
package-lock.json
package.json
parse_baseline_local.json
parse_baseline_sample.json
phase2_integration_report.json
PHASE_5_MILESTONE.md
PRIVACY.md — Privacy Policy (Project Repository)
QUANTUM_CONSCIOUSNESS_BREAKTHROUGH_ANNOUNCEMENT.md — 🎉 PHASE 7.2 ADVANCED QUANTUM COGNITION - COMPLETE! ✅
quantum_memory_bridge.py — Quantum memory bridge placeholder (alpha stub)."""
README.md — Aetherra
README_DEPLOY.md — Aetherra Deployment Guide
RELEASE_NOTES_0.5.0-beta.0.md — Aetherra 0.5.0-beta.0 Release Notes
restart_aetherra.py — Perform pre-restart system checks"""
ROADMAP.md — Aetherra Roadmap
root_cleanup_apply.json
root_cleanup_dryrun.json
root_cleanup_prune.json
sbom.json
SECURITY.md — Security Policy
self_model.json
self_organizer.aether
setup.py — !/usr/bin/env python3
setup_dev.py — Print the Aetherra setup banner"""
SMOKE_PROFILE.md — Deterministic Smoke Profile
STEWARDSHIP.md — Aetherra Stewardship Statement
SUPPORT.md — Support
test_ai_os.aether
test_consciousness_dashboards.py — Test importing all consciousness dashboard components.
test_consciousness_integration.py — Test that all consciousness components can be imported"""
test_hub_plugins.py — !/usr/bin/env python3
test_multiple_plugins.py — Test installing multiple plugins
test_plugin_installation.py — Handles plugin installation for Lyrixa Basic"""
test_real_backend.py — SPDX-License-Identifier: GPL-3.0-or-later
test_real_llm.py — SPDX-License-Identifier: GPL-3.0-or-later
test_shared_registry.py — !/usr/bin/env python3
ui_standards_report.md — UI Standards Report
unicode_logger.py — Unicode-safe logging helpers (alpha utility)."""
website_truth_audit.md — Aetherra Website Truth Audit
wf_sample.json
what is Aether Script.md — Aether Script (`.aether`) Language Overview
workflow_failures.md — Workflow Failure Classification
workflow_failures_postpush.json
workflow_failures_postpush.md — Workflow Failure Classification
workflow_failures_sample.json
workflow_failures_sample.md — Workflow Failure Classification
```
