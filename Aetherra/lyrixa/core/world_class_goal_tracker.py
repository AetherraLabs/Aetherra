#!/usr/bin/env python3
"""
World-Class Goal Tracker
========================
🎯 Intelligent Goal Management with Progress Tracking and Reasoning Trails
📊 Interactive progress indicators, goal analysis, and smart insights
🧠 "Why was this goal created? What's blocking it?" intelligence
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
        QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
        QGroupBox, QTabWidget, QListWidget, QListWidgetItem, QProgressBar,
        QMessageBox, QDialog, QDialogButtonBox, QSlider, QCheckBox,
        QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
        QApplication, QMenu, QFormLayout, QDateTimeEdit, QPlainTextEdit
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QDateTime
    from PySide6.QtGui import QFont, QColor, QIcon, QAction, QPainter, QPen, QBrush
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    print("⚠️  PySide6 not available - running in console mode")


class GoalStatus(Enum):
    """Goal status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class GoalPriority(Enum):
    """Goal priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GoalTrigger:
    """What triggered the creation of this goal"""
    trigger_type: str  # user_request, system_insight, deadline, dependency, opportunity
    description: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8


@dataclass
class GoalBlocker:
    """What's blocking this goal"""
    blocker_type: str  # resource, dependency, knowledge, external, technical
    description: str
    severity: float  # 0.0 to 1.0
    identified_at: datetime
    resolution_plan: str = ""
    estimated_resolution: Optional[datetime] = None


@dataclass
class GoalMilestone:
    """Goal milestone or sub-goal"""
    id: str
    title: str
    description: str
    target_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0


@dataclass
class GoalProgress:
    """Goal progress tracking"""
    current_progress: float = 0.0  # 0.0 to 1.0
    milestones: List[GoalMilestone] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    progress_history: List[Tuple[datetime, float]] = field(default_factory=list)
    velocity: float = 0.0  # Progress per day
    estimated_completion: Optional[datetime] = None


@dataclass
class GoalReasoning:
    """Goal reasoning trail"""
    creation_reason: str = ""
    triggers: List[GoalTrigger] = field(default_factory=list)
    blockers: List[GoalBlocker] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class Goal:
    """Enhanced goal with progress tracking and reasoning"""
    id: str
    title: str
    description: str
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    status: GoalStatus = GoalStatus.ACTIVE
    priority: GoalPriority = GoalPriority.MEDIUM
    target_date: Optional[datetime] = None

    # Progress tracking
    progress: GoalProgress = field(default_factory=lambda: GoalProgress())

    # Reasoning trail
    reasoning: GoalReasoning = field(default_factory=lambda: GoalReasoning())

    # Metadata
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    owner: str = "system"
    context: Dict[str, Any] = field(default_factory=dict)

    # Relationships
    parent_goal: Optional[str] = None
    sub_goals: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)


