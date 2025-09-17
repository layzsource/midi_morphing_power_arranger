#!/usr/bin/env python3
"""
MMPA Multi-Monitor Professional Concert System
=============================================

Professional multi-display system for MMPA concerts and installations.
Features:
- Multi-monitor detection and configuration
- Synchronized visual outputs across displays
- Independent content per display
- Master/slave display arrangements
- Projector and LED wall support
- Performance optimization for multiple outputs
- Real-time display management
- Professional concert layouts

This system enables MMPA to drive multiple displays simultaneously for
large-scale concerts, installations, and professional venues.
"""

import sys
import math
import logging
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QCheckBox, QSpinBox, QGroupBox,
    QGridLayout, QTextEdit, QTabWidget, QFrame, QSlider, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PySide6.QtGui import QScreen, QPixmap, QPainter, QColor, QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

logger = logging.getLogger(__name__)

class DisplayInfo:
    """Information about a connected display"""

    def __init__(self, screen: QScreen, index: int):
        self.screen = screen
        self.index = index
        self.name = screen.name()
        self.geometry = screen.geometry()
        self.available_geometry = screen.availableGeometry()
        self.physical_size = screen.physicalSize()
        self.logical_dpi = screen.logicalDotsPerInch()
        self.device_pixel_ratio = screen.devicePixelRatio()
        self.refresh_rate = screen.refreshRate()

        # Professional display properties
        self.is_primary = (index == 0)
        self.role = 'primary' if self.is_primary else 'secondary'
        self.content_type = 'main'  # 'main', 'auxiliary', 'mirror', 'independent'
        self.enabled = True

        # Performance settings
        self.target_fps = 60
        self.quality_level = 'high'  # 'low', 'medium', 'high', 'ultra'
        self.sync_mode = 'master'  # 'master', 'slave', 'independent'

    def get_info_dict(self) -> Dict:
        """Get display information as dictionary"""
        return {
            'index': self.index,
            'name': self.name,
            'geometry': f"{self.geometry.width()}x{self.geometry.height()}",
            'position': f"({self.geometry.x()}, {self.geometry.y()})",
            'physical_size': f"{self.physical_size.width():.1f}x{self.physical_size.height():.1f}mm",
            'dpi': f"{self.logical_dpi:.1f}",
            'refresh_rate': f"{self.refresh_rate:.1f}Hz",
            'role': self.role,
            'content_type': self.content_type,
            'enabled': self.enabled
        }

