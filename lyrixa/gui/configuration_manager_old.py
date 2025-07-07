"""
Configuration Manager for Lyrixa AI Assistant

Provides comprehensive configuration management for:
- User preferences and settings
- Anticipation engine tuning parameters
- Theme and display customization
- Data export/import functionality
- System configuration backup and restore
"""

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QColor, QFont, QPalette
    from PySide6.QtWidgets import (
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDoubleSpinBox,
        QFileDialog,
        QFontDialog,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    logger.warning("PySide6 not available. Configuration manager will not function.")

    # Mock classes for when PySide6 is not available
    class QWidget:
        def __init__(self, *args, **kwargs):
            pass

        def resize(self, *args):
            pass

        def show(self):
            pass

    class Signal:
        def __init__(self, *args):
            pass

        def connect(self, *args):
            pass

        def emit(self, *args):
            pass

    class QThread:
        pass

    class QTimer:
        def __init__(self, *args):
            pass

        def start(self, *args):
            pass

        def stop(self):
            pass

    # Mock other Qt classes
    Qt = type("Qt", (), {"AlignCenter": 0, "AlignLeft": 0})
    QVBoxLayout = QHBoxLayout = QTabWidget = QLabel = QPushButton = QWidget
    QGroupBox = QFormLayout = QLineEdit = QSpinBox = QDoubleSpinBox = QWidget
    QCheckBox = QComboBox = QSlider = QTextEdit = QFileDialog = QWidget
    QMessageBox = QProgressBar = QColorDialog = QFontDialog = QWidget
    QScrollArea = QSplitter = QListWidget = QListWidgetItem = QWidget
    QFont = QColor = QPalette = QWidget

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User preference settings."""

    # General preferences
    language: str = "en"
    theme: str = "light"
    font_family: str = "Arial"
    font_size: int = 10

    # Notification preferences
    enable_notifications: bool = True
    notification_position: str = "bottom_right"
    auto_dismiss_time: int = 10
    play_sounds: bool = False

    # Anticipation engine preferences
    enable_anticipation: bool = True
    suggestion_frequency: int = 5  # minutes
    confidence_threshold: float = 0.7
    max_suggestions: int = 5

    # Analytics preferences
    enable_analytics: bool = True
    data_retention_days: int = 30
    export_format: str = "json"

    # Privacy preferences
    enable_telemetry: bool = False
    share_anonymous_data: bool = False


@dataclass
class AnticipationSettings:
    """Anticipation engine configuration."""

    # Pattern detection
    pattern_detection_sensitivity: float = 0.8
    minimum_pattern_occurrences: int = 3
    pattern_confidence_threshold: float = 0.75

    # Context analysis
    context_window_size: int = 30  # minutes
    activity_weight: float = 1.0
    time_weight: float = 0.8
    location_weight: float = 0.6

    # Suggestion generation
    suggestion_diversity: float = 0.7
    max_concurrent_suggestions: int = 3
    suggestion_cooldown: int = 5  # minutes

    # Learning parameters
    learning_rate: float = 0.1
    feedback_weight: float = 1.5
    adaptation_speed: float = 0.3


@dataclass
class SystemConfiguration:
    """System-level configuration."""

    # Database settings
    database_path: str = "lyrixa_config.db"
    backup_frequency: int = 24  # hours
    auto_vacuum: bool = True

    # Performance settings
    max_memory_usage: int = 512  # MB
    max_cpu_usage: int = 25  # percentage
    enable_background_processing: bool = True

    # Logging settings
    log_level: str = "INFO"
    log_file_size: int = 10  # MB
    log_rotation_count: int = 5


class ConfigurationBackupWorker(QThread if PYSIDE6_AVAILABLE else object):
    """Background worker for configuration backup operations."""

    progress_updated = Signal(int) if PYSIDE6_AVAILABLE else None
    backup_completed = Signal(str) if PYSIDE6_AVAILABLE else None
    backup_failed = Signal(str) if PYSIDE6_AVAILABLE else None

    def __init__(self, config_manager, backup_path: str):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__()
        self.config_manager = config_manager
        self.backup_path = backup_path

    def run(self):
        """Perform configuration backup."""
        try:
            if self.progress_updated:
                self.progress_updated.emit(10)

            # Collect all configuration data
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "user_preferences": asdict(self.config_manager.user_preferences),
                "anticipation_settings": asdict(
                    self.config_manager.anticipation_settings
                ),
                "system_configuration": asdict(
                    self.config_manager.system_configuration
                ),
            }

            if self.progress_updated:
                self.progress_updated.emit(50)

            # Write backup file
            with open(self.backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            if self.progress_updated:
                self.progress_updated.emit(100)

            if self.backup_completed:
                self.backup_completed.emit(self.backup_path)

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if self.backup_failed:
                self.backup_failed.emit(str(e))


class PreferencesTab(QWidget if PYSIDE6_AVAILABLE else object):
    """Tab for user preferences."""

    preferences_changed = Signal() if PYSIDE6_AVAILABLE else None

    def __init__(self, preferences: UserPreferences, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.preferences = preferences
        self.controls = {}
        self.init_ui()

    def init_ui(self):
        """Initialize preferences UI."""
        layout = QVBoxLayout()

        # Scroll area for all settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # General settings
        general_group = QGroupBox("General Settings")
        general_form = QFormLayout()

        # Language
        self.controls["language"] = QComboBox()
        self.controls["language"].addItems(["en", "es", "fr", "de", "zh"])
        self.controls["language"].setCurrentText(self.preferences.language)
        general_form.addRow("Language:", self.controls["language"])

        # Theme
        self.controls["theme"] = QComboBox()
        self.controls["theme"].addItems(["light", "dark", "auto"])
        self.controls["theme"].setCurrentText(self.preferences.theme)
        general_form.addRow("Theme:", self.controls["theme"])

        # Font
        font_layout = QHBoxLayout()
        self.controls["font_family"] = QLineEdit(self.preferences.font_family)
        self.controls["font_family"].setReadOnly(True)
        font_btn = QPushButton("Choose Font")
        font_btn.clicked.connect(self.choose_font)
        font_layout.addWidget(self.controls["font_family"])
        font_layout.addWidget(font_btn)
        general_form.addRow("Font:", font_layout)

        # Font size
        self.controls["font_size"] = QSpinBox()
        self.controls["font_size"].setRange(8, 20)
        self.controls["font_size"].setValue(self.preferences.font_size)
        general_form.addRow("Font Size:", self.controls["font_size"])

        general_group.setLayout(general_form)
        content_layout.addWidget(general_group)

        # Notification settings
        notif_group = QGroupBox("Notification Settings")
        notif_form = QFormLayout()

        # Enable notifications
        self.controls["enable_notifications"] = QCheckBox()
        self.controls["enable_notifications"].setChecked(
            self.preferences.enable_notifications
        )
        notif_form.addRow(
            "Enable Notifications:", self.controls["enable_notifications"]
        )

        # Auto dismiss time
        self.controls["auto_dismiss_time"] = QSpinBox()
        self.controls["auto_dismiss_time"].setRange(0, 60)
        self.controls["auto_dismiss_time"].setValue(self.preferences.auto_dismiss_time)
        self.controls["auto_dismiss_time"].setSpecialValueText("Never")
        notif_form.addRow("Auto Dismiss (minutes):", self.controls["auto_dismiss_time"])

        # Play sounds
        self.controls["play_sounds"] = QCheckBox()
        self.controls["play_sounds"].setChecked(self.preferences.play_sounds)
        notif_form.addRow("Play Sounds:", self.controls["play_sounds"])

        notif_group.setLayout(notif_form)
        content_layout.addWidget(notif_group)

        # Privacy settings
        privacy_group = QGroupBox("Privacy Settings")
        privacy_form = QFormLayout()

        # Enable telemetry
        self.controls["enable_telemetry"] = QCheckBox()
        self.controls["enable_telemetry"].setChecked(self.preferences.enable_telemetry)
        privacy_form.addRow("Enable Telemetry:", self.controls["enable_telemetry"])

        # Share anonymous data
        self.controls["share_anonymous_data"] = QCheckBox()
        self.controls["share_anonymous_data"].setChecked(
            self.preferences.share_anonymous_data
        )
        privacy_form.addRow(
            "Share Anonymous Data:", self.controls["share_anonymous_data"]
        )

        privacy_group.setLayout(privacy_form)
        content_layout.addWidget(privacy_group)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Connect change signals
        for control in self.controls.values():
            if hasattr(control, "currentTextChanged"):
                control.currentTextChanged.connect(self.on_preference_changed)
            elif hasattr(control, "valueChanged"):
                control.valueChanged.connect(self.on_preference_changed)
            elif hasattr(control, "toggled"):
                control.toggled.connect(self.on_preference_changed)
            elif hasattr(control, "textChanged"):
                control.textChanged.connect(self.on_preference_changed)

    def choose_font(self):
        """Open font selection dialog."""
        current_font = QFont(self.preferences.font_family, self.preferences.font_size)
        font, ok = QFontDialog.getFont(current_font, self)

        if ok:
            self.controls["font_family"].setText(font.family())
            self.controls["font_size"].setValue(font.pointSize())
            self.on_preference_changed()

    def on_preference_changed(self):
        """Handle preference changes."""
        self.update_preferences()
        if self.preferences_changed:
            self.preferences_changed.emit()

    def update_preferences(self):
        """Update preferences from UI controls."""
        self.preferences.language = self.controls["language"].currentText()
        self.preferences.theme = self.controls["theme"].currentText()
        self.preferences.font_family = self.controls["font_family"].text()
        self.preferences.font_size = self.controls["font_size"].value()
        self.preferences.enable_notifications = self.controls[
            "enable_notifications"
        ].isChecked()
        self.preferences.auto_dismiss_time = self.controls["auto_dismiss_time"].value()
        self.preferences.play_sounds = self.controls["play_sounds"].isChecked()
        self.preferences.enable_telemetry = self.controls[
            "enable_telemetry"
        ].isChecked()
        self.preferences.share_anonymous_data = self.controls[
            "share_anonymous_data"
        ].isChecked()


class AnticipationTab(QWidget if PYSIDE6_AVAILABLE else object):
    """Tab for anticipation engine settings."""

    settings_changed = Signal() if PYSIDE6_AVAILABLE else None

    def __init__(self, settings: AnticipationSettings, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.settings = settings
        self.controls = {}
        self.init_ui()

    def init_ui(self):
        """Initialize anticipation settings UI."""
        layout = QVBoxLayout()

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Pattern detection settings
        pattern_group = QGroupBox("Pattern Detection")
        pattern_form = QFormLayout()

        # Sensitivity
        self.controls["pattern_detection_sensitivity"] = QDoubleSpinBox()
        self.controls["pattern_detection_sensitivity"].setRange(0.1, 1.0)
        self.controls["pattern_detection_sensitivity"].setSingleStep(0.1)
        self.controls["pattern_detection_sensitivity"].setValue(
            self.settings.pattern_detection_sensitivity
        )
        pattern_form.addRow(
            "Sensitivity:", self.controls["pattern_detection_sensitivity"]
        )

        # Minimum occurrences
        self.controls["minimum_pattern_occurrences"] = QSpinBox()
        self.controls["minimum_pattern_occurrences"].setRange(1, 10)
        self.controls["minimum_pattern_occurrences"].setValue(
            self.settings.minimum_pattern_occurrences
        )
        pattern_form.addRow(
            "Min Occurrences:", self.controls["minimum_pattern_occurrences"]
        )

        # Confidence threshold
        self.controls["pattern_confidence_threshold"] = QDoubleSpinBox()
        self.controls["pattern_confidence_threshold"].setRange(0.1, 1.0)
        self.controls["pattern_confidence_threshold"].setSingleStep(0.05)
        self.controls["pattern_confidence_threshold"].setValue(
            self.settings.pattern_confidence_threshold
        )
        pattern_form.addRow(
            "Confidence Threshold:", self.controls["pattern_confidence_threshold"]
        )

        pattern_group.setLayout(pattern_form)
        content_layout.addWidget(pattern_group)

        # Context analysis settings
        context_group = QGroupBox("Context Analysis")
        context_form = QFormLayout()

        # Context window size
        self.controls["context_window_size"] = QSpinBox()
        self.controls["context_window_size"].setRange(5, 120)
        self.controls["context_window_size"].setValue(self.settings.context_window_size)
        self.controls["context_window_size"].setSuffix(" minutes")
        context_form.addRow("Context Window:", self.controls["context_window_size"])

        # Weights
        for weight_name in ["activity_weight", "time_weight", "location_weight"]:
            self.controls[weight_name] = QDoubleSpinBox()
            self.controls[weight_name].setRange(0.0, 2.0)
            self.controls[weight_name].setSingleStep(0.1)
            self.controls[weight_name].setValue(getattr(self.settings, weight_name))
            context_form.addRow(
                f"{weight_name.replace('_', ' ').title()}:", self.controls[weight_name]
            )

        context_group.setLayout(context_form)
        content_layout.addWidget(context_group)

        # Suggestion settings
        suggestion_group = QGroupBox("Suggestion Generation")
        suggestion_form = QFormLayout()

        # Diversity
        self.controls["suggestion_diversity"] = QSlider(Qt.Horizontal)
        self.controls["suggestion_diversity"].setRange(0, 100)
        self.controls["suggestion_diversity"].setValue(
            int(self.settings.suggestion_diversity * 100)
        )
        self.controls["suggestion_diversity"].setTickPosition(QSlider.TicksBelow)
        self.controls["suggestion_diversity"].setTickInterval(25)
        suggestion_form.addRow("Diversity:", self.controls["suggestion_diversity"])

        # Max concurrent
        self.controls["max_concurrent_suggestions"] = QSpinBox()
        self.controls["max_concurrent_suggestions"].setRange(1, 10)
        self.controls["max_concurrent_suggestions"].setValue(
            self.settings.max_concurrent_suggestions
        )
        suggestion_form.addRow(
            "Max Concurrent:", self.controls["max_concurrent_suggestions"]
        )

        # Cooldown
        self.controls["suggestion_cooldown"] = QSpinBox()
        self.controls["suggestion_cooldown"].setRange(1, 30)
        self.controls["suggestion_cooldown"].setValue(self.settings.suggestion_cooldown)
        self.controls["suggestion_cooldown"].setSuffix(" minutes")
        suggestion_form.addRow("Cooldown:", self.controls["suggestion_cooldown"])

        suggestion_group.setLayout(suggestion_form)
        content_layout.addWidget(suggestion_group)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Connect change signals
        for control in self.controls.values():
            if hasattr(control, "valueChanged"):
                control.valueChanged.connect(self.on_setting_changed)

    def on_setting_changed(self):
        """Handle setting changes."""
        self.update_settings()
        if self.settings_changed:
            self.settings_changed.emit()

    def update_settings(self):
        """Update settings from UI controls."""
        self.settings.pattern_detection_sensitivity = self.controls[
            "pattern_detection_sensitivity"
        ].value()
        self.settings.minimum_pattern_occurrences = self.controls[
            "minimum_pattern_occurrences"
        ].value()
        self.settings.pattern_confidence_threshold = self.controls[
            "pattern_confidence_threshold"
        ].value()
        self.settings.context_window_size = self.controls["context_window_size"].value()
        self.settings.activity_weight = self.controls["activity_weight"].value()
        self.settings.time_weight = self.controls["time_weight"].value()
        self.settings.location_weight = self.controls["location_weight"].value()
        self.settings.suggestion_diversity = (
            self.controls["suggestion_diversity"].value() / 100.0
        )
        self.settings.max_concurrent_suggestions = self.controls[
            "max_concurrent_suggestions"
        ].value()
        self.settings.suggestion_cooldown = self.controls["suggestion_cooldown"].value()


class DataManagementTab(QWidget if PYSIDE6_AVAILABLE else object):
    """Tab for data management operations."""

    def __init__(self, config_manager, parent=None):
        if not PYSIDE6_AVAILABLE:
            return

        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        """Initialize data management UI."""
        layout = QVBoxLayout()

        # Export section
        export_group = QGroupBox("Export Configuration")
        export_layout = QVBoxLayout()

        export_btn = QPushButton("📊 Export All Settings")
        export_btn.clicked.connect(self.export_configuration)
        export_layout.addWidget(export_btn)

        export_partial_btn = QPushButton("📄 Export User Preferences Only")
        export_partial_btn.clicked.connect(self.export_preferences_only)
        export_layout.addWidget(export_partial_btn)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Import section
        import_group = QGroupBox("Import Configuration")
        import_layout = QVBoxLayout()

        import_btn = QPushButton("📥 Import Settings")
        import_btn.clicked.connect(self.import_configuration)
        import_layout.addWidget(import_btn)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Backup section
        backup_group = QGroupBox("Backup & Restore")
        backup_layout = QVBoxLayout()

        backup_btn = QPushButton("💾 Create Backup")
        backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(backup_btn)

        restore_btn = QPushButton("🔄 Restore from Backup")
        restore_btn.clicked.connect(self.restore_backup)
        backup_layout.addWidget(restore_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        backup_layout.addWidget(self.progress_bar)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # Reset section
        reset_group = QGroupBox("Reset Settings")
        reset_layout = QVBoxLayout()

        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setStyleSheet(
            "QPushButton { background-color: #ff6b6b; color: white; }"
        )
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(reset_btn)

        reset_group.setLayout(reset_layout)
        layout.addWidget(reset_group)

        layout.addStretch()
        self.setLayout(layout)

    def export_configuration(self):
        """Export all configuration data."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            f"lyrixa_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)",
        )

        if filename:
            try:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "version": "3.0.0",
                    "user_preferences": asdict(self.config_manager.user_preferences),
                    "anticipation_settings": asdict(
                        self.config_manager.anticipation_settings
                    ),
                    "system_configuration": asdict(
                        self.config_manager.system_configuration
                    ),
                }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(
                    self, "Export Successful", f"Configuration exported to:\n{filename}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Export Failed", f"Failed to export configuration:\n{e}"
                )

    def export_preferences_only(self):
        """Export only user preferences."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export User Preferences",
            f"lyrixa_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)",
        )

        if filename:
            try:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "version": "3.0.0",
                    "user_preferences": asdict(self.config_manager.user_preferences),
                }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(
                    self, "Export Successful", f"Preferences exported to:\n{filename}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Export Failed", f"Failed to export preferences:\n{e}"
                )

    def import_configuration(self):
        """Import configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "JSON Files (*.json)"
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    import_data = json.load(f)

                # Validate import data
                if "version" not in import_data:
                    QMessageBox.warning(
                        self,
                        "Import Warning",
                        "Configuration file format not recognized.",
                    )
                    return

                # Import user preferences
                if "user_preferences" in import_data:
                    prefs_data = import_data["user_preferences"]
                    for key, value in prefs_data.items():
                        if hasattr(self.config_manager.user_preferences, key):
                            setattr(self.config_manager.user_preferences, key, value)

                # Import anticipation settings
                if "anticipation_settings" in import_data:
                    settings_data = import_data["anticipation_settings"]
                    for key, value in settings_data.items():
                        if hasattr(self.config_manager.anticipation_settings, key):
                            setattr(
                                self.config_manager.anticipation_settings, key, value
                            )

                self.config_manager.save_configuration()
                QMessageBox.information(
                    self, "Import Successful", "Configuration imported successfully."
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Import Failed", f"Failed to import configuration:\n{e}"
                )

    def create_backup(self):
        """Create configuration backup."""
        backup_dir = Path.home() / "Documents" / "Lyrixa" / "Backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_filename = (
            backup_dir
            / f"lyrixa_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create backup worker
        self.backup_worker = ConfigurationBackupWorker(
            self.config_manager, str(backup_filename)
        )
        self.backup_worker.progress_updated.connect(self.progress_bar.setValue)
        self.backup_worker.backup_completed.connect(self.on_backup_completed)
        self.backup_worker.backup_failed.connect(self.on_backup_failed)
        self.backup_worker.start()

    def on_backup_completed(self, backup_path: str):
        """Handle backup completion."""
        self.progress_bar.setVisible(False)
        QMessageBox.information(
            self, "Backup Successful", f"Configuration backed up to:\n{backup_path}"
        )

    def on_backup_failed(self, error: str):
        """Handle backup failure."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self, "Backup Failed", f"Failed to create backup:\n{error}"
        )

    def restore_backup(self):
        """Restore from backup file."""
        backup_dir = Path.home() / "Documents" / "Lyrixa" / "Backups"

        filename, _ = QFileDialog.getOpenFileName(
            self, "Restore from Backup", str(backup_dir), "JSON Files (*.json)"
        )

        if filename:
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                "This will replace all current settings. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        backup_data = json.load(f)

                    # Restore all configuration
                    if "user_preferences" in backup_data:
                        self.config_manager.user_preferences = UserPreferences(
                            **backup_data["user_preferences"]
                        )

                    if "anticipation_settings" in backup_data:
                        self.config_manager.anticipation_settings = (
                            AnticipationSettings(**backup_data["anticipation_settings"])
                        )

                    if "system_configuration" in backup_data:
                        self.config_manager.system_configuration = SystemConfiguration(
                            **backup_data["system_configuration"]
                        )

                    self.config_manager.save_configuration()
                    QMessageBox.information(
                        self,
                        "Restore Successful",
                        "Configuration restored successfully.",
                    )

                except Exception as e:
                    QMessageBox.critical(
                        self, "Restore Failed", f"Failed to restore configuration:\n{e}"
                    )

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "This will reset ALL settings to default values. This cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.config_manager.user_preferences = UserPreferences()
                self.config_manager.anticipation_settings = AnticipationSettings()
                self.config_manager.system_configuration = SystemConfiguration()

                self.config_manager.save_configuration()
                QMessageBox.information(
                    self, "Reset Complete", "All settings have been reset to defaults."
                )

            except Exception as e:
                QMessageBox.critical(
                    self, "Reset Failed", f"Failed to reset settings:\n{e}"
                )


class ConfigurationManager(QWidget if PYSIDE6_AVAILABLE else object):
    """
    Comprehensive configuration manager for Lyrixa AI Assistant.

    Provides centralized management for:
    - User preferences and settings
    - Anticipation engine parameters
    - System configuration
    - Data backup and restore
    - Import/export functionality
    """

    # Signals
    configuration_changed = Signal() if PYSIDE6_AVAILABLE else None
    preferences_applied = Signal() if PYSIDE6_AVAILABLE else None

    def __init__(self, parent=None):
        if not PYSIDE6_AVAILABLE:
            logger.warning(
                "PySide6 not available. Configuration manager will not function."
            )
            return

        super().__init__(parent)

        # Initialize configuration objects
        self.user_preferences = UserPreferences()
        self.anticipation_settings = AnticipationSettings()
        self.system_configuration = SystemConfiguration()

        # Configuration file path
        self.config_file = Path.home() / "Documents" / "Lyrixa" / "config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.init_ui()
        self.load_configuration()

        logger.info("Configuration Manager initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Header
        header_label = QLabel("⚙️ Configuration Manager")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Preferences tab
        self.preferences_tab = PreferencesTab(self.user_preferences)
        self.preferences_tab.preferences_changed.connect(self.on_configuration_changed)
        self.tab_widget.addTab(self.preferences_tab, "👤 User Preferences")

        # Anticipation settings tab
        self.anticipation_tab = AnticipationTab(self.anticipation_settings)
        self.anticipation_tab.settings_changed.connect(self.on_configuration_changed)
        self.tab_widget.addTab(self.anticipation_tab, "🔮 Anticipation Engine")

        # Data management tab
        self.data_tab = DataManagementTab(self)
        self.tab_widget.addTab(self.data_tab, "💾 Data Management")

        layout.addWidget(self.tab_widget)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_configuration)
        button_layout.addWidget(save_btn)

        apply_btn = QPushButton("✅ Apply Settings")
        apply_btn.clicked.connect(self.apply_configuration)
        button_layout.addWidget(apply_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("❌ Discard Changes")
        cancel_btn.clicked.connect(self.load_configuration)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6c757d; font-style: italic;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_configuration(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Load user preferences
                if "user_preferences" in config_data:
                    self.user_preferences = UserPreferences(
                        **config_data["user_preferences"]
                    )

                # Load anticipation settings
                if "anticipation_settings" in config_data:
                    self.anticipation_settings = AnticipationSettings(
                        **config_data["anticipation_settings"]
                    )

                # Load system configuration
                if "system_configuration" in config_data:
                    self.system_configuration = SystemConfiguration(
                        **config_data["system_configuration"]
                    )

                self.status_label.setText("Configuration loaded successfully")
                logger.info("Configuration loaded from file")
            else:
                self.status_label.setText("Using default configuration")
                logger.info("Using default configuration")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.status_label.setText(f"Error loading configuration: {e}")

    def save_configuration(self):
        """Save configuration to file."""
        try:
            config_data = {
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "user_preferences": asdict(self.user_preferences),
                "anticipation_settings": asdict(self.anticipation_settings),
                "system_configuration": asdict(self.system_configuration),
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.status_label.setText("Configuration saved successfully")
            logger.info("Configuration saved to file")

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            self.status_label.setText(f"Error saving configuration: {e}")

    def apply_configuration(self):
        """Apply current configuration settings."""
        try:
            # Update UI components from current settings
            self.preferences_tab.update_preferences()
            self.anticipation_tab.update_settings()

            # Save changes
            self.save_configuration()

            # Emit signals
            if self.configuration_changed:
                self.configuration_changed.emit()
            if self.preferences_applied:
                self.preferences_applied.emit()

            self.status_label.setText("Configuration applied successfully")
            logger.info("Configuration applied")

        except Exception as e:
            logger.error(f"Error applying configuration: {e}")
            self.status_label.setText(f"Error applying configuration: {e}")

    def on_configuration_changed(self):
        """Handle configuration changes."""
        self.status_label.setText("Configuration modified (unsaved)")
        if self.configuration_changed:
            self.configuration_changed.emit()

    def get_preferences(self) -> UserPreferences:
        """Get current user preferences."""
        return self.user_preferences

    def get_anticipation_settings(self) -> AnticipationSettings:
        """Get current anticipation settings."""
        return self.anticipation_settings

    def get_system_configuration(self) -> SystemConfiguration:
        """Get current system configuration."""
        return self.system_configuration

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            # Stop any background workers
            pass  # ConfigurationManager doesn't have background threads currently
        except Exception:
            pass

    def closeEvent(self, event):
        """Handle close event properly."""
        if PYSIDE6_AVAILABLE:
            try:
                # Save configuration before closing
                self.save_configuration()
            except Exception:
                pass
            super().closeEvent(event)


# Example usage
if __name__ == "__main__":
    if PYSIDE6_AVAILABLE:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        config_manager = ConfigurationManager()
        config_manager.show()
        config_manager.resize(800, 600)

        sys.exit(app.exec())
    else:
        print("PySide6 is required to run the Configuration Manager")
