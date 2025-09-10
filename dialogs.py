"""
UI dialogs for configuration and performance monitoring.
"""

import json
import time
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QGroupBox, QDialogButtonBox, QPushButton, QFileDialog, QMessageBox,
    QTextEdit, QProgressBar, QWidget
)
from PySide6.QtCore import QTimer, Signal

from config import Config
from profiler import PerformanceProfiler

logger = logging.getLogger(__name__)

class ConfigDialog(QDialog):
    """Configuration settings dialog."""
    
    config_changed = Signal(Config)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config.to_dict() if hasattr(config, 'to_dict') else config.__dict__.copy()
        self.original_config = config
        self.setWindowTitle("Configuration Settings")
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
        self._load_current_config()
    
    def _setup_ui(self):
        """Setup the configuration dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_midi_osc_tab()
        self._create_visualization_tab()
        self._create_lighting_tab()
        self._create_performance_tab()
        self._create_audio_tab()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._restore_defaults)
        layout.addWidget(button_box)
    
    def _create_midi_osc_tab(self):
        """Create MIDI/OSC configuration tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # MIDI Settings
        midi_group = QGroupBox("MIDI Settings")
        midi_layout = QGridLayout(midi_group)
        
        midi_layout.addWidget(QLabel("MIDI Port:"), 0, 0)
        self.midi_port_edit = QLineEdit()
        midi_layout.addWidget(self.midi_port_edit, 0, 1)
        
        layout.addWidget(midi_group, 0, 0, 1, 2)
        
        # OSC Settings
        osc_group = QGroupBox("OSC Settings")
        osc_layout = QGridLayout(osc_group)
        
        osc_layout.addWidget(QLabel("OSC IP:"), 0, 0)
        self.osc_ip_edit = QLineEdit()
        osc_layout.addWidget(self.osc_ip_edit, 0, 1)
        
        osc_layout.addWidget(QLabel("OSC Port:"), 1, 0)
        self.osc_port_spin = QSpinBox()
        self.osc_port_spin.setRange(1024, 65535)
        osc_layout.addWidget(self.osc_port_spin, 1, 1)
        
        layout.addWidget(osc_group, 1, 0, 1, 2)
        
        self.tab_widget.addTab(tab, "MIDI/OSC")
    
    def _create_visualization_tab(self):
        """Create visualization configuration tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Mesh Settings
        mesh_group = QGroupBox("Mesh Settings")
        mesh_layout = QGridLayout(mesh_group)
        
        mesh_layout.addWidget(QLabel("Resolution:"), 0, 0)
        self.mesh_resolution_spin = QSpinBox()
        self.mesh_resolution_spin.setRange(10, 200)
        self.mesh_resolution_spin.setSuffix(" vertices")
        mesh_layout.addWidget(self.mesh_resolution_spin, 0, 1)
        
        mesh_layout.addWidget(QLabel("Mesh Color:"), 1, 0)
        self.mesh_color_edit = QLineEdit()
        mesh_layout.addWidget(self.mesh_color_edit, 1, 1)
        
        mesh_layout.addWidget(QLabel("Metallic:"), 2, 0)
        self.metallic_spin = QDoubleSpinBox()
        self.metallic_spin.setRange(0.0, 1.0)
        self.metallic_spin.setSingleStep(0.1)
        mesh_layout.addWidget(self.metallic_spin, 2, 1)
        
        mesh_layout.addWidget(QLabel("Roughness:"), 3, 0)
        self.roughness_spin = QDoubleSpinBox()
        self.roughness_spin.setRange(0.0, 1.0)
        self.roughness_spin.setSingleStep(0.1)
        mesh_layout.addWidget(self.roughness_spin, 3, 1)
        
        layout.addWidget(mesh_group, 0, 0, 1, 2)
        
        # Color Settings
        color_group = QGroupBox("Light Color Settings")
        color_layout = QGridLayout(color_group)
        
        color_layout.addWidget(QLabel("Use HSV Colors:"), 0, 0)
        self.use_hsv_check = QCheckBox()
        color_layout.addWidget(self.use_hsv_check, 0, 1)
        
        color_layout.addWidget(QLabel("Base Hue:"), 1, 0)
        self.base_hue_spin = QDoubleSpinBox()
        self.base_hue_spin.setRange(0.0, 1.0)
        self.base_hue_spin.setSingleStep(0.01)
        color_layout.addWidget(self.base_hue_spin, 1, 1)
        
        color_layout.addWidget(QLabel("Saturation:"), 2, 0)
        self.saturation_spin = QDoubleSpinBox()
        self.saturation_spin.setRange(0.0, 1.0)
        self.saturation_spin.setSingleStep(0.01)
        color_layout.addWidget(self.saturation_spin, 2, 1)
        
        color_layout.addWidget(QLabel("Value/Brightness:"), 3, 0)
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0.0, 1.0)
        self.value_spin.setSingleStep(0.01)
        color_layout.addWidget(self.value_spin, 3, 1)
        
        layout.addWidget(color_group, 1, 0, 1, 2)
        
        self.tab_widget.addTab(tab, "Visualization")
    
    def _create_lighting_tab(self):
        """Create lighting configuration tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Light Management
        light_group = QGroupBox("Light Management")
        light_layout = QGridLayout(light_group)
        
        light_layout.addWidget(QLabel("Max Active Lights:"), 0, 0)
        self.max_lights_spin = QSpinBox()
        self.max_lights_spin.setRange(1, 32)
        light_layout.addWidget(self.max_lights_spin, 0, 1)
        
        light_layout.addWidget(QLabel("Light Intensity Scale:"), 1, 0)
        self.intensity_scale_spin = QDoubleSpinBox()
        self.intensity_scale_spin.setRange(0.1, 50.0)
        self.intensity_scale_spin.setSingleStep(0.5)
        light_layout.addWidget(self.intensity_scale_spin, 1, 1)
        
        light_layout.addWidget(QLabel("Light Expire Time:"), 2, 0)
        self.expire_time_spin = QDoubleSpinBox()
        self.expire_time_spin.setRange(5.0, 300.0)
        self.expire_time_spin.setSuffix(" seconds")
        light_layout.addWidget(self.expire_time_spin, 2, 1)
        
        light_layout.addWidget(QLabel("Removal Strategy:"), 3, 0)
        self.removal_strategy_combo = QComboBox()
        self.removal_strategy_combo.addItems([
            "oldest", "random", "lowest_intensity", "highest_note"
        ])
        light_layout.addWidget(self.removal_strategy_combo, 3, 1)
        
        layout.addWidget(light_group, 0, 0, 1, 2)
        
        self.tab_widget.addTab(tab, "Lighting")
    
    def _create_performance_tab(self):
        """Create performance configuration tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Performance Settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QGridLayout(perf_group)
        
        perf_layout.addWidget(QLabel("Render Debounce:"), 0, 0)
        self.render_debounce_spin = QSpinBox()
        self.render_debounce_spin.setRange(1, 100)
        self.render_debounce_spin.setSuffix(" ms")
        perf_layout.addWidget(self.render_debounce_spin, 0, 1)
        
        perf_layout.addWidget(QLabel("Cleanup Interval:"), 1, 0)
        self.cleanup_interval_spin = QSpinBox()
        self.cleanup_interval_spin.setRange(1000, 30000)
        self.cleanup_interval_spin.setSuffix(" ms")
        perf_layout.addWidget(self.cleanup_interval_spin, 1, 1)
        
        perf_layout.addWidget(QLabel("UI Update Interval:"), 2, 0)
        self.ui_update_interval_spin = QSpinBox()
        self.ui_update_interval_spin.setRange(100, 5000)
        self.ui_update_interval_spin.setSuffix(" ms")
        perf_layout.addWidget(self.ui_update_interval_spin, 2, 1)
        
        perf_layout.addWidget(QLabel("Enable Profiling:"), 3, 0)
        self.profiling_enabled_check = QCheckBox()
        perf_layout.addWidget(self.profiling_enabled_check, 3, 1)
        
        perf_layout.addWidget(QLabel("Profiling Update Interval:"), 4, 0)
        self.profiling_interval_spin = QSpinBox()
        self.profiling_interval_spin.setRange(500, 10000)
        self.profiling_interval_spin.setSuffix(" ms")
        perf_layout.addWidget(self.profiling_interval_spin, 4, 1)
        
        layout.addWidget(perf_group, 0, 0, 1, 2)
        
        # Export/Import Settings
        io_group = QGroupBox("Settings Import/Export")
        io_layout = QHBoxLayout(io_group)
        
        export_btn = QPushButton("Export Settings...")
        export_btn.clicked.connect(self._export_settings)
        io_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Settings...")
        import_btn.clicked.connect(self._import_settings)
        io_layout.addWidget(import_btn)
        
        layout.addWidget(io_group, 1, 0, 1, 2)
        
        self.tab_widget.addTab(tab, "Performance")
    
    def _create_audio_tab(self):
        """Create audio configuration tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Audio Input Settings
        audio_group = QGroupBox("Audio Input Settings")
        audio_layout = QGridLayout(audio_group)
        
        audio_layout.addWidget(QLabel("Enable Audio:"), 0, 0)
        self.audio_enabled_check = QCheckBox()
        audio_layout.addWidget(self.audio_enabled_check, 0, 1)
        
        audio_layout.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["22050", "44100", "48000", "96000"])
        audio_layout.addWidget(self.sample_rate_combo, 1, 1)
        
        audio_layout.addWidget(QLabel("Chunk Size:"), 2, 0)
        self.chunk_size_combo = QComboBox()
        self.chunk_size_combo.addItems(["512", "1024", "2048", "4096"])
        audio_layout.addWidget(self.chunk_size_combo, 2, 1)
        
        layout.addWidget(audio_group, 0, 0, 1, 2)
        
        # Audio Analysis Settings
        analysis_group = QGroupBox("Audio Analysis")
        analysis_layout = QGridLayout(analysis_group)
        
        analysis_layout.addWidget(QLabel("Onset Threshold:"), 0, 0)
        self.onset_threshold_spin = QDoubleSpinBox()
        self.onset_threshold_spin.setRange(0.1, 2.0)
        self.onset_threshold_spin.setSingleStep(0.1)
        analysis_layout.addWidget(self.onset_threshold_spin, 0, 1)
        
        analysis_layout.addWidget(QLabel("Morph Sensitivity:"), 1, 0)
        self.morph_sensitivity_spin = QDoubleSpinBox()
        self.morph_sensitivity_spin.setRange(0.0, 2.0)
        self.morph_sensitivity_spin.setSingleStep(0.1)
        analysis_layout.addWidget(self.morph_sensitivity_spin, 1, 1)
        
        analysis_layout.addWidget(QLabel("Light Sensitivity:"), 2, 0)
        self.light_sensitivity_spin = QDoubleSpinBox()
        self.light_sensitivity_spin.setRange(0.0, 2.0)
        self.light_sensitivity_spin.setSingleStep(0.1)
        analysis_layout.addWidget(self.light_sensitivity_spin, 2, 1)
        
        analysis_layout.addWidget(QLabel("Pitch to Hue:"), 3, 0)
        self.pitch_to_hue_check = QCheckBox()
        analysis_layout.addWidget(self.pitch_to_hue_check, 3, 1)
        
        analysis_layout.addWidget(QLabel("Amplitude to Intensity:"), 4, 0)
        self.amplitude_to_intensity_check = QCheckBox()
        analysis_layout.addWidget(self.amplitude_to_intensity_check, 4, 1)
        
        layout.addWidget(analysis_group, 1, 0, 1, 2)
        
        self.tab_widget.addTab(tab, "Audio")
    
    def _load_current_config(self):
        """Load current configuration into UI controls."""
        self.midi_port_edit.setText(self.config.get('MIDI_PORT', ''))
        self.osc_ip_edit.setText(self.config.get('OSC_IP', ''))
        self.osc_port_spin.setValue(self.config.get('OSC_PORT', 5005))
        
        self.mesh_resolution_spin.setValue(self.config.get('MESH_RESOLUTION', 60))
        self.mesh_color_edit.setText(self.config.get('MESH_COLOR', 'lightblue'))
        self.metallic_spin.setValue(self.config.get('METALLIC', 0.7))
        self.roughness_spin.setValue(self.config.get('ROUGHNESS', 0.3))
        
        self.use_hsv_check.setChecked(self.config.get('USE_HSV_COLORS', True))
        self.base_hue_spin.setValue(self.config.get('BASE_HUE', 0.0))
        self.saturation_spin.setValue(self.config.get('SATURATION', 1.0))
        self.value_spin.setValue(self.config.get('VALUE', 1.0))
        
        self.max_lights_spin.setValue(self.config.get('MAX_LIGHTS', 8))
        self.intensity_scale_spin.setValue(self.config.get('LIGHT_INTENSITY_SCALE', 10.0))
        self.expire_time_spin.setValue(self.config.get('LIGHT_EXPIRE_TIME', 30.0))
        self.removal_strategy_combo.setCurrentText(self.config.get('LIGHT_REMOVAL_STRATEGY', 'oldest'))
        
        self.render_debounce_spin.setValue(self.config.get('RENDER_DEBOUNCE_MS', 16))
        self.cleanup_interval_spin.setValue(self.config.get('CLEANUP_INTERVAL_MS', 5000))
        self.ui_update_interval_spin.setValue(self.config.get('UI_UPDATE_INTERVAL_MS', 1000))
        self.profiling_enabled_check.setChecked(self.config.get('PROFILING_ENABLED', True))
        self.profiling_interval_spin.setValue(self.config.get('PROFILING_INTERVAL_MS', 2000))
        
        # Audio settings
        self.audio_enabled_check.setChecked(self.config.get('AUDIO_ENABLED', True))
        self.sample_rate_combo.setCurrentText(str(self.config.get('AUDIO_SAMPLE_RATE', 44100)))
        self.chunk_size_combo.setCurrentText(str(self.config.get('AUDIO_CHUNK_SIZE', 1024)))
        self.onset_threshold_spin.setValue(self.config.get('AUDIO_ONSET_THRESHOLD', 0.3))
        self.morph_sensitivity_spin.setValue(self.config.get('AUDIO_MORPH_SENSITIVITY', 0.5))
        self.light_sensitivity_spin.setValue(self.config.get('AUDIO_LIGHT_SENSITIVITY', 1.0))
        self.pitch_to_hue_check.setChecked(self.config.get('AUDIO_PITCH_TO_HUE', True))
        self.amplitude_to_intensity_check.setChecked(self.config.get('AUDIO_AMPLITUDE_TO_INTENSITY', True))
    
    def _save_current_config(self):
        """Save UI values to config dictionary."""
        self.config['MIDI_PORT'] = self.midi_port_edit.text()
        self.config['OSC_IP'] = self.osc_ip_edit.text()
        self.config['OSC_PORT'] = self.osc_port_spin.value()
        
        self.config['MESH_RESOLUTION'] = self.mesh_resolution_spin.value()
        self.config['MESH_COLOR'] = self.mesh_color_edit.text()
        self.config['METALLIC'] = self.metallic_spin.value()
        self.config['ROUGHNESS'] = self.roughness_spin.value()
        
        self.config['USE_HSV_COLORS'] = self.use_hsv_check.isChecked()
        self.config['BASE_HUE'] = self.base_hue_spin.value()
        self.config['SATURATION'] = self.saturation_spin.value()
        self.config['VALUE'] = self.value_spin.value()
        
        self.config['MAX_LIGHTS'] = self.max_lights_spin.value()
        self.config['LIGHT_INTENSITY_SCALE'] = self.intensity_scale_spin.value()
        self.config['LIGHT_EXPIRE_TIME'] = self.expire_time_spin.value()
        self.config['LIGHT_REMOVAL_STRATEGY'] = self.removal_strategy_combo.currentText()
        
        self.config['RENDER_DEBOUNCE_MS'] = self.render_debounce_spin.value()
        self.config['CLEANUP_INTERVAL_MS'] = self.cleanup_interval_spin.value()
        self.config['UI_UPDATE_INTERVAL_MS'] = self.ui_update_interval_spin.value()
        self.config['PROFILING_ENABLED'] = self.profiling_enabled_check.isChecked()
        self.config['PROFILING_INTERVAL_MS'] = self.profiling_interval_spin.value()
        
        # Audio settings
        self.config['AUDIO_ENABLED'] = self.audio_enabled_check.isChecked()
        self.config['AUDIO_SAMPLE_RATE'] = int(self.sample_rate_combo.currentText())
        self.config['AUDIO_CHUNK_SIZE'] = int(self.chunk_size_combo.currentText())
        self.config['AUDIO_ONSET_THRESHOLD'] = self.onset_threshold_spin.value()
        self.config['AUDIO_MORPH_SENSITIVITY'] = self.morph_sensitivity_spin.value()
        self.config['AUDIO_LIGHT_SENSITIVITY'] = self.light_sensitivity_spin.value()
        self.config['AUDIO_PITCH_TO_HUE'] = self.pitch_to_hue_check.isChecked()
        self.config['AUDIO_AMPLITUDE_TO_INTENSITY'] = self.amplitude_to_intensity_check.isChecked()
    
    def _restore_defaults(self):
        """Restore default configuration values."""
        default_config = Config()
        self.config = default_config.to_dict()
        self._load_current_config()
    
    def _export_settings(self):
        """Export settings to JSON file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Settings", "morphing_config.json", "JSON Files (*.json)"
            )
            if filename:
                self._save_current_config()
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=2)
                QMessageBox.information(self, "Success", "Settings exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from JSON file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Import Settings", "", "JSON Files (*.json)"
            )
            if filename:
                with open(filename, 'r') as f:
                    imported_config = json.load(f)
                self.config.update(imported_config)
                self._load_current_config()
                QMessageBox.information(self, "Success", "Settings imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import settings: {e}")
    
    def accept(self):
        """Accept dialog and emit config changes."""
        self._save_current_config()
        # Create new Config object from dictionary
        new_config = Config()
        new_config.from_dict(self.config)
        self.config_changed.emit(new_config)
        super().accept()
    
    def get_config(self) -> Config:
        """Get the current configuration."""
        self._save_current_config()
        config = Config()
        config.from_dict(self.config)
        return config


class PerformanceDialog(QDialog):
    """Real-time performance monitoring dialog."""
    
    def __init__(self, profiler: PerformanceProfiler, parent=None):
        super().__init__(parent)
        self.profiler = profiler
        self.setWindowTitle("Performance Monitor")
        self.setModal(False)
        self.resize(800, 600)
        
        self._setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Setup the performance dialog UI."""
        layout = QVBoxLayout(self)
        
        # Performance metrics display
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setFont(self.font())
        layout.addWidget(QLabel("Real-time Performance Metrics:"))
        layout.addWidget(self.metrics_text)
        
        # Performance bars
        metrics_layout = QGridLayout()
        
        # FPS bar
        metrics_layout.addWidget(QLabel("FPS:"), 0, 0)
        self.fps_bar = QProgressBar()
        self.fps_bar.setRange(0, 60)
        self.fps_label = QLabel("0.0")
        metrics_layout.addWidget(self.fps_bar, 0, 1)
        metrics_layout.addWidget(self.fps_label, 0, 2)
        
        # Memory bar
        metrics_layout.addWidget(QLabel("Memory:"), 1, 0)
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 1000)  # 1GB max
        self.memory_label = QLabel("0 MB")
        metrics_layout.addWidget(self.memory_bar, 1, 1)
        metrics_layout.addWidget(self.memory_label, 1, 2)
        
        # CPU bar
        metrics_layout.addWidget(QLabel("CPU:"), 2, 0)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_label = QLabel("0%")
        metrics_layout.addWidget(self.cpu_bar, 2, 1)
        metrics_layout.addWidget(self.cpu_label, 2, 2)
        
        layout.addLayout(metrics_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Report...")
        self.export_button.clicked.connect(self._export_report)
        button_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("Clear Metrics")
        self.clear_button.clicked.connect(self._clear_metrics)
        button_layout.addWidget(self.clear_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _update_display(self):
        """Update the performance display."""
        try:
            # Update system metrics
            self.profiler.record_system_metrics()
            
            # Generate real-time report
            report = self._generate_realtime_report()
            self.metrics_text.setPlainText(report)
            
            # Update progress bars
            fps = self.profiler.get_fps()
            self.fps_bar.setValue(min(int(fps), 60))
            self.fps_label.setText(f"{fps:.1f}")
            
            memory_stats = self.profiler.get_stats('memory_mb')
            if memory_stats:
                memory_mb = memory_stats['latest']
                self.memory_bar.setValue(min(int(memory_mb), 1000))
                self.memory_label.setText(f"{memory_mb:.0f} MB")
            
            cpu_stats = self.profiler.get_stats('cpu_percent')
            if cpu_stats:
                cpu_percent = cpu_stats['latest']
                self.cpu_bar.setValue(min(int(cpu_percent), 100))
                self.cpu_label.setText(f"{cpu_percent:.1f}%")
                
                # Color coding for performance bars
                if fps < 30:
                    self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                elif fps < 45:
                    self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
                else:
                    self.fps_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
                    
        except Exception as e:
            logger.error(f"Failed to update performance display: {e}")
    
    def _generate_realtime_report(self) -> str:
        """Generate a condensed real-time performance report."""
        try:
            lines = []
            
            # Key metrics summary
            key_metrics = ['render_time', 'light_update_time', 'mesh_update_time']
            
            for metric in key_metrics:
                stats = self.profiler.get_stats(metric)
                if stats and stats['count'] > 0:
                    lines.append(f"{metric.replace('_', ' ').title()}:")
                    lines.append(f"  Latest: {stats['latest']*1000:.2f}ms")
                    lines.append(f"  Average: {stats['mean']*1000:.2f}ms")
                    lines.append(f"  95th: {stats['p95']*1000:.2f}ms")
                    lines.append("")
            
            # Performance warnings
            warnings = self.profiler.check_performance_warnings()
            if warnings:
                lines.append("⚠ PERFORMANCE WARNINGS:")
                lines.extend(f"  {warning}" for warning in warnings)
                lines.append("")
            
            # Counters
            if self.profiler.counters:
                lines.append("EVENT COUNTERS:")
                session_time = time.time() - self.profiler.start_time
                for name, count in sorted(self.profiler.counters.items()):
                    if session_time > 0:
                        rate = count / session_time
                        lines.append(f"  {name}: {count} ({rate:.1f}/sec)")
                
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error generating report: {e}"
    
    def _export_report(self):
        """Export full performance report to file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Performance Report", 
                f"performance_report_{int(time.time())}.txt", 
                "Text Files (*.txt)"
            )
            if filename:
                report = self.profiler.generate_report()
                with open(filename, 'w') as f:
                    f.write(report)
                QMessageBox.information(self, "Success", "Performance report exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report: {e}")
    
    def _clear_metrics(self):
        """Clear all performance metrics."""
        try:
            self.profiler.metrics.clear()
            self.profiler.counters.clear()
            self.profiler.system_metrics.clear()
            self.profiler.start_time = time.time()
            QMessageBox.information(self, "Success", "Performance metrics cleared!")
        except Exception as e:
            QMessageBox.critical(self, "Clear Error", f"Failed to clear metrics: {e}")
    
    def closeEvent(self, event):
        """Clean up when dialog is closed."""
        self.update_timer.stop()
        event.accept()