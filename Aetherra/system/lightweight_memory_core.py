"""
DEPRECATED: lightweight_memory_core.py is now an adapter for QuantumEnhancedMemoryEngine.
All memory operations are delegated to the canonical engine.
"""

from ..memory.QuantumEnhancedMemoryEngine.engine import QuantumEnhancedMemoryEngine


class LightweightMemoryCore:
    def __init__(self, *args, **kwargs):
        self.engine = QuantumEnhancedMemoryEngine()

    def store(self, memory_entry: dict) -> dict:
        return self.engine.store(memory_entry)

    def retrieve(self, query: str, context: dict = None) -> dict:
        return self.engine.retrieve(query, context)

    memory_type: str = "general"  # general, goal, insight, experience, knowledge
    importance: float = 0.5  # 0.0 to 1.0
    confidence: float = 0.8  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)  # Connected memory IDs
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    relevance_score: float = 0.0  # For goal relevance


@dataclass
class Goal:
    """Goal for memory relevance"""

    id: str
    description: str
    priority: float = 0.5
    status: str = "active"
    created: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


class MemoryCore:
    """Core memory management system"""

    def __init__(self):
        self.memories = {}  # memory_id -> Memory
        self.current_goals = []  # List of Goal
        self.initialize_sample_data()

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

    def search_memories(
        self, query: str, filters: Dict[str, Any] = None
    ) -> List[Memory]:
        """Search memories with filters"""
        results = []

        for memory in self.memories.values():
            # Text search
            if query and query.lower() not in memory.content.lower():
                continue

            # Apply filters if provided
            if filters:
                if filters.get("type") and filters["type"] != "All Types":
                    if memory.memory_type != filters["type"].lower():
                        continue

                if filters.get("importance", 0) > memory.importance:
                    continue

                if filters.get("time") and filters["time"] != "All Time":
                    time_delta = self.get_time_delta(filters["time"])
                    if datetime.now() - memory.timestamp > time_delta:
                        continue

            results.append(memory)

        return results

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
        return timedelta(days=365)

    def get_relevant_memories(self, goal_id: str = None) -> List[Memory]:
        """Get memories relevant to a goal"""
        if not self.current_goals:
            return []

        # Get target goal
        if goal_id:
            target_goal = next((g for g in self.current_goals if g.id == goal_id), None)
        else:
            # Get highest priority active goal
            target_goal = max(
                [g for g in self.current_goals if g.status == "active"],
                key=lambda g: g.priority,
                default=None,
            )

        if not target_goal:
            return []

        # Calculate relevance scores
        relevant_memories = []
        for memory in self.memories.values():
            relevance = self.calculate_goal_relevance(memory, target_goal)
            if relevance > 0.3:  # Threshold for relevance
                memory.relevance_score = relevance
                relevant_memories.append(memory)

        # Sort by relevance
        relevant_memories.sort(key=lambda m: m.relevance_score, reverse=True)
        return relevant_memories[:10]  # Top 10

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

        # Memory type bonus
        if memory.memory_type == "goal":
            relevance += 0.2
        elif memory.memory_type == "insight":
            relevance += 0.1

        # Importance weighting
        relevance *= 0.5 + memory.importance * 0.5

        return min(relevance, 1.0)

    def inject_memory(
        self,
        content: str,
        memory_type: str = "general",
        importance: float = 0.5,
        confidence: float = 0.8,
        tags: List[str] = None,
        auto_link: bool = True,
    ) -> Memory:
        """Inject a new memory"""
        memory_id = f"mem_{len(self.memories) + 1}"

        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            confidence=confidence,
            tags=tags or [],
            timestamp=datetime.now(),
            access_count=0,
        )

        self.memories[memory_id] = memory

        # Auto-link if requested
        if auto_link:
            self.auto_link_memory(memory)

        # Link to goals
        self.link_to_goals(memory)

        return memory

    def auto_link_memory(self, memory: Memory):
        """Auto-link memory to similar memories"""
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

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_memories = len(self.memories)

        if total_memories == 0:
            return {"total": 0}

        # Type distribution
        type_counts = {}
        importance_sum = 0
        confidence_sum = 0

        for memory in self.memories.values():
            type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1
            importance_sum += memory.importance
            confidence_sum += memory.confidence

        avg_importance = importance_sum / total_memories
        avg_confidence = confidence_sum / total_memories

        return {
            "total": total_memories,
            "type_distribution": type_counts,
            "avg_importance": avg_importance,
            "avg_confidence": avg_confidence,
            "active_goals": len(
                [g for g in self.current_goals if g.status == "active"]
            ),
        }


