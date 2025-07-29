"""
AI Presence Projection - Mini-Lyrixa Avatar
A dynamic AI glyph that visualizes Lyrixa's cognitive state
"""

import math

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget


class MiniLyrixaAvatar(QWidget):
    """🔥 AI Presence Projection - Dynamic cognitive avatar"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Animation state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)  # ~30 FPS for smooth animation
        self.phase = 0.0

        # Cognitive state variables
        self.emotional_state = "neutral"
        self.reasoning_intensity = 0.5  # 0.0 = idle, 1.0 = deep thought
        self.confidence_level = 0.8
        self.curiosity_level = 0.7
        self.coherence_level = 0.85

        # Visual parameters
        self.base_size = 60
        self.glyph_complexity = 3  # Number of elements in the glyph
        self.pulse_speed = 1.0

        # Animation properties
        self.expansion_factor = 1.0
        self.rotation_angle = 0.0

    def update_cognitive_state(self, state_data):
        """Update avatar based on Lyrixa's cognitive state"""
        self.emotional_state = state_data.get("emotional_state", "neutral")
        self.reasoning_intensity = state_data.get("reasoning_intensity", 0.5)
        self.confidence_level = state_data.get("confidence", 0.8)
        self.curiosity_level = state_data.get("curiosity", 0.7)
        self.coherence_level = state_data.get("coherence", 0.85)

        # Adjust visual parameters based on state
        if self.reasoning_intensity > 0.8:
            self.glyph_complexity = 5  # More complex when thinking hard
            self.pulse_speed = 2.0
        elif self.reasoning_intensity < 0.3:
            self.glyph_complexity = 2  # Simpler when idle
            self.pulse_speed = 0.5
        else:
            self.glyph_complexity = 3
            self.pulse_speed = 1.0

    def get_emotional_color(self):
        """Get color based on emotional state"""
        colors = {
            "curious": QColor("#00ff88"),  # Bright green
            "confident": QColor("#0088ff"),  # Blue
            "uncertain": QColor("#ff8800"),  # Orange
            "processing": QColor("#8800ff"),  # Purple
            "neutral": QColor("#00ff88"),  # Default green
            "excited": QColor("#ffff00"),  # Yellow
            "focused": QColor("#ff0088"),  # Magenta
        }
        return colors.get(self.emotional_state, colors["neutral"])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center position
        center_x = self.width() // 2
        center_y = self.height() // 2

        # Dynamic expansion based on reasoning intensity
        self.expansion_factor = 0.8 + (
            0.4
            * self.reasoning_intensity
            * (1 + 0.3 * math.sin(self.phase * self.pulse_speed))
        )

        # Draw outer energy rings (based on coherence)
        self.draw_energy_rings(painter, center_x, center_y)

        # Draw main glyph (based on complexity and state)
        self.draw_ai_glyph(painter, center_x, center_y)

        # Draw confidence indicator
        self.draw_confidence_core(painter, center_x, center_y)

        # Update animation phase
        self.phase += 0.05

    def draw_energy_rings(self, painter, center_x, center_y):
        """Draw pulsing energy rings around the avatar"""
        base_color = self.get_emotional_color()

        for i in range(3):
            # Ring properties
            ring_radius = (self.base_size + i * 15) * self.expansion_factor

            # Alpha based on coherence and pulse
            alpha = 0.1 + (
                0.2
                * self.coherence_level
                * (1 + 0.5 * math.sin(self.phase * 2 + i * 0.8))
            )

            color = QColor(base_color)
            color.setAlphaF(alpha)

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawEllipse(
                int(center_x - ring_radius),
                int(center_y - ring_radius),
                int(ring_radius * 2),
                int(ring_radius * 2),
            )

    def draw_ai_glyph(self, painter, center_x, center_y):
        """Draw the main AI glyph - changes complexity based on reasoning"""
        base_color = self.get_emotional_color()

        # Rotation based on curiosity
        self.rotation_angle += self.curiosity_level * 0.02

        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle * 180 / math.pi)

        # Draw glyph elements based on complexity
        for i in range(self.glyph_complexity):
            angle = (2 * math.pi * i) / self.glyph_complexity

            # Element position
            radius = 20 * self.expansion_factor
            x = radius * math.cos(angle + self.phase * 0.5)
            y = radius * math.sin(angle + self.phase * 0.5)

            # Element size based on confidence
            element_size = 8 + (6 * self.confidence_level)

            # Color variation based on reasoning intensity
            color = QColor(base_color)
            intensity_variation = 0.5 + (0.5 * self.reasoning_intensity)
            color = color.lighter(int(100 + 50 * intensity_variation))

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawEllipse(
                int(x - element_size / 2),
                int(y - element_size / 2),
                int(element_size),
                int(element_size),
            )

        painter.restore()

    def draw_confidence_core(self, painter, center_x, center_y):
        """Draw central confidence indicator"""
        # Core size based on confidence level
        core_size = 12 + (8 * self.confidence_level)

        # Core color - brighter when more confident
        base_color = self.get_emotional_color()
        core_color = base_color.lighter(int(150 + 50 * self.confidence_level))

        # Pulsing alpha
        alpha = 0.6 + (0.4 * math.sin(self.phase * 3))
        core_color.setAlphaF(alpha)

        painter.setBrush(QBrush(core_color))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            int(center_x - core_size / 2),
            int(center_y - core_size / 2),
            int(core_size),
            int(core_size),
        )

    def set_reasoning_mode(self, intensity):
        """Trigger reasoning animation"""
        self.reasoning_intensity = min(1.0, max(0.0, intensity))
        if intensity > 0.8:
            # Start expansion animation for deep thought
            self.start_expansion_animation()

    def start_expansion_animation(self):
        """Animate expansion during deep reasoning"""
        # This could be enhanced with QPropertyAnimation for smoother effects
        pass

    def set_emotional_state(self, emotion):
        """Change emotional state"""
        valid_emotions = [
            "curious",
            "confident",
            "uncertain",
            "processing",
            "neutral",
            "excited",
            "focused",
        ]
        if emotion in valid_emotions:
            self.emotional_state = emotion