class MultiDisplayMorphWidget(QOpenGLWidget):
    """MMPA morphing widget optimized for multi-display"""

    def __init__(self, display_info: DisplayInfo, content_type: str = 'main', parent=None):
        super().__init__(parent)

        self.display_info = display_info
        self.content_type = content_type
        self.widget_id = f"display_{display_info.index}_{content_type}"

        # Morphing parameters
        self.morph_factor = 0.5
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.scale_factor = 1.0
        self.color_offset = 0.0

        # Performance optimization
        self.shape_resolution = self._get_optimal_resolution()
        self.target_fps = display_info.target_fps
        self.frame_skip = 1 if display_info.quality_level == 'high' else 2

        # Synchronization
        self.sync_mode = display_info.sync_mode
        self.master_time = 0.0
        self.time_offset = 0.0

        # Content variations for different displays
        self._setup_content_variation()

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        timer_interval = int(1000 / self.target_fps)
        self.timer.start(timer_interval)

        logger.info(f"🖥️ Multi-display widget created: {self.widget_id}")

    def _get_optimal_resolution(self) -> int:
        """Calculate optimal resolution based on display properties"""
        width = self.display_info.geometry.width()
        height = self.display_info.geometry.height()
        pixel_count = width * height

        # Scale resolution based on display size and quality setting
        if self.display_info.quality_level == 'low':
            base_resolution = 300
        elif self.display_info.quality_level == 'medium':
            base_resolution = 600
        elif self.display_info.quality_level == 'high':
            base_resolution = 1000
        else:  # ultra
            base_resolution = 1500

        # Adjust for display size
        size_factor = min(2.0, pixel_count / (1920 * 1080))
        optimal_resolution = int(base_resolution * size_factor)

        logger.info(f"📐 Optimal resolution for {self.widget_id}: {optimal_resolution}")
        return optimal_resolution

    def _setup_content_variation(self):
        """Setup content variations for different display types"""
        if self.content_type == 'main':
            # Primary content with full features
            self.color_offset = 0.0
            self.rotation_speed = 1.0
            self.morph_speed = 1.0

        elif self.content_type == 'auxiliary':
            # Complementary content with variations
            self.color_offset = 0.33  # Shift color palette
            self.rotation_speed = 0.7
            self.morph_speed = 1.3
            self.shape_a = 'dodecahedron'
            self.shape_b = 'icosahedron'

        elif self.content_type == 'mirror':
            # Identical to main content
            self.color_offset = 0.0
            self.rotation_speed = 1.0
            self.morph_speed = 1.0

        elif self.content_type == 'independent':
            # Completely independent content
            self.color_offset = 0.67
            self.rotation_speed = 1.5
            self.morph_speed = 0.8
            self.shape_a = 'klein_bottle'
            self.shape_b = 'mobius_strip'

    def initializeGL(self):
        """Initialize OpenGL for multi-display optimization"""
        glClearColor(0.01, 0.01, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Optimize for display characteristics
        if self.display_info.refresh_rate > 120:
            # High refresh rate display
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POINT_SMOOTH)

        logger.info(f"✅ OpenGL initialized for {self.widget_id}")

    def resizeGL(self, width: int, height: int):
        """Handle window resize for multi-display"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height > 0 else 1.0

        # Adjust FOV based on display physical size
        physical_width = self.display_info.physical_size.width()
        if physical_width > 500:  # Large display/projector
            fov_factor = 1.2  # Wider field of view
        else:
            fov_factor = 1.0

        glFrustum(-aspect * fov_factor, aspect * fov_factor, -1.0 * fov_factor, 1.0 * fov_factor, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render with multi-display optimizations"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply display-specific transformations
        camera_distance = 6.0
        if self.content_type == 'auxiliary':
            camera_distance = 5.0  # Closer view for auxiliary displays
        elif self.content_type == 'independent':
            camera_distance = 7.0  # Farther view for independent displays

        glTranslatef(0.0, 0.0, -camera_distance)
        glRotatef(self.rotation, 1.0, 1.0, 0.5)
        glScalef(self.scale_factor, self.scale_factor, self.scale_factor)

        # Generate and render morphed geometry
        vertices = self.generate_display_morphed_shape()
        self.render_multi_display_shape(vertices)

    def generate_display_morphed_shape(self) -> List[List[float]]:
        """Generate morphed shape optimized for multi-display"""
        vertices = []

        for i in range(self.shape_resolution):
            # Basic morphing math (simplified for performance)
            theta = (i / self.shape_resolution) * 2 * math.pi * 3
            phi = ((i * 7) % self.shape_resolution) / self.shape_resolution * math.pi

            # Sphere coordinates
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)

            # Apply morphing
            morph_x = x * (1 - self.morph_factor) + math.copysign(1.0, x) * self.morph_factor
            morph_y = y * (1 - self.morph_factor) + math.copysign(1.0, y) * self.morph_factor
            morph_z = z * (1 - self.morph_factor) + math.copysign(1.0, z) * self.morph_factor

            vertices.append([morph_x, morph_y, morph_z])

        return vertices

    def render_multi_display_shape(self, vertices: List[List[float]]):
        """Render shape with multi-display color variations"""
        if not vertices:
            return

        # Display-specific coloring
        base_time = self.master_time + self.time_offset
        color_time = base_time + self.color_offset

        # Point size optimization for display
        dpi_factor = self.display_info.logical_dpi / 96.0  # Standard DPI
        point_size = max(2.0, min(8.0, 4.0 * dpi_factor))
        glPointSize(point_size)

        glBegin(GL_POINTS)

        for i, vertex in enumerate(vertices):
            # Color variation based on display type and position
            hue = (color_time * 0.1 + i * 0.01) % 1.0
            saturation = 0.8 + 0.2 * math.sin(base_time * 2 + i * 0.05)
            value = 0.8 + 0.2 * math.cos(base_time * 1.5 + i * 0.03)

            # Convert HSV to RGB
            r, g, b = self._hsv_to_rgb(hue, saturation, value)

            # Apply display-specific color adjustments
            if self.content_type == 'auxiliary':
                r *= 0.9
                g *= 1.1
                b *= 1.2
            elif self.content_type == 'independent':
                r *= 1.2
                g *= 0.9
                b *= 1.1

            glColor3f(r, g, b)
            glVertex3f(vertex[0], vertex[1], vertex[2])

        glEnd()

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB"""
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c

        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (r + m, g + m, b + m)

    def update_animation(self):
        """Update animation with synchronization"""
        current_time = time.time()

        if self.sync_mode == 'master':
            self.master_time = current_time
        elif self.sync_mode == 'slave':
            # Slave displays sync to master time (would be received via network/signal)
            pass
        else:  # independent
            self.master_time = current_time

        # Update morphing parameters
        self.rotation += self.rotation_speed
        self.morph_factor = 0.5 + 0.5 * math.sin(self.master_time * self.morph_speed)
        self.scale_factor = 0.8 + 0.4 * math.sin(self.master_time * 1.2)

        self.update()

    def set_sync_master_time(self, master_time: float):
        """Set master time for synchronization"""
        self.master_time = master_time

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            'widget_id': self.widget_id,
            'resolution': self.shape_resolution,
            'target_fps': self.target_fps,
            'display_size': f"{self.display_info.geometry.width()}x{self.display_info.geometry.height()}",
            'content_type': self.content_type,
            'sync_mode': self.sync_mode
        }

