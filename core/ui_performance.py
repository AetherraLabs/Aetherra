#!/usr/bin/env python3
"""
🚀 AetherraCode UI Performance Optimizer
=====================================

Advanced UI performance optimization for AetherraCode & Lyrixa components.
This module enhances responsiveness, reduces memory usage, and improves
rendering performance across all UI components.

Features:
- Widget virtualization for large data sets
- Efficient event handling and debouncing
- Smart rendering and paint optimization
- Memory-efficient widget management
- Adaptive UI scaling and caching
"""

import gc
import time
import weakref
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

try:
    from PySide6.QtCore import QObject, QThread, QTimer, Signal
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QWidget

    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    QTimer = QThread = Signal = QObject = QApplication = QWidget = QPixmap = None


@dataclass
class UIPerformanceMetrics:
    """UI-specific performance metrics"""

    widget_count: int
    render_time: float
    memory_usage: float
    event_queue_size: int
    fps: float
    timestamp: float


class UIOptimizer:
    """Advanced UI performance optimizer"""

    def __init__(self):
        self.metrics_history: deque = deque(maxlen=100)
        self.widget_cache: Dict[str, Any] = {}
        self.render_cache: Dict[str, Any] = {}
        self.event_debounce: Dict[str, float] = {}
        self.widget_refs: List[weakref.ref] = []
        self.optimization_enabled = True

        # Performance thresholds
        self.max_fps = 60
        self.target_render_time = 16.67  # 60 FPS in milliseconds
        self.memory_threshold_mb = 100

        # Setup cleanup timer
        if PYSIDE_AVAILABLE and QTimer:
            self.cleanup_timer = QTimer()
            self.cleanup_timer.timeout.connect(self._cleanup_widgets)
            self.cleanup_timer.start(30000)  # 30 seconds
        else:
            self.cleanup_timer = None

    def optimize_widget_creation(self, widget_class: type, *args, **kwargs) -> Any:
        """Optimize widget creation with caching"""
        if not self.optimization_enabled:
            return widget_class(*args, **kwargs)

        # Generate cache key
        cache_key = (
            f"{widget_class.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
        )

        # Check cache
        if cache_key in self.widget_cache:
            cached_widget = self.widget_cache[cache_key]
            if cached_widget and hasattr(cached_widget, "isVisible"):
                return cached_widget

        # Create new widget
        start_time = time.time()
        widget = widget_class(*args, **kwargs)
        creation_time = (time.time() - start_time) * 1000

        # Cache if creation was expensive
        if creation_time > 10:  # Cache widgets that take >10ms to create
            self.widget_cache[cache_key] = widget
            self.widget_refs.append(weakref.ref(widget))

        return widget

    def debounce_event(
        self, event_name: str, callback: Callable, delay_ms: int = 100
    ) -> bool:
        """Debounce UI events to prevent excessive calls"""
        current_time = time.time() * 1000
        last_time = self.event_debounce.get(event_name, 0)

        if current_time - last_time >= delay_ms:
            self.event_debounce[event_name] = current_time
            callback()
            return True
        return False

    def optimize_render_operation(
        self, operation_name: str, render_func: Callable
    ) -> Any:
        """Optimize rendering operations with caching"""
        if not self.optimization_enabled:
            return render_func()

        # Check render cache
        if operation_name in self.render_cache:
            return self.render_cache[operation_name]

        # Perform rendering
        start_time = time.time()
        result = render_func()
        render_time = (time.time() - start_time) * 1000

        # Cache expensive renders
        if (
            render_time > self.target_render_time
            and PYSIDE_AVAILABLE
            and QPixmap
            and isinstance(result, QPixmap)
        ):
            self.render_cache[operation_name] = result

        return result

    def virtualize_list(self, items: List[Any], visible_count: int = 50) -> List[Any]:
        """Virtualize large lists for better performance"""
        if len(items) <= visible_count * 2:
            return items

        # Return only visible items plus buffer
        buffer_size = visible_count // 2
        return items[: visible_count + buffer_size]

    def batch_ui_updates(self, updates: List[Callable], batch_size: int = 10) -> None:
        """Batch UI updates to reduce repaints"""
        if not PYSIDE_AVAILABLE or not QApplication:
            for update in updates:
                update()
            return

        app = QApplication.instance() if QApplication else None
        if not app:
            for update in updates:
                update()
            return

        # Process updates in batches
        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]

            # Suspend updates
            for update in batch:
                update()

            # Process events to prevent UI freezing
            app.processEvents()

    def measure_ui_performance(self) -> UIPerformanceMetrics:
        """Measure current UI performance"""
        if not PYSIDE_AVAILABLE or not QApplication:
            return UIPerformanceMetrics(0, 0, 0, 0, 0, time.time())

        app = QApplication.instance() if QApplication else None
        widget_count = 0
        if app:
            try:
                # Try to get widget count safely - use try/except for type safety
                widgets = getattr(app, "allWidgets", lambda: [])()
                widget_count = len(list(widgets))
            except Exception:
                try:
                    widgets = getattr(app, "topLevelWidgets", lambda: [])()
                    widget_count = len(list(widgets))
                except Exception:
                    widget_count = 0

        # Measure memory usage
        import psutil

        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        # Estimate FPS (simplified)
        current_time = time.time()
        fps = 60  # Default assumption

        if len(self.metrics_history) > 1:
            time_diff = current_time - self.metrics_history[-1].timestamp
            fps = min(60, 1.0 / time_diff) if time_diff > 0 else 60

        metrics = UIPerformanceMetrics(
            widget_count=widget_count,
            render_time=0,  # Would need more complex measurement
            memory_usage=memory_mb,
            event_queue_size=0,  # Would need event system integration
            fps=fps,
            timestamp=current_time,
        )

        self.metrics_history.append(metrics)
        return metrics

    def get_optimization_suggestions(self) -> List[str]:
        """Get UI optimization suggestions based on metrics"""
        if not self.metrics_history:
            return ["No performance data available"]

        latest = self.metrics_history[-1]
        suggestions = []

        # Widget count optimization
        if latest.widget_count > 1000:
            suggestions.append(
                "Consider widget virtualization - high widget count detected"
            )

        # Memory optimization
        if latest.memory_usage > self.memory_threshold_mb:
            suggestions.append("High memory usage - consider clearing widget caches")

        # FPS optimization
        if latest.fps < 30:
            suggestions.append("Low FPS detected - consider reducing update frequency")

        # Cache optimization
        if len(self.render_cache) > 100:
            suggestions.append(
                "Large render cache - consider clearing old cached renders"
            )

        if not suggestions:
            suggestions.append("UI performance is optimal")

        return suggestions

    def clear_caches(self) -> Dict[str, int]:
        """Clear all performance caches"""
        widget_cache_size = len(self.widget_cache)
        render_cache_size = len(self.render_cache)

        self.widget_cache.clear()
        self.render_cache.clear()
        self.event_debounce.clear()

        # Force garbage collection
        gc.collect()

        return {
            "widgets_cleared": widget_cache_size,
            "renders_cleared": render_cache_size,
            "memory_freed": True,
        }

    def _cleanup_widgets(self) -> None:
        """Clean up dead widget references"""
        active_refs = []
        for ref in self.widget_refs:
            if ref() is not None:
                active_refs.append(ref)

        self.widget_refs = active_refs

        # Clean up widget cache
        dead_keys = []
        for key, widget in self.widget_cache.items():
            if widget is None or (
                hasattr(widget, "isVisible") and not widget.isVisible()
            ):
                dead_keys.append(key)

        for key in dead_keys:
            del self.widget_cache[key]


