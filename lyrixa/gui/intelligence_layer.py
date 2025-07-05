"""
GUI Intelligence Layer for Lyrixa AI Assistant

Advanced visualization and intelligence features including:
- Memory visualization with context graphs
- Live "Lyrixa Thinks..." pane showing current anticipations
- Interactive timeline with color-coded contexts
- Real-time confidence modeling display
- Workflow state visualization
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import time

try:
    from PySide6.QtCore import (
        Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve,
        QParallelAnimationGroup, QSequentialAnimationGroup, QRect
    )
    from PySide6.QtGui import (
        QColor, QFont, QPalette, QPainter, QLinearGradient, QBrush,
        QPixmap, QIcon, QPen
    )
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFrame, QScrollArea, QSplitter, QTabWidget, QGroupBox,
        QTextEdit, QProgressBar, QSlider, QSpinBox, QCheckBox,
        QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene,
        QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem,
        QGraphicsTextItem, QTreeWidget, QTreeWidgetItem, QComboBox
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # Mock classes for when PySide6 is not available
    class QWidget:
        def __init__(self, *args, **kwargs):
            pass
        def resize(self, *args):
            pass
        def show(self):
            pass
    class Signal:
        def __init__(self, *args):
            pass
        def connect(self, *args):
            pass
        def emit(self, *args):
            pass
    class QThread:
        pass
    class QTimer:
        def __init__(self, *args):
            pass
        def start(self, *args):
            pass
        def stop(self):
            pass
    # Mock other Qt classes
    Qt = type('Qt', (), {'AlignCenter': 0, 'AlignLeft': 0})
    QVBoxLayout = QHBoxLayout = QTabWidget = QLabel = QPushButton = QWidget
    QGroupBox = QFrame = QScrollArea = QSplitter = QTextEdit = QWidget
    QProgressBar = QSlider = QSpinBox = QCheckBox = QListWidget = QWidget
    QGraphicsView = QGraphicsScene = QTreeWidget = QWidget
    QFont = QColor = QPalette = QWidget

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryNode:
    """Represents a memory node in the visualization graph."""
    id: str
    content: str
    memory_type: str
    confidence: float
    importance: float
    timestamp: datetime
    connections: List[str]
    position: Tuple[float, float] = (0.0, 0.0)
    color: str = "#4CAF50"

@dataclass
class ThoughtProcess:
    """Represents a current thought/anticipation process."""
    id: str
    description: str
    confidence: float
    context: Dict[str, Any]
    suggestions: List[str]
    timestamp: datetime
    status: str = "active"  # active, completed, discarded

class ContextMood(Enum):
    """Context mood types for timeline visualization."""
    PRODUCTIVE = "productive"
    CONFUSED = "confused"
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    LEARNING = "learning"
    CREATING = "creating"

@dataclass
class TimelineEvent:
    """Represents an event in the interaction timeline."""
    timestamp: datetime
    event_type: str
    description: str
    mood: ContextMood
    confidence: float
    goal_progress: float
    color: str

class MemoryGraphWidget(QWidget if PYSIDE6_AVAILABLE else object):
    """Interactive memory visualization graph with advanced features."""
    
    node_selected = Signal(str) if PYSIDE6_AVAILABLE else None
    connection_created = Signal(str, str) if PYSIDE6_AVAILABLE else None
    
    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return
            
        super().__init__(parent)
        self.memory_nodes = []
        self.connections = []
        self.selected_node = None
        self.hover_node = None
        self.real_time_updates = True
        self.layout_algorithm = "force_directed"
        
        self.init_ui()
        self.setup_animations()
        self.setup_real_time_updates()
        
    def init_ui(self):
        """Initialize the advanced memory graph UI."""
        layout = QVBoxLayout()
        
        # Enhanced header with controls
        header_layout = QHBoxLayout()
        header = QLabel("🧠 Memory Context Graph")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        header_layout.addWidget(header)
        
        # Real-time toggle
        self.realtime_checkbox = QCheckBox("Real-time Updates")
        self.realtime_checkbox.setChecked(True)
        self.realtime_checkbox.toggled.connect(self.toggle_realtime)
        header_layout.addWidget(self.realtime_checkbox)
        
        # Layout algorithm selector
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(["Force Directed", "Circular", "Hierarchical", "Grid"])
        self.layout_selector.currentTextChanged.connect(self.change_layout_algorithm)
        header_layout.addWidget(self.layout_selector)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Graph view with enhanced features
        self.graph_view = QGraphicsView()
        self.graph_scene = QGraphicsScene()
        self.graph_view.setScene(self.graph_scene)
        self.graph_view.setRenderHint(QPainter.Antialiasing)
        self.graph_view.setDragMode(QGraphicsView.RubberBandDrag)
        self.graph_view.setInteractive(True)
        layout.addWidget(self.graph_view)
        
        # Enhanced controls
        controls_layout = QHBoxLayout()
        
        self.auto_layout_btn = QPushButton("🔄 Auto Layout")
        self.auto_layout_btn.clicked.connect(self.auto_layout_nodes)
        controls_layout.addWidget(self.auto_layout_btn)
        
        self.filter_btn = QPushButton("🎯 Filter Nodes")
        self.filter_btn.clicked.connect(self.show_filter_dialog)
        controls_layout.addWidget(self.filter_btn)
        
        self.cluster_btn = QPushButton("🔗 Auto Cluster")
        self.cluster_btn.clicked.connect(self.auto_cluster_nodes)
        controls_layout.addWidget(self.cluster_btn)
        
        # Zoom controls
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_in_btn.clicked.connect(lambda: self.graph_view.scale(1.2, 1.2))
        controls_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.zoom_out_btn.clicked.connect(lambda: self.graph_view.scale(0.8, 0.8))
        controls_layout.addWidget(self.zoom_out_btn)
        
        self.reset_view_btn = QPushButton("🎯 Reset View")
        self.reset_view_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_view_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Info panel
        self.info_panel = QTextEdit()
        self.info_panel.setMaximumHeight(100)
        self.info_panel.setPlaceholderText("Select a node to see details...")
        layout.addWidget(self.info_panel)
        
        self.setLayout(layout)
        
    def setup_animations(self):
        """Setup animation effects for the graph."""
        if not PYSIDE6_AVAILABLE:
            return
            
        self.node_animations = QParallelAnimationGroup()
        
    def add_memory_node(self, node: MemoryNode):
        """Add a memory node to the graph."""
        if not PYSIDE6_AVAILABLE:
            return
            
        self.memory_nodes.append(node)
        self.draw_node(node)
        
    def draw_node(self, node: MemoryNode):
        """Draw a memory node in the graph."""
        # Create node circle
        x, y = node.position
        radius = 20 + (node.importance * 30)  # Size based on importance
        
        # Color based on memory type and confidence
        color_map = {
            "goal": "#FF6B6B",
            "context": "#4ECDC4", 
            "pattern": "#45B7D1",
            "preference": "#96CEB4",
            "general": "#FFEAA7"
        }
        base_color = color_map.get(node.memory_type, "#95A5A6")
        
        # Adjust opacity based on confidence
        color = QColor(base_color)
        color.setAlpha(int(node.confidence * 255))
        
        ellipse = self.graph_scene.addEllipse(
            x - radius, y - radius, radius * 2, radius * 2,
            QPen(QColor("#2C3E50"), 2), QBrush(color)
        )
        
        # Add text label
        text = self.graph_scene.addText(
            node.content[:20] + "..." if len(node.content) > 20 else node.content,
            QFont("Arial", 8)
        )
        text.setPos(x - radius, y + radius + 5)
        
    def auto_layout_nodes(self):
        """Automatically layout nodes using force-directed algorithm."""
        if not self.memory_nodes:
            return
            
        # Simple circular layout for now
        import math
        center_x, center_y = 200, 200
        radius = 150
        
        for i, node in enumerate(self.memory_nodes):
            angle = (2 * math.pi * i) / len(self.memory_nodes)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node.position = (x, y)
            
        self.redraw_graph()
        
    def redraw_graph(self):
        """Redraw the entire graph."""
        if not PYSIDE6_AVAILABLE:
            return
            
        self.graph_scene.clear()
        
        # Draw connections first (so they appear behind nodes)
        for connection in self.connections:
            self.draw_connection(connection)
            
        # Draw nodes
        for node in self.memory_nodes:
            self.draw_node(node)
            
    def draw_connection(self, start_node: MemoryNode, end_node: MemoryNode):
        """Draw a connection between two nodes."""
        if not PYSIDE6_AVAILABLE:
            return
            
        x1, y1 = start_node.position
        x2, y2 = end_node.position
        
        # Create connection line
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(QColor("#95A5A6"), 2))
        self.graph_scene.addItem(line)

    def setup_real_time_updates(self):
        """Setup real-time update system."""
        if not PYSIDE6_AVAILABLE:
            return
            
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graph_data)
        self.update_timer.start(1000)  # Update every second
        
    def toggle_realtime(self, enabled: bool):
        """Toggle real-time updates."""
        self.real_time_updates = enabled
        if enabled:
            self.update_timer.start(1000)
        else:
            self.update_timer.stop()
            
    def change_layout_algorithm(self, algorithm: str):
        """Change the graph layout algorithm."""
        self.layout_algorithm = algorithm.lower().replace(" ", "_")
        self.auto_layout_nodes()
        
    def show_filter_dialog(self):
        """Show dialog for filtering nodes."""
        # Simple implementation - in real app would show proper dialog
        self.info_panel.setText("Filter dialog would open here...")
        
    def auto_cluster_nodes(self):
        """Automatically cluster related nodes."""
        if not self.memory_nodes:
            return
            
        # Simple clustering by memory type
        clusters = {}
        for node in self.memory_nodes:
            node_type = node.memory_type
            if node_type not in clusters:
                clusters[node_type] = []
            clusters[node_type].append(node)
            
        # Position clusters in a circle
        import math
        center_x, center_y = 300, 300
        cluster_radius = 200
        
        for i, (cluster_type, nodes) in enumerate(clusters.items()):
            angle = (2 * math.pi * i) / len(clusters)
            cluster_x = center_x + cluster_radius * math.cos(angle)
            cluster_y = center_y + cluster_radius * math.sin(angle)
            
            # Position nodes within cluster
            for j, node in enumerate(nodes):
                node_angle = (2 * math.pi * j) / len(nodes)
                node.position = (
                    cluster_x + 50 * math.cos(node_angle),
                    cluster_y + 50 * math.sin(node_angle)
                )
                
        self.redraw_graph()
        
    def reset_view(self):
        """Reset the graph view to default."""
        self.graph_view.resetTransform()
        self.graph_view.centerOn(0, 0)
        
    def update_graph_data(self):
        """Update graph with real-time data."""
        if not self.real_time_updates:
            return
            
        # In a real implementation, this would fetch data from the memory system
        # For now, we'll just update node colors based on recent activity
        current_time = datetime.now()
        for node in self.memory_nodes:
            time_diff = (current_time - node.timestamp).total_seconds()
            if time_diff < 60:  # Recent activity (last minute)
                node.color = "#FF6B6B"  # Red for very recent
            elif time_diff < 300:  # Within 5 minutes
                node.color = "#FFA500"  # Orange for recent
            else:
                node.color = "#4CAF50"  # Green for older
                
        self.redraw_graph()
        
class LiveThinkingPane(QWidget if PYSIDE6_AVAILABLE else object):
    """Live display of Lyrixa's current thinking process."""
    
    thought_updated = Signal(dict) if PYSIDE6_AVAILABLE else None
    
    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return
            
        super().__init__(parent)
        self.current_thoughts = []
        self.thinking_animation_timer = QTimer()
        self.thinking_animation_timer.timeout.connect(self.animate_thinking)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the thinking pane UI."""
        layout = QVBoxLayout()
        
        # Header with animation
        header_layout = QHBoxLayout()
        self.header_label = QLabel("🤔 Lyrixa Thinks...")
        self.header_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.header_label.setStyleSheet("color: #8E44AD; margin-bottom: 10px;")
        header_layout.addWidget(self.header_label)
        
        self.thinking_indicator = QLabel("●")
        self.thinking_indicator.setStyleSheet("color: #E74C3C; font-size: 16px;")
        header_layout.addWidget(self.thinking_indicator)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Current thoughts area
        self.thoughts_area = QTextEdit()
        self.thoughts_area.setMaximumHeight(200)
        self.thoughts_area.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.thoughts_area)
        
        # Confidence meters
        confidence_group = QGroupBox("Current Confidence Levels")
        confidence_layout = QVBoxLayout()
        
        self.pattern_confidence = self.create_confidence_meter("Pattern Recognition")
        self.context_confidence = self.create_confidence_meter("Context Understanding")
        self.suggestion_confidence = self.create_confidence_meter("Suggestion Quality")
        
        confidence_layout.addWidget(self.pattern_confidence)
        confidence_layout.addWidget(self.context_confidence)
        confidence_layout.addWidget(self.suggestion_confidence)
        
        confidence_group.setLayout(confidence_layout)
        layout.addWidget(confidence_group)
        
        # Active anticipations
        anticipations_group = QGroupBox("Active Anticipations")
        self.anticipations_list = QListWidget()
        self.anticipations_list.setMaximumHeight(150)
        
        anticipations_layout = QVBoxLayout()
        anticipations_layout.addWidget(self.anticipations_list)
        anticipations_group.setLayout(anticipations_layout)
        layout.addWidget(anticipations_group)
        
        self.setLayout(layout)
        
    def create_confidence_meter(self, label: str):
        """Create a confidence meter widget."""
        container = QWidget()
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setMinimumWidth(120)
        layout.addWidget(label_widget)
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #E74C3C, stop: 0.5 #F39C12, stop: 1 #27AE60
                );
                border-radius: 5px;
            }
        """)
        layout.addWidget(progress)
        
        container.setLayout(layout)
        setattr(container, 'progress_bar', progress)
        return container
        
    def add_thought(self, thought: ThoughtProcess):
        """Add a new thought process."""
        self.current_thoughts.append(thought)
        self.update_display()
        
        if self.thought_updated:
            self.thought_updated.emit({
                'thought': thought.description,
                'confidence': thought.confidence,
                'suggestions': thought.suggestions
            })
            
    def update_display(self):
        """Update the thinking display."""
        if not self.current_thoughts:
            self.thoughts_area.setText("💭 Waiting for context...")
            return
            
        # Display most recent thoughts
        recent_thoughts = self.current_thoughts[-5:]  # Last 5 thoughts
        thoughts_text = ""
        
        for i, thought in enumerate(recent_thoughts):
            timestamp = thought.timestamp.strftime("%H:%M:%S")
            confidence_bar = "▓" * int(thought.confidence * 10) + "░" * (10 - int(thought.confidence * 10))
            
            thoughts_text += f"[{timestamp}] {thought.description}\n"
            thoughts_text += f"    Confidence: {confidence_bar} {thought.confidence:.1%}\n"
            
            if thought.suggestions:
                thoughts_text += f"    → {', '.join(thought.suggestions[:2])}\n"
            thoughts_text += "\n"
            
        self.thoughts_area.setText(thoughts_text)
        
        # Update confidence meters if we have recent thoughts
        if recent_thoughts:
            latest = recent_thoughts[-1]
            self.update_confidence_meters(latest)
            
    def update_confidence_meters(self, thought: ThoughtProcess):
        """Update confidence meters based on current thought."""
        # Simulate different confidence types
        pattern_conf = min(thought.confidence + 0.1, 1.0) * 100
        context_conf = thought.confidence * 100
        suggestion_conf = max(thought.confidence - 0.1, 0.0) * 100
        
        self.pattern_confidence.progress_bar.setValue(int(pattern_conf))
        self.context_confidence.progress_bar.setValue(int(context_conf))
        self.suggestion_confidence.progress_bar.setValue(int(suggestion_conf))
        
    def animate_thinking(self):
        """Animate the thinking indicator."""
        current_color = self.thinking_indicator.styleSheet()
        if "#E74C3C" in current_color:
            self.thinking_indicator.setStyleSheet("color: #F39C12; font-size: 16px;")
        elif "#F39C12" in current_color:
            self.thinking_indicator.setStyleSheet("color: #27AE60; font-size: 16px;")
        else:
            self.thinking_indicator.setStyleSheet("color: #E74C3C; font-size: 16px;")
            
    def start_thinking_animation(self):
        """Start the thinking animation."""
        self.thinking_animation_timer.start(500)  # 500ms interval
        
    def stop_thinking_animation(self):
        """Stop the thinking animation."""
        self.thinking_animation_timer.stop()
        self.thinking_indicator.setStyleSheet("color: #95A5A6; font-size: 16px;")

