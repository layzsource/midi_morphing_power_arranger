#!/usr/bin/env python3
"""
Simple MIDI Morphing Visualizer - Master Plan Aligned
Week 1-2 Foundation: Focused morphing display without complex multi-window interface.

This is the simplified version that focuses on the core morphing functionality
as specified in the fig_master_plan.txt roadmap.
"""

import sys
import os
import logging
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QBrush
from PySide6.QtOpenGLWidgets import QOpenGLWidget

# Import the enhanced foundation but use it selectively
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from enhanced_foundation import (
    MorphingEngine, EnhancedGLWidget, AudioEngine, MidiHandler,
    MorphShapes, ParticleSystem, LightingSystem, logger, audio_state
)

class AudioVisualizationWidget(QWidget):
    """Compact audio visualization widget for the simple morphing system"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(280, 120)  # Compact size
        self.setStyleSheet("background-color: black; border: 1px solid gray;")

        # Audio data storage
        self.fft_data = np.zeros(64)  # Smaller FFT for compact display
        self.waveform_data = np.zeros(256)
        self.spectral_centroid = 0.0
        self.amplitude = 0.0

        # Colors
        self.fft_color = QColor(0, 255, 128)  # Green
        self.waveform_color = QColor(0, 128, 255)  # Blue
        self.centroid_color = QColor(255, 255, 0)  # Yellow

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_data)
        self.update_timer.start(50)  # 20 FPS

    def _update_data(self):
        """Update audio visualization data"""
        try:
            if not audio_state.audio_enabled:
                # When audio is off, show idle state
                self.fft_data = np.random.random(64) * 0.1  # Very low noise
                self.waveform_data = np.zeros(256)
                self.spectral_centroid = 0.0
                self.amplitude = 0.0
            else:
                # Get real audio data from the audio state
                self.amplitude = audio_state.amplitude
                self.spectral_centroid = audio_state.centroid_hz

                # Generate simplified FFT visualization
                if hasattr(audio_state, 'fft_data') and audio_state.fft_data is not None:
                    # Downsample FFT data for compact display
                    full_fft = np.abs(audio_state.fft_data)
                    if len(full_fft) > 64:
                        # Average bins to reduce to 64 bars
                        step = len(full_fft) // 64
                        self.fft_data = np.array([np.mean(full_fft[i:i+step]) for i in range(0, len(full_fft), step)][:64])
                    else:
                        self.fft_data = full_fft[:64]
                else:
                    # Fallback: generate data based on amplitude
                    self.fft_data = np.random.random(64) * self.amplitude

            # Trigger repaint
            self.update()

        except Exception as e:
            # Silent error handling for visualization
            pass

    def paintEvent(self, event):
        """Paint the audio visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Clear background
        painter.fillRect(self.rect(), QColor(20, 20, 20))

        # Draw FFT bars (top half)
        bar_width = self.width() / len(self.fft_data)
        fft_height = self.height() // 2 - 10

        painter.setPen(QPen(self.fft_color, 1))
        painter.setBrush(QBrush(self.fft_color))

        for i, magnitude in enumerate(self.fft_data):
            x = i * bar_width
            bar_height = min(magnitude * fft_height * 50, fft_height)  # Scale appropriately
            y = fft_height - bar_height + 5
            painter.drawRect(int(x), int(y), int(bar_width - 1), int(bar_height))

        # Draw spectral centroid indicator
        if self.spectral_centroid > 0 and audio_state.audio_enabled:
            centroid_x = (self.spectral_centroid / 8000.0) * self.width()  # Assume 8kHz max
            painter.setPen(QPen(self.centroid_color, 2))
            painter.drawLine(int(centroid_x), 5, int(centroid_x), fft_height)

        # Draw amplitude meter (bottom)
        amp_rect_y = fft_height + 15
        amp_rect_height = 20
        amp_width = self.amplitude * self.width()

        # Background
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawRect(0, amp_rect_y, self.width(), amp_rect_height)

        # Amplitude bar
        if self.amplitude > 0:
            painter.setBrush(QBrush(self.waveform_color))
            painter.drawRect(0, amp_rect_y, int(amp_width), amp_rect_height)

        # Labels
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(5, fft_height - 5, "FFT")
        painter.drawText(5, amp_rect_y + amp_rect_height - 5, f"Amp: {self.amplitude:.2f}")

        if self.spectral_centroid > 0:
            painter.drawText(self.width() - 80, 15, f"Cent: {self.spectral_centroid:.0f}Hz")

