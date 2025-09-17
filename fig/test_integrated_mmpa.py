#!/usr/bin/env python3
"""
Test Integrated MMPA System with Musical Intelligence
Tests the complete audio-visual system with genre detection, key signatures, and chord progressions
"""

import sys
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

# Import the enhanced MMPA system
from enhanced_visual_morphing_mmpa import MMPAMorphWidget

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MMPATestWindow(QMainWindow):
    """Test window for integrated MMPA system"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 MMPA Musical Intelligence Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Add title
        title = QLabel("🎼 MMPA Musical Intelligence Visualization")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2E86AB; margin: 10px;")
        layout.addWidget(title)

        # Add instructions
        instructions = QLabel("""
🎧 Instructions:
1. Route audio through BlackHole 64ch
2. Play music - watch the system detect:
   • Genre (rock, jazz, classical, electronic, etc.)
   • Key signature (affects color palette)
   • Chord progressions (affects shape morphing)
   • BPM and rhythm (affects animation speed)
   • Frequency emphasis (creates colored particle bands)

🎯 Musical Intelligence Features:
   • Genre Classification → Visual Styles
   • Key Detection → Color Palettes
   • Chord Analysis → Form Transformations
   • Beat Detection → Synchronized Effects
   • Harmonic Analysis → Particle Arrangements
        """)
        instructions.setFont(QFont("Arial", 10))
        instructions.setStyleSheet("background-color: #F0F8FF; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)

        # Create MMPA morph widget with musical intelligence
        self.mmpa_widget = MMPAMorphWidget()
        layout.addWidget(self.mmpa_widget)

        # Add status display
        self.status_label = QLabel("🎵 Waiting for audio...")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("background-color: #2E86AB; color: white; padding: 5px; border-radius: 3px;")
        layout.addWidget(self.status_label)

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second

        logger.info("🚀 MMPA Test Window initialized")

    def update_status(self):
        """Update status display with current musical intelligence info"""
        if hasattr(self.mmpa_widget, 'signal_history') and self.mmpa_widget.signal_history:
            # Get latest signal data
            latest_signal = self.mmpa_widget.signal_history[-1]
            features = latest_signal['features']

            if hasattr(features, 'raw_data') and features.raw_data:
                raw_data = features.raw_data

                # Extract musical intelligence info
                genre = raw_data.get('genre', 'unknown')
                key_sig = raw_data.get('key_signature', 'unknown')
                chord = raw_data.get('chord', 'unknown')
                bpm = raw_data.get('bpm', 0)

                # Format status
                status_text = f"🎭 Genre: {genre} | 🎨 Key: {key_sig} | 🎸 Chord: {chord} | 🥁 BPM: {bpm:.1f}"

                # Add style indicators if available
                style_indicators = raw_data.get('style_indicators', {})
                if style_indicators:
                    tempo_style = style_indicators.get('tempo', 'unknown')
                    rhythm_style = style_indicators.get('rhythm', 'unknown')
                    status_text += f" | ⚡ {tempo_style}, {rhythm_style}"

                self.status_label.setText(status_text)
            else:
                self.status_label.setText("🎵 Audio detected - analyzing musical intelligence...")
        else:
            self.status_label.setText("🎵 Waiting for audio input...")

def main():
    """Run the integrated MMPA test"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show test window
    window = MMPATestWindow()
    window.show()

    logger.info("🎼 MMPA Musical Intelligence Test started")
    logger.info("🎧 Route audio through BlackHole 64ch to see musical intelligence in action!")

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()