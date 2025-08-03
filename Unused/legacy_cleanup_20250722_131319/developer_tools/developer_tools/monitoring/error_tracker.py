"""
Error Tracking System - Centralized error logging and analysis for Aetherra & Lyrixa

This module provides comprehensive error tracking including:
- Centralized error logging
- Error categorization and analysis
- Stack trace capture and analysis
- Error rate monitoring
- Alert integration
- Error trend analysis
"""

import os
import json
import time
import traceback
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib
import sys
from contextlib import contextmanager


@dataclass
class ErrorConfig:
    """Configuration for error tracking"""
    # Storage
    error_log_file: str = "error_tracker.log"
    error_data_file: str = "error_data.json"
    max_errors_stored: int = 1000

    # Analysis
    duplicate_threshold: int = 5  # Same error this many times = duplicate
    error_rate_window: int = 300  # 5 minutes in seconds
    critical_error_rate: int = 10  # errors per window

    # Reporting
    daily_report: bool = True
    report_file: str = "daily_error_report.md"

    # Integration
    health_dashboard_integration: bool = True
    alert_on_critical: bool = True

    # Filtering
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "KeyboardInterrupt",
        "SystemExit"
    ])


@dataclass
class ErrorRecord:
    """Individual error record"""
    timestamp: float
    error_type: str
    error_message: str
    error_hash: str
    stack_trace: str
    context: Dict[str, Any]
    severity: str = "error"  # debug, info, warning, error, critical
    category: str = "general"
    count: int = 1
    first_seen: float = 0
    last_seen: float = 0
    resolved: bool = False
    tags: List[str] = field(default_factory=list)


