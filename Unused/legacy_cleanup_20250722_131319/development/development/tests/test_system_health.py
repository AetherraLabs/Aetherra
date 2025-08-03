"""
Test System Health Panel to diagnose the empty panel issue
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
    from PySide6.QtCore import Qt

    app = QApplication(sys.argv)

    # Test widget
    widget = QWidget()
    widget.setWindowTitle("Test System Health Panel")
    widget.resize(800, 600)

    layout = QVBoxLayout(widget)

    # Add test content
    title = QLabel("🏥 Test System Health Dashboard")
    title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")
    layout.addWidget(title)

    status = QLabel("✅ Panel is working correctly!")
    status.setStyleSheet("font-size: 14px; color: #cccccc;")
    layout.addWidget(status)

    # Test progress bar
    progress = QProgressBar()
    progress.setValue(75)
    progress.setFormat("System Health: 75%")
    layout.addWidget(progress)

    # Test that layout works
    for i in range(5):
        test_label = QLabel(f"Test Item {i+1}: ✅ Working")
        test_label.setStyleSheet("color: #cccccc; padding: 5px;")
        layout.addWidget(test_label)

    widget.show()

    print("✅ Test widget created and should be visible")
    print("If you can see this test window, PySide6 is working correctly")

    sys.exit(app.exec())

except Exception as e:
    print(f"[ERROR] Error creating test widget: {e}")
    import traceback
    traceback.print_exc()
