import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, 
    QGroupBox, QGridLayout, QSlider, QLineEdit, QColorDialog, 
    QFormLayout, QMessageBox, QFileDialog, QTextEdit, QListWidget,
    QListWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import QColor, QPalette, QFont
import json
import os

try:
    import pygame.midi
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class ConfigurationDialog(QDialog):
    """Comprehensive configuration dialog for the morphing interface."""
    
    settings_changed = Signal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.settings = QSettings("MorphingVisualizer", "Config")
        
        self.setWindowTitle("Configuration Settings")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Store original config values for cancel operation
        self._store_original_config()
        
        self._setup_ui()
        self._load_current_settings()
        
    def _store_original_config(self):
        """Store original configuration values."""
        self.original_config = {}
        for attr in dir(self.config):
            if not attr.startswith('_') and not callable(getattr(self.config, attr)):
                self.original_config[attr] = getattr(self.config, attr)
    
    def _setup_ui(self):
        """Setup the configuration dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_midi_tab()
        self._create_audio_tab()
        self._create_visualization_tab()
        self._create_performance_tab()
        self._create_advanced_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Settings")
        self.test_button.clicked.connect(self._test_settings)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        self.load_button = QPushButton("Load Config")
        self.load_button.clicked.connect(self._load_config_file)
        button_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("Save Config")
        self.save_button.clicked.connect(self._save_config_file)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _create_midi_tab(self):
        """Create MIDI configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # MIDI Device Selection
        device_group = QGroupBox("MIDI Device")
        device_layout = QFormLayout(device_group)
        
        # MIDI device dropdown
        self.midi_device_combo = QComboBox()
        self._populate_midi_devices()
        device_layout.addRow("MIDI Device:", self.midi_device_combo)
        
        # MIDI port override
        self.midi_port_edit = QLineEdit()
        self.midi_port_edit.setPlaceholderText("Leave empty for auto-detection")
        device_layout.addRow("Port Override:", self.midi_port_edit)
        
        # Auto-reconnect
        self.midi_auto_reconnect = QCheckBox("Auto-reconnect on disconnect")
        device_layout.addRow(self.midi_auto_reconnect)
        
        layout.addWidget(device_group)
        
        # MIDI Mapping
        mapping_group = QGroupBox("MIDI Mapping")
        mapping_layout = QFormLayout(mapping_group)
        
        # Velocity sensitivity
        self.velocity_sensitivity = QDoubleSpinBox()
        self.velocity_sensitivity.setRange(0.1, 5.0)
        self.velocity_sensitivity.setSingleStep(0.1)
        self.velocity_sensitivity.setValue(1.0)
        mapping_layout.addRow("Velocity Sensitivity:", self.velocity_sensitivity)
        
        # Note range
        self.note_min = QSpinBox()
        self.note_min.setRange(0, 127)
        self.note_min.setValue(0)
        mapping_layout.addRow("Minimum Note:", self.note_min)
        
        self.note_max = QSpinBox()
        self.note_max.setRange(0, 127)
        self.note_max.setValue(127)
        mapping_layout.addRow("Maximum Note:", self.note_max)
        
        # CC assignments
        self.morph_cc = QSpinBox()
        self.morph_cc.setRange(0, 127)
        self.morph_cc.setValue(1)
        mapping_layout.addRow("Morph Control CC:", self.morph_cc)
        
        # Note duration
        self.note_timeout = QSpinBox()
        self.note_timeout.setRange(1, 300)
        self.note_timeout.setValue(60)
        self.note_timeout.setSuffix(" seconds")
        mapping_layout.addRow("Note Timeout:", self.note_timeout)
        
        layout.addWidget(mapping_group)
        
        # MIDI Channels
        channels_group = QGroupBox("MIDI Channels")
        channels_layout = QFormLayout(channels_group)
        
        self.midi_channel = QSpinBox()
        self.midi_channel.setRange(0, 16)  # 0 = all channels
        self.midi_channel.setValue(0)
        self.midi_channel.setSpecialValueText("All Channels")
        channels_layout.addRow("Listen Channel:", self.midi_channel)
        
        layout.addWidget(channels_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "MIDI")
    
    def _create_audio_tab(self):
        """Create audio configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Audio Device
        device_group = QGroupBox("Audio Device")
        device_layout = QFormLayout(device_group)
        
        # Audio device selection
        self.audio_device_combo = QComboBox()
        self._populate_audio_devices()
        device_layout.addRow("Audio Device:", self.audio_device_combo)
        
        # Sample rate
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["22050", "44100", "48000", "96000"])
        self.sample_rate_combo.setCurrentText("44100")
        device_layout.addRow("Sample Rate:", self.sample_rate_combo)
        
        # Buffer size
        self.buffer_size_combo = QComboBox()
        self.buffer_size_combo.addItems(["128", "256", "512", "1024", "2048"])
        self.buffer_size_combo.setCurrentText("512")
        device_layout.addRow("Buffer Size:", self.buffer_size_combo)
        
        layout.addWidget(device_group)
        
        # Audio Analysis
        analysis_group = QGroupBox("Audio Analysis")
        analysis_layout = QFormLayout(analysis_group)
        
        # Onset detection sensitivity
        self.onset_threshold = QDoubleSpinBox()
        self.onset_threshold.setRange(1.1, 5.0)
        self.onset_threshold.setSingleStep(0.1)
        self.onset_threshold.setValue(1.5)
        analysis_layout.addRow("Onset Threshold:", self.onset_threshold)
        
        # Audio-to-visual mapping
        self.audio_color_strength = QDoubleSpinBox()
        self.audio_color_strength.setRange(0.0, 5.0)
        self.audio_color_strength.setSingleStep(0.1)
        self.audio_color_strength.setValue(1.0)
        analysis_layout.addRow("Color Response:", self.audio_color_strength)
        
        self.audio_morph_strength = QDoubleSpinBox()
        self.audio_morph_strength.setRange(0.0, 1.0)
        self.audio_morph_strength.setSingleStep(0.05)
        self.audio_morph_strength.setValue(0.2)
        analysis_layout.addRow("Morph Response:", self.audio_morph_strength)
        
        # Frequency range
        self.freq_min = QSpinBox()
        self.freq_min.setRange(20, 10000)
        self.freq_min.setValue(80)
        self.freq_min.setSuffix(" Hz")
        analysis_layout.addRow("Min Frequency:", self.freq_min)
        
        self.freq_max = QSpinBox()
        self.freq_max.setRange(100, 20000)
        self.freq_max.setValue(8000)
        self.freq_max.setSuffix(" Hz")
        analysis_layout.addRow("Max Frequency:", self.freq_max)
        
        layout.addWidget(analysis_group)
        
        # Audio Features
        features_group = QGroupBox("Feature Extraction")
        features_layout = QVBoxLayout(features_group)
        
        self.enable_spectral_centroid = QCheckBox("Enable Spectral Centroid")
        self.enable_spectral_centroid.setChecked(True)
        features_layout.addWidget(self.enable_spectral_centroid)
        
        self.enable_mfcc = QCheckBox("Enable MFCC Analysis")
        self.enable_mfcc.setChecked(False)
        features_layout.addWidget(self.enable_mfcc)
        
        self.enable_tempo = QCheckBox("Enable Tempo Detection")
        self.enable_tempo.setChecked(False)
        features_layout.addWidget(self.enable_tempo)
        
        layout.addWidget(features_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Audio")
    
    def _create_visualization_tab(self):
        """Create visualization configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Mesh Settings
        mesh_group = QGroupBox("Mesh Settings")
        mesh_layout = QFormLayout(mesh_group)
        
        # Mesh resolution
        self.mesh_resolution = QSpinBox()
        self.mesh_resolution.setRange(10, 200)
        self.mesh_resolution.setValue(50)
        mesh_layout.addRow("Mesh Resolution:", self.mesh_resolution)
        
        # Smoothing
        self.smooth_shading = QCheckBox("Smooth Shading")
        self.smooth_shading.setChecked(True)
        mesh_layout.addRow(self.smooth_shading)
        
        # Wireframe mode
        self.wireframe_mode = QCheckBox("Wireframe Mode")
        mesh_layout.addRow(self.wireframe_mode)
        
        layout.addWidget(mesh_group)
        
        # Color Settings
        color_group = QGroupBox("Color Settings")
        color_layout = QFormLayout(color_group)
        
        # Default color
        self.default_color_button = QPushButton("Choose Default Color")
        self.default_color = QColor(204, 204, 204)  # Light gray
        self.default_color_button.clicked.connect(self._choose_default_color)
        self._update_color_button(self.default_color_button, self.default_color)
        color_layout.addRow("Default Color:", self.default_color_button)
        
        # Color saturation
        self.color_saturation = QDoubleSpinBox()
        self.color_saturation.setRange(0.0, 1.0)
        self.color_saturation.setSingleStep(0.1)
        self.color_saturation.setValue(0.8)
        color_layout.addRow("Color Saturation:", self.color_saturation)
        
        # Color brightness
        self.color_brightness = QDoubleSpinBox()
        self.color_brightness.setRange(0.1, 2.0)
        self.color_brightness.setSingleStep(0.1)
        self.color_brightness.setValue(1.0)
        color_layout.addRow("Color Brightness:", self.color_brightness)
        
        layout.addWidget(color_group)
        
        # Animation Settings
        animation_group = QGroupBox("Animation Settings")
        animation_layout = QFormLayout(animation_group)
        
        # Morphing speed
        self.morph_speed = QDoubleSpinBox()
        self.morph_speed.setRange(0.1, 5.0)
        self.morph_speed.setSingleStep(0.1)
        self.morph_speed.setValue(1.0)
        animation_layout.addRow("Morphing Speed:", self.morph_speed)
        
        # Color transition speed
        self.color_transition_speed = QDoubleSpinBox()
        self.color_transition_speed.setRange(0.1, 2.0)
        self.color_transition_speed.setSingleStep(0.1)
        self.color_transition_speed.setValue(0.5)
        animation_layout.addRow("Color Transition:", self.color_transition_speed)
        
        # Flash duration
        self.flash_duration = QSpinBox()
        self.flash_duration.setRange(50, 1000)
        self.flash_duration.setValue(150)
        self.flash_duration.setSuffix(" ms")
        animation_layout.addRow("Flash Duration:", self.flash_duration)
        
        layout.addWidget(animation_group)
        
        # Camera Settings
        camera_group = QGroupBox("Camera Settings")
        camera_layout = QFormLayout(camera_group)
        
        # Auto-rotate
        self.auto_rotate = QCheckBox("Auto-rotate Camera")
        camera_layout.addRow(self.auto_rotate)
        
        # Rotation speed
        self.rotation_speed = QDoubleSpinBox()
        self.rotation_speed.setRange(0.1, 5.0)
        self.rotation_speed.setSingleStep(0.1)
        self.rotation_speed.setValue(1.0)
        self.rotation_speed.setEnabled(False)
        self.auto_rotate.toggled.connect(self.rotation_speed.setEnabled)
        camera_layout.addRow("Rotation Speed:", self.rotation_speed)
        
        layout.addWidget(camera_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Visualization")
    
    def _create_performance_tab(self):
        """Create performance configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Rendering Performance
        render_group = QGroupBox("Rendering Performance")
        render_layout = QFormLayout(render_group)
        
        # Target FPS
        self.target_fps = QSpinBox()
        self.target_fps.setRange(15, 120)
        self.target_fps.setValue(60)
        render_layout.addRow("Target FPS:", self.target_fps)
        
        # VSync
        self.vsync = QCheckBox("Enable VSync")
        self.vsync.setChecked(True)
        render_layout.addRow(self.vsync)
        
        # Render quality
        self.render_quality = QComboBox()
        self.render_quality.addItems(["Low", "Medium", "High", "Ultra"])
        self.render_quality.setCurrentText("High")
        render_layout.addRow("Render Quality:", self.render_quality)
        
        layout.addWidget(render_group)
        
        # Memory Management
        memory_group = QGroupBox("Memory Management")
        memory_layout = QFormLayout(memory_group)
        
        # Memory limit
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(100, 8000)
        self.memory_limit.setValue(1000)
        self.memory_limit.setSuffix(" MB")
        memory_layout.addRow("Memory Limit:", self.memory_limit)
        
        # Cleanup interval
        self.cleanup_interval = QSpinBox()
        self.cleanup_interval.setRange(1, 60)
        self.cleanup_interval.setValue(5)
        self.cleanup_interval.setSuffix(" seconds")
        memory_layout.addRow("Cleanup Interval:", self.cleanup_interval)
        
        layout.addWidget(memory_group)
        
        # Monitoring Thresholds
        monitor_group = QGroupBox("Performance Monitoring")
        monitor_layout = QFormLayout(monitor_group)
        
        # FPS warning threshold
        self.fps_warning = QSpinBox()
        self.fps_warning.setRange(10, 60)
        self.fps_warning.setValue(30)
        monitor_layout.addRow("FPS Warning:", self.fps_warning)
        
        # Memory warning threshold
        self.memory_warning = QSpinBox()
        self.memory_warning.setRange(50, 95)
        self.memory_warning.setValue(80)
        self.memory_warning.setSuffix("%")
        monitor_layout.addRow("Memory Warning:", self.memory_warning)
        
        # CPU warning threshold
        self.cpu_warning = QSpinBox()
        self.cpu_warning.setRange(50, 95)
        self.cpu_warning.setValue(85)
        self.cpu_warning.setSuffix("%")
        monitor_layout.addRow("CPU Warning:", self.cpu_warning)
        
        layout.addWidget(monitor_group)
        
        # Debugging
        debug_group = QGroupBox("Debugging")
        debug_layout = QVBoxLayout(debug_group)
        
        self.enable_profiling = QCheckBox("Enable Function Profiling")
        self.enable_profiling.setChecked(True)
        debug_layout.addWidget(self.enable_profiling)
        
        self.verbose_logging = QCheckBox("Verbose Logging")
        debug_layout.addWidget(self.verbose_logging)
        
        self.show_debug_info = QCheckBox("Show Debug Info on Screen")
        debug_layout.addWidget(self.show_debug_info)
        
        layout.addWidget(debug_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Performance")
    
    def _create_advanced_tab(self):
        """Create advanced configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # OSC Settings
        osc_group = QGroupBox("OSC Configuration")
        osc_layout = QFormLayout(osc_group)
        
        # OSC IP
        self.osc_ip = QLineEdit()
        self.osc_ip.setText("127.0.0.1")
        osc_layout.addRow("OSC IP Address:", self.osc_ip)
        
        # OSC Port
        self.osc_port = QSpinBox()
        self.osc_port.setRange(1024, 65535)
        self.osc_port.setValue(5005)
        osc_layout.addRow("OSC Port:", self.osc_port)
        
        # Enable OSC
        self.enable_osc = QCheckBox("Enable OSC Output")
        osc_layout.addRow(self.enable_osc)
        
        layout.addWidget(osc_group)
        
        # Threading
        thread_group = QGroupBox("Threading")
        thread_layout = QFormLayout(thread_group)
        
        # Worker threads
        self.worker_threads = QSpinBox()
        self.worker_threads.setRange(1, 8)
        self.worker_threads.setValue(2)
        thread_layout.addRow("Worker Threads:", self.worker_threads)
        
        # Audio thread priority
        self.audio_priority = QComboBox()
        self.audio_priority.addItems(["Normal", "High", "Real-time"])
        self.audio_priority.setCurrentText("High")
        thread_layout.addRow("Audio Thread Priority:", self.audio_priority)
        
        layout.addWidget(thread_group)
        
        # File Paths
        paths_group = QGroupBox("File Paths")
        paths_layout = QFormLayout(paths_group)
        
        # Config directory
        config_layout = QHBoxLayout()
        self.config_dir = QLineEdit()
        self.config_dir.setText(os.path.expanduser("~/.morphing_visualizer"))
        config_layout.addWidget(self.config_dir)
        config_browse = QPushButton("Browse")
        config_browse.clicked.connect(lambda: self._browse_directory(self.config_dir))
        config_layout.addWidget(config_browse)
        paths_layout.addRow("Config Directory:", config_layout)
        
        # Log directory
        log_layout = QHBoxLayout()
        self.log_dir = QLineEdit()
        self.log_dir.setText(os.path.expanduser("~/.morphing_visualizer/logs"))
        log_layout.addWidget(self.log_dir)
        log_browse = QPushButton("Browse")
        log_browse.clicked.connect(lambda: self._browse_directory(self.log_dir))
        log_layout.addWidget(log_browse)
        paths_layout.addRow("Log Directory:", log_layout)
        
        layout.addWidget(paths_group)
        
        # Experimental Features
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QVBoxLayout(experimental_group)
        
        self.enable_ml_features = QCheckBox("Enable Machine Learning Features")
        experimental_layout.addWidget(self.enable_ml_features)
        
        self.enable_network_sync = QCheckBox("Enable Network Synchronization")
        experimental_layout.addWidget(self.enable_network_sync)
        
        self.enable_plugin_system = QCheckBox("Enable Plugin System")
        experimental_layout.addWidget(self.enable_plugin_system)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "Advanced")
    
    def _populate_midi_devices(self):
        """Populate MIDI device dropdown."""
        self.midi_device_combo.clear()
        self.midi_device_combo.addItem("Auto-detect", None)
        
        if not MIDI_AVAILABLE:
            self.midi_device_combo.addItem("MIDI not available", None)
            return
        
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]
                
                if is_input:
                    self.midi_device_combo.addItem(name, i)
            
            pygame.midi.quit()
        except Exception as e:
            self.midi_device_combo.addItem(f"Error: {e}", None)
    
    def _populate_audio_devices(self):
        """Populate audio device dropdown."""
        self.audio_device_combo.clear()
        self.audio_device_combo.addItem("Default Device", None)
        
        if not AUDIO_AVAILABLE:
            self.audio_device_combo.addItem("Audio not available", None)
            return
        
        try:
            audio = pyaudio.PyAudio()
            
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    name = device_info['name']
                    self.audio_device_combo.addItem(name, i)
            
            audio.terminate()
        except Exception as e:
            self.audio_device_combo.addItem(f"Error: {e}", None)
    
    def _choose_default_color(self):
        """Open color picker for default color."""
        color = QColorDialog.getColor(self.default_color, self, "Choose Default Color")
        if color.isValid():
            self.default_color = color
            self._update_color_button(self.default_color_button, color)
    
    def _update_color_button(self, button, color):
        """Update color button appearance."""
        button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")
    
    def _browse_directory(self, line_edit):
        """Browse for directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if directory:
            line_edit.setText(directory)
    
    def _load_current_settings(self):
        """Load current configuration values into UI."""
        # MIDI settings
        if hasattr(self.config, 'MIDI_PORT') and self.config.MIDI_PORT:
            self.midi_port_edit.setText(self.config.MIDI_PORT)
        
        # Audio settings
        if hasattr(self.config, 'AUDIO_SAMPLE_RATE'):
            self.sample_rate_combo.setCurrentText(str(self.config.AUDIO_SAMPLE_RATE))
        if hasattr(self.config, 'AUDIO_CHUNK_SIZE'):
            self.buffer_size_combo.setCurrentText(str(self.config.AUDIO_CHUNK_SIZE))
        if hasattr(self.config, 'AUDIO_ONSET_THRESHOLD'):
            self.onset_threshold.setValue(self.config.AUDIO_ONSET_THRESHOLD)
        
        # Visualization settings
        if hasattr(self.config, 'MESH_RESOLUTION'):
            self.mesh_resolution.setValue(self.config.MESH_RESOLUTION)
        
        # Load from QSettings
        self._load_ui_from_settings()
    
    def _load_ui_from_settings(self):
        """Load UI values from QSettings."""
        # MIDI
        self.velocity_sensitivity.setValue(self.settings.value("midi/velocity_sensitivity", 1.0, float))
        self.note_min.setValue(self.settings.value("midi/note_min", 0, int))
        self.note_max.setValue(self.settings.value("midi/note_max", 127, int))
        self.morph_cc.setValue(self.settings.value("midi/morph_cc", 1, int))
        self.note_timeout.setValue(self.settings.value("midi/note_timeout", 60, int))
        self.midi_channel.setValue(self.settings.value("midi/channel", 0, int))
        self.midi_auto_reconnect.setChecked(self.settings.value("midi/auto_reconnect", True, bool))
        
        # Audio
        self.audio_color_strength.setValue(self.settings.value("audio/color_strength", 1.0, float))
        self.audio_morph_strength.setValue(self.settings.value("audio/morph_strength", 0.2, float))
        self.freq_min.setValue(self.settings.value("audio/freq_min", 80, int))
        self.freq_max.setValue(self.settings.value("audio/freq_max", 8000, int))
        
        # Visualization
        self.color_saturation.setValue(self.settings.value("visualization/color_saturation", 0.8, float))
        self.color_brightness.setValue(self.settings.value("visualization/color_brightness", 1.0, float))
        self.morph_speed.setValue(self.settings.value("visualization/morph_speed", 1.0, float))
        self.color_transition_speed.setValue(self.settings.value("visualization/color_transition_speed", 0.5, float))
        self.flash_duration.setValue(self.settings.value("visualization/flash_duration", 150, int))
        self.smooth_shading.setChecked(self.settings.value("visualization/smooth_shading", True, bool))
        self.wireframe_mode.setChecked(self.settings.value("visualization/wireframe_mode", False, bool))
        self.auto_rotate.setChecked(self.settings.value("visualization/auto_rotate", False, bool))
        self.rotation_speed.setValue(self.settings.value("visualization/rotation_speed", 1.0, float))
        
        # Performance
        self.target_fps.setValue(self.settings.value("performance/target_fps", 60, int))
        self.vsync.setChecked(self.settings.value("performance/vsync", True, bool))
        self.render_quality.setCurrentText(self.settings.value("performance/render_quality", "High"))
        self.memory_limit.setValue(self.settings.value("performance/memory_limit", 1000, int))
        self.cleanup_interval.setValue(self.settings.value("performance/cleanup_interval", 5, int))
        self.fps_warning.setValue(self.settings.value("performance/fps_warning", 30, int))
        self.memory_warning.setValue(self.settings.value("performance/memory_warning", 80, int))
        self.cpu_warning.setValue(self.settings.value("performance/cpu_warning", 85, int))
        self.enable_profiling.setChecked(self.settings.value("performance/enable_profiling", True, bool))
        self.verbose_logging.setChecked(self.settings.value("performance/verbose_logging", False, bool))
        self.show_debug_info.setChecked(self.settings.value("performance/show_debug_info", False, bool))
        
        # Advanced
        self.osc_ip.setText(self.settings.value("advanced/osc_ip", "127.0.0.1"))
        self.osc_port.setValue(self.settings.value("advanced/osc_port", 5005, int))
        self.enable_osc.setChecked(self.settings.value("advanced/enable_osc", False, bool))
        self.worker_threads.setValue(self.settings.value("advanced/worker_threads", 2, int))
        self.audio_priority.setCurrentText(self.settings.value("advanced/audio_priority", "High"))
        self.config_dir.setText(self.settings.value("advanced/config_dir", os.path.expanduser("~/.morphing_visualizer")))
        self.log_dir.setText(self.settings.value("advanced/log_dir", os.path.expanduser("~/.morphing_visualizer/logs")))
        self.enable_ml_features.setChecked(self.settings.value("advanced/enable_ml", False, bool))
        self.enable_network_sync.setChecked(self.settings.value("advanced/enable_network_sync", False, bool))
        self.enable_plugin_system.setChecked(self.settings.value("advanced/enable_plugins", False, bool))
        
        # Load default color
        default_color_name = self.settings.value("visualization/default_color", "#CCCCCC")
        self.default_color = QColor(default_color_name)
        self._update_color_button(self.default_color_button, self.default_color)
    
    def _save_ui_to_settings(self):
        """Save UI values to QSettings."""
        # MIDI
        self.settings.setValue("midi/velocity_sensitivity", self.velocity_sensitivity.value())
        self.settings.setValue("midi/note_min", self.note_min.value())
        self.settings.setValue("midi/note_max", self.note_max.value())
        self.settings.setValue("midi/morph_cc", self.morph_cc.value())
        self.settings.setValue("midi/note_timeout", self.note_timeout.value())
        self.settings.setValue("midi/channel", self.midi_channel.value())
        self.settings.setValue("midi/auto_reconnect", self.midi_auto_reconnect.isChecked())
        
        # Audio
        self.settings.setValue("audio/color_strength", self.audio_color_strength.value())
        self.settings.setValue("audio/morph_strength", self.audio_morph_strength.value())
        self.settings.setValue("audio/freq_min", self.freq_min.value())
        self.settings.setValue("audio/freq_max", self.freq_max.value())
        
        # Visualization
        self.settings.setValue("visualization/color_saturation", self.color_saturation.value())
        self.settings.setValue("visualization/color_brightness", self.color_brightness.value())
        self.settings.setValue("visualization/morph_speed", self.morph_speed.value())
        self.settings.setValue("visualization/color_transition_speed", self.color_transition_speed.value())
        self.settings.setValue("visualization/flash_duration", self.flash_duration.value())
        self.settings.setValue("visualization/smooth_shading", self.smooth_shading.isChecked())
        self.settings.setValue("visualization/wireframe_mode", self.wireframe_mode.isChecked())
        self.settings.setValue("visualization/auto_rotate", self.auto_rotate.isChecked())
        self.settings.setValue("visualization/rotation_speed", self.rotation_speed.value())
        self.settings.setValue("visualization/default_color", self.default_color.name())
        
        # Performance
        self.settings.setValue("performance/target_fps", self.target_fps.value())
        self.settings.setValue("performance/vsync", self.vsync.isChecked())
        self.settings.setValue("performance/render_quality", self.render_quality.currentText())
        self.settings.setValue("performance/memory_limit", self.memory_limit.value())
        self.settings.setValue("performance/cleanup_interval", self.cleanup_interval.value())
        self.settings.setValue("performance/fps_warning", self.fps_warning.value())
        self.settings.setValue("performance/memory_warning", self.memory_warning.value())
        self.settings.setValue("performance/cpu_warning", self.cpu_warning.value())
        self.settings.setValue("performance/enable_profiling", self.enable_profiling.isChecked())
        self.settings.setValue("performance/verbose_logging", self.verbose_logging.isChecked())
        self.settings.setValue("performance/show_debug_info", self.show_debug_info.isChecked())
        
        # Advanced
        self.settings.setValue("advanced/osc_ip", self.osc_ip.text())
        self.settings.setValue("advanced/osc_port", self.osc_port.value())
        self.settings.setValue("advanced/enable_osc", self.enable_osc.isChecked())
        self.settings.setValue("advanced/worker_threads", self.worker_threads.value())
        self.settings.setValue("advanced/audio_priority", self.audio_priority.currentText())
        self.settings.setValue("advanced/config_dir", self.config_dir.text())
        self.settings.setValue("advanced/log_dir", self.log_dir.text())
        self.settings.setValue("advanced/enable_ml", self.enable_ml_features.isChecked())
        self.settings.setValue("advanced/enable_network_sync", self.enable_network_sync.isChecked())
        self.settings.setValue("advanced/enable_plugins", self.enable_plugin_system.isChecked())
        
        self.settings.sync()
    
    def _apply_settings_to_config(self):
        """Apply UI settings to the config object."""
        # Update config object with new values
        if self.midi_port_edit.text().strip():
            self.config.MIDI_PORT = self.midi_port_edit.text().strip()
        else:
            self.config.MIDI_PORT = None
        
        # Audio settings
        self.config.AUDIO_SAMPLE_RATE = int(self.sample_rate_combo.currentText())
        self.config.AUDIO_CHUNK_SIZE = int(self.buffer_size_combo.currentText())
        self.config.AUDIO_ONSET_THRESHOLD = self.onset_threshold.value()
        
        # Visualization settings
        self.config.MESH_RESOLUTION = self.mesh_resolution.value()
        
        # Add new config attributes for extended settings
        self.config.VELOCITY_SENSITIVITY = self.velocity_sensitivity.value()
        self.config.NOTE_MIN = self.note_min.value()
        self.config.NOTE_MAX = self.note_max.value()
        self.config.MORPH_CC = self.morph_cc.value()
        self.config.NOTE_TIMEOUT = self.note_timeout.value()
        self.config.MIDI_CHANNEL = self.midi_channel.value()
        self.config.MIDI_AUTO_RECONNECT = self.midi_auto_reconnect.isChecked()
        
        self.config.AUDIO_COLOR_STRENGTH = self.audio_color_strength.value()
        self.config.AUDIO_MORPH_STRENGTH = self.audio_morph_strength.value()
        self.config.FREQ_MIN = self.freq_min.value()
        self.config.FREQ_MAX = self.freq_max.value()
        
        self.config.COLOR_SATURATION = self.color_saturation.value()
        self.config.COLOR_BRIGHTNESS = self.color_brightness.value()
        self.config.MORPH_SPEED = self.morph_speed.value()
        self.config.COLOR_TRANSITION_SPEED = self.color_transition_speed.value()
        self.config.FLASH_DURATION = self.flash_duration.value()
        self.config.SMOOTH_SHADING = self.smooth_shading.isChecked()
        self.config.WIREFRAME_MODE = self.wireframe_mode.isChecked()
        self.config.AUTO_ROTATE = self.auto_rotate.isChecked()
        self.config.ROTATION_SPEED = self.rotation_speed.value()
        self.config.DEFAULT_COLOR = [self.default_color.redF(), self.default_color.greenF(), self.default_color.blueF()]
        
        self.config.TARGET_FPS = self.target_fps.value()
        self.config.VSYNC = self.vsync.isChecked()
        self.config.RENDER_QUALITY = self.render_quality.currentText()
        self.config.MEMORY_LIMIT = self.memory_limit.value()
        self.config.CLEANUP_INTERVAL = self.cleanup_interval.value()
        self.config.FPS_WARNING = self.fps_warning.value()
        self.config.MEMORY_WARNING = self.memory_warning.value()
        self.config.CPU_WARNING = self.cpu_warning.value()
        self.config.ENABLE_PROFILING = self.enable_profiling.isChecked()
        self.config.VERBOSE_LOGGING = self.verbose_logging.isChecked()
        self.config.SHOW_DEBUG_INFO = self.show_debug_info.isChecked()
        
        self.config.OSC_IP = self.osc_ip.text()
        self.config.OSC_PORT = self.osc_port.value()
        self.config.ENABLE_OSC = self.enable_osc.isChecked()
        self.config.WORKER_THREADS = self.worker_threads.value()
        self.config.AUDIO_PRIORITY = self.audio_priority.currentText()
        self.config.CONFIG_DIR = self.config_dir.text()
        self.config.LOG_DIR = self.log_dir.text()
        self.config.ENABLE_ML_FEATURES = self.enable_ml_features.isChecked()
        self.config.ENABLE_NETWORK_SYNC = self.enable_network_sync.isChecked()
        self.config.ENABLE_PLUGIN_SYSTEM = self.enable_plugin_system.isChecked()
    
    def _test_settings(self):
        """Test current settings."""
        messages = []
        
        # Test MIDI
        if MIDI_AVAILABLE:
            try:
                pygame.midi.init()
                device_id = self.midi_device_combo.currentData()
                if device_id is not None:
                    test_input = pygame.midi.Input(device_id)
                    test_input.close()
                    messages.append("✓ MIDI device connection successful")
                else:
                    messages.append("⚠ MIDI set to auto-detect")
                pygame.midi.quit()
            except Exception as e:
                messages.append(f"✗ MIDI test failed: {e}")
        else:
            messages.append("⚠ MIDI not available")
        
        # Test Audio
        if AUDIO_AVAILABLE:
            try:
                audio = pyaudio.PyAudio()
                device_id = self.audio_device_combo.currentData()
                sample_rate = int(self.sample_rate_combo.currentText())
                buffer_size = int(self.buffer_size_combo.currentText())
                
                # Test audio stream
                if device_id is not None:
                    stream = audio.open(
                        format=pyaudio.paFloat32,
                        channels=1,
                        rate=sample_rate,
                        input=True,
                        input_device_index=device_id,
                        frames_per_buffer=buffer_size
                    )
                    stream.close()
                    messages.append("✓ Audio device test successful")
                else:
                    messages.append("⚠ Audio set to default device")
                
                audio.terminate()
            except Exception as e:
                messages.append(f"✗ Audio test failed: {e}")
        else:
            messages.append("⚠ Audio not available")
        
        # Test performance settings
        if self.target_fps.value() < 30:
            messages.append("⚠ Low target FPS may affect responsiveness")
        
        if self.memory_limit.value() < 500:
            messages.append("⚠ Low memory limit may cause instability")
        
        # Test paths
        config_path = self.config_dir.text()
        if not os.path.exists(config_path):
            try:
                os.makedirs(config_path, exist_ok=True)
                messages.append("✓ Config directory created")
            except Exception as e:
                messages.append(f"✗ Cannot create config directory: {e}")
        else:
            messages.append("✓ Config directory exists")
        
        log_path = self.log_dir.text()
        if not os.path.exists(log_path):
            try:
                os.makedirs(log_path, exist_ok=True)
                messages.append("✓ Log directory created")
            except Exception as e:
                messages.append(f"✗ Cannot create log directory: {e}")
        else:
            messages.append("✓ Log directory exists")
        
        # Show results
        result_dialog = QMessageBox(self)
        result_dialog.setWindowTitle("Settings Test Results")
        result_dialog.setText("Configuration Test Results:")
        result_dialog.setDetailedText("\n".join(messages))
        result_dialog.exec()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, 
            "Reset to Defaults", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all settings
            self.settings.clear()
            
            # Reset UI to defaults
            self._load_ui_from_settings()
            
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to defaults.")
    
    def _save_config_file(self):
        """Save configuration to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            f"morphing_config_{int(__import__('time').time())}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                config_data = {}
                
                # Collect all settings
                config_data["midi"] = {
                    "velocity_sensitivity": self.velocity_sensitivity.value(),
                    "note_min": self.note_min.value(),
                    "note_max": self.note_max.value(),
                    "morph_cc": self.morph_cc.value(),
                    "note_timeout": self.note_timeout.value(),
                    "channel": self.midi_channel.value(),
                    "auto_reconnect": self.midi_auto_reconnect.isChecked(),
                    "port": self.midi_port_edit.text()
                }
                
                config_data["audio"] = {
                    "sample_rate": int(self.sample_rate_combo.currentText()),
                    "buffer_size": int(self.buffer_size_combo.currentText()),
                    "onset_threshold": self.onset_threshold.value(),
                    "color_strength": self.audio_color_strength.value(),
                    "morph_strength": self.audio_morph_strength.value(),
                    "freq_min": self.freq_min.value(),
                    "freq_max": self.freq_max.value()
                }
                
                config_data["visualization"] = {
                    "mesh_resolution": self.mesh_resolution.value(),
                    "color_saturation": self.color_saturation.value(),
                    "color_brightness": self.color_brightness.value(),
                    "morph_speed": self.morph_speed.value(),
                    "color_transition_speed": self.color_transition_speed.value(),
                    "flash_duration": self.flash_duration.value(),
                    "smooth_shading": self.smooth_shading.isChecked(),
                    "wireframe_mode": self.wireframe_mode.isChecked(),
                    "auto_rotate": self.auto_rotate.isChecked(),
                    "rotation_speed": self.rotation_speed.value(),
                    "default_color": self.default_color.name()
                }
                
                config_data["performance"] = {
                    "target_fps": self.target_fps.value(),
                    "vsync": self.vsync.isChecked(),
                    "render_quality": self.render_quality.currentText(),
                    "memory_limit": self.memory_limit.value(),
                    "cleanup_interval": self.cleanup_interval.value(),
                    "fps_warning": self.fps_warning.value(),
                    "memory_warning": self.memory_warning.value(),
                    "cpu_warning": self.cpu_warning.value(),
                    "enable_profiling": self.enable_profiling.isChecked(),
                    "verbose_logging": self.verbose_logging.isChecked(),
                    "show_debug_info": self.show_debug_info.isChecked()
                }
                
                config_data["advanced"] = {
                    "osc_ip": self.osc_ip.text(),
                    "osc_port": self.osc_port.value(),
                    "enable_osc": self.enable_osc.isChecked(),
                    "worker_threads": self.worker_threads.value(),
                    "audio_priority": self.audio_priority.currentText(),
                    "config_dir": self.config_dir.text(),
                    "log_dir": self.log_dir.text(),
                    "enable_ml": self.enable_ml_features.isChecked(),
                    "enable_network_sync": self.enable_network_sync.isChecked(),
                    "enable_plugins": self.enable_plugin_system.isChecked()
                }
                
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                QMessageBox.information(self, "Save Successful", f"Configuration saved to:\n{filename}")
                
            except Exception as e:
                QMessageBox.warning(self, "Save Failed", f"Failed to save configuration:\n{e}")
    
    def _load_config_file(self):
        """Load configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                
                # Load MIDI settings
                if "midi" in config_data:
                    midi = config_data["midi"]
                    self.velocity_sensitivity.setValue(midi.get("velocity_sensitivity", 1.0))
                    self.note_min.setValue(midi.get("note_min", 0))
                    self.note_max.setValue(midi.get("note_max", 127))
                    self.morph_cc.setValue(midi.get("morph_cc", 1))
                    self.note_timeout.setValue(midi.get("note_timeout", 60))
                    self.midi_channel.setValue(midi.get("channel", 0))
                    self.midi_auto_reconnect.setChecked(midi.get("auto_reconnect", True))
                    self.midi_port_edit.setText(midi.get("port", ""))
                
                # Load audio settings
                if "audio" in config_data:
                    audio = config_data["audio"]
                    self.sample_rate_combo.setCurrentText(str(audio.get("sample_rate", 44100)))
                    self.buffer_size_combo.setCurrentText(str(audio.get("buffer_size", 512)))
                    self.onset_threshold.setValue(audio.get("onset_threshold", 1.5))
                    self.audio_color_strength.setValue(audio.get("color_strength", 1.0))
                    self.audio_morph_strength.setValue(audio.get("morph_strength", 0.2))
                    self.freq_min.setValue(audio.get("freq_min", 80))
                    self.freq_max.setValue(audio.get("freq_max", 8000))
                
                # Load visualization settings
                if "visualization" in config_data:
                    viz = config_data["visualization"]
                    self.mesh_resolution.setValue(viz.get("mesh_resolution", 50))
                    self.color_saturation.setValue(viz.get("color_saturation", 0.8))
                    self.color_brightness.setValue(viz.get("color_brightness", 1.0))
                    self.morph_speed.setValue(viz.get("morph_speed", 1.0))
                    self.color_transition_speed.setValue(viz.get("color_transition_speed", 0.5))
                    self.flash_duration.setValue(viz.get("flash_duration", 150))
                    self.smooth_shading.setChecked(viz.get("smooth_shading", True))
                    self.wireframe_mode.setChecked(viz.get("wireframe_mode", False))
                    self.auto_rotate.setChecked(viz.get("auto_rotate", False))
                    self.rotation_speed.setValue(viz.get("rotation_speed", 1.0))
                    
                    color_name = viz.get("default_color", "#CCCCCC")
                    self.default_color = QColor(color_name)
                    self._update_color_button(self.default_color_button, self.default_color)
                
                # Load performance settings
                if "performance" in config_data:
                    perf = config_data["performance"]
                    self.target_fps.setValue(perf.get("target_fps", 60))
                    self.vsync.setChecked(perf.get("vsync", True))
                    self.render_quality.setCurrentText(perf.get("render_quality", "High"))
                    self.memory_limit.setValue(perf.get("memory_limit", 1000))
                    self.cleanup_interval.setValue(perf.get("cleanup_interval", 5))
                    self.fps_warning.setValue(perf.get("fps_warning", 30))
                    self.memory_warning.setValue(perf.get("memory_warning", 80))
                    self.cpu_warning.setValue(perf.get("cpu_warning", 85))
                    self.enable_profiling.setChecked(perf.get("enable_profiling", True))
                    self.verbose_logging.setChecked(perf.get("verbose_logging", False))
                    self.show_debug_info.setChecked(perf.get("show_debug_info", False))
                
                # Load advanced settings
                if "advanced" in config_data:
                    adv = config_data["advanced"]
                    self.osc_ip.setText(adv.get("osc_ip", "127.0.0.1"))
                    self.osc_port.setValue(adv.get("osc_port", 5005))
                    self.enable_osc.setChecked(adv.get("enable_osc", False))
                    self.worker_threads.setValue(adv.get("worker_threads", 2))
                    self.audio_priority.setCurrentText(adv.get("audio_priority", "High"))
                    self.config_dir.setText(adv.get("config_dir", os.path.expanduser("~/.morphing_visualizer")))
                    self.log_dir.setText(adv.get("log_dir", os.path.expanduser("~/.morphing_visualizer/logs")))
                    self.enable_ml_features.setChecked(adv.get("enable_ml", False))
                    self.enable_network_sync.setChecked(adv.get("enable_network_sync", False))
                    self.enable_plugin_system.setChecked(adv.get("enable_plugins", False))
                
                QMessageBox.information(self, "Load Successful", f"Configuration loaded from:\n{filename}")
                
            except Exception as e:
                QMessageBox.warning(self, "Load Failed", f"Failed to load configuration:\n{e}")
    
    def accept(self):
        """Accept dialog and save settings."""
        try:
            # Validate settings
            if self.note_min.value() >= self.note_max.value():
                QMessageBox.warning(self, "Invalid Settings", "Minimum note must be less than maximum note.")
                return
            
            if self.freq_min.value() >= self.freq_max.value():
                QMessageBox.warning(self, "Invalid Settings", "Minimum frequency must be less than maximum frequency.")
                return
            
            # Apply settings to config
            self._apply_settings_to_config()
            
            # Save to QSettings
            self._save_ui_to_settings()
            
            # Emit settings changed signal
            self.settings_changed.emit()
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings:\n{e}")
    
    def reject(self):
        """Reject dialog and restore original config."""
        # Restore original configuration
        for attr, value in self.original_config.items():
            setattr(self.config, attr, value)
        
        super().reject()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from config import Config
    
    app = QApplication(sys.argv)
    
    config = Config()
    dialog = ConfigurationDialog(config)
    
    if dialog.exec() == QDialog.Accepted:
        print("Settings accepted and saved!")
    else:
        print("Settings canceled")
    
    sys.exit()
