"""
🔗 QFAC PHASE INTEGRATION MODULE
================================================================================
Handles integration between Phase 2 (FractalEncoder), Phase 3 (ObserverEffectSimulator),
and Phase 4 (CausalBranchSimulator) with proper dependency management.

This module provides:
- Clean import paths for cross-phase integration
- Fallback mechanisms when components are not available
- Unified interface for multi-phase operations
- Production-ready component coordination
"""

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class QFACIntegrationManager:
    """Manages integration between QFAC phases with graceful degradation"""

    def __init__(self, base_path: str = None):
        """Initialize integration manager with component discovery"""
        if base_path is None:
            base_path = Path(__file__).parent
        else:
            base_path = Path(base_path)

        self.base_path = base_path
        self.aetherra_path = base_path / "Aetherra" / "lyrixa" / "memory"

        # Component availability flags
        self.phase2_available = False
        self.phase3_available = False
        self.phase4_available = False

        # Component instances
        self.fractal_encoder = None
        self.observer_simulator = None
        self.causal_simulator = None

        # Discover and load available components
        self._discover_components()

    def _discover_components(self):
        """Discover which QFAC components are available"""
        try:
            # Check for Phase 2: FractalEncoder
            if self._check_component_availability("fractal_encoder"):
                self.phase2_available = True
                print("[OK] Phase 2 (FractalEncoder) available")

            # Check for Phase 3: ObserverEffectSimulator
            if self._check_component_availability("observer_effect_simulator"):
                self.phase3_available = True
                print("[OK] Phase 3 (ObserverEffectSimulator) available")

            # Check for Phase 4: CausalBranchSimulator
            if self._check_component_availability("causal_branch_simulator"):
                self.phase4_available = True
                print("[OK] Phase 4 (CausalBranchSimulator) available")

        except Exception as e:
            print(f"⚠️ Component discovery failed: {e}")

    def _check_component_availability(self, module_name: str) -> bool:
        """Check if a specific component module is available"""
        # Check in Aetherra memory directory
        aetherra_module_path = self.aetherra_path / f"{module_name}.py"
        if aetherra_module_path.exists():
            return True

        # Check in current directory
        current_module_path = self.base_path / f"{module_name}.py"
        if current_module_path.exists():
            return True

        return False

    async def initialize_phase2(self, data_dir: str = None) -> Optional[Any]:
        """Initialize Phase 2 FractalEncoder if available"""
        if not self.phase2_available:
            return None

        try:
            # Try Aetherra path first
            if (self.aetherra_path / "fractal_encoder.py").exists():
                sys.path.insert(0, str(self.aetherra_path))

            # Import and initialize
            import fractal_encoder

            self.fractal_encoder = fractal_encoder.FractalEncoder(data_dir=data_dir)
            print(f"🧬 Phase 2 initialized: {data_dir or 'default'}")
            return self.fractal_encoder

        except Exception as e:
            print(f"❌ Phase 2 initialization failed: {e}")
            return None

    async def initialize_phase3(
        self, data_dir: str = None, fractal_encoder: Any = None
    ) -> Optional[Any]:
        """Initialize Phase 3 ObserverEffectSimulator if available"""
        if not self.phase3_available:
            return None

        try:
            # Try Aetherra path first
            if (self.aetherra_path / "observer_effect_simulator.py").exists():
                sys.path.insert(0, str(self.aetherra_path))

            # Import and initialize
            import observer_effect_simulator

            self.observer_simulator = observer_effect_simulator.ObserverEffectSimulator(
                data_dir=data_dir,
                fractal_encoder=fractal_encoder or self.fractal_encoder,
            )
            print(f"👁️ Phase 3 initialized: {data_dir or 'default'}")
            return self.observer_simulator

        except Exception as e:
            print(f"❌ Phase 3 initialization failed: {e}")
            return None

    async def initialize_phase4(
        self,
        data_dir: str = None,
        fractal_encoder: Any = None,
        observer_simulator: Any = None,
    ) -> Optional[Any]:
        """Initialize Phase 4 CausalBranchSimulator if available"""
        if not self.phase4_available:
            return None

        try:
            # Import and initialize
            import causal_branch_simulator

            self.causal_simulator = causal_branch_simulator.CausalBranchSimulator(
                data_dir=data_dir,
                fractal_encoder=fractal_encoder or self.fractal_encoder,
                observer_simulator=observer_simulator or self.observer_simulator,
            )
            print(f"🧿 Phase 4 initialized: {data_dir or 'default'}")
            return self.causal_simulator

        except Exception as e:
            print(f"❌ Phase 4 initialization failed: {e}")
            return None

    async def initialize_full_pipeline(
        self, base_data_dir: str = None
    ) -> Dict[str, Any]:
        """Initialize complete Phase 2-3-4 pipeline"""
        print("🚀 Initializing QFAC Full Pipeline...")

        if base_data_dir is None:
            base_data_dir = "qfac_integrated"

        results = {
            "phase2": None,
            "phase3": None,
            "phase4": None,
            "integration_success": False,
        }

        # Initialize Phase 2
        if self.phase2_available:
            results["phase2"] = await self.initialize_phase2(f"{base_data_dir}/phase2")

        # Initialize Phase 3 with Phase 2 integration
        if self.phase3_available:
            results["phase3"] = await self.initialize_phase3(
                f"{base_data_dir}/phase3", results["phase2"]
            )

        # Initialize Phase 4 with Phase 2-3 integration
        if self.phase4_available:
            results["phase4"] = await self.initialize_phase4(
                f"{base_data_dir}/phase4", results["phase2"], results["phase3"]
            )

        # Check integration success
        available_phases = sum(
            [
                1 if results["phase2"] else 0,
                1 if results["phase3"] else 0,
                1 if results["phase4"] else 0,
            ]
        )

        results["integration_success"] = available_phases >= 2

        if results["integration_success"]:
            print(f"[OK] QFAC Pipeline integrated: {available_phases}/3 phases active")
        else:
            print(f"⚠️ Limited integration: {available_phases}/3 phases active")

        return results

    async def demonstrate_integrated_memory_processing(
        self, memory_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Demonstrate complete memory processing through all available phases"""
        print("\n🔬 INTEGRATED MEMORY PROCESSING DEMONSTRATION")
        print("=" * 60)

        results = {
            "input": memory_content,
            "phase2_result": None,
            "phase3_result": None,
            "phase4_result": None,
            "pipeline_success": False,
        }

        memory_id = "integrated_demo"

        try:
            # Phase 2: Fractal Encoding
            if self.fractal_encoder:
                print("🧬 Phase 2: Fractal encoding...")
                results["phase2_result"] = await self.fractal_encoder.encode_memory(
                    memory_id=memory_id,
                    content=memory_content.get("content", ""),
                    metadata=memory_content,
                )
                print(
                    f"   [OK] Fractal patterns: {results['phase2_result'].pattern_count}"
                )

            # Phase 3: Observer Access
            if self.observer_simulator:
                print("👁️ Phase 3: Observer access simulation...")
                results["phase3_result"] = await self.observer_simulator.access_memory(
                    memory_id=memory_id, observer_id="lyrixa_core", access_layer="deep"
                )
                print(
                    f"   [OK] Observer fidelity: {results['phase3_result'].get('fidelity', 'N/A')}"
                )

            # Phase 4: Causal Branching
            if self.causal_simulator:
                print("🧿 Phase 4: Causal branching...")
                branch = await self.causal_simulator.create_causal_branch(
                    source_memory_id=memory_id,
                    memory_content=results["phase3_result"] or memory_content,
                    branch_scenario="Integrated pipeline demonstration",
                )
                results["phase4_result"] = {
                    "branch_id": branch.branch_id,
                    "probability": branch.probability_weight,
                    "coherence": branch.coherence_score,
                }
                print(f"   [OK] Causal branch: {branch.branch_id}")

            results["pipeline_success"] = True
            print("🎉 Integrated processing complete!")

        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            results["pipeline_success"] = False

        return results

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status and capabilities"""
        return {
            "components_available": {
                "phase2_fractal_encoder": self.phase2_available,
                "phase3_observer_simulator": self.phase3_available,
                "phase4_causal_simulator": self.phase4_available,
            },
            "components_initialized": {
                "fractal_encoder": self.fractal_encoder is not None,
                "observer_simulator": self.observer_simulator is not None,
                "causal_simulator": self.causal_simulator is not None,
            },
            "integration_level": self._calculate_integration_level(),
            "base_path": str(self.base_path),
            "aetherra_path": str(self.aetherra_path),
        }

    def _calculate_integration_level(self) -> str:
        """Calculate current integration level"""
        available = sum(
            [self.phase2_available, self.phase3_available, self.phase4_available]
        )

        if available == 3:
            return "Full Integration (Phases 2-3-4)"
        elif available == 2:
            return "Partial Integration (2/3 phases)"
        elif available == 1:
            return "Single Phase Available"
        else:
            return "No Integration Available"


# Global integration manager instance
_integration_manager = None


def get_integration_manager(base_path: str = None) -> QFACIntegrationManager:
    """Get or create the global integration manager"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = QFACIntegrationManager(base_path)
    return _integration_manager


async def demonstrate_full_integration():
    """Demonstrate complete QFAC integration capabilities"""
    print("🔗 QFAC PHASE INTEGRATION DEMONSTRATION")
    print("=" * 80)

    # Initialize integration manager
    manager = get_integration_manager()

    # Show current status
    status = manager.get_integration_status()
    print(f"🎯 Integration Level: {status['integration_level']}")
    print(f"📁 Base Path: {status['base_path']}")
    print(f"🗂️ Aetherra Path: {status['aetherra_path']}")

    # Initialize full pipeline
    pipeline = await manager.initialize_full_pipeline()

    # Demonstrate integrated processing
    if pipeline["integration_success"]:
        test_memory = {
            "content": "User exploring quantum consciousness and fractal cognition patterns",
            "emotional_tag": "fascination",
            "complexity": 0.9,
            "domain": "quantum_consciousness_fractals",
        }

        results = await manager.demonstrate_integrated_memory_processing(test_memory)

        print(f"\n📊 INTEGRATION RESULTS:")
        print(f"   🧬 Phase 2 Success: {'[OK]' if results['phase2_result'] else '❌'}")
        print(f"   👁️ Phase 3 Success: {'[OK]' if results['phase3_result'] else '❌'}")
        print(f"   🧿 Phase 4 Success: {'[OK]' if results['phase4_result'] else '❌'}")
        print(
            f"   🔗 Pipeline Success: {'[OK]' if results['pipeline_success'] else '❌'}"
        )

    print(f"\n🚀 Integration demonstration complete!")
    return manager


if __name__ == "__main__":
    asyncio.run(demonstrate_full_integration())
