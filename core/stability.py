"""
🛡️ Stability & Error Handling System
====================================

Comprehensive error handling, graceful degradation, and stability improvements
for the AetherraCode & Lyrixasystem.
"""

import functools
import logging
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""

    RETRY = "retry"
    FALLBACK = "fallback"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    USER_INTERVENTION = "user_intervention"
    SYSTEM_RESTART = "system_restart"


@dataclass
class ErrorContext:
    """Context information for errors"""

    error_type: str
    severity: ErrorSeverity
    component: str
    timestamp: float
    user_message: str
    technical_details: str
    recovery_strategy: RecoveryStrategy
    retry_count: int = 0
    max_retries: int = 3


class StabilityManager:
    """Central stability and error handling manager"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history: List[ErrorContext] = []
        self.recovery_handlers: Dict[str, Callable] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def register_recovery_handler(self, component: str, handler: Callable):
        """Register a recovery handler for a specific component"""
        self.recovery_handlers[component] = handler

    def register_fallback_handler(self, component: str, handler: Callable):
        """Register a fallback handler for a specific component"""
        self.fallback_handlers[component] = handler

    def get_circuit_breaker(self, component: str) -> "CircuitBreaker":
        """Get or create a circuit breaker for a component"""
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = CircuitBreaker(component)
        return self.circuit_breakers[component]


class CircuitBreaker:
    """Circuit breaker pattern for component isolation"""

    def __init__(
        self, component: str, failure_threshold: int = 5, recovery_timeout: int = 60
    ):
        self.component = component
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Check if component can execute based on circuit breaker state"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


# Global stability manager instance
stability_manager = StabilityManager()


def safe_execute(
    component: str = "unknown",
    fallback: Optional[Callable] = None,
    user_message: str = "An error occurred",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    max_retries: int = 3,
):
    """
    Decorator for safe execution with error handling and recovery

    Args:
        component: Name of the component being executed
        fallback: Fallback function to call if operation fails
        user_message: User-friendly error message
        severity: Error severity level
        max_retries: Maximum number of retry attempts
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            circuit_breaker = stability_manager.get_circuit_breaker(component)

            if not circuit_breaker.can_execute():
                stability_manager.logger.warning(
                    f"Circuit breaker open for {component}, using fallback"
                )
                return fallback(*args, **kwargs) if fallback else None

            error_context = ErrorContext(
                error_type="",
                severity=severity,
                component=component,
                timestamp=time.time(),
                user_message=user_message,
                technical_details="",
                recovery_strategy=RecoveryStrategy.RETRY,
                max_retries=max_retries,
            )

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    circuit_breaker.record_success()
                    return result

                except Exception as e:
                    error_context.retry_count = attempt
                    error_context.error_type = type(e).__name__
                    error_context.technical_details = traceback.format_exc()

                    stability_manager.logger.error(
                        f"Error in {component} (attempt {attempt + 1}): {str(e)}"
                    )

                    if attempt < max_retries:
                        # Exponential backoff
                        time.sleep(0.1 * (2**attempt))
                        continue
                    else:
                        # Max retries reached
                        circuit_breaker.record_failure()
                        stability_manager.error_history.append(error_context)

                        # Try recovery handler
                        if component in stability_manager.recovery_handlers:
                            try:
                                return stability_manager.recovery_handlers[component](
                                    error_context, *args, **kwargs
                                )
                            except Exception as recovery_error:
                                stability_manager.logger.error(
                                    f"Recovery handler failed: {recovery_error}"
                                )

                        # Try fallback
                        if fallback:
                            try:
                                return fallback(*args, **kwargs)
                            except Exception as fallback_error:
                                stability_manager.logger.error(
                                    f"Fallback failed: {fallback_error}"
                                )

                        # Final failure - return None or raise based on severity
                        if severity == ErrorSeverity.CRITICAL:
                            raise e
                        return None

        return wrapper

    return decorator


