"""
DEPRECATED: world_class_memory_core.py is now an adapter for QuantumEnhancedMemoryEngine.
All memory operations are delegated to the canonical engine.
"""

from ..memory.QuantumEnhancedMemoryEngine.engine import QuantumEnhancedMemoryEngine


class WorldClassMemoryCore:
    def __init__(self, *args, **kwargs):
        self.engine = QuantumEnhancedMemoryEngine()

    def store(self, memory_entry: dict) -> dict:
        return self.engine.store(memory_entry)

    def retrieve(self, query: str, context: dict = None) -> dict:
        return self.engine.retrieve(query, context)

    content: str
    timestamp: datetime
    memory_type: str = "general"  # general, goal, insight, experience, knowledge
    importance: float = 0.5  # 0.0 to 1.0
    confidence: float = 0.8  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)  # Connected memory IDs
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    embedding: List[float] = field(default_factory=list)  # For similarity search
    cluster_id: Optional[str] = None
    relevance_score: float = 0.0  # For goal relevance


@dataclass
class MemoryCluster:
    """Memory cluster for visualization"""

    id: str
    name: str
    center: Tuple[float, float]
    memories: List[str]  # Memory IDs
    color: str
    size: float
    coherence: float  # How well memories fit together


@dataclass
class Goal:
    """Goal for memory relevance"""

    id: str
    description: str
    priority: float = 0.5
    status: str = "active"
    created: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


class MemoryGraphNode(QGraphicsEllipseItem):
    """Interactive memory node for graph visualization"""

    def __init__(self, memory: Memory, x: float, y: float, radius: float = 20):
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.memory = memory
        self.radius = radius
        self.graph_view = None  # Will be set by parent
        self.setPos(x, y)

        # Visual styling based on memory properties
        self.update_appearance()

        # Make interactive
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Tooltip
        self.setToolTip(f"{memory.memory_type.title()}: {memory.content[:100]}...")

        # Text label
        self.text_item = QGraphicsTextItem(memory.content[:15] + "...", self)
        self.text_item.setPos(-50, radius + 5)
        self.text_item.setFont(QFont("Arial", 8))

    def update_appearance(self):
        """Update node appearance based on memory properties"""
        # Color based on type
        type_colors = {
            "general": "#87CEEB",  # Sky blue
            "goal": "#FFD700",  # Gold
            "insight": "#FF69B4",  # Hot pink
            "experience": "#90EE90",  # Light green
            "knowledge": "#DDA0DD",  # Plum
        }

        base_color = type_colors.get(self.memory.memory_type, "#87CEEB")

        # Intensity based on importance
        alpha = int(128 + (self.memory.importance * 127))
        color = QColor(base_color)
        color.setAlpha(alpha)

        # Border based on confidence
        border_width = 1 + (self.memory.confidence * 3)
        border_color = QColor("#2F4F4F")

        self.setBrush(QBrush(color))
        self.setPen(QPen(border_color, border_width))

        # Size based on access count
        scale = 0.8 + (min(self.memory.access_count, 10) * 0.02)
        self.setScale(scale)

    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        super().mousePressEvent(event)
        if self.graph_view:
            self.graph_view.memory_selected.emit(self.memory)


class MemoryConnection(QGraphicsLineItem):
    """Connection line between memory nodes"""

    def __init__(
        self,
        start_node: MemoryGraphNode,
        end_node: MemoryGraphNode,
        strength: float = 0.5,
    ):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.strength = strength
        self.update_line()

        # Visual styling
        alpha = int(50 + (strength * 150))
        color = QColor("#696969")
        color.setAlpha(alpha)

        width = 1 + (strength * 2)
        self.setPen(QPen(color, width))

    def update_line(self):
        """Update line position based on node positions"""
        start_pos = self.start_node.pos()
        end_pos = self.end_node.pos()
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())


