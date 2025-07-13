
def process_data(data):
    # This function needs improvement
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
        else:
            result.append(0)
    return result

def calculate_average(numbers):
    # Basic function that could use better error handling
    return sum(numbers) / len(numbers)

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_data(self, value):
        self.data.append(value)
    
    def process_all(self):
        return process_data(self.data)
