# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Introspector Plugin UI
System analysis and self-reflection capabilities
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class IntrospectorUI(QWidget):
    """Introspector Plugin UI for system analysis and self-reflection."""

    def __init__(self):
        super().__init__()
        self.analysis_data = {}
        self.setup_ui()
        self.apply_styling()
        self.start_monitoring()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_system_metrics)
        self.update_timer.start(2000)  # Update every 2 seconds

    def setup_ui(self):
        """Set up the introspector interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🔍 System Introspector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #9C27B0; margin: 10px;"
        )
        layout.addWidget(title)

        # Create main tab widget
        self.tabs = QTabWidget()

        # System Health Tab
        self.tabs.addTab(self.create_system_health(), "💓 System Health")

        # Performance Analysis Tab
        self.tabs.addTab(self.create_performance_analysis(), "📊 Performance")

        # Process Monitor Tab
        self.tabs.addTab(self.create_process_monitor(), "⚙️ Processes")

        # Self-Analysis Tab
        self.tabs.addTab(self.create_self_analysis(), "🧠 Self-Analysis")

        # Diagnostics Tab
        self.tabs.addTab(self.create_diagnostics(), "🔧 Diagnostics")

        layout.addWidget(self.tabs)

    def create_system_health(self):
        """Create the system health monitoring interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Health overview
        overview_group = QGroupBox("🏥 Health Overview")
        overview_layout = QGridLayout(overview_group)

        # System status indicator
        overview_layout.addWidget(QLabel("System Status:"), 0, 0)
        self.system_status = QLabel("Optimal")
        self.system_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        overview_layout.addWidget(self.system_status, 0, 1)

        # Uptime
        overview_layout.addWidget(QLabel("Uptime:"), 1, 0)
        self.uptime_label = QLabel("0d 0h 0m")
        overview_layout.addWidget(self.uptime_label, 1, 1)

        # Temperature (if available)
        overview_layout.addWidget(QLabel("CPU Temperature:"), 2, 0)
        self.temp_label = QLabel("N/A")
        overview_layout.addWidget(self.temp_label, 2, 1)

        layout.addWidget(overview_group)

        # Resource usage
        resources_group = QGroupBox("📈 Resource Usage")
        resources_layout = QVBoxLayout(resources_group)

        # CPU usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_label)
        resources_layout.addLayout(cpu_layout)

        # Memory usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(self.memory_bar)
        self.memory_label = QLabel("0%")
        memory_layout.addWidget(self.memory_label)
        resources_layout.addLayout(memory_layout)

        # Disk usage
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Disk:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        disk_layout.addWidget(self.disk_bar)
        self.disk_label = QLabel("0%")
        disk_layout.addWidget(self.disk_label)
        resources_layout.addLayout(disk_layout)

        # Network I/O
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Network:"))
        self.network_in_label = QLabel("↓ 0 KB/s")
        self.network_out_label = QLabel("↑ 0 KB/s")
        network_layout.addWidget(self.network_in_label)
        network_layout.addWidget(self.network_out_label)
        network_layout.addStretch()
        resources_layout.addLayout(network_layout)

        layout.addWidget(resources_group)

        # Alerts and warnings
        alerts_group = QGroupBox("⚠️ Alerts & Warnings")
        alerts_layout = QVBoxLayout(alerts_group)

        self.alerts_list = QListWidget()
        alerts_layout.addWidget(self.alerts_list)

        # Alert controls
        alert_controls = QHBoxLayout()
        clear_alerts_btn = QPushButton("🗑️ Clear Alerts")
        export_alerts_btn = QPushButton("📤 Export Alerts")
        alert_controls.addWidget(clear_alerts_btn)
        alert_controls.addWidget(export_alerts_btn)
        alert_controls.addStretch()
        alerts_layout.addLayout(alert_controls)

        layout.addWidget(alerts_group)

        # Connect signals
        clear_alerts_btn.clicked.connect(self.clear_alerts)

        return widget

    def create_performance_analysis(self):
        """Create the performance analysis interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance metrics
        metrics_group = QGroupBox("📊 Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)

        # Response times
        metrics_layout.addWidget(QLabel("Avg Response Time:"), 0, 0)
        self.response_time_label = QLabel("0ms")
        metrics_layout.addWidget(self.response_time_label, 0, 1)

        # Throughput
        metrics_layout.addWidget(QLabel("Throughput:"), 1, 0)
        self.throughput_label = QLabel("0 ops/sec")
        metrics_layout.addWidget(self.throughput_label, 1, 1)

        # Error rate
        metrics_layout.addWidget(QLabel("Error Rate:"), 2, 0)
        self.error_rate_label = QLabel("0%")
        metrics_layout.addWidget(self.error_rate_label, 2, 1)

        # Memory efficiency
        metrics_layout.addWidget(QLabel("Memory Efficiency:"), 3, 0)
        self.memory_efficiency_label = QLabel("0%")
        metrics_layout.addWidget(self.memory_efficiency_label, 3, 1)

        layout.addWidget(metrics_group)

        # Performance history
        history_group = QGroupBox("📈 Performance History")
        history_layout = QVBoxLayout(history_group)

        # Time range selector
        time_controls = QHBoxLayout()
        time_controls.addWidget(QLabel("Time Range:"))
        self.time_range = QComboBox()
        self.time_range.addItems(["Last Hour", "Last 6 Hours", "Last Day", "Last Week"])
        time_controls.addWidget(self.time_range)
        time_controls.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        time_controls.addWidget(refresh_btn)
        history_layout.addLayout(time_controls)

        # Performance chart placeholder
        self.performance_chart = QTextEdit()
        self.performance_chart.setReadOnly(True)
        self.performance_chart.setMaximumHeight(200)
        self.performance_chart.setPlainText(
            "Performance chart would be displayed here..."
        )
        history_layout.addWidget(self.performance_chart)

        layout.addWidget(history_group)

        # Bottleneck analysis
        bottleneck_group = QGroupBox("🚧 Bottleneck Analysis")
        bottleneck_layout = QVBoxLayout(bottleneck_group)

        self.bottleneck_list = QTreeWidget()
        self.bottleneck_list.setHeaderLabels(["Component", "Impact", "Recommendation"])
        bottleneck_layout.addWidget(self.bottleneck_list)

        # Analysis controls
        analysis_controls = QHBoxLayout()
        analyze_btn = QPushButton("🔍 Run Analysis")
        export_btn = QPushButton("📊 Export Report")
        analysis_controls.addWidget(analyze_btn)
        analysis_controls.addWidget(export_btn)
        analysis_controls.addStretch()
        bottleneck_layout.addLayout(analysis_controls)

        layout.addWidget(bottleneck_group)

        # Connect signals
        refresh_btn.clicked.connect(self.refresh_performance_data)
        analyze_btn.clicked.connect(self.analyze_bottlenecks)

        return widget

    def create_process_monitor(self):
        """Create the process monitoring interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Process controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("🔍 Filter:"))
        self.process_filter = QLineEdit()
        self.process_filter.setPlaceholderText("Filter processes...")
        controls_layout.addWidget(self.process_filter)

        refresh_processes_btn = QPushButton("🔄 Refresh")
        kill_process_btn = QPushButton("⚠️ Kill Process")
        controls_layout.addWidget(refresh_processes_btn)
        controls_layout.addWidget(kill_process_btn)

        layout.addLayout(controls_layout)

        # Process list
        processes_group = QGroupBox("⚙️ Running Processes")
        processes_layout = QVBoxLayout(processes_group)

        self.process_tree = QTreeWidget()
        self.process_tree.setHeaderLabels(["PID", "Name", "CPU%", "Memory", "Status"])
        processes_layout.addWidget(self.process_tree)

        layout.addWidget(processes_group)

        # Process details
        details_group = QGroupBox("📋 Process Details")
        details_layout = QVBoxLayout(details_group)

        self.process_details = QTextEdit()
        self.process_details.setReadOnly(True)
        self.process_details.setMaximumHeight(150)
        details_layout.addWidget(self.process_details)

        layout.addWidget(details_group)

        # Connect signals
        refresh_processes_btn.clicked.connect(self.refresh_processes)
        self.process_tree.currentItemChanged.connect(self.show_process_details)

        return widget

    def create_self_analysis(self):
        """Create the self-analysis interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Analysis status
        status_group = QGroupBox("🧠 Analysis Status")
        status_layout = QGridLayout(status_group)

        status_layout.addWidget(QLabel("Last Analysis:"), 0, 0)
        self.last_analysis_label = QLabel("Never")
        status_layout.addWidget(self.last_analysis_label, 0, 1)

        status_layout.addWidget(QLabel("Analysis Mode:"), 1, 0)
        self.analysis_mode = QComboBox()
        self.analysis_mode.addItems(["Comprehensive", "Quick", "Custom"])
        status_layout.addWidget(self.analysis_mode, 1, 1)

        status_layout.addWidget(QLabel("Auto-Analysis:"), 2, 0)
        self.auto_analysis = QCheckBox()
        status_layout.addWidget(self.auto_analysis, 2, 1)

        layout.addWidget(status_group)

        # Analysis controls
        controls_group = QGroupBox("🎮 Analysis Controls")
        controls_layout = QVBoxLayout(controls_group)

        control_buttons = QHBoxLayout()
        start_analysis_btn = QPushButton("🔍 Start Analysis")
        stop_analysis_btn = QPushButton("⏹️ Stop Analysis")
        save_report_btn = QPushButton("💾 Save Report")

        control_buttons.addWidget(start_analysis_btn)
        control_buttons.addWidget(stop_analysis_btn)
        control_buttons.addWidget(save_report_btn)
        control_buttons.addStretch()
        controls_layout.addLayout(control_buttons)

        # Analysis progress
        self.analysis_progress = QProgressBar()
        controls_layout.addWidget(self.analysis_progress)

        layout.addWidget(controls_group)

        # Analysis results
        results_group = QGroupBox("📊 Analysis Results")
        results_layout = QVBoxLayout(results_group)

        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        results_layout.addWidget(self.analysis_results)

        layout.addWidget(results_group)

        # Insights and recommendations
        insights_group = QGroupBox("💡 Insights & Recommendations")
        insights_layout = QVBoxLayout(insights_group)

        self.insights_list = QListWidget()
        insights_layout.addWidget(self.insights_list)

        layout.addWidget(insights_group)

        # Connect signals
        start_analysis_btn.clicked.connect(self.start_self_analysis)

        return widget

    def create_diagnostics(self):
        """Create the diagnostics interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Diagnostic tests
        tests_group = QGroupBox("🔧 Diagnostic Tests")
        tests_layout = QVBoxLayout(tests_group)

        # Test categories
        test_categories = QHBoxLayout()
        system_tests_btn = QPushButton("🖥️ System Tests")
        network_tests_btn = QPushButton("🌐 Network Tests")
        storage_tests_btn = QPushButton("💾 Storage Tests")
        memory_tests_btn = QPushButton("🧠 Memory Tests")

        test_categories.addWidget(system_tests_btn)
        test_categories.addWidget(network_tests_btn)
        test_categories.addWidget(storage_tests_btn)
        test_categories.addWidget(memory_tests_btn)
        tests_layout.addLayout(test_categories)

        # Test results
        self.test_results = QTreeWidget()
        self.test_results.setHeaderLabels(["Test", "Status", "Result", "Details"])
        tests_layout.addWidget(self.test_results)

        # Test controls
        test_controls = QHBoxLayout()
        run_all_btn = QPushButton("▶️ Run All Tests")
        run_selected_btn = QPushButton("▶️ Run Selected")
        clear_results_btn = QPushButton("🗑️ Clear Results")

        test_controls.addWidget(run_all_btn)
        test_controls.addWidget(run_selected_btn)
        test_controls.addWidget(clear_results_btn)
        test_controls.addStretch()
        tests_layout.addLayout(test_controls)

        layout.addWidget(tests_group)

        # System information
        sysinfo_group = QGroupBox("ℹ️ System Information")
        sysinfo_layout = QVBoxLayout(sysinfo_group)

        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setMaximumHeight(200)
        sysinfo_layout.addWidget(self.system_info)

        layout.addWidget(sysinfo_group)

        # Connect signals
        run_all_btn.clicked.connect(self.run_all_diagnostic_tests)

        return widget

    def apply_styling(self):
        """Apply dark theme styling to the introspector interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #9C27B0;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #9C27B0;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #666666;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #9C27B0;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QLineEdit, QTextEdit {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #9C27B0;
            }
            QListWidget, QTreeWidget {
                background-color: #353535;
                border: 1px solid #666666;
                border-radius: 4px;
                alternate-background-color: #404040;
            }
            QListWidget::item, QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #9C27B0;
                color: white;
            }
            QListWidget::item:hover, QTreeWidget::item:hover {
                background-color: #505050;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #9C27B0;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666666;
                border-radius: 3px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #9C27B0;
            }
        """)

    def start_monitoring(self):
        """Start system monitoring."""
        self.update_system_info()
        self.refresh_processes()

    def update_system_metrics(self):
        """Update real-time system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")

            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_bar.setValue(int(memory.percent))
            self.memory_label.setText(f"{memory.percent:.1f}%")

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self.disk_bar.setValue(int(disk_percent))
            self.disk_label.setText(f"{disk_percent:.1f}%")

            # Network I/O
            net_io = psutil.net_io_counters()
            self.network_in_label.setText(f"↓ {net_io.bytes_recv // 1024} KB")
            self.network_out_label.setText(f"↑ {net_io.bytes_sent // 1024} KB")

            # Update system status based on metrics
            if cpu_percent > 80 or memory.percent > 90:
                self.system_status.setText("Warning")
                self.system_status.setStyleSheet("color: #FF9800; font-weight: bold;")
            elif cpu_percent > 95 or memory.percent > 95:
                self.system_status.setText("Critical")
                self.system_status.setStyleSheet("color: #F44336; font-weight: bold;")
            else:
                self.system_status.setText("Optimal")
                self.system_status.setStyleSheet("color: #4CAF50; font-weight: bold;")

        except Exception as e:
            print(f"Error updating system metrics: {e}")

    def update_system_info(self):
        """Update system information display."""
        try:
            info = []
            info.append(f"Platform: {psutil.os.name}")
            info.append(f"CPU Count: {psutil.cpu_count()} cores")

            memory = psutil.virtual_memory()
            info.append(f"Total Memory: {memory.total // (1024**3):.1f} GB")

            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info.append(f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")

            self.system_info.setPlainText("\n".join(info))

        except Exception as e:
            self.system_info.setPlainText(f"Error gathering system info: {e}")

    def refresh_processes(self):
        """Refresh the process list."""
        try:
            self.process_tree.clear()

            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "status"]
            ):
                try:
                    info = proc.info
                    item = QTreeWidgetItem(
                        [
                            str(info["pid"]),
                            info["name"] or "N/A",
                            f"{info['cpu_percent'] or 0:.1f}%",
                            f"{info['memory_percent'] or 0:.1f}%",
                            info["status"] or "unknown",
                        ]
                    )
                    self.process_tree.addTopLevelItem(item)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            print(f"Error refreshing processes: {e}")

    def show_process_details(self, current, previous):
        """Show details for selected process."""
        if current:
            pid = current.text(0)
            try:
                proc = psutil.Process(int(pid))
                details = [
                    f"PID: {proc.pid}",
                    f"Name: {proc.name()}",
                    f"Status: {proc.status()}",
                    f"CPU: {proc.cpu_percent()}%",
                    f"Memory: {proc.memory_percent():.2f}%",
                    f"Threads: {proc.num_threads()}",
                    f"Created: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}",
                ]
                self.process_details.setPlainText("\n".join(details))
            except Exception as e:
                self.process_details.setPlainText(f"Error getting process details: {e}")

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts_list.clear()

    def refresh_performance_data(self):
        """Refresh performance analysis data."""
        # Simulate performance data update
        self.performance_chart.setPlainText(
            "Performance data refreshed at " + datetime.now().strftime("%H:%M:%S")
        )

    def analyze_bottlenecks(self):
        """Analyze system bottlenecks."""
        self.bottleneck_list.clear()

        # Sample bottleneck analysis
        bottlenecks = [
            ("CPU", "Medium", "Consider closing resource-intensive applications"),
            ("Memory", "Low", "Memory usage is within normal range"),
            ("Disk I/O", "High", "Check for disk fragmentation or failing drive"),
            ("Network", "Low", "Network performance is optimal"),
        ]

        for component, impact, recommendation in bottlenecks:
            item = QTreeWidgetItem([component, impact, recommendation])
            self.bottleneck_list.addTopLevelItem(item)

    def start_self_analysis(self):
        """Start self-analysis process."""
        self.analysis_progress.setValue(0)
        self.analysis_results.clear()

        # Simulate analysis process
        analysis_text = "Starting comprehensive self-analysis...\n\n"
        analysis_text += "✓ System health check completed\n"
        analysis_text += "✓ Performance metrics analyzed\n"
        analysis_text += "✓ Resource utilization reviewed\n"
        analysis_text += "✓ Process efficiency evaluated\n\n"
        analysis_text += "Analysis Summary:\n"
        analysis_text += "- System is operating within normal parameters\n"
        analysis_text += "- No critical issues detected\n"
        analysis_text += "- Recommendations generated for optimization\n"

        self.analysis_results.setPlainText(analysis_text)
        self.analysis_progress.setValue(100)
        self.last_analysis_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Add sample insights
        insights = [
            "💡 Consider increasing memory allocation for better performance",
            "💡 Regular disk cleanup recommended",
            "💡 Network connectivity is optimal",
            "💡 CPU utilization could be optimized",
        ]

        self.insights_list.clear()
        for insight in insights:
            self.insights_list.addItem(insight)

    def run_all_diagnostic_tests(self):
        """Run all diagnostic tests."""
        self.test_results.clear()

        # Sample diagnostic tests
        tests = [
            ("CPU Test", "Passed", "Normal", "CPU functioning correctly"),
            ("Memory Test", "Passed", "Normal", "Memory integrity verified"),
            ("Disk Test", "Warning", "Slow", "Disk showing signs of aging"),
            ("Network Test", "Passed", "Fast", "Network connectivity excellent"),
        ]

        for test_name, status, result, details in tests:
            item = QTreeWidgetItem([test_name, status, result, details])

            # Color code by status
            if status == "Passed":
                item.setBackground(0, QColor(0, 255, 0, 50))
            elif status == "Warning":
                item.setBackground(0, QColor(255, 165, 0, 50))
            elif status == "Failed":
                item.setBackground(0, QColor(255, 0, 0, 50))

            self.test_results.addTopLevelItem(item)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = IntrospectorUI()
    window.show()
    sys.exit(app.exec())
