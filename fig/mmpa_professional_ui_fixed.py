#!/usr/bin/env python3
"""
MMPA Professional UI - Fixed Integration Version
===============================================

Simplified professional interface that works with existing MMPA systems.
This version removes complex dependencies and focuses on core functionality
that integrates with our verified working components.
"""

import sys
import math
import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QSpinBox, QTextEdit, QTabWidget, QProgressBar,
    QSplitter, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Use existing verified components
try:
    from enhanced_visual_morphing_mmpa import EnhancedMorphWidget
    ENHANCED_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Using existing enhanced morphing widget")
except ImportError:
    ENHANCED_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Enhanced widget not available, using basic fallback")

class ProfessionalControlPanel(QWidget):
    """Professional control panel that works with existing systems"""

    def __init__(self, morph_widget, parent=None):
        super().__init__(parent)
        self.morph_widget = morph_widget
        self.setMaximumWidth(350)
        self._setup_ui()

    def _setup_ui(self):
        """Setup professional control interface"""
        layout = QVBoxLayout(self)

        # Professional header
        header_label = QLabel("🚀 MMPA Professional Controls")
        header_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            }
        """)
        layout.addWidget(header_label)

        # Control tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #34495e; background: #2c3e50; }
            QTabBar::tab { background: #34495e; color: white; padding: 8px 12px; margin: 2px; }
            QTabBar::tab:selected { background: #e74c3c; }
        """)

        # Morphing tab
        morph_tab = self._create_morphing_tab()
        tabs.addTab(morph_tab, "🔷 Shapes")

        # Performance tab
        perf_tab = self._create_performance_tab()
        tabs.addTab(perf_tab, "⚡ Performance")

        # Intelligence tab
        intel_tab = self._create_intelligence_tab()
        tabs.addTab(intel_tab, "🧠 Intelligence")

        layout.addWidget(tabs)

        # Status section
        status_section = self._create_status_section()
        layout.addWidget(status_section)

    def _create_morphing_tab(self):
        """Create morphing controls tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Shape selection
        shapes_group = QGroupBox("🔷 Shape Selection")
        shapes_layout = QGridLayout(shapes_group)

        # Get available shapes from the widget
        if hasattr(self.morph_widget, 'available_shapes'):
            shapes = self.morph_widget.available_shapes
        else:
            shapes = ['sphere', 'cube', 'torus', 'dodecahedron', 'icosahedron']

        shapes_layout.addWidget(QLabel("Primary:"), 0, 0)
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems(shapes)
        if hasattr(self.morph_widget, 'shape_a'):
            self.shape_a_combo.setCurrentText(self.morph_widget.shape_a)
        self.shape_a_combo.currentTextChanged.connect(self._update_shapes)
        shapes_layout.addWidget(self.shape_a_combo, 0, 1)

        shapes_layout.addWidget(QLabel("Secondary:"), 1, 0)
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems(shapes)
        if hasattr(self.morph_widget, 'shape_b'):
            self.shape_b_combo.setCurrentText(self.morph_widget.shape_b)
        self.shape_b_combo.currentTextChanged.connect(self._update_shapes)
        shapes_layout.addWidget(self.shape_b_combo, 1, 1)

        layout.addWidget(shapes_group)

        # Quality controls
        quality_group = QGroupBox("📐 Quality")
        quality_layout = QGridLayout(quality_group)

        quality_layout.addWidget(QLabel("Resolution:"), 0, 0)
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(200, 2000)
        current_res = getattr(self.morph_widget, 'shape_resolution', 800)
        self.resolution_slider.setValue(current_res)
        self.resolution_slider.valueChanged.connect(self._update_resolution)
        quality_layout.addWidget(self.resolution_slider, 0, 1)

        self.resolution_label = QLabel(str(current_res))
        quality_layout.addWidget(self.resolution_label, 0, 2)

        layout.addWidget(quality_group)

        # Advanced features
        features_group = QGroupBox("✨ Features")
        features_layout = QVBoxLayout(features_group)

        self.multi_layer_cb = QCheckBox("Multi-Layer Morphing")
        self.multi_layer_cb.setChecked(getattr(self.morph_widget, 'use_multi_layer', True))
        self.multi_layer_cb.toggled.connect(self._toggle_multilayer)
        features_layout.addWidget(self.multi_layer_cb)

        self.physics_cb = QCheckBox("Particle Physics")
        self.physics_cb.setChecked(getattr(self.morph_widget, 'use_physics', True))
        self.physics_cb.toggled.connect(self._toggle_physics)
        features_layout.addWidget(self.physics_cb)

        self.trails_cb = QCheckBox("Particle Trails")
        self.trails_cb.setChecked(getattr(self.morph_widget, 'particle_trails', True))
        self.trails_cb.toggled.connect(self._toggle_trails)
        features_layout.addWidget(self.trails_cb)

        layout.addWidget(features_group)
        return tab

    def _create_performance_tab(self):
        """Create performance monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Performance display
        perf_group = QGroupBox("📊 Live Performance")
        perf_layout = QVBoxLayout(perf_group)

        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        self.performance_text.setStyleSheet("""
            QTextEdit {
                background: #2c3e50; color: #2ecc71;
                font-family: monospace; font-size: 11px;
            }
        """)
        self.performance_text.setMaximumHeight(120)
        perf_layout.addWidget(self.performance_text)

        layout.addWidget(perf_group)

        # Performance settings
        settings_group = QGroupBox("⚙️ Settings")
        settings_layout = QGridLayout(settings_group)

        settings_layout.addWidget(QLabel("Target FPS:"), 0, 0)
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(30, 120)
        self.fps_spinbox.setValue(getattr(self.morph_widget, 'target_fps', 60))
        settings_layout.addWidget(self.fps_spinbox, 0, 1)

        self.performance_mode_cb = QCheckBox("Performance Mode")
        self.performance_mode_cb.setChecked(getattr(self.morph_widget, 'performance_mode', False))
        settings_layout.addWidget(self.performance_mode_cb, 1, 0, 1, 2)

        layout.addWidget(settings_group)

        # Update performance display
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self._update_performance_display)
        self.perf_timer.start(1000)

        return tab

    def _create_intelligence_tab(self):
        """Create musical intelligence tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Intelligence display
        intel_group = QGroupBox("🧠 Musical Analysis")
        intel_layout = QVBoxLayout(intel_group)

        self.intelligence_text = QTextEdit()
        self.intelligence_text.setReadOnly(True)
        self.intelligence_text.setStyleSheet("""
            QTextEdit {
                background: #34495e; color: #e67e22;
                font-family: monospace; font-size: 11px;
            }
        """)
        self.intelligence_text.setMaximumHeight(120)
        intel_layout.addWidget(self.intelligence_text)

        layout.addWidget(intel_group)

        # Genre controls
        genre_group = QGroupBox("🎭 Manual Genre Override")
        genre_layout = QVBoxLayout(genre_group)

        genres = ['auto', 'jazz', 'classical', 'rock', 'electronic', 'blues', 'folk']
        for genre in genres:
            btn = QPushButton(f"{genre.title()}")
            btn.clicked.connect(lambda checked, g=genre: self._set_genre(g))
            genre_layout.addWidget(btn)

        layout.addWidget(genre_group)

        # Update intelligence display
        self.intel_timer = QTimer()
        self.intel_timer.timeout.connect(self._update_intelligence_display)
        self.intel_timer.start(500)

        return tab

    def _create_status_section(self):
        """Create status display section"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Box)
        status_frame.setStyleSheet("""
            QFrame { background: #34495e; color: white; padding: 8px; border-radius: 4px; }
        """)

        layout = QHBoxLayout(status_frame)

        self.fps_status = QLabel("FPS: --")
        self.genre_status = QLabel("Genre: --")
        self.connection_status = QLabel("🔌 Connected")

        layout.addWidget(self.fps_status)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.genre_status)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.connection_status)

        # Update status
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)

        return status_frame

    # Event handlers
    def _update_shapes(self):
        """Update shapes in the morphing widget"""
        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()

        if hasattr(self.morph_widget, 'set_shapes'):
            self.morph_widget.set_shapes(shape_a, shape_b)
        elif hasattr(self.morph_widget, 'shape_a'):
            self.morph_widget.shape_a = shape_a
            self.morph_widget.shape_b = shape_b

    def _update_resolution(self):
        """Update resolution"""
        resolution = self.resolution_slider.value()
        self.resolution_label.setText(str(resolution))

        if hasattr(self.morph_widget, 'shape_resolution'):
            self.morph_widget.shape_resolution = resolution

    def _toggle_multilayer(self, enabled):
        """Toggle multi-layer morphing"""
        if hasattr(self.morph_widget, 'use_multi_layer'):
            self.morph_widget.use_multi_layer = enabled

    def _toggle_physics(self, enabled):
        """Toggle physics"""
        if hasattr(self.morph_widget, 'use_physics'):
            self.morph_widget.use_physics = enabled

    def _toggle_trails(self, enabled):
        """Toggle particle trails"""
        if hasattr(self.morph_widget, 'particle_trails'):
            self.morph_widget.particle_trails = enabled

    def _set_genre(self, genre):
        """Set genre override"""
        if hasattr(self.morph_widget, '_apply_genre_visual_style'):
            self.morph_widget._apply_genre_visual_style(genre)

    def _update_performance_display(self):
        """Update performance display"""
        try:
            fps = getattr(self.morph_widget, 'current_fps', 'N/A')
            frame_count = getattr(self.morph_widget, 'frame_count', 'N/A')
            resolution = getattr(self.morph_widget, 'shape_resolution', 'N/A')

            perf_text = f"""🚀 MMPA Performance Monitor
{"="*25}
FPS: {fps}
Frames: {frame_count}
Resolution: {resolution} points
Features: Multi-layer, Physics, Intelligence
Status: Running"""

            self.performance_text.setText(perf_text)
        except Exception as e:
            self.performance_text.setText(f"Performance data unavailable: {e}")

    def _update_intelligence_display(self):
        """Update musical intelligence display"""
        try:
            genre = getattr(self.morph_widget, 'current_genre', 'unknown')
            key = getattr(self.morph_widget, 'current_key', 'unknown')
            tempo = getattr(self.morph_widget, 'current_tempo', 'unknown')

            intel_text = f"""🎵 Musical Intelligence
{"="*20}
Genre: {genre.title()}
Key: {key.title()}
Tempo: {tempo} BPM
Analysis: Real-time
Visual Mapping: Active"""

            self.intelligence_text.setText(intel_text)
        except Exception as e:
            self.intelligence_text.setText(f"Intelligence data unavailable: {e}")

    def _update_status(self):
        """Update status bar"""
        try:
            fps = getattr(self.morph_widget, 'current_fps', 0)
            genre = getattr(self.morph_widget, 'current_genre', 'unknown')

            self.fps_status.setText(f"FPS: {fps:.1f}" if isinstance(fps, (int, float)) else "FPS: --")
            self.genre_status.setText(f"Genre: {genre.title()}")

            # Update connection status based on MMPA engine
            if hasattr(self.morph_widget, 'mmpa_engine'):
                self.connection_status.setText("🟢 MMPA Active")
            else:
                self.connection_status.setText("🟡 Basic Mode")

        except Exception as e:
            logger.warning(f"Status update error: {e}")

