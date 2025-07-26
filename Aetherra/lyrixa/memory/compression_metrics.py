#!/usr/bin/env python3
"""
🔬 AETHERRA QFAC: CompressionMetrics Module
==============================================================

Calculates entropy, structure depth, recursive pattern density,
and fidelity scores for memory fragments in the QFAC system.

Core Metrics:
• Entropy: Information density and randomness
• Structure Depth: Hierarchical complexity
• Recursive Pattern Density: Self-similarity measure
• Fidelity Score: {lossless, lossy-safe, lossy-risky}
"""

import hashlib
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

import numpy as np


class FidelityLevel(Enum):
    """Memory compression fidelity levels"""
    LOSSLESS = "lossless"          # 100% reconstruction guarantee
    LOSSY_SAFE = "lossy-safe"      # 95-99% reconstruction, semantic preservation
    LOSSY_RISKY = "lossy-risky"    # 80-95% reconstruction, acceptable loss
    DEGRADED = "degraded"          # <80% reconstruction, significant loss


@dataclass
class CompressionScore:
    """Comprehensive compression metrics for a memory fragment"""
    
    # Core metrics
    entropy: float                    # Shannon entropy (0-1 normalized)
    structure_depth: int              # Hierarchical nesting levels
    recursive_density: float          # Self-similarity coefficient (0-1)
    fidelity_level: FidelityLevel     # Compression safety category
    
    # Performance metrics
    compression_ratio: float          # Original size / compressed size
    access_frequency: float           # How often this memory is accessed
    temporal_decay: float             # Age-based degradation factor
    
    # Metadata
    fragment_id: str                  # Unique identifier
    original_size: int                # Bytes in original form
    compressed_size: int              # Bytes in compressed form
    last_access: float                # Unix timestamp
    compression_timestamp: float      # When compression was calculated
    
    # Quality indicators
    pattern_confidence: float         # How confident we are in detected patterns
    reconstruction_quality: float     # Estimated reconstruction accuracy
    semantic_preservation: float      # Meaning preservation estimate


