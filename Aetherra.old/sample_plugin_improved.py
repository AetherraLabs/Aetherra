
from typing import List, Union

def process_data(data: List[Union[int, float]]) -> List[Union[int, float]]:
    """
    Process a list of numbers by doubling positive values and setting negatives to zero.
    
    Args:
        data: List of numbers to process
        
    Returns:
        List of processed numbers
    """
    if not data:
        return []
    
    result = []
    for value in data:
        if value > 0:
            result.append(value * 2)
        else:
            result.append(0)
    return result

def calculate_average(numbers: List[Union[int, float]]) -> float:
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        The average value
        
    Raises:
        ValueError: If the list is empty
        TypeError: If the list contains non-numeric values
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    try:
        return sum(numbers) / len(numbers)
    except TypeError as e:
        raise TypeError("All values must be numeric") from e

class DataProcessor:
    """A class for processing numerical data."""
    
    def __init__(self):
        self.data: List[Union[int, float]] = []
    
    def add_data(self, value: Union[int, float]) -> None:
        """Add a value to the data collection."""
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be numeric")
        self.data.append(value)
    
    def process_all(self) -> List[Union[int, float]]:
        """Process all data in the collection."""
        return process_data(self.data)
