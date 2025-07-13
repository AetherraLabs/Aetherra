# type: ignore
"""
GUI Intelligence Layer for Lyrixa AI Assistant

Advanced visualization and intelligence features including:
- Memory visualization with context graphs
- Live "Lyrixa Thinks..." pane showing current anticipations
- Interactive timeline with color-coded contexts
- Real-time confidence modeling display
- Workflow state visualization
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

# Check for PySide6 availability
PYSIDE6_AVAILABLE = False
try:
    from PySide6.QtCore import (
        QEasingCurve,
        QParallelAnimationGroup,
        QPropertyAnimation,
        QRect,
        QSequentialAnimationGroup,
        Qt,
        QThread,
        QTimer,
        Signal,
    )
    from PySide6.QtGui import (
        QBrush,
        QColor,
        QFont,
        QIcon,
        QLinearGradient,
        QPainter,
        QPalette,
        QPen,
        QPixmap,
    )
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFrame,
        QGraphicsEllipseItem,
        QGraphicsItem,
        QGraphicsLineItem,
        QGraphicsScene,
        QGraphicsTextItem,
        QGraphicsView,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

if not PYSIDE6_AVAILABLE:
    # Comprehensive mock classes for when PySide6 is not available
    class MockWidget:
        def __init__(self, *args, **kwargs):
            self.progress_bar = self  # For confidence widgets
            
        def __getattr__(self, name):
            return self
            
        def __call__(self, *args, **kwargs):
            return self
            
        def __contains__(self, item):
            return False
            
        def __str__(self):
            return ""
            
        def __int__(self):
            return 0
            
        def __float__(self):
            return 0.0
            
        def __bool__(self):
            return True
            
        def __len__(self):
            return 0

    class MockSignal(MockWidget):
        def __init__(self, *args):
            super().__init__()

    class MockQTimer(MockWidget):
        pass

    class MockQThread(MockWidget):
        pass

    # Base Qt classes
    Qt = type(
        "Qt",
        (),
        {
            "AlignCenter": 4,
            "AlignLeft": 1,
            "AlignRight": 2,
            "Horizontal": 1,
            "Vertical": 2,
            "UserRole": 256,
        },
    )

    QEasingCurve = MockWidget
    QParallelAnimationGroup = MockWidget
    QPropertyAnimation = MockWidget
    QRect = MockWidget
    QSequentialAnimationGroup = MockWidget
    QThread = MockQThread
    QTimer = MockQTimer
    Signal = MockSignal

    # GUI classes
    QBrush = MockWidget
    QColor = MockWidget
    QFont = type("QFont", (MockWidget,), {"Bold": 75})
    QIcon = MockWidget
    QLinearGradient = MockWidget
    QPainter = type("QPainter", (MockWidget,), {"Antialiasing": 1})
    QPalette = MockWidget
    QPen = MockWidget
    QPixmap = MockWidget

    # Widget classes
    QApplication = MockWidget
    QWidget = MockWidget
    QCheckBox = MockWidget
    QComboBox = MockWidget
    QFrame = MockWidget
    QGraphicsEllipseItem = MockWidget
    QGraphicsItem = MockWidget
    QGraphicsLineItem = MockWidget
    QGraphicsScene = MockWidget
    QGraphicsTextItem = MockWidget
    QGraphicsView = type("QGraphicsView", (MockWidget,), {"RubberBandDrag": 1})
    QGroupBox = MockWidget
    QHBoxLayout = MockWidget
    QLabel = MockWidget
    QListWidget = MockWidget
    QListWidgetItem = MockWidget
    QProgressBar = MockWidget
    QPushButton = MockWidget
    QScrollArea = MockWidget
    QSlider = MockWidget
    QSpinBox = MockWidget
    QSplitter = MockWidget
    QTabWidget = MockWidget
    QTextEdit = MockWidget
    QTreeWidget = MockWidget
    QTreeWidgetItem = MockWidget
    QVBoxLayout = MockWidget


@dataclass
class MemoryNode:
    """Represents a memory node in the visualization"""
    id: str
    text: str
    confidence: float
    context: str
    timestamp: datetime
    connections: List[str]
    node_type: str = "memory"


@dataclass
class Connection:
    """Represents a connection between memory nodes"""
    from_node: str
    to_node: str
    strength: float
    connection_type: str = "association"


class NodeType(Enum):
    """Types of memory nodes"""
    MEMORY = "memory"
    CONCEPT = "concept"
    EXPERIENCE = "experience"
    PATTERN = "pattern"
    GOAL = "goal"


class MemoryGraphWidget(QWidget if PYSIDE6_AVAILABLE else MockWidget):  # type: ignore
    """Interactive memory visualization widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = {}  # type: Dict[str, MemoryNode]
        self.connections = []  # type: List[Connection]
        self.node_positions = {}  # type: Dict[str, Tuple[float, float]]
        self.selected_node = None
        self.dragging = False
        self.realtime_updates = True
        self.layout_algorithm = "force_directed"
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()  # type: ignore
        
        # Header with controls
        header_layout = QHBoxLayout()  # type: ignore
        
        header = QLabel("Memory Graph")  # type: ignore
        header.setFont(QFont("Arial", 14, QFont.Bold))  # type: ignore
        
        header_layout.addWidget(header)  # type: ignore
        
        # Real-time updates checkbox
        self.realtime_checkbox = QCheckBox("Real-time updates")  # type: ignore
        self.realtime_checkbox.setChecked(True)  # type: ignore
        self.realtime_checkbox.toggled.connect(self.toggle_realtime)  # type: ignore
        
        header_layout.addWidget(self.realtime_checkbox)  # type: ignore
        
        # Layout algorithm selector
        self.layout_selector = QComboBox()  # type: ignore
        self.layout_selector.addItems(["Force Directed", "Circular", "Hierarchical", "Grid"])  # type: ignore
        self.layout_selector.currentTextChanged.connect(self.change_layout_algorithm)  # type: ignore
        
        header_layout.addWidget(self.layout_selector)  # type: ignore
        
        layout.addLayout(header_layout)  # type: ignore
        
        # Graph view
        self.graph_scene = QGraphicsScene()  # type: ignore
        self.graph_view = QGraphicsView(self.graph_scene)  # type: ignore
        self.graph_view.setScene(self.graph_scene)  # type: ignore
        self.graph_view.setRenderHint(QPainter.Antialiasing)  # type: ignore
        self.graph_view.setDragMode(QGraphicsView.RubberBandDrag)  # type: ignore
        
        layout.addWidget(self.graph_view)  # type: ignore
        
        # Control buttons
        controls_layout = QHBoxLayout()  # type: ignore
        
        self.auto_layout_btn = QPushButton("Auto Layout")  # type: ignore
        self.auto_layout_btn.clicked.connect(self.auto_layout_nodes)  # type: ignore
        
        controls_layout.addWidget(self.auto_layout_btn)  # type: ignore
        
        self.filter_btn = QPushButton("Filter")  # type: ignore
        self.filter_btn.clicked.connect(self.show_filter_dialog)  # type: ignore
        
        controls_layout.addWidget(self.filter_btn)  # type: ignore
        
        self.cluster_btn = QPushButton("Auto Cluster")  # type: ignore
        self.cluster_btn.clicked.connect(self.auto_cluster_nodes)  # type: ignore
        
        controls_layout.addWidget(self.cluster_btn)  # type: ignore
        
        # Zoom controls
        self.zoom_in_btn = QPushButton("Zoom In")  # type: ignore
        self.zoom_in_btn.clicked.connect(lambda: self.graph_view.scale(1.2, 1.2))  # type: ignore
        
        controls_layout.addWidget(self.zoom_in_btn)  # type: ignore
        
        self.zoom_out_btn = QPushButton("Zoom Out")  # type: ignore
        self.zoom_out_btn.clicked.connect(lambda: self.graph_view.scale(0.8, 0.8))  # type: ignore
        
        controls_layout.addWidget(self.zoom_out_btn)  # type: ignore
        
        self.reset_view_btn = QPushButton("Reset View")  # type: ignore
        self.reset_view_btn.clicked.connect(self.reset_view)  # type: ignore
        
        controls_layout.addWidget(self.reset_view_btn)  # type: ignore
        
        layout.addLayout(controls_layout)  # type: ignore
        
        # Info panel
        self.info_panel = QTextEdit()  # type: ignore
        self.info_panel.setMaximumHeight(100)  # type: ignore
        self.info_panel.setPlaceholderText("Select a node to view details...")  # type: ignore
        
        layout.addWidget(self.info_panel)  # type: ignore
        
        self.setLayout(layout)  # type: ignore
        
        # Initialize update timer
        self.update_timer = QTimer()  # type: ignore
        self.update_timer.timeout.connect(self.update_graph_data)  # type: ignore
        self.update_timer.start(1000)  # Update every second
        
    def add_node(self, node: MemoryNode):
        """Add a memory node to the graph"""
        self.nodes[node.id] = node
        if node.id not in self.node_positions:
            # Random initial position
            import random
            self.node_positions[node.id] = (
                random.uniform(50, 500),
                random.uniform(50, 400)
            )
        
        if self.realtime_updates:
            self.update_visualization()
    
    def add_connection(self, connection: Connection):
        """Add a connection between nodes"""
        self.connections.append(connection)
        
        if self.realtime_updates:
            self.update_visualization()
    
    def update_visualization(self):
        """Update the graph visualization"""
        self.graph_scene.clear()  # type: ignore
        
        # Draw nodes
        for node_id, node in self.nodes.items():
            x, y = self.node_positions[node_id]
            self.draw_node(node, x, y)
        
        # Draw connections
        for connection in self.connections:
            if connection.from_node in self.nodes and connection.to_node in self.nodes:
                self.draw_connection(connection)
    
    def draw_node(self, node: MemoryNode, x: float, y: float):
        """Draw a memory node"""
        # Node circle
        radius = 20 + (node.confidence * 30)
        color = QColor("#3498DB")  # type: ignore
        color.setAlpha(int(node.confidence * 255))  # type: ignore
        
        # Create node circle
        self.graph_scene.addEllipse(  # type: ignore
            x - radius, y - radius, radius * 2, radius * 2,
            QPen(QColor("#2C3E50"), 2),  # type: ignore
            QBrush(color),  # type: ignore
        )
        
        # Add text label
        self.graph_scene.addText(  # type: ignore
            node.text[:20] + "..." if len(node.text) > 20 else node.text,
            QFont("Arial", 8),  # type: ignore
        ).setPos(x - radius, y + radius + 5)  # type: ignore
    
    def draw_connection(self, connection: Connection):
        """Draw a connection between nodes"""
        if (connection.from_node not in self.node_positions or 
            connection.to_node not in self.node_positions):
            return
            
        from_x, from_y = self.node_positions[connection.from_node]
        to_x, to_y = self.node_positions[connection.to_node]
        
        # Create connection line
        line = QGraphicsLineItem(from_x, from_y, to_x, to_y)  # type: ignore
        line.setPen(QPen(QColor("#95A5A6"), 2))  # type: ignore
        self.graph_scene.addItem(line)  # type: ignore
        
        # Add strength indicator
        if connection.strength > 0.7:
            line.setPen(QPen(QColor("#27AE60"), 3))  # type: ignore
        elif connection.strength > 0.4:
            line.setPen(QPen(QColor("#F39C12"), 2))  # type: ignore
        else:
            line.setPen(QPen(QColor("#E74C3C"), 1))  # type: ignore
    
    def toggle_realtime(self, checked):
        """Toggle real-time updates"""
        self.realtime_updates = checked
        if checked:
            self.update_timer.start(1000)  # type: ignore
        else:
            self.update_timer.stop()  # type: ignore
    
    def change_layout_algorithm(self, algorithm):
        """Change the layout algorithm"""
        self.layout_algorithm = algorithm.lower().replace(" ", "_")
        self.auto_layout_nodes()
    
    def auto_layout_nodes(self):
        """Automatically layout nodes based on selected algorithm"""
        if not self.nodes:
            return
            
        if self.layout_algorithm == "force_directed":
            self.force_directed_layout()
        elif self.layout_algorithm == "circular":
            self.circular_layout()
        elif self.layout_algorithm == "hierarchical":
            self.hierarchical_layout()
        elif self.layout_algorithm == "grid":
            self.grid_layout()
        
        self.update_visualization()
    
    def force_directed_layout(self):
        """Force-directed layout algorithm"""
        # Simple force-directed algorithm
        import random
        import math
        
        # Reset positions if needed
        if not self.node_positions:
            for node_id in self.nodes:
                self.node_positions[node_id] = (
                    random.uniform(100, 400),
                    random.uniform(100, 300)
                )
        
        # Iterate for layout
        for iteration in range(50):
            forces = {}
            
            # Calculate repulsive forces
            for node_id in self.nodes:
                forces[node_id] = [0, 0]
                
            for node1_id in self.nodes:
                for node2_id in self.nodes:
                    if node1_id != node2_id:
                        x1, y1 = self.node_positions[node1_id]
                        x2, y2 = self.node_positions[node2_id]
                        
                        dx = x1 - x2
                        dy = y1 - y2
                        distance = math.sqrt(dx * dx + dy * dy) + 1
                        
                        force = 1000 / (distance * distance)
                        forces[node1_id][0] += force * dx / distance
                        forces[node1_id][1] += force * dy / distance
            
            # Calculate attractive forces from connections
            for connection in self.connections:
                if (connection.from_node in self.node_positions and 
                    connection.to_node in self.node_positions):
                    
                    x1, y1 = self.node_positions[connection.from_node]
                    x2, y2 = self.node_positions[connection.to_node]
                    
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx * dx + dy * dy) + 1
                    
                    force = distance * 0.1 * connection.strength
                    forces[connection.from_node][0] += force * dx / distance
                    forces[connection.from_node][1] += force * dy / distance
                    forces[connection.to_node][0] -= force * dx / distance
                    forces[connection.to_node][1] -= force * dy / distance
            
            # Apply forces
            for node_id in self.nodes:
                x, y = self.node_positions[node_id]
                fx, fy = forces[node_id]
                
                x += fx * 0.1
                y += fy * 0.1
                
                # Keep nodes within bounds
                x = max(50, min(550, x))
                y = max(50, min(450, y))
                
                self.node_positions[node_id] = (x, y)
    
    def circular_layout(self):
        """Circular layout algorithm"""
        import math
        
        node_ids = list(self.nodes.keys())
        center_x, center_y = 300, 250
        radius = 150
        
        for i, node_id in enumerate(node_ids):
            angle = 2 * math.pi * i / len(node_ids)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[node_id] = (x, y)
    
    def hierarchical_layout(self):
        """Hierarchical layout algorithm"""
        # Simple hierarchical layout based on node types
        node_types = {}
        for node_id, node in self.nodes.items():
            if node.node_type not in node_types:
                node_types[node.node_type] = []
            node_types[node.node_type].append(node_id)
        
        y = 50
        for node_type, node_ids in node_types.items():
            x = 50
            for node_id in node_ids:
                self.node_positions[node_id] = (x, y)
                x += 100
            y += 80
    
    def grid_layout(self):
        """Grid layout algorithm"""
        import math
        
        node_ids = list(self.nodes.keys())
        cols = math.ceil(math.sqrt(len(node_ids)))
        
        for i, node_id in enumerate(node_ids):
            col = i % cols
            row = i // cols
            x = 50 + col * 100
            y = 50 + row * 80
            self.node_positions[node_id] = (x, y)
    
    def show_filter_dialog(self):
        """Show filter dialog"""
        # TODO: Implement filter dialog
        pass
    
    def auto_cluster_nodes(self):
        """Automatically cluster nodes"""
        # TODO: Implement clustering algorithm
        pass
    
    def reset_view(self):
        """Reset the view to default"""
        self.graph_view.resetTransform()  # type: ignore
        self.graph_view.centerOn(0, 0)  # type: ignore
    
    def update_graph_data(self):
        """Update graph data from memory system"""
        # TODO: Connect to actual memory system
        pass


