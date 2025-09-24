
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
import time

class AudioProcessingThread(QThread):
    update_signal = Signal(float, float)  # Tempo and onset time signal

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            # Simulate audio processing (this would be replaced with actual logic)
            tempo = 120.0  # Example tempo
            onset_time = time.time()  # Simulated onset time

            # Emit signal for GUI update
            self.update_signal.emit(tempo, onset_time)
            time.sleep(0.1)  # Simulate delay in processing

    def stop(self):
        self.running = False
        self.wait()  # Ensure the thread stops gracefully

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio Visual Sync")
        self.setGeometry(100, 100, 800, 600)

        # Layout and widgets
        self.label = QLabel("Tempo: 120 BPM", self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        # Main container
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Initialize Audio Processing Thread
        self.audio_thread = AudioProcessingThread()
        self.audio_thread.update_signal.connect(self.update_gui)
        self.audio_thread.start()

    def update_gui(self, tempo, onset_time):
        # Update GUI based on audio analysis
        self.label.setText(f"Tempo: {tempo:.2f} BPM
Onset Time: {onset_time:.2f} s")

    def closeEvent(self, event):
        self.audio_thread.stop()  # Stop the thread gracefully
        event.accept()