class SimpleMorphingWindow(QMainWindow):
    """
    Simplified morphing window aligned with fig master plan Week 1-2.
    Focuses on clear, visible morphing without complex multi-window interface.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple MIDI Morphing Visualizer - Master Plan Aligned')
        self.setGeometry(200, 200, 1000, 700)

        # Initialize core systems with higher quality settings
        self.morph_engine = MorphingEngine(resolution=32)

        # FORCE higher quality for clear visualization
        self.morph_engine.render_idx = 2  # Solid rendering mode

        # Initialize audio engine (but keep it OFF by default)
        self.audio_engine = AudioEngine()

        # Initialize minimal systems for GL widget compatibility
        self.particle_system = ParticleSystem()
        self.lighting_system = LightingSystem()

        # Initialize GL widget with minimal systems
        self.gl_widget = EnhancedGLWidget(
            self.morph_engine,
            self.particle_system,
            self.lighting_system
        )

        # Force quality settings for clear morphing
        self._force_high_quality()

        # Initialize MIDI handler
        self.midi_handler = MidiHandler(
            self.morph_engine,
            self.audio_engine,
            midi_note_callback=self._on_midi_note,
            desired_port_substr='MPK',
            main_window=self
        )

        # Manual control state
        self.manual_morph_control = False

        # Setup UI
        self._setup_ui()

        # Setup update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_display)
        self.ui_timer.start(50)  # 20 FPS updates

        logger.info("🎯 Simple Morphing Visualizer initialized - Master Plan Week 1-2 aligned")

    def _force_high_quality(self):
        """Force high quality settings for clear morphing visualization"""
        try:
            # Force the GL widget to use better quality settings
            if hasattr(self.gl_widget, 'quality_controller'):
                # Override ultra_low quality with medium quality
                self.gl_widget.quality_controller.current_preset = 'medium'
                logger.info("🎨 Forced quality preset to: medium for clear morphing")

            # Force better render quality
            self.morph_engine.render_idx = 2  # Solid rendering

        except Exception as e:
            logger.warning(f"Quality forcing failed: {e}")

    def _setup_ui(self):
        """Setup simplified UI focused on morphing controls"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout: 70% visualization, 30% controls
        main_layout = QHBoxLayout(central_widget)

        # Left side: Large morphing visualization
        viz_frame = QFrame()
        viz_frame.setFrameStyle(QFrame.Box)
        viz_frame.setLineWidth(2)
        viz_layout = QVBoxLayout(viz_frame)

        # Title for visualization area
        viz_title = QLabel("🎯 Morphing Visualization")
        viz_title.setFont(QFont("Arial", 14, QFont.Bold))
        viz_title.setAlignment(Qt.AlignCenter)
        viz_layout.addWidget(viz_title)

        # The main GL widget (large and prominent)
        self.gl_widget.setMinimumSize(700, 500)
        viz_layout.addWidget(self.gl_widget)

        # Right side: Simplified controls
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Box)
        controls_frame.setLineWidth(2)
        controls_frame.setMaximumWidth(280)
        controls_layout = QVBoxLayout(controls_frame)

        # Title
        controls_title = QLabel("🎮 Morphing Controls")
        controls_title.setFont(QFont("Arial", 12, QFont.Bold))
        controls_title.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(controls_title)

        # Shape selection group
        shapes_group = QGroupBox("Shape Selection")
        shapes_layout = QVBoxLayout(shapes_group)

        # Shape A dropdown
        shapes_layout.addWidget(QLabel("Shape A (Start):"))
        self.shape_a_combo = QComboBox()
        for shape in MorphShapes:
            self.shape_a_combo.addItem(shape.value.replace('_', ' ').title(), shape)
        self.shape_a_combo.setCurrentText("Sphere")
        self.shape_a_combo.currentTextChanged.connect(self._on_shape_a_changed)
        shapes_layout.addWidget(self.shape_a_combo)

        # Shape B dropdown
        shapes_layout.addWidget(QLabel("Shape B (Target):"))
        self.shape_b_combo = QComboBox()
        for shape in MorphShapes:
            self.shape_b_combo.addItem(shape.value.replace('_', ' ').title(), shape)
        self.shape_b_combo.setCurrentText("Cube")
        self.shape_b_combo.currentTextChanged.connect(self._on_shape_b_changed)
        shapes_layout.addWidget(self.shape_b_combo)

        controls_layout.addWidget(shapes_group)

        # Morphing control group
        morph_group = QGroupBox("Morphing Control")
        morph_layout = QVBoxLayout(morph_group)

        # Large, prominent morph slider
        morph_layout.addWidget(QLabel("Morph Factor:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.setMinimumHeight(30)  # Make it prominent
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        morph_layout.addWidget(self.morph_slider)

        # Morph value display
        self.morph_value_label = QLabel("0%")
        self.morph_value_label.setAlignment(Qt.AlignCenter)
        self.morph_value_label.setFont(QFont("Arial", 12, QFont.Bold))
        morph_layout.addWidget(self.morph_value_label)

        # Manual control reset button
        reset_btn = QPushButton("Enable MIDI Control")
        reset_btn.setToolTip("Allow MIDI CC1 to control morphing")
        reset_btn.clicked.connect(self._reset_manual_control)
        morph_layout.addWidget(reset_btn)

        controls_layout.addWidget(morph_group)

        # Connection status group
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)

        # MIDI status
        self.midi_status_label = QLabel("MIDI: Checking...")
        status_layout.addWidget(self.midi_status_label)

        # Audio status
        self.audio_status_label = QLabel("Audio: Off (Safe)")
        status_layout.addWidget(self.audio_status_label)

        # Audio enable button
        self.audio_btn = QPushButton("Enable Audio Analysis")
        self.audio_btn.clicked.connect(self._toggle_audio)
        status_layout.addWidget(self.audio_btn)

        controls_layout.addWidget(status_group)

        # Audio visualization group (NEW - Phase 1)
        audio_viz_group = QGroupBox("Audio Analysis")
        audio_viz_layout = QVBoxLayout(audio_viz_group)

        # Add the compact audio visualization widget
        self.audio_viz_widget = AudioVisualizationWidget()
        audio_viz_layout.addWidget(self.audio_viz_widget)

        # Auto-morph from audio checkbox
        self.auto_morph_audio_cb = QCheckBox("Auto-morph from spectral centroid")
        self.auto_morph_audio_cb.setChecked(False)
        self.auto_morph_audio_cb.stateChanged.connect(self._on_auto_morph_audio_changed)
        audio_viz_layout.addWidget(self.auto_morph_audio_cb)

        controls_layout.addWidget(audio_viz_group)

        # Quality info
        quality_group = QGroupBox("Rendering Info")
        quality_layout = QVBoxLayout(quality_group)

        self.quality_label = QLabel("Quality: Medium (Forced)")
        self.render_mode_label = QLabel("Mode: Solid")
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.render_mode_label)

        controls_layout.addWidget(quality_group)

        # Add stretch to push controls to top
        controls_layout.addStretch()

        # Add to main layout with proportions
        main_layout.addWidget(viz_frame, 7)  # 70% for visualization
        main_layout.addWidget(controls_frame, 3)  # 30% for controls

        # Set initial shapes
        self.morph_engine.shape_a = MorphShapes.SPHERE
        self.morph_engine.shape_b = MorphShapes.CUBE

    def _on_shape_a_changed(self, text):
        """Handle Shape A change"""
        try:
            shape_data = self.shape_a_combo.currentData()
            if shape_data:
                self.morph_engine.shape_a = shape_data
                logger.debug(f"Shape A changed to: {shape_data.value}")
        except Exception as e:
            logger.error(f"Error changing shape A: {e}")

    def _on_shape_b_changed(self, text):
        """Handle Shape B change"""
        try:
            shape_data = self.shape_b_combo.currentData()
            if shape_data:
                self.morph_engine.shape_b = shape_data
                logger.debug(f"Shape B changed to: {shape_data.value}")
        except Exception as e:
            logger.error(f"Error changing shape B: {e}")

    def _on_morph_slider_changed(self, value):
        """Handle manual morph slider change"""
        manual_morph = value / 100.0
        self.manual_morph_control = True
        self.morph_engine.morph = manual_morph
        self.morph_value_label.setText(f"{value}%")
        logger.debug(f"Manual morph: {manual_morph:.2f}")

    def _reset_manual_control(self):
        """Reset manual control to allow MIDI control"""
        self.manual_morph_control = False
        logger.info("Manual control reset: MIDI control restored")

    def _on_auto_morph_audio_changed(self, state):
        """Handle auto-morph from audio checkbox change"""
        if state == Qt.Checked:
            logger.info("🎵 Audio-driven morphing enabled")
        else:
            logger.info("🎵 Audio-driven morphing disabled")

    def _toggle_audio(self):
        """Toggle audio analysis on/off"""
        try:
            from enhanced_foundation import audio_state
            audio_state.audio_enabled = not audio_state.audio_enabled

            if audio_state.audio_enabled:
                self.audio_btn.setText("Disable Audio Analysis")
                self.audio_status_label.setText("Audio: On")
                logger.info("🔊 Audio analysis enabled")
            else:
                self.audio_btn.setText("Enable Audio Analysis")
                self.audio_status_label.setText("Audio: Off")
                logger.info("🔇 Audio analysis disabled")

        except Exception as e:
            logger.error(f"Audio toggle failed: {e}")

    def _on_midi_note(self, note, velocity, channel):
        """Handle MIDI note events with controlled particle effects"""
        try:
            logger.info(f"🎵 MIDI Note: {note}, Velocity: {velocity}, Channel: {channel}")

            # Add controlled particle burst for note events
            if velocity > 0:  # Note on
                self._create_midi_particle_burst(note, velocity, channel)

        except Exception as e:
            logger.error(f"MIDI note callback error: {e}")

    def _create_midi_particle_burst(self, note, velocity, channel):
        """Create controlled particle burst for MIDI note"""
        try:
            logger.info(f"🎆 Creating particle burst for note {note}, velocity {velocity}")
            # Map MIDI note to color (musical colors)
            # C=Red, C#=Orange, D=Yellow, etc.
            note_colors = [
                [1.0, 0.0, 0.0],  # C - Red
                [1.0, 0.3, 0.0],  # C# - Orange-Red
                [1.0, 0.6, 0.0],  # D - Orange
                [1.0, 1.0, 0.0],  # D# - Yellow
                [0.6, 1.0, 0.0],  # E - Yellow-Green
                [0.0, 1.0, 0.0],  # F - Green
                [0.0, 1.0, 0.6],  # F# - Green-Cyan
                [0.0, 0.6, 1.0],  # G - Cyan-Blue
                [0.0, 0.0, 1.0],  # G# - Blue
                [0.3, 0.0, 1.0],  # A - Blue-Violet
                [0.6, 0.0, 1.0],  # A# - Violet
                [1.0, 0.0, 0.6],  # B - Magenta
            ]

            color = note_colors[int(note) % 12]

            # Enhanced particle parameters (more visible)
            particle_count = min(int(velocity / 4), 30)  # Max 30 particles, more responsive
            burst_strength = velocity / 127.0 * 2.0      # Much stronger burst

            # Create small particle burst around current morph shape
            if hasattr(self.particle_system, 'emit_particles'):
                logger.info(f"✨ Calling particle_system.emit_particles with {particle_count} particles")
                import numpy as np
                from enhanced_foundation import ParticleType

                position = np.array([0.0, 0.0, 0.0])  # Center of morph shape
                velocity_base = np.array([
                    np.random.uniform(-2.0, 2.0),
                    np.random.uniform(-2.0, 2.0),
                    np.random.uniform(-2.0, 2.0)
                ]) * burst_strength

                self.particle_system.emit_particles(
                    position=position,
                    velocity=velocity_base,
                    count=particle_count,
                    particle_type=ParticleType.BURST,
                    size_range=(0.1, 0.3),    # Much larger particles
                    life_range=(2.0, 4.0)    # Longer lifetime for visibility
                )
            else:
                logger.warning("⚠️ Particle system does not have emit_particles method")

            # Optional: Subtle lighting pulse
            if hasattr(self.lighting_system, 'midi_pulse'):
                self.lighting_system.midi_pulse(color, velocity / 127.0 * 0.4)

        except Exception as e:
            logger.error(f"Particle burst creation failed: {e}")

    def _update_display(self):
        """Update display information"""
        try:
            # Update MIDI status
            if self.midi_handler.connected_device:
                self.midi_status_label.setText(f"MIDI: Connected ({self.midi_handler.connected_device})")
            else:
                self.midi_status_label.setText("MIDI: No device connected")

            # Update render mode
            self.render_mode_label.setText(f"Mode: {self.morph_engine.get_render_mode().title()}")

            # Audio-driven morphing (NEW - Phase 1)
            if (self.auto_morph_audio_cb.isChecked() and
                audio_state.audio_enabled and
                not self.manual_morph_control):

                # Use spectral centroid to drive morphing
                if hasattr(audio_state, 'centroid_hz') and audio_state.centroid_hz > 0:
                    # Map spectral centroid (typically 100-4000 Hz) to morph factor (0-1)
                    centroid_normalized = min(max(audio_state.centroid_hz - 100, 0) / 3900, 1.0)

                    # Apply smoothing to prevent jarring changes
                    current_morph = self.morph_engine.morph
                    target_morph = centroid_normalized
                    smoothed_morph = current_morph + (target_morph - current_morph) * 0.1

                    self.morph_engine.morph = smoothed_morph

                    # Update UI to reflect audio-driven morph
                    slider_value = int(smoothed_morph * 100)
                    self.morph_slider.setValue(slider_value)
                    self.morph_value_label.setText(f"{slider_value}% (Audio)")

        except Exception as e:
            logger.debug(f"Display update error: {e}")

