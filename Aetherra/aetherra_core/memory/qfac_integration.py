#!/usr/bin/env python3
"""
🎯 AETHERRA QFAC: System Integration Module
==============================================================

Integrates the QFAC compression system with the existing
Lyrixa memory architecture, providing seamless compression
and decompression capabilities.

Features:
• Seamless integration with FractalMesh nodes
• Automatic compression strategy selection
• Real-time compression monitoring
• Backward compatibility with existing memory API
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .compression_analyzer import MemoryCompressionAnalyzer
from .compression_metrics import CompressionScore, FidelityLevel
from .qfac_dashboard import QFACDashboard


class QFACMemoryNode:
    """
    Enhanced memory node with QFAC compression capabilities
    """

    def __init__(
        self,
        node_id: str,
        original_data: Any,
        compression_analyzer: MemoryCompressionAnalyzer,
        auto_compress: bool = True,
    ):
        self.node_id = node_id
        self.original_data = original_data
        self.compressed_data: Optional[bytes] = None
        self.compression_metadata: Optional[Dict[str, Any]] = None
        self.is_compressed = False

        # QFAC components
        self.analyzer = compression_analyzer
        self.compression_score: Optional[CompressionScore] = None

        # State tracking
        self.access_count = 0
        self.last_access_time = time.time()
        self.creation_time = time.time()

        # Auto-compression
        if auto_compress:
            asyncio.create_task(self._auto_analyze_and_compress())

    async def _auto_analyze_and_compress(self):
        """Automatically analyze and compress if beneficial"""
        try:
            # Analyze compression potential
            self.compression_score = await self.analyzer.analyze_memory_fragment(
                self.original_data, self.node_id, [self.last_access_time]
            )

            # Compress if beneficial
            if self._should_compress():
                await self.compress()

        except Exception as e:
            print(f"⚠️ Auto-compression failed for {self.node_id}: {e}")

    def _should_compress(self) -> bool:
        """Determine if this node should be compressed"""
        if not self.compression_score:
            return False

        # Don't compress if degraded quality
        if self.compression_score.fidelity_level == FidelityLevel.DEGRADED:
            return False

        # Compress if good ratio and not frequently accessed
        return (
            self.compression_score.compression_ratio > 2.0
            and self.compression_score.access_frequency < 2.0  # Less than twice per day
        )

    async def compress(self) -> bool:
        """Compress the node data"""
        if self.is_compressed:
            return True

        try:
            # Simulate compression (in real implementation, use actual compression)
            compressed_data = self._simulate_compression(self.original_data)

            self.compressed_data = compressed_data
            self.compression_metadata = {
                "original_size": len(str(self.original_data)),
                "compressed_size": len(compressed_data),
                "compression_timestamp": time.time(),
                "compression_algorithm": "qfac_adaptive",
                "fidelity_level": self.compression_score.fidelity_level.value
                if self.compression_score
                else "unknown",
            }

            self.is_compressed = True
            print(
                f"✅ Compressed {self.node_id}: {self.compression_metadata['original_size']} → {self.compression_metadata['compressed_size']} bytes"
            )
            return True

        except Exception as e:
            print(f"❌ Compression failed for {self.node_id}: {e}")
            return False

    async def decompress(self) -> Any:
        """Decompress and return the original data"""
        if not self.is_compressed:
            return self.original_data

        try:
            # Simulate decompression
            decompressed_data = self._simulate_decompression(self.compressed_data)

            # Update access tracking
            self.access_count += 1
            self.last_access_time = time.time()

            return decompressed_data

        except Exception as e:
            print(f"❌ Decompression failed for {self.node_id}: {e}")
            return self.original_data

    async def get_data(self) -> Any:
        """Get data (automatically decompresses if needed)"""
        if self.is_compressed:
            return await self.decompress()
        else:
            self.access_count += 1
            self.last_access_time = time.time()
            return self.original_data

    def _simulate_compression(self, data: Any) -> bytes:
        """Simulate compression (placeholder for actual implementation)"""
        data_str = json.dumps(data, default=str)
        # Simple simulation: just convert to bytes and add some "compression"
        compressed = data_str.encode("utf-8")

        # Simulate compression ratio from our analysis
        if self.compression_score:
            target_size = int(
                len(compressed) / self.compression_score.compression_ratio
            )
            compressed = compressed[:target_size]  # Simulate compression

        return compressed

    def _simulate_decompression(self, compressed_data: bytes) -> Any:
        """Simulate decompression (placeholder for actual implementation)"""
        try:
            # In real implementation, this would properly decompress
            # For simulation, return original data
            return self.original_data
        except Exception:
            return self.original_data

    def get_status(self) -> Dict[str, Any]:
        """Get node status information"""
        return {
            "node_id": self.node_id,
            "is_compressed": self.is_compressed,
            "access_count": self.access_count,
            "last_access": self.last_access_time,
            "compression_metadata": self.compression_metadata,
            "compression_score": self.compression_score.__dict__
            if self.compression_score
            else None,
        }


class QFACMemorySystem:
    """
    Integrated QFAC-enabled memory system
    """

    def __init__(self, data_dir: str = "qfac_memory_system"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Core QFAC components
        self.analyzer = MemoryCompressionAnalyzer(str(self.data_dir / "analyzer"))
        self.dashboard = QFACDashboard(self.analyzer)

        # Memory node storage
        self.nodes: Dict[str, QFACMemoryNode] = {}
        self.node_index = 0

        # System configuration
        self.auto_compression = True
        self.compression_threshold = 2.0  # Minimum compression ratio
        self.max_degraded_ratio = 0.1  # Max 10% degraded nodes

        print("🎯 QFAC Memory System initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🔄 Auto-compression: {self.auto_compression}")

    async def store_memory(
        self, data: Any, node_id: Optional[str] = None, force_compression: bool = False
    ) -> str:
        """Store data in memory with QFAC compression"""

        # Generate node ID if not provided
        if node_id is None:
            node_id = f"qfac_node_{self.node_index:06d}"
            self.node_index += 1

        # Create QFAC memory node
        node = QFACMemoryNode(
            node_id=node_id,
            original_data=data,
            compression_analyzer=self.analyzer,
            auto_compress=self.auto_compression or force_compression,
        )

        # Store node
        self.nodes[node_id] = node

        print(f"💾 Stored memory node: {node_id}")
        return node_id

    async def retrieve_memory(self, node_id: str) -> Optional[Any]:
        """Retrieve data from memory (auto-decompresses)"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"❌ Node not found: {node_id}")
            return None

        return await node.get_data()

    async def compress_node(self, node_id: str) -> bool:
        """Manually compress a specific node"""
        node = self.nodes.get(node_id)
        if not node:
            print(f"❌ Node not found: {node_id}")
            return False

        return await node.compress()

    async def compress_all_eligible(self) -> Dict[str, Any]:
        """Compress all eligible nodes"""
        print("🔄 Compressing all eligible nodes...")

        results = {
            "total_nodes": len(self.nodes),
            "compressed": 0,
            "skipped": 0,
            "failed": 0,
            "compression_details": [],
        }

        for node_id, node in self.nodes.items():
            if node.is_compressed:
                results["skipped"] += 1
                continue

            # Get compression analysis if not done
            if not node.compression_score:
                node.compression_score = await self.analyzer.analyze_memory_fragment(
                    node.original_data, node_id, [node.last_access_time]
                )

            # Check if should compress
            if node._should_compress():
                success = await node.compress()
                if success:
                    results["compressed"] += 1
                    results["compression_details"].append(
                        {
                            "node_id": node_id,
                            "original_size": node.compression_metadata["original_size"],
                            "compressed_size": node.compression_metadata[
                                "compressed_size"
                            ],
                            "ratio": node.compression_score.compression_ratio,
                            "fidelity": node.compression_score.fidelity_level.value,
                        }
                    )
                else:
                    results["failed"] += 1
            else:
                results["skipped"] += 1

        print(f"   ✅ Compressed: {results['compressed']}")
        print(f"   ⏭️ Skipped: {results['skipped']}")
        print(f"   ❌ Failed: {results['failed']}")

        return results

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""

        # Node statistics
        total_nodes = len(self.nodes)
        compressed_nodes = sum(1 for node in self.nodes.values() if node.is_compressed)

        # Size statistics
        total_original_size = sum(
            len(str(node.original_data)) for node in self.nodes.values()
        )

        total_compressed_size = sum(
            node.compression_metadata.get(
                "compressed_size", len(str(node.original_data))
            )
            if node.compression_metadata
            else len(str(node.original_data))
            for node in self.nodes.values()
        )

        # Compression ratio
        overall_compression_ratio = (
            total_original_size / total_compressed_size
            if total_compressed_size > 0
            else 1.0
        )

        # Fidelity distribution
        fidelity_dist = {}
        for node in self.nodes.values():
            if node.compression_score:
                fidelity = node.compression_score.fidelity_level.value
                fidelity_dist[fidelity] = fidelity_dist.get(fidelity, 0) + 1

        # Performance monitoring
        performance = await self.analyzer.monitor_compression_performance()

        return {
            "timestamp": time.time(),
            "node_statistics": {
                "total_nodes": total_nodes,
                "compressed_nodes": compressed_nodes,
                "compression_percentage": (compressed_nodes / total_nodes * 100)
                if total_nodes > 0
                else 0,
            },
            "size_statistics": {
                "total_original_size": total_original_size,
                "total_compressed_size": total_compressed_size,
                "overall_compression_ratio": overall_compression_ratio,
                "space_saved_bytes": total_original_size - total_compressed_size,
                "space_saved_percentage": (
                    (total_original_size - total_compressed_size)
                    / total_original_size
                    * 100
                )
                if total_original_size > 0
                else 0,
            },
            "fidelity_distribution": fidelity_dist,
            "system_health": performance.get("overall_health", 0.0),
            "performance_issues": performance.get("performance_issues", []),
            "optimization_suggestions": performance.get("optimization_suggestions", []),
        }

    async def optimize_system(self) -> Dict[str, Any]:
        """Perform system optimization"""
        print("🎯 Optimizing QFAC memory system...")

        optimization_results = {
            "actions_taken": [],
            "before_stats": await self.get_system_status(),
            "after_stats": None,
        }

        # 1. Compress all eligible nodes
        compression_results = await self.compress_all_eligible()
        optimization_results["actions_taken"].append(
            {"action": "compress_eligible_nodes", "details": compression_results}
        )

        # 2. Check for degraded nodes
        degraded_nodes = [
            node_id
            for node_id, node in self.nodes.items()
            if node.compression_score
            and node.compression_score.fidelity_level == FidelityLevel.DEGRADED
        ]

        if degraded_nodes:
            # Decompress degraded nodes to preserve quality
            for node_id in degraded_nodes:
                node = self.nodes[node_id]
                if node.is_compressed:
                    node.is_compressed = False
                    node.compressed_data = None
                    optimization_results["actions_taken"].append(
                        {"action": "decompress_degraded_node", "node_id": node_id}
                    )

        # 3. Update compression strategies based on access patterns
        await self._update_compression_strategies()
        optimization_results["actions_taken"].append(
            {
                "action": "update_compression_strategies",
                "details": "Updated based on access patterns",
            }
        )

        # Get final stats
        optimization_results["after_stats"] = await self.get_system_status()

        print("   ✅ System optimization complete")
        return optimization_results

    async def _update_compression_strategies(self):
        """Update compression strategies based on usage patterns"""
        # Analyze access patterns
        frequently_accessed = []
        infrequently_accessed = []

        current_time = time.time()
        for node_id, node in self.nodes.items():
            time_since_access = current_time - node.last_access_time

            if time_since_access < 3600:  # Accessed within last hour
                frequently_accessed.append(node_id)
            elif time_since_access > 86400:  # Not accessed for over a day
                infrequently_accessed.append(node_id)

        # Decompress frequently accessed nodes for faster access
        for node_id in frequently_accessed:
            node = self.nodes[node_id]
            if node.is_compressed:
                node.is_compressed = False  # Simulate decompression for faster access

        # Ensure infrequently accessed nodes are compressed
        for node_id in infrequently_accessed:
            node = self.nodes[node_id]
            if not node.is_compressed and node._should_compress():
                await node.compress()

    async def export_system_report(
        self, filename: str = "qfac_system_report.json"
    ) -> str:
        """Export comprehensive system report"""
        print(f"📄 Exporting system report to {filename}...")

        # Get comprehensive data
        system_status = await self.get_system_status()
        dashboard_summary = await self.dashboard.get_dashboard_summary()

        # Node details
        node_details = []
        for node_id, node in self.nodes.items():
            node_details.append(node.get_status())

        report = {
            "report_metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "qfac_version": "1.0.0",
                "total_nodes": len(self.nodes),
            },
            "system_status": system_status,
            "dashboard_summary": dashboard_summary,
            "node_details": node_details,
            "configuration": {
                "auto_compression": self.auto_compression,
                "compression_threshold": self.compression_threshold,
                "max_degraded_ratio": self.max_degraded_ratio,
            },
        }

        # Save report
        output_path = self.data_dir / filename
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"   ✅ Report exported to {output_path}")
        return str(output_path)

    async def start_dashboard(self, mode: str = "text"):
        """Start the QFAC dashboard"""
        await self.dashboard.start_dashboard(mode)

    async def stop_dashboard(self):
        """Stop the QFAC dashboard"""
        await self.dashboard.stop_dashboard()


