#!/usr/bin/env python3
"""
Goal Tracking Panel
==================

Modular component for tracking goals and objectives.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict

from ..cards import ModernCard
from ..theme import ModernTheme
from ..utils.qt_imports import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    Qt,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class GoalTrackingPanel(ModernCard):
    """Panel for tracking goals and objectives"""

    def __init__(self, parent=None):
        super().__init__("🎯 Goal Tracking", parent)
        self.goals = []
        self.goals_file = "goals_store.json"
        self.init_ui()
        self.load_goals()

    def init_ui(self):
        """Initialize the user interface"""
        # Goals list
        self.goals_list = QListWidget()
        self.goals_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {ModernTheme.BORDER};
            }}
            QListWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.goals_list.itemClicked.connect(self.show_goal_details)
        self.add_widget(self.goals_list)

        # Goal details
        self.goal_details = QTextEdit()
        self.goal_details.setMaximumHeight(80)
        self.goal_details.setPlaceholderText("Select a goal to view details...")
        self.goal_details.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 11px;
            }}
        """)
        self.add_widget(self.goal_details)

        # Progress section
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("Overall Progress:"))

        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {ModernTheme.SURFACE};
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.SUCCESS};
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(self.overall_progress)

        progress_widget = QWidget()
        progress_widget.setLayout(progress_layout)
        self.add_widget(progress_widget)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.add_goal_btn = QPushButton("➕ Add Goal")
        self.add_goal_btn.clicked.connect(self.add_goal)
        controls_layout.addWidget(self.add_goal_btn)

        self.complete_goal_btn = QPushButton("✅ Complete")
        self.complete_goal_btn.clicked.connect(self.complete_goal)
        self.complete_goal_btn.setEnabled(False)
        controls_layout.addWidget(self.complete_goal_btn)

        self.remove_goal_btn = QPushButton("🗑️ Remove")
        self.remove_goal_btn.clicked.connect(self.remove_goal)
        self.remove_goal_btn.setEnabled(False)
        controls_layout.addWidget(self.remove_goal_btn)

        controls_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_goals)
        controls_layout.addWidget(self.refresh_btn)

        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        self.add_widget(controls_widget)

    def load_goals(self):
        """Load goals from storage"""
        try:
            if os.path.exists(self.goals_file):
                with open(self.goals_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Convert dict values to list
                        self.goals = list(data.values()) if data else []
                    elif isinstance(data, list):
                        self.goals = data
                    else:
                        self.goals = []
            else:
                # Create default goals if file doesn't exist
                self.goals = [
                    {
                        "id": 1,
                        "title": "Complete Neuroplex Modularization",
                        "description": "Break down monolithic GUI into modular components",
                        "status": "in_progress",
                        "priority": "high",
                        "created_at": datetime.now().isoformat(),
                        "progress": 65,
                    },
                    {
                        "id": 2,
                        "title": "Implement NeuroCode Language Features",
                        "description": "Add advanced syntax and stdlib functions",
                        "status": "completed",
                        "priority": "medium",
                        "created_at": datetime.now().isoformat(),
                        "progress": 100,
                    },
                ]
                self.save_goals()

            self.update_goals_display()

        except Exception as e:
            print(f"Error loading goals: {e}")
            # Initialize with empty goals if there's an error
            self.goals = []
            self.update_goals_display()

    def save_goals(self):
        """Save goals to storage"""
        try:
            with open(self.goals_file, "w", encoding="utf-8") as f:
                json.dump(self.goals, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving goals: {e}")

    def update_goals_display(self):
        """Update the goals display"""
        self.goals_list.clear()

        total_progress = 0
        completed_goals = 0

        for goal in self.goals:
            status_icon = "✅" if goal.get("status") == "completed" else "🔄"
            priority_icon = (
                "🔴"
                if goal.get("priority") == "high"
                else "🟡"
                if goal.get("priority") == "medium"
                else "🟢"
            )

            item_text = f"{status_icon} {priority_icon} {goal.get('title', 'Untitled Goal')}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, goal)

            # Color code by status
            if goal.get("status") == "completed":
                from ..utils.qt_imports import QColor

                item.setForeground(QColor(ModernTheme.SUCCESS))
                completed_goals += 1
            elif goal.get("status") == "in_progress":
                from ..utils.qt_imports import QColor

                item.setForeground(QColor(ModernTheme.PRIMARY))
            else:
                from ..utils.qt_imports import QColor

                item.setForeground(QColor(ModernTheme.TEXT_SECONDARY))

            self.goals_list.addItem(item)
            total_progress += goal.get("progress", 0)

        # Update overall progress
        if self.goals:
            avg_progress = total_progress / len(self.goals)
            self.overall_progress.setValue(int(avg_progress))
        else:
            self.overall_progress.setValue(0)

    def show_goal_details(self, item):
        """Show details for selected goal"""
        goal = item.data(Qt.ItemDataRole.UserRole)
        if goal:
            details = f"""Title: {goal.get("title", "N/A")}
Description: {goal.get("description", "N/A")}
Status: {goal.get("status", "N/A")}
Priority: {goal.get("priority", "N/A")}
Progress: {goal.get("progress", 0)}%
Created: {goal.get("created_at", "N/A")}"""

            self.goal_details.setText(details)

            # Enable buttons based on selection
            self.complete_goal_btn.setEnabled(goal.get("status") != "completed")
            self.remove_goal_btn.setEnabled(True)

    def add_goal(self):
        """Add a new goal"""
        from ..utils.qt_imports import QInputDialog

        title, ok = QInputDialog.getText(self, "Add Goal", "Goal title:")
        if ok and title:
            description, ok = QInputDialog.getText(self, "Add Goal", "Goal description:")
            if ok:
                new_goal = {
                    "id": len(self.goals) + 1,
                    "title": title,
                    "description": description,
                    "status": "pending",
                    "priority": "medium",
                    "created_at": datetime.now().isoformat(),
                    "progress": 0,
                }

                self.goals.append(new_goal)
                self.save_goals()
                self.update_goals_display()

    def complete_goal(self):
        """Mark selected goal as completed"""
        current_item = self.goals_list.currentItem()
        if current_item:
            goal = current_item.data(Qt.ItemDataRole.UserRole)
            goal["status"] = "completed"
            goal["progress"] = 100

            self.save_goals()
            self.update_goals_display()
            self.goal_details.clear()

    def remove_goal(self):
        """Remove selected goal"""
        from ..utils.qt_imports import QMessageBox

        current_item = self.goals_list.currentItem()
        if current_item:
            goal = current_item.data(Qt.ItemDataRole.UserRole)

            reply = QMessageBox.question(
                self,
                "Remove Goal",
                f'Are you sure you want to remove "{goal.get("title", "this goal")}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.goals = [g for g in self.goals if g.get("id") != goal.get("id")]
                self.save_goals()
                self.update_goals_display()
                self.goal_details.clear()

    def refresh_goals(self):
        """Refresh goals from storage"""
        self.load_goals()

    def get_goals_summary(self) -> Dict[str, Any]:
        """Get goals summary statistics"""
        total = len(self.goals)
        completed = sum(1 for goal in self.goals if goal.get("status") == "completed")
        in_progress = sum(1 for goal in self.goals if goal.get("status") == "in_progress")

        return {
            "total_goals": total,
            "completed_goals": completed,
            "in_progress_goals": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
        }