def main():
    """Main entry point for simple morphing visualizer"""

    print("=" * 80)
    print("🎯 Simple MIDI Morphing Visualizer")
    print("=" * 80)
    print()
    print("🎪 STARTING FOCUSED MORPHING SYSTEM...")
    print()
    print("📋 ALIGNED WITH MASTER PLAN:")
    print("   • Week 1-2: Foundation with basic working loop")
    print("   • Large central morphing viewport")
    print("   • Simple shape selection and morph control")
    print("   • Clear, visible solid 3D morphing")
    print("   • MIDI integration with MPK Mini")
    print()
    print("🎮 CONTROLS:")
    print("   • Shape dropdowns: Select start/target shapes")
    print("   • Morph slider: Manual morphing control (0-100%)")
    print("   • MIDI CC1: Automatic morph control when not manual")
    print("   • Audio analysis: Optional, disabled by default")
    print()

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Simple MIDI Morphing Visualizer")
    app.setApplicationVersion("1.0 - Master Plan Aligned")

    try:
        window = SimpleMorphingWindow()
        window.show()

        print("🎉 SIMPLE MORPHING VISUALIZER READY!")
        print("    Focus on clear, visible morphing between 20 shapes")
        print("    Master Plan Week 1-2 foundation established")
        print()

        return app.exec()

    except Exception as e:
        logger.error(f"Failed to start simple morphing visualizer: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())