@contextmanager
def stability_context(component: str, operation: str = "operation"):
    """
    Context manager for safe operations

    Args:
        component: Component name
        operation: Operation description
    """
    start_time = time.time()
    try:
        stability_manager.logger.info(f"Starting {operation} in {component}")
        yield
        stability_manager.logger.info(
            f"Completed {operation} in {component} ({time.time() - start_time:.2f}s)"
        )
    except Exception as e:
        stability_manager.logger.error(f"Failed {operation} in {component}: {str(e)}")
        raise


class GracefulDegradation:
    """System for graceful degradation when components fail"""

    def __init__(self):
        self.degradation_levels: Dict[str, List[str]] = {
            "ui": ["rich_formatting", "animations", "themes", "shortcuts"],
            "memory": ["analytics", "search", "compression", "backup"],
            "plugins": ["auto_suggestions", "discovery", "ratings"],
            "chat": ["streaming", "markdown", "history", "formatting"],
        }
        self.current_degradations: Dict[str, List[str]] = {}

    def degrade_component(self, component: str, feature: str):
        """Disable a specific feature of a component"""
        if component not in self.current_degradations:
            self.current_degradations[component] = []
        if feature not in self.current_degradations[component]:
            self.current_degradations[component].append(feature)
            stability_manager.logger.warning(
                f"Degraded {component}: disabled {feature}"
            )

    def is_feature_available(self, component: str, feature: str) -> bool:
        """Check if a feature is currently available"""
        degradations = self.current_degradations.get(component, [])
        return feature not in degradations

    def restore_component(self, component: str, feature: str):
        """Restore a degraded feature"""
        if component in self.current_degradations:
            if feature in self.current_degradations[component]:
                self.current_degradations[component].remove(feature)
                stability_manager.logger.info(
                    f"Restored {component}: enabled {feature}"
                )


# Global degradation manager
degradation_manager = GracefulDegradation()


class PerformanceMonitor:
    """Monitor system performance and trigger degradation if needed"""

    def __init__(self):
        self.performance_history: List[Dict[str, Any]] = []
        self.thresholds = {
            "response_time": 2.0,  # seconds
            "memory_usage": 80,  # percentage
            "cpu_usage": 90,  # percentage
            "error_rate": 0.1,  # 10%
        }

    def record_performance(self, component: str, metrics: Dict[str, Any]):
        """Record performance metrics for a component"""
        record = {"component": component, "timestamp": time.time(), "metrics": metrics}
        self.performance_history.append(record)

        # Check if degradation is needed
        self._check_degradation_triggers(component, metrics)

    def _check_degradation_triggers(self, component: str, metrics: Dict[str, Any]):
        """Check if performance metrics indicate need for degradation"""
        if metrics.get("response_time", 0) > self.thresholds["response_time"]:
            if component == "ui":
                degradation_manager.degrade_component("ui", "animations")
            elif component == "chat":
                degradation_manager.degrade_component("chat", "streaming")

        if metrics.get("error_rate", 0) > self.thresholds["error_rate"]:
            degradation_manager.degrade_component(component, "advanced_features")


# Global performance monitor
performance_monitor = PerformanceMonitor()


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example of safe execution
    @safe_execute(
        component="test_component", user_message="Test operation failed", max_retries=2
    )
    def risky_operation(should_fail: bool = False):
        if should_fail:
            raise ValueError("Simulated failure")
        return "Success!"

    # Test successful operation
    #     print("Testing successful operation:")
    result = risky_operation(False)
    print(f"Result: {result}")

    # Test failed operation with fallback
    print("\nTesting failed operation:")
    result = risky_operation(True)
    print(f"Result: {result}")

    # Test circuit breaker
    print("\nTesting circuit breaker:")
    for i in range(10):
        result = risky_operation(True)
        print(f"Attempt {i + 1}: {result}")

    # Test degradation
    print("\nTesting graceful degradation:")
    print(
        f"UI animations available: {degradation_manager.is_feature_available('ui', 'animations')}"
    )
    degradation_manager.degrade_component("ui", "animations")
    print(
        f"UI animations available: {degradation_manager.is_feature_available('ui', 'animations')}"
    )