if HAS_PYSIDE6:

    class MemorySearchWidget(QWidget):
        """Advanced memory search widget"""

        search_performed = Signal(str, dict)
        memory_selected = Signal(Memory)

        def __init__(self, memory_core):
            super().__init__()
            self.memory_core = memory_core
            self.init_ui()

        def init_ui(self):
            """Initialize search UI"""
            layout = QVBoxLayout()

            # Search bar
            search_layout = QHBoxLayout()

            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍 Search memories...")
            self.search_input.returnPressed.connect(self.perform_search)

            self.search_btn = QPushButton("Search")
            self.search_btn.clicked.connect(self.perform_search)

            search_layout.addWidget(self.search_input)
            search_layout.addWidget(self.search_btn)

            layout.addLayout(search_layout)

            # Filters
            filters_group = QGroupBox("Filters")
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

            # Time filter
            self.time_filter = QComboBox()
            self.time_filter.addItems(
                ["All Time", "Last Hour", "Last Day", "Last Week", "Last Month"]
            )

            filters_layout.addWidget(QLabel("Type:"))
            filters_layout.addWidget(self.type_filter)
            filters_layout.addWidget(QLabel("Importance:"))
            filters_layout.addWidget(self.importance_filter)
            filters_layout.addWidget(QLabel("Time:"))
            filters_layout.addWidget(self.time_filter)

            layout.addWidget(filters_group)

            # Results
            self.results_list = QListWidget()
            self.results_list.itemClicked.connect(self.on_result_selected)
            layout.addWidget(self.results_list)

            # Stats
            self.stats_label = QLabel("Ready to search...")
            layout.addWidget(self.stats_label)

            self.setLayout(layout)

        def perform_search(self):
            """Perform memory search"""
            query = self.search_input.text().strip()

            filters = {
                "type": self.type_filter.currentText(),
                "importance": self.importance_filter.value() / 100.0,
                "time": self.time_filter.currentText(),
            }

            results = self.memory_core.search_memories(query, filters)
            self.update_results(results)

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

                item.setText(f"{type_icon} {memory.content[:80]}...")
                item.setData(Qt.UserRole, memory)

                self.results_list.addItem(item)

            self.stats_label.setText(f"Found {len(memories)} memories")

        def on_result_selected(self, item):
            """Handle result selection"""
            memory = item.data(Qt.UserRole)
            if memory:
                self.memory_selected.emit(memory)

    class MemoryInjectionDialog(QDialog):
        """Dialog for injecting new memories"""

        def __init__(self, memory_core, parent=None):
            super().__init__(parent)
            self.memory_core = memory_core
            self.setWindowTitle("💉 Inject New Memory")
            self.setModal(True)
            self.resize(500, 400)
            self.init_ui()

        def init_ui(self):
            """Initialize injection dialog UI"""
            layout = QVBoxLayout()

            # Content input
            content_group = QGroupBox("Memory Content")
            content_layout = QVBoxLayout(content_group)

            self.content_input = QTextEdit()
            self.content_input.setPlaceholderText("Enter the memory content...")
            content_layout.addWidget(self.content_input)

            layout.addWidget(content_group)

            # Properties
            props_group = QGroupBox("Properties")
            props_layout = QFormLayout(props_group)

            self.type_combo = QComboBox()
            self.type_combo.addItems(
                ["general", "goal", "insight", "experience", "knowledge"]
            )

            self.importance_slider = QSlider(Qt.Horizontal)
            self.importance_slider.setRange(0, 100)
            self.importance_slider.setValue(50)

            self.tags_input = QLineEdit()
            self.tags_input.setPlaceholderText("tag1, tag2, tag3...")

            props_layout.addRow("Type:", self.type_combo)
            props_layout.addRow("Importance:", self.importance_slider)
            props_layout.addRow("Tags:", self.tags_input)

            layout.addWidget(props_group)

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
                "tags": [
                    tag.strip()
                    for tag in self.tags_input.text().split(",")
                    if tag.strip()
                ],
            }

    class LightweightMemoryCore(QWidget):
        """Lightweight memory management system"""

        def __init__(self):
            super().__init__()
            self.memory_core = MemoryCore()
            self.init_ui()
            self.setup_connections()

        def init_ui(self):
            """Initialize UI"""
            layout = QVBoxLayout()

            # Header
            header_layout = QHBoxLayout()
            title_label = QLabel("🧠 World-Class Memory Core")
            title_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #2E8B57;"
            )

            stats = self.memory_core.get_memory_stats()
            self.stats_label = QLabel(
                f"📊 {stats['total']} memories • {stats['active_goals']} active goals"
            )

            header_layout.addWidget(title_label)
            header_layout.addStretch()
            header_layout.addWidget(self.stats_label)

            layout.addLayout(header_layout)

            # Tabs
            self.tabs = QTabWidget()

            # Search tab
            self.search_widget = MemorySearchWidget(self.memory_core)
            self.tabs.addTab(self.search_widget, "🔍 Search")

            # Memory details tab
            self.details_widget = QTextEdit()
            self.details_widget.setReadOnly(True)
            self.tabs.addTab(self.details_widget, "📋 Details")

            # Analytics tab
            self.analytics_widget = QTextEdit()
            self.analytics_widget.setReadOnly(True)
            self.update_analytics()
            self.tabs.addTab(self.analytics_widget, "📊 Analytics")

            layout.addWidget(self.tabs)

            # Action buttons
            actions_layout = QHBoxLayout()

            self.inject_btn = QPushButton("💉 Inject Memory")
            self.inject_btn.clicked.connect(self.inject_memory)

            self.relevant_btn = QPushButton("🎯 Show Relevant to Goal")
            self.relevant_btn.clicked.connect(self.show_relevant_memories)

            actions_layout.addWidget(self.inject_btn)
            actions_layout.addWidget(self.relevant_btn)
            actions_layout.addStretch()

            layout.addLayout(actions_layout)

            # Status
            self.status_label = QLabel("Ready • Interactive memory management active")
            layout.addWidget(self.status_label)

            self.setLayout(layout)

        def setup_connections(self):
            """Setup signal connections"""
            self.search_widget.memory_selected.connect(self.on_memory_selected)

        def inject_memory(self):
            """Open memory injection dialog"""
            dialog = MemoryInjectionDialog(self.memory_core, self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_memory_data()
                memory = self.memory_core.inject_memory(
                    content=data["content"],
                    memory_type=data["memory_type"],
                    importance=data["importance"],
                    tags=data["tags"],
                )
                self.status_label.setText(
                    f"✅ Memory injected: {memory.content[:50]}..."
                )
                self.update_stats()

        def show_relevant_memories(self):
            """Show memories relevant to current goal"""
            relevant_memories = self.memory_core.get_relevant_memories()

            if not relevant_memories:
                QMessageBox.information(
                    self,
                    "No Relevant Memories",
                    "No memories found relevant to current goals.",
                )
                return

            self.search_widget.update_results(relevant_memories)
            self.tabs.setCurrentIndex(0)  # Switch to search tab

            goal = next(
                (g for g in self.memory_core.current_goals if g.status == "active"),
                None,
            )
            if goal:
                self.status_label.setText(
                    f"🎯 Showing {len(relevant_memories)} memories relevant to: {goal.description}"
                )

        def on_memory_selected(self, memory: Memory):
            """Handle memory selection"""
            memory.access_count += 1
            memory.last_accessed = datetime.now()

            details_text = f"""
📋 Memory Details
=================

ID: {memory.id}
Type: {memory.memory_type.title()}
Content: {memory.content}
Importance: {memory.importance:.1%}
Confidence: {memory.confidence:.1%}
Created: {memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Last Accessed: {memory.last_accessed.strftime("%Y-%m-%d %H:%M:%S") if memory.last_accessed else "Never"}
Access Count: {memory.access_count}
Tags: {", ".join(memory.tags) if memory.tags else "None"}

Connected Memories: {len(memory.connections)}
{chr(10).join([f"  • {conn_id}" for conn_id in memory.connections[:5]])}

Relevance Score: {memory.relevance_score:.2f}
"""

            self.details_widget.setPlainText(details_text)
            self.tabs.setCurrentIndex(1)  # Switch to details tab

        def update_analytics(self):
            """Update analytics display"""
            stats = self.memory_core.get_memory_stats()

            analytics_text = f"""
📊 Memory Analytics
===================

Total Memories: {stats["total"]}
Active Goals: {stats["active_goals"]}
Average Importance: {stats["avg_importance"]:.1%}
Average Confidence: {stats["avg_confidence"]:.1%}

Memory Type Distribution:
{
                chr(10).join(
                    [
                        f"  {mtype.title()}: {count} ({count / stats['total']:.1%})"
                        for mtype, count in stats["type_distribution"].items()
                    ]
                )
            }

Most Accessed Memories:
{
                chr(10).join(
                    [
                        f"  • {mem.content[:50]}... (accessed {mem.access_count} times)"
                        for mem in sorted(
                            self.memory_core.memories.values(),
                            key=lambda m: m.access_count,
                            reverse=True,
                        )[:5]
                    ]
                )
            }

Recent Memories:
{
                chr(10).join(
                    [
                        f"  • {mem.timestamp.strftime('%H:%M')} - {mem.content[:40]}..."
                        for mem in sorted(
                            self.memory_core.memories.values(),
                            key=lambda m: m.timestamp,
                            reverse=True,
                        )[:5]
                    ]
                )
            }
"""

            self.analytics_widget.setPlainText(analytics_text)

        def update_stats(self):
            """Update statistics display"""
            stats = self.memory_core.get_memory_stats()
            self.stats_label.setText(
                f"📊 {stats['total']} memories • {stats['active_goals']} active goals"
            )
            self.update_analytics()


def console_demo():
    """Console-based demo when GUI is not available"""
    print("🧠 World-Class Memory Core - Console Demo")
    print("=" * 50)

    core = MemoryCore()

    while True:
        print("\n🎯 Available Commands:")
        print("1. Search memories")
        print("2. Show relevant to goal")
        print("3. Inject new memory")
        print("4. Show statistics")
        print("5. List all memories")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            query = input("Enter search query: ")
            results = core.search_memories(query)
            print(f"\n📋 Found {len(results)} memories:")
            for i, memory in enumerate(results, 1):
                print(f"{i}. [{memory.memory_type.upper()}] {memory.content[:80]}...")

        elif choice == "2":
            relevant = core.get_relevant_memories()
            print(f"\n🎯 Found {len(relevant)} relevant memories:")
            for i, memory in enumerate(relevant, 1):
                print(
                    f"{i}. [Score: {memory.relevance_score:.2f}] {memory.content[:60]}..."
                )

        elif choice == "3":
            content = input("Enter memory content: ")
            memory_type = (
                input("Enter type (general/goal/insight/experience/knowledge): ")
                or "general"
            )
            importance = float(input("Enter importance (0.0-1.0): ") or "0.5")
            tags = input("Enter tags (comma-separated): ").split(",")
            tags = [tag.strip() for tag in tags if tag.strip()]

            memory = core.inject_memory(content, memory_type, importance, tags=tags)
            print(f"✅ Memory injected: {memory.id}")

        elif choice == "4":
            stats = core.get_memory_stats()
            print(f"\n📊 Memory Statistics:")
            print(f"Total Memories: {stats['total']}")
            print(f"Active Goals: {stats['active_goals']}")
            print(f"Average Importance: {stats['avg_importance']:.1%}")
            print(f"Average Confidence: {stats['avg_confidence']:.1%}")
            print(f"Type Distribution: {stats['type_distribution']}")

        elif choice == "5":
            print(f"\n📚 All Memories ({len(core.memories)}):")
            for memory in core.memories.values():
                print(f"  • [{memory.memory_type.upper()}] {memory.content[:60]}...")

        elif choice == "6":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


def main():
    """Main application entry point"""
    if HAS_PYSIDE6:
        app = QApplication([])

        # Create and show the main window
        window = LightweightMemoryCore()
        window.setWindowTitle("🧠 World-Class Memory Core")
        window.resize(1000, 700)
        window.show()

        # Show welcome message
        QMessageBox.information(
            window,
            "🧠 World-Class Memory Core",
            "Welcome to the World-Class Memory Core!\n\n"
            "Features:\n"
            "🔍 Advanced memory search with filters\n"
            "🎯 Goal-relevant memory discovery\n"
            "💉 Memory injection with auto-linking\n"
            "📊 Comprehensive analytics\n\n"
            "Try 'Show Relevant to Goal' to see intelligent discovery!",
        )

        app.exec()
    else:
        console_demo()


if __name__ == "__main__":
    main()