class ProgressIndicator(QWidget):
    """Custom progress indicator widget"""

    def __init__(self, progress: float = 0.0, goal: Optional[Goal] = None):
        super().__init__()
        self.progress = progress
        self.goal = goal
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)

    def paintEvent(self, event):
        """Custom paint event for progress indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
          # Background
        bg_color = QColor("#0a0a0a")
        painter.fillRect(self.rect(), bg_color)

        # Progress bar
        progress_rect = self.rect()
        progress_rect.setWidth(int(progress_rect.width() * self.progress))

        # Color based on progress
        if self.progress >= 0.8:
            progress_color = QColor("#00ff88")  # Green
        elif self.progress >= 0.5:
            progress_color = QColor("#ffff00")  # Yellow
        else:
            progress_color = QColor("#00aaff")  # Blue

        painter.fillRect(progress_rect, progress_color)

        # Border
        painter.setPen(QPen(QColor("#00ff88"), 1))
        painter.drawRect(self.rect())

        # Text
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.progress:.1%}")

    def update_progress(self, progress: float):
        """Update progress value"""
        self.progress = progress
        self.update()


class GoalDetailDialog(QDialog):
    """Detailed goal information dialog"""

    def __init__(self, goal: Goal, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.setWindowTitle(f"🎯 Goal Details: {goal.title}")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(f"🎯 {self.goal.title}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E8B57;")

        status_label = QLabel(f"Status: {self.goal.status.value.title()}")
        status_label.setStyleSheet(f"color: {self.get_status_color()};")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Tabs
        tabs = QTabWidget()

        # Overview tab
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)

        # Basic info
        basic_group = QGroupBox("📋 Basic Information")
        basic_layout = QFormLayout(basic_group)

        basic_layout.addRow("Description:", QLabel(self.goal.description))
        basic_layout.addRow("Priority:", QLabel(self.goal.priority.value.title()))
        basic_layout.addRow("Category:", QLabel(self.goal.category))
        basic_layout.addRow("Created:", QLabel(self.goal.created.strftime("%Y-%m-%d %H:%M")))
        basic_layout.addRow("Updated:", QLabel(self.goal.updated.strftime("%Y-%m-%d %H:%M")))

        if self.goal.target_date:
            basic_layout.addRow("Target Date:", QLabel(self.goal.target_date.strftime("%Y-%m-%d")))

        overview_layout.addWidget(basic_group)

        # Progress info
        progress_group = QGroupBox("📊 Progress Information")
        progress_layout = QVBoxLayout(progress_group)

        progress_indicator = ProgressIndicator(self.goal.progress.current_progress, self.goal)
        progress_layout.addWidget(progress_indicator)

        progress_info = QLabel(f"""