class ErrorTracker:
    """Comprehensive error tracking and analysis system"""

    def __init__(self, config: Optional[ErrorConfig] = None):
        self.config = config or ErrorConfig()
        self.errors: Dict[str, ErrorRecord] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

        # Setup logging
        self.logger = self._setup_logger()

        # Load existing data
        self._load_error_data()

        # Register global exception handler if requested
        self.original_excepthook = sys.excepthook

        self.logger.info("Error Tracker initialized")

    def _setup_logger(self) -> logging.Logger:
        """Setup error tracking logger"""
        logger = logging.getLogger(f"{__name__}_errors")
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.config.error_log_file)
        file_handler.setLevel(logging.ERROR)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def enable_global_tracking(self) -> None:
        """Enable global exception tracking"""
        sys.excepthook = self._global_exception_handler
        print("🔍 Global error tracking enabled")

    def disable_global_tracking(self) -> None:
        """Disable global exception tracking"""
        sys.excepthook = self.original_excepthook
        print("🔍 Global error tracking disabled")

    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if exc_type in (KeyboardInterrupt, SystemExit):
            # Don't track these
            self.original_excepthook(exc_type, exc_value, exc_traceback)
            return

        # Track the error
        self.track_error(
            error=exc_value,
            context={"global_handler": True},
            severity="critical"
        )

        # Call original handler
        self.original_excepthook(exc_type, exc_value, exc_traceback)

    @contextmanager
    def track_context(self, context_name: str, **context_data):
        """Context manager for tracking errors in specific contexts"""
        try:
            yield
        except Exception as e:
            self.track_error(
                error=e,
                context={
                    "context_name": context_name,
                    **context_data
                },
                severity="error"
            )
            raise

    def track_error(self,
                   error: Optional[Exception] = None,
                   error_message: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None,
                   severity: str = "error",
                   category: str = "general",
                   tags: Optional[List[str]] = None) -> str:
        """Track an error occurrence"""

        timestamp = time.time()
        context = context or {}
        tags = tags or []

        # Handle different input types
        if error is not None:
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
        else:
            error_type = "ManualError"
            error_message = error_message or "Unknown error"
            stack_trace = "".join(traceback.format_stack())

        # Check if we should ignore this error
        if any(pattern in error_type for pattern in self.config.ignore_patterns):
            return ""

        # Generate error hash for deduplication
        error_hash = self._generate_error_hash(error_type, error_message, stack_trace)

        with self.lock:
            if error_hash in self.errors:
                # Update existing error
                existing = self.errors[error_hash]
                existing.count += 1
                existing.last_seen = timestamp
                existing.context.update(context)

                # Add new tags
                for tag in tags:
                    if tag not in existing.tags:
                        existing.tags.append(tag)

            else:
                # Create new error record
                self.errors[error_hash] = ErrorRecord(
                    timestamp=timestamp,
                    error_type=error_type,
                    error_message=error_message,
                    error_hash=error_hash,
                    stack_trace=stack_trace,
                    context=context,
                    severity=severity,
                    category=category,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    tags=tags
                )

            # Add to history
            self.error_history.append({
                "timestamp": timestamp,
                "error_hash": error_hash,
                "severity": severity,
                "category": category
            })

            # Cleanup old history
            cutoff_time = timestamp - (7 * 24 * 3600)  # 7 days
            self.error_history = [h for h in self.error_history if h["timestamp"] > cutoff_time]

        # Log the error
        self.logger.error(f"[{category}] {error_type}: {error_message}")

        # Check for critical conditions
        self._check_critical_conditions()

        return error_hash

    def _generate_error_hash(self, error_type: str, message: str, stack_trace: str) -> str:
        """Generate unique hash for error deduplication"""
        # Use error type + message + simplified stack trace
        stack_lines = stack_trace.split('\n')
        # Keep only file/function lines, ignore line numbers
        relevant_stack = []
        for line in stack_lines:
            if 'File "' in line and 'line' in line:
                # Extract file and function, ignore line number
                parts = line.split(', ')
                if len(parts) >= 2:
                    file_part = parts[0]
                    func_part = parts[1] if len(parts) > 1 else ""
                    relevant_stack.append(f"{file_part}, {func_part}")

        hash_content = f"{error_type}|{message}|{'|'.join(relevant_stack[-5:])}"  # Last 5 stack frames
        return hashlib.md5(hash_content.encode()).hexdigest()[:12]

    def _check_critical_conditions(self) -> None:
        """Check for critical error conditions"""
        current_time = time.time()
        window_start = current_time - self.config.error_rate_window

        # Count recent errors
        recent_errors = [h for h in self.error_history if h["timestamp"] > window_start]

        if len(recent_errors) >= self.config.critical_error_rate:
            self.logger.critical(f"Critical error rate: {len(recent_errors)} errors in {self.config.error_rate_window} seconds")

            if self.config.alert_on_critical:
                print(f"🚨 CRITICAL: High error rate detected - {len(recent_errors)} errors in {self.config.error_rate_window//60} minutes")

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for time period"""
        cutoff_time = time.time() - (hours * 3600)

        # Recent errors
        recent_history = [h for h in self.error_history if h["timestamp"] > cutoff_time]
        recent_errors = {h: e for h, e in self.errors.items() if e.last_seen > cutoff_time}

        # Category breakdown
        categories = {}
        for error in recent_errors.values():
            cat = error.category
            if cat not in categories:
                categories[cat] = {"count": 0, "unique": 0}
            categories[cat]["count"] += error.count
            categories[cat]["unique"] += 1

        # Severity breakdown
        severities = {}
        for error in recent_errors.values():
            sev = error.severity
            if sev not in severities:
                severities[sev] = {"count": 0, "unique": 0}
            severities[sev]["count"] += error.count
            severities[sev]["unique"] += 1

        # Top errors
        top_errors = sorted(recent_errors.values(), key=lambda x: x.count, reverse=True)[:10]

        return {
            "time_period_hours": hours,
            "total_occurrences": len(recent_history),
            "unique_errors": len(recent_errors),
            "categories": categories,
            "severities": severities,
            "top_errors": [
                {
                    "hash": e.error_hash,
                    "type": e.error_type,
                    "message": e.error_message[:100] + "..." if len(e.error_message) > 100 else e.error_message,
                    "count": e.count,
                    "severity": e.severity,
                    "last_seen": e.last_seen
                }
                for e in top_errors
            ],
            "error_rate": len(recent_history) / hours if hours > 0 else 0
        }

    def get_error_details(self, error_hash: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific error"""
        if error_hash not in self.errors:
            return None

        error = self.errors[error_hash]

        # Get occurrence timestamps
        occurrences = [h["timestamp"] for h in self.error_history if h["error_hash"] == error_hash]

        return {
            "hash": error.error_hash,
            "type": error.error_type,
            "message": error.error_message,
            "severity": error.severity,
            "category": error.category,
            "count": error.count,
            "first_seen": error.first_seen,
            "last_seen": error.last_seen,
            "stack_trace": error.stack_trace,
            "context": error.context,
            "tags": error.tags,
            "resolved": error.resolved,
            "occurrences": occurrences
        }

    def analyze_error_trends(self, hours: int = 168) -> Dict[str, Any]:  # 7 days default
        """Analyze error trends over time"""
        cutoff_time = time.time() - (hours * 3600)
        recent_history = [h for h in self.error_history if h["timestamp"] > cutoff_time]

        if not recent_history:
            return {"error": "No error data for the specified time period"}

        # Group by hour
        hourly_counts = {}
        for error in recent_history:
            hour = int(error["timestamp"] // 3600)
            if hour not in hourly_counts:
                hourly_counts[hour] = 0
            hourly_counts[hour] += 1

        # Calculate trends
        hours_sorted = sorted(hourly_counts.keys())
        if len(hours_sorted) < 2:
            trend = "insufficient_data"
        else:
            first_half = hours_sorted[:len(hours_sorted)//2]
            second_half = hours_sorted[len(hours_sorted)//2:]

            first_avg = sum(hourly_counts[h] for h in first_half) / len(first_half)
            second_avg = sum(hourly_counts[h] for h in second_half) / len(second_half)

            if second_avg > first_avg * 1.2:
                trend = "increasing"
            elif second_avg < first_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"

        # Find peak error hours
        peak_hour = max(hourly_counts.keys(), key=lambda h: hourly_counts[h]) if hourly_counts else None

        return {
            "analysis_period_hours": hours,
            "total_errors": len(recent_history),
            "hourly_distribution": hourly_counts,
            "trend": trend,
            "peak_error_hour": peak_hour,
            "peak_error_count": hourly_counts.get(peak_hour, 0) if peak_hour else 0,
            "average_errors_per_hour": len(recent_history) / hours if hours > 0 else 0
        }

    def mark_error_resolved(self, error_hash: str, resolution_note: str = "") -> bool:
        """Mark an error as resolved"""
        if error_hash not in self.errors:
            return False

        self.errors[error_hash].resolved = True
        self.errors[error_hash].context["resolution_note"] = resolution_note
        self.errors[error_hash].context["resolved_at"] = time.time()

        self.logger.info(f"Error {error_hash} marked as resolved: {resolution_note}")
        return True

    def generate_daily_report(self) -> str:
        """Generate daily error report"""
        summary = self.get_error_summary(hours=24)
        trends = self.analyze_error_trends(hours=168)  # 7 days for trend

        report_date = datetime.now().strftime("%Y-%m-%d")

        report = f"""# Error Tracking Report - {report_date}

## 📊 24-Hour Summary

- **Total Error Occurrences**: {summary['total_occurrences']}
- **Unique Errors**: {summary['unique_errors']}
- **Error Rate**: {summary['error_rate']:.2f} errors/hour

## 🎯 Error Categories

"""

        for category, data in summary['categories'].items():
            report += f"- **{category.title()}**: {data['count']} occurrences ({data['unique']} unique)\n"

        report += f"""
## [WARN] Severity Breakdown

"""

        for severity, data in summary['severities'].items():
            report += f"- **{severity.title()}**: {data['count']} occurrences ({data['unique']} unique)\n"

        report += f"""
## 🔥 Top Errors (Last 24h)

"""

        for i, error in enumerate(summary['top_errors'][:5], 1):
            last_seen = datetime.fromtimestamp(error['last_seen']).strftime("%H:%M")
            report += f"{i}. **{error['type']}** (Count: {error['count']}, Last: {last_seen})\n"
            report += f"   - {error['message']}\n"
            report += f"   - Severity: {error['severity']}\n\n"

        report += f"""
## 📈 7-Day Trend Analysis

- **Trend**: {trends['trend'].title()}
- **Average Errors/Hour**: {trends['average_errors_per_hour']:.2f}
- **Peak Hour**: {trends.get('peak_error_hour', 'N/A')} ({trends.get('peak_error_count', 0)} errors)

## 🎯 Recommendations

"""

        # Add recommendations based on data
        if summary['total_occurrences'] > 50:
            report += "- [WARN] High error volume detected - investigate top errors\n"

        if trends['trend'] == 'increasing':
            report += "- 📈 Error rate is increasing - monitor closely\n"

        critical_errors = [e for e in summary['top_errors'] if e['severity'] == 'critical']
        if critical_errors:
            report += f"- 🚨 {len(critical_errors)} critical errors need immediate attention\n"

        unresolved_count = len([e for e in self.errors.values() if not e.resolved])
        if unresolved_count > 10:
            report += f"- 📋 {unresolved_count} unresolved errors - consider reviewing\n"

        report += f"""
---
*Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by Error Tracker*
"""

        # Save report
        if self.config.daily_report:
            with open(self.config.report_file, 'w', encoding='utf-8') as f:
                f.write(report)

        return report

    def _save_error_data(self) -> None:
        """Save error data to file"""
        try:
            # Limit stored errors
            if len(self.errors) > self.config.max_errors_stored:
                # Keep most recent errors
                sorted_errors = sorted(self.errors.values(), key=lambda x: x.last_seen, reverse=True)
                self.errors = {e.error_hash: e for e in sorted_errors[:self.config.max_errors_stored]}

            data = {
                "timestamp": time.time(),
                "errors": {
                    error_hash: {
                        "timestamp": error.timestamp,
                        "error_type": error.error_type,
                        "error_message": error.error_message,
                        "error_hash": error.error_hash,
                        "stack_trace": error.stack_trace,
                        "context": error.context,
                        "severity": error.severity,
                        "category": error.category,
                        "count": error.count,
                        "first_seen": error.first_seen,
                        "last_seen": error.last_seen,
                        "resolved": error.resolved,
                        "tags": error.tags
                    }
                    for error_hash, error in self.errors.items()
                },
                "error_history": self.error_history
            }

            with open(self.config.error_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save error data: {e}")

    def _load_error_data(self) -> None:
        """Load error data from file"""
        try:
            if os.path.exists(self.config.error_data_file):
                with open(self.config.error_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Load errors
                for error_hash, error_data in data.get("errors", {}).items():
                    self.errors[error_hash] = ErrorRecord(
                        timestamp=error_data["timestamp"],
                        error_type=error_data["error_type"],
                        error_message=error_data["error_message"],
                        error_hash=error_data["error_hash"],
                        stack_trace=error_data["stack_trace"],
                        context=error_data["context"],
                        severity=error_data["severity"],
                        category=error_data["category"],
                        count=error_data["count"],
                        first_seen=error_data["first_seen"],
                        last_seen=error_data["last_seen"],
                        resolved=error_data.get("resolved", False),
                        tags=error_data.get("tags", [])
                    )

                # Load history
                self.error_history = data.get("error_history", [])

                self.logger.info(f"Loaded {len(self.errors)} errors and {len(self.error_history)} history entries")

        except Exception as e:
            self.logger.error(f"Failed to load error data: {e}")

    def export_errors(self, format: str = "json", filter_category: Optional[str] = None) -> str:
        """Export error data in various formats"""
        errors_to_export = self.errors

        if filter_category:
            errors_to_export = {h: e for h, e in self.errors.items() if e.category == filter_category}

        if format.lower() == "json":
            return json.dumps({
                "export_timestamp": time.time(),
                "total_errors": len(errors_to_export),
                "errors": {
                    error_hash: {
                        "type": error.error_type,
                        "message": error.error_message,
                        "count": error.count,
                        "severity": error.severity,
                        "category": error.category,
                        "first_seen": error.first_seen,
                        "last_seen": error.last_seen,
                        "resolved": error.resolved
                    }
                    for error_hash, error in errors_to_export.items()
                }
            }, indent=2)

        elif format.lower() == "csv":
            lines = ["hash,type,message,count,severity,category,first_seen,last_seen,resolved"]
            for error in errors_to_export.values():
                message = error.error_message.replace(',', ';').replace('\n', ' ')[:100]
                lines.append(f"{error.error_hash},{error.error_type},{message},{error.count},{error.severity},{error.category},{error.first_seen},{error.last_seen},{error.resolved}")
            return '\n'.join(lines)

        else:
            return "Unsupported format. Use 'json' or 'csv'."

    def cleanup(self) -> None:
        """Cleanup and save data"""
        self._save_error_data()
        self.disable_global_tracking()


def demo_error_tracker():
    """Demonstrate the Error Tracking System"""
    print("🚨 Error Tracking System Demo")
    print("=" * 50)

    # Create tracker with demo config
    config = ErrorConfig()
    config.critical_error_rate = 3  # Lower threshold for demo

    tracker = ErrorTracker(config)

    try:
        print("\n1. Enabling global error tracking...")
        tracker.enable_global_tracking()

        print("\n2. Tracking some sample errors...")

        # Track manual errors
        tracker.track_error(
            error_message="Database connection failed",
            context={"database": "main", "host": "localhost"},
            severity="critical",
            category="database"
        )

        tracker.track_error(
            error_message="Configuration file not found",
            context={"file": "config.json"},
            severity="warning",
            category="config"
        )

        # Track errors with context manager
        try:
            with tracker.track_context("demo_operation", user="demo_user"):
                raise ValueError("Invalid input value")
        except ValueError:
            pass  # Already tracked by context manager

        # Simulate duplicate errors
        for i in range(3):
            tracker.track_error(
                error_message="Memory allocation failed",
                context={"attempt": i + 1},
                severity="error",
                category="memory"
            )

        print("\n3. Error summary:")
        summary = tracker.get_error_summary(hours=1)
        print(json.dumps(summary, indent=2))

        print("\n4. Error trends:")
        trends = tracker.analyze_error_trends(hours=1)
        print(json.dumps(trends, indent=2))

        print("\n5. Detailed error info:")
        if summary['top_errors']:
            error_hash = summary['top_errors'][0]['hash']
            details = tracker.get_error_details(error_hash)
            print(json.dumps(details, indent=2))

        print("\n6. Generating daily report...")
        report = tracker.generate_daily_report()
        print("Report generated (saved to file)")
        print(report[:500] + "..." if len(report) > 500 else report)

        print("\n7. Exporting errors...")
        csv_export = tracker.export_errors(format="csv")
        print("CSV Export (first 300 chars):")
        print(csv_export[:300] + "..." if len(csv_export) > 300 else csv_export)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")
        traceback.print_exc()
    finally:
        print("\n8. Cleaning up...")
        tracker.cleanup()
        print("✅ Demo complete!")


if __name__ == "__main__":
    demo_error_tracker()
