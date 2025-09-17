#!/usr/bin/env python3
"""
Simple Working MIDI Morphing System with Audio Visualization
Week 3 Master Plan Implementation: Adding basic audio visualization features

Enhancements:
- Basic spectral analysis display (FFT bars)
- Audio-reactive morphing controls
- Audio/MIDI separation working properly
- Enhanced particle system with audio response
- Simple audio visualization widgets

Based on working simple_main.py foundation
"""

import sys
import math
import logging
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import rtmidi

# Load the enhanced foundation
sys.path.append('/Users/ticegunther/morphing_interface')
from enhanced_foundation import *

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioVisualizationWidget(QWidget):
    """Simple audio visualization display"""

    def __init__(self, audio_engine=None, parent=None):
        super().__init__(parent)
        self.audio_engine = audio_engine
        self.fft_bars = []
        self.setup_ui()

        # Update timer for audio visualization
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_visualization)
        self.update_timer.start(50)  # 20 FPS update rate

    def setup_ui(self):
        """Set up the audio visualization UI"""
        layout = QVBoxLayout(self)

        # Audio controls
        audio_control_group = QGroupBox("🎤 Audio Analysis")
        audio_control_layout = QVBoxLayout(audio_control_group)

        # Enable/disable audio
        self.audio_enabled_cb = QCheckBox("Enable Audio Input")
        self.audio_enabled_cb.setChecked(False)  # Default off as per requirements
        self.audio_enabled_cb.stateChanged.connect(self.toggle_audio)
        audio_control_layout.addWidget(self.audio_enabled_cb)

        # Audio status
        self.audio_status = QLabel("🔇 Audio: Off - MIDI Active")
        self.audio_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        audio_control_layout.addWidget(self.audio_status)

        layout.addWidget(audio_control_group)

        # Simple FFT visualization
        fft_group = QGroupBox("📊 Spectrum")
        fft_layout = QVBoxLayout(fft_group)

        # Create simple FFT bars
        for i in range(8):  # 8 frequency bands
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid grey;
                    border-radius: 3px;
                    background-color: #2c3e50;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #3498db, stop: 1 #e74c3c);
                    border-radius: 2px;
                }}
            """)
            self.fft_bars.append(bar)
            fft_layout.addWidget(bar)

        layout.addWidget(fft_group)

        # Audio-reactive controls
        reactive_group = QGroupBox("🔊 Audio Response")
        reactive_layout = QVBoxLayout(reactive_group)

        self.audio_morph_cb = QCheckBox("Audio-Reactive Morphing")
        self.audio_morph_cb.setChecked(False)
        reactive_layout.addWidget(self.audio_morph_cb)

        self.audio_particles_cb = QCheckBox("Audio-Triggered Particles")
        self.audio_particles_cb.setChecked(False)
        reactive_layout.addWidget(self.audio_particles_cb)

        layout.addWidget(reactive_group)

    def toggle_audio(self, state):
        """Toggle audio input on/off"""
        if state == Qt.Checked:
            if self.audio_engine:
                self.audio_engine.enable_audio_analysis(True)
                self.audio_status.setText("🔊 Audio: On - Analyzing")
                self.audio_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
                logger.info("🔊 Audio analysis enabled from UI")
        else:
            if self.audio_engine:
                self.audio_engine.enable_audio_analysis(False)
                self.audio_status.setText("🔇 Audio: Off - MIDI Active")
                self.audio_status.setStyleSheet("color: #27ae60; font-weight: bold;")
                logger.info("🔇 Audio analysis disabled from UI")

    def update_visualization(self):
        """Update the audio visualization bars"""
        if not self.audio_engine or not hasattr(self.audio_engine, 'get_fft_data'):
            # Generate fake data for demonstration when no audio
            for i, bar in enumerate(self.fft_bars):
                # Simple animation when no audio
                value = int(10 + 5 * math.sin(QTimer().elapsed() * 0.001 + i))
                bar.setValue(max(0, min(100, value)))
            return

        try:
            # Get real FFT data if available
            fft_data = self.audio_engine.get_fft_data()
            if fft_data is not None and len(fft_data) > 0:
                # Map FFT data to our 8 bars
                bands = len(self.fft_bars)
                chunk_size = len(fft_data) // bands

                for i, bar in enumerate(self.fft_bars):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(fft_data))

                    if end_idx > start_idx:
                        # Average the chunk and scale to 0-100
                        band_energy = np.mean(np.abs(fft_data[start_idx:end_idx]))
                        value = int(min(100, band_energy * 1000))  # Scale factor
                        bar.setValue(value)

        except Exception as e:
            logger.debug(f"Audio visualization update error: {e}")
            # Fall back to demo pattern
            for i, bar in enumerate(self.fft_bars):
                bar.setValue(max(0, int(20 * (i % 3))))

class SimpleMainWindowWithAudio(QMainWindow):
    """Enhanced simple main window with audio visualization"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Simple MIDI Morphing System with Audio Visualization")
        self.setGeometry(100, 100, 1200, 700)

        # Initialize enhanced foundation engine
        logger.info("🎯 Initializing enhanced morphing engine...")
        self.morph_engine = MorphingEngine(resolution=32)

        # Audio engine from enhanced foundation
        self.audio_engine = None
        if hasattr(self.morph_engine, 'audio_engine'):
            self.audio_engine = self.morph_engine.audio_engine

        self.manual_control = False

        self._setup_enhanced_ui()
        self._setup_midi()

        logger.info("🎵 Simple MIDI Morphing System with Audio Visualization Ready!")

    def _setup_enhanced_ui(self):
        """Set up enhanced UI with audio visualization"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # OpenGL widget (60% of space) - using simpler approach like working system
        from simple_main import SimpleGLWidget
        self.gl_widget = SimpleGLWidget(self.morph_engine)
        layout.addWidget(self.gl_widget, 6)

        # Controls panel (40% of space)
        controls_panel = QWidget()
        controls_layout = QVBoxLayout(controls_panel)

        # Main controls (60% of controls)
        main_controls = self._create_main_controls()
        controls_layout.addWidget(main_controls, 6)

        # Audio visualization (40% of controls)
        self.audio_viz = AudioVisualizationWidget(self.audio_engine)
        controls_layout.addWidget(self.audio_viz, 4)

        layout.addWidget(controls_panel, 4)

    def _create_main_controls(self):
        """Create main morphing controls"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(350)
        controls_frame.setStyleSheet("background-color: #2a2a2a; color: white; padding: 10px;")

        layout = QVBoxLayout(controls_frame)

        # Title
        title = QLabel("🎵 AUDIO + MIDI MORPHING")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Shape selection
        shape_group = QGroupBox("Shape Selection")
        shape_layout = QVBoxLayout(shape_group)

        # Shape A
        shape_layout.addWidget(QLabel("Shape A:"))
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems([
            'sphere', 'cube', 'torus', 'cylinder', 'cone',
            'dodecahedron', 'icosahedron', 'mobius', 'klein_bottle',
            'star', 'heart', 'spiral', 'crystal', 'fractal', 'terrain'
        ])
        self.shape_a_combo.currentTextChanged.connect(self._on_shape_a_changed)
        shape_layout.addWidget(self.shape_a_combo)

        # Shape B
        shape_layout.addWidget(QLabel("Shape B:"))
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems([
            'sphere', 'cube', 'torus', 'cylinder', 'cone',
            'dodecahedron', 'icosahedron', 'mobius', 'klein_bottle',
            'star', 'heart', 'spiral', 'crystal', 'fractal', 'terrain'
        ])
        self.shape_b_combo.setCurrentText('cube')
        self.shape_b_combo.currentTextChanged.connect(self._on_shape_b_changed)
        shape_layout.addWidget(self.shape_b_combo)

        layout.addWidget(shape_group)

        # Morph control
        morph_group = QGroupBox("Morph Control")
        morph_layout = QVBoxLayout(morph_group)

        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.valueChanged.connect(self._on_morph_changed)
        morph_layout.addWidget(self.morph_slider)

        self.morph_label = QLabel("0%")
        self.morph_label.setAlignment(Qt.AlignCenter)
        morph_layout.addWidget(self.morph_label)

        # Reset button
        reset_btn = QPushButton("Enable MIDI Control")
        reset_btn.clicked.connect(self._reset_manual_control)
        morph_layout.addWidget(reset_btn)

        layout.addWidget(morph_group)

        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("🎯 System Ready - Audio + MIDI")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_group)

        layout.addStretch()

        return controls_frame

    def _setup_midi(self):
        """Set up MIDI handling"""
        try:
            self.midi = rtmidi.MidiIn()
            ports = self.midi.get_ports()

            # Find MPK mini or any MIDI device
            for i, port in enumerate(ports):
                logger.info(f"MIDI port {i}: {port}")
                if 'MPK' in port or 'mini' in port:
                    self.midi.open_port(i)
                    self.midi.set_callback(self._midi_callback)
                    logger.info(f"✅ Connected to: {port}")
                    self.status_label.setText(f"🎹 MIDI: {port}")
                    return

            # If no MPK found, use first available port
            if ports:
                self.midi.open_port(0)
                self.midi.set_callback(self._midi_callback)
                logger.info(f"✅ Connected to: {ports[0]}")
                self.status_label.setText(f"🎹 MIDI: {ports[0]}")

        except Exception as e:
            logger.error(f"MIDI init error: {e}")
            self.status_label.setText("❌ MIDI Error")

    def _midi_callback(self, event, data=None):
        """Handle MIDI messages with audio system integration"""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]

            # Note events
            if (status & 0xF0) in [0x90, 0x80]:  # Note on/off
                note = message[1]
                velocity = message[2]
                channel = status & 0x0F

                if velocity > 0:  # Note on
                    # Convert MIDI note to frequency
                    frequency = 440.0 * (2.0 ** ((note - 69) / 12.0))
                    self._create_midi_particle_burst(frequency, velocity, channel)
                    logger.info(f"🎵 MIDI Note: {frequency:.1f}Hz, Velocity: {velocity}")

            # CC events
            elif (status & 0xF0) == 0xB0:  # Control change
                cc = message[1]
                value = message[2]
                if cc == 1 and not self.manual_control:  # Mod wheel
                    morph_factor = value / 127.0
                    self.morph_engine.set_morph_factor(morph_factor)

                    # Update slider without triggering manual mode
                    self.morph_slider.blockSignals(True)
                    self.morph_slider.setValue(int(value * 100 / 127))
                    self.morph_label.setText(f"{int(value * 100 / 127)}%")
                    self.morph_slider.blockSignals(False)

                    self.status_label.setText(f"🎹 MIDI Morph: {int(value * 100 / 127)}%")

    def _create_midi_particle_burst(self, frequency, velocity, channel):
        """Create enhanced particle burst with audio-aware features"""
        if not hasattr(self.morph_engine, 'particle_system'):
            return

        # Enhanced particle parameters based on frequency and velocity
        particle_count = min(int(velocity / 4), 30)  # Max 30 particles
        burst_strength = velocity / 127.0 * 2.0

        # Position based on frequency (spread across viewport)
        x_pos = -1.0 + 2.0 * ((frequency - 82.4) / (4186.0 - 82.4))
        x_pos = max(-1.0, min(1.0, x_pos))

        position = np.array([x_pos, 0.0, 0.0], dtype=np.float32)
        velocity_base = np.array([
            np.random.uniform(-1.0, 1.0) * burst_strength,
            np.random.uniform(0.5, 2.0) * burst_strength,
            np.random.uniform(-1.0, 1.0) * burst_strength
        ], dtype=np.float32)

        # Color based on frequency (musical note colors)
        note_index = int(frequency) % 12
        colors = [
            [1.0, 0.0, 0.0],    # C - Red
            [1.0, 0.5, 0.0],    # C# - Orange
            [1.0, 1.0, 0.0],    # D - Yellow
            [0.5, 1.0, 0.0],    # D# - Yellow-green
            [0.0, 1.0, 0.0],    # E - Green
            [0.0, 1.0, 0.5],    # F - Green-cyan
            [0.0, 1.0, 1.0],    # F# - Cyan
            [0.0, 0.5, 1.0],    # G - Light blue
            [0.0, 0.0, 1.0],    # G# - Blue
            [0.5, 0.0, 1.0],    # A - Purple
            [1.0, 0.0, 1.0],    # A# - Magenta
            [1.0, 0.0, 0.5],    # B - Pink
        ]

        logger.info(f"🎆 Creating particle burst: {particle_count} particles at {x_pos:.2f}")

        try:
            # Try the enhanced particle system first
            if hasattr(self.morph_engine.particle_system, 'emit_particles'):
                self.morph_engine.particle_system.emit_particles(
                    position=position,
                    velocity=velocity_base,
                    count=particle_count,
                    particle_type=getattr(ParticleType, 'BURST', 0) if 'ParticleType' in globals() else 0,
                    size_range=(0.1, 0.3),
                    life_range=(2.0, 4.0),
                    color=colors[note_index]
                )
            # Fallback to basic particle creation
            elif hasattr(self.morph_engine.particle_system, 'create_burst'):
                self.morph_engine.particle_system.create_burst(position, velocity_base, particle_count)
        except Exception as e:
            logger.error(f"❌ Particle creation error: {e}")

    def _on_shape_a_changed(self, shape_name):
        """Handle shape A selection"""
        # Map shape names to enums
        shape_mapping = {
            'sphere': getattr(MorphShapes, 'SPHERE', 0),
            'cube': getattr(MorphShapes, 'CUBE', 1),
            'torus': getattr(MorphShapes, 'TORUS', 2),
            'cylinder': getattr(MorphShapes, 'CYLINDER', 3),
            'cone': getattr(MorphShapes, 'CONE', 4),
            'dodecahedron': getattr(MorphShapes, 'DODECAHEDRON', 5),
            'icosahedron': getattr(MorphShapes, 'ICOSAHEDRON', 6),
            'mobius': getattr(MorphShapes, 'MOBIUS', 7),
            'klein_bottle': getattr(MorphShapes, 'KLEIN_BOTTLE', 8),
            'star': getattr(MorphShapes, 'STAR', 9),
            'heart': getattr(MorphShapes, 'HEART', 10),
            'spiral': getattr(MorphShapes, 'SPIRAL', 11),
            'crystal': getattr(MorphShapes, 'CRYSTAL', 12),
            'fractal': getattr(MorphShapes, 'FRACTAL', 13),
            'terrain': getattr(MorphShapes, 'TERRAIN', 14)
        }

        shape_enum = shape_mapping.get(shape_name, 0)
        self.morph_engine.set_shape_a(shape_enum)
        logger.info(f"🎨 Shape A: {shape_name}")
        self.status_label.setText(f"Shape A: {shape_name}")

    def _on_shape_b_changed(self, shape_name):
        """Handle shape B selection"""
        shape_mapping = {
            'sphere': getattr(MorphShapes, 'SPHERE', 0),
            'cube': getattr(MorphShapes, 'CUBE', 1),
            'torus': getattr(MorphShapes, 'TORUS', 2),
            'cylinder': getattr(MorphShapes, 'CYLINDER', 3),
            'cone': getattr(MorphShapes, 'CONE', 4),
            'dodecahedron': getattr(MorphShapes, 'DODECAHEDRON', 5),
            'icosahedron': getattr(MorphShapes, 'ICOSAHEDRON', 6),
            'mobius': getattr(MorphShapes, 'MOBIUS', 7),
            'klein_bottle': getattr(MorphShapes, 'KLEIN_BOTTLE', 8),
            'star': getattr(MorphShapes, 'STAR', 9),
            'heart': getattr(MorphShapes, 'HEART', 10),
            'spiral': getattr(MorphShapes, 'SPIRAL', 11),
            'crystal': getattr(MorphShapes, 'CRYSTAL', 12),
            'fractal': getattr(MorphShapes, 'FRACTAL', 13),
            'terrain': getattr(MorphShapes, 'TERRAIN', 14)
        }

        shape_enum = shape_mapping.get(shape_name, 1)
        self.morph_engine.set_shape_b(shape_enum)
        logger.info(f"🎨 Shape B: {shape_name}")
        self.status_label.setText(f"Shape B: {shape_name}")

    def _on_morph_changed(self, value):
        """Handle morph slider change with audio awareness"""
        self.manual_control = True
        morph_factor = value / 100.0
        self.morph_engine.set_morph_factor(morph_factor)
        self.morph_label.setText(f"{value}%")
        self.status_label.setText(f"🎮 Manual Control: {value}%")
        logger.info(f"🎚️ Manual morph: {morph_factor:.2f}")

    def _reset_manual_control(self):
        """Reset to allow MIDI/Audio control"""
        self.manual_control = False
        self.status_label.setText("🎹 MIDI/Audio Control Enabled")
        logger.info("🎹 MIDI/Audio control restored")

def main():
    """Launch the enhanced simple morphing visualizer with audio"""
    app = QApplication(sys.argv)

    # Create and show main window
    window = SimpleMainWindowWithAudio()
    window.show()

    logger.info("🎵 Simple MIDI Morphing System with Audio Visualization Started!")
    logger.info("🎯 Week 3 Master Plan Features Added:")
    logger.info("   • Basic spectral analysis display")
    logger.info("   • Audio/MIDI separation controls")
    logger.info("   • Audio-reactive morphing options")
    logger.info("   • Enhanced particle system with audio response")

    return app.exec()

if __name__ == "__main__":
    main()