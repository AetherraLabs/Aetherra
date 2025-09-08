#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Simple GUI test to verify PySide6 works
"""
import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test GUI")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        label = QLabel("[OK] PySide6 GUI is working!")
        label.setStyleSheet("font-size: 18px; color: green; padding: 20px;")
        layout.addWidget(label)


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