class ResponsiveUIManager:
    """Manage responsive UI behavior and adaptive performance"""

    def __init__(self):
        self.window_sizes: Dict[str, tuple] = {}
        self.performance_mode = "balanced"  # "performance", "balanced", "quality"
        self.adaptive_settings = {
            "performance": {"max_fps": 30, "cache_size": 50, "update_interval": 100},
            "balanced": {"max_fps": 60, "cache_size": 100, "update_interval": 50},
            "quality": {"max_fps": 120, "cache_size": 200, "update_interval": 16},
        }

    def adapt_to_performance(self, metrics: UIPerformanceMetrics) -> Dict[str, Any]:
        """Adapt UI settings based on performance metrics"""
        adaptations = {}

        # Auto-adjust performance mode
        if metrics.fps < 20 and self.performance_mode != "performance":
            self.performance_mode = "performance"
            adaptations["mode_change"] = "performance"
        elif (
            metrics.fps > 50
            and metrics.memory_usage < 50
            and self.performance_mode != "quality"
        ):
            self.performance_mode = "quality"
            adaptations["mode_change"] = "quality"

        # Apply adaptive settings
        settings = self.adaptive_settings[self.performance_mode]
        adaptations.update(settings)

        return adaptations

    def optimize_for_screen_size(self, width: int, height: int) -> Dict[str, Any]:
        """Optimize UI for specific screen size"""
        optimizations = {}

        # Small screens (mobile/tablet)
        if width < 1200 or height < 800:
            optimizations.update(
                {
                    "simplified_ui": True,
                    "reduced_animations": True,
                    "smaller_cache": True,
                    "touch_optimized": True,
                }
            )

        # Large screens (desktop/4K)
        elif width > 2000 or height > 1200:
            optimizations.update(
                {
                    "enhanced_details": True,
                    "larger_cache": True,
                    "high_quality_renders": True,
                    "multi_panel_layout": True,
                }
            )

        return optimizations