class InteractiveTimeline(QWidget if PYSIDE6_AVAILABLE else object):
    """Interactive timeline showing user interactions with context and mood."""
    
    event_selected = Signal(dict) if PYSIDE6_AVAILABLE else None
    
    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return
            
        super().__init__(parent)
        self.timeline_events = []
        self.selected_event = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the timeline UI."""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📅 Interaction Timeline")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Timeline view
        self.timeline_tree = QTreeWidget()
        self.timeline_tree.setHeaderLabels([
            "Time", "Event", "Mood", "Confidence", "Goal Progress"
        ])
        self.timeline_tree.itemClicked.connect(self.on_event_selected)
        layout.addWidget(self.timeline_tree)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Mood Legend:"))
        
        mood_colors = {
            "productive": "#27AE60",
            "confused": "#E74C3C", 
            "focused": "#3498DB",
            "distracted": "#F39C12",
            "learning": "#9B59B6",
            "creating": "#E67E22"
        }
        
        for mood, color in mood_colors.items():
            label = QLabel(f"● {mood.title()}")
            label.setStyleSheet(f"color: {color}; font-weight: bold;")
            legend_layout.addWidget(label)
            
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        self.setLayout(layout)
        
    def add_timeline_event(self, event: TimelineEvent):
        """Add an event to the timeline."""
        self.timeline_events.append(event)
        self.refresh_timeline()
        
    def refresh_timeline(self):
        """Refresh the timeline display."""
        self.timeline_tree.clear()
        
        # Group events by day
        events_by_day = {}
        for event in self.timeline_events:
            day_key = event.timestamp.strftime("%Y-%m-%d")
            if day_key not in events_by_day:
                events_by_day[day_key] = []
            events_by_day[day_key].append(event)
            
        # Add events to tree
        for day, events in sorted(events_by_day.items(), reverse=True):
            day_item = QTreeWidgetItem([day, "", "", "", ""])
            day_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            
            for event in sorted(events, key=lambda e: e.timestamp, reverse=True):
                event_item = QTreeWidgetItem([
                    event.timestamp.strftime("%H:%M:%S"),
                    event.description[:50] + "..." if len(event.description) > 50 else event.description,
                    event.mood.value.title(),
                    f"{event.confidence:.1%}",
                    f"{event.goal_progress:.1%}"
                ])
                
                # Color code by mood
                mood_colors = {
                    ContextMood.PRODUCTIVE: QColor("#27AE60"),
                    ContextMood.CONFUSED: QColor("#E74C3C"),
                    ContextMood.FOCUSED: QColor("#3498DB"),
                    ContextMood.DISTRACTED: QColor("#F39C12"),
                    ContextMood.LEARNING: QColor("#9B59B6"),
                    ContextMood.CREATING: QColor("#E67E22")
                }
                
                color = mood_colors.get(event.mood, QColor("#95A5A6"))
                for i in range(5):
                    event_item.setForeground(i, color)
                    
                # Store event data
                event_item.setData(0, Qt.UserRole, event)
                day_item.addChild(event_item)
                
            self.timeline_tree.addTopLevelItem(day_item)
            day_item.setExpanded(True)
            
    def on_event_selected(self, item, column):
        """Handle event selection."""
        event = item.data(0, Qt.UserRole)
        if event and self.event_selected:
            self.event_selected.emit({
                'timestamp': event.timestamp.isoformat(),
                'description': event.description,
                'mood': event.mood.value,
                'confidence': event.confidence,
                'goal_progress': event.goal_progress
            })

class IntelligenceLayerWidget(QWidget if PYSIDE6_AVAILABLE else object):
    """Main GUI Intelligence Layer widget combining all components."""
    
    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning("PySide6 not available. Intelligence Layer will not function.")
            return
            
        super().__init__(parent)
        self.init_ui()
        self.start_demo_data()
        
        logger.info("GUI Intelligence Layer initialized successfully")
        
    def init_ui(self):
        """Initialize the intelligence layer UI."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🧠 Lyrixa Intelligence Layer")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(header_label)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Memory Graph and Timeline
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.memory_graph = MemoryGraphWidget()
        left_layout.addWidget(self.memory_graph)
        
        self.timeline = InteractiveTimeline()
        self.timeline.event_selected.connect(self.on_timeline_event_selected)
        left_layout.addWidget(self.timeline)
        
        left_widget.setLayout(left_layout)
        main_splitter.addWidget(left_widget)
        
        # Right panel - Live Thinking
        self.thinking_pane = LiveThinkingPane()
        self.thinking_pane.thought_updated.connect(self.on_thought_updated)
        main_splitter.addWidget(self.thinking_pane)
        
        # Set splitter sizes
        main_splitter.setSizes([700, 300])
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
        
    def on_timeline_event_selected(self, event_data):
        """Handle timeline event selection."""
        logger.info(f"Timeline event selected: {event_data['description']}")
        
    def on_thought_updated(self, thought_data):
        """Handle thought updates."""
        logger.info(f"New thought: {thought_data['thought']}")
        
    def add_memory_node(self, content: str, memory_type: str, confidence: float, importance: float):
        """Add a memory node to the visualization."""
        node = MemoryNode(
            id=f"mem_{len(self.memory_graph.memory_nodes)}",
            content=content,
            memory_type=memory_type,
            confidence=confidence,
            importance=importance,
            timestamp=datetime.now(),
            connections=[]
        )
        self.memory_graph.add_memory_node(node)
        
    def add_thought_process(self, description: str, confidence: float, suggestions: List[str]):
        """Add a new thought process."""
        thought = ThoughtProcess(
            id=f"thought_{int(time.time())}",
            description=description,
            confidence=confidence,
            context={},
            suggestions=suggestions,
            timestamp=datetime.now()
        )
        self.thinking_pane.add_thought(thought)
        
    def add_timeline_event(self, description: str, mood: ContextMood, confidence: float, goal_progress: float):
        """Add an event to the timeline."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            event_type="interaction",
            description=description,
            mood=mood,
            confidence=confidence,
            goal_progress=goal_progress,
            color="#3498DB"
        )
        self.timeline.add_timeline_event(event)
        
    def start_demo_data(self):
        """Start generating demo data for visualization."""
        if not PYSIDE6_AVAILABLE:
            return
            
        # Demo timer for simulating live data
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.generate_demo_data)
        self.demo_timer.start(3000)  # Every 3 seconds
        
        # Initial demo data
        self.generate_initial_demo_data()
        
    def generate_initial_demo_data(self):
        """Generate initial demo data."""
        # Memory nodes
        demo_memories = [
            ("Working on Aetherra project", "goal", 0.9, 0.8),
            ("User prefers Python for automation", "preference", 0.85, 0.6),
            ("Pattern: asks for help around 3 PM", "pattern", 0.75, 0.7),
            ("Current context: GUI development", "context", 0.95, 0.9),
            ("Learning Qt/PySide6 framework", "learning", 0.7, 0.5)
        ]
        
        for content, mem_type, conf, imp in demo_memories:
            self.add_memory_node(content, mem_type, conf, imp)
            
        # Timeline events
        demo_events = [
            ("Started working on intelligence layer", ContextMood.FOCUSED, 0.8, 0.2),
            ("Asked for GUI implementation help", ContextMood.LEARNING, 0.6, 0.4),
            ("Successfully integrated memory system", ContextMood.PRODUCTIVE, 0.9, 0.6),
            ("Debugging Qt layout issues", ContextMood.CONFUSED, 0.4, 0.7),
            ("Implementing visualization features", ContextMood.CREATING, 0.85, 0.8)
        ]
        
        for desc, mood, conf, progress in demo_events:
            self.add_timeline_event(desc, mood, conf, progress)
            
        # Start thinking animation
        self.thinking_pane.start_thinking_animation()
        
    def generate_demo_data(self):
        """Generate demo data periodically."""
        import random
        
        # Random thought processes
        thoughts = [
            "Analyzing user's current workflow pattern...",
            "Detecting potential optimization opportunity...",
            "Cross-referencing with historical preferences...",
            "Evaluating suggestion relevance...",
            "Monitoring context for state changes..."
        ]
        
        suggestions = [
            ["Consider taking a short break", "Review recent progress"],
            ["Try using keyboard shortcuts", "Optimize current workflow"],
            ["Save current work", "Document key insights"],
            ["Check for updates", "Review code structure"],
            ["Plan next development phase", "Test current implementation"]
        ]
        
        thought = random.choice(thoughts)
        suggestion_set = random.choice(suggestions)
        confidence = random.uniform(0.4, 0.95)
        
        self.add_thought_process(thought, confidence, suggestion_set)

# Example usage and testing
async def test_intelligence_layer():
    """Test the intelligence layer components."""
    print("🧪 Testing GUI Intelligence Layer")
    print("=" * 50)
    
    if not PYSIDE6_AVAILABLE:
        print("⚠️ PySide6 not available - GUI test skipped")
        return
        
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    
    # Create intelligence layer
    intelligence_widget = IntelligenceLayerWidget()
    intelligence_widget.resize(1200, 800)
    intelligence_widget.show()
    
    print("✅ Intelligence Layer created and displayed")
    print("📊 Demo data generation started")
    print("🔄 Live thinking animation active")
    
    # Don't exit immediately in test mode
    # app.exec()

if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        asyncio.run(test_intelligence_layer())
    else:
        print("PySide6 is required to run the Intelligence Layer")
