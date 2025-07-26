#!/usr/bin/env python3
"""
🎯 AETHERRA QFAC: MemoryCompressionAnalyzer
==============================================================

Advanced memory compression analysis engine that detects optimal
compression schemas per memory type and monitors performance.

Features:
• Auto-detection of memory types (text, embeddings, timelines, narratives)
• Optimal compression schema selection
• Real-time performance monitoring
• Adaptive compression strategy adjustment
"""

import asyncio
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .compression_metrics import CompressionMetrics, CompressionScore, FidelityLevel


class MemoryType:
    """Memory type classification"""
    TEXT = "text"
    EMBEDDINGS = "embeddings"
    TIMELINE = "timeline"
    NARRATIVE = "narrative"
    STRUCTURED = "structured"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    UNKNOWN = "unknown"


@dataclass
class CompressionSchema:
    """Compression strategy configuration"""
    
    memory_type: str
    algorithm: str                    # compression algorithm name
    fidelity_target: FidelityLevel   # target fidelity level
    performance_weight: float        # speed vs quality tradeoff (0-1)
    adaptive_threshold: float        # when to switch strategies
    
    # Algorithm-specific parameters
    parameters: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    """Compression/decompression performance data"""
    
    compression_time: float          # seconds
    decompression_time: float        # seconds
    memory_type: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    fidelity_achieved: FidelityLevel
    access_frequency: float
    timestamp: float


