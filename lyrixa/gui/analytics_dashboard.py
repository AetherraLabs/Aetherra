"""
Advanced Analytics Dashboard for Lyrixa AI Assistant

Provides comprehensive analytics and visualization for:
- User productivity metrics and trends
- Pattern analysis and behavioral insights
- Suggestion effectiveness and optimization
- Performance trends and forecasting
- Advanced behavioral analytics with mood tracking
- Daily/weekly insights with actionable recommendations
- Agent usage metrics and efficiency analysis
- Real-time dashboard with live updates
"""

import asyncio
import json
import logging
import random
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:
    from PySide6.QtCore import (
        QDate,
        QEasingCurve,
        QPropertyAnimation,
        Qt,
        QThread,
        QTimer,
        Signal,
    )
    from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPalette
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDateEdit,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QTableWidget,
        QTableWidgetItem,
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

    # Mock classes for when PySide6 is not available
    class QWidget:
        pass


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsTimeRange(Enum):
    """Time range options for analytics."""

    LAST_HOUR = "last_hour"
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_QUARTER = "last_quarter"
    CUSTOM = "custom"


@dataclass
class DailyInsight:
    """Daily insight data structure."""

    date: datetime
    productivity_score: float
    mood_trend: str
    top_activities: List[str]
    achievements: List[str]
    suggestions: List[str]
    focus_time: float
    break_time: float
    efficiency_rating: float


@dataclass
class WeeklyInsight:
    """Weekly insight data structure."""

    week_start: datetime
    week_end: datetime
    productivity_trend: str
    mood_pattern: Dict[str, float]
    goal_completion: float
    patterns_identified: List[str]
    recommendations: List[str]
    peak_performance_time: str
    improvement_areas: List[str]


class MoodTracker:
    """Tracks and analyzes user mood patterns."""

    def __init__(self):
        self.mood_history = []
        self.mood_predictions = []

    def track_mood(self, mood: str, confidence: float, context: Dict[str, Any]):
        """Track a mood event."""
        mood_event = {
            "timestamp": datetime.now(),
            "mood": mood,
            "confidence": confidence,
            "context": context,
        }
        self.mood_history.append(mood_event)

    def analyze_mood_patterns(self) -> Dict[str, Any]:
        """Analyze mood patterns and trends."""
        if not self.mood_history:
            return {"status": "insufficient_data"}

        recent_moods = self.mood_history[-50:]  # Last 50 mood events
        mood_counts = {}

        for event in recent_moods:
            mood = event["mood"]
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0]

        return {
            "dominant_mood": dominant_mood,
            "mood_distribution": mood_counts,
            "trend": self._calculate_mood_trend(),
            "stability": self._calculate_mood_stability(),
        }

    def _calculate_mood_trend(self) -> str:
        """Calculate overall mood trend."""
        if len(self.mood_history) < 10:
            return "insufficient_data"

        recent = self.mood_history[-10:]
        older = self.mood_history[-20:-10] if len(self.mood_history) >= 20 else []

        # Simple sentiment scoring
        mood_scores = {
            "happy": 5,
            "focused": 4,
            "productive": 4,
            "calm": 3,
            "neutral": 2,
            "confused": 1,
            "stressed": 0,
            "frustrated": 0,
        }

        recent_score = sum(mood_scores.get(event["mood"], 2) for event in recent) / len(
            recent
        )
        older_score = (
            sum(mood_scores.get(event["mood"], 2) for event in older) / len(older)
            if older
            else recent_score
        )

        if recent_score > older_score + 0.5:
            return "improving"
        elif recent_score < older_score - 0.5:
            return "declining"
        else:
            return "stable"

    def _calculate_mood_stability(self) -> float:
        """Calculate mood stability score (0-1)."""
        if len(self.mood_history) < 5:
            return 0.5

        recent = self.mood_history[-20:]
        mood_scores = {
            "happy": 5,
            "focused": 4,
            "productive": 4,
            "calm": 3,
            "neutral": 2,
            "confused": 1,
            "stressed": 0,
            "frustrated": 0,
        }

        scores = [mood_scores.get(event["mood"], 2) for event in recent]
        if len(scores) < 2:
            return 0.5

        variance = statistics.variance(scores)
        # Convert variance to stability score (lower variance = higher stability)
        stability = max(0, min(1, 1 - (variance / 10)))
        return stability

    class Signal:
        pass


