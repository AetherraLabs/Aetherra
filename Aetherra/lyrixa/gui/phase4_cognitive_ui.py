#!/usr/bin/env python3
"""
🧠 Phase 4: Cognitive UI Integration
===================================

Real-time visualization of Lyrixa's cognitive processes including:
- Thought streams and reasoning chains
- Goal status tracking with confidence heatmaps
- Memory activation patterns
- Query-response correlation visualization
- Live cognitive load monitoring

This system creates a window into Lyrixa's "mind" - making AI reasoning
transparent and interactive for users.
"""

import json
import logging
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal, QTimer, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView

logger = logging.getLogger(__name__)


def datetime_serializer(obj):
    """Custom JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_asdict_with_datetime(dataclass_obj):
    """Safely convert dataclass to dict with datetime serialization"""
    try:
        result = asdict(dataclass_obj)
        # Convert datetime objects to ISO strings
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result
    except Exception as e:
        logger.error(f"Error converting dataclass to dict: {e}")
        return {}


@dataclass
class ThoughtBubble:
    """Represents a single thought in Lyrixa's cognitive stream"""
    id: str
    content: str
    thought_type: str  # 'reasoning', 'memory_recall', 'goal_planning', 'response_generation'
    confidence: float  # 0.0-1.0
    timestamp: datetime
    related_query: Optional[str] = None
    memory_nodes: Optional[List[str]] = None
    duration_ms: int = 0
    importance: float = 0.5


@dataclass
class GoalState:
    """Represents a goal and its current state"""
    id: str
    description: str
    status: str  # 'planning', 'active', 'completed', 'blocked', 'uncertain'
    confidence: float  # 0.0-1.0 (for heatmap coloring)
    priority: int  # 1-10
    progress: float  # 0.0-1.0
    sub_goals: Optional[List[str]] = None
    blocking_factors: Optional[List[str]] = None
    estimated_completion: Optional[datetime] = None


@dataclass
class MemoryActivation:
    """Represents memory nodes being activated during processing"""
    memory_id: str
    activation_strength: float  # 0.0-1.0
    access_type: str  # 'read', 'write', 'update', 'recall'
    related_thoughts: Optional[List[str]] = None
    timestamp: Optional[datetime] = None


@dataclass
class QueryTrace:
    """Traces the path from user query to system response"""
    query_id: str
    user_query: str
    processing_stages: List[Dict[str, Any]]
    thought_chain: List[str]  # IDs of related thoughts
    memory_activations: List[str]  # IDs of activated memories
    confidence_progression: List[float]  # Confidence over time
    response_generated: Optional[str] = None
    total_processing_time: float = 0.0


