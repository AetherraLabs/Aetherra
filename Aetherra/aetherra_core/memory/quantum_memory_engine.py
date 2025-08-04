from .causal_brancher import CausalBranchSimulator
from .compression import CompressionAnalytics
from .fidelity_metrics import MemoryFidelityScorer
from .fractal_encoder import FractalEncoder
from .observer_effects import ObserverMemoryManager
from .quantum_bridge import QuantumBridgeInterface


class QuantumEnhancedMemoryEngine:
    def __init__(self, config_path="QuantumEnhancedMemoryEngine/quantum_config.json"):
        self.config = self._load_config(config_path)
        self.compression = CompressionAnalytics(self.config)
        self.fractal = FractalEncoder(self.config)
        self.observer = ObserverMemoryManager()
        self.brancher = CausalBranchSimulator()
        self.quantum = QuantumBridgeInterface(self.config)
        self.scorer = MemoryFidelityScorer()

    def _load_config(self, path):
        import json
        import os

        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def store(self, memory_entry: dict) -> dict:
        compressed = self.compression.compress(memory_entry)
        fractalized = self.fractal.encode(compressed)
        observer_encoded = self.observer.apply(fractalized)
        scored = self.scorer.score(observer_encoded)
        return self.quantum.write(observer_encoded, metadata=scored)

    def retrieve(self, query: str, context: dict = None) -> dict:
        # Accept context as Optional[dict]
        results = self.quantum.query(query)
        collapsed = self.brancher.collapse(results, context)
        return self.observer.mutate_upon_access(collapsed)

    def debug_info(self):
        return {
            "quantum_backend": self.quantum.backend_name(),
            "last_fidelity": self.scorer.last_score,
            "coherence_status": self.quantum.coherence_metrics(),
        }