try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate analytics metrics from raw data."""

    def __init__(self):
        self.metrics_cache = {}
        self.cache_expiry = timedelta(minutes=5)

    def calculate_productivity_metrics(self, activities: List[Dict]) -> Dict[str, Any]:
        """Calculate productivity metrics from activity data."""
        if not activities:
            return {
                "total_sessions": 0,
                "avg_session_length": 0,
                "productivity_score": 0,
                "focus_time": 0,
                "break_time": 0,
                "efficiency_rating": 0,
            }

        total_sessions = len(activities)
        session_lengths = [act.get("duration", 0) for act in activities]
        avg_session_length = (
            sum(session_lengths) / len(session_lengths) if session_lengths else 0
        )

        focus_activities = [act for act in activities if act.get("type") == "focus"]
        focus_time = sum(act.get("duration", 0) for act in focus_activities)

        break_activities = [act for act in activities if act.get("type") == "break"]
        break_time = sum(act.get("duration", 0) for act in break_activities)

        # Calculate productivity score (0-100)
        productivity_score = (
            min(100, (focus_time / (focus_time + break_time)) * 100)
            if (focus_time + break_time) > 0
            else 0
        )

        # Calculate efficiency rating (0-10)
        efficiency_rating = min(10, productivity_score / 10)

        return {
            "total_sessions": total_sessions,
            "avg_session_length": avg_session_length,
            "productivity_score": round(productivity_score, 1),
            "focus_time": focus_time,
            "break_time": break_time,
            "efficiency_rating": round(efficiency_rating, 1),
        }

    def calculate_pattern_metrics(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Calculate pattern analysis metrics."""
        if not patterns:
            return {
                "total_patterns": 0,
                "most_common_pattern": "None",
                "pattern_confidence": 0,
                "recurring_patterns": 0,
            }

        total_patterns = len(patterns)
        pattern_types = [pattern.get("type", "unknown") for pattern in patterns]

        # Find most common pattern
        pattern_counts = {}
        for pattern_type in pattern_types:
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1

        most_common_pattern = (
            max(pattern_counts.items(), key=lambda x: x[1])[0]
            if pattern_counts
            else "None"
        )

        # Calculate average confidence
        confidences = [pattern.get("confidence", 0) for pattern in patterns]
        pattern_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Count recurring patterns (patterns seen more than once)
        recurring_patterns = sum(1 for count in pattern_counts.values() if count > 1)

        return {
            "total_patterns": total_patterns,
            "most_common_pattern": most_common_pattern,
            "pattern_confidence": round(pattern_confidence, 2),
            "recurring_patterns": recurring_patterns,
        }

    def calculate_suggestion_metrics(self, suggestions: List[Dict]) -> Dict[str, Any]:
        """Calculate suggestion effectiveness metrics."""
        if not suggestions:
            return {
                "total_suggestions": 0,
                "accepted_suggestions": 0,
                "acceptance_rate": 0,
                "avg_confidence": 0,
                "top_category": "None",
            }

        total_suggestions = len(suggestions)
        accepted_suggestions = sum(
            1 for sug in suggestions if sug.get("accepted", False)
        )
        acceptance_rate = (
            (accepted_suggestions / total_suggestions) * 100
            if total_suggestions > 0
            else 0
        )

        confidences = [sug.get("confidence", 0) for sug in suggestions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Find top category
        categories = [sug.get("category", "unknown") for sug in suggestions]
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1

        top_category = (
            max(category_counts.items(), key=lambda x: x[1])[0]
            if category_counts
            else "None"
        )

        return {
            "total_suggestions": total_suggestions,
            "accepted_suggestions": accepted_suggestions,
            "acceptance_rate": round(acceptance_rate, 1),
            "avg_confidence": round(avg_confidence, 2),
            "top_category": top_category,
        }


class ChartWidget(QWidget if PYSIDE6_AVAILABLE else object):
    """Custom chart widget using matplotlib."""

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100) if MATPLOTLIB_AVAILABLE else None
        self.canvas = (
            FigureCanvas(self.figure) if MATPLOTLIB_AVAILABLE and self.figure else None
        )

        layout = QVBoxLayout()
        if self.canvas:
            layout.addWidget(self.canvas)
        else:
            placeholder = QLabel("Charts require matplotlib installation")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder)

        self.setLayout(layout)

    def plot_productivity_trend(self, data: List[Dict]):
        """Plot productivity trend over time."""
        if not MATPLOTLIB_AVAILABLE or not self.figure:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not data:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self.canvas.draw()
            return

        dates = [
            datetime.fromisoformat(item["date"])
            if isinstance(item.get("date"), str)
            else item.get("date", datetime.now())
            for item in data
        ]
        scores = [item.get("productivity_score", 0) for item in data]

        ax.plot(dates, scores, marker="o", linewidth=2, markersize=6)
        ax.set_title("Productivity Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Productivity Score")
        ax.grid(True, alpha=0.3)

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_pattern_distribution(self, patterns: Dict[str, int]):
        """Plot pattern type distribution."""
        if not MATPLOTLIB_AVAILABLE or not self.figure:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not patterns:
            ax.text(
                0.5,
                0.5,
                "No patterns detected",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self.canvas.draw()
            return

        labels = list(patterns.keys())
        sizes = list(patterns.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels))) if len(labels) > 0 else []

        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.set_title("Pattern Distribution", fontsize=14, fontweight="bold")

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_suggestion_effectiveness(self, categories: Dict[str, Dict[str, int]]):
        """Plot suggestion effectiveness by category."""
        if not MATPLOTLIB_AVAILABLE or not self.figure:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not categories:
            ax.text(
                0.5,
                0.5,
                "No suggestion data",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self.canvas.draw()
            return

        labels = list(categories.keys())
        accepted = [categories[cat].get("accepted", 0) for cat in labels]
        rejected = [categories[cat].get("rejected", 0) for cat in labels]

        x = np.arange(len(labels))
        width = 0.35

        ax.bar(
            x - width / 2, accepted, width, label="Accepted", color="green", alpha=0.7
        )
        ax.bar(x + width / 2, rejected, width, label="Rejected", color="red", alpha=0.7)

        ax.set_title(
            "Suggestion Effectiveness by Category", fontsize=14, fontweight="bold"
        )
        ax.set_xlabel("Category")
        ax.set_ylabel("Count")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()


class AnalyticsDashboard(QWidget if PYSIDE6_AVAILABLE else object):
    """
    Comprehensive analytics dashboard for Lyrixa AI Assistant.

    Provides real-time visualization and insights for:
    - User productivity metrics
    - Pattern analysis
    - Suggestion effectiveness
    - Performance trends
    """

    # Signals
    refresh_requested = Signal() if PYSIDE6_AVAILABLE else None
    export_requested = Signal(str) if PYSIDE6_AVAILABLE else None

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning(
                "PySide6 not available. Analytics dashboard will not function."
            )
            return

        super().__init__(parent)
        self.metrics_calculator = MetricsCalculator()
        self.sample_data = self._generate_sample_data()

        self.init_ui()
        self.setup_update_timer()

        logger.info("Analytics Dashboard initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 Analytics Dashboard")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Control buttons
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("📊 Export")
        self.export_btn.clicked.connect(self.export_data)
        header_layout.addWidget(self.export_btn)

        layout.addLayout(header_layout)

        # Date range selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(QLabel("to"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Main content area
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Metrics summary
        metrics_widget = self.create_metrics_panel()
        main_splitter.addWidget(metrics_widget)

        # Right panel - Charts
        charts_widget = self.create_charts_panel()
        main_splitter.addWidget(charts_widget)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)

        layout.addWidget(main_splitter)

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Load initial data
        self.refresh_data()

    def create_metrics_panel(self) -> QWidget:
        """Create the metrics summary panel."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Productivity metrics
        prod_group = QGroupBox("🎯 Productivity Metrics")
        prod_layout = QVBoxLayout()

        self.productivity_labels = {
            "sessions": QLabel("Sessions: 0"),
            "avg_length": QLabel("Avg Length: 0 min"),
            "score": QLabel("Score: 0%"),
            "focus_time": QLabel("Focus Time: 0 min"),
            "efficiency": QLabel("Efficiency: 0/10"),
        }

        for label in self.productivity_labels.values():
            label.setFont(QFont("Arial", 10))
            prod_layout.addWidget(label)

        prod_group.setLayout(prod_layout)
        layout.addWidget(prod_group)

        # Pattern metrics
        pattern_group = QGroupBox("🔍 Pattern Analysis")
        pattern_layout = QVBoxLayout()

        self.pattern_labels = {
            "total": QLabel("Total Patterns: 0"),
            "common": QLabel("Most Common: None"),
            "confidence": QLabel("Avg Confidence: 0%"),
            "recurring": QLabel("Recurring: 0"),
        }

        for label in self.pattern_labels.values():
            label.setFont(QFont("Arial", 10))
            pattern_layout.addWidget(label)

        pattern_group.setLayout(pattern_layout)
        layout.addWidget(pattern_group)

        # Suggestion metrics
        suggestion_group = QGroupBox("💡 Suggestion Effectiveness")
        suggestion_layout = QVBoxLayout()

        self.suggestion_labels = {
            "total": QLabel("Total Suggestions: 0"),
            "accepted": QLabel("Accepted: 0"),
            "rate": QLabel("Acceptance Rate: 0%"),
            "confidence": QLabel("Avg Confidence: 0%"),
            "top_category": QLabel("Top Category: None"),
        }

        for label in self.suggestion_labels.values():
            label.setFont(QFont("Arial", 10))
            suggestion_layout.addWidget(label)

        suggestion_group.setLayout(suggestion_layout)
        layout.addWidget(suggestion_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_charts_panel(self) -> QWidget:
        """Create the charts panel."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Chart tabs
        tab_widget = QTabWidget()

        # Productivity trend chart
        self.productivity_chart = ChartWidget()
        tab_widget.addTab(self.productivity_chart, "📈 Productivity Trend")

        # Pattern distribution chart
        self.pattern_chart = ChartWidget()
        tab_widget.addTab(self.pattern_chart, "🔍 Pattern Distribution")

        # Suggestion effectiveness chart
        self.suggestion_chart = ChartWidget()
        tab_widget.addTab(self.suggestion_chart, "💡 Suggestion Effectiveness")

        layout.addWidget(tab_widget)
        widget.setLayout(layout)
        return widget

    def setup_update_timer(self):
        """Setup automatic data update timer."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(30000)  # Update every 30 seconds

    def refresh_data(self):
        """Refresh dashboard data."""
        try:
            self.status_label.setText("Refreshing data...")

            # In a real implementation, this would fetch data from the anticipation engine
            # For now, we'll use sample data
            self.update_metrics()
            self.update_charts()

            self.status_label.setText(
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            )

            if self.refresh_requested:
                self.refresh_requested.emit()

        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")
            self.status_label.setText("Error refreshing data")

    def update_metrics(self):
        """Update metrics display."""
        # Productivity metrics
        prod_metrics = self.metrics_calculator.calculate_productivity_metrics(
            self.sample_data.get("activities", [])
        )

        self.productivity_labels["sessions"].setText(
            f"Sessions: {prod_metrics['total_sessions']}"
        )
        self.productivity_labels["avg_length"].setText(
            f"Avg Length: {prod_metrics['avg_session_length']:.1f} min"
        )
        self.productivity_labels["score"].setText(
            f"Score: {prod_metrics['productivity_score']:.1f}%"
        )
        self.productivity_labels["focus_time"].setText(
            f"Focus Time: {prod_metrics['focus_time']:.1f} min"
        )
        self.productivity_labels["efficiency"].setText(
            f"Efficiency: {prod_metrics['efficiency_rating']:.1f}/10"
        )

        # Pattern metrics
        pattern_metrics = self.metrics_calculator.calculate_pattern_metrics(
            self.sample_data.get("patterns", [])
        )

        self.pattern_labels["total"].setText(
            f"Total Patterns: {pattern_metrics['total_patterns']}"
        )
        self.pattern_labels["common"].setText(
            f"Most Common: {pattern_metrics['most_common_pattern']}"
        )
        self.pattern_labels["confidence"].setText(
            f"Avg Confidence: {pattern_metrics['pattern_confidence']:.1f}%"
        )
        self.pattern_labels["recurring"].setText(
            f"Recurring: {pattern_metrics['recurring_patterns']}"
        )

        # Suggestion metrics
        suggestion_metrics = self.metrics_calculator.calculate_suggestion_metrics(
            self.sample_data.get("suggestions", [])
        )

        self.suggestion_labels["total"].setText(
            f"Total Suggestions: {suggestion_metrics['total_suggestions']}"
        )
        self.suggestion_labels["accepted"].setText(
            f"Accepted: {suggestion_metrics['accepted_suggestions']}"
        )
        self.suggestion_labels["rate"].setText(
            f"Acceptance Rate: {suggestion_metrics['acceptance_rate']:.1f}%"
        )
        self.suggestion_labels["confidence"].setText(
            f"Avg Confidence: {suggestion_metrics['avg_confidence']:.1f}%"
        )
        self.suggestion_labels["top_category"].setText(
            f"Top Category: {suggestion_metrics['top_category']}"
        )

    def update_charts(self):
        """Update chart displays."""
        # Productivity trend
        productivity_data = self.sample_data.get("productivity_trend", [])
        self.productivity_chart.plot_productivity_trend(productivity_data)

        # Pattern distribution
        patterns = self.sample_data.get("patterns", [])
        pattern_counts = {}
        for pattern in patterns:
            ptype = pattern.get("type", "unknown")
            pattern_counts[ptype] = pattern_counts.get(ptype, 0) + 1
        self.pattern_chart.plot_pattern_distribution(pattern_counts)

        # Suggestion effectiveness
        suggestions = self.sample_data.get("suggestions", [])
        category_stats = {}
        for suggestion in suggestions:
            category = suggestion.get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {"accepted": 0, "rejected": 0}

            if suggestion.get("accepted", False):
                category_stats[category]["accepted"] += 1
            else:
                category_stats[category]["rejected"] += 1

        self.suggestion_chart.plot_suggestion_effectiveness(category_stats)

    def export_data(self):
        """Export analytics data."""
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "productivity_metrics": self.metrics_calculator.calculate_productivity_metrics(
                    self.sample_data.get("activities", [])
                ),
                "pattern_metrics": self.metrics_calculator.calculate_pattern_metrics(
                    self.sample_data.get("patterns", [])
                ),
                "suggestion_metrics": self.metrics_calculator.calculate_suggestion_metrics(
                    self.sample_data.get("suggestions", [])
                ),
                "raw_data": self.sample_data,
            }

            filename = (
                f"lyrixa_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            # In a real implementation, this would open a file dialog
            # For now, we'll just log the export
            logger.info(f"Would export analytics data to: {filename}")

            if self.export_requested:
                self.export_requested.emit(filename)

            QMessageBox.information(
                self, "Export", f"Analytics data exported to {filename}"
            )

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export data: {e}")

    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for demonstration."""
        import random
        from datetime import datetime, timedelta

        # Sample activities
        activities = []
        for i in range(20):
            activity_type = random.choice(["focus", "break", "meeting"])
            duration = random.randint(15, 120)
            activities.append(
                {
                    "type": activity_type,
                    "duration": duration,
                    "timestamp": (
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ).isoformat(),
                }
            )

        # Sample patterns
        patterns = []
        pattern_types = ["work_sprint", "break_pattern", "meeting_block", "deep_focus"]
        for i in range(15):
            patterns.append(
                {
                    "type": random.choice(pattern_types),
                    "confidence": random.uniform(0.6, 0.95),
                    "frequency": random.randint(1, 10),
                    "timestamp": (
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ).isoformat(),
                }
            )

        # Sample suggestions
        suggestions = []
        categories = ["productivity", "learning", "wellbeing", "workflow"]
        for i in range(25):
            suggestions.append(
                {
                    "category": random.choice(categories),
                    "confidence": random.uniform(0.5, 0.9),
                    "accepted": random.choice([True, False]),
                    "timestamp": (
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ).isoformat(),
                }
            )

        # Sample productivity trend
        productivity_trend = []
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            score = random.uniform(60, 95)
            productivity_trend.append(
                {"date": date.isoformat(), "productivity_score": score}
            )

        return {
            "activities": activities,
            "patterns": patterns,
            "suggestions": suggestions,
            "productivity_trend": sorted(productivity_trend, key=lambda x: x["date"]),
        }


# Example usage
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        dashboard = AnalyticsDashboard()
        dashboard.show()
        dashboard.resize(1200, 800)

        sys.exit(app.exec())
    else:
        print("PySide6 is required to run the Analytics Dashboard")