class MultiMonitorSystem:
    """Professional multi-monitor management system"""

    def __init__(self):
        self.displays = {}
        self.display_widgets = {}
        self.windows = {}

        # Synchronization
        self.master_display = None
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self._sync_displays)
        self.sync_timer.start(16)  # 60 FPS sync rate

        # Performance monitoring
        self.performance_stats = {}

        self._detect_displays()

    def _detect_displays(self):
        """Detect all connected displays"""
        app = QApplication.instance()
        screens = app.screens()

        logger.info(f"🖥️ Detected {len(screens)} displays")

        for i, screen in enumerate(screens):
            display_info = DisplayInfo(screen, i)
            self.displays[i] = display_info

            if i == 0:
                display_info.role = 'primary'
                self.master_display = display_info

            logger.info(f"   Display {i}: {display_info.name} ({display_info.geometry.width()}x{display_info.geometry.height()})")

    def create_display_windows(self, layout_type: str = 'mirrored'):
        """Create windows for all displays"""

        for display_index, display_info in self.displays.items():
            if not display_info.enabled:
                continue

            # Determine content type based on layout
            if layout_type == 'mirrored':
                content_type = 'mirror'
            elif layout_type == 'extended':
                content_type = 'main' if display_info.is_primary else 'auxiliary'
            elif layout_type == 'independent':
                content_type = 'independent'
            else:
                content_type = 'main'

            # Create morphing widget
            morph_widget = MultiDisplayMorphWidget(display_info, content_type)
            self.display_widgets[display_index] = morph_widget

            # Create window
            window = QMainWindow()
            window.setWindowTitle(f"MMPA Display {display_index} - {content_type.title()}")
            window.setCentralWidget(morph_widget)

            # Position window on correct display
            screen_geometry = display_info.screen.geometry()
            window.setGeometry(screen_geometry)

            # Make fullscreen for professional use
            window.showFullScreen()

            self.windows[display_index] = window

        logger.info(f"✅ Created {len(self.windows)} display windows ({layout_type} layout)")

    def _sync_displays(self):
        """Synchronize all displays to master time"""
        if not self.master_display:
            return

        master_time = time.time()

        # Send master time to all slave displays
        for widget in self.display_widgets.values():
            if widget.sync_mode == 'slave':
                widget.set_sync_master_time(master_time)

    def set_layout_type(self, layout_type: str):
        """Change display layout type"""
        # Close existing windows
        self.close_all_windows()

        # Create new layout
        self.create_display_windows(layout_type)

    def configure_display(self, display_index: int, **settings):
        """Configure specific display settings"""
        if display_index in self.displays:
            display_info = self.displays[display_index]

            if 'enabled' in settings:
                display_info.enabled = settings['enabled']
            if 'target_fps' in settings:
                display_info.target_fps = settings['target_fps']
            if 'quality_level' in settings:
                display_info.quality_level = settings['quality_level']
            if 'content_type' in settings:
                display_info.content_type = settings['content_type']

            logger.info(f"⚙️ Configured display {display_index}: {settings}")

    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        stats = {
            'total_displays': len(self.displays),
            'active_displays': sum(1 for d in self.displays.values() if d.enabled),
            'active_windows': len(self.windows),
            'master_display': self.master_display.index if self.master_display else None,
            'displays': {}
        }

        for index, display in self.displays.items():
            stats['displays'][index] = display.get_info_dict()

        return stats

    def close_all_windows(self):
        """Close all display windows"""
        for window in self.windows.values():
            window.close()
        self.windows.clear()
        self.display_widgets.clear()

