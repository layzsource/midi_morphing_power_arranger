"""
UI Integration for Particle Effects System
Adds particle controls to existing configuration dialogs and main window.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QFormLayout, QCheckBox, QSlider, QSpinBox, 
                            QDoubleSpinBox, QComboBox, QPushButton, QLabel,
                            QTabWidget, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
import json
from typing import Dict, Any
from particle_system import ParticleSystem, ParticleType, ParticleBlendMode, ParticleSystemIntegration


class ParticleControlWidget(QWidget):
    """Widget for controlling particle system settings."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, particle_system: ParticleSystem, parent=None):
        super().__init__(parent)
        self.particle_system = particle_system
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the particle control UI."""
        layout = QVBoxLayout(self)
        
        # Main enable/disable
        main_group = QGroupBox("Particle Effects")
        main_layout = QFormLayout(main_group)
        
        self.enabled_check = QCheckBox("Enable Particle Effects")
        self.enabled_check.setChecked(True)
        self.enabled_check.toggled.connect(self.on_enabled_changed)
        main_layout.addRow(self.enabled_check)
        
        # Performance mode
        self.performance_mode_check = QCheckBox("Performance Mode")
        self.performance_mode_check.setToolTip("Reduces particle count and quality for better performance")
        self.performance_mode_check.toggled.connect(self.on_performance_mode_changed)
        main_layout.addRow(self.performance_mode_check)
        
        layout.addWidget(main_group)
        
        # Particle settings
        settings_group = QGroupBox("Particle Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Max particles
        self.max_particles_spin = QSpinBox()
        self.max_particles_spin.setRange(100, 2000)
        self.max_particles_spin.setValue(1000)
        self.max_particles_spin.setSuffix(" particles")
        self.max_particles_spin.valueChanged.connect(self.on_max_particles_changed)
        settings_layout.addRow("Max Particles:", self.max_particles_spin)
        
        # Particle size scale
        self.size_scale_slider = QSlider(Qt.Horizontal)
        self.size_scale_slider.setRange(10, 300)
        self.size_scale_slider.setValue(100)
        self.size_scale_slider.valueChanged.connect(self.on_size_scale_changed)
        self.size_scale_label = QLabel("100%")
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.size_scale_slider)
        size_layout.addWidget(self.size_scale_label)
        settings_layout.addRow("Particle Size:", size_layout)
        
        # Opacity scale
        self.opacity_scale_slider = QSlider(Qt.Horizontal)
        self.opacity_scale_slider.setRange(10, 100)
        self.opacity_scale_slider.setValue(100)
        self.opacity_scale_slider.valueChanged.connect(self.on_opacity_scale_changed)
        self.opacity_scale_label = QLabel("100%")
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_scale_slider)
        opacity_layout.addWidget(self.opacity_scale_label)
        settings_layout.addRow("Opacity:", opacity_layout)
        
        # Blend mode
        self.blend_mode_combo = QComboBox()
        self.blend_mode_combo.addItems([mode.value for mode in ParticleBlendMode])
        self.blend_mode_combo.setCurrentText(ParticleBlendMode.ADDITIVE.value)
        self.blend_mode_combo.currentTextChanged.connect(self.on_blend_mode_changed)
        settings_layout.addRow("Blend Mode:", self.blend_mode_combo)
        
        layout.addWidget(settings_group)
        
        # Physics settings
        physics_group = QGroupBox("Physics Settings")
        physics_layout = QFormLayout(physics_group)
        
        # Gravity
        self.gravity_x_spin = QDoubleSpinBox()
        self.gravity_x_spin.setRange(-20.0, 20.0)
        self.gravity_x_spin.setSingleStep(0.1)
        self.gravity_x_spin.setValue(0.0)
        self.gravity_x_spin.valueChanged.connect(self.on_gravity_changed)
        physics_layout.addRow("Gravity X:", self.gravity_x_spin)
        
        self.gravity_y_spin = QDoubleSpinBox()
        self.gravity_y_spin.setRange(-20.0, 20.0)
        self.gravity_y_spin.setSingleStep(0.1)
        self.gravity_y_spin.setValue(-9.81)
        self.gravity_y_spin.valueChanged.connect(self.on_gravity_changed)
        physics_layout.addRow("Gravity Y:", self.gravity_y_spin)
        
        self.gravity_z_spin = QDoubleSpinBox()
        self.gravity_z_spin.setRange(-20.0, 20.0)
        self.gravity_z_spin.setSingleStep(0.1)
        self.gravity_z_spin.setValue(0.0)
        self.gravity_z_spin.valueChanged.connect(self.on_gravity_changed)
        physics_layout.addRow("Gravity Z:", self.gravity_z_spin)
        
        layout.addWidget(physics_group)
        
        # Effect triggers
        effects_group = QGroupBox("Effect Triggers")
        effects_layout = QVBoxLayout(effects_group)
        
        # Test buttons
        test_layout = QHBoxLayout()
        
        self.test_explosion_btn = QPushButton("Test Explosion")
        self.test_explosion_btn.clicked.connect(self.test_explosion)
        test_layout.addWidget(self.test_explosion_btn)
        
        self.test_shockwave_btn = QPushButton("Test Shockwave")
        self.test_shockwave_btn.clicked.connect(self.test_shockwave)
        test_layout.addWidget(self.test_shockwave_btn)
        
        self.test_bloom_btn = QPushButton("Test Bloom")
        self.test_bloom_btn.clicked.connect(self.test_bloom)
        test_layout.addWidget(self.test_bloom_btn)
        
        effects_layout.addLayout(test_layout)
        
        # Clear button
        self.clear_particles_btn = QPushButton("Clear All Particles")
        self.clear_particles_btn.clicked.connect(self.clear_particles)
        effects_layout.addWidget(self.clear_particles_btn)
        
        layout.addWidget(effects_group)
        
        layout.addStretch()
    
    def on_enabled_changed(self, enabled):
        """Handle particle system enable/disable."""
        self.particle_system.render_particles = enabled
        if not enabled:
            self.particle_system.clear_all_particles()
        self.emit_settings_changed()
    
    def on_performance_mode_changed(self, enabled):
        """Handle performance mode toggle."""
        self.particle_system.set_performance_mode(enabled)
        if enabled:
            self.max_particles_spin.setValue(500)
        else:
            self.max_particles_spin.setValue(1000)
        self.emit_settings_changed()
    
    def on_max_particles_changed(self, value):
        """Handle max particles change."""
        self.particle_system.max_particles = value
        self.emit_settings_changed()
    
    def on_size_scale_changed(self, value):
        """Handle particle size scale change."""
        scale = value / 100.0
        self.particle_system.particle_size_scale = scale
        self.size_scale_label.setText(f"{value}%")
        self.emit_settings_changed()
    
    def on_opacity_scale_changed(self, value):
        """Handle opacity scale change."""
        scale = value / 100.0
        self.particle_system.opacity_scale = scale
        self.opacity_scale_label.setText(f"{value}%")
        self.emit_settings_changed()
    
    def on_blend_mode_changed(self, mode_text):
        """Handle blend mode change."""
        for mode in ParticleBlendMode:
            if mode.value == mode_text:
                self.particle_system.blend_mode = mode
                break
        self.emit_settings_changed()
    
    def on_gravity_changed(self):
        """Handle gravity settings change."""
        gravity = [
            self.gravity_x_spin.value(),
            self.gravity_y_spin.value(),
            self.gravity_z_spin.value()
        ]
        self.particle_system.gravity = gravity
        self.emit_settings_changed()
    
    def test_explosion(self):
        """Test explosion effect."""
        import numpy as np
        position = np.array([0, 0, 0])
        self.particle_system.emit_special_effect("explosion", position, 1.0)
    
    def test_shockwave(self):
        """Test shockwave effect."""
        import numpy as np
        position = np.array([0, 0, 0])
        self.particle_system.emit_special_effect("shockwave", position, 0.8)
    
    def test_bloom(self):
        """Test bloom effect."""
        import numpy as np
        position = np.array([0, 0, 0])
        self.particle_system.emit_special_effect("bloom", position, 0.6)
    
    def clear_particles(self):
        """Clear all particles."""
        self.particle_system.clear_all_particles()
    
    def emit_settings_changed(self):
        """Emit settings changed signal."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current particle settings."""
        return {
            'enabled': self.enabled_check.isChecked(),
            'performance_mode': self.performance_mode_check.isChecked(),
            'max_particles': self.max_particles_spin.value(),
            'size_scale': self.size_scale_slider.value() / 100.0,
            'opacity_scale': self.opacity_scale_slider.value() / 100.0,
            'blend_mode': self.blend_mode_combo.currentText(),
            'gravity': [
                self.gravity_x_spin.value(),
                self.gravity_y_spin.value(),
                self.gravity_z_spin.value()
            ]
        }
    
    def load_settings(self, settings: Dict[str, Any] = None):
        """Load particle settings."""
        if settings is None:
            settings = self.get_default_settings()
        
        self.enabled_check.setChecked(settings.get('enabled', True))
        self.performance_mode_check.setChecked(settings.get('performance_mode', False))
        self.max_particles_spin.setValue(settings.get('max_particles', 1000))
        
        size_scale = int(settings.get('size_scale', 1.0) * 100)
        self.size_scale_slider.setValue(size_scale)
        self.size_scale_label.setText(f"{size_scale}%")
        
        opacity_scale = int(settings.get('opacity_scale', 1.0) * 100)
        self.opacity_scale_slider.setValue(opacity_scale)
        self.opacity_scale_label.setText(f"{opacity_scale}%")
        
        self.blend_mode_combo.setCurrentText(settings.get('blend_mode', 'additive'))
        
        gravity = settings.get('gravity', [0.0, -9.81, 0.0])
        self.gravity_x_spin.setValue(gravity[0])
        self.gravity_y_spin.setValue(gravity[1])
        self.gravity_z_spin.setValue(gravity[2])
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default particle settings."""
        return {
            'enabled': True,
            'performance_mode': False,
            'max_particles': 1000,
            'size_scale': 1.0,
            'opacity_scale': 1.0,
            'blend_mode': 'additive',
            'gravity': [0.0, -9.81, 0.0]
        }


class ParticlePerformanceWidget(QWidget):
    """Widget for monitoring particle system performance."""
    
    def __init__(self, particle_system: ParticleSystem, parent=None):
        super().__init__(parent)
        self.particle_system = particle_system
        self.setup_ui()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup the performance monitoring UI."""
        layout = QVBoxLayout(self)
        
        # Performance stats
        stats_group = QGroupBox("Particle Performance")
        stats_layout = QFormLayout(stats_group)
        
        self.active_particles_label = QLabel("0")
        stats_layout.addRow("Active Particles:", self.active_particles_label)
        
        self.active_emitters_label = QLabel("0")
        stats_layout.addRow("Active Emitters:", self.active_emitters_label)
        
        self.update_time_label = QLabel("0.0 ms")
        stats_layout.addRow("Update Time:", self.update_time_label)
        
        self.avg_particles_label = QLabel("0")
        stats_layout.addRow("Avg Particle Count:", self.avg_particles_label)
        
        self.performance_mode_label = QLabel("Disabled")
        stats_layout.addRow("Performance Mode:", self.performance_mode_label)
        
        layout.addWidget(stats_group)
        
        # Performance bars
        bars_group = QGroupBox("Performance Indicators")
        bars_layout = QFormLayout(bars_group)
        
        # Particle count bar
        self.particle_count_bar = QProgressBar()
        self.particle_count_bar.setRange(0, 1000)
        bars_layout.addRow("Particle Load:", self.particle_count_bar)
        
        # Update time bar
        self.update_time_bar = QProgressBar()
        self.update_time_bar.setRange(0, 100)  # 0-100ms
        bars_layout.addRow("Update Time:", self.update_time_bar)
        
        layout.addWidget(bars_group)
        
        # Controls
        controls_group = QGroupBox("Performance Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.auto_optimize_check = QCheckBox("Auto-optimize for performance")
        self.auto_optimize_check.setToolTip("Automatically enable performance mode when particle count is high")
        controls_layout.addWidget(self.auto_optimize_check)
        
        self.clear_stats_btn = QPushButton("Clear Statistics")
        self.clear_stats_btn.clicked.connect(self.clear_stats)
        controls_layout.addWidget(self.clear_stats_btn)
        
        layout.addWidget(controls_group)
        
        layout.addStretch()
    
    def update_stats(self):
        """Update performance statistics display."""
        stats = self.particle_system.get_performance_stats()
        
        if not stats:
            return
        
        # Update labels
        self.active_particles_label.setText(str(stats.get('active_particles', 0)))
        self.active_emitters_label.setText(str(stats.get('active_emitters', 0)))
        
        update_time = stats.get('avg_update_time_ms', 0)
        self.update_time_label.setText(f"{update_time:.1f} ms")
        
        avg_particles = stats.get('avg_particle_count', 0)
        self.avg_particles_label.setText(f"{avg_particles:.0f}")
        
        performance_mode = "Enabled" if stats.get('performance_mode', False) else "Disabled"
        self.performance_mode_label.setText(performance_mode)
        
        # Update progress bars
        particle_count = stats.get('active_particles', 0)
        max_particles = self.particle_system.max_particles
        self.particle_count_bar.setMaximum(max_particles)
        self.particle_count_bar.setValue(particle_count)
        
        # Color code particle count bar
        if particle_count > max_particles * 0.8:
            self.particle_count_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif particle_count > max_particles * 0.6:
            self.particle_count_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.particle_count_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        # Update time bar
        self.update_time_bar.setValue(min(int(update_time), 100))
        
        # Auto-optimization
        if self.auto_optimize_check.isChecked():
            if particle_count > max_particles * 0.8 and not stats.get('performance_mode', False):
                self.particle_system.set_performance_mode(True)
            elif particle_count < max_particles * 0.4 and stats.get('performance_mode', False):
                self.particle_system.set_performance_mode(False)
    
    def clear_stats(self):
        """Clear performance statistics."""
        self.particle_system.update_times.clear()
        self.particle_system.particle_count_history.clear()


def add_particle_tab_to_scene_config(scene_config_dialog, particle_integration):
    """
    Add particle controls to the existing scene configuration dialog.
    Call this function after creating your scene configuration dialog.
    """
    if not hasattr(scene_config_dialog, 'tab_widget'):
        print("Scene config dialog doesn't have tab_widget - cannot add particle tab")
        return
    
    # Create particle control widget
    particle_widget = ParticleControlWidget(particle_integration.particle_system)
    
    # Add to tab widget
    scene_config_dialog.tab_widget.addTab(particle_widget, "Particle Effects")
    
    # Connect settings changed signal
    def on_particle_settings_changed(settings):
        # Save settings with scene configuration
        if hasattr(scene_config_dialog, 'save_particle_settings'):
            scene_config_dialog.save_particle_settings(settings)
    
    particle_widget.settings_changed.connect(on_particle_settings_changed)
    
    print("Particle tab added to scene configuration dialog")


def add_particle_performance_to_dialog(performance_dialog, particle_integration):
    """
    Add particle performance monitoring to existing performance dialog.
    """
    if not hasattr(performance_dialog, 'tab_widget'):
        print("Performance dialog doesn't have tab_widget - cannot add particle performance")
        return
    
    # Create particle performance widget
    particle_perf_widget = ParticlePerformanceWidget(particle_integration.particle_system)
    
    # Add to tab widget
    performance_dialog.tab_widget.addTab(particle_perf_widget, "Particle Performance")
    
    print("Particle performance monitoring added to performance dialog")


def integrate_particle_ui_with_main_window(main_window, particle_integration):
    """
    Integrate particle controls with the main application window.
    Adds particle toggle button and status information.
    """
    try:
        # Add particle toggle button to main controls
        if hasattr(main_window, 'layout') and main_window.layout:
            particle_toggle = QCheckBox("Particle Effects")
            particle_toggle.setChecked(True)
            particle_toggle.toggled.connect(particle_integration.set_enabled)
            main_window.layout.addWidget(particle_toggle)
            
            # Store reference
            main_window.particle_toggle = particle_toggle
        
        # Add particle status to status bar
        if hasattr(main_window, 'status_bar'):
            particle_status_label = QLabel("Particles: Active")
            main_window.status_bar.addPermanentWidget(particle_status_label)
            main_window.particle_status_label = particle_status_label
            
            # Update particle status periodically
            def update_particle_status():
                stats = particle_integration.particle_system.get_performance_stats()
                if stats:
                    count = stats.get('active_particles', 0)
                    particle_status_label.setText(f"Particles: {count}")
                else:
                    particle_status_label.setText("Particles: Inactive")
            
            # Connect to existing update timer if available
            if hasattr(main_window, 'update_timer'):
                main_window.update_timer.timeout.connect(update_particle_status)
        
        print("Particle UI integration complete")
        
    except Exception as e:
        print(f"Error integrating particle UI: {e}")


# Configuration persistence
def save_particle_config(particle_control_widget: ParticleControlWidget, filename: str):
    """Save particle configuration to file."""
    try:
        settings = particle_control_widget.get_settings()
        with open(filename, 'w') as f:
            json.dump(settings, f, indent=2)
        print(f"Particle configuration saved to {filename}")
    except Exception as e:
        print(f"Error saving particle configuration: {e}")


def load_particle_config(particle_control_widget: ParticleControlWidget, filename: str):
    """Load particle configuration from file."""
    try:
        with open(filename, 'r') as f:
            settings = json.load(f)
        particle_control_widget.load_settings(settings)
        print(f"Particle configuration loaded from {filename}")
    except Exception as e:
        print(f"Error loading particle configuration: {e}")
        # Load defaults on error
        particle_control_widget.load_settings()


# Example integration with existing application
if __name__ == "__main__":
    """
    Example of how to integrate particle UI components.
    This would typically be called from your main application.
    """
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
    import sys
    
    app = QApplication(sys.argv)
    
    # Mock main window for testing
    main_window = QMainWindow()
    main_window.setWindowTitle("Particle System UI Test")
    main_window.resize(800, 600)
    
    # Create tab widget for testing
    tab_widget = QTabWidget()
    main_window.setCentralWidget(tab_widget)
    
    # Mock particle system
    from particle_system import ParticleSystem
    particle_system = ParticleSystem()
    
    # Create control widget
    particle_control = ParticleControlWidget(particle_system)
    tab_widget.addTab(particle_control, "Particle Controls")
    
    # Create performance widget
    particle_perf = ParticlePerformanceWidget(particle_system)
    tab_widget.addTab(particle_perf, "Performance")
    
    main_window.show()
    
    print("Particle UI test application started")
    sys.exit(app.exec_())
