import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication(sys.argv)
window = QMainWindow()
window.setCentralWidget(QLabel("Test Window"))
window.resize(400, 300)
window.show()
print("Window should be visible now")
sys.exit(app.exec())