Progress: {self.goal.progress.current_progress:.1%}
Velocity: {self.goal.progress.velocity:.3f} per day
Milestones: {len(self.goal.progress.milestones)} total
Completed: {len([m for m in self.goal.progress.milestones if m.completed])} milestones
        """)
        progress_layout.addWidget(progress_info)

        overview_layout.addWidget(progress_group)

        tabs.addTab(overview_widget, "📋 Overview")

        # Reasoning tab
        reasoning_widget = QWidget()
        reasoning_layout = QVBoxLayout(reasoning_widget)

        # Creation reason
        creation_group = QGroupBox("🤔 Why was this goal created?")
        creation_layout = QVBoxLayout(creation_group)

        creation_text = QTextEdit()
        creation_text.setReadOnly(True)
        creation_text.setPlainText(self.goal.reasoning.creation_reason)
        creation_layout.addWidget(creation_text)

        reasoning_layout.addWidget(creation_group)

        # Triggers
        triggers_group = QGroupBox("⚡ What triggered this goal?")
        triggers_layout = QVBoxLayout(triggers_group)

        triggers_text = QTextEdit()
        triggers_text.setReadOnly(True)

        if self.goal.reasoning.triggers:
            trigger_info = "\n".join([
                f"🔥 {trigger.trigger_type.title()}: {trigger.description}"
                for trigger in self.goal.reasoning.triggers
            ])
        else:
            trigger_info = "No specific triggers identified."

        triggers_text.setPlainText(trigger_info)
        triggers_layout.addWidget(triggers_text)

        reasoning_layout.addWidget(triggers_group)

        # Blockers
        blockers_group = QGroupBox("🚫 What's blocking this goal?")
        blockers_layout = QVBoxLayout(blockers_group)

        blockers_text = QTextEdit()
        blockers_text.setReadOnly(True)

        if self.goal.reasoning.blockers:
            blocker_info = "\n".join([
                f"⚠️ {blocker.blocker_type.title()}: {blocker.description} (Severity: {blocker.severity:.1%})"
                for blocker in self.goal.reasoning.blockers
            ])
        else:
            blocker_info = "No blockers identified. Goal is clear to proceed!"

        blockers_text.setPlainText(blocker_info)
        blockers_layout.addWidget(blockers_text)

        reasoning_layout.addWidget(blockers_group)

        tabs.addTab(reasoning_widget, "🧠 Reasoning")

        # Milestones tab
        milestones_widget = QWidget()
        milestones_layout = QVBoxLayout(milestones_widget)

        milestones_list = QListWidget()

        for milestone in self.goal.progress.milestones:
            item = QListWidgetItem()

            status_icon = "✅" if milestone.completed else "⏳"
            progress_text = f"{milestone.progress:.1%}" if not milestone.completed else "100%"

            item.setText(f"{status_icon} {milestone.title} - {progress_text}")

            if milestone.completed:
                item.setBackground(QColor("#e8f5e8"))

            milestones_list.addItem(item)

        milestones_layout.addWidget(milestones_list)

        tabs.addTab(milestones_widget, "🎯 Milestones")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def get_status_color(self) -> str:
        """Get color for status display"""
        colors = {
            GoalStatus.ACTIVE: "#2196F3",
            GoalStatus.COMPLETED: "#4CAF50",
            GoalStatus.PAUSED: "#FF9800",
            GoalStatus.CANCELLED: "#F44336",
            GoalStatus.BLOCKED: "#9C27B0"
        }
        return colors.get(self.goal.status, "#666")


class GoalCreationDialog(QDialog):
    """Dialog for creating new goals"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎯 Create New Goal")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()

        # Basic info
        basic_group = QGroupBox("📋 Basic Information")
        basic_layout = QFormLayout(basic_group)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter goal title...")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe the goal in detail...")
        self.description_input.setMaximumHeight(100)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems([p.value.title() for p in GoalPriority])
        self.priority_combo.setCurrentText("Medium")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., work, personal, learning...")

        self.target_date_input = QDateTimeEdit()
        self.target_date_input.setDateTime(QDateTime.currentDateTime().addDays(30))

        basic_layout.addRow("Title:", self.title_input)
        basic_layout.addRow("Description:", self.description_input)
        basic_layout.addRow("Priority:", self.priority_combo)
        basic_layout.addRow("Category:", self.category_input)
        basic_layout.addRow("Target Date:", self.target_date_input)

        layout.addWidget(basic_group)

        # Reasoning
        reasoning_group = QGroupBox("🧠 Goal Reasoning")
        reasoning_layout = QVBoxLayout(reasoning_group)

        self.creation_reason_input = QTextEdit()
        self.creation_reason_input.setPlaceholderText("Why is this goal being created? What's the motivation?")
        self.creation_reason_input.setMaximumHeight(80)

        reasoning_layout.addWidget(QLabel("Creation Reason:"))
        reasoning_layout.addWidget(self.creation_reason_input)

        layout.addWidget(reasoning_group)

        # Triggers
        triggers_group = QGroupBox("⚡ Goal Triggers")
        triggers_layout = QVBoxLayout(triggers_group)

        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItems([
            "User Request", "System Insight", "Deadline", "Dependency", "Opportunity"
        ])

        self.trigger_description_input = QLineEdit()
        self.trigger_description_input.setPlaceholderText("What specifically triggered this goal?")

        triggers_layout.addWidget(QLabel("Trigger Type:"))
        triggers_layout.addWidget(self.trigger_type_combo)
        triggers_layout.addWidget(QLabel("Trigger Description:"))
        triggers_layout.addWidget(self.trigger_description_input)

        layout.addWidget(triggers_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_goal_data(self) -> Dict[str, Any]:
        """Get goal data from form"""
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "priority": self.priority_combo.currentText().lower(),
            "category": self.category_input.text() or "general",
            "target_date": self.target_date_input.dateTime().toPython(),
            "creation_reason": self.creation_reason_input.toPlainText(),
            "trigger_type": self.trigger_type_combo.currentText().lower().replace(" ", "_"),
            "trigger_description": self.trigger_description_input.text()
        }