class LiveThinkingPane(QWidget if PYSIDE6_AVAILABLE else MockWidget):  # type: ignore
    """Live thinking visualization pane"""
    
    thought_updated = Signal(dict) if PYSIDE6_AVAILABLE else None  # type: ignore
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_thoughts = []
        self.thinking_animation_timer = QTimer()  # type: ignore
        self.thinking_animation_timer.timeout.connect(self.animate_thinking)  # type: ignore
        self.thinking_animation_timer.start(500)  # Update every 500ms
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()  # type: ignore
        
        # Header
        header_layout = QHBoxLayout()  # type: ignore
        
        self.header_label = QLabel("Lyrixa Thinks...")  # type: ignore
        self.header_label.setFont(QFont("Arial", 14, QFont.Bold))  # type: ignore
        
        header_layout.addWidget(self.header_label)  # type: ignore
        
        self.thinking_indicator = QLabel("●")  # type: ignore
        self.thinking_indicator.setStyleSheet("color: #E74C3C; font-size: 16px;")  # type: ignore
        
        header_layout.addWidget(self.thinking_indicator)  # type: ignore
        
        layout.addLayout(header_layout)  # type: ignore
        
        # Thinking content area
        self.thoughts_area = QTextEdit()  # type: ignore
        self.thoughts_area.setReadOnly(True)  # type: ignore
        self.thoughts_area.setMaximumHeight(150)  # type: ignore
        self.thoughts_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 5px;
                background-color: #F8F9FA;
            }
        """)  # type: ignore
        
        layout.addWidget(self.thoughts_area)  # type: ignore
        
        # Confidence indicators
        confidence_group = QGroupBox("Confidence Levels")  # type: ignore
        confidence_layout = QVBoxLayout()  # type: ignore
        
        self.pattern_confidence = self.create_confidence_widget("Pattern Recognition")
        self.context_confidence = self.create_confidence_widget("Context Understanding")
        self.suggestion_confidence = self.create_confidence_widget("Suggestion Quality")
        
        confidence_layout.addWidget(self.pattern_confidence)  # type: ignore
        confidence_layout.addWidget(self.context_confidence)  # type: ignore
        confidence_layout.addWidget(self.suggestion_confidence)  # type: ignore
        
        confidence_group.setLayout(confidence_layout)  # type: ignore
        layout.addWidget(confidence_group)  # type: ignore
        
        # Anticipations section
        anticipations_group = QGroupBox("Current Anticipations")  # type: ignore
        anticipations_layout = QVBoxLayout()  # type: ignore
        
        self.anticipations_list = QListWidget()  # type: ignore
        self.anticipations_list.setMaximumHeight(120)  # type: ignore
        
        anticipations_layout.addWidget(self.anticipations_list)  # type: ignore
        anticipations_group.setLayout(anticipations_layout)  # type: ignore
        layout.addWidget(anticipations_group)  # type: ignore
        
        self.setLayout(layout)  # type: ignore
        
    def create_confidence_widget(self, label_text):
        """Create a confidence indicator widget"""
        container = QWidget()  # type: ignore
        layout = QHBoxLayout()  # type: ignore
        
        label_widget = QLabel(label_text)  # type: ignore
        label_widget.setFont(QFont("Arial", 9))  # type: ignore
        
        layout.addWidget(label_widget)  # type: ignore
        
        # Progress bar for confidence
        progress = QProgressBar()  # type: ignore
        progress.setRange(0, 100)  # type: ignore
        progress.setValue(0)  # type: ignore
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 3px;
            }
        """)  # type: ignore
        
        layout.addWidget(progress)  # type: ignore
        
        container.setLayout(layout)  # type: ignore
        
        # Add progress bar reference for easy access
        container.progress_bar = progress  # type: ignore
        
        return container
    
    def add_thought(self, thought_text, confidence=0.0, thought_type="general"):
        """Add a new thought to the display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        thought_entry = f"[{timestamp}] {thought_text}"
        
        self.current_thoughts.append({
            "text": thought_entry,
            "confidence": confidence,
            "type": thought_type,
            "timestamp": timestamp
        })
        
        # Keep only last 10 thoughts
        if len(self.current_thoughts) > 10:
            self.current_thoughts.pop(0)
        
        self.update_thoughts_display()
    
    def update_thoughts_display(self):
        """Update the thoughts display area"""
        thoughts_text = "\n".join([thought["text"] for thought in self.current_thoughts])
        self.thoughts_area.setText(thoughts_text)  # type: ignore
        
        # Scroll to bottom
        cursor = self.thoughts_area.textCursor()  # type: ignore
        cursor.movePosition(cursor.End)  # type: ignore
        self.thoughts_area.setTextCursor(cursor)  # type: ignore
    
    def update_confidence(self, pattern_conf=0, context_conf=0, suggestion_conf=0):
        """Update confidence indicators"""
        self.pattern_confidence.progress_bar.setValue(int(pattern_conf))  # type: ignore
        self.context_confidence.progress_bar.setValue(int(context_conf))  # type: ignore
        self.suggestion_confidence.progress_bar.setValue(int(suggestion_conf))  # type: ignore
    
    def animate_thinking(self):
        """Animate the thinking indicator"""
        current_color = self.thinking_indicator.styleSheet()  # type: ignore
        if "#E74C3C" in current_color:
            self.thinking_indicator.setStyleSheet("color: #F39C12; font-size: 16px;")  # type: ignore
        elif "#F39C12" in current_color:
            self.thinking_indicator.setStyleSheet("color: #27AE60; font-size: 16px;")  # type: ignore
        else:
            self.thinking_indicator.setStyleSheet("color: #E74C3C; font-size: 16px;")  # type: ignore
    
    def add_anticipation(self, anticipation_text, confidence=0.0):
        """Add an anticipation to the list"""
        item = QListWidgetItem(f"{anticipation_text} ({confidence:.1%})")  # type: ignore
        
        # Color code by confidence
        if confidence > 0.8:
            item.setForeground(QColor("#27AE60"))  # type: ignore
        elif confidence > 0.5:
            item.setForeground(QColor("#F39C12"))  # type: ignore
        else:
            item.setForeground(QColor("#E74C3C"))  # type: ignore
        
        self.anticipations_list.addItem(item)  # type: ignore
        
        # Keep only last 5 anticipations
        if self.anticipations_list.count() > 5:  # type: ignore
            self.anticipations_list.takeItem(0)  # type: ignore
    
    def clear_anticipations(self):
        """Clear all anticipations"""
        self.anticipations_list.clear()  # type: ignore
    
    def set_thinking_status(self, is_thinking=True):
        """Set the thinking status"""
        if is_thinking:
            self.thinking_animation_timer.start(500)  # type: ignore
        else:
            self.thinking_animation_timer.stop()  # type: ignore
            self.thinking_indicator.setStyleSheet("color: #95A5A6; font-size: 16px;")  # type: ignore


class IntelligenceTimeline(QWidget if PYSIDE6_AVAILABLE else MockWidget):  # type: ignore
    """Interactive timeline showing intelligence events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = []
        self.selected_event = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()  # type: ignore
        
        # Header
        header = QLabel("Intelligence Timeline")  # type: ignore
        header.setFont(QFont("Arial", 14, QFont.Bold))  # type: ignore
        
        layout.addWidget(header)  # type: ignore
        
        # Timeline tree
        self.timeline_tree = QTreeWidget()  # type: ignore
        self.timeline_tree.setHeaderLabels(["Time", "Event", "Context", "Confidence"])  # type: ignore
        self.timeline_tree.itemClicked.connect(self.on_event_selected)  # type: ignore
        
        layout.addWidget(self.timeline_tree)  # type: ignore
        
        # Color legend
        legend_layout = QHBoxLayout()  # type: ignore
        
        legend_items = [
            ("High Confidence", "#27AE60"),
            ("Medium Confidence", "#F39C12"),
            ("Low Confidence", "#E74C3C"),
            ("System Event", "#3498DB")
        ]
        
        for text, color in legend_items:
            label = QLabel(f"● {text}")  # type: ignore
            label.setStyleSheet(f"color: {color}; font-weight: bold;")  # type: ignore
            legend_layout.addWidget(label)  # type: ignore
        
        layout.addLayout(legend_layout)  # type: ignore
        
        self.setLayout(layout)  # type: ignore
        
    def add_event(self, event_type, description, context="", confidence=0.0):
        """Add an event to the timeline"""
        timestamp = datetime.now()
        event_data = {
            "timestamp": timestamp,
            "type": event_type,
            "description": description,
            "context": context,
            "confidence": confidence
        }
        
        self.events.append(event_data)
        self.update_timeline_display()
        
    def update_timeline_display(self):
        """Update the timeline display"""
        self.timeline_tree.clear()  # type: ignore
        
        # Group events by day
        events_by_day = {}
        for event in self.events:
            day_key = event["timestamp"].strftime("%Y-%m-%d")
            if day_key not in events_by_day:
                events_by_day[day_key] = []
            events_by_day[day_key].append(event)
        
        # Add events to tree
        for day, day_events in sorted(events_by_day.items(), reverse=True):
            day_item = QTreeWidgetItem([day, f"{len(day_events)} events", "", ""])  # type: ignore
            
            for event in sorted(day_events, key=lambda x: x["timestamp"], reverse=True):
                event_item = QTreeWidgetItem([  # type: ignore
                    event["timestamp"].strftime("%H:%M:%S"),
                    event["description"],
                    event["context"],
                    f"{event['confidence']:.1%}"
                ])
                
                # Color code by confidence
                if event["confidence"] > 0.8:
                    color = QColor("#27AE60")  # type: ignore
                elif event["confidence"] > 0.5:
                    color = QColor("#F39C12")  # type: ignore
                else:
                    color = QColor("#E74C3C")  # type: ignore
                
                for i in range(4):
                    event_item.setForeground(i, color)  # type: ignore
                
                day_item.addChild(event_item)  # type: ignore
            
            self.timeline_tree.addTopLevelItem(day_item)  # type: ignore
            day_item.setExpanded(True)  # type: ignore
    
    def on_event_selected(self, item, column):
        """Handle event selection"""
        if item.parent():  # Event item (not day item)
            event_text = item.text(1)
            self.selected_event = event_text
            
            # Emit signal if available
            if hasattr(self, 'event_selected'):
                self.event_selected.emit(event_text)  # type: ignore
    
    def clear_events(self):
        """Clear all events"""
        self.events.clear()
        self.timeline_tree.clear()  # type: ignore


