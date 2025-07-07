"""
🔄 Visual Feedback System
========================

Provides visual feedback components for Lyrixaincluding status indicators,
progress bars, loading animations, and real-time AI thinking indicators.
"""

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional


class StatusType(Enum):
    """Types of status indicators"""

    IDLE = "idle"
    THINKING = "thinking"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"


class AnimationType(Enum):
    """Types of animations"""

    SPINNER = "spinner"
    DOTS = "dots"
    WAVE = "wave"
    PULSE = "pulse"
    PROGRESS = "progress"
    TYPEWRITER = "typewriter"


@dataclass
class StatusUpdate:
    """Status update data structure"""

    status: StatusType
    message: str
    timestamp: datetime
    progress: Optional[float] = None
    details: Optional[str] = None


class StatusIndicator:
    """Manages status indicators and visual feedback"""

    def __init__(self):
        self.current_status = StatusType.IDLE
        self.current_message = "Ready"
        self.callbacks: List[Callable[[StatusUpdate], None]] = []
        self.history: List[StatusUpdate] = []
        self.max_history = 100

    def add_callback(self, callback: Callable[[StatusUpdate], None]):
        """Add a callback for status updates"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[StatusUpdate], None]):
        """Remove a status update callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def update_status(
        self,
        status: StatusType,
        message: str,
        progress: Optional[float] = None,
        details: Optional[str] = None,
    ):
        """Update the current status"""
        self.current_status = status
        self.current_message = message

        update = StatusUpdate(
            status=status,
            message=message,
            timestamp=datetime.now(),
            progress=progress,
            details=details,
        )

        # Add to history
        self.history.append(update)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(update)
            except Exception as e:
                print(f"Error in status callback: {e}")

    def get_current_status(self) -> StatusUpdate:
        """Get the current status"""
        return StatusUpdate(
            status=self.current_status,
            message=self.current_message,
            timestamp=datetime.now(),
        )

    def get_history(self, limit: Optional[int] = None) -> List[StatusUpdate]:
        """Get status history"""
        if limit:
            return self.history[-limit:]
        return self.history.copy()


class ProgressIndicator:
    """Manages progress indicators for long-running operations"""

    def __init__(self, total: float = 100.0, description: str = "Processing"):
        self.total = total
        self.current = 0.0
        self.description = description
        self.start_time = time.time()
        self.callbacks: List[Callable[[float, str], None]] = []
        self.is_complete = False

    def add_callback(self, callback: Callable[[float, str], None]):
        """Add a progress update callback"""
        self.callbacks.append(callback)

    def update(self, progress: float, description: Optional[str] = None):
        """Update progress"""
        self.current = min(progress, self.total)
        if description:
            self.description = description

        percentage = (self.current / self.total) * 100

        for callback in self.callbacks:
            try:
                callback(percentage, self.description)
            except Exception as e:
                print(f"Error in progress callback: {e}")

        if self.current >= self.total:
            self.is_complete = True

    def increment(self, amount: float = 1.0, description: Optional[str] = None):
        """Increment progress by amount"""
        self.update(self.current + amount, description)

    def get_percentage(self) -> float:
        """Get current percentage"""
        return (self.current / self.total) * 100

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time

    def get_eta(self) -> Optional[float]:
        """Get estimated time remaining"""
        if self.current <= 0:
            return None

        elapsed = self.get_elapsed_time()
        rate = self.current / elapsed
        remaining = self.total - self.current

        if rate > 0:
            return remaining / rate
        return None


class LoadingAnimation:
    """Manages loading animations"""

    def __init__(self, animation_type: AnimationType = AnimationType.SPINNER):
        self.animation_type = animation_type
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[str], None]] = []
        self.frames = self._get_animation_frames()
        self.frame_delay = 0.1

    def _get_animation_frames(self) -> List[str]:
        """Get animation frames based on type"""
        if self.animation_type == AnimationType.SPINNER:
            return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        elif self.animation_type == AnimationType.DOTS:
            return ["   ", ".  ", ".. ", "..."]
        elif self.animation_type == AnimationType.WAVE:
            return [
                "▁",
                "▂",
                "▃",
                "▄",
                "▅",
                "▆",
                "▇",
                "█",
                "▇",
                "▆",
                "▅",
                "▄",
                "▃",
                "▂",
            ]
        elif self.animation_type == AnimationType.PULSE:
            return ["●", "○", "●", "○"]
        else:
            return ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def add_callback(self, callback: Callable[[str], None]):
        """Add animation frame callback"""
        self.callbacks.append(callback)

    def start(self):
        """Start the animation"""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the animation"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _animate(self):
        """Animation loop"""
        frame_index = 0
        while self.is_running:
            frame = self.frames[frame_index]

            for callback in self.callbacks:
                try:
                    callback(frame)
                except Exception as e:
                    print(f"Error in animation callback: {e}")

            frame_index = (frame_index + 1) % len(self.frames)
            time.sleep(self.frame_delay)