class CompressionMetrics:
    """
    Advanced compression metrics calculator for QFAC memory system
    """
    
    def __init__(self):
        self.pattern_cache = {}
        self.entropy_cache = {}
        self.structure_cache = {}
        
        # Fidelity thresholds
        self.fidelity_thresholds = {
            FidelityLevel.LOSSLESS: 0.99,
            FidelityLevel.LOSSY_SAFE: 0.95,
            FidelityLevel.LOSSY_RISKY: 0.80,
            FidelityLevel.DEGRADED: 0.0
        }
        
        print("🔬 CompressionMetrics engine initialized")
    
    def calculate_comprehensive_score(
        self, 
        memory_data: Any, 
        fragment_id: str,
        access_history: Optional[List[float]] = None
    ) -> CompressionScore:
        """
        Calculate complete compression metrics for a memory fragment
        """
        start_time = time.time()
        
        # Serialize data for analysis
        serialized = self._serialize_memory_data(memory_data)
        original_size = len(serialized.encode('utf-8'))
        
        # Calculate core metrics
        entropy = self.calculate_entropy(serialized)
        structure_depth = self.calculate_structure_depth(memory_data)
        recursive_density = self.calculate_recursive_density(serialized)
        
        # Estimate compression performance
        compression_ratio = self._estimate_compression_ratio(
            entropy, recursive_density, structure_depth
        )
        compressed_size = max(1, int(original_size / compression_ratio))
        
        # Calculate fidelity and quality metrics
        fidelity_level = self._determine_fidelity_level(
            entropy, recursive_density, structure_depth
        )
        
        pattern_confidence = self._calculate_pattern_confidence(
            recursive_density, structure_depth
        )
        
        reconstruction_quality = self._estimate_reconstruction_quality(
            fidelity_level, pattern_confidence, entropy
        )
        
        semantic_preservation = self._estimate_semantic_preservation(
            memory_data, fidelity_level
        )
        
        # Access frequency analysis
        access_frequency = self._calculate_access_frequency(access_history)
        temporal_decay = self._calculate_temporal_decay(access_history)
        
        score = CompressionScore(
            entropy=entropy,
            structure_depth=structure_depth,
            recursive_density=recursive_density,
            fidelity_level=fidelity_level,
            compression_ratio=compression_ratio,
            access_frequency=access_frequency,
            temporal_decay=temporal_decay,
            fragment_id=fragment_id,
            original_size=original_size,
            compressed_size=compressed_size,
            last_access=time.time(),
            compression_timestamp=time.time(),
            pattern_confidence=pattern_confidence,
            reconstruction_quality=reconstruction_quality,
            semantic_preservation=semantic_preservation
        )
        
        calculation_time = time.time() - start_time
        print(f"   🔬 Calculated compression score for {fragment_id} in {calculation_time:.3f}s")
        print(f"      • Entropy: {entropy:.3f}")
        print(f"      • Recursive Density: {recursive_density:.3f}")
        print(f"      • Fidelity: {fidelity_level.value}")
        print(f"      • Compression Ratio: {compression_ratio:.1f}x")
        
        return score
    
    def calculate_entropy(self, data: str) -> float:
        """
        Calculate Shannon entropy, normalized to 0-1 range
        """
        if not data:
            return 0.0
        
        # Use cache for repeated calculations
        data_hash = hashlib.md5(data.encode()).hexdigest()
        if data_hash in self.entropy_cache:
            return self.entropy_cache[data_hash]
        
        # Calculate character frequency
        counter = Counter(data)
        total_chars = len(data)
        
        # Shannon entropy calculation
        entropy = 0.0
        for count in counter.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalize to 0-1 range (max entropy for uniform distribution)
        max_entropy = math.log2(min(256, len(counter)))  # 8-bit characters
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # Cache result
        self.entropy_cache[data_hash] = normalized_entropy
        return normalized_entropy
    
    def calculate_structure_depth(self, data: Any) -> int:
        """
        Calculate hierarchical structure depth
        """
        def _depth(obj, current_depth=0):
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, (list, tuple)):
                if not obj:
                    return current_depth
                return max(_depth(item, current_depth + 1) for item in obj)
            else:
                return current_depth
        
        try:
            return _depth(data)
        except (RecursionError, TypeError):
            # Handle deeply nested or problematic structures
            return 10  # Reasonable default for complex structures
    
    def calculate_recursive_density(self, data: str) -> float:
        """
        Calculate recursive pattern density (self-similarity measure)
        """
        if len(data) < 4:
            return 0.0
        
        # Use cache for expensive calculations
        data_hash = hashlib.md5(data.encode()).hexdigest()
        if data_hash in self.pattern_cache:
            return self.pattern_cache[data_hash]
        
        # Multi-scale pattern detection
        pattern_scores = []
        
        # Check different substring lengths
        for pattern_length in [2, 3, 4, 5, 8]:
            if pattern_length >= len(data):
                continue
                
            substrings = []
            for i in range(len(data) - pattern_length + 1):
                substrings.append(data[i:i + pattern_length])
            
            # Count repeated patterns
            pattern_counts = Counter(substrings)
            repeated_patterns = sum(count - 1 for count in pattern_counts.values() if count > 1)
            total_possible = len(substrings)
            
            if total_possible > 0:
                density = repeated_patterns / total_possible
                pattern_scores.append(density)
        
        # Weighted average (favor longer patterns)
        if pattern_scores:
            weights = np.linspace(1, 2, len(pattern_scores))
            recursive_density = np.average(pattern_scores, weights=weights)
        else:
            recursive_density = 0.0
        
        # Cache result
        self.pattern_cache[data_hash] = recursive_density
        return min(1.0, recursive_density)  # Cap at 1.0
    
    def _serialize_memory_data(self, data: Any) -> str:
        """
        Convert memory data to serialized string for analysis
        """
        try:
            if isinstance(data, str):
                return data
            elif isinstance(data, (dict, list, tuple)):
                return json.dumps(data, sort_keys=True, default=str)
            else:
                return str(data)
        except (TypeError, ValueError):
            return str(data)
    
    def _estimate_compression_ratio(
        self, 
        entropy: float, 
        recursive_density: float, 
        structure_depth: int
    ) -> float:
        """
        Estimate achievable compression ratio based on metrics
        """
        # Base compression from entropy (higher entropy = harder to compress)
        entropy_factor = 1.0 + (1.0 - entropy) * 2.0  # 1.0 to 3.0
        
        # Recursive patterns allow better compression
        pattern_factor = 1.0 + recursive_density * 3.0  # 1.0 to 4.0
        
        # Structure allows hierarchical compression
        structure_factor = 1.0 + min(structure_depth / 10.0, 1.0) * 2.0  # 1.0 to 3.0
        
        # Combined compression estimate
        estimated_ratio = entropy_factor * pattern_factor * structure_factor
        
        # Realistic bounds (common compression tools achieve 2x-20x)
        return max(1.1, min(20.0, estimated_ratio))
    
    def _determine_fidelity_level(
        self, 
        entropy: float, 
        recursive_density: float, 
        structure_depth: int
    ) -> FidelityLevel:
        """
        Determine safe compression fidelity level
        """
        # Calculate quality score
        quality_score = (
            (1.0 - entropy) * 0.4 +          # Lower entropy = higher quality
            recursive_density * 0.4 +         # More patterns = safer compression
            min(structure_depth / 5.0, 1.0) * 0.2  # Structure helps
        )
        
        # Map to fidelity levels
        if quality_score >= 0.8:
            return FidelityLevel.LOSSLESS
        elif quality_score >= 0.6:
            return FidelityLevel.LOSSY_SAFE
        elif quality_score >= 0.4:
            return FidelityLevel.LOSSY_RISKY
        else:
            return FidelityLevel.DEGRADED
    
    def _calculate_pattern_confidence(
        self, 
        recursive_density: float, 
        structure_depth: int
    ) -> float:
        """
        Calculate confidence in detected patterns
        """
        # High recursive density means clear patterns
        density_confidence = recursive_density
        
        # Structure depth adds confidence
        structure_confidence = min(structure_depth / 5.0, 1.0)
        
        # Combined confidence
        return (density_confidence * 0.7 + structure_confidence * 0.3)
    
    def _estimate_reconstruction_quality(
        self, 
        fidelity_level: FidelityLevel, 
        pattern_confidence: float, 
        entropy: float
    ) -> float:
        """
        Estimate reconstruction quality percentage
        """
        base_quality = {
            FidelityLevel.LOSSLESS: 0.99,
            FidelityLevel.LOSSY_SAFE: 0.97,
            FidelityLevel.LOSSY_RISKY: 0.87,
            FidelityLevel.DEGRADED: 0.70
        }[fidelity_level]
        
        # Adjust based on pattern confidence and entropy
        confidence_bonus = pattern_confidence * 0.05
        entropy_penalty = entropy * 0.05
        
        return max(0.5, min(1.0, base_quality + confidence_bonus - entropy_penalty))
    
    def _estimate_semantic_preservation(
        self, 
        memory_data: Any, 
        fidelity_level: FidelityLevel
    ) -> float:
        """
        Estimate how well semantic meaning will be preserved
        """
        # Base preservation by fidelity level
        base_preservation = {
            FidelityLevel.LOSSLESS: 1.0,
            FidelityLevel.LOSSY_SAFE: 0.95,
            FidelityLevel.LOSSY_RISKY: 0.85,
            FidelityLevel.DEGRADED: 0.70
        }[fidelity_level]
        
        # Adjust based on data type
        if isinstance(memory_data, str):
            # Text generally preserves meaning well
            return base_preservation
        elif isinstance(memory_data, dict):
            # Structured data preserves well
            return min(1.0, base_preservation + 0.05)
        else:
            # Other data types may be more fragile
            return max(0.6, base_preservation - 0.05)
    
    def _calculate_access_frequency(self, access_history: Optional[List[float]]) -> float:
        """
        Calculate memory access frequency (accesses per day)
        """
        if not access_history:
            return 0.0
        
        if len(access_history) < 2:
            return 1.0  # Single access
        
        # Calculate frequency over time period
        time_span = max(access_history) - min(access_history)
        if time_span <= 0:
            return len(access_history)  # All accesses at same time
        
        # Convert to accesses per day
        days = time_span / (24 * 3600)
        return len(access_history) / max(days, 1.0)
    
    def _calculate_temporal_decay(self, access_history: Optional[List[float]]) -> float:
        """
        Calculate temporal decay factor (how much memory has degraded over time)
        """
        if not access_history:
            return 1.0  # No access history = no decay
        
        last_access = max(access_history)
        time_since_access = time.time() - last_access
        
        # Decay over time (days)
        days_since_access = time_since_access / (24 * 3600)
        
        # Exponential decay with half-life of ~30 days
        decay_factor = math.exp(-days_since_access / 30.0)
        return max(0.1, decay_factor)  # Minimum 10% retention


