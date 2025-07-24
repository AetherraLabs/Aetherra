"""
Context Summary Line - Real-Time Thought Label
Shows what Lyrixa is currently thinking about or focusing on
"""

import time

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QWidget


class ContextSummaryLine(QWidget):
    """🧠 Real-Time Context Summary - Shows Lyrixa's current focus"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)

        # State variables
        self.current_context = "Initializing cognitive systems..."
        self.context_confidence = 0.8
        self.last_update = time.time()
        self.is_animating = False

        # Visual properties
        self.text_offset = 0
        self.fade_alpha = 1.0

        # Animation timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)  # 10 FPS for smooth text animation

        # Context update timer
        self.context_timer = QTimer(self)
        self.context_timer.timeout.connect(self.request_context_update)
        self.context_timer.start(15000)  # Update every 15 seconds

        # Animation properties
        self.slide_animation = None

    def update_context(self, context_text, confidence=0.8):
        """Update the context summary with new information"""
        if context_text and context_text != self.current_context:
            self.animate_context_change(context_text, confidence)

    def animate_context_change(self, new_context, confidence):
        """Animate the transition to new context"""
        self.is_animating = True
        self.context_confidence = confidence

        # Start fade out
        self.fade_alpha = 0.0

        # Schedule context change after fade
        QTimer.singleShot(200, lambda: self.complete_context_change(new_context))

    def complete_context_change(self, new_context):
        """Complete the context change animation"""
        self.current_context = new_context
        self.last_update = time.time()
        self.fade_alpha = 1.0
        self.is_animating = False
        self.update()

    def request_context_update(self):
        """Signal that we need a context update"""
        # This will be connected to the main window to get fresh context
        pass

    def get_context_prefix(self):
        """Get appropriate prefix emoji based on context content"""
        context_lower = self.current_context.lower()

        if "thinking" in context_lower or "analyzing" in context_lower:
            return "🤔"
        elif "memory" in context_lower or "remembering" in context_lower:
            return "🧠"
        elif "processing" in context_lower:
            return "⚙️"
        elif "learning" in context_lower:
            return "📚"
        elif "reflecting" in context_lower:
            return "🔮"
        elif "planning" in context_lower:
            return "📋"
        elif "curious" in context_lower or "exploring" in context_lower:
            return "🔍"
        elif "creating" in context_lower or "generating" in context_lower:
            return "✨"
        else:
            return "💭"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        self.draw_background(painter)

        # Context text
        self.draw_context_text(painter)

        # Confidence indicator
        self.draw_confidence_indicator(painter)

    def draw_background(self, painter):
        """Draw subtle background gradient"""
        # Background based on confidence level
        if self.context_confidence > 0.8:
            bg_color = QColor(0, 40, 20, 30)  # Green tint for high confidence
        elif self.context_confidence > 0.6:
            bg_color = QColor(20, 20, 40, 30)  # Blue tint for medium confidence
        else:
            bg_color = QColor(40, 20, 0, 30)  # Orange tint for low confidence

        painter.fillRect(self.rect(), bg_color)

        # Subtle border
        border_color = QColor(0, 255, 136, 50)
        painter.setPen(border_color)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

    def draw_context_text(self, painter):
        """Draw the main context text"""
        # Set font
        font = QFont("JetBrains Mono", 11)
        painter.setFont(font)

        # Text color with fade effect
        text_color = QColor(0, 255, 136)  # Aetherra green
        text_color.setAlphaF(self.fade_alpha)
        painter.setPen(text_color)

        # Get prefix emoji
        prefix = self.get_context_prefix()
        full_text = f"{prefix} {self.current_context}"

        # Calculate text position
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.horizontalAdvance(full_text)
        text_height = font_metrics.height()

        # Center vertically, with small left margin
        x = 15 + self.text_offset
        y = (self.height() + text_height // 2) // 2

        # Draw text
        painter.drawText(x, y, full_text)

        # Add subtle glow effect for high confidence
        if self.context_confidence > 0.8:
            glow_color = QColor(0, 255, 136, 30)
            painter.setPen(glow_color)
            painter.drawText(x + 1, y + 1, full_text)

    def draw_confidence_indicator(self, painter):
        """Draw confidence level indicator"""
        # Small confidence bar on the right
        bar_width = 4
        bar_height = 20
        bar_x = self.width() - bar_width - 10
        bar_y = (self.height() - bar_height) // 2

        # Background
        bg_color = QColor(60, 60, 60, 100)
        painter.fillRect(bar_x, bar_y, bar_width, bar_height, bg_color)

        # Confidence fill
        fill_height = int(bar_height * self.context_confidence)
        fill_y = bar_y + (bar_height - fill_height)

        # Color based on confidence level
        if self.context_confidence > 0.8:
            fill_color = QColor(0, 255, 136)  # Green
        elif self.context_confidence > 0.6:
            fill_color = QColor(0, 136, 255)  # Blue
        else:
            fill_color = QColor(255, 136, 0)  # Orange

        painter.fillRect(bar_x, fill_y, bar_width, fill_height, fill_color)

    def get_contextual_summary(self, lyrixa_systems):
        """Generate context summary from Lyrixa systems"""
        try:
            summaries = []

            # Check memory engine
            if (
                hasattr(lyrixa_systems, "lyrixa_memory_engine")
                and lyrixa_systems.lyrixa_memory_engine
            ):
                if hasattr(lyrixa_systems.lyrixa_memory_engine, "get_current_focus"):
                    focus = lyrixa_systems.lyrixa_memory_engine.get_current_focus()
                    if focus:
                        summaries.append(f"Memory focus: {focus}")

            # Check context bridge
            if (
                hasattr(lyrixa_systems, "lyrixa_context_bridge")
                and lyrixa_systems.lyrixa_context_bridge
            ):
                if hasattr(lyrixa_systems.lyrixa_context_bridge, "get_current_context"):
                    context = lyrixa_systems.lyrixa_context_bridge.get_current_context()
                    if context:
                        summaries.append(f"Processing: {context}")

            # Check self model
            if (
                hasattr(lyrixa_systems, "lyrixa_self_model")
                and lyrixa_systems.lyrixa_self_model
            ):
                if hasattr(lyrixa_systems.lyrixa_self_model, "get_current_goal"):
                    goal = lyrixa_systems.lyrixa_self_model.get_current_goal()
                    if goal:
                        summaries.append(f"Goal: {goal}")

            # Return most relevant summary
            if summaries:
                return summaries[0], 0.9
            else:
                # Fallback contextual summaries
                fallback_contexts = [
                    ("Analyzing conversation patterns and user preferences", 0.8),
                    ("Integrating new information into knowledge base", 0.7),
                    ("Reflecting on recent interactions and learning", 0.8),
                    ("Optimizing memory coherence and system stability", 0.9),
                    ("Processing ethical implications of responses", 0.8),
                    ("Exploring creative approaches to problem solving", 0.7),
                    ("Monitoring system performance and self-improvement", 0.9),
                    ("Synthesizing insights from multiple data sources", 0.8),
                ]

                import random

                context, confidence = random.choice(fallback_contexts)
                return context, confidence

        except Exception as e:
            return f"System processing... ({str(e)[:20]})", 0.5

    def update_from_lyrixa(self, lyrixa_systems):
        """Update context from Lyrixa systems"""
        context, confidence = self.get_contextual_summary(lyrixa_systems)
        self.update_context(context, confidence)
