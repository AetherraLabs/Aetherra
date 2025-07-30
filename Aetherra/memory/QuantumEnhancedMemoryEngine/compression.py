"""
Compression Core
Handles entropy analysis and fidelity scoring for quantum memory.
"""
import math

def entropy_score(text):
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(text)]
    return -sum([p * math.log(p) / math.log(2) for p in prob])

def fidelity_score(original, compressed):
    return 1.0 if original == compressed else 1.0 - (abs(len(original) - len(compressed)) / len(original))

def compress_data(text):
    return text[::-1]

def decompress_data(text):
    return text[::-1]
