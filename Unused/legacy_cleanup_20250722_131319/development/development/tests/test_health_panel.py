"""
ISOLATED TEST PANEL - This will prove if our class instantiation works
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SystemHealthPanel(QWidget):
    """ISOLATED TEST VERSION"""

    def __init__(self, parent=None):
        super().__init__(parent)

        print("\n" + "🚨" * 50)
        print("🚨 ISOLATED TEST: SystemHealthPanel constructor called!")
        print("🚨" * 50 + "\n")

        layout = QVBoxLayout(self)

        label = QLabel("🚨 ISOLATED TEST PANEL WORKS! 🚨")
        label.setStyleSheet("""
            QLabel {
                background-color: red;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 40px;
                border: 5px solid yellow;
            }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        print("🚨 ISOLATED TEST: Panel created successfully!")


if __name__ == "__main__":
    # Direct test
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    panel = SystemHealthPanel()
    panel.show()
    app.exec()