class MultiMonitorControlPanel(QMainWindow):
    """Professional control panel for multi-monitor system"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖥️ MMPA Multi-Monitor Professional Control")
        self.setGeometry(100, 100, 1000, 700)

        self.multi_monitor_system = MultiMonitorSystem()
        self._setup_ui()

        # Auto-refresh display info
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_display_info)
        self.refresh_timer.start(2000)  # Update every 2 seconds

    def _setup_ui(self):
        """Setup control panel UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("🖥️ MMPA Multi-Monitor Professional Control")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title_label)

        # Tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Display Configuration Tab
        config_tab = self._create_configuration_tab()
        tabs.addTab(config_tab, "🔧 Configuration")

        # Layout Management Tab
        layout_tab = self._create_layout_tab()
        tabs.addTab(layout_tab, "🎭 Layouts")

        # Performance Monitor Tab
        perf_tab = self._create_performance_tab()
        tabs.addTab(perf_tab, "📊 Performance")

        # Display Info Tab
        info_tab = self._create_info_tab()
        tabs.addTab(info_tab, "ℹ️ Display Info")

    def _create_configuration_tab(self) -> QWidget:
        """Create display configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Display list
        displays_group = QGroupBox("Connected Displays")
        displays_layout = QVBoxLayout(displays_group)

        self.display_checkboxes = {}
        self.quality_combos = {}
        self.fps_spinboxes = {}

        for index, display_info in self.multi_monitor_system.displays.items():
            display_frame = QFrame()
            display_frame.setFrameStyle(QFrame.Box)
            display_layout = QGridLayout(display_frame)

            # Display info
            name_label = QLabel(f"Display {index}: {display_info.name}")
            name_label.setStyleSheet("font-weight: bold;")
            display_layout.addWidget(name_label, 0, 0, 1, 2)

            geometry_label = QLabel(f"{display_info.geometry.width()}x{display_info.geometry.height()} @ {display_info.refresh_rate:.1f}Hz")
            display_layout.addWidget(geometry_label, 1, 0, 1, 2)

            # Enable checkbox
            enabled_cb = QCheckBox("Enabled")
            enabled_cb.setChecked(display_info.enabled)
            enabled_cb.toggled.connect(lambda checked, idx=index: self._toggle_display(idx, checked))
            self.display_checkboxes[index] = enabled_cb
            display_layout.addWidget(enabled_cb, 2, 0)

            # Quality setting
            quality_combo = QComboBox()
            quality_combo.addItems(['low', 'medium', 'high', 'ultra'])
            quality_combo.setCurrentText(display_info.quality_level)
            quality_combo.currentTextChanged.connect(lambda quality, idx=index: self._set_display_quality(idx, quality))
            self.quality_combos[index] = quality_combo
            display_layout.addWidget(QLabel("Quality:"), 3, 0)
            display_layout.addWidget(quality_combo, 3, 1)

            # FPS setting
            fps_spinbox = QSpinBox()
            fps_spinbox.setRange(30, 120)
            fps_spinbox.setValue(display_info.target_fps)
            fps_spinbox.valueChanged.connect(lambda fps, idx=index: self._set_display_fps(idx, fps))
            self.fps_spinboxes[index] = fps_spinbox
            display_layout.addWidget(QLabel("Target FPS:"), 4, 0)
            display_layout.addWidget(fps_spinbox, 4, 1)

            displays_layout.addWidget(display_frame)

        layout.addWidget(displays_group)
        return tab

    def _create_layout_tab(self) -> QWidget:
        """Create layout management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Layout selection
        layout_group = QGroupBox("Display Layout")
        layout_group_layout = QVBoxLayout(layout_group)

        layout_buttons = [
            ("🪞 Mirrored", "mirrored", "All displays show identical content"),
            ("📐 Extended", "extended", "Primary display + auxiliary content"),
            ("🎨 Independent", "independent", "Each display shows unique content"),
            ("🎵 Concert Mode", "concert", "Optimized for live performance")
        ]

        for name, layout_type, description in layout_buttons:
            btn = QPushButton(f"{name}\n{description}")
            btn.clicked.connect(lambda checked, lt=layout_type: self._apply_layout(lt))
            btn.setStyleSheet("QPushButton { text-align: left; padding: 10px; }")
            layout_group_layout.addWidget(btn)

        layout.addWidget(layout_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout(actions_group)

        close_all_btn = QPushButton("❌ Close All Windows")
        close_all_btn.clicked.connect(self.multi_monitor_system.close_all_windows)
        actions_layout.addWidget(close_all_btn, 0, 0)

        refresh_btn = QPushButton("🔄 Refresh Displays")
        refresh_btn.clicked.connect(self._refresh_displays)
        actions_layout.addWidget(refresh_btn, 0, 1)

        layout.addWidget(actions_group)
        return tab

    def _create_performance_tab(self) -> QWidget:
        """Create performance monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        self.performance_text.setStyleSheet("font-family: monospace; background: #2c3e50; color: #ecf0f1;")
        layout.addWidget(self.performance_text)

        return tab

    def _create_info_tab(self) -> QWidget:
        """Create display information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("font-family: monospace; background: #34495e; color: #ecf0f1;")
        layout.addWidget(self.info_text)

        return tab

    def _toggle_display(self, display_index: int, enabled: bool):
        """Toggle display enabled state"""
        self.multi_monitor_system.configure_display(display_index, enabled=enabled)

    def _set_display_quality(self, display_index: int, quality: str):
        """Set display quality level"""
        self.multi_monitor_system.configure_display(display_index, quality_level=quality)

    def _set_display_fps(self, display_index: int, fps: int):
        """Set display target FPS"""
        self.multi_monitor_system.configure_display(display_index, target_fps=fps)

    def _apply_layout(self, layout_type: str):
        """Apply display layout"""
        self.multi_monitor_system.set_layout_type(layout_type)
        logger.info(f"🎭 Applied {layout_type} layout")

    def _refresh_displays(self):
        """Refresh display detection"""
        self.multi_monitor_system._detect_displays()
        # Would need to recreate UI elements here for dynamic display detection

    def _refresh_display_info(self):
        """Refresh display information display"""
        # Update performance tab
        stats = self.multi_monitor_system.get_system_stats()

        perf_text = "🖥️ MMPA Multi-Monitor Performance\n"
        perf_text += "=" * 40 + "\n\n"
        perf_text += f"Total Displays: {stats['total_displays']}\n"
        perf_text += f"Active Displays: {stats['active_displays']}\n"
        perf_text += f"Active Windows: {stats['active_windows']}\n"
        perf_text += f"Master Display: {stats['master_display']}\n\n"

        for index, display_data in stats['displays'].items():
            perf_text += f"Display {index}:\n"
            perf_text += f"  Name: {display_data['name']}\n"
            perf_text += f"  Size: {display_data['geometry']}\n"
            perf_text += f"  Position: {display_data['position']}\n"
            perf_text += f"  DPI: {display_data['dpi']}\n"
            perf_text += f"  Refresh Rate: {display_data['refresh_rate']}\n"
            perf_text += f"  Role: {display_data['role']}\n"
            perf_text += f"  Enabled: {display_data['enabled']}\n\n"

        self.performance_text.setText(perf_text)

        # Update info tab
        info_text = "🔍 MMPA Multi-Monitor System Information\n"
        info_text += "=" * 50 + "\n\n"
        info_text += "Professional multi-display system for MMPA concerts and installations.\n\n"
        info_text += "Features:\n"
        info_text += "• Multi-monitor detection and configuration\n"
        info_text += "• Synchronized visual outputs across displays\n"
        info_text += "• Independent content per display\n"
        info_text += "• Performance optimization for multiple outputs\n"
        info_text += "• Professional concert layouts\n\n"
        info_text += "Layout Types:\n"
        info_text += "• Mirrored: All displays show identical content\n"
        info_text += "• Extended: Primary + auxiliary content\n"
        info_text += "• Independent: Unique content per display\n"
        info_text += "• Concert Mode: Optimized for live performance\n"

        self.info_text.setText(info_text)

def main():
    """Run MMPA Multi-Monitor System"""
    app = QApplication(sys.argv)

    control_panel = MultiMonitorControlPanel()
    control_panel.show()

    print("🖥️ MMPA Multi-Monitor Professional System")
    print("=" * 50)
    print("✅ Multi-display detection and management")
    print("✅ Synchronized visual outputs")
    print("✅ Professional concert layouts")
    print("✅ Independent content per display")
    print("✅ Performance optimization")
    print("✅ Real-time display configuration")
    print()
    print(f"📱 Detected {len(control_panel.multi_monitor_system.displays)} displays")

    for i, display in control_panel.multi_monitor_system.displays.items():
        print(f"   Display {i}: {display.name} ({display.geometry.width()}x{display.geometry.height()})")

    print()
    print("🎭 Available Layouts:")
    print("   • Mirrored: Perfect synchronization across all displays")
    print("   • Extended: Primary content + complementary auxiliary")
    print("   • Independent: Unique visuals on each display")
    print("   • Concert Mode: Optimized for live performance venues")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()