class GoalProgressManager:
    """Manages goal progress calculations and updates"""

    def __init__(self):
        self.goals = {}

    def update_goal_progress(self, goal: Goal):
        """Update goal progress based on milestones"""
        if not goal.progress.milestones:
            return

        # Calculate progress from milestones
        total_milestones = len(goal.progress.milestones)
        completed_milestones = sum(1 for m in goal.progress.milestones if m.completed)

        # Weighted progress including partial completion
        milestone_progress = sum(m.progress for m in goal.progress.milestones)
        goal.progress.current_progress = milestone_progress / total_milestones

        # Update progress history
        now = datetime.now()
        goal.progress.progress_history.append((now, goal.progress.current_progress))
        goal.progress.last_update = now

        # Calculate velocity (progress per day)
        if len(goal.progress.progress_history) > 1:
            recent_history = goal.progress.progress_history[-10:]  # Last 10 updates
            if len(recent_history) >= 2:
                time_span = (recent_history[-1][0] - recent_history[0][0]).total_seconds() / 86400  # Days
                progress_change = recent_history[-1][1] - recent_history[0][1]
                if time_span > 0:
                    goal.progress.velocity = progress_change / time_span

        # Estimate completion date
        if goal.progress.velocity > 0:
            remaining_progress = 1.0 - goal.progress.current_progress
            days_to_completion = remaining_progress / goal.progress.velocity
            goal.progress.estimated_completion = now + timedelta(days=days_to_completion)

    def add_milestone(self, goal: Goal, title: str, description: str, target_date: datetime = None):
        """Add a milestone to a goal"""
        milestone_id = f"milestone_{len(goal.progress.milestones) + 1}"

        milestone = GoalMilestone(
            id=milestone_id,
            title=title,
            description=description,
            target_date=target_date
        )

        goal.progress.milestones.append(milestone)
        self.update_goal_progress(goal)

    def complete_milestone(self, goal: Goal, milestone_id: str):
        """Mark a milestone as completed"""
        for milestone in goal.progress.milestones:
            if milestone.id == milestone_id:
                milestone.completed = True
                milestone.completed_date = datetime.now()
                milestone.progress = 1.0
                break

        self.update_goal_progress(goal)

    def identify_blockers(self, goal: Goal) -> List[GoalBlocker]:
        """Identify potential blockers for a goal"""
        blockers = []

        # Check for overdue milestones
        now = datetime.now()
        for milestone in goal.progress.milestones:
            if milestone.target_date and milestone.target_date < now and not milestone.completed:
                blocker = GoalBlocker(
                    blocker_type="deadline",
                    description=f"Milestone '{milestone.title}' is overdue",
                    severity=0.8,
                    identified_at=now
                )
                blockers.append(blocker)

        # Check for low velocity
        if goal.progress.velocity < 0.01:  # Very slow progress
            blocker = GoalBlocker(
                blocker_type="progress",
                description="Progress velocity is very low",
                severity=0.6,
                identified_at=now
            )
            blockers.append(blocker)

        return blockers


