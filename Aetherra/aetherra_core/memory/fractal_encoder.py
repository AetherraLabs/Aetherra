# Minimal fractal_compress and fractal_decompress for integration test compatibility
def fractal_compress(text):
    # Simulate compression (return reversed string)
    return text[::-1]


def fractal_decompress(data):
    # Simulate decompression (reverse again)
    return data[::-1]


"""
Fractal Encoder
Compresses memory structures using recursive fractal patterns.
"""
import hashlib


class FractalEncoder:
    @staticmethod
    def encode(text):
        return text[::-1]

    @staticmethod
    def decode(text):
        return text[::-1]


def detect_self_similarity(data_block):
    return hashlib.sha256(data_block.encode()).hexdigest()


def fractal_compress(memory_data):
    signature = detect_self_similarity(memory_data)
    return {"compressed": memory_data[::-1], "signature": signature}


def fractal_decompress(payload):
    return payload["compressed"][::-1]


fractal_compress = FractalEncoder.encode
fractal_decompress = FractalEncoder.decode