class MMPAProfessionalDemo(QMainWindow):
    """Professional MMPA demo using existing components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 MMPA Professional System - Integrated")
        self.setGeometry(50, 50, 1400, 900)

        self._setup_ui()
        self._setup_menu()

        logger.info("🚀 MMPA Professional Demo initialized")

    def _setup_ui(self):
        """Setup main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        splitter = QSplitter(Qt.Horizontal)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)

        # Create morphing widget (use enhanced if available)
        if ENHANCED_AVAILABLE:
            self.morph_widget = EnhancedMorphWidget()
            logger.info("✅ Using enhanced morphing widget")
        else:
            # Fallback to basic widget
            self.morph_widget = BasicFallbackWidget()
            logger.info("⚠️ Using fallback widget")

        splitter.addWidget(self.morph_widget)

        # Professional controls
        self.control_panel = ProfessionalControlPanel(self.morph_widget)
        splitter.addWidget(self.control_panel)

        # Set splitter proportions
        splitter.setSizes([1050, 350])

    def _setup_menu(self):
        """Setup menu system"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Session", lambda: logger.info("New session"))
        file_menu.addAction("Save Settings", lambda: logger.info("Save settings"))
        file_menu.addAction("Export Performance", lambda: logger.info("Export performance"))

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Fullscreen", self._toggle_fullscreen)
        view_menu.addAction("Reset Layout", lambda: logger.info("Reset layout"))

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Audio Setup", lambda: logger.info("Audio setup"))
        tools_menu.addAction("MIDI Config", lambda: logger.info("MIDI config"))

        # Status bar
        self.statusBar().showMessage("🚀 MMPA Professional System Ready")

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().showMessage("Windowed mode")
        else:
            self.showFullScreen()
            self.statusBar().showMessage("Fullscreen mode - Press Esc to exit")

class BasicFallbackWidget(QOpenGLWidget):
    """Basic fallback widget when enhanced version unavailable"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation = 0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.shape_resolution = 800
        self.current_fps = 60.0
        self.frame_count = 0
        self.current_genre = 'unknown'
        self.current_key = 'unknown'
        self.current_tempo = 120

        # Available shapes
        self.available_shapes = ['sphere', 'cube', 'torus']

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

    def initializeGL(self):
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.rotation, 1.0, 1.0, 0.0)

        # Simple rendering
        glColor3f(0.5, 0.8, 1.0)
        glBegin(GL_POINTS)
        for i in range(100):
            angle = (i / 100.0) * 2 * math.pi
            x = math.cos(angle)
            y = math.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()

    def update_animation(self):
        self.rotation += 1.0
        self.frame_count += 1
        self.update()

    def set_shapes(self, shape_a, shape_b):
        self.shape_a = shape_a
        self.shape_b = shape_b

def main():
    """Launch professional MMPA demo"""
    app = QApplication(sys.argv)

    window = MMPAProfessionalDemo()
    window.show()

    print("🚀 MMPA Professional System - Testing Version")
    print("=" * 50)
    if ENHANCED_AVAILABLE:
        print("✅ Using enhanced morphing system")
        print("✅ Full feature integration available")
    else:
        print("⚠️ Using basic fallback system")
        print("⚠️ Limited features available")

    print("✅ Professional UI controls")
    print("✅ Real-time performance monitoring")
    print("✅ Musical intelligence display")
    print("✅ Multi-tab control interface")
    print()
    print("🎵 Test the controls and monitor system performance!")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()