class MemoryCompressionAnalyzer:
    """
    Main compression analysis engine for QFAC memory system
    """
    
    def __init__(self, data_dir: str = "qfac_compression_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize metrics engine
        self.metrics = CompressionMetrics()
        
        # Database for tracking performance
        self.db_path = self.data_dir / "compression_analysis.db"
        self._init_database()
        
        # Memory type classifier
        self.type_classifier = MemoryTypeClassifier()
        
        # Compression schemas by memory type
        self.schemas = self._init_compression_schemas()
        
        # Performance tracking
        self.performance_history = []
        self.schema_performance = {}
        
        # Adaptive thresholds
        self.fidelity_safety_threshold = 0.85
        self.performance_target_ratio = 10.0  # target compression ratio
        
        print("🎯 MemoryCompressionAnalyzer initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🗃️ Database: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database for compression analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Compression scores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compression_scores (
                fragment_id TEXT PRIMARY KEY,
                memory_type TEXT,
                entropy REAL,
                structure_depth INTEGER,
                recursive_density REAL,
                fidelity_level TEXT,
                compression_ratio REAL,
                access_frequency REAL,
                temporal_decay REAL,
                original_size INTEGER,
                compressed_size INTEGER,
                reconstruction_quality REAL,
                semantic_preservation REAL,
                timestamp REAL,
                schema_used TEXT
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT,
                compression_time REAL,
                decompression_time REAL,
                original_size INTEGER,
                compressed_size INTEGER,
                compression_ratio REAL,
                fidelity_achieved TEXT,
                access_frequency REAL,
                timestamp REAL,
                schema_used TEXT
            )
        """)
        
        # Schema effectiveness table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_effectiveness (
                memory_type TEXT,
                schema_name TEXT,
                avg_compression_ratio REAL,
                avg_compression_time REAL,
                avg_fidelity_score REAL,
                success_rate REAL,
                sample_count INTEGER,
                last_updated REAL,
                PRIMARY KEY (memory_type, schema_name)
            )
        """)
        
        conn.commit()
        conn.close()
        print("   📋 Compression analysis database initialized")
    
    def _init_compression_schemas(self) -> Dict[str, CompressionSchema]:
        """Initialize compression schemas for different memory types"""
        schemas = {
            MemoryType.TEXT: CompressionSchema(
                memory_type=MemoryType.TEXT,
                algorithm="adaptive_lz",
                fidelity_target=FidelityLevel.LOSSY_SAFE,
                performance_weight=0.7,
                adaptive_threshold=0.85,
                parameters={
                    "window_size": 1024,
                    "min_match_length": 3,
                    "max_compression_ratio": 15.0
                }
            ),
            MemoryType.EMBEDDINGS: CompressionSchema(
                memory_type=MemoryType.EMBEDDINGS,
                algorithm="vector_quantization",
                fidelity_target=FidelityLevel.LOSSY_SAFE,
                performance_weight=0.8,
                adaptive_threshold=0.90,
                parameters={
                    "codebook_size": 256,
                    "quantization_bits": 8,
                    "pca_components": 128
                }
            ),
            MemoryType.TIMELINE: CompressionSchema(
                memory_type=MemoryType.TIMELINE,
                algorithm="temporal_delta",
                fidelity_target=FidelityLevel.LOSSLESS,
                performance_weight=0.6,
                adaptive_threshold=0.95,
                parameters={
                    "delta_encoding": True,
                    "timestamp_precision": 1000,  # milliseconds
                    "event_clustering": True
                }
            ),
            MemoryType.NARRATIVE: CompressionSchema(
                memory_type=MemoryType.NARRATIVE,
                algorithm="semantic_hierarchy",
                fidelity_target=FidelityLevel.LOSSY_SAFE,
                performance_weight=0.5,
                adaptive_threshold=0.88,
                parameters={
                    "max_hierarchy_depth": 5,
                    "semantic_threshold": 0.7,
                    "narrative_chunking": True
                }
            ),
            MemoryType.STRUCTURED: CompressionSchema(
                memory_type=MemoryType.STRUCTURED,
                algorithm="schema_aware",
                fidelity_target=FidelityLevel.LOSSLESS,
                performance_weight=0.8,
                adaptive_threshold=0.92,
                parameters={
                    "schema_detection": True,
                    "field_ordering": True,
                    "null_compression": True
                }
            ),
            MemoryType.CONVERSATION: CompressionSchema(
                memory_type=MemoryType.CONVERSATION,
                algorithm="dialogue_aware",
                fidelity_target=FidelityLevel.LOSSY_SAFE,
                performance_weight=0.6,
                adaptive_threshold=0.86,
                parameters={
                    "speaker_encoding": True,
                    "turn_boundary_detection": True,
                    "emotion_preservation": True
                }
            ),
        }
        
        return schemas
    
    async def analyze_memory_fragment(
        self, 
        memory_data: Any, 
        fragment_id: str,
        access_history: Optional[List[float]] = None,
        force_analysis: bool = False
    ) -> CompressionScore:
        """
        Comprehensive analysis of a memory fragment
        """
        print(f"🔍 Analyzing memory fragment: {fragment_id}")
        
        # Check if analysis already exists and is recent
        if not force_analysis:
            existing_score = await self._get_cached_analysis(fragment_id)
            if existing_score:
                print(f"   ✅ Using cached analysis (age: {time.time() - existing_score.compression_timestamp:.1f}s)")
                return existing_score
        
        # Classify memory type
        memory_type = self.type_classifier.classify(memory_data)
        print(f"   🏷️ Memory type: {memory_type}")
        
        # Calculate compression metrics
        score = self.metrics.calculate_comprehensive_score(
            memory_data, fragment_id, access_history
        )
        
        # Select optimal compression schema
        optimal_schema = await self._select_optimal_schema(memory_type, score)
        print(f"   🎯 Optimal schema: {optimal_schema.algorithm}")
        
        # Store analysis results
        await self._store_analysis_results(score, memory_type, optimal_schema.algorithm)
        
        # Update performance tracking
        await self._update_performance_tracking(score, memory_type, optimal_schema)
        
        return score
    
    async def get_compression_recommendations(
        self, 
        memory_fragments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get compression recommendations for multiple memory fragments
        """
        print(f"📊 Generating compression recommendations for {len(memory_fragments)} fragments")
        
        recommendations = {
            "fragments": [],
            "summary": {
                "total_fragments": len(memory_fragments),
                "total_original_size": 0,
                "estimated_compressed_size": 0,
                "estimated_compression_ratio": 0,
                "fidelity_distribution": {},
                "memory_type_distribution": {},
                "recommendations": []
            }
        }
        
        fidelity_counts = {}
        type_counts = {}
        
        for fragment in memory_fragments:
            fragment_id = fragment.get("id", f"fragment_{hash(str(fragment))}")
            memory_data = fragment.get("data")
            access_history = fragment.get("access_history", [])
            
            # Analyze fragment
            score = await self.analyze_memory_fragment(
                memory_data, fragment_id, access_history
            )
            
            # Classify memory type
            memory_type = self.type_classifier.classify(memory_data)
            
            # Add to recommendations
            fragment_rec = {
                "fragment_id": fragment_id,
                "memory_type": memory_type,
                "compression_score": asdict(score),
                "recommended_action": self._get_recommended_action(score),
                "priority": self._calculate_compression_priority(score)
            }
            
            recommendations["fragments"].append(fragment_rec)
            
            # Update summaries
            recommendations["summary"]["total_original_size"] += score.original_size
            recommendations["summary"]["estimated_compressed_size"] += score.compressed_size
            
            # Track distributions
            fidelity_counts[score.fidelity_level.value] = fidelity_counts.get(score.fidelity_level.value, 0) + 1
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
        
        # Calculate overall metrics
        if recommendations["summary"]["total_original_size"] > 0:
            recommendations["summary"]["estimated_compression_ratio"] = (
                recommendations["summary"]["total_original_size"] / 
                recommendations["summary"]["estimated_compressed_size"]
            )
        
        recommendations["summary"]["fidelity_distribution"] = fidelity_counts
        recommendations["summary"]["memory_type_distribution"] = type_counts
        
        # Generate global recommendations
        recommendations["summary"]["recommendations"] = await self._generate_global_recommendations(
            recommendations["fragments"]
        )
        
        return recommendations
    
    async def monitor_compression_performance(self) -> Dict[str, Any]:
        """
        Monitor compression performance across all memory types
        """
        print("📈 Monitoring compression performance")
        
        # Get recent performance data
        performance_data = await self._get_recent_performance_data()
        
        # Calculate performance metrics by memory type
        performance_by_type = {}
        for memory_type in [MemoryType.TEXT, MemoryType.EMBEDDINGS, MemoryType.TIMELINE, 
                           MemoryType.NARRATIVE, MemoryType.STRUCTURED, MemoryType.CONVERSATION]:
            type_data = [p for p in performance_data if p["memory_type"] == memory_type]
            if type_data:
                performance_by_type[memory_type] = {
                    "avg_compression_ratio": sum(p["compression_ratio"] for p in type_data) / len(type_data),
                    "avg_compression_time": sum(p["compression_time"] for p in type_data) / len(type_data),
                    "sample_count": len(type_data),
                    "fidelity_distribution": self._calculate_fidelity_distribution(type_data)
                }
        
        # Identify performance issues
        performance_issues = await self._identify_performance_issues(performance_by_type)
        
        # Generate optimization suggestions
        optimization_suggestions = await self._generate_optimization_suggestions(
            performance_by_type, performance_issues
        )
        
        return {
            "timestamp": time.time(),
            "performance_by_type": performance_by_type,
            "performance_issues": performance_issues,
            "optimization_suggestions": optimization_suggestions,
            "overall_health": self._calculate_overall_health(performance_by_type)
        }
    
    async def _get_cached_analysis(self, fragment_id: str) -> Optional[CompressionScore]:
        """Get cached compression analysis if recent enough"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM compression_scores 
            WHERE fragment_id = ? AND timestamp > ?
        """, (fragment_id, time.time() - 3600))  # 1 hour cache
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return CompressionScore(
                entropy=row[2],
                structure_depth=row[3],
                recursive_density=row[4],
                fidelity_level=FidelityLevel(row[5]),
                compression_ratio=row[6],
                access_frequency=row[7],
                temporal_decay=row[8],
                fragment_id=row[0],
                original_size=row[9],
                compressed_size=row[10],
                last_access=time.time(),
                compression_timestamp=row[13],
                pattern_confidence=0.8,  # Default values for missing fields
                reconstruction_quality=row[11],
                semantic_preservation=row[12]
            )
        
        return None
    
    async def _select_optimal_schema(
        self, 
        memory_type: str, 
        score: CompressionScore
    ) -> CompressionSchema:
        """Select optimal compression schema based on analysis"""
        
        # Get base schema for memory type
        base_schema = self.schemas.get(memory_type, self.schemas[MemoryType.TEXT])
        
        # Adapt schema based on compression score
        adapted_schema = CompressionSchema(
            memory_type=memory_type,
            algorithm=base_schema.algorithm,
            fidelity_target=base_schema.fidelity_target,
            performance_weight=base_schema.performance_weight,
            adaptive_threshold=base_schema.adaptive_threshold,
            parameters=base_schema.parameters.copy()
        )
        
        # Adapt based on entropy and patterns
        if score.entropy > 0.8:  # High entropy - harder to compress
            adapted_schema.fidelity_target = FidelityLevel.LOSSY_RISKY
            adapted_schema.performance_weight = 0.9  # Favor speed
        elif score.recursive_density > 0.7:  # High pattern density
            adapted_schema.fidelity_target = FidelityLevel.LOSSLESS
            adapted_schema.performance_weight = 0.3  # Favor quality
        
        return adapted_schema
    
    async def _store_analysis_results(
        self, 
        score: CompressionScore, 
        memory_type: str, 
        schema_used: str
    ):
        """Store analysis results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO compression_scores (
                fragment_id, memory_type, entropy, structure_depth, recursive_density,
                fidelity_level, compression_ratio, access_frequency, temporal_decay,
                original_size, compressed_size, reconstruction_quality, semantic_preservation,
                timestamp, schema_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            score.fragment_id, memory_type, score.entropy, score.structure_depth,
            score.recursive_density, score.fidelity_level.value, score.compression_ratio,
            score.access_frequency, score.temporal_decay, score.original_size,
            score.compressed_size, score.reconstruction_quality, score.semantic_preservation,
            score.compression_timestamp, schema_used
        ))
        
        conn.commit()
        conn.close()
    
    async def _update_performance_tracking(
        self, 
        score: CompressionScore, 
        memory_type: str, 
        schema: CompressionSchema
    ):
        """Update performance tracking data"""
        
        # Create performance metric (simulated timing for now)
        performance = PerformanceMetrics(
            compression_time=0.001 * score.original_size,  # Simulated
            decompression_time=0.0005 * score.compressed_size,  # Simulated
            memory_type=memory_type,
            original_size=score.original_size,
            compressed_size=score.compressed_size,
            compression_ratio=score.compression_ratio,
            fidelity_achieved=score.fidelity_level,
            access_frequency=score.access_frequency,
            timestamp=time.time()
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics (
                memory_type, compression_time, decompression_time, original_size,
                compressed_size, compression_ratio, fidelity_achieved, access_frequency,
                timestamp, schema_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            performance.memory_type, performance.compression_time, performance.decompression_time,
            performance.original_size, performance.compressed_size, performance.compression_ratio,
            performance.fidelity_achieved.value, performance.access_frequency,
            performance.timestamp, schema.algorithm
        ))
        
        conn.commit()
        conn.close()
    
    def _get_recommended_action(self, score: CompressionScore) -> str:
        """Get recommended action based on compression score"""
        if score.fidelity_level == FidelityLevel.DEGRADED:
            return "preserve_uncompressed"
        elif score.compression_ratio > 10.0 and score.fidelity_level in [FidelityLevel.LOSSLESS, FidelityLevel.LOSSY_SAFE]:
            return "compress_aggressive"
        elif score.access_frequency > 1.0:  # Daily access
            return "compress_conservative"
        else:
            return "compress_standard"
    
    def _calculate_compression_priority(self, score: CompressionScore) -> float:
        """Calculate compression priority (0-1, higher = more urgent)"""
        size_factor = min(score.original_size / 10000, 1.0)  # Larger files = higher priority
        ratio_factor = min(score.compression_ratio / 20.0, 1.0)  # Better compression = higher priority
        access_factor = 1.0 - min(score.access_frequency / 5.0, 1.0)  # Less accessed = higher priority
        
        return (size_factor * 0.4 + ratio_factor * 0.4 + access_factor * 0.2)
    
    async def _generate_global_recommendations(self, fragments: List[Dict[str, Any]]) -> List[str]:
        """Generate global compression recommendations"""
        recommendations = []
        
        # Analyze compression potential
        total_original = sum(f["compression_score"]["original_size"] for f in fragments)
        total_compressed = sum(f["compression_score"]["compressed_size"] for f in fragments)
        
        if total_original > 0:
            overall_ratio = total_original / total_compressed
            
            if overall_ratio > 5.0:
                recommendations.append("Excellent compression potential detected - proceed with aggressive compression")
            elif overall_ratio > 3.0:
                recommendations.append("Good compression potential - standard compression recommended")
            else:
                recommendations.append("Limited compression potential - use conservative settings")
        
        # Check fidelity concerns
        degraded_count = sum(1 for f in fragments if f["compression_score"]["fidelity_level"] == "degraded")
        if degraded_count > len(fragments) * 0.1:
            recommendations.append(f"Warning: {degraded_count} fragments may lose significant quality during compression")
        
        return recommendations
    
    async def _get_recent_performance_data(self) -> List[Dict[str, Any]]:
        """Get recent performance data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get data from last 24 hours
        since_timestamp = time.time() - 86400
        
        cursor.execute("""
            SELECT * FROM performance_metrics 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC
        """, (since_timestamp,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dictionaries
        performance_data = []
        for row in rows:
            performance_data.append({
                "memory_type": row[1],
                "compression_time": row[2],
                "decompression_time": row[3],
                "original_size": row[4],
                "compressed_size": row[5],
                "compression_ratio": row[6],
                "fidelity_achieved": row[7],
                "access_frequency": row[8],
                "timestamp": row[9]
            })
        
        return performance_data
    
    def _calculate_fidelity_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of fidelity levels"""
        distribution = {}
        for item in data:
            fidelity = item["fidelity_achieved"]
            distribution[fidelity] = distribution.get(fidelity, 0) + 1
        return distribution
    
    async def _identify_performance_issues(self, performance_by_type: Dict[str, Any]) -> List[str]:
        """Identify performance issues"""
        issues = []
        
        for memory_type, metrics in performance_by_type.items():
            if metrics["avg_compression_ratio"] < 2.0:
                issues.append(f"Poor compression ratio for {memory_type}: {metrics['avg_compression_ratio']:.1f}x")
            
            if metrics["avg_compression_time"] > 1.0:
                issues.append(f"Slow compression for {memory_type}: {metrics['avg_compression_time']:.3f}s")
        
        return issues
    
    async def _generate_optimization_suggestions(
        self, 
        performance_by_type: Dict[str, Any], 
        issues: List[str]
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if issues:
            suggestions.append("Consider adjusting compression schemas for underperforming memory types")
            suggestions.append("Monitor access patterns to optimize compression strategies")
        else:
            suggestions.append("Compression performance is optimal - maintain current settings")
        
        return suggestions
    
    def _calculate_overall_health(self, performance_by_type: Dict[str, Any]) -> float:
        """Calculate overall compression system health (0-1)"""
        if not performance_by_type:
            return 0.0
        
        health_scores = []
        for metrics in performance_by_type.values():
            # Score based on compression ratio and time
            ratio_score = min(metrics["avg_compression_ratio"] / 5.0, 1.0)
            time_score = max(0, 1.0 - metrics["avg_compression_time"])
            health_scores.append((ratio_score + time_score) / 2.0)
        
        return sum(health_scores) / len(health_scores)


class MemoryTypeClassifier:
    """Classifies memory data into types for optimal compression"""
    
    def classify(self, memory_data: Any) -> str:
        """Classify memory data type"""
        
        if isinstance(memory_data, str):
            return self._classify_text(memory_data)
        elif isinstance(memory_data, dict):
            return self._classify_dict(memory_data)
        elif isinstance(memory_data, list):
            return self._classify_list(memory_data)
        else:
            return MemoryType.UNKNOWN
    
    def _classify_text(self, text: str) -> str:
        """Classify text data"""
        text_lower = text.lower()
        
        # Check for conversation patterns
        if any(pattern in text_lower for pattern in ["user:", "assistant:", "human:", "ai:"]):
            return MemoryType.CONVERSATION
        
        # Check for narrative patterns
        if any(pattern in text_lower for pattern in ["once upon", "story", "narrative", "chapter"]):
            return MemoryType.NARRATIVE
        
        # Default to text
        return MemoryType.TEXT
    
    def _classify_dict(self, data: Dict[str, Any]) -> str:
        """Classify dictionary data"""
        keys = set(data.keys())
        
        # Check for conversation structure
        if keys & {"messages", "conversation", "dialogue", "turns"}:
            return MemoryType.CONVERSATION
        
        # Check for timeline structure
        if keys & {"timestamp", "events", "timeline", "chronology"}:
            return MemoryType.TIMELINE
        
        # Check for embeddings
        if keys & {"embedding", "vector", "embeddings"}:
            return MemoryType.EMBEDDINGS
        
        # Check for narrative structure
        if keys & {"story", "narrative", "plot", "characters"}:
            return MemoryType.NARRATIVE
        
        # Default to structured
        return MemoryType.STRUCTURED
    
    def _classify_list(self, data: List[Any]) -> str:
        """Classify list data"""
        if not data:
            return MemoryType.UNKNOWN
        
        # Check first few elements
        sample = data[:3]
        
        # Check for numeric vectors (embeddings)
        if all(isinstance(item, (int, float)) for item in sample):
            return MemoryType.EMBEDDINGS
        
        # Check for timeline events
        if all(isinstance(item, dict) and "timestamp" in item for item in sample):
            return MemoryType.TIMELINE
        
        # Default to structured
        return MemoryType.STRUCTURED


# Example usage and testing
async def demo_compression_analyzer():
    """Demonstrate compression analyzer capabilities"""
    print("🎯 MEMORY COMPRESSION ANALYZER DEMONSTRATION")
    print("=" * 60)
    
    analyzer = MemoryCompressionAnalyzer()
    
    # Test memory fragments
    test_fragments = [
        {
            "id": "conversation_001",
            "data": {
                "type": "conversation",
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "I'm doing well, thank you!"},
                    {"role": "user", "content": "Can you help me with a question?"}
                ]
            },
            "access_history": [time.time() - 3600, time.time()]
        },
        {
            "id": "narrative_001", 
            "data": "Once upon a time, in a digital realm far away, there lived an AI named Lyrixa who dreamed of understanding the nature of consciousness and memory.",
            "access_history": [time.time() - 86400]
        },
        {
            "id": "structured_001",
            "data": {
                "knowledge_base": {
                    "concepts": ["AI", "consciousness", "memory", "compression"],
                    "relationships": [
                        {"from": "AI", "to": "consciousness", "type": "explores"},
                        {"from": "memory", "to": "compression", "type": "benefits_from"}
                    ]
                }
            },
            "access_history": []
        }
    ]
    
    # Analyze individual fragments
    print("\n🧪 Individual Fragment Analysis:")
    for fragment in test_fragments:
        score = await analyzer.analyze_memory_fragment(
            fragment["data"],
            fragment["id"],
            fragment["access_history"]
        )
        print(f"   ✅ {fragment['id']}: {score.fidelity_level.value} | {score.compression_ratio:.1f}x compression")
    
    # Get comprehensive recommendations
    print("\n📊 Comprehensive Compression Recommendations:")
    recommendations = await analyzer.get_compression_recommendations(test_fragments)
    
    print(f"   📈 Total original size: {recommendations['summary']['total_original_size']} bytes")
    print(f"   📉 Estimated compressed: {recommendations['summary']['estimated_compressed_size']} bytes")
    print(f"   🎯 Overall compression ratio: {recommendations['summary']['estimated_compression_ratio']:.1f}x")
    
    print("\n   🎭 Memory type distribution:")
    for mem_type, count in recommendations['summary']['memory_type_distribution'].items():
        print(f"      • {mem_type}: {count}")
    
    print("\n   🎪 Fidelity distribution:")
    for fidelity, count in recommendations['summary']['fidelity_distribution'].items():
        print(f"      • {fidelity}: {count}")
    
    # Monitor performance
    print("\n📈 Performance Monitoring:")
    performance = await analyzer.monitor_compression_performance()
    print(f"   🏥 Overall health: {performance['overall_health']:.1%}")
    print(f"   ⚠️ Issues detected: {len(performance['performance_issues'])}")
    print(f"   💡 Optimization suggestions: {len(performance['optimization_suggestions'])}")


if __name__ == "__main__":
    asyncio.run(demo_compression_analyzer())
