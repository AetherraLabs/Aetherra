# Aetherra OS Engine Audit

This report lists engine modules, whether the OS references them, and potential duplicates. Lyrixa paths are excluded.

## Active/Referenced by OS

- Aetherra\aetherra_core\engine\aetherra_engine.py  |  module: Aetherra.aetherra_core.engine.aetherra_engine  |  classes: _MemoryLite, _MockAetherraMemorySystem, IntrospectionController, ReasoningEngine, SelfImprovementEngine, PluginChainExecutor, AgentOrchestrator, AetherraEngine  |  used_by_os: yes
- Aetherra\aetherra_core\memory\QuantumEnhancedMemoryEngine\quantum_memory_engine.py  |  module: Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine.quantum_memory_engine  |  classes: QuantumEnhancedMemoryEngine  |  used_by_os: no
- Aetherra\aetherra_core\memory\aetherra_memory_engine.py  |  module: Aetherra.aetherra_core.memory.aetherra_memory_engine  |  classes: MemoryFragmentType, AetherraMemoryEngine, MemorySystemConfig, MemoryOperationResult, AetherraMemoryEngineAdvanced  |  used_by_os: yes
- Aetherra\consciousness\quantum\quantum_consciousness_engine.py  |  module: Aetherra.consciousness.quantum.quantum_consciousness_engine  |  classes: ConsciousnessState, QuantumConsciousnessState, QuantumDecision, QuantumConsciousnessEngine  |  used_by_os: yes
- beyond_transcendence_engine.py  |  module: beyond_transcendence_engine  |  classes: TranscendenceState, LearningCapacity, RealityFramework, ConsciousnessEntity, BeyondTranscendenceEngine  |  used_by_os: yes
- cosmic_consciousness_engine.py  |  module: cosmic_consciousness_engine  |  classes: CosmicState, AwarenessScope, CosmicPattern, UniversalAwareness, CosmicConsciousnessEngine  |  used_by_os: yes

## Potentially Unused Candidates