class VisualFeedback:
    """Main visual feedback coordinator"""

    def __init__(self):
        self.status_indicator = StatusIndicator()
        self.loading_animation: Optional[LoadingAnimation] = None
        self.progress_indicators: dict[str, ProgressIndicator] = {}
        self.ai_thinking = False
        self.thinking_animation: Optional[LoadingAnimation] = None

    def show_status(
        self,
        status: StatusType,
        message: str,
        progress: Optional[float] = None,
        details: Optional[str] = None,
    ):
        """Show a status message"""
        self.status_indicator.update_status(status, message, progress, details)

    def show_thinking(self, message: str = "AI is thinking..."):
        """Show AI thinking indicator"""
        if not self.ai_thinking:
            self.ai_thinking = True
            self.thinking_animation = LoadingAnimation(AnimationType.DOTS)
            self.thinking_animation.start()
            self.show_status(StatusType.THINKING, message)

    def hide_thinking(self):
        """Hide AI thinking indicator"""
        if self.ai_thinking:
            self.ai_thinking = False
            if self.thinking_animation:
                self.thinking_animation.stop()
                self.thinking_animation = None
            self.show_status(StatusType.IDLE, "Ready")

    def show_loading(
        self,
        message: str = "Loading...",
        animation_type: AnimationType = AnimationType.SPINNER,
    ):
        """Show loading animation"""
        if self.loading_animation:
            self.loading_animation.stop()

        self.loading_animation = LoadingAnimation(animation_type)
        self.loading_animation.start()
        self.show_status(StatusType.LOADING, message)

    def hide_loading(self):
        """Hide loading animation"""
        if self.loading_animation:
            self.loading_animation.stop()
            self.loading_animation = None
        self.show_status(StatusType.IDLE, "Ready")

    def create_progress(
        self, operation_id: str, total: float = 100.0, description: str = "Processing"
    ) -> ProgressIndicator:
        """Create a new progress indicator"""
        progress = ProgressIndicator(total, description)
        self.progress_indicators[operation_id] = progress
        return progress

    def get_progress(self, operation_id: str) -> Optional[ProgressIndicator]:
        """Get a progress indicator by ID"""
        return self.progress_indicators.get(operation_id)

    def remove_progress(self, operation_id: str):
        """Remove a progress indicator"""
        if operation_id in self.progress_indicators:
            del self.progress_indicators[operation_id]

    def show_success(self, message: str, details: Optional[str] = None):
        """Show success message"""
        self.show_status(StatusType.SUCCESS, message, details=details)

    def show_error(self, message: str, details: Optional[str] = None):
        """Show error message"""
        self.show_status(StatusType.ERROR, message, details=details)

    def show_warning(self, message: str, details: Optional[str] = None):
        """Show warning message"""
        self.show_status(StatusType.WARNING, message, details=details)

    def show_info(self, message: str, details: Optional[str] = None):
        """Show info message"""
        self.show_status(StatusType.INFO, message, details=details)

    def cleanup(self):
        """Clean up resources"""
        if self.loading_animation:
            self.loading_animation.stop()
        if self.thinking_animation:
            self.thinking_animation.stop()

        for _progress in self.progress_indicators.values():
            # Progress indicators don't need explicit cleanup
            pass

        self.progress_indicators.clear()


# Context manager for automatic feedback management
class FeedbackContext:
    """Context manager for automatic feedback management"""

    def __init__(self, feedback: VisualFeedback, operation_type: str = "operation"):
        self.feedback = feedback
        self.operation_type = operation_type
        self.start_time = time.time()

    def __enter__(self):
        self.feedback.show_thinking(f"Starting {self.operation_type}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time

        if exc_type is None:
            self.feedback.show_success(
                f"{self.operation_type.capitalize()} completed successfully",
                details=f"Completed in {elapsed:.2f} seconds",
            )
        else:
            self.feedback.show_error(
                f"{self.operation_type.capitalize()} failed", details=str(exc_val)
            )

        # Reset to idle after a short delay
        threading.Timer(
            2.0, lambda: self.feedback.show_status(StatusType.IDLE, "Ready")
        ).start()
