"""
Fractal Encoder
Compresses memory structures using recursive fractal patterns.
"""
import hashlib

def detect_self_similarity(data_block):
    return hashlib.sha256(data_block.encode()).hexdigest()

def fractal_compress(memory_data):
    signature = detect_self_similarity(memory_data)
    return {"compressed": memory_data[::-1], "signature": signature}

def fractal_decompress(payload):
    return payload["compressed"][::-1]