class IntelligenceLayer(QWidget if PYSIDE6_AVAILABLE else MockWidget):  # type: ignore
    """Main intelligence layer widget combining all components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()  # type: ignore
        
        # Header
        header_label = QLabel("Intelligence Layer")  # type: ignore
        header_label.setFont(QFont("Arial", 16, QFont.Bold))  # type: ignore
        header_label.setStyleSheet("color: #2C3E50; padding: 10px;")  # type: ignore
        
        layout.addWidget(header_label)  # type: ignore
        
        # Main content area with splitter
        main_splitter = QSplitter(Qt.Horizontal)  # type: ignore
        
        # Left side - Memory graph and thinking pane
        left_widget = QWidget()  # type: ignore
        left_layout = QVBoxLayout()  # type: ignore
        
        # Memory graph
        self.memory_graph = MemoryGraphWidget()
        left_layout.addWidget(self.memory_graph)  # type: ignore
        
        # Live thinking pane
        self.thinking_pane = LiveThinkingPane()
        left_layout.addWidget(self.thinking_pane)  # type: ignore
        
        left_widget.setLayout(left_layout)  # type: ignore
        main_splitter.addWidget(left_widget)  # type: ignore
        
        # Right side - Timeline
        self.timeline = IntelligenceTimeline()
        main_splitter.addWidget(self.timeline)  # type: ignore
        
        # Set splitter proportions
        main_splitter.setSizes([400, 200])  # type: ignore
        
        layout.addWidget(main_splitter)  # type: ignore
        
        self.setLayout(layout)  # type: ignore
        
    def add_memory_node(self, node_id, text, confidence=0.0, context="", connections=None):
        """Add a memory node to the graph"""
        if connections is None:
            connections = []
            
        node = MemoryNode(
            id=node_id,
            text=text,
            confidence=confidence,
            context=context,
            timestamp=datetime.now(),
            connections=connections
        )
        
        self.memory_graph.add_node(node)
        
        # Add timeline event
        self.timeline.add_event(
            "Memory Created",
            f"New memory: {text[:50]}...",
            context,
            confidence
        )
        
        # Add thinking event
        self.thinking_pane.add_thought(
            f"Created memory: {text[:30]}...",
            confidence,
            "memory"
        )
    
    def add_memory_connection(self, from_node, to_node, strength=0.5):
        """Add a connection between memory nodes"""
        connection = Connection(
            from_node=from_node,
            to_node=to_node,
            strength=strength
        )
        
        self.memory_graph.add_connection(connection)
        
        # Add timeline event
        self.timeline.add_event(
            "Connection Created",
            f"Connected {from_node} → {to_node}",
            f"Strength: {strength:.1%}",
            strength
        )
    
    def update_thinking_status(self, thought_text, confidence=0.0):
        """Update the thinking status"""
        self.thinking_pane.add_thought(thought_text, confidence)
        
        # Update confidence indicators
        self.thinking_pane.update_confidence(
            pattern_conf=min(100, confidence * 120),
            context_conf=min(100, confidence * 100),
            suggestion_conf=min(100, confidence * 80)
        )
    
    def add_anticipation(self, anticipation_text, confidence=0.0):
        """Add an anticipation"""
        self.thinking_pane.add_anticipation(anticipation_text, confidence)
        
        # Add timeline event
        self.timeline.add_event(
            "Anticipation",
            anticipation_text,
            "Future prediction",
            confidence
        )
    
    def set_thinking_active(self, is_active=True):
        """Set thinking animation active/inactive"""
        self.thinking_pane.set_thinking_status(is_active)


# Demo function
def demo_intelligence_layer():
    """Demonstrate the intelligence layer functionality"""
    if PYSIDE6_AVAILABLE:
        app = QApplication([])  # type: ignore
        
        # Create main window
        window = IntelligenceLayer()
        window.setWindowTitle("Lyrixa Intelligence Layer")  # type: ignore
        window.resize(1200, 800)  # type: ignore
        
        # Add demo data
        window.add_memory_node(
            "mem1",
            "User asked about Python functions",
            0.8,
            "Programming context",
            ["mem2", "mem3"]
        )
        
        window.add_memory_node(
            "mem2",
            "Functions are reusable code blocks",
            0.9,
            "Programming context",
            ["mem1"]
        )
        
        window.add_memory_node(
            "mem3",
            "Python uses def keyword for functions",
            0.7,
            "Programming context",
            ["mem1", "mem2"]
        )
        
        window.add_memory_connection("mem1", "mem2", 0.8)
        window.add_memory_connection("mem1", "mem3", 0.6)
        window.add_memory_connection("mem2", "mem3", 0.9)
        
        # Add some thinking updates
        window.update_thinking_status("Analyzing user query about functions", 0.7)
        window.update_thinking_status("Retrieving relevant programming concepts", 0.8)
        window.update_thinking_status("Formulating comprehensive response", 0.9)
        
        # Add anticipations
        window.add_anticipation("User might ask about function parameters", 0.6)
        window.add_anticipation("User might want to see examples", 0.8)
        window.add_anticipation("User might ask about return values", 0.5)
        
        # Set thinking active
        window.set_thinking_active(True)
        
        window.show()  # type: ignore
        app.exec()  # type: ignore
    else:
        print("PySide6 not available. Intelligence layer would run in headless mode.")


if __name__ == "__main__":
    demo_intelligence_layer()