class MemoryGraphView(QGraphicsView):
    """Interactive memory graph visualization"""

    memory_selected = Signal(Memory)
    memories_connected = Signal(str, str)  # memory_id1, memory_id2

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Setup view
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMinimumSize(400, 300)

        # Memory nodes and connections
        self.memory_nodes = {}  # memory_id -> MemoryGraphNode
        self.connections = []  # List of MemoryConnection

        # Layout parameters
        self.center_x = 0
        self.center_y = 0
        self.radius_multiplier = 100

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_memory_node(self, memory: Memory):
        """Add a memory node to the graph"""
        # Calculate position (simple circular layout for now)
        angle = len(self.memory_nodes) * (
            2 * math.pi / max(len(self.memory_nodes) + 1, 8)
        )
        x = self.center_x + math.cos(angle) * self.radius_multiplier
        y = self.center_y + math.sin(angle) * self.radius_multiplier

        # Create node
        node = MemoryGraphNode(memory, x, y)
        node.graph_view = self  # Set reference for signal emission
        self.memory_nodes[memory.id] = node
        scene = self.scene()
        scene.addItem(node)

        return node

    def add_connection(self, memory_id1: str, memory_id2: str, strength: float = 0.5):
        """Add connection between memory nodes"""
        if memory_id1 in self.memory_nodes and memory_id2 in self.memory_nodes:
            node1 = self.memory_nodes[memory_id1]
            node2 = self.memory_nodes[memory_id2]

            connection = MemoryConnection(node1, node2, strength)
            self.connections.append(connection)
            self.scene.addItem(connection)

    def cluster_layout(self, clusters: List[MemoryCluster]):
        """Arrange nodes in clusters"""
        self.scene.clear()
        self.memory_nodes.clear()
        self.connections.clear()

        # Position clusters
        cluster_positions = {}
        for i, cluster in enumerate(clusters):
            angle = i * (2 * math.pi / len(clusters))
            cluster_x = math.cos(angle) * 200
            cluster_y = math.sin(angle) * 200
            cluster_positions[cluster.id] = (cluster_x, cluster_y)

        # Add cluster backgrounds
        for cluster in clusters:
            cx, cy = cluster_positions[cluster.id]
            cluster_radius = 80 + (cluster.size * 20)

            # Create cluster background
            cluster_bg = QGraphicsEllipseItem(
                -cluster_radius, -cluster_radius, cluster_radius * 2, cluster_radius * 2
            )
            cluster_bg.setPos(cx, cy)
            cluster_bg.setBrush(QBrush(QColor(cluster.color).lighter(150)))
            cluster_bg.setPen(QPen(QColor(cluster.color), 2))
            cluster_bg.setOpacity(0.3)
            self.scene.addItem(cluster_bg)

            # Add cluster label
            label = QGraphicsTextItem(cluster.name)
            label.setPos(cx - 30, cy - cluster_radius - 20)
            label.setFont(QFont("Arial", 10, QFont.Bold))
            self.scene.addItem(label)

    def on_node_selected(self, memory: Memory):
        """Handle node selection"""
        self.memory_selected.emit(memory)

    def show_context_menu(self, position):
        """Show context menu for graph operations"""
        menu = QMenu(self)

        # Add actions
        cluster_action = QAction("Auto-cluster memories", self)
        cluster_action.triggered.connect(self.auto_cluster)
        menu.addAction(cluster_action)

        layout_action = QAction("Reorganize layout", self)
        layout_action.triggered.connect(self.reorganize_layout)
        menu.addAction(layout_action)

        menu.exec(self.mapToGlobal(position))

    def auto_cluster(self):
        """Auto-cluster memories based on similarity"""
        # This would use embedding similarity in real implementation
        print("Auto-clustering memories...")

    def reorganize_layout(self):
        """Reorganize the graph layout"""
        print("Reorganizing layout...")

    def highlight_relevant_memories(self, memory_ids: List[str]):
        """Highlight memories relevant to current goal"""
        # Reset all nodes
        for node in self.memory_nodes.values():
            node.setOpacity(0.3)

        # Highlight relevant nodes
        for memory_id in memory_ids:
            if memory_id in self.memory_nodes:
                node = self.memory_nodes[memory_id]
                node.setOpacity(1.0)

                # Add glow effect
                glow_color = QColor("#FFD700")
                glow_pen = QPen(glow_color, 4)
                node.setPen(glow_pen)


class MemorySearchWidget(QWidget):
    """Advanced memory search with filters and sorting"""

    search_performed = Signal(str, dict)  # query, filters
    memory_selected = Signal(Memory)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize search UI"""
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search memories, tags, or content...")
        self.search_input.textChanged.connect(self.on_search_changed)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        # Filters
        filters_group = QGroupBox("🔧 Filters")
        filters_layout = QHBoxLayout(filters_group)

        # Memory type filter
        self.type_filter = QComboBox()
        self.type_filter.addItems(
            ["All Types", "General", "Goal", "Insight", "Experience", "Knowledge"]
        )

        # Importance filter
        self.importance_filter = QSlider(Qt.Horizontal)
        self.importance_filter.setRange(0, 100)
        self.importance_filter.setValue(0)
        self.importance_filter.setToolTip("Minimum importance level")

        # Time filter
        self.time_filter = QComboBox()
        self.time_filter.addItems(
            ["All Time", "Last Hour", "Last Day", "Last Week", "Last Month"]
        )

        # Sort options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            ["Relevance", "Newest", "Oldest", "Most Important", "Most Accessed"]
        )

        filters_layout.addWidget(QLabel("Type:"))
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(QLabel("Importance:"))
        filters_layout.addWidget(self.importance_filter)
        filters_layout.addWidget(QLabel("Time:"))
        filters_layout.addWidget(self.time_filter)
        filters_layout.addWidget(QLabel("Sort:"))
        filters_layout.addWidget(self.sort_combo)

        layout.addWidget(filters_group)

        # Results
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_result_selected)
        layout.addWidget(self.results_list)

        # Search stats
        self.stats_label = QLabel("Ready to search...")
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def on_search_changed(self):
        """Handle search input changes"""
        if len(self.search_input.text()) > 2:
            QTimer.singleShot(300, self.perform_search)  # Debounced search

    def perform_search(self):
        """Perform memory search"""
        query = self.search_input.text().strip()

        filters = {
            "type": self.type_filter.currentText(),
            "importance": self.importance_filter.value() / 100.0,
            "time": self.time_filter.currentText(),
            "sort": self.sort_combo.currentText(),
        }

        self.search_performed.emit(query, filters)

    def update_results(self, memories: List[Memory]):
        """Update search results"""
        self.results_list.clear()

        for memory in memories:
            item = QListWidgetItem()

            # Format result
            type_icon = {
                "general": "💭",
                "goal": "🎯",
                "insight": "💡",
                "experience": "🔥",
                "knowledge": "📚",
            }.get(memory.memory_type, "💭")

            importance_stars = "⭐" * int(memory.importance * 5)

            item.setText(f"{type_icon} {memory.content[:80]}...")
            item.setData(Qt.UserRole, memory)

            # Add tooltip with details
            tooltip = f"""
