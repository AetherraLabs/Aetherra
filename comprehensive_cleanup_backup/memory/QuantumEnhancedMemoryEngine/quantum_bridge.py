class QuantumBridgeInterface:
    def __init__(self, config):
        self.config = config

    def write(self, data, metadata=None):
        # Placeholder: just return a dict
        return {"written": data, "metadata": metadata}

    def query(self, query):
        # Placeholder: return a list of mock results
        return [{"result": "mock", "query": query}]

    def backend_name(self):
        return self.config.get("quantum_backend", "simulator")

    def coherence_metrics(self):
        return {"coherence": 1.0}