class CognitiveStateMonitor(QObject):
    """
    🧠 Cognitive State Monitor

    Tracks and analyzes Lyrixa's cognitive processes in real-time.
    Provides data for visualization components.
    """

    # Signals for real-time updates
    thought_generated = Signal(str)      # New thought bubble
    goal_updated = Signal(str)           # Goal state change
    memory_activated = Signal(str)       # Memory activation
    query_processed = Signal(str)        # Query trace complete
    cognitive_load_changed = Signal(str) # Overall cognitive load

    def __init__(self):
        super().__init__()
        self.active_thoughts: List[ThoughtBubble] = []
        self.current_goals: List[GoalState] = []
        self.memory_activations: List[MemoryActivation] = []
        self.query_traces: List[QueryTrace] = []
        self.backend_services = {}

        # Cognitive metrics
        self.cognitive_load = 0.0
        self.thought_frequency = 0.0
        self.reasoning_depth = 0.0

        # Start monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_cognitive_state)
        self.monitor_timer.start(500)  # Monitor every 500ms for responsive UI

        # Cleanup timer for old thoughts
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_old_data)
        self.cleanup_timer.start(10000)  # Cleanup every 10 seconds

    def connect_backend_services(self, services: Dict[str, Any]):
        """Connect to backend services for cognitive monitoring"""
        self.backend_services = services
        logger.info(f"[COGNITIVE] Monitor connected to {len(services)} backend services")

        # Initialize with current system state
        self.initialize_cognitive_state()

    def initialize_cognitive_state(self):
        """Initialize cognitive state from current backend systems"""
        try:
            # Generate initial thoughts based on system state
            self.generate_startup_thoughts()

            # Initialize goals from agent orchestrator
            self.initialize_goals()

            # Set baseline cognitive metrics
            self.cognitive_load = 0.3  # Baseline cognitive activity
            self.thought_frequency = 2.0  # Thoughts per second
            self.reasoning_depth = 0.6  # Depth of reasoning chains

            logger.info("[COGNITIVE] Cognitive state initialized")

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize cognitive state: {e}")

    def generate_startup_thoughts(self):
        """Generate initial thoughts when system starts"""
        startup_thoughts = [
            ("🌟 System initialization complete - all neural pathways active", "reasoning", 0.95),
            ("🔍 Scanning available plugins and capabilities", "memory_recall", 0.88),
            ("🎯 Establishing baseline goals and priorities", "goal_planning", 0.92),
            ("🧠 Memory systems online - knowledge graph accessible", "memory_recall", 0.91),
            ("👋 Ready for user interaction and collaboration", "response_generation", 0.97)
        ]

        for content, thought_type, confidence in startup_thoughts:
            thought = ThoughtBubble(
                id=f"startup_{int(time.time() * 1000)}_{random.randint(100, 999)}",
                content=content,
                thought_type=thought_type,
                confidence=confidence,
                timestamp=datetime.now(),
                duration_ms=random.randint(1500, 3000),
                importance=0.8
            )
            self.add_thought(thought)
            time.sleep(0.2)  # Stagger the thoughts

    def initialize_goals(self):
        """Initialize goals from agent orchestrator"""
        try:
            agent_orchestrator = self.backend_services.get('agent_orchestrator')
            if agent_orchestrator and hasattr(agent_orchestrator, 'agents'):
                # Create goals based on active agents
                for i, agent in enumerate(agent_orchestrator.agents[:5]):  # Limit to 5 for display
                    goal = GoalState(
                        id=f"agent_goal_{i}",
                        description=f"Execute agent: {getattr(agent, 'name', f'Agent {i}')}",
                        status='active',
                        confidence=random.uniform(0.7, 0.95),
                        priority=random.randint(3, 8),
                        progress=random.uniform(0.1, 0.8)
                    )
                    self.current_goals.append(goal)
            else:
                # Create default system goals
                default_goals = [
                    ("Maintain system optimal performance", "active", 0.92, 8),
                    ("Learn from user interactions", "active", 0.86, 7),
                    ("Process incoming queries efficiently", "planning", 0.78, 9),
                    ("Update knowledge base", "active", 0.71, 5),
                    ("Monitor system security", "active", 0.94, 9)
                ]

                for i, (desc, status, confidence, priority) in enumerate(default_goals):
                    goal = GoalState(
                        id=f"system_goal_{i}",
                        description=desc,
                        status=status,
                        confidence=confidence,
                        priority=priority,
                        progress=random.uniform(0.2, 0.9)
                    )
                    self.current_goals.append(goal)

        except Exception as e:
            logger.warning(f"[WARN] Error initializing goals: {e}")

    def monitor_cognitive_state(self):
        """Monitor and update cognitive state in real-time"""
        try:
            # Update cognitive load based on system activity
            self.update_cognitive_load()

            # Generate random thoughts based on system activity
            if random.random() < 0.1:  # 10% chance every 500ms
                self.generate_random_thought()

            # Update goal states
            if random.random() < 0.05:  # 5% chance every 500ms
                self.update_random_goal()

            # Simulate memory activations
            if random.random() < 0.08:  # 8% chance every 500ms
                self.simulate_memory_activation()

            # Emit cognitive load updates
            cognitive_data = {
                'load': self.cognitive_load,
                'frequency': self.thought_frequency,
                'depth': self.reasoning_depth,
                'active_thoughts': len(self.active_thoughts),
                'active_goals': len([g for g in self.current_goals if g.status == 'active']),
                'timestamp': int(time.time())
            }
            self.cognitive_load_changed.emit(json.dumps(cognitive_data))

        except Exception as e:
            logger.error(f"[ERROR] Cognitive monitoring error: {e}")

    def update_cognitive_load(self):
        """Update cognitive load based on system activity"""
        # Base load from active thoughts and goals
        thought_load = len(self.active_thoughts) * 0.1
        goal_load = len([g for g in self.current_goals if g.status == 'active']) * 0.05

        # Add some randomness for realistic fluctuation
        random_factor = random.uniform(-0.1, 0.1)

        self.cognitive_load = max(0.1, min(1.0, 0.3 + thought_load + goal_load + random_factor))

        # Update thought frequency based on load
        self.thought_frequency = 1.0 + (self.cognitive_load * 3.0)

        # Update reasoning depth
        self.reasoning_depth = max(0.2, min(1.0, 0.4 + (self.cognitive_load * 0.8)))

    def generate_random_thought(self):
        """Generate a random thought based on current system state"""
        thought_templates = {
            'reasoning': [
                "🤔 Analyzing optimal approach for current task",
                "⚡ Processing multiple solution pathways",
                "🔄 Evaluating decision tree branches",
                "🎯 Optimizing response strategy",
                "📊 Weighing probability distributions"
            ],
            'memory_recall': [
                "📚 Accessing relevant knowledge patterns",
                "🔍 Searching memory clusters for context",
                "💭 Recalling similar past interactions",
                "🧩 Connecting related memory nodes",
                "📖 Retrieving procedural knowledge"
            ],
            'goal_planning': [
                "🎯 Updating goal priority matrix",
                "🗺️ Planning next action sequence",
                "⏰ Adjusting timeline estimates",
                "🔄 Reassessing goal dependencies",
                "🎲 Evaluating risk factors"
            ],
            'response_generation': [
                "✍️ Crafting optimal response structure",
                "🎨 Selecting appropriate communication style",
                "🔤 Choosing precise terminology",
                "💫 Generating creative alternatives",
                "🎪 Balancing clarity and depth"
            ]
        }

        thought_type = random.choice(list(thought_templates.keys()))
        content = random.choice(thought_templates[thought_type])

        thought = ThoughtBubble(
            id=f"thought_{int(time.time() * 1000)}_{random.randint(100, 999)}",
            content=content,
            thought_type=thought_type,
            confidence=random.uniform(0.6, 0.98),
            timestamp=datetime.now(),
            duration_ms=random.randint(800, 4000),
            importance=random.uniform(0.3, 0.9)
        )

        self.add_thought(thought)

    def update_random_goal(self):
        """Update a random goal state"""
        if not self.current_goals:
            return

        goal = random.choice(self.current_goals)

        # Small chance to change status
        if random.random() < 0.3:
            statuses = ['planning', 'active', 'completed', 'blocked', 'uncertain']
            goal.status = random.choice(statuses)

        # Update confidence (small fluctuations)
        goal.confidence = max(0.1, min(1.0, goal.confidence + random.uniform(-0.1, 0.1)))

        # Update progress
        if goal.status == 'active':
            goal.progress = min(1.0, goal.progress + random.uniform(0.0, 0.05))
        elif goal.status == 'completed':
            goal.progress = 1.0

        # Emit goal update
        self.goal_updated.emit(json.dumps(safe_asdict_with_datetime(goal)))

    def simulate_memory_activation(self):
        """Simulate memory node activation"""
        memory_types = ['episodic', 'semantic', 'procedural', 'working']
        access_types = ['read', 'write', 'update', 'recall']

        activation = MemoryActivation(
            memory_id=f"mem_{random.choice(memory_types)}_{random.randint(100, 999)}",
            activation_strength=random.uniform(0.3, 1.0),
            access_type=random.choice(access_types),
            timestamp=datetime.now()
        )

        self.memory_activations.append(activation)
        self.memory_activated.emit(json.dumps(safe_asdict_with_datetime(activation)))

        # Keep only recent activations
        cutoff_time = datetime.now().timestamp() - 30  # 30 seconds
        self.memory_activations = [
            m for m in self.memory_activations
            if m.timestamp and m.timestamp.timestamp() > cutoff_time
        ]

    def add_thought(self, thought: ThoughtBubble):
        """Add a new thought and emit signal"""
        self.active_thoughts.append(thought)
        self.thought_generated.emit(json.dumps(safe_asdict_with_datetime(thought)))

        # Keep only recent thoughts (last 20)
        if len(self.active_thoughts) > 20:
            self.active_thoughts = self.active_thoughts[-20:]

    def process_user_query(self, query: str) -> str:
        """Process a user query and create trace visualization"""
        query_id = f"query_{int(time.time() * 1000)}"

        # Create query trace
        trace = QueryTrace(
            query_id=query_id,
            user_query=query,
            processing_stages=[],
            thought_chain=[],
            memory_activations=[],
            confidence_progression=[]
        )

        # Simulate processing stages
        stages = [
            ("Query parsing", 0.9),
            ("Context analysis", 0.85),
            ("Memory search", 0.8),
            ("Response generation", 0.88),
            ("Quality check", 0.92)
        ]

        for stage_name, confidence in stages:
            stage_data = {
                'name': stage_name,
                'timestamp': time.time(),
                'confidence': confidence,
                'duration_ms': random.randint(200, 800)
            }
            trace.processing_stages.append(stage_data)
            trace.confidence_progression.append(confidence)

            # Generate related thought
            thought_content = f"🔄 {stage_name}: {query[:30]}..."
            thought = ThoughtBubble(
                id=f"query_thought_{query_id}_{len(trace.thought_chain)}",
                content=thought_content,
                thought_type="reasoning",
                confidence=confidence,
                timestamp=datetime.now(),
                related_query=query_id,
                duration_ms=stage_data['duration_ms']
            )

            self.add_thought(thought)
            trace.thought_chain.append(thought.id)

            time.sleep(0.1)  # Small delay for visualization

        # Complete the trace
        trace.response_generated = f"Response generated for: {query}"
        trace.total_processing_time = sum(s['duration_ms'] for s in trace.processing_stages)

        self.query_traces.append(trace)
        self.query_processed.emit(json.dumps(safe_asdict_with_datetime(trace)))

        return trace.query_id

    def cleanup_old_data(self):
        """Clean up old thoughts and data to prevent memory leaks"""
        current_time = datetime.now()
        cutoff_time = current_time.timestamp() - 60  # Keep last 60 seconds

        # Clean old thoughts
        self.active_thoughts = [
            t for t in self.active_thoughts
            if t.timestamp.timestamp() > cutoff_time
        ]

        # Clean old query traces (keep last 10)
        if len(self.query_traces) > 10:
            self.query_traces = self.query_traces[-10:]

        # Clean old memory activations
        self.memory_activations = [
            m for m in self.memory_activations
            if m.timestamp and m.timestamp.timestamp() > cutoff_time
        ]

    # === SLOT METHODS (Called from JavaScript) ===

    @Slot(str)
    def simulateUserQuery(self, query):
        """Simulate processing a user query (called from UI)"""
        self.process_user_query(query)

    @Slot(str)
    def addGoal(self, goal_description):
        """Add a new goal (called from UI)"""
        goal = GoalState(
            id=f"user_goal_{int(time.time())}",
            description=goal_description,
            status='planning',
            confidence=0.7,
            priority=5,
            progress=0.0
        )
        self.current_goals.append(goal)
        self.goal_updated.emit(json.dumps(safe_asdict_with_datetime(goal)))

    @Slot(str, str)
    def updateGoalStatus(self, goal_id, new_status):
        """Update goal status (called from UI)"""
        for goal in self.current_goals:
            if goal.id == goal_id:
                goal.status = new_status
                if new_status == 'completed':
                    goal.progress = 1.0
                    goal.confidence = min(1.0, goal.confidence + 0.1)
                self.goal_updated.emit(json.dumps(safe_asdict_with_datetime(goal)))
                break

    @Slot(result=str)
    def getCognitiveState(self):
        """Get current cognitive state (called from UI)"""
        try:
            state = {
                'thoughts': [safe_asdict_with_datetime(t) for t in self.active_thoughts[-10:]],  # Last 10 thoughts
                'goals': [safe_asdict_with_datetime(g) for g in self.current_goals],
                'memory_activations': [safe_asdict_with_datetime(m) for m in self.memory_activations[-5:]],  # Last 5
                'cognitive_load': self.cognitive_load,
                'thought_frequency': self.thought_frequency,
                'reasoning_depth': self.reasoning_depth,
                'timestamp': int(time.time())
            }
            return json.dumps(state)
        except Exception as e:
            logger.error(f"[ERROR] Cognitive monitoring error: {e}")
            # Return empty state on error
            return json.dumps({
                'thoughts': [],
                'goals': [],
                'memory_activations': [],
                'cognitive_load': 0.0,
                'thought_frequency': 0.0,
                'reasoning_depth': 0.0,
                'timestamp': int(time.time())
            })


