class MemoryFidelityScorer:
    def __init__(self):
        self.last_score = 1.0

    def score(self, data):
        # Placeholder: just return a mock score
        self.last_score = 0.99
        return {"score": self.last_score}