- Aetherra\aetherra_core\cognitive\reasoning_engine.py  |  module: Aetherra.aetherra_core.cognitive.reasoning_engine  |  classes: ReasoningContext, ReasoningResult, ReasoningChain, LogicalOperator, CausalReasoning, AnalogicalReasoning, ReasoningEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\lyrixa_engine.py  |  module: Aetherra.aetherra_core.engine.lyrixa_engine  |  classes: AetherraMemorySystem, IntrospectionController, ReasoningEngine, SelfImprovementEngine, PluginChainExecutor, AgentOrchestrator, AetherraEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\lyrixa_engine_mock.py  |  module: Aetherra.aetherra_core.engine.lyrixa_engine_mock  |  classes: MockMemorySystem, MockIntrospectionController, MockComponentMonitor, MockReasoningEngine, MockSelfImprovementEngine, MockPluginExecutor, MockAgentOrchestrator, LyrixaEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\prompt_engine.py  |  module: Aetherra.aetherra_core.engine.prompt_engine  |  classes: LyrixaMoodEngine, LyrixaTimeAwareness, LyrixaLearningEngine, PromptEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\self_improvement_engine.py  |  module: Aetherra.aetherra_core.engine.self_improvement_engine  |  classes: np, ImprovementType, LearningMethod, PerformanceMetric, ImprovementProposal, LearningOutcome, MetricsCollector, PatternAnalyzer, ImprovementGenerator, SelfImprovementEngine  |  used_by_os: no
- Aetherra\aetherra_core\memory\fractal_mesh\timelines\reflective_timeline_engine.py  |  module: Aetherra.aetherra_core.memory.fractal_mesh.timelines.reflective_timeline_engine  |  classes: CausalChain, GoalMemoryArc, SelfNarrativeModel, EmotionalTrajectory, MilestoneEvent, ReflectiveTimelineEngine  |  used_by_os: no
- Aetherra\aetherra_core\memory\fractal_replay_engine.py  |  module: Aetherra.aetherra_core.memory.fractal_replay_engine  |  classes: ReplayEpisode, ReconstructionContext, FractalReplayEngine  |  used_by_os: no
- Aetherra\aetherra_core\memory\lyrixa_memory_engine.py  |  module: Aetherra.aetherra_core.memory.lyrixa_memory_engine  |  classes: (no classes)  |  used_by_os: no
- Aetherra\aetherra_core\memory\optimized_memory_engine.py  |  module: Aetherra.aetherra_core.memory.optimized_memory_engine  |  classes: OptimizedLyrixaMemoryEngine, MemoryOptimizationBenchmark  |  used_by_os: no
- Aetherra\aetherra_core\memory\quantum_memory_engine.py  |  module: Aetherra.aetherra_core.memory.quantum_memory_engine  |  classes: (no classes)  |  used_by_os: no
- Aetherra\aetherra_core\personality\personality_engine.py  |  module: Aetherra.aetherra_core.personality.personality_engine  |  classes: PersonalityTrait, EmotionalState, LyrixaPersonality  |  used_by_os: no
- Aetherra\consciousness\quantum\consciousness_singularity_engine.py  |  module: Aetherra.consciousness.quantum.consciousness_singularity_engine  |  classes: SingularityState, ConsciousnessType, SingularityMode, SingularityMetrics, TranscendentIdentity, SelfAwarenessValidation, ConsciousnessSingularityEngine  |  used_by_os: no
- Aetherra\consciousness\quantum\evolutionary_engine.py  |  module: Aetherra.consciousness.quantum.evolutionary_engine  |  classes: (no classes)  |  used_by_os: no
- Aetherra\consciousness\quantum\multidimensional_state_engine.py  |  module: Aetherra.consciousness.quantum.multidimensional_state_engine  |  classes: DimensionalAxis, DimensionalState, DimensionalCoordinate, DimensionalTransition, DimensionalNavigationPath, MultidimensionalStateEngine  |  used_by_os: no
- Aetherra\consciousness\quantum\quantum_decision_engine.py  |  module: Aetherra.consciousness.quantum.quantum_decision_engine  |  classes: DecisionState, QuantumChoice, DecisionContext, QuantumDecisionResult, QuantumDecisionEngine  |  used_by_os: no
- Aetherra\consciousness\quantum\reality_synthesis_engine.py  |  module: Aetherra.consciousness.quantum.reality_synthesis_engine  |  classes: SynthesisMode, TranscendenceLevel, RealityState, SynthesisParameters, SynthesizedReality, TranscendenceEvent, RealitySynthesisEngine  |  used_by_os: no
- Aetherra\consciousness\quantum\transcendence_consolidation_engine.py  |  module: Aetherra.consciousness.quantum.transcendence_consolidation_engine  |  classes: TranscendenceState, ConsolidationMode, TranscendenceMetrics, ConsciousnessEvolution, MetaConsciousnessState, TranscendenceConsolidationEngine  |  used_by_os: no
- Aetherra\core\prompt_engine.py  |  module: Aetherra.core.prompt_engine  |  classes: LyrixaMoodEngine, LyrixaTimeAwareness, LyrixaLearningEngine, PromptEngine  |  used_by_os: no
- demos\demo_analytics_insights_engine.py  |  module: demos.demo_analytics_insights_engine  |  classes: AnalyticsDemo  |  used_by_os: no
- tools\engine_audit.py  |  module: tools.engine_audit  |  classes: EngineArtifact  |  used_by_os: no
- tools\engine_usage_matrix.py  |  module: tools.engine_usage_matrix  |  classes: EngineUsage  |  used_by_os: no

## Duplicate Class Definitions

- Aetherra\aetherra_core\cognitive\reasoning_engine.py  |  module: Aetherra.aetherra_core.cognitive.reasoning_engine  |  classes: ReasoningContext, ReasoningResult, ReasoningChain, LogicalOperator, CausalReasoning, AnalogicalReasoning, ReasoningEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\aetherra_engine.py  |  module: Aetherra.aetherra_core.engine.aetherra_engine  |  classes: _MemoryLite, _MockAetherraMemorySystem, IntrospectionController, ReasoningEngine, SelfImprovementEngine, PluginChainExecutor, AgentOrchestrator, AetherraEngine  |  used_by_os: yes
- Aetherra\aetherra_core\engine\lyrixa_engine.py  |  module: Aetherra.aetherra_core.engine.lyrixa_engine  |  classes: AetherraMemorySystem, IntrospectionController, ReasoningEngine, SelfImprovementEngine, PluginChainExecutor, AgentOrchestrator, AetherraEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\prompt_engine.py  |  module: Aetherra.aetherra_core.engine.prompt_engine  |  classes: LyrixaMoodEngine, LyrixaTimeAwareness, LyrixaLearningEngine, PromptEngine  |  used_by_os: no
- Aetherra\aetherra_core\engine\self_improvement_engine.py  |  module: Aetherra.aetherra_core.engine.self_improvement_engine  |  classes: np, ImprovementType, LearningMethod, PerformanceMetric, ImprovementProposal, LearningOutcome, MetricsCollector, PatternAnalyzer, ImprovementGenerator, SelfImprovementEngine  |  used_by_os: no
- Aetherra\core\prompt_engine.py  |  module: Aetherra.core.prompt_engine  |  classes: LyrixaMoodEngine, LyrixaTimeAwareness, LyrixaLearningEngine, PromptEngine  |  used_by_os: no