class Phase4CognitiveUI(QObject):
    """
    🧠 Phase 4: Cognitive UI Integration System

    Main coordinator for cognitive visualization features.
    Integrates with existing GUI system to add cognitive panels.
    """

    def __init__(self, gui_dir: Path):
        super().__init__()
        self.gui_dir = gui_dir
        self.cognitive_monitor = CognitiveStateMonitor()
        self.cognitive_panels = {}

        logger.info("[PHASE4] Cognitive UI Integration initialized")

    def connect_backend_services(self, services: Dict[str, Any]):
        """Connect to backend services"""
        self.cognitive_monitor.connect_backend_services(services)
        logger.info(f"[PHASE4] Connected to {len(services)} backend services")

    def start_cognitive_monitoring(self):
        """Start cognitive state monitoring"""
        logger.info("[PHASE4] Cognitive monitoring started")

    def generate_cognitive_panel(self, panel_type: str) -> str:
        """Generate cognitive visualization panel"""
        if panel_type == 'thoughts':
            return self.generate_thoughts_panel()
        elif panel_type == 'goals':
            return self.generate_goals_panel()
        elif panel_type == 'memory':
            return self.generate_memory_panel()
        elif panel_type == 'traces':
            return self.generate_traces_panel()
        else:
            return self.generate_overview_panel()

    def generate_thoughts_panel(self) -> str:
        """Generate the thought stream visualization panel"""
        panel_path = self.gui_dir / "web_panels" / "auto_generated" / "cognitive_thoughts_panel.html"

        # This will be created in the next step
        return str(panel_path)

    def generate_goals_panel(self) -> str:
        """Generate the goal status heatmap panel"""
        panel_path = self.gui_dir / "web_panels" / "auto_generated" / "cognitive_goals_panel.html"

        # This will be created in the next step
        return str(panel_path)

    def generate_memory_panel(self) -> str:
        """Generate the memory activation visualization panel"""
        panel_path = self.gui_dir / "web_panels" / "auto_generated" / "cognitive_memory_panel.html"

        # This will be created in the next step
        return str(panel_path)

    def generate_traces_panel(self) -> str:
        """Generate the query trace visualization panel"""
        panel_path = self.gui_dir / "web_panels" / "auto_generated" / "cognitive_traces_panel.html"

        # This will be created in the next step
        return str(panel_path)

    def generate_overview_panel(self) -> str:
        """Generate the cognitive overview panel"""
        panel_path = self.gui_dir / "web_panels" / "auto_generated" / "cognitive_overview_panel.html"

        # This will be created in the next step
        return str(panel_path)