class WorldClassGoalTracker(QWidget):
    """World-class goal tracking system"""

    def __init__(self):
        super().__init__()
        self.goals = {}  # goal_id -> Goal
        self.progress_manager = GoalProgressManager()

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

            QTreeWidget {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
            }

            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(0, 255, 136, 0.05);
            }

            QTreeWidget::item:selected {
                background: rgba(0, 255, 136, 0.2);
            }

            QProgressBar {
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                background: #0a0a0a;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.6));
                border-radius: 3px;
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

            QDateTimeEdit {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
            }

            QSpinBox {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
            }

            QTableWidget {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                gridline-color: rgba(0, 255, 136, 0.1);
            }

            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(0, 255, 136, 0.1);
            }

            QTableWidget::item:selected {
                background: rgba(0, 255, 136, 0.2);
            }

            QHeaderView::section {
                background: rgba(0, 255, 136, 0.1);
                color: #ffffff;
                padding: 8px;
                border: 1px solid rgba(0, 255, 136, 0.3);
                font-weight: bold;
            }
        """)

        # Initialize with sample data
        self.initialize_sample_data()

        self.init_ui()
        self.setup_connections()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🎯 World-Class Goal Tracker")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")

        # Goal stats
        active_goals = len([g for g in self.goals.values() if g.status == GoalStatus.ACTIVE])
        completed_goals = len([g for g in self.goals.values() if g.status == GoalStatus.COMPLETED])

        self.stats_label = QLabel(f"📊 {active_goals} active • {completed_goals} completed")
        self.stats_label.setStyleSheet("font-size: 12px; color: #ffffff;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)

        layout.addLayout(header_layout)

        # Main content tabs
        self.tabs = QTabWidget()

        # Active Goals tab
        self.setup_active_goals_tab()

        # Goal Analytics tab
        self.setup_analytics_tab()

        # Goal History tab
        self.setup_history_tab()

        layout.addWidget(self.tabs)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.create_goal_btn = QPushButton("🎯 Create Goal")
        self.create_goal_btn.clicked.connect(self.create_goal)

        self.analyze_blockers_btn = QPushButton("🔍 Analyze Blockers")
        self.analyze_blockers_btn.clicked.connect(self.analyze_blockers)

        self.update_progress_btn = QPushButton("📊 Update Progress")
        self.update_progress_btn.clicked.connect(self.update_all_progress)

        actions_layout.addWidget(self.create_goal_btn)
        actions_layout.addWidget(self.analyze_blockers_btn)
        actions_layout.addWidget(self.update_progress_btn)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        # Status bar
        self.status_label = QLabel("Ready • Intelligent goal tracking active")
        self.status_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def setup_active_goals_tab(self):
        """Setup active goals tab"""
        goals_widget = QWidget()
        layout = QVBoxLayout(goals_widget)

        # Goal list
        self.goals_list = QListWidget()
        self.goals_list.itemDoubleClicked.connect(self.show_goal_details)
        self.populate_goals_list()
        layout.addWidget(self.goals_list)

        # Goal details panel
        details_group = QGroupBox("📋 Goal Details")
        details_layout = QVBoxLayout(details_group)

        self.goal_details_text = QTextEdit()
        self.goal_details_text.setReadOnly(True)
        self.goal_details_text.setMaximumHeight(200)
        details_layout.addWidget(self.goal_details_text)

        layout.addWidget(details_group)

        self.tabs.addTab(goals_widget, "🎯 Active Goals")

    def setup_analytics_tab(self):
        """Setup analytics tab"""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)

        # Progress overview
        progress_group = QGroupBox("📊 Progress Overview")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.update_progress_analytics()
        progress_layout.addWidget(self.progress_text)

        layout.addWidget(progress_group)

        # Blockers analysis
        blockers_group = QGroupBox("🚫 Blockers Analysis")
        blockers_layout = QVBoxLayout(blockers_group)

        self.blockers_text = QTextEdit()
        self.blockers_text.setReadOnly(True)
        self.update_blockers_analysis()
        blockers_layout.addWidget(self.blockers_text)

        layout.addWidget(blockers_group)

        self.tabs.addTab(analytics_widget, "📊 Analytics")

    def setup_history_tab(self):
        """Setup history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)

        # Goal history
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.update_goal_history()
        layout.addWidget(self.history_text)

        self.tabs.addTab(history_widget, "📈 History")

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def initialize_sample_data(self):
        """Initialize with sample goal data"""
        # Sample goals
        sample_goals = [
            {
                "title": "Complete AI Memory System",
                "description": "Implement a world-class memory management system with clustering and context linking",
                "priority": GoalPriority.HIGH,
                "category": "development",
                "creation_reason": "Critical component needed for AI system functionality",
                "trigger_type": "system_insight",
                "trigger_description": "Identified need for better memory management during system analysis",
                "milestones": [
                    {"title": "Design memory architecture", "completed": True},
                    {"title": "Implement basic memory storage", "completed": True},
                    {"title": "Add clustering functionality", "completed": False, "progress": 0.7},
                    {"title": "Integrate with AI system", "completed": False, "progress": 0.3}
                ]
            },
            {
                "title": "Develop Goal Tracking System",
                "description": "Create an intelligent goal tracking system with progress indicators and reasoning trails",
                "priority": GoalPriority.MEDIUM,
                "category": "development",
                "creation_reason": "Need better visibility into goal progress and blockers",
                "trigger_type": "user_request",
                "trigger_description": "User requested enhanced goal tracking capabilities",
                "milestones": [
                    {"title": "Design goal data structure", "completed": True},
                    {"title": "Implement progress tracking", "completed": False, "progress": 0.8},
                    {"title": "Add reasoning trail", "completed": False, "progress": 0.5},
                    {"title": "Create user interface", "completed": False, "progress": 0.6}
                ]
            },
            {
                "title": "Improve System Performance",
                "description": "Optimize system performance and reduce response times",
                "priority": GoalPriority.LOW,
                "category": "optimization",
                "creation_reason": "System performance metrics indicate room for improvement",
                "trigger_type": "deadline",
                "trigger_description": "Performance review deadline approaching",
                "milestones": [
                    {"title": "Profile system performance", "completed": True},
                    {"title": "Identify bottlenecks", "completed": False, "progress": 0.4},
                    {"title": "Implement optimizations", "completed": False, "progress": 0.1}
                ]
            }
        ]

        # Create goal objects
        for i, goal_data in enumerate(sample_goals):
            goal_id = f"goal_{i+1}"

            # Create goal
            goal = Goal(
                id=goal_id,
                title=goal_data["title"],
                description=goal_data["description"],
                priority=goal_data["priority"],
                category=goal_data["category"],
                target_date=datetime.now() + timedelta(days=30),
                status=GoalStatus.ACTIVE
            )

            # Set reasoning
            goal.reasoning.creation_reason = goal_data["creation_reason"]
            goal.reasoning.triggers.append(GoalTrigger(
                trigger_type=goal_data["trigger_type"],
                description=goal_data["trigger_description"],
                timestamp=datetime.now() - timedelta(days=random.randint(1, 10))
            ))

            # Add milestones
            for j, milestone_data in enumerate(goal_data["milestones"]):
                milestone = GoalMilestone(
                    id=f"milestone_{j+1}",
                    title=milestone_data["title"],
                    description=milestone_data["title"],
                    completed=milestone_data["completed"],
                    progress=milestone_data.get("progress", 1.0 if milestone_data["completed"] else 0.0)
                )

                if milestone.completed:
                    milestone.completed_date = datetime.now() - timedelta(days=random.randint(1, 5))

                goal.progress.milestones.append(milestone)

            # Update progress
            self.progress_manager.update_goal_progress(goal)

            # Add some blockers for demonstration
            if i == 1:  # Add blocker to second goal
                blocker = GoalBlocker(
                    blocker_type="resource",
                    description="Waiting for UI design approval",
                    severity=0.6,
                    identified_at=datetime.now() - timedelta(days=2)
                )
                goal.reasoning.blockers.append(blocker)

            self.goals[goal_id] = goal

    def populate_goals_list(self):
        """Populate the goals list"""
        self.goals_list.clear()

        for goal in self.goals.values():
            if goal.status == GoalStatus.ACTIVE:
                item = QListWidgetItem()

                # Status indicators
                priority_icon = {
                    GoalPriority.CRITICAL: "🔴",
                    GoalPriority.HIGH: "🟠",
                    GoalPriority.MEDIUM: "🟡",
                    GoalPriority.LOW: "🟢"
                }[goal.priority]

                progress_text = f"{goal.progress.current_progress:.1%}"

                # Blocker indicator
                blocker_icon = "🚫" if goal.reasoning.blockers else ""

                item.setText(f"{priority_icon} {goal.title} - {progress_text} {blocker_icon}")
                item.setData(Qt.UserRole, goal)

                # Add tooltip with details
                tooltip = f"""
Title: {goal.title}
Progress: {goal.progress.current_progress:.1%}
Priority: {goal.priority.value.title()}
Target: {goal.target_date.strftime('%Y-%m-%d') if goal.target_date else 'No target'}
Blockers: {len(goal.reasoning.blockers)}
Milestones: {len([m for m in goal.progress.milestones if m.completed])}/{len(goal.progress.milestones)} completed
"""
                item.setToolTip(tooltip)

                self.goals_list.addItem(item)

    def show_goal_details(self, item):
        """Show detailed goal information"""
        goal = item.data(Qt.UserRole)
        if goal:
            dialog = GoalDetailDialog(goal, self)
            dialog.exec()

    def create_goal(self):
        """Create a new goal"""
        dialog = GoalCreationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_goal_data()
            self.create_goal_from_data(data)

    def create_goal_from_data(self, data: Dict[str, Any]):
        """Create goal from dialog data"""
        goal_id = f"goal_{len(self.goals) + 1}"

        goal = Goal(
            id=goal_id,
            title=data["title"],
            description=data["description"],
            priority=GoalPriority(data["priority"]),
            category=data["category"],
            target_date=data["target_date"],
            status=GoalStatus.ACTIVE
        )

        # Set reasoning
        goal.reasoning.creation_reason = data["creation_reason"]
        goal.reasoning.triggers.append(GoalTrigger(
            trigger_type=data["trigger_type"],
            description=data["trigger_description"],
            timestamp=datetime.now()
        ))

        # Add initial milestone
        initial_milestone = GoalMilestone(
            id="milestone_1",
            title="Goal created",
            description="Initial goal setup completed",
            completed=True,
            completed_date=datetime.now(),
            progress=1.0
        )
        goal.progress.milestones.append(initial_milestone)

        self.progress_manager.update_goal_progress(goal)

        self.goals[goal_id] = goal

        # Refresh UI
        self.refresh_ui()

        self.status_label.setText(f"✅ Goal created: {goal.title}")

    def analyze_blockers(self):
        """Analyze blockers across all goals"""
        total_blockers = 0
        blocker_analysis = "🔍 Blocker Analysis Report\n" + "=" * 30 + "\n\n"

        for goal in self.goals.values():
            if goal.status == GoalStatus.ACTIVE:
                # Identify new blockers
                new_blockers = self.progress_manager.identify_blockers(goal)

                # Add to goal if not already present
                existing_descriptions = [b.description for b in goal.reasoning.blockers]
                for blocker in new_blockers:
                    if blocker.description not in existing_descriptions:
                        goal.reasoning.blockers.append(blocker)

                # Report blockers
                if goal.reasoning.blockers:
                    blocker_analysis += f"🎯 {goal.title}:\n"
                    for blocker in goal.reasoning.blockers:
                        blocker_analysis += f"  🚫 {blocker.blocker_type.title()}: {blocker.description}\n"
                        blocker_analysis += f"     Severity: {blocker.severity:.1%}\n"
                        total_blockers += 1
                    blocker_analysis += "\n"

        if total_blockers == 0:
            blocker_analysis += "✅ No blockers found! All goals are clear to proceed.\n"
        else:
            blocker_analysis += f"📊 Total blockers found: {total_blockers}\n"

        # Show analysis
        QMessageBox.information(self, "Blocker Analysis", blocker_analysis)

        # Update UI
        self.update_blockers_analysis()
        self.populate_goals_list()

        self.status_label.setText(f"🔍 Analyzed blockers: {total_blockers} found")

    def update_all_progress(self):
        """Update progress for all goals"""
        updated_count = 0

        for goal in self.goals.values():
            if goal.status == GoalStatus.ACTIVE:
                old_progress = goal.progress.current_progress
                self.progress_manager.update_goal_progress(goal)

                # Check for completion
                if goal.progress.current_progress >= 1.0:
                    goal.status = GoalStatus.COMPLETED
                    goal.updated = datetime.now()

                updated_count += 1

        # Refresh UI
        self.refresh_ui()

        self.status_label.setText(f"📊 Updated progress for {updated_count} goals")

    def update_progress_analytics(self):
        """Update progress analytics display"""
        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]

        if not active_goals:
            self.progress_text.setPlainText("No active goals to analyze.")
            return

        # Calculate statistics
        total_progress = sum(g.progress.current_progress for g in active_goals)
        avg_progress = total_progress / len(active_goals)

        high_progress_goals = [g for g in active_goals if g.progress.current_progress >= 0.8]
        low_progress_goals = [g for g in active_goals if g.progress.current_progress < 0.3]

        analytics_text = f"""
📊 Progress Analytics
====================

Active Goals: {len(active_goals)}
Average Progress: {avg_progress:.1%}
High Progress Goals (≥80%): {len(high_progress_goals)}
Low Progress Goals (<30%): {len(low_progress_goals)}

Goal Progress Details:
{chr(10).join([f"  • {g.title}: {g.progress.current_progress:.1%} (Velocity: {g.progress.velocity:.3f}/day)" for g in active_goals])}

Completion Estimates:
{chr(10).join([f"  • {g.title}: {g.progress.estimated_completion.strftime('%Y-%m-%d') if g.progress.estimated_completion else 'Unknown'}" for g in active_goals])}
"""

        self.progress_text.setPlainText(analytics_text)

    def update_blockers_analysis(self):
        """Update blockers analysis display"""
        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]

        total_blockers = sum(len(g.reasoning.blockers) for g in active_goals)

        if total_blockers == 0:
            self.blockers_text.setPlainText("✅ No blockers identified! All goals are clear to proceed.")
            return

        # Analyze blocker types
        blocker_types = {}
        for goal in active_goals:
            for blocker in goal.reasoning.blockers:
                blocker_types[blocker.blocker_type] = blocker_types.get(blocker.blocker_type, 0) + 1

        blockers_text = f"""
🚫 Blockers Analysis
===================

Total Blockers: {total_blockers}
Goals with Blockers: {len([g for g in active_goals if g.reasoning.blockers])}

Blocker Types:
{chr(10).join([f"  • {btype.title()}: {count}" for btype, count in blocker_types.items()])}

Detailed Blockers:
{chr(10).join([f"🎯 {g.title}:" + chr(10) + chr(10).join([f"    🚫 {b.blocker_type.title()}: {b.description} (Severity: {b.severity:.1%})" for b in g.reasoning.blockers]) for g in active_goals if g.reasoning.blockers])}
"""

        self.blockers_text.setPlainText(blockers_text)

    def update_goal_history(self):
        """Update goal history display"""
        all_goals = sorted(self.goals.values(), key=lambda g: g.created, reverse=True)

        history_text = "📈 Goal History\n" + "=" * 15 + "\n\n"

        for goal in all_goals:
            status_icon = {
                GoalStatus.ACTIVE: "⏳",
                GoalStatus.COMPLETED: "✅",
                GoalStatus.PAUSED: "⏸️",
                GoalStatus.CANCELLED: "❌",
                GoalStatus.BLOCKED: "🚫"
            }[goal.status]

            history_text += f"{goal.created.strftime('%Y-%m-%d')} {status_icon} {goal.title}\n"
            history_text += f"  Status: {goal.status.value.title()}\n"
            history_text += f"  Progress: {goal.progress.current_progress:.1%}\n"
            history_text += f"  Reason: {goal.reasoning.creation_reason[:80]}...\n"
            history_text += "\n"

        self.history_text.setPlainText(history_text)

    def refresh_data(self):
        """Refresh all data and analytics"""
        self.update_all_progress()

        # Update analytics
        self.update_progress_analytics()
        self.update_blockers_analysis()
        self.update_goal_history()

        # Update stats
        active_goals = len([g for g in self.goals.values() if g.status == GoalStatus.ACTIVE])
        completed_goals = len([g for g in self.goals.values() if g.status == GoalStatus.COMPLETED])

        self.stats_label.setText(f"📊 {active_goals} active • {completed_goals} completed")

    def refresh_ui(self):
        """Refresh all UI elements"""
        self.populate_goals_list()
        self.update_progress_analytics()
        self.update_blockers_analysis()
        self.update_goal_history()
        self.refresh_data()


def main():
    """Main application entry point"""
    if HAS_PYSIDE6:
        app = QApplication([])

        # Create and show the main window
        window = WorldClassGoalTracker()
        window.setWindowTitle("🎯 World-Class Goal Tracker")
        window.resize(1000, 700)
        window.show()

        # Show welcome message
        QMessageBox.information(window, "🎯 World-Class Goal Tracker",
                              "Welcome to the World-Class Goal Tracker!\n\n"
                              "Features:\n"
                              "📊 Interactive progress indicators\n"
                              "🧠 Reasoning trails for each goal\n"
                              "🔍 Blocker analysis and identification\n"
                              "📈 Progress analytics and velocity tracking\n"
                              "🎯 Milestone management\n\n"
                              "Try 'Analyze Blockers' to see intelligent goal analysis!")

        app.exec()
    else:
        print("🎯 World-Class Goal Tracker - Console Mode")
        print("PySide6 not available. Please install PySide6 for full functionality.")


if __name__ == "__main__":
    main()