# Global UI optimizer instance
ui_optimizer = UIOptimizer()
responsive_manager = ResponsiveUIManager()


# Decorators for UI optimization
def ui_optimized(cache_renders: bool = False, debounce_ms: int = 0):
    """Decorator for UI performance optimization"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if debounce_ms > 0:
                event_name = f"{func.__name__}:{id(func)}"
                if not ui_optimizer.debounce_event(
                    event_name, lambda: None, debounce_ms
                ):
                    return  # Event was debounced

            if cache_renders:
                operation_name = (
                    f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
                )
                return ui_optimizer.optimize_render_operation(
                    operation_name, lambda: func(*args, **kwargs)
                )
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def batch_ui_operation(batch_size: int = 10):
    """Decorator for batching UI operations"""

    def decorator(func):
        def wrapper(items, *args, **kwargs):
            if not isinstance(items, list):
                return func(items, *args, **kwargs)

            operations = [
                lambda item=item: func(item, *args, **kwargs) for item in items
            ]
            ui_optimizer.batch_ui_updates(operations, batch_size)

        return wrapper

    return decorator


# Utility functions
def optimize_ui_startup() -> Dict[str, Any]:
    """Optimize UI startup performance"""
    results = {}

    # Clear old caches
    cache_results = ui_optimizer.clear_caches()
    results.update(cache_results)

    # Set performance mode
    responsive_manager.performance_mode = "performance"
    results["startup_mode"] = "performance"

    return results


def get_ui_performance_report() -> Dict[str, Any]:
    """Get comprehensive UI performance report"""
    metrics = ui_optimizer.measure_ui_performance()
    suggestions = ui_optimizer.get_optimization_suggestions()

    return {
        "current_metrics": {
            "widget_count": metrics.widget_count,
            "memory_usage_mb": metrics.memory_usage,
            "fps": metrics.fps,
            "timestamp": metrics.timestamp,
        },
        "cache_stats": {
            "widget_cache_size": len(ui_optimizer.widget_cache),
            "render_cache_size": len(ui_optimizer.render_cache),
            "debounce_events": len(ui_optimizer.event_debounce),
        },
        "optimization_suggestions": suggestions,
        "performance_mode": responsive_manager.performance_mode,
    }


if __name__ == "__main__":
    # Example usage
    print("🎨 AetherraCode UI Performance Optimizer")
    print("=" * 50)

    # Test UI optimization
    if PYSIDE_AVAILABLE:
        # Simulate widget creation optimization
        @ui_optimized(cache_renders=True, debounce_ms=100)
        def create_optimized_widget():
            print("Creating optimized widget...")
            return "widget"

        # Test performance measurement
        metrics = ui_optimizer.measure_ui_performance()
        print(
            f"📊 Current metrics: {metrics.widget_count} widgets, {metrics.memory_usage:.1f}MB"
        )

        # Get optimization suggestions
        suggestions = ui_optimizer.get_optimization_suggestions()
        print(f"💡 Suggestions: {', '.join(suggestions)}")
    else:
        print("⚠️ PySide6 not available - UI optimization disabled")

    # Test responsive management
    adaptations = responsive_manager.adapt_to_performance(
        UIPerformanceMetrics(100, 16.7, 50, 0, 60, time.time())
    )
    print(f"🔧 Adaptive settings: {adaptations}")
