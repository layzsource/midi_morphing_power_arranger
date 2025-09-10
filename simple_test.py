#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Window")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel("If you can read this, PySide6 is working"))
        layout.addWidget(QPushButton("Test Button"))
        
        print(f"Window size set to: {self.size()}")
        print("Window should be visible now...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Force window size and position
    window = TestWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    
    print(f"Actual window size: {window.size()}")
    print("Starting event loop...")
    
    sys.exit(app.exec())
