#!/usr/bin/env python3
"""
🧠 NeuroCode Memory Performance Optimizer
=========================================

Advanced memory management and optimization for NeuroCode operations.
Optimizes memory usage, reduces garbage collection overhead, and provides
intelligent caching for NeuroCode syntax parsing, AI operations, and data processing.

Features:
- Smart memory pooling for frequent operations
- Efficient string interning for NeuroCode keywords
- Optimized data structures for parsing and AST operations
- Memory-mapped file operations for large datasets
- Garbage collection optimization and monitoring
"""

import gc
import json
import mmap
import os
import sys
import time
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Union
import tracemalloc
import psutil


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""
    total_memory_mb: float
    heap_size_mb: float
    gc_collections: tuple
    object_counts: Dict[str, int]
    timestamp: float


class StringInterningPool:
    """Efficient string interning for NeuroCode keywords and common patterns"""
    
    def __init__(self):
        # Common NeuroCode keywords
        self.neurocode_keywords = {
            'goal', 'remember', 'recall', 'think', 'agent', 'when', 'if', 'else', 
            'end', 'function', 'define', 'run', 'simulate', 'learn', 'memory',
            'pattern', 'analyze', 'optimize', 'debug', 'load', 'apply', 'fix',
            'priority', 'high', 'medium', 'low', 'confidence', 'as', 'from',
            'for', 'while', 'in', 'and', 'or', 'not', 'true', 'false'
        }
        
        # Intern common strings
        self.interned_strings = {keyword: sys.intern(keyword) for keyword in self.neurocode_keywords}
        self.intern_cache = {}
        self.usage_count = defaultdict(int)
    
    def intern_string(self, text: str) -> str:
        """Intern string with usage tracking"""
        if text in self.interned_strings:
            self.usage_count[text] += 1
            return self.interned_strings[text]
        
        # Intern frequently used strings
        self.usage_count[text] += 1
        if self.usage_count[text] >= 5:  # Intern after 5 uses
            interned = sys.intern(text)
            self.interned_strings[text] = interned
            return interned
        
        return text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interning statistics"""
        return {
            "total_interned": len(self.interned_strings),
            "keywords_interned": len(self.neurocode_keywords),
            "most_used": sorted(self.usage_count.items(), key=lambda x: x[1], reverse=True)[:10]
        }


class ObjectPool:
    """Memory pool for frequently created objects"""
    
    def __init__(self, object_type: type, initial_size: int = 50):
        self.object_type = object_type
        self.pool = deque()
        self.in_use = set()
        self.created_count = 0
        self.reused_count = 0
        
        # Pre-populate pool
        for _ in range(initial_size):
            self.pool.append(self._create_object())
    
    def acquire(self, *args, **kwargs) -> Any:
        """Acquire object from pool"""
        if self.pool:
            obj = self.pool.popleft()
            self.in_use.add(id(obj))
            self.reused_count += 1
            
            # Reset object if it has a reset method
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            
            return obj
        else:
            # Create new object if pool is empty
            obj = self._create_object(*args, **kwargs)
            self.in_use.add(id(obj))
            self.created_count += 1
            return obj
    
    def release(self, obj: Any) -> None:
        """Release object back to pool"""
        obj_id = id(obj)
        if obj_id in self.in_use:
            self.in_use.remove(obj_id)
            
            # Clean object if it has a clean method
            if hasattr(obj, 'clean'):
                obj.clean()
            
            self.pool.append(obj)
    
    def _create_object(self, *args, **kwargs) -> Any:
        """Create new object instance"""
        return self.object_type(*args, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "pool_size": len(self.pool),
            "in_use": len(self.in_use),
            "created": self.created_count,
            "reused": self.reused_count,
            "reuse_ratio": self.reused_count / max(1, self.created_count + self.reused_count)
        }


class MemoryMappedFileHandler:
    """Efficient handling of large files using memory mapping"""
    
    def __init__(self):
        self.mapped_files = {}
        self.file_cache = {}
    
    def map_file(self, filepath: str, mode: str = 'r') -> mmap.mmap:
        """Memory map a file for efficient access"""
        if filepath in self.mapped_files:
            return self.mapped_files[filepath]
        
        try:
            with open(filepath, 'rb' if 'b' in mode else 'r') as f:
                if os.path.getsize(filepath) > 1024 * 1024:  # Files > 1MB
                    mapped = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    self.mapped_files[filepath] = mapped
                    return mapped
                else:
                    # Small files - read normally
                    content = f.read()
                    self.file_cache[filepath] = content
                    return content
        except Exception as e:
            print(f"⚠️ Failed to map file {filepath}: {e}")
            return None
    
    def close_mapped_file(self, filepath: str) -> None:
        """Close memory mapped file"""
        if filepath in self.mapped_files:
            self.mapped_files[filepath].close()
            del self.mapped_files[filepath]
    
    def close_all(self) -> None:
        """Close all mapped files"""
        for mapped in self.mapped_files.values():
            mapped.close()
        self.mapped_files.clear()
        self.file_cache.clear()


class GarbageCollectionOptimizer:
    """Optimize garbage collection for NeuroCode operations"""
    
    def __init__(self):
        # Get current GC thresholds
        self.original_thresholds = gc.get_threshold()
        self.gc_stats = []
        self.last_collection = time.time()
        
        # Optimize for NeuroCode workloads
        self._optimize_gc_settings()
    
    def _optimize_gc_settings(self) -> None:
        """Optimize GC settings for typical NeuroCode usage patterns"""
        # Increase thresholds for generation 0 (temporary objects)
        # This reduces frequent collections of short-lived parsing objects
        threshold0, threshold1, threshold2 = self.original_thresholds
        
        # Adjust thresholds based on workload
        new_threshold0 = min(threshold0 * 2, 2000)  # Increase gen0 threshold
        new_threshold1 = threshold1
        new_threshold2 = threshold2
        
        gc.set_threshold(new_threshold0, new_threshold1, new_threshold2)
    
    def force_collection(self) -> Dict[str, Any]:
        """Force garbage collection and return statistics"""
        start_time = time.time()
        
        # Get pre-collection stats
        pre_stats = gc.get_stats()
        pre_count = len(gc.get_objects())
        
        # Force collection
        collected = gc.collect()
        
        # Get post-collection stats
        post_count = len(gc.get_objects())
        collection_time = time.time() - start_time
        
        stats = {
            "objects_collected": collected,
            "objects_before": pre_count,
            "objects_after": post_count,
            "collection_time_ms": collection_time * 1000,
            "memory_freed": pre_count - post_count
        }
        
        self.gc_stats.append(stats)
        self.last_collection = time.time()
        
        return stats
    
    def should_collect(self) -> bool:
        """Determine if GC should be triggered"""
        # Collect if it's been more than 30 seconds since last collection
        # and there are many objects
        time_since_last = time.time() - self.last_collection
        object_count = len(gc.get_objects())
        
        return time_since_last > 30 and object_count > 10000
    
    def restore_settings(self) -> None:
        """Restore original GC settings"""
        gc.set_threshold(*self.original_thresholds)


class MemoryProfiler:
    """Advanced memory profiling for NeuroCode operations"""
    
    def __init__(self):
        self.snapshots = deque(maxlen=100)
        self.profiling_enabled = False
        self.baseline_snapshot = None
    
    def start_profiling(self) -> None:
        """Start memory profiling"""
        if not self.profiling_enabled:
            tracemalloc.start()
            self.profiling_enabled = True
            self.baseline_snapshot = self.take_snapshot()
    
    def stop_profiling(self) -> None:
        """Stop memory profiling"""
        if self.profiling_enabled:
            tracemalloc.stop()
            self.profiling_enabled = False
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        # System memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        total_memory_mb = memory_info.rss / 1024 / 1024
        
        # Python heap info
        if self.profiling_enabled:
            current, peak = tracemalloc.get_traced_memory()
            heap_size_mb = current / 1024 / 1024
        else:
            heap_size_mb = 0
        
        # Garbage collection stats
        gc_collections = gc.get_count()
        
        # Object counts by type
        object_counts = defaultdict(int)
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] += 1
        
        snapshot = MemorySnapshot(
            total_memory_mb=total_memory_mb,
            heap_size_mb=heap_size_mb,
            gc_collections=gc_collections,
            object_counts=dict(object_counts),
            timestamp=time.time()
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_diff(self, start_snapshot: MemorySnapshot = None) -> Dict[str, Any]:
        """Get memory difference between snapshots"""
        end_snapshot = self.take_snapshot()
        start = start_snapshot or self.baseline_snapshot
        
        if not start:
            return {"error": "No baseline snapshot available"}
        
        return {
            "memory_diff_mb": end_snapshot.total_memory_mb - start.total_memory_mb,
            "heap_diff_mb": end_snapshot.heap_size_mb - start.heap_size_mb,
            "gc_collections_diff": tuple(
                end - start for end, start in zip(end_snapshot.gc_collections, start.gc_collections)
            ),
            "duration_seconds": end_snapshot.timestamp - start.timestamp
        }


class NeuroCodeMemoryOptimizer:
    """Main memory optimizer for NeuroCode operations"""
    
    def __init__(self):
        self.string_pool = StringInterningPool()
        self.object_pools = {}
        self.file_handler = MemoryMappedFileHandler()
        self.gc_optimizer = GarbageCollectionOptimizer()
        self.profiler = MemoryProfiler()
        
        # Weak references to track objects
        self.tracked_objects = weakref.WeakSet()
        
        # Memory limits
        self.memory_limit_mb = 512
        self.warning_threshold_mb = 400
    
    def optimize_string(self, text: str) -> str:
        """Optimize string using interning"""
        return self.string_pool.intern_string(text)
    
    def get_object_pool(self, object_type: type, initial_size: int = 50) -> ObjectPool:
        """Get or create object pool for type"""
        type_name = object_type.__name__
        if type_name not in self.object_pools:
            self.object_pools[type_name] = ObjectPool(object_type, initial_size)
        return self.object_pools[type_name]
    
    def load_large_file(self, filepath: str) -> Union[str, mmap.mmap]:
        """Load large file efficiently"""
        return self.file_handler.map_file(filepath)
    
    def check_memory_pressure(self) -> Dict[str, Any]:
        """Check current memory pressure"""
        snapshot = self.profiler.take_snapshot()
        
        pressure_level = "low"
        if snapshot.total_memory_mb > self.memory_limit_mb:
            pressure_level = "critical"
        elif snapshot.total_memory_mb > self.warning_threshold_mb:
            pressure_level = "high"
        
        return {
            "pressure_level": pressure_level,
            "memory_mb": snapshot.total_memory_mb,
            "limit_mb": self.memory_limit_mb,
            "usage_percent": (snapshot.total_memory_mb / self.memory_limit_mb) * 100
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform comprehensive memory optimization"""
        initial_snapshot = self.profiler.take_snapshot()
        optimizations = []
        
        # Force garbage collection
        gc_stats = self.gc_optimizer.force_collection()
        optimizations.append(f"GC: {gc_stats['objects_collected']} objects collected")
        
        # Clear weak references
        self.tracked_objects.clear()
        
        # Clear object pools if memory pressure is high
        pressure = self.check_memory_pressure()
        if pressure["pressure_level"] in ["high", "critical"]:
            for pool in self.object_pools.values():
                pool.pool.clear()
            optimizations.append("Cleared object pools")
        
        # Close unused memory mapped files
        self.file_handler.close_all()
        optimizations.append("Closed memory mapped files")
        
        final_snapshot = self.profiler.take_snapshot()
        memory_freed = initial_snapshot.total_memory_mb - final_snapshot.total_memory_mb
        
        return {
            "memory_freed_mb": memory_freed,
            "optimizations_applied": optimizations,
            "final_memory_mb": final_snapshot.total_memory_mb,
            "gc_stats": gc_stats
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive memory performance report"""
        snapshot = self.profiler.take_snapshot()
        pressure = self.check_memory_pressure()
        
        # Object pool stats
        pool_stats = {}
        for name, pool in self.object_pools.items():
            pool_stats[name] = pool.get_stats()
        
        # String interning stats
        string_stats = self.string_pool.get_stats()
        
        return {
            "memory_status": {
                "total_memory_mb": snapshot.total_memory_mb,
                "heap_size_mb": snapshot.heap_size_mb,
                "pressure_level": pressure["pressure_level"],
                "usage_percent": pressure["usage_percent"]
            },
            "object_pools": pool_stats,
            "string_interning": string_stats,
            "gc_collections": snapshot.gc_collections,
            "top_object_types": sorted(
                snapshot.object_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.file_handler.close_all()
        self.gc_optimizer.restore_settings()
        self.profiler.stop_profiling()


# Global memory optimizer instance
memory_optimizer = NeuroCodeMemoryOptimizer()


# Context manager for memory profiling
class memory_profiled:
    """Context manager for profiling memory usage of operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_snapshot = None
    
    def __enter__(self):
        memory_optimizer.profiler.start_profiling()
        self.start_snapshot = memory_optimizer.profiler.take_snapshot()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        memory_diff = memory_optimizer.profiler.get_memory_diff(self.start_snapshot)
        print(f"🧠 {self.operation_name}: {memory_diff['memory_diff_mb']:.2f}MB memory change")


# Decorators for memory optimization
def memory_optimized(intern_strings: bool = True, use_pools: bool = True):
    """Decorator for memory-optimized operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Auto-optimize strings in arguments
            if intern_strings:
                optimized_args = []
                for arg in args:
                    if isinstance(arg, str):
                        optimized_args.append(memory_optimizer.optimize_string(arg))
                    else:
                        optimized_args.append(arg)
                args = tuple(optimized_args)
            
            # Check memory pressure before operation
            pressure = memory_optimizer.check_memory_pressure()
            if pressure["pressure_level"] == "critical":
                memory_optimizer.optimize_memory()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Utility functions
def optimize_neurocode_memory() -> Dict[str, Any]:
    """Optimize memory for NeuroCode operations"""
    return memory_optimizer.optimize_memory()


def get_memory_status() -> Dict[str, Any]:
    """Get current memory status"""
    return memory_optimizer.get_performance_report()


if __name__ == "__main__":
    # Example usage
    print("🧠 NeuroCode Memory Optimizer")
    print("=" * 50)
    
    # Test string interning
    test_strings = ["goal", "remember", "think", "goal", "remember"]
    for s in test_strings:
        optimized = memory_optimizer.optimize_string(s)
        print(f"String '{s}' -> interned: {id(optimized)}")
    
    # Test memory profiling
    with memory_profiled("test_operation"):
        # Simulate some work
        data = [i ** 2 for i in range(10000)]
        result = sum(data)
    
    # Get performance report
    report = memory_optimizer.get_performance_report()
    print(f"\n📊 Memory Report:")
    print(f"Total memory: {report['memory_status']['total_memory_mb']:.1f}MB")
    print(f"Pressure level: {report['memory_status']['pressure_level']}")
    print(f"String interning: {report['string_interning']['total_interned']} strings")
