
class DataAnalyzer:
    def __init__(self):
        self.version = "1.2"
        self.features = ["basic_analysis", "median_calculation", "std_deviation"]
    
    def analyze(self, data):
        sorted_data = sorted(data)
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return {
            "mean": mean,
            "median": sorted_data[len(data)//2],
            "std_dev": variance ** 0.5
        }
