"""
🌌 Quantum Memory Integration for Lyrixa
======================================

Quantum-enhanced memory processing layer that seamlessly integrates
Phase 5 Quantum Memory Bridge with the existing LyrixaMemoryEngine.

Features:
- Quantum encoding/retrieval alongside traditional memory operations
- Quantum interference-based memory association discovery
- Quantum coherence monitoring and error correction
- Seamless fallback to classical operations when needed
- Enhanced recall with quantum superposition benefits

Integration Points:
- Extends MemoryOperationResult with quantum metrics
- Adds quantum recall strategy to existing vector/episodic/conceptual
- Quantum-enhanced memory validation and coherence checking
- Quantum state persistence and recovery
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    # Import Phase 5 Quantum Memory Bridge from project root
    import sys
    import os

    # Add project root to path for quantum bridge import
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from quantum_memory_bridge import (
        QuantumMemoryBridge,
        QuantumMemoryState,
        QuantumCircuitTemplate,
        QuantumExperimentResult
    )
    QUANTUM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Quantum memory bridge not available: {e}")
    QUANTUM_AVAILABLE = False
    # Create placeholder classes for graceful degradation
    class QuantumMemoryBridge:
        pass
    class QuantumMemoryState:
        pass
    class QuantumCircuitTemplate:
        pass
    class QuantumExperimentResult:
        pass

from .lyrixa_memory_engine import LyrixaMemoryEngine, MemoryOperationResult, MemorySystemConfig


@dataclass
class QuantumMemoryMetrics:
    """Quantum-specific memory metrics"""
    coherence_score: float = 0.0
    entanglement_strength: float = 0.0
    quantum_fidelity: float = 0.0
    error_correction_rate: float = 0.0
    superposition_advantage: float = 0.0
    measurement_accuracy: float = 0.0
    quantum_volume: int = 0
    decoherence_time: float = 0.0
    gate_fidelity: float = 0.0


@dataclass
class QuantumMemoryOperationResult(MemoryOperationResult):
    """Extended memory operation result with quantum metrics"""
    quantum_enabled: bool = False
    quantum_metrics: Optional[QuantumMemoryMetrics] = None
    quantum_state_id: Optional[str] = None
    quantum_circuit_used: Optional[str] = None
    classical_fallback: bool = False
    quantum_experiment_results: List[QuantumExperimentResult] = field(default_factory=list)


@dataclass
class QuantumMemoryConfig:
    """Configuration for quantum memory operations"""
    quantum_backend: str = "simulator"
    max_qubits: int = 16
    enable_quantum_recall: bool = True
    enable_quantum_encoding: bool = True
    quantum_fallback_threshold: float = 0.5
    enable_interference_experiments: bool = True
    quantum_error_correction: bool = True
    coherence_monitoring_interval: timedelta = timedelta(minutes=30)
    quantum_state_persistence: bool = True
    max_quantum_experiments_per_operation: int = 3


class QuantumEnhancedMemoryEngine(LyrixaMemoryEngine):
    """
    LyrixaMemoryEngine enhanced with quantum memory capabilities

    Extends the base memory engine with:
    - Quantum encoding of memory fragments
    - Quantum superposition-based recall
    - Quantum interference pattern analysis
    - Quantum error correction and validation
    - Seamless classical/quantum hybrid operations
    """

    def __init__(
        self,
        config: Optional[MemorySystemConfig] = None,
        quantum_config: Optional[QuantumMemoryConfig] = None
    ):
        super().__init__(config)

        self.quantum_config = quantum_config or QuantumMemoryConfig()
        self.quantum_available = QUANTUM_AVAILABLE

        # Initialize quantum bridge if available
        if self.quantum_available:
            try:
                self.quantum_bridge = QuantumMemoryBridge(
                    quantum_backend=self.quantum_config.quantum_backend,
                    max_qubits=self.quantum_config.max_qubits
                )
                logging.info("✅ Quantum Memory Bridge initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize quantum bridge: {e}")
                self.quantum_available = False
                self.quantum_bridge = None
        else:
            self.quantum_bridge = None

        # Quantum state tracking
        self.quantum_states: Dict[str, QuantumMemoryState] = {}
        self.quantum_coherence_history: List[Tuple[datetime, float]] = []
        self.last_coherence_check = datetime.now()

        # Enhanced operation stats
        self.quantum_operation_stats = {
            "quantum_encodings": 0,
            "quantum_recalls": 0,
            "quantum_experiments": 0,
            "classical_fallbacks": 0,
            "coherence_corrections": 0,
            "quantum_associations_discovered": 0
        }

    async def remember(
        self,
        content: Any,
        tags: Optional[List[str]] = None,
        category: str = "general",
        fragment_type: Any = None,
        confidence: float = 1.0,
        narrative_role: Optional[str] = None,
        enable_quantum_encoding: Optional[bool] = None
    ) -> QuantumMemoryOperationResult:
        """
        Enhanced memory storage with optional quantum encoding
        """

        # Determine if quantum encoding should be used
        use_quantum = (
            self.quantum_available and
            self.quantum_config.enable_quantum_encoding and
            (enable_quantum_encoding is None or enable_quantum_encoding) and
            confidence >= self.quantum_config.quantum_fallback_threshold
        )

        # Start with classical memory storage
        classical_result = await super().remember(
            content=content,
            tags=tags,
            category=category,
            fragment_type=fragment_type,
            confidence=confidence,
            narrative_role=narrative_role
        )

        # Create quantum-enhanced result
        quantum_result = QuantumMemoryOperationResult(
            success=classical_result.success,
            operation_type="quantum_remember" if use_quantum else "classical_remember",
            fragment_id=classical_result.fragment_id,
            insights=classical_result.insights,
            narrative=classical_result.narrative,
            alerts=classical_result.alerts,
            message=classical_result.message,
            quantum_enabled=use_quantum,
            classical_fallback=not use_quantum
        )

        if not use_quantum or not self.quantum_bridge:
            return quantum_result

        try:
            # Quantum encoding process
            quantum_state_id = f"quantum_memory_{uuid.uuid4()}"

            # Prepare memory data for quantum encoding
            memory_data = {
                "content": str(content),
                "tags": tags or [],
                "category": category,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "fragment_id": classical_result.fragment_id
            }

            # Encode memory into quantum state
            encoding_result = await self.quantum_bridge.encode_memory(
                memory_data=memory_data,
                encoding_strategy="superposition_enhanced"
            )

            if encoding_result.success:
                # Store quantum state
                self.quantum_states[quantum_state_id] = encoding_result.quantum_state

                # Update result with quantum information
                quantum_result.quantum_state_id = quantum_state_id
                quantum_result.quantum_circuit_used = encoding_result.circuit_template.template_id

                # Run quantum association experiments
                if self.quantum_config.enable_interference_experiments:
                    association_experiments = await self._run_quantum_association_experiments(
                        new_state=encoding_result.quantum_state,
                        content=memory_data
                    )
                    quantum_result.quantum_experiment_results = association_experiments

                # Calculate quantum metrics
                quantum_metrics = await self._calculate_quantum_metrics(
                    encoding_result.quantum_state,
                    encoding_result.experiment_results
                )
                quantum_result.quantum_metrics = quantum_metrics

                # Update stats
                self.quantum_operation_stats["quantum_encodings"] += 1
                if association_experiments:
                    self.quantum_operation_stats["quantum_experiments"] += len(association_experiments)

                quantum_result.message = f"{classical_result.message} + quantum encoding successful"
                logging.info(f"🌌 Quantum memory encoding completed for fragment {classical_result.fragment_id}")

            else:
                # Quantum encoding failed, use classical fallback
                quantum_result.classical_fallback = True
                quantum_result.quantum_enabled = False
                quantum_result.message = f"{classical_result.message} (quantum encoding failed, using classical)"
                self.quantum_operation_stats["classical_fallbacks"] += 1
                logging.warning(f"Quantum encoding failed for fragment {classical_result.fragment_id}, using classical fallback")

        except Exception as e:
            # Error in quantum processing, fallback to classical
            quantum_result.classical_fallback = True
            quantum_result.quantum_enabled = False
            quantum_result.message = f"{classical_result.message} (quantum error: {str(e)})"
            self.quantum_operation_stats["classical_fallbacks"] += 1
            logging.error(f"Quantum memory processing error: {e}")

        return quantum_result

    async def recall(
        self,
        query: str,
        recall_strategy: str = "quantum_hybrid",
        limit: int = 10,
        time_filter: Optional[Dict[str, Any]] = None,
        concept_filter: Optional[List[str]] = None,
        quantum_coherence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Enhanced memory recall with quantum superposition capabilities

        New strategies:
        - "quantum": Pure quantum superposition-based recall
        - "quantum_hybrid": Classical + quantum interference recall (default)
        - "quantum_association": Quantum entanglement-based association discovery
        """

        # Start with classical recall for baseline
        classical_results = await super().recall(
            query=query,
            recall_strategy="hybrid" if recall_strategy.startswith("quantum") else recall_strategy,
            limit=limit,
            time_filter=time_filter,
            concept_filter=concept_filter
        )

        # If quantum not available or not requested, return classical results
        if (not self.quantum_available or
            not self.quantum_config.enable_quantum_recall or
            not recall_strategy.startswith("quantum") or
            not self.quantum_bridge):
            return classical_results

        try:
            quantum_results = []

            if recall_strategy in ["quantum", "quantum_hybrid"]:
                # Quantum superposition-based recall
                quantum_recall_results = await self._quantum_superposition_recall(
                    query=query,
                    limit=limit,
                    coherence_threshold=quantum_coherence_threshold
                )
                quantum_results.extend(quantum_recall_results)
                self.quantum_operation_stats["quantum_recalls"] += 1

            if recall_strategy in ["quantum_association", "quantum_hybrid"]:
                # Quantum entanglement-based association discovery
                association_results = await self._quantum_association_recall(
                    query=query,
                    limit=limit//2  # Half limit for associations
                )
                quantum_results.extend(association_results)
                self.quantum_operation_stats["quantum_associations_discovered"] += len(association_results)

            # Merge classical and quantum results for hybrid approach
            if recall_strategy == "quantum_hybrid":
                merged_results = self._merge_classical_quantum_results(
                    classical_results, quantum_results, limit
                )
                return merged_results
            else:
                # Pure quantum recall
                return quantum_results[:limit]

        except Exception as e:
            logging.error(f"Quantum recall error: {e}")
            self.quantum_operation_stats["classical_fallbacks"] += 1
            # Fallback to classical results
            return classical_results

    async def _run_quantum_association_experiments(
        self,
        new_state: QuantumMemoryState,
        content: Dict[str, Any]
    ) -> List[QuantumExperimentResult]:
        """Run quantum interference experiments to discover memory associations"""

        experiments = []

        try:
            # Limit experiments to avoid overwhelming the system
            max_experiments = min(
                self.quantum_config.max_quantum_experiments_per_operation,
                len(self.quantum_states)
            )

            # Select representative existing quantum states for interference
            existing_states = list(self.quantum_states.values())[:max_experiments]

            for existing_state in existing_states:
                try:
                    # Run quantum interference experiment
                    interference_result = await self.quantum_bridge.run_interference_experiment(
                        state_a=new_state,
                        state_b=existing_state,
                        experiment_type="association_discovery"
                    )

                    if interference_result.success:
                        experiments.append(interference_result)

                except Exception as e:
                    logging.warning(f"Quantum interference experiment failed: {e}")
                    continue

            return experiments

        except Exception as e:
            logging.error(f"Error running quantum association experiments: {e}")
            return []

    async def _quantum_superposition_recall(
        self,
        query: str,
        limit: int,
        coherence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Recall memories using quantum superposition and measurement"""

        results = []

        try:
            # Create quantum query state
            query_encoding = await self.quantum_bridge.encode_memory(
                memory_data={"query": query, "type": "search"},
                encoding_strategy="query_superposition"
            )

            if not query_encoding.success:
                return results

            # Test quantum state against stored quantum memories
            for state_id, quantum_state in self.quantum_states.items():
                try:
                    # Run quantum comparison
                    comparison_result = await self.quantum_bridge.run_interference_experiment(
                        state_a=query_encoding.quantum_state,
                        state_b=quantum_state,
                        experiment_type="similarity_measurement"
                    )

                    if (comparison_result.success and
                        comparison_result.coherence_score >= coherence_threshold):

                        # Retrieve classical memory for this quantum state
                        retrieved_memory = await self._retrieve_classical_memory_for_quantum_state(state_id)

                        if retrieved_memory:
                            results.append({
                                "content": retrieved_memory,
                                "source": "quantum_superposition",
                                "relevance_score": comparison_result.coherence_score,
                                "type": "quantum_match",
                                "quantum_state_id": state_id,
                                "quantum_coherence": comparison_result.coherence_score,
                                "measurement_fidelity": comparison_result.measurement_fidelity
                            })

                except Exception as e:
                    logging.warning(f"Quantum comparison failed for state {state_id}: {e}")
                    continue

            # Sort by quantum relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logging.error(f"Quantum superposition recall error: {e}")
            return []

    async def _quantum_association_recall(
        self,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Discover memory associations using quantum entanglement patterns"""

        associations = []

        try:
            # Find quantum states with high entanglement to query
            query_encoding = await self.quantum_bridge.encode_memory(
                memory_data={"query": query, "type": "association_search"},
                encoding_strategy="entanglement_discovery"
            )

            if not query_encoding.success:
                return associations

            # Test for quantum entanglement patterns
            for state_id, quantum_state in self.quantum_states.items():
                try:
                    entanglement_result = await self.quantum_bridge.run_interference_experiment(
                        state_a=query_encoding.quantum_state,
                        state_b=quantum_state,
                        experiment_type="entanglement_detection"
                    )

                    if (entanglement_result.success and
                        entanglement_result.entanglement_strength > 0.3):

                        retrieved_memory = await self._retrieve_classical_memory_for_quantum_state(state_id)

                        if retrieved_memory:
                            associations.append({
                                "content": retrieved_memory,
                                "source": "quantum_entanglement",
                                "relevance_score": entanglement_result.entanglement_strength,
                                "type": "quantum_association",
                                "quantum_state_id": state_id,
                                "entanglement_strength": entanglement_result.entanglement_strength
                            })

                except Exception as e:
                    logging.warning(f"Quantum entanglement check failed for state {state_id}: {e}")
                    continue

            # Sort by entanglement strength
            associations.sort(key=lambda x: x["relevance_score"], reverse=True)
            return associations[:limit]

        except Exception as e:
            logging.error(f"Quantum association recall error: {e}")
            return []

    async def _retrieve_classical_memory_for_quantum_state(self, quantum_state_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the classical memory associated with a quantum state"""

        try:
            # In a full implementation, this would map quantum state IDs to classical fragment IDs
            # For now, we'll use a simplified approach

            # Search for fragment with matching quantum_state_id in metadata
            for fragment in self.fractal_mesh.fragments.values():
                if (hasattr(fragment, 'quantum_state_id') and
                    fragment.quantum_state_id == quantum_state_id):
                    return {
                        "fragment_id": fragment.fragment_id,
                        "content": fragment.content,
                        "confidence": fragment.confidence_score,
                        "created_at": fragment.created_at.isoformat(),
                        "tags": list(fragment.symbolic_tags)
                    }

            return None

        except Exception as e:
            logging.error(f"Error retrieving classical memory for quantum state {quantum_state_id}: {e}")
            return None

    def _merge_classical_quantum_results(
        self,
        classical_results: List[Dict[str, Any]],
        quantum_results: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Intelligently merge classical and quantum recall results"""

        try:
            # Combine results with weighted scoring
            all_results = []

            # Add classical results with weight factor
            for result in classical_results:
                result["combined_score"] = result["relevance_score"] * 0.7  # 70% weight for classical
                result["result_type"] = "classical"
                all_results.append(result)

            # Add quantum results with weight factor
            for result in quantum_results:
                result["combined_score"] = result["relevance_score"] * 1.3  # 130% weight for quantum
                result["result_type"] = "quantum"
                all_results.append(result)

            # Remove duplicates (if classical and quantum found same memory)
            unique_results = []
            seen_content = set()

            for result in all_results:
                content_key = str(result.get("content", ""))[:100]  # Use first 100 chars as key

                if content_key not in seen_content:
                    seen_content.add(content_key)
                    unique_results.append(result)

            # Sort by combined score
            unique_results.sort(key=lambda x: x["combined_score"], reverse=True)

            return unique_results[:limit]

        except Exception as e:
            logging.error(f"Error merging classical and quantum results: {e}")
            # Fallback to classical results
            return classical_results[:limit]

    async def _calculate_quantum_metrics(
        self,
        quantum_state: QuantumMemoryState,
        experiment_results: List[QuantumExperimentResult]
    ) -> QuantumMemoryMetrics:
        """Calculate quantum-specific metrics for memory operations"""

        try:
            metrics = QuantumMemoryMetrics()

            # Basic quantum state metrics using available attributes
            metrics.coherence_score = getattr(quantum_state, 'encoding_fidelity', 0.5)
            metrics.quantum_fidelity = getattr(quantum_state, 'encoding_fidelity', 0.5)
            metrics.quantum_volume = getattr(quantum_state, 'qubit_count', 4)

            # Experiment-based metrics
            if experiment_results:
                metrics.entanglement_strength = sum(
                    r.entanglement_strength for r in experiment_results if r.success
                ) / len(experiment_results)

                metrics.measurement_accuracy = sum(
                    r.measurement_fidelity for r in experiment_results if r.success
                ) / len(experiment_results)

                metrics.error_correction_rate = sum(
                    1 for r in experiment_results if r.success
                ) / len(experiment_results)

            # Calculate superposition advantage (simplified)
            if hasattr(quantum_state, 'superposition_advantage'):
                metrics.superposition_advantage = quantum_state.superposition_advantage
            else:
                metrics.superposition_advantage = metrics.coherence_score * 0.8

            # Estimate decoherence time (simplified)
            metrics.decoherence_time = max(1.0, metrics.coherence_score * 10.0)  # ms

            # Gate fidelity estimation
            metrics.gate_fidelity = min(0.99, metrics.quantum_fidelity * 1.1)

            return metrics

        except Exception as e:
            logging.error(f"Error calculating quantum metrics: {e}")
            return QuantumMemoryMetrics()  # Return default metrics

    async def check_quantum_coherence(self) -> Dict[str, Any]:
        """Monitor quantum state coherence and perform corrections if needed"""

        if not self.quantum_available or not self.quantum_bridge:
            return {"quantum_available": False, "message": "Quantum bridge not available"}

        try:
            coherence_results = {
                "check_time": datetime.now().isoformat(),
                "total_quantum_states": len(self.quantum_states),
                "coherent_states": 0,
                "decoherent_states": 0,
                "corrected_states": 0,
                "average_coherence": 0.0,
                "recommendations": []
            }

            total_coherence = 0.0

            for state_id, quantum_state in self.quantum_states.items():
                try:
                    # Check coherence using encoding_fidelity
                    current_coherence = getattr(quantum_state, 'encoding_fidelity', 0.5)
                    total_coherence += current_coherence

                    if current_coherence >= 0.7:
                        coherence_results["coherent_states"] += 1
                    else:
                        coherence_results["decoherent_states"] += 1

                        # Attempt error correction if enabled
                        if self.quantum_config.quantum_error_correction:
                            correction_result = await self.quantum_bridge.apply_error_correction(
                                quantum_state, "decoherence_correction"
                            )

                            if correction_result.success:
                                # Update the quantum state
                                self.quantum_states[state_id] = correction_result.corrected_state
                                coherence_results["corrected_states"] += 1
                                self.quantum_operation_stats["coherence_corrections"] += 1

                except Exception as e:
                    logging.warning(f"Coherence check failed for state {state_id}: {e}")
                    continue

            # Calculate average coherence
            if self.quantum_states:
                coherence_results["average_coherence"] = total_coherence / len(self.quantum_states)

            # Add recommendations
            if coherence_results["decoherent_states"] > 0:
                coherence_results["recommendations"].append(
                    "Consider increasing coherence monitoring frequency"
                )

            if coherence_results["average_coherence"] < 0.6:
                coherence_results["recommendations"].append(
                    "System experiencing significant decoherence - quantum operations may be degraded"
                )

            # Store coherence history
            self.quantum_coherence_history.append(
                (datetime.now(), coherence_results["average_coherence"])
            )

            # Keep only last 100 measurements
            if len(self.quantum_coherence_history) > 100:
                self.quantum_coherence_history = self.quantum_coherence_history[-100:]

            self.last_coherence_check = datetime.now()

            return coherence_results

        except Exception as e:
            return {
                "quantum_available": True,
                "error": str(e),
                "message": "Quantum coherence check failed"
            }

    def get_quantum_system_status(self) -> Dict[str, Any]:
        """Get comprehensive quantum memory system status"""

        status = {
            "quantum_available": self.quantum_available,
            "quantum_bridge_active": self.quantum_bridge is not None,
            "quantum_states_count": len(self.quantum_states),
            "last_coherence_check": self.last_coherence_check.isoformat(),
            "quantum_operations": self.quantum_operation_stats.copy(),
            "configuration": {
                "quantum_backend": self.quantum_config.quantum_backend,
                "max_qubits": self.quantum_config.max_qubits,
                "quantum_recall_enabled": self.quantum_config.enable_quantum_recall,
                "quantum_encoding_enabled": self.quantum_config.enable_quantum_encoding,
                "error_correction_enabled": self.quantum_config.quantum_error_correction
            }
        }

        if self.quantum_coherence_history:
            latest_coherence = self.quantum_coherence_history[-1][1]
            status["current_coherence"] = latest_coherence
            status["coherence_trend"] = self._calculate_coherence_trend()

        return status

    def _calculate_coherence_trend(self) -> str:
        """Calculate the trend in quantum coherence over time"""

        if len(self.quantum_coherence_history) < 2:
            return "insufficient_data"

        recent_measurements = self.quantum_coherence_history[-5:]  # Last 5 measurements

        if len(recent_measurements) < 2:
            return "stable"

        # Simple trend calculation
        first_coherence = recent_measurements[0][1]
        last_coherence = recent_measurements[-1][1]

        change = last_coherence - first_coherence

        if abs(change) < 0.05:
            return "stable"
        elif change > 0:
            return "improving"
        else:
            return "degrading"

    async def quantum_maintenance_cycle(self) -> Dict[str, Any]:
        """Run quantum-specific maintenance operations"""

        if not self.quantum_available:
            return {"quantum_available": False, "message": "Quantum maintenance not available"}

        maintenance_results = {
            "start_time": datetime.now().isoformat(),
            "coherence_check": None,
            "error_corrections": 0,
            "state_optimizations": 0,
            "quantum_garbage_collection": 0,
            "performance_improvements": []
        }

        try:
            # 1. Run coherence check and corrections
            coherence_results = await self.check_quantum_coherence()
            maintenance_results["coherence_check"] = coherence_results
            maintenance_results["error_corrections"] = coherence_results.get("corrected_states", 0)

            # 2. Optimize quantum states
            for state_id, quantum_state in list(self.quantum_states.items()):
                try:
                    current_fidelity = getattr(quantum_state, 'encoding_fidelity', 0.5)
                    if current_fidelity < 0.8:
                        optimization_result = await self.quantum_bridge.optimize_quantum_state(
                            quantum_state, "coherence_optimization"
                        )

                        if optimization_result.success:
                            self.quantum_states[state_id] = optimization_result.optimized_state
                            maintenance_results["state_optimizations"] += 1

                except Exception as e:
                    logging.warning(f"State optimization failed for {state_id}: {e}")
                    continue

            # 3. Quantum garbage collection (remove very old, low-coherence states)
            cutoff_time = datetime.now() - timedelta(days=30)
            states_to_remove = []

            for state_id, quantum_state in self.quantum_states.items():
                current_fidelity = getattr(quantum_state, 'encoding_fidelity', 0.5)
                creation_time = getattr(quantum_state, 'creation_timestamp', datetime.now())
                if (current_fidelity < 0.3 and creation_time < cutoff_time):
                    states_to_remove.append(state_id)

            for state_id in states_to_remove:
                del self.quantum_states[state_id]
                maintenance_results["quantum_garbage_collection"] += 1

            # 4. Performance analysis
            if self.quantum_operation_stats["quantum_recalls"] > 0:
                recall_success_rate = (
                    self.quantum_operation_stats["quantum_recalls"] /
                    (self.quantum_operation_stats["quantum_recalls"] +
                     self.quantum_operation_stats["classical_fallbacks"])
                )

                if recall_success_rate > 0.8:
                    maintenance_results["performance_improvements"].append(
                        "High quantum recall success rate - system performing well"
                    )
                else:
                    maintenance_results["performance_improvements"].append(
                        "Consider adjusting quantum coherence thresholds"
                    )

            maintenance_results["end_time"] = datetime.now().isoformat()
            maintenance_results["success"] = True

            return maintenance_results

        except Exception as e:
            maintenance_results["error"] = str(e)
            maintenance_results["success"] = False
            return maintenance_results

    async def get_enhanced_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including quantum components"""

        # Get base system status
        base_status = self.get_system_status()

        # Add quantum information
        quantum_status = self.get_quantum_system_status()

        # Combine and enhance
        enhanced_status = {
            **base_status,
            "quantum_system": quantum_status,
            "hybrid_operations": {
                "total_operations": (
                    self.operation_stats["total_operations"] +
                    sum(self.quantum_operation_stats.values())
                ),
                "quantum_enhanced_ratio": (
                    self.quantum_operation_stats["quantum_encodings"] /
                    max(1, self.operation_stats["total_operations"])
                ),
                "quantum_success_rate": (
                    (self.quantum_operation_stats["quantum_recalls"] +
                     self.quantum_operation_stats["quantum_encodings"]) /
                    max(1, sum(self.quantum_operation_stats.values()))
                )
            },
            "capabilities": {
                "classical_memory": True,
                "quantum_encoding": self.quantum_config.enable_quantum_encoding and self.quantum_available,
                "quantum_recall": self.quantum_config.enable_quantum_recall and self.quantum_available,
                "quantum_associations": self.quantum_config.enable_interference_experiments and self.quantum_available,
                "error_correction": self.quantum_config.quantum_error_correction and self.quantum_available,
                "hybrid_operations": self.quantum_available
            }
        }

        return enhanced_status


# Convenience function for easy integration
def create_quantum_enhanced_memory_engine(
    memory_config: Optional[MemorySystemConfig] = None,
    quantum_config: Optional[QuantumMemoryConfig] = None
) -> QuantumEnhancedMemoryEngine:
    """
    Create a quantum-enhanced memory engine with sensible defaults

    This function provides an easy way to create a quantum-enhanced memory system
    that gracefully falls back to classical operation if quantum components are unavailable.
    """

    if memory_config is None:
        memory_config = MemorySystemConfig()

    if quantum_config is None:
        quantum_config = QuantumMemoryConfig()

    engine = QuantumEnhancedMemoryEngine(
        config=memory_config,
        quantum_config=quantum_config
    )

    return engine


# Example usage and testing
async def demo_quantum_memory_integration():
    """Demonstrate quantum memory integration capabilities"""

    print("🌌 Quantum Memory Integration Demo")
    print("=" * 50)

    # Create quantum-enhanced memory engine
    engine = create_quantum_enhanced_memory_engine()

    # Check system status
    status = await engine.get_enhanced_system_status()
    print(f"✅ System initialized - Quantum available: {status['quantum_system']['quantum_available']}")

    # Store some memories with quantum encoding
    test_memories = [
        ("The concept of quantum superposition enables parallel information processing", ["quantum", "superposition", "processing"]),
        ("Machine learning algorithms can benefit from quantum acceleration", ["ml", "quantum", "acceleration"]),
        ("Consciousness may emerge from quantum coherence in neural systems", ["consciousness", "quantum", "neural"]),
    ]

    print("\n📝 Storing memories with quantum encoding...")
    stored_memories = []

    for content, tags in test_memories:
        result = await engine.remember(
            content=content,
            tags=tags,
            category="scientific",
            confidence=0.9
        )

        stored_memories.append(result)
        status_icon = "🌌" if result.quantum_enabled else "📁"
        print(f"{status_icon} Stored: {content[:50]}...")

        if result.quantum_metrics:
            print(f"   Quantum coherence: {result.quantum_metrics.coherence_score:.3f}")

    # Test different recall strategies
    print("\n🔍 Testing quantum-enhanced recall...")

    test_queries = [
        ("quantum computing", "quantum_hybrid"),
        ("consciousness", "quantum_superposition"),
        ("machine learning", "classical")
    ]

    for query, strategy in test_queries:
        print(f"\n🔎 Query: '{query}' (strategy: {strategy})")

        results = await engine.recall(
            query=query,
            recall_strategy=strategy,
            limit=3
        )

        for i, result in enumerate(results[:2]):
            source_icon = "🌌" if result["source"].startswith("quantum") else "📁"
            print(f"   {source_icon} {result['content'][:60]}...")
            print(f"      Relevance: {result['relevance_score']:.3f} | Source: {result['source']}")

    # Check quantum system health
    print("\n🔧 Quantum system health check...")
    coherence_check = await engine.check_quantum_coherence()

    if coherence_check.get("quantum_available"):
        print(f"   Quantum states: {coherence_check['total_quantum_states']}")
        print(f"   Average coherence: {coherence_check['average_coherence']:.3f}")
        print(f"   Coherent states: {coherence_check['coherent_states']}")
    else:
        print("   Quantum bridge not available - running in classical mode")

    # Final system status
    final_status = await engine.get_enhanced_system_status()
    print("\n📊 Final system statistics:")
    print(f"   Total operations: {final_status['hybrid_operations']['total_operations']}")
    print(f"   Quantum enhancement ratio: {final_status['hybrid_operations']['quantum_enhanced_ratio']:.2%}")

    quantum_ops = engine.quantum_operation_stats
    print(f"   Quantum encodings: {quantum_ops['quantum_encodings']}")
    print(f"   Quantum recalls: {quantum_ops['quantum_recalls']}")
    print(f"   Classical fallbacks: {quantum_ops['classical_fallbacks']}")

    print("\n✅ Quantum memory integration demo completed!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_quantum_memory_integration())