Type: {memory.memory_type.title()}
Importance: {importance_stars}
Confidence: {memory.confidence:.1%}
Created: {memory.timestamp.strftime("%Y-%m-%d %H:%M")}
Tags: {", ".join(memory.tags) if memory.tags else "None"}
Access Count: {memory.access_count}
"""
            item.setToolTip(tooltip)

            self.results_list.addItem(item)

        # Update stats
        self.stats_label.setText(f"Found {len(memories)} memories")

    def on_result_selected(self, item):
        """Handle result selection"""
        memory = item.data(Qt.UserRole)
        if memory:
            self.memory_selected.emit(memory)


class MemoryInjectionDialog(QDialog):
    """Dialog for injecting new memories"""

    memory_created = Signal(Memory)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💉 Inject New Memory")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize injection dialog UI"""
        layout = QVBoxLayout()

        # Content input
        content_group = QGroupBox("📝 Memory Content")
        content_layout = QVBoxLayout(content_group)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText(
            "Enter the memory content, insight, or knowledge..."
        )
        content_layout.addWidget(self.content_input)

        layout.addWidget(content_group)

        # Memory properties
        props_group = QGroupBox("⚙️ Memory Properties")
        props_layout = QVBoxLayout(props_group)

        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(
            ["general", "goal", "insight", "experience", "knowledge"]
        )
        type_layout.addWidget(self.type_combo)
        props_layout.addLayout(type_layout)

        # Importance slider
        importance_layout = QHBoxLayout()
        importance_layout.addWidget(QLabel("Importance:"))
        self.importance_slider = QSlider(Qt.Horizontal)
        self.importance_slider.setRange(0, 100)
        self.importance_slider.setValue(50)
        self.importance_label = QLabel("50%")
        self.importance_slider.valueChanged.connect(
            lambda v: self.importance_label.setText(f"{v}%")
        )
        importance_layout.addWidget(self.importance_slider)
        importance_layout.addWidget(self.importance_label)
        props_layout.addLayout(importance_layout)

        # Confidence slider
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(80)
        self.confidence_label = QLabel("80%")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v}%")
        )
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        props_layout.addLayout(confidence_layout)

        # Tags input
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3...")
        tags_layout.addWidget(self.tags_input)
        props_layout.addLayout(tags_layout)

        layout.addWidget(props_group)

        # Context linking
        context_group = QGroupBox("🔗 Context Linking")
        context_layout = QVBoxLayout(context_group)

        # Auto-link checkbox
        self.auto_link_cb = QCheckBox("Auto-link to similar memories")
        self.auto_link_cb.setChecked(True)
        context_layout.addWidget(self.auto_link_cb)

        # Goal relevance
        self.goal_relevance_cb = QCheckBox("Link to current active goals")
        self.goal_relevance_cb.setChecked(True)
        context_layout.addWidget(self.goal_relevance_cb)

        layout.addWidget(context_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_memory_data(self) -> Dict[str, Any]:
        """Get memory data from form"""
        return {
            "content": self.content_input.toPlainText(),
            "memory_type": self.type_combo.currentText(),
            "importance": self.importance_slider.value() / 100.0,
            "confidence": self.confidence_slider.value() / 100.0,
            "tags": [
                tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()
            ],
            "auto_link": self.auto_link_cb.isChecked(),
            "goal_relevance": self.goal_relevance_cb.isChecked(),
        }


class WorldClassMemoryCore(QWidget):
    """World-class interactive memory management system"""

    def __init__(self, memory_manager=None):
        super().__init__()
        self.memory_manager = memory_manager
        self.memories = {}  # memory_id -> Memory
        self.clusters = []  # List of MemoryCluster
        self.current_goals = []  # List of Goal

        # Apply Aetherra dark theme
        self.setStyleSheet("""
            /* === AETHERRA DARK THEME === */
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #0d0d0d, stop:1 #0a0a0a);
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            }

            QTabWidget::pane {
                border: 1px solid rgba(0, 255, 136, 0.3);
                background: #0f0f0f;
            }

            QTabBar::tab {
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: rgba(0, 255, 136, 0.3);
                border: 2px solid #00ff88;
            }

            QLineEdit {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
            }

            QLineEdit:focus {
                border: 2px solid #00ff88;
            }

            QTextEdit {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
            }

            QListWidget {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
            }

            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(0, 255, 136, 0.1);
            }

            QListWidget::item:selected {
                background: rgba(0, 255, 136, 0.2);
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.3), stop:1 rgba(0, 255, 136, 0.1));
                border: 1px solid #00ff88;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 10px 20px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.7));
                color: #000000;
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.8);
                color: #000000;
            }

            QLabel {
                color: #ffffff;
                font-weight: bold;
            }

            QComboBox {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
            }

            QComboBox::drop-down {
                border: none;
                background: rgba(0, 255, 136, 0.2);
            }

            QComboBox::down-arrow {
                border: none;
                background: #00ff88;
            }

            QGroupBox {
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #00ff88;
            }

            QGroupBox::title {
                color: #00ff88;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QGraphicsView {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
            }

            QSlider::groove:horizontal {
                border: 1px solid rgba(0, 255, 136, 0.3);
                background: #0a0a0a;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #00ff88;
                border: 1px solid rgba(0, 255, 136, 0.5);
                width: 18px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 3px;
            }

            QSlider::handle:horizontal:hover {
                background: rgba(0, 255, 136, 0.8);
            }
        """)

        # Initialize with sample data
        self.initialize_sample_data()

        self.init_ui()
        self.setup_connections()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_memory_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def init_ui(self):
        """Initialize the world-class UI"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🧠 World-Class Memory Core")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")

        # Memory stats
        self.stats_label = QLabel(
            f"📊 {len(self.memories)} memories • {len(self.clusters)} clusters"
        )
        self.stats_label.setStyleSheet("font-size: 12px; color: #ffffff;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)

        layout.addLayout(header_layout)

        # Main content tabs
        self.tabs = QTabWidget()

        # Memory Graph tab
        self.setup_graph_tab()

        # Memory Search tab
        self.setup_search_tab()

        # Memory Analytics tab
        self.setup_analytics_tab()

        # Memory Management tab
        self.setup_management_tab()

        layout.addWidget(self.tabs)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.inject_btn = QPushButton("💉 Inject Memory")
        self.inject_btn.clicked.connect(self.inject_memory)

        self.relevant_btn = QPushButton("🎯 Show Relevant to Goal")
        self.relevant_btn.clicked.connect(self.show_relevant_memories)

        self.cluster_btn = QPushButton("🔄 Auto-Cluster")
        self.cluster_btn.clicked.connect(self.auto_cluster_memories)

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_memories)

        actions_layout.addWidget(self.inject_btn)
        actions_layout.addWidget(self.relevant_btn)
        actions_layout.addWidget(self.cluster_btn)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # Status bar
        self.status_label = QLabel("Ready • Interactive memory management active")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def setup_graph_tab(self):
        """Setup memory graph visualization tab"""
        graph_widget = QWidget()
        layout = QVBoxLayout(graph_widget)

        # Graph controls
        controls_layout = QHBoxLayout()

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(
            ["Circular", "Clustered", "Force-directed", "Hierarchical"]
        )
        self.layout_combo.currentTextChanged.connect(self.change_graph_layout)

        self.show_connections_cb = QCheckBox("Show Connections")
        self.show_connections_cb.setChecked(True)

        self.filter_importance_slider = QSlider(Qt.Horizontal)
        self.filter_importance_slider.setRange(0, 100)
        self.filter_importance_slider.setValue(0)
        self.filter_importance_slider.valueChanged.connect(self.filter_by_importance)

        controls_layout.addWidget(QLabel("Layout:"))
        controls_layout.addWidget(self.layout_combo)
        controls_layout.addWidget(self.show_connections_cb)
        controls_layout.addWidget(QLabel("Min Importance:"))
        controls_layout.addWidget(self.filter_importance_slider)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Memory graph
        self.memory_graph = MemoryGraphView()
        layout.addWidget(self.memory_graph)

        # Memory details panel
        details_group = QGroupBox("📋 Memory Details")
        details_layout = QVBoxLayout(details_group)

        self.memory_details = QTextEdit()
        self.memory_details.setReadOnly(True)
        self.memory_details.setMaximumHeight(150)
        details_layout.addWidget(self.memory_details)

        layout.addWidget(details_group)

        self.tabs.addTab(graph_widget, "🌐 Memory Graph")

        # Populate graph
        self.populate_memory_graph()

    def setup_search_tab(self):
        """Setup memory search tab"""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)

        # Search widget
        self.search_widget = MemorySearchWidget()
        layout.addWidget(self.search_widget)

        self.tabs.addTab(search_widget, "🔍 Memory Search")

    def setup_analytics_tab(self):
        """Setup memory analytics tab"""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)

        # Analytics summary
        summary_group = QGroupBox("📊 Memory Analytics")
        summary_layout = QVBoxLayout(summary_group)

        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        self.update_analytics()
        summary_layout.addWidget(self.analytics_text)

        layout.addWidget(summary_group)

        # Memory timeline
        timeline_group = QGroupBox("📈 Memory Timeline")
        timeline_layout = QVBoxLayout(timeline_group)

        self.timeline_widget = QTextEdit()
        self.timeline_widget.setReadOnly(True)
        self.update_timeline()
        timeline_layout.addWidget(self.timeline_widget)

        layout.addWidget(timeline_group)

        self.tabs.addTab(analytics_widget, "📊 Analytics")

    def setup_management_tab(self):
        """Setup memory management tab"""
        management_widget = QWidget()
        layout = QVBoxLayout(management_widget)

        # Memory list
        memories_group = QGroupBox("📚 All Memories")
        memories_layout = QVBoxLayout(memories_group)

        # Memory table
        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(6)
        self.memory_table.setHorizontalHeaderLabels(
            ["Type", "Content", "Importance", "Confidence", "Created", "Actions"]
        )
        self.memory_table.horizontalHeader().setStretchLastSection(True)

        self.populate_memory_table()
        memories_layout.addWidget(self.memory_table)

        layout.addWidget(memories_group)

        # Cluster management
        clusters_group = QGroupBox("🎯 Memory Clusters")
        clusters_layout = QVBoxLayout(clusters_group)

        self.clusters_list = QListWidget()
        self.populate_clusters_list()
        clusters_layout.addWidget(self.clusters_list)

        layout.addWidget(clusters_group)

        self.tabs.addTab(management_widget, "⚙️ Management")

    def setup_connections(self):
        """Setup signal connections"""
        # Memory graph connections
        self.memory_graph.memory_selected.connect(self.on_memory_selected)

        # Search widget connections
        self.search_widget.search_performed.connect(self.perform_memory_search)
        self.search_widget.memory_selected.connect(self.on_memory_selected)

    def initialize_sample_data(self):
        """Initialize with sample memory data"""
        # Sample memories
        sample_memories = [
            {
                "content": "Learned that regular exercise improves cognitive function and memory retention",
                "memory_type": "knowledge",
                "importance": 0.8,
                "tags": ["health", "cognitive", "exercise"],
                "timestamp": datetime.now() - timedelta(days=2),
            },
            {
                "content": "Goal: Complete the AI memory system by end of week",
                "memory_type": "goal",
                "importance": 0.9,
                "tags": ["work", "ai", "deadline"],
                "timestamp": datetime.now() - timedelta(days=1),
            },
            {
                "content": "Had insight about using graph visualization for memory connections",
                "memory_type": "insight",
                "importance": 0.7,
                "tags": ["visualization", "memory", "graph"],
                "timestamp": datetime.now() - timedelta(hours=3),
            },
            {
                "content": "Experienced breakthrough in understanding memory clustering algorithms",
                "memory_type": "experience",
                "importance": 0.6,
                "tags": ["algorithm", "clustering", "breakthrough"],
                "timestamp": datetime.now() - timedelta(hours=1),
            },
            {
                "content": "Remember to follow up with team about project timeline",
                "memory_type": "general",
                "importance": 0.5,
                "tags": ["team", "timeline", "followup"],
                "timestamp": datetime.now() - timedelta(minutes=30),
            },
        ]

        # Create memory objects
        for i, mem_data in enumerate(sample_memories):
            memory = Memory(
                id=f"mem_{i + 1}",
                content=mem_data["content"],
                memory_type=mem_data["memory_type"],
                importance=mem_data["importance"],
                tags=mem_data["tags"],
                timestamp=mem_data["timestamp"],
                confidence=0.8,
                access_count=random.randint(0, 10),
            )
            self.memories[memory.id] = memory

        # Create sample clusters
        self.clusters = [
            MemoryCluster(
                id="cluster_1",
                name="Work & Goals",
                center=(0, 0),
                memories=["mem_2", "mem_5"],
                color="#FFD700",
                size=0.8,
                coherence=0.7,
            ),
            MemoryCluster(
                id="cluster_2",
                name="Learning & Knowledge",
                center=(100, 100),
                memories=["mem_1", "mem_3"],
                color="#87CEEB",
                size=0.6,
                coherence=0.8,
            ),
            MemoryCluster(
                id="cluster_3",
                name="Insights & Experiences",
                center=(-100, 100),
                memories=["mem_3", "mem_4"],
                color="#FF69B4",
                size=0.7,
                coherence=0.6,
            ),
        ]

        # Sample goals
        self.current_goals = [
            Goal(
                id="goal_1",
                description="Complete AI memory system implementation",
                priority=0.9,
                status="active",
            ),
            Goal(
                id="goal_2",
                description="Improve memory clustering algorithms",
                priority=0.7,
                status="active",
            ),
        ]

    def populate_memory_graph(self):
        """Populate the memory graph with current memories"""
        # Clear existing graph
        self.memory_graph.scene.clear()
        self.memory_graph.memory_nodes.clear()
        self.memory_graph.connections.clear()

        # Add memory nodes
        for memory in self.memories.values():
            self.memory_graph.add_memory_node(memory)

        # Add connections based on memory relationships
        for memory in self.memories.values():
            for connected_id in memory.connections:
                if connected_id in self.memories:
                    self.memory_graph.add_connection(memory.id, connected_id)

    def populate_memory_table(self):
        """Populate the memory management table"""
        self.memory_table.setRowCount(len(self.memories))

        for row, memory in enumerate(self.memories.values()):
            # Type
            type_item = QTableWidgetItem(memory.memory_type.title())
            self.memory_table.setItem(row, 0, type_item)

            # Content (truncated)
            content_item = QTableWidgetItem(memory.content[:50] + "...")
            self.memory_table.setItem(row, 1, content_item)

            # Importance
            importance_item = QTableWidgetItem(f"{memory.importance:.1%}")
            self.memory_table.setItem(row, 2, importance_item)

            # Confidence
            confidence_item = QTableWidgetItem(f"{memory.confidence:.1%}")
            self.memory_table.setItem(row, 3, confidence_item)

            # Created
            created_item = QTableWidgetItem(memory.timestamp.strftime("%Y-%m-%d %H:%M"))
            self.memory_table.setItem(row, 4, created_item)

            # Actions
            actions_item = QTableWidgetItem("Edit • Delete • Connect")
            self.memory_table.setItem(row, 5, actions_item)

    def populate_clusters_list(self):
        """Populate the clusters list"""
        self.clusters_list.clear()

        for cluster in self.clusters:
            item = QListWidgetItem(
                f"🎯 {cluster.name} ({len(cluster.memories)} memories)"
            )
            item.setData(Qt.UserRole, cluster)
            self.clusters_list.addItem(item)

    def update_analytics(self):
        """Update memory analytics display"""
        total_memories = len(self.memories)

        # Type distribution
        type_counts = {}
        importance_sum = 0
        confidence_sum = 0

        for memory in self.memories.values():
            type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1
            importance_sum += memory.importance
            confidence_sum += memory.confidence

        avg_importance = importance_sum / total_memories if total_memories > 0 else 0
        avg_confidence = confidence_sum / total_memories if total_memories > 0 else 0

        analytics_text = f"""
📊 Memory Analytics Summary
===========================

Total Memories: {total_memories}
Active Clusters: {len(self.clusters)}
Average Importance: {avg_importance:.1%}
Average Confidence: {avg_confidence:.1%}

Memory Type Distribution:
{chr(10).join([f"  {mtype.title()}: {count} ({count / total_memories:.1%})" for mtype, count in type_counts.items()])}

Most Accessed Memories:
{chr(10).join([f"  • {mem.content[:50]}... (accessed {mem.access_count} times)" for mem in sorted(self.memories.values(), key=lambda m: m.access_count, reverse=True)[:3]])}

Recent Activity:
{chr(10).join([f"  • {mem.timestamp.strftime('%H:%M')} - {mem.content[:40]}..." for mem in sorted(self.memories.values(), key=lambda m: m.timestamp, reverse=True)[:3]])}
"""

        self.analytics_text.setPlainText(analytics_text)

    def update_timeline(self):
        """Update memory timeline"""
        sorted_memories = sorted(
            self.memories.values(), key=lambda m: m.timestamp, reverse=True
        )

        timeline_text = "📈 Memory Timeline\n" + "=" * 20 + "\n\n"

        for memory in sorted_memories:
            type_icon = {
                "general": "💭",
                "goal": "🎯",
                "insight": "💡",
                "experience": "🔥",
                "knowledge": "📚",
            }.get(memory.memory_type, "💭")

            timeline_text += f"{memory.timestamp.strftime('%Y-%m-%d %H:%M')} {type_icon} {memory.content[:80]}...\n"

        self.timeline_widget.setPlainText(timeline_text)

    def inject_memory(self):
        """Open memory injection dialog"""
        dialog = MemoryInjectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            memory_data = dialog.get_memory_data()
            self.create_memory_from_data(memory_data)

    def create_memory_from_data(self, data: Dict[str, Any]):
        """Create new memory from injection data"""
        memory_id = f"mem_{len(self.memories) + 1}"

        memory = Memory(
            id=memory_id,
            content=data["content"],
            memory_type=data["memory_type"],
            importance=data["importance"],
            confidence=data["confidence"],
            tags=data["tags"],
            timestamp=datetime.now(),
            access_count=0,
        )

        self.memories[memory_id] = memory

        # Auto-link if requested
        if data["auto_link"]:
            self.auto_link_memory(memory)

        # Link to goals if requested
        if data["goal_relevance"]:
            self.link_to_goals(memory)

        # Refresh UI
        self.refresh_ui()

        self.status_label.setText(f"✅ Memory injected: {memory.content[:50]}...")

    def auto_link_memory(self, memory: Memory):
        """Auto-link memory to similar memories"""
        # Simple similarity based on tags and content
        for other_memory in self.memories.values():
            if other_memory.id != memory.id:
                # Check tag overlap
                tag_overlap = set(memory.tags) & set(other_memory.tags)
                if tag_overlap:
                    memory.connections.append(other_memory.id)
                    other_memory.connections.append(memory.id)

    def link_to_goals(self, memory: Memory):
        """Link memory to relevant goals"""
        for goal in self.current_goals:
            if goal.status == "active":
                # Simple keyword matching
                goal_keywords = goal.description.lower().split()
                memory_keywords = memory.content.lower().split()

                if any(keyword in memory_keywords for keyword in goal_keywords):
                    memory.context["linked_goals"] = memory.context.get(
                        "linked_goals", []
                    )
                    memory.context["linked_goals"].append(goal.id)

    def show_relevant_memories(self):
        """Show memories most relevant to current goal"""
        if not self.current_goals:
            QMessageBox.information(
                self, "No Goals", "No active goals found to show relevant memories."
            )
            return

        # Get current goal (highest priority active goal)
        current_goal = max(
            [g for g in self.current_goals if g.status == "active"],
            key=lambda g: g.priority,
            default=None,
        )

        if not current_goal:
            return

        # Calculate relevance scores
        relevant_memories = []

        for memory in self.memories.values():
            relevance = self.calculate_goal_relevance(memory, current_goal)
            if relevance > 0.3:  # Threshold for relevance
                memory.relevance_score = relevance
                relevant_memories.append(memory)

        # Sort by relevance
        relevant_memories.sort(key=lambda m: m.relevance_score, reverse=True)

        # Update search results
        self.search_widget.update_results(relevant_memories[:10])  # Top 10

        # Switch to search tab
        self.tabs.setCurrentIndex(1)

        # Highlight in graph
        relevant_ids = [m.id for m in relevant_memories]
        self.memory_graph.highlight_relevant_memories(relevant_ids)

        self.status_label.setText(
            f"🎯 Showing {len(relevant_memories)} memories relevant to: {current_goal.description}"
        )

    def calculate_goal_relevance(self, memory: Memory, goal: Goal) -> float:
        """Calculate how relevant a memory is to a goal"""
        relevance = 0.0

        # Direct goal linking
        if (
            "linked_goals" in memory.context
            and goal.id in memory.context["linked_goals"]
        ):
            relevance += 0.5

        # Keyword matching
        goal_keywords = set(goal.description.lower().split())
        memory_keywords = set(memory.content.lower().split())

        keyword_overlap = goal_keywords & memory_keywords
        relevance += min(len(keyword_overlap) * 0.1, 0.3)

        # Tag matching
        if hasattr(goal, "tags") and memory.tags:
            tag_overlap = set(goal.context.get("tags", [])) & set(memory.tags)
            relevance += min(len(tag_overlap) * 0.15, 0.3)

        # Memory type bonus
        if memory.memory_type == "goal":
            relevance += 0.2
        elif memory.memory_type == "insight":
            relevance += 0.1

        # Importance weighting
        relevance *= 0.5 + memory.importance * 0.5

        return min(relevance, 1.0)

    def auto_cluster_memories(self):
        """Auto-cluster memories based on similarity"""
        self.status_label.setText("🔄 Auto-clustering memories...")

        # Simple clustering based on tags and content similarity
        clusters = {}

        for memory in self.memories.values():
            # Find best cluster
            best_cluster = None
            best_score = 0.0

            for cluster_id, cluster_memories in clusters.items():
                score = self.calculate_cluster_similarity(memory, cluster_memories)
                if score > best_score:
                    best_score = score
                    best_cluster = cluster_id

            # Add to cluster or create new one
            if best_cluster and best_score > 0.3:
                clusters[best_cluster].append(memory)
            else:
                cluster_id = f"auto_cluster_{len(clusters) + 1}"
                clusters[cluster_id] = [memory]

        # Update clusters
        self.clusters = []
        for cluster_id, cluster_memories in clusters.items():
            if len(cluster_memories) > 1:  # Only create clusters with multiple memories
                cluster = MemoryCluster(
                    id=cluster_id,
                    name=f"Cluster {cluster_id.split('_')[-1]}",
                    center=(0, 0),
                    memories=[m.id for m in cluster_memories],
                    color=f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}",
                    size=len(cluster_memories) / 10.0,
                    coherence=0.7,
                )
                self.clusters.append(cluster)

        # Refresh UI
        self.refresh_ui()

        self.status_label.setText(
            f"✅ Auto-clustered into {len(self.clusters)} clusters"
        )

    def calculate_cluster_similarity(
        self, memory: Memory, cluster_memories: List[Memory]
    ) -> float:
        """Calculate similarity between memory and cluster"""
        if not cluster_memories:
            return 0.0

        total_similarity = 0.0

        for cluster_memory in cluster_memories:
            # Tag similarity
            tag_overlap = set(memory.tags) & set(cluster_memory.tags)
            tag_similarity = len(tag_overlap) / max(
                len(memory.tags), len(cluster_memory.tags), 1
            )

            # Type similarity
            type_similarity = (
                1.0 if memory.memory_type == cluster_memory.memory_type else 0.0
            )

            # Combined similarity
            similarity = (tag_similarity * 0.6) + (type_similarity * 0.4)
            total_similarity += similarity

        return total_similarity / len(cluster_memories)

    def perform_memory_search(self, query: str, filters: Dict[str, Any]):
        """Perform memory search with filters"""
        results = []

        for memory in self.memories.values():
            # Text search
            if query and query.lower() not in memory.content.lower():
                continue

            # Type filter
            if (
                filters["type"] != "All Types"
                and memory.memory_type != filters["type"].lower()
            ):
                continue

            # Importance filter
            if memory.importance < filters["importance"]:
                continue

            # Time filter
            if filters["time"] != "All Time":
                time_delta = self.get_time_delta(filters["time"])
                if datetime.now() - memory.timestamp > time_delta:
                    continue

            results.append(memory)

        # Sort results
        if filters["sort"] == "Newest":
            results.sort(key=lambda m: m.timestamp, reverse=True)
        elif filters["sort"] == "Oldest":
            results.sort(key=lambda m: m.timestamp)
        elif filters["sort"] == "Most Important":
            results.sort(key=lambda m: m.importance, reverse=True)
        elif filters["sort"] == "Most Accessed":
            results.sort(key=lambda m: m.access_count, reverse=True)

        # Update search results
        self.search_widget.update_results(results)

        self.status_label.setText(
            f"🔍 Found {len(results)} memories matching search criteria"
        )

    def get_time_delta(self, time_filter: str) -> timedelta:
        """Get time delta for filtering"""
        if time_filter == "Last Hour":
            return timedelta(hours=1)
        elif time_filter == "Last Day":
            return timedelta(days=1)
        elif time_filter == "Last Week":
            return timedelta(weeks=1)
        elif time_filter == "Last Month":
            return timedelta(days=30)
        return timedelta(days=365)  # Default: 1 year

    def on_memory_selected(self, memory: Memory):
        """Handle memory selection"""
        # Update access count
        memory.access_count += 1
        memory.last_accessed = datetime.now()

        # Show details
        details_text = f"""
📋 Memory Details
=================

Type: {memory.memory_type.title()}
Content: {memory.content}
Importance: {memory.importance:.1%}
Confidence: {memory.confidence:.1%}
Created: {memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Last Accessed: {memory.last_accessed.strftime("%Y-%m-%d %H:%M:%S") if memory.last_accessed else "Never"}
Access Count: {memory.access_count}
Tags: {", ".join(memory.tags) if memory.tags else "None"}

Connected Memories: {len(memory.connections)}
{chr(10).join([f"  • {self.memories[conn_id].content[:50]}..." for conn_id in memory.connections[:3] if conn_id in self.memories])}
"""

        self.memory_details.setPlainText(details_text)

        # Switch to graph tab if not already there
        if self.tabs.currentIndex() != 0:
            self.tabs.setCurrentIndex(0)

    def change_graph_layout(self, layout_type: str):
        """Change graph layout"""
        if layout_type == "Clustered":
            self.memory_graph.cluster_layout(self.clusters)
        else:
            self.populate_memory_graph()

        self.status_label.setText(f"📊 Changed to {layout_type} layout")

    def filter_by_importance(self, min_importance: int):
        """Filter graph by importance level"""
        threshold = min_importance / 100.0

        for memory_id, node in self.memory_graph.memory_nodes.items():
            memory = self.memories[memory_id]
            if memory.importance >= threshold:
                node.setVisible(True)
            else:
                node.setVisible(False)

    def export_memories(self):
        """Export memories to file"""
        export_data = {
            "memories": [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "type": mem.memory_type,
                    "importance": mem.importance,
                    "confidence": mem.confidence,
                    "tags": mem.tags,
                    "timestamp": mem.timestamp.isoformat(),
                    "access_count": mem.access_count,
                    "connections": mem.connections,
                }
                for mem in self.memories.values()
            ],
            "clusters": [
                {
                    "id": cluster.id,
                    "name": cluster.name,
                    "memories": cluster.memories,
                    "color": cluster.color,
                    "size": cluster.size,
                    "coherence": cluster.coherence,
                }
                for cluster in self.clusters
            ],
            "export_timestamp": datetime.now().isoformat(),
        }

        # In a real implementation, this would open a file dialog
        filename = f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)

            QMessageBox.information(
                self, "Export Complete", f"Memories exported to {filename}"
            )
            self.status_label.setText(
                f"📤 Exported {len(self.memories)} memories to {filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export memories: {str(e)}"
            )

    def refresh_memory_data(self):
        """Refresh memory data from memory manager"""
        if self.memory_manager:
            # In real implementation, this would sync with the actual memory manager
            pass

        # Update UI elements
        self.stats_label.setText(
            f"📊 {len(self.memories)} memories • {len(self.clusters)} clusters"
        )

    def refresh_ui(self):
        """Refresh all UI elements"""
        self.populate_memory_graph()
        self.populate_memory_table()
        self.populate_clusters_list()
        self.update_analytics()
        self.update_timeline()
        self.refresh_memory_data()


# Demo application
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Create world-class memory core
    memory_core = WorldClassMemoryCore()
    memory_core.setWindowTitle("🧠 World-Class Memory Core")
    memory_core.resize(1200, 800)
    memory_core.show()

    sys.exit(app.exec())