# Example usage and testing
async def demo_compression_metrics():
    """Demonstrate compression metrics calculation"""
    print("🔬 COMPRESSION METRICS DEMONSTRATION")
    print("=" * 60)
    
    metrics = CompressionMetrics()
    
    # Test different types of memory data
    test_cases = [
        {
            "id": "simple_text",
            "data": "Hello world! This is a simple text message.",
            "access_history": [time.time() - 3600, time.time() - 1800, time.time()]
        },
        {
            "id": "structured_data",
            "data": {
                "type": "conversation",
                "content": "This is a conversation memory",
                "participants": ["user", "lyrixa"],
                "metadata": {"confidence": 0.9, "topic": "discussion"}
            },
            "access_history": [time.time() - 86400, time.time()]
        },
        {
            "id": "repetitive_pattern",
            "data": "abc abc abc def def ghi ghi ghi abc abc def",
            "access_history": [time.time() - 7200]
        },
        {
            "id": "complex_nested",
            "data": {
                "level1": {
                    "level2": {
                        "level3": {
                            "data": "deeply nested structure",
                            "values": [1, 2, 3, 1, 2, 3, 1, 2, 3]
                        }
                    }
                }
            },
            "access_history": []
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['id']}")
        score = metrics.calculate_comprehensive_score(
            test_case["data"],
            test_case["id"],
            test_case["access_history"]
        )
        
        print("   📊 Results:")
        print(f"      • Fidelity Level: {score.fidelity_level.value}")
        print(f"      • Compression Ratio: {score.compression_ratio:.1f}x")
        print(f"      • Reconstruction Quality: {score.reconstruction_quality:.1%}")
        print(f"      • Semantic Preservation: {score.semantic_preservation:.1%}")
        print(f"      • Access Frequency: {score.access_frequency:.1f}/day")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_compression_metrics())
