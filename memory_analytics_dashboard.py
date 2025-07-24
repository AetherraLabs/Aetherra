#!/usr/bin/env python3
"""
📊 Memory Analytics Dashboard
============================

Real-time visualization and monitoring dashboard for Aetherra's memory system.
Provides insights into memory health, confidence evolution, narrative quality,
and system performance with interactive visualizations.
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Web framework for dashboard
try:
    from flask import Flask, jsonify, render_template, request

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Visualization libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.utils
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Memory system imports
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))

try:
    from Aetherra.lyrixa.memory.fractal_mesh.base import (
        MemoryFragment,
        MemoryFragmentType,
    )
    from Aetherra.lyrixa.memory.fractal_mesh.timelines.reflective_timeline_engine import (
        ReflectiveTimelineEngine,
    )
    from Aetherra.lyrixa.memory.narrator.llm_narrator import LLMEnhancedNarrator

    MEMORY_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Memory system imports not available: {e}")
    MEMORY_IMPORTS_AVAILABLE = False


@dataclass
class MemoryHealthMetrics:
    """Real-time memory system health indicators"""

    total_fragments: int
    avg_confidence: float
    confidence_std: float
    memory_coherence: float
    narrative_quality: float
    causal_chain_count: int
    goal_arc_count: int
    decay_rate: float
    growth_rate: float
    timestamp: datetime


@dataclass
class MemoryMapNode:
    """Node in the real-time memory map visualization"""

    node_id: str
    content_preview: str
    confidence: float
    fragment_type: str
    symbolic_tags: List[str]
    connections: List[str]
    temporal_position: datetime
    cluster_id: Optional[str]
    decay_score: float
    narrative_role: Optional[str]


@dataclass
class StoryFeedback:
    """Feedback data for story quality improvement"""

    story_id: str
    story_type: str
    quality_score: float
    coherence_score: float
    engagement_score: float
    accuracy_score: float
    feedback_text: Optional[str]
    improvement_suggestions: List[str]
    timestamp: datetime


class MemoryAnalyticsDashboard:
    """
    📊 Real-time Memory Analytics Dashboard

    Features:
    - Real-time memory map visualization
    - Confidence/decay evolution tracking
    - Story feedback and quality metrics
    - Performance monitoring
    - Health alerts and recommendations
    """

    def __init__(self, db_path: str = "memory_analytics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

        # Initialize components if available
        self.timeline_engine = None
        self.narrator = None

        if MEMORY_IMPORTS_AVAILABLE:
            try:
                self.timeline_engine = ReflectiveTimelineEngine("analytics_timeline.db")
                self.narrator = LLMEnhancedNarrator()
            except Exception as e:
                self.logger.warning(f"Could not initialize memory components: {e}")

        # Initialize dashboard database
        self._init_analytics_db()

        # Flask app for web interface
        self.app = None
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            self._setup_routes()

    def _init_analytics_db(self):
        """Initialize analytics database schema"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Memory health metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_health_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_fragments INTEGER,
                    avg_confidence REAL,
                    confidence_std REAL,
                    memory_coherence REAL,
                    narrative_quality REAL,
                    causal_chain_count INTEGER,
                    goal_arc_count INTEGER,
                    decay_rate REAL,
                    growth_rate REAL,
                    metrics_json TEXT
                )
            """)

            # Story feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS story_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id TEXT NOT NULL,
                    story_type TEXT NOT NULL,
                    quality_score REAL,
                    coherence_score REAL,
                    engagement_score REAL,
                    accuracy_score REAL,
                    feedback_text TEXT,
                    improvement_suggestions TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            # Memory evolution tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fragment_id TEXT NOT NULL,
                    confidence_score REAL,
                    access_count INTEGER,
                    last_modified TEXT,
                    decay_score REAL,
                    cluster_changes INTEGER,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()
        finally:
            conn.close()

    async def collect_memory_health_metrics(
        self, fragments: List[MemoryFragment]
    ) -> MemoryHealthMetrics:
        """📊 Collect comprehensive memory health metrics"""
        if not fragments:
            return MemoryHealthMetrics(
                total_fragments=0,
                avg_confidence=0.0,
                confidence_std=0.0,
                memory_coherence=0.0,
                narrative_quality=0.0,
                causal_chain_count=0,
                goal_arc_count=0,
                decay_rate=0.0,
                growth_rate=0.0,
                timestamp=datetime.now(),
            )

        # Basic fragment metrics
        confidences = [f.confidence_score for f in fragments]
        avg_confidence = sum(confidences) / len(confidences)
        confidence_std = (
            sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
        ) ** 0.5

        # Advanced metrics from timeline engine
        causal_chain_count = 0
        goal_arc_count = 0
        memory_coherence = 0.0

        if self.timeline_engine:
            try:
                causal_chains = (
                    await self.timeline_engine.detect_advanced_causal_patterns(
                        fragments
                    )
                )
                goal_arcs = await self.timeline_engine.analyze_goal_memory_arcs(
                    fragments
                )
                self_model = await self.timeline_engine.build_self_narrative_model(
                    fragments
                )

                causal_chain_count = len(causal_chains)
                goal_arc_count = len(goal_arcs)
                memory_coherence = self_model.narrative_coherence
            except Exception as e:
                self.logger.warning(f"Advanced metrics collection failed: {e}")

        # Narrative quality assessment
        narrative_quality = 0.0
        if self.narrator and len(fragments) >= 3:
            try:
                daily_narrative = await self.narrator.generate_enhanced_daily_narrative(
                    fragments[:10]
                )
                narrative_quality = daily_narrative.confidence
            except Exception as e:
                self.logger.warning(f"Narrative quality assessment failed: {e}")

        # Decay and growth rate calculation
        decay_rate = self._calculate_decay_rate(fragments)
        growth_rate = self._calculate_growth_rate(fragments)

        metrics = MemoryHealthMetrics(
            total_fragments=len(fragments),
            avg_confidence=avg_confidence,
            confidence_std=confidence_std,
            memory_coherence=memory_coherence,
            narrative_quality=narrative_quality,
            causal_chain_count=causal_chain_count,
            goal_arc_count=goal_arc_count,
            decay_rate=decay_rate,
            growth_rate=growth_rate,
            timestamp=datetime.now(),
        )

        # Store metrics in database
        self._store_health_metrics(metrics)

        return metrics

    def generate_memory_map_data(
        self, fragments: List[MemoryFragment]
    ) -> List[MemoryMapNode]:
        """🗺️ Generate data for real-time memory map visualization"""
        map_nodes = []

        for fragment in fragments:
            # Calculate decay score based on age and access pattern
            age_days = (datetime.now() - fragment.created_at).days
            decay_score = max(0.0, 1.0 - (age_days * 0.01))  # Simple decay model

            # Extract cluster information
            cluster_id = None
            if hasattr(fragment, "cluster_id"):
                cluster_id = fragment.cluster_id

            # Extract content preview safely
            content_preview = ""
            if isinstance(fragment.content, dict):
                content_preview = (
                    fragment.content.get("text", str(fragment.content))[:100] + "..."
                )
            else:
                content_preview = str(fragment.content)[:100] + "..."

            node = MemoryMapNode(
                node_id=fragment.fragment_id,
                content_preview=content_preview,
                confidence=fragment.confidence_score,
                fragment_type=fragment.fragment_type.value,
                symbolic_tags=list(fragment.symbolic_tags),
                connections=fragment.associative_links,
                temporal_position=fragment.created_at,
                cluster_id=cluster_id,
                decay_score=decay_score,
                narrative_role=fragment.narrative_role,
            )
            map_nodes.append(node)

        return map_nodes

    def create_confidence_evolution_chart(
        self, fragments: List[MemoryFragment]
    ) -> Optional[str]:
        """📈 Create confidence/decay evolution visualization"""
        if not PLOTLY_AVAILABLE or not fragments:
            return None

        # Sort fragments by creation time
        sorted_fragments = sorted(fragments, key=lambda f: f.created_at)

        # Extract data for plotting
        timestamps = [f.created_at for f in sorted_fragments]
        confidences = [f.confidence_score for f in sorted_fragments]

        # Calculate decay scores
        decay_scores = []
        for f in sorted_fragments:
            age_days = (datetime.now() - f.created_at).days
            decay_score = max(0.0, 1.0 - (age_days * 0.01))
            decay_scores.append(decay_score)

        # Create subplot with confidence and decay trends
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Memory Confidence Evolution", "Decay Score Analysis"),
            vertical_spacing=0.1,
        )

        # Confidence trend
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=confidences,
                mode="lines+markers",
                name="Confidence Score",
                line=dict(color="blue", width=2),
                marker=dict(size=6),
            ),
            row=1,
            col=1,
        )

        # Add confidence trend line
        if len(confidences) > 1:
            z = np.polyfit(range(len(confidences)), confidences, 1)
            trend_line = np.poly1d(z)
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=[trend_line(i) for i in range(len(confidences))],
                    mode="lines",
                    name="Confidence Trend",
                    line=dict(color="lightblue", dash="dash"),
                ),
                row=1,
                col=1,
            )

        # Decay analysis
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=decay_scores,
                mode="lines+markers",
                name="Decay Score",
                line=dict(color="red", width=2),
                marker=dict(size=6),
            ),
            row=2,
            col=1,
        )

        # Update layout
        fig.update_layout(
            title="Memory Confidence & Decay Analysis", height=600, showlegend=True
        )

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Confidence Score", row=1, col=1)
        fig.update_yaxes(title_text="Decay Score", row=2, col=1)

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_memory_network_graph(
        self, map_nodes: List[MemoryMapNode]
    ) -> Optional[str]:
        """🕸️ Create interactive memory network visualization"""
        if not PLOTLY_AVAILABLE or not map_nodes:
            return None

        # Build network graph data
        node_ids = [node.node_id for node in map_nodes]
        node_texts = [
            f"{node.content_preview}<br>Confidence: {node.confidence:.2f}<br>Type: {node.fragment_type}"
            for node in map_nodes
        ]

        # Create edges based on connections
        edge_x = []
        edge_y = []

        # Simple circular layout for visualization
        import math

        n_nodes = len(map_nodes)
        for i, node in enumerate(map_nodes):
            angle = 2 * math.pi * i / n_nodes
            x = math.cos(angle)
            y = math.sin(angle)

            # Store positions for edges
            node.x_pos = x
            node.y_pos = y

        # Add edges
        for node in map_nodes:
            for connection_id in node.connections:
                connected_node = next(
                    (n for n in map_nodes if n.node_id == connection_id), None
                )
                if connected_node:
                    edge_x.extend([node.x_pos, connected_node.x_pos, None])
                    edge_y.extend([node.y_pos, connected_node.y_pos, None])

        # Create network graph
        fig = go.Figure()

        # Add edges
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=1, color="lightgray"),
                hoverinfo="none",
                mode="lines",
                name="Connections",
            )
        )

        # Add nodes
        node_x = [node.x_pos for node in map_nodes]
        node_y = [node.y_pos for node in map_nodes]
        node_colors = [node.confidence for node in map_nodes]

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers",
                hoverinfo="text",
                text=node_texts,
                marker=dict(
                    size=15,
                    color=node_colors,
                    colorscale="Viridis",
                    colorbar=dict(title="Confidence Score"),
                    line=dict(width=2, color="white"),
                ),
                name="Memory Fragments",
            )
        )

        fig.update_layout(
            title="Real-time Memory Network Map",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Memory fragments connected by associative links. Color indicates confidence level.",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(color="#888"),
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def store_story_feedback(self, feedback: StoryFeedback):
        """💬 Store story feedback for quality improvement"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO story_feedback
                (story_id, story_type, quality_score, coherence_score, engagement_score,
                 accuracy_score, feedback_text, improvement_suggestions, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feedback.story_id,
                    feedback.story_type,
                    feedback.quality_score,
                    feedback.coherence_score,
                    feedback.engagement_score,
                    feedback.accuracy_score,
                    feedback.feedback_text,
                    json.dumps(feedback.improvement_suggestions),
                    feedback.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_story_feedback_analytics(self) -> Dict[str, Any]:
        """📊 Get story feedback analytics and trends"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT story_type, AVG(quality_score), AVG(coherence_score),
                       AVG(engagement_score), AVG(accuracy_score), COUNT(*)
                FROM story_feedback
                GROUP BY story_type
            """)

            analytics = {}
            for row in cursor.fetchall():
                analytics[row[0]] = {
                    "avg_quality": row[1],
                    "avg_coherence": row[2],
                    "avg_engagement": row[3],
                    "avg_accuracy": row[4],
                    "feedback_count": row[5],
                }

            return analytics
        finally:
            conn.close()

    def _calculate_decay_rate(self, fragments: List[MemoryFragment]) -> float:
        """Calculate memory decay rate based on age and access patterns"""
        if not fragments:
            return 0.0

        total_decay = 0.0
        for fragment in fragments:
            age_days = (datetime.now() - fragment.created_at).days
            # Simple decay model - could be enhanced with access patterns
            decay = min(1.0, age_days * 0.01)  # 1% decay per day
            total_decay += decay

        return total_decay / len(fragments)

    def _calculate_growth_rate(self, fragments: List[MemoryFragment]) -> float:
        """Calculate memory system growth rate"""
        if not fragments:
            return 0.0

        # Count fragments created in last 24 hours
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_fragments = [f for f in fragments if f.created_at > recent_cutoff]

        return len(recent_fragments) / 24.0  # Fragments per hour

    def _store_health_metrics(self, metrics: MemoryHealthMetrics):
        """Store health metrics in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO memory_health_metrics
                (timestamp, total_fragments, avg_confidence, confidence_std,
                 memory_coherence, narrative_quality, causal_chain_count,
                 goal_arc_count, decay_rate, growth_rate, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.timestamp.isoformat(),
                    metrics.total_fragments,
                    metrics.avg_confidence,
                    metrics.confidence_std,
                    metrics.memory_coherence,
                    metrics.narrative_quality,
                    metrics.causal_chain_count,
                    metrics.goal_arc_count,
                    metrics.decay_rate,
                    metrics.growth_rate,
                    json.dumps(asdict(metrics), default=str),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _setup_routes(self):
        """Setup Flask routes for web dashboard"""
        if not self.app:
            return

        @self.app.route("/")
        def dashboard():
            return render_template("memory_dashboard.html")

        @self.app.route("/api/health-metrics")
        def get_health_metrics():
            # Return latest health metrics
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT metrics_json FROM memory_health_metrics
                    ORDER BY timestamp DESC LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                else:
                    return {"error": "No metrics available"}
            finally:
                conn.close()

        @self.app.route("/api/memory-map")
        def get_memory_map():
            # Return memory map data - would need fragments from request
            return {"nodes": [], "message": "Memory map data endpoint"}

        @self.app.route("/api/story-feedback", methods=["POST"])
        def submit_story_feedback():
            data = request.json
            feedback = StoryFeedback(
                story_id=data["story_id"],
                story_type=data["story_type"],
                quality_score=data["quality_score"],
                coherence_score=data["coherence_score"],
                engagement_score=data["engagement_score"],
                accuracy_score=data["accuracy_score"],
                feedback_text=data.get("feedback_text"),
                improvement_suggestions=data.get("improvement_suggestions", []),
                timestamp=datetime.now(),
            )

            self.store_story_feedback(feedback)
            return {"status": "success"}

    def run_dashboard(self, host="localhost", port=5000, debug=False):
        """🚀 Launch the web dashboard"""
        if not FLASK_AVAILABLE:
            print("❌ Flask not available - cannot run web dashboard")
            print("💡 Install with: pip install flask plotly pandas")
            return

        if not self.app:
            print("❌ Dashboard app not initialized")
            return

        print(f"🚀 Starting Memory Analytics Dashboard...")
        print(f"📊 Dashboard URL: http://{host}:{port}")
        print(f"💡 Features: Real-time memory map, confidence tracking, story feedback")

        self.app.run(host=host, port=port, debug=debug)


# Add numpy import for trend line calculation
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Fallback without trend lines
    pass


def create_sample_dashboard_demo():
    """Create a sample demo of the dashboard with synthetic data"""
    print("📊 MEMORY ANALYTICS DASHBOARD DEMO")
    print("=" * 50)

    dashboard = MemoryAnalyticsDashboard("demo_analytics.db")

    if not MEMORY_IMPORTS_AVAILABLE:
        print("⚠️ Memory system not available - using synthetic data")
        # Could create synthetic data here for demo
        return dashboard

    # Create sample fragments for demo
    from datetime import datetime, timedelta

    base_time = datetime.now() - timedelta(days=7)

    sample_fragments = []
    for i in range(20):
        fragment = MemoryFragment(
            fragment_id=f"demo_{i}",
            content={
                "text": f"Sample memory fragment {i} with some content for testing"
            },
            fragment_type=MemoryFragmentType.EPISODIC,
            temporal_tags={"timestamp": base_time + timedelta(hours=i * 6)},
            symbolic_tags={f"tag_{i % 5}", "demo", "analytics"},
            associative_links=[f"demo_{j}" for j in range(max(0, i - 2), i)],
            confidence_score=0.3 + (i * 0.035),  # Increasing confidence
            access_pattern={"frequency": i % 3 + 1},
            narrative_role="sample_data",
            created_at=base_time + timedelta(hours=i * 6),
            last_evolved=base_time + timedelta(hours=i * 6),
        )
        sample_fragments.append(fragment)

    print(f"📊 Created {len(sample_fragments)} sample fragments")

    # Test analytics collection
    async def run_analytics():
        metrics = await dashboard.collect_memory_health_metrics(sample_fragments)
        print(f"\n📈 Health Metrics:")
        print(f"   Total fragments: {metrics.total_fragments}")
        print(f"   Average confidence: {metrics.avg_confidence:.3f}")
        print(f"   Memory coherence: {metrics.memory_coherence:.3f}")
        print(f"   Narrative quality: {metrics.narrative_quality:.3f}")
        print(f"   Causal chains: {metrics.causal_chain_count}")
        print(f"   Goal arcs: {metrics.goal_arc_count}")
        print(f"   Decay rate: {metrics.decay_rate:.3f}")
        print(f"   Growth rate: {metrics.growth_rate:.3f}")

        # Generate memory map
        map_nodes = dashboard.generate_memory_map_data(sample_fragments)
        print(f"\n🗺️ Memory Map: {len(map_nodes)} nodes generated")

        # Test visualizations
        if PLOTLY_AVAILABLE:
            confidence_chart = dashboard.create_confidence_evolution_chart(
                sample_fragments
            )
            network_graph = dashboard.create_memory_network_graph(map_nodes)

            print(
                f"📈 Confidence chart: {'Generated' if confidence_chart else 'Failed'}"
            )
            print(f"🕸️ Network graph: {'Generated' if network_graph else 'Failed'}")

        # Sample story feedback
        feedback = StoryFeedback(
            story_id="demo_story_1",
            story_type="daily_narrative",
            quality_score=0.85,
            coherence_score=0.78,
            engagement_score=0.90,
            accuracy_score=0.82,
            feedback_text="Great storytelling, very engaging narrative",
            improvement_suggestions=[
                "Add more emotional context",
                "Include causal connections",
            ],
            timestamp=datetime.now(),
        )

        dashboard.store_story_feedback(feedback)
        print(f"\n💬 Story feedback: Stored sample feedback")

        # Get feedback analytics
        feedback_analytics = dashboard.get_story_feedback_analytics()
        print(f"📊 Feedback analytics: {feedback_analytics}")

    # Run async analytics
    asyncio.run(run_analytics())

    return dashboard


if __name__ == "__main__":
    # Demo the dashboard
    dashboard = create_sample_dashboard_demo()

    print(f"\n🎉 Memory Analytics Dashboard Demo Complete!")
    print(f"💡 Features demonstrated:")
    print(f"   📊 Real-time health metrics collection")
    print(f"   🗺️ Memory map data generation")
    print(f"   📈 Confidence/decay visualization")
    print(f"   💬 Story feedback system")
    print(f"   📈 Analytics and trend tracking")

    if FLASK_AVAILABLE:
        print(f"\n🚀 To launch web dashboard, run:")
        print(f"   dashboard.run_dashboard()")
    else:
        print(f"\n💡 Install Flask for web dashboard: pip install flask plotly pandas")