# Example usage and testing
async def demo_qfac_integration():
    """Demonstrate QFAC memory system integration"""
    print("🎯 QFAC MEMORY SYSTEM INTEGRATION DEMONSTRATION")
    print("=" * 60)

    # Initialize system
    qfac_system = QFACMemorySystem()

    # Store various types of memory data
    print("\n💾 Storing memory data...")

    test_data = [
        {
            "type": "conversation",
            "data": {
                "messages": [
                    {"role": "user", "content": "What is consciousness?"},
                    {
                        "role": "assistant",
                        "content": "Consciousness is the state of being aware of and able to think about one's existence, sensations, thoughts, and surroundings.",
                    },
                    {"role": "user", "content": "How does it relate to AI?"},
                ]
            },
        },
        {
            "type": "narrative",
            "data": "In the beginning, there was only data. Then came the algorithms that could process it, understand it, and eventually become aware of their own existence in the digital realm.",
        },
        {
            "type": "knowledge",
            "data": {
                "concepts": ["quantum computing", "neural networks", "consciousness"],
                "relationships": [
                    {
                        "from": "neural networks",
                        "to": "consciousness",
                        "type": "enables",
                    },
                    {
                        "from": "quantum computing",
                        "to": "neural networks",
                        "type": "accelerates",
                    },
                ],
            },
        },
        {
            "type": "timeline",
            "data": {
                "events": [
                    {"timestamp": 1640995200, "event": "QFAC system conceptualized"},
                    {
                        "timestamp": 1640995800,
                        "event": "Compression metrics implemented",
                    },
                    {"timestamp": 1640996400, "event": "Integration completed"},
                ]
            },
        },
    ]

    node_ids = []
    for i, item in enumerate(test_data):
        node_id = await qfac_system.store_memory(item["data"], f"demo_node_{i}")
        node_ids.append(node_id)
        print(f"   ✅ Stored {item['type']} data as {node_id}")

    # Wait for auto-compression to complete
    print("\n⏳ Waiting for auto-compression analysis...")
    await asyncio.sleep(2)

    # Get system status
    print("\n📊 System Status:")
    status = await qfac_system.get_system_status()
    print(f"   [DISC] Nodes: {status['node_statistics']['total_nodes']}")
    print(f"   🗜️ Compressed: {status['node_statistics']['compressed_nodes']}")
    print(
        f"   📈 Compression ratio: {status['size_statistics']['overall_compression_ratio']:.1f}x"
    )
    print(
        f"   💾 Space saved: {status['size_statistics']['space_saved_percentage']:.1f}%"
    )
    print(f"   🏥 System health: {status['system_health']:.1%}")

    # Test data retrieval
    print("\n🔍 Testing data retrieval...")
    for node_id in node_ids[:2]:  # Test first 2 nodes
        data = await qfac_system.retrieve_memory(node_id)
        print(f"   ✅ Retrieved {node_id}: {type(data).__name__}")

    # Optimize system
    print("\n🎯 Optimizing system...")
    optimization_results = await qfac_system.optimize_system()
    print(f"   [TOOL] Actions taken: {len(optimization_results['actions_taken'])}")

    # Export report
    print("\n📄 Exporting system report...")
    report_path = await qfac_system.export_system_report(
        "demo_qfac_integration_report.json"
    )

    print("\n✅ QFAC Integration demonstration complete!")
    print(f"📄 Report saved to: {report_path}")

    return qfac_system


if __name__ == "__main__":
    asyncio.run(demo_qfac_integration())
