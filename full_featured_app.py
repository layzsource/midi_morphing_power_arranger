# Onset detection
            onset_strength = np.sum(np.diff(magnitude_spectrum) ** 2)
            onset_detected = onset_strength > self.previous_onset_strength * (1 + self.config.AUDIO_ONSET_THRESHOLD)
            
            if onset_detected:
                self.onset_detected_signal.emit(features['rms'])
            
            self.previous_onset_strength = onset_strength * 0.9 + onset_strength * 0.1
            
            # Emit basic amplitude
            self.amplitude_signal.emit(features['rms'])
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
    
    def stop(self):
        self.running = False
        self.is_active = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
        print("Advanced audio analysis stopped")

# =============================================================================
# MIDI Handler (Enhanced)
# =============================================================================

class EnhancedMidiHandler(QObject):
    note_on_signal = Signal(int, float, int)  # note, velocity, channel
    note_off_signal = Signal(int, int)        # note, channel
    cc_signal = Signal(int, float, int)       # cc, value, channel
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.midi_input = None
        self.running = False
        self.thread = None
        self.midi_initialized = False
        
    def start(self, device_name=None):
        if not MIDI_AVAILABLE:
            return False
            
        try:
            if not self.midi_initialized:
                pygame.midi.init()
                self.midi_initialized = True
            
            device_id = self._find_device(device_name or self.config.MIDI_PORT)
            if device_id is None:
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"✓ Connected to MIDI device: {device_name}")
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to start MIDI: {e}")
            self._cleanup_midi()
            return False
    
    def _find_device(self, preferred_name=None):
        try:
            device_count = pygame.midi.get_count()
            print(f"Found {device_count} MIDI devices")
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]
                
                if is_input:
                    if preferred_name and preferred_name.lower() in name.lower():
                        return i
                    elif not preferred_name:
                        return i
            
            return None
        except Exception as e:
            print(f"Error finding MIDI device: {e}")
            return None
    
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
                if not self.midi_initialized:
                    break
                    
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                time.sleep(0.001)
                
            except Exception as e:
                print(f"MIDI polling error: {e}")
                break
    
    def _process_midi_event(self, midi_data):
        if len(midi_data) < 3:
            return
            
        status, data1, data2 = midi_data[:3]
        channel = status & 0x0F
        
        # Check channel filter
        if self.config.MIDI_CHANNEL > 0 and channel != (self.config.MIDI_CHANNEL - 1):
            return
        
        if MidiConstants.NOTE_ON_START <= status <= MidiConstants.NOTE_ON_END:
            if data2 > 0:
                velocity = (data2 / MidiConstants.MAX_VALUE) * self.config.VELOCITY_SENSITIVITY
                self.note_on_signal.emit(data1, min(velocity, 1.0), channel)
            else:
                self.note_off_signal.emit(data1, channel)
        elif MidiConstants.NOTE_OFF_START <= status <= MidiConstants.NOTE_OFF_END:
            self.note_off_signal.emit(data1, channel)
        elif MidiConstants.CC_START <= status <= MidiConstants.CC_END:
            cc_value = data2 / MidiConstants.MAX_VALUE
            self.cc_signal.emit(data1, cc_value, channel)
    
    def _cleanup_midi(self):
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None
        except Exception as e:
            print(f"Error closing MIDI input: {e}")
        
        try:
            if self.midi_initialized:
                pygame.midi.quit()
                self.midi_initialized = False
        except Exception as e:
            print(f"Error quitting pygame.midi: {e}")
    
    def stop(self):
        print("Stopping enhanced MIDI handler...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self._cleanup_midi()
        print("Enhanced MIDI handler stopped")

# =============================================================================
# Performance Monitoring
# =============================================================================

class PerformanceProfiler(QObject):
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)
    cpu_updated = Signal(float)
    performance_warning = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.enabled = config.ENABLE_PROFILING
        
        if PERFORMANCE_MONITORING:
            self.process = psutil.Process()
            self.fps_history = []
            self.frame_count = 0
            self.last_fps_time = time.time()
            self.start_time = time.time()
            
            # Start monitoring thread
            self.monitoring_active = False
            self.monitoring_thread = None
            if self.enabled:
                self.start_monitoring()
    
    def start_monitoring(self):
        if not PERFORMANCE_MONITORING or self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("✓ Performance monitoring started")
    
    def _monitoring_loop(self):
        while self.monitoring_active:
            try:
                if PERFORMANCE_MONITORING:
                    # System metrics
                    memory_info = psutil.virtual_memory()
                    memory_mb = memory_info.used / (1024 * 1024)
                    memory_percent = memory_info.percent
                    
                    cpu_percent = psutil.cpu_percent(interval=None)
                    
                    # Emit signals
                    self.memory_updated.emit(memory_mb, memory_percent)
                    self.cpu_updated.emit(cpu_percent)
                    
                    # Check warnings
                    if memory_percent > self.config.MEMORY_WARNING:
                        self.performance_warning.emit(f"High memory usage: {memory_percent:.1f}%")
                    
                    if cpu_percent > self.config.CPU_WARNING:
                        self.performance_warning.emit(f"High CPU usage: {cpu_percent:.1f}%")
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(2.0)
    
    def record_frame(self):
        """Call this each frame to track FPS."""
        if not self.enabled:
            return
            
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            fps = self.frame_count / (current_time - self.last_fps_time)
            self.fps_history.append(fps)
            
            if len(self.fps_history) > 60:  # Keep last 60 seconds
                self.fps_history.pop(0)
            
            self.fps_updated.emit(fps)
            
            if fps < self.config.FPS_WARNING:
                self.performance_warning.emit(f"Low FPS: {fps:.1f}")
            
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def stop_monitoring(self):
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)

# =============================================================================
# Configuration Dialog
# =============================================================================

class AdvancedConfigDialog(QWidget):
    settings_changed = Signal()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Advanced Configuration")
        self.resize(600, 500)
        
        self._setup_ui()
        self._load_current_config()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_midi_tab()
        self._create_audio_tab()
        self._create_visual_tab()
        self._create_performance_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Settings")
        self.test_button.clicked.connect(self._test_settings)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_defaults)
        button_layout.addWidget(self.reset_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _create_midi_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # MIDI Settings Group
        midi_group = QGroupBox("MIDI Settings")
        midi_layout = QGridLayout(midi_group)
        
        midi_layout.addWidget(QLabel("Velocity Sensitivity:"), 0, 0)
        self.velocity_sensitivity = QDoubleSpinBox()
        self.velocity_sensitivity.setRange(0.1, 5.0)
        self.velocity_sensitivity.setSingleStep(0.1)
        midi_layout.addWidget(self.velocity_sensitivity, 0, 1)
        
        midi_layout.addWidget(QLabel("Note Range Min:"), 1, 0)
        self.note_min = QSpinBox()
        self.note_min.setRange(0, 127)
        midi_layout.addWidget(self.note_min, 1, 1)
        
        midi_layout.addWidget(QLabel("Note Range Max:"), 2, 0)
        self.note_max = QSpinBox()
        self.note_max.setRange(0, 127)
        midi_layout.addWidget(self.note_max, 2, 1)
        
        midi_layout.addWidget(QLabel("Morph CC:"), 3, 0)
        self.morph_cc = QSpinBox()
        self.morph_cc.setRange(0, 127)
        midi_layout.addWidget(self.morph_cc, 3, 1)
        
        midi_layout.addWidget(QLabel("MIDI Channel (0=All):"), 4, 0)
        self.midi_channel = QSpinBox()
        self.midi_channel.setRange(0, 16)
        midi_layout.addWidget(self.midi_channel, 4, 1)
        
        layout.addWidget(midi_group)
        
        self.tab_widget.addTab(widget, "MIDI")
    
    def _create_audio_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Audio Analysis Group
        audio_group = QGroupBox("Audio Analysis")
        audio_layout = QGridLayout(audio_group)
        
        audio_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.sample_rate = QComboBox()
        self.sample_rate.addItems(["22050", "44100", "48000", "96000"])
        audio_layout.addWidget(self.sample_rate, 0, 1)
        
        audio_layout.addWidget(QLabel("Chunk Size:"), 1, 0)
        self.chunk_size = QComboBox()
        self.chunk_size.addItems(["256", "512", "1024", "2048"])
        audio_layout.addWidget(self.chunk_size, 1, 1)
        
        audio_layout.addWidget(QLabel("Onset Threshold:"), 2, 0)
        self.onset_threshold = QDoubleSpinBox()
        self.onset_threshold.setRange(1.1, 5.0)
        self.onset_threshold.setSingleStep(0.1)
        audio_layout.addWidget(self.onset_threshold, 2, 1)
        
        audio_layout.addWidget(QLabel("Color Strength:"), 3, 0)
        self.audio_color_strength = QDoubleSpinBox()
        self.audio_color_strength.setRange(0.0, 5.0)
        self.audio_color_strength.setSingleStep(0.1)
        audio_layout.addWidget(self.audio_color_strength, 3, 1)
        
        layout.addWidget(audio_group)
        
        self.tab_widget.addTab(widget, "Audio")
    
    def _create_visual_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Visual Settings Group
        visual_group = QGroupBox("Visual Settings")
        visual_layout = QGridLayout(visual_group)
        
        visual_layout.addWidget(QLabel("Mesh Resolution:"), 0, 0)
        self.mesh_resolution = QSpinBox()
        self.mesh_resolution.setRange(10, 100)
        visual_layout.addWidget(self.mesh_resolution, 0, 1)
        
        visual_layout.addWidget(QLabel("Color Saturation:"), 1, 0)
        self.color_saturation = QDoubleSpinBox()
        self.color_saturation.setRange(0.0, 1.0)
        self.color_saturation.setSingleStep(0.1)
        visual_layout.addWidget(self.color_saturation, 1, 1)
        
        visual_layout.addWidget(QLabel("Color Brightness:"), 2, 0)
        self.color_brightness = QDoubleSpinBox()
        self.color_brightness.setRange(0.1, 2.0)
        self.color_brightness.setSingleStep(0.1)
        visual_layout.addWidget(self.color_brightness, 2, 1)
        
        visual_layout.addWidget(QLabel("Morph Speed:"), 3, 0)
        self.morph_speed = QDoubleSpinBox()
        self.morph_speed.setRange(0.1, 5.0)
        self.morph_speed.setSingleStep(0.1)
        visual_layout.addWidget(self.morph_speed, 3, 1)
        
        layout.addWidget(visual_group)
        
        self.tab_widget.addTab(widget, "Visual")
    
    def _create_performance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance Settings Group
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QGridLayout(perf_group)
        
        perf_layout.addWidget(QLabel("Target FPS:"), 0, 0)
        self.target_fps = QSpinBox()
        self.target_fps.setRange(15, 120)
        perf_layout.addWidget(self.target_fps, 0, 1)
        
        perf_layout.addWidget(QLabel("Memory Warning (%):"), 1, 0)
        self.memory_warning = QSpinBox()
        self.memory_warning.setRange(50, 95)
        perf_layout.addWidget(self.memory_warning, 1, 1)
        
        perf_layout.addWidget(QLabel("CPU Warning (%):"), 2, 0)
        self.cpu_warning = QSpinBox()
        self.cpu_warning.setRange(50, 95)
        perf_layout.addWidget(self.cpu_warning, 2, 1)
        
        perf_layout.addWidget(QLabel("Enable Profiling:"), 3, 0)
        self.enable_profiling = QCheckBox()
        perf_layout.addWidget(self.enable_profiling, 3, 1)
        
        layout.addWidget(perf_group)
        
        self.tab_widget.addTab(widget, "Performance")
    
    def _load_current_config(self):
        """Load current configuration into UI."""
        # MIDI
        self.velocity_sensitivity.setValue(self.config.VELOCITY_SENSITIVITY)
        self.note_min.setValue(self.config.NOTE_MIN)
        self.note_max.setValue(self.config.NOTE_MAX)
        self.morph_cc.setValue(self.config.MORPH_CC)
        self.midi_channel.setValue(self.config.MIDI_CHANNEL)
        
        # Audio
        self.sample_rate.setCurrentText(str(self.config.AUDIO_SAMPLE_RATE))
        self.chunk_size.setCurrentText(str(self.config.AUDIO_CHUNK_SIZE))
        self.onset_threshold.setValue(self.config.AUDIO_ONSET_THRESHOLD)
        self.audio_color_strength.setValue(self.config.AUDIO_COLOR_STRENGTH)
        
        # Visual
        self.mesh_resolution.setValue(self.config.MESH_RESOLUTION)
        self.color_saturation.setValue(self.config.COLOR_SATURATION)
        self.color_brightness.setValue(self.config.COLOR_BRIGHTNESS)
        self.morph_speed.setValue(self.config.MORPH_SPEED)
        
        # Performance
        self.target_fps.setValue(self.config.TARGET_FPS)
        self.memory_warning.setValue(self.config.MEMORY_WARNING)
        self.cpu_warning.setValue(self.config.CPU_WARNING)
        self.enable_profiling.setChecked(self.config.ENABLE_PROFILING)
    
    def _apply_settings(self):
        """Apply UI settings to config."""
        # MIDI
        self.config.VELOCITY_SENSITIVITY = self.velocity_sensitivity.value()
        self.config.NOTE_MIN = self.note_min.value()
        self.config.NOTE_MAX = self.note_max.value()
        self.config.MORPH_CC = self.morph_cc.value()
        self.config.MIDI_CHANNEL = self.midi_channel.value()
        
        # Audio
        self.config.AUDIO_SAMPLE_RATE = int(self.sample_rate.currentText())
        self.config.AUDIO_CHUNK_SIZE = int(self.chunk_size.currentText())
        self.config.AUDIO_ONSET_THRESHOLD = self.onset_threshold.value()
        self.config.AUDIO_COLOR_STRENGTH = self.audio_color_strength.value()
        
        # Visual
        self.config.MESH_RESOLUTION = self.mesh_resolution.value()
        self.config.COLOR_SATURATION = self.color_saturation.value()
        self.config.COLOR_BRIGHTNESS = self.color_brightness.value()
        self.config.MORPH_SPEED = self.morph_speed.value()
        
        # Performance
        self.config.TARGET_FPS = self.target_fps.value()
        self.config.MEMORY_WARNING = self.memory_warning.value()
        self.config.CPU_WARNING = self.cpu_warning.value()
        self.config.ENABLE_PROFILING = self.enable_profiling.isChecked()
        
        self.settings_changed.emit()
        print("✓ Configuration updated")
    
    def _test_settings(self):
        """Test current settings."""
        messages = []
        
        # Validate MIDI settings
        if self.note_min.value() >= self.note_max.value():
            messages.append("❌ Note range invalid: min >= max")
        else:
            messages.append("✓ Note range valid")
        
        # Validate audio settings
        sample_rate = int(self.sample_rate.currentText())
        if sample_rate in [22050, 44100, 48000, 96000]:
            messages.append("✓ Sample rate supported")
        else:
            messages.append("⚠ Sample rate may not be supported")
        
        # Performance checks
        target_fps = self.target_fps.value()
        if target_fps < 30:
            messages.append("⚠ Low target FPS may affect responsiveness")
        else:
            messages.append("✓ Target FPS appropriate")
        
        QMessageBox.information(self, "Settings Test", "\n".join(messages))
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        default_config = Config()
        self.config = default_config
        self._load_current_config()
        print("Settings reset to defaults")

# =============================================================================
# Main Application Window (Full Featured)
# =============================================================================

class FullFeaturedMorphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Visualizer - Full Featured")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "FullFeatured")
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "cube"
        self.audio_enabled = False
        self.audio_color_influence = 0.0
        
        # Initialize components
        self.profiler = PerformanceProfiler(self.config) if PERFORMANCE_MONITORING else None
        self.midi_handler = EnhancedMidiHandler(self.config) if MIDI_AVAILABLE else None
        self.audio_analyzer = AdvancedAudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        self.scene_manager = None
        
        # UI components
        self.config_dialog = None
        
        # Initialize visualization and UI
        print("Initializing full-featured MIDI morphing visualizer...")
        self._initialize_visualization()
        self._setup_ui()
        self._setup_menu()
        self._setup_connections()
        
        # Start components
        if self.midi_handler:
            self.midi_handler.start()
        
        # Timers
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(self.config.CLEANUP_INTERVAL * 1000)
        
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._frame_update)
        self.render_timer.start(int(1000 / self.config.TARGET_FPS))
        
        print("✅ Full-featured application initialized!")
    
    def _initialize_visualization(self):
        try:
            print("Creating meshes for full-featured version...")
            self.initial_meshes = create_perfectly_matched_meshes(self.config.MESH_RESOLUTION)
            
            if len(self.initial_meshes) >= 2:
                print(f"✓ Created {len(self.initial_meshes)} perfectly matched meshes")
            else:
                print("⚠ Limited mesh set available")
                
        except Exception as e:
            print(f"Mesh creation error: {e}")
            self.initial_meshes = {'sphere': pv.Sphere()}
    
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        # Status bar with performance info
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        if self.profiler:
            self.fps_label = QLabel("FPS: --")
            self.memory_label = QLabel("Memory: --")
            self.status_bar.addPermanentWidget(self.fps_label)
            self.status_bar.addPermanentWidget(self.memory_label)
        
        # 3D Visualization
        self.plotter_widget = QtInteractor(self.central_widget)
        layout.addWidget(self.plotter_widget)
        
        # Initialize scene manager
        self.scene_manager = SceneManager(self.initial_meshes, self.plotter_widget)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Left controls
        left_controls = QVBoxLayout()
        
        left_controls.addWidget(QLabel("Global Morph Target:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self.initial_meshes.keys()))
        if 'cube' in self.initial_meshes:
            self.target_combo.setCurrentText('cube')
        left_controls.addWidget(self.target_combo)
        
        left_controls.addWidget(QLabel("Global Morph Amount:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        left_controls.addWidget(self.morph_slider)
        
        controls_layout.addLayout(left_controls)
        
        # Right controls
        right_controls = QVBoxLayout()
        
        if AUDIO_AVAILABLE:
            self.audio_check = QCheckBox("Enable Audio Analysis")
            right_controls.addWidget(self.audio_check)
        
        if MIDI_AVAILABLE:
            self.midi_status_label = QLabel("MIDI: Connecting...")
            right_controls.addWidget(self.midi_status_label)
            
            self.midi_reconnect_button = QPushButton("Reconnect MIDI")
            right_controls.addWidget(self.midi_reconnect_button)
        
        self.config_button = QPushButton("Advanced Settings")
        right_controls.addWidget(self.config_button)
        
        controls_layout.addLayout(right_controls)
        layout.addLayout(controls_layout)
        
        # Status displays
        status_layout = QHBoxLayout()
        
        # Scene info
        scene_info = QVBoxLayout()
        self.scene_summary_label = QLabel("Scene: Multiple objects with note range mapping")
        scene_info.addWidget(self.scene_summary_label)
        
        self.active_notes_label = QLabel("Active Notes: None")
        scene_info.addWidget(self.active_notes_label)
        
        status_layout.addLayout(scene_info)
        
        # Audio info
        if AUDIO_AVAILABLE:
            audio_info = QVBoxLayout()
            self.audio_status_label = QLabel("Audio: Disabled")
            audio_info.addWidget(self.audio_status_label)
            
            self.spectral_info_label = QLabel("Spectral: --")
            audio_info.addWidget(self.spectral_info_label)
            
            status_layout.addLayout(audio_info)
        
        layout.addLayout(status_layout)
        
        # Clear button
        clear_button = QPushButton("Clear All Notes")
        clear_button.clicked.connect(self._clear_all_notes)
        layout.addWidget(clear_button)
        
        # Reset camera
        self.plotter_widget.reset_camera()
        
        vertex_count = list(self.initial_meshes.values())[0].n_points
        self.status_bar.showMessage(f"Full-Featured MIDI Morphing Ready - Scene Manager Active ({vertex_count} vertices per shape)")
    
    def _setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        config_action = QAction("Advanced Settings...", self)
        config_action.triggered.connect(self._show_config_dialog)
        config_action.setShortcut("Ctrl+,")
        file_menu.addAction(config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        scene_config_action = QAction("Scene Configuration...", self)
        scene_config_action.triggered.connect(self._show_scene_config)
        view_menu.addAction(scene_config_action)
        
        # Performance menu
        if self.profiler:
            perf_menu = menubar.addMenu("Performance")
            
            show_monitor_action = QAction("Show Performance Monitor", self)
            show_monitor_action.triggered.connect(self._show_performance_monitor)
            perf_menu.addAction(show_monitor_action)
    
    def _setup_connections(self):
        # UI connections
        self.morph_slider.valueChanged.connect(self._on_global_morph_change)
        self.target_combo.currentTextChanged.connect(self._on_target_change)
        self.config_button.clicked.connect(self._show_config_dialog)
        
        if MIDI_AVAILABLE and self.midi_handler:
            self.midi_reconnect_button.clicked.connect(self._reconnect_midi)
            self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
            self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
            self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if AUDIO_AVAILABLE and self.audio_analyzer:
            self.audio_check.toggled.connect(self._toggle_audio)
            self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
            self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
            self.audio_analyzer.spectral_centroid_signal.connect(self._on_spectral_centroid)
            self.audio_analyzer.spectral_rolloff_signal.connect(self._on_spectral_rolloff)
        
        if self.profiler:
            self.profiler.fps_updated.connect(self._update_fps_display)
            self.profiler.memory_updated.connect(self._update_memory_display)
            self.profiler.cpu_updated.connect(self._update_cpu_display)
            self.profiler.performance_warning.connect(self._show_performance_warning)
    
    def _on_global_morph_change(self, value):
        """Apply global morphing to all objects in the scene."""
        alpha = value / 100.0
        target_shape = self.target_combo.currentText()
        
        if self.scene_manager and target_shape in self.initial_meshes:
            self.scene_manager.apply_global_morphing(target_shape, alpha)
            self.status_bar.showMessage(f"Global morph: → {target_shape} ({value}%)", 1000)
    
    def _on_target_change(self, target_key):
        """Update global morph target."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self._on_global_morph_change(self.morph_slider.value())
    
    def _toggle_audio(self, enabled):
        """Toggle advanced audio analysis."""
        if enabled and self.audio_analyzer:
            if self.audio_analyzer.start():
                self.audio_enabled = True
                self.audio_status_label.setText("Audio: Active (Advanced)")
            else:
                self.audio_check.setChecked(False)
                self.audio_status_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_enabled = False
            self.audio_status_label.setText("Audio: Disabled")
    
    def _reconnect_midi(self):
        """Reconnect MIDI with enhanced handler."""
        if self.midi_handler:
            self.midi_handler.stop()
            QTimer.singleShot(100, self._do_midi_reconnect)
    
    def _do_midi_reconnect(self):
        if self.midi_handler and self.midi_handler.start():
            self.midi_status_label.setText("MIDI: Connected (Enhanced)")
            self.status_bar.showMessage("MIDI reconnected successfully", 3000)
        else:
            self.midi_status_label.setText("MIDI: Connection failed")
            self.status_bar.showMessage("MIDI reconnection failed", 3000)
    
    def _on_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note with scene manager routing."""
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, velocity, True, channel)
                
                if affected_objects:
                    print(f"Note ON: {note} (vel: {velocity:.2f}, ch: {channel}) -> {', '.join(affected_objects)}")
                    self._update_scene_display()
                else:
                    print(f"Note ON: {note} - No objects in range")
            
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note, channel):
        """Handle MIDI note off with scene manager."""
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, 0, False, channel)
                
                if affected_objects:
                    print(f"Note OFF: {note} (ch: {channel}) -> {', '.join(affected_objects)}")
                    self._update_scene_display()
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value, channel):
        """Handle MIDI CC with enhanced mapping."""
        if cc_number == self.config.MORPH_CC:  # Default CC1 (mod wheel)
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
            print(f"CC{cc_number}: {value:.2f} -> Global morph: {slider_value}%")
        
        # Add more CC mappings here in the future
        # elif cc_number == 2:  # CC2 could control color saturation
        # elif cc_number == 3:  # CC3 could control morph speed
    
    def _on_audio_onset(self, amplitude):
        """Handle audio onset with enhanced effects."""
        try:
            if not self.audio_enabled:
                return
            
            # Global flash effect across all scene objects
            self.audio_color_influence = min(amplitude * self.config.AUDIO_COLOR_STRENGTH, 1.0)
            
            # Apply flash to all objects in scene
            if self.scene_manager:
                for obj_id, visual_obj in self.scene_manager.objects.items():
                    # Temporarily brighten the object
                    visual_obj.opacity = min(visual_obj.opacity + self.audio_color_influence * 0.3, 1.0)
                    self.scene_manager._update_object_visual(obj_id)
            
            # Fade out flash
            QTimer.singleShot(self.config.FLASH_DURATION, self._fade_audio_influence)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude for reactive effects."""
        try:
            if amplitude > 0.1:
                # Apply audio-driven morphing
                audio_morph = min(amplitude * self.config.AUDIO_MORPH_STRENGTH, 0.2)
                base_morph = self.morph_slider.value() / 100.0
                combined_morph = np.clip(base_morph + audio_morph, 0, 1)
                
                # Apply to scene without changing slider
                if self.scene_manager:
                    target_shape = self.target_combo.currentText()
                    self.scene_manager.apply_global_morphing(target_shape, combined_morph)
            
            self.audio_status_label.setText(f"Audio: Amplitude {amplitude:.3f}")
            
        except Exception as e:
            print(f"Error handling audio amplitude: {e}")
    
    def _on_spectral_centroid(self, centroid):
        """Handle spectral centroid for advanced color mapping."""
        try:
            # Map spectral centroid to global color shift
            normalized_centroid = np.clip(
                (centroid - self.config.AUDIO_FREQUENCY_RANGE[0]) / 
                (self.config.AUDIO_FREQUENCY_RANGE[1] - self.config.AUDIO_FREQUENCY_RANGE[0]), 
                0, 1
            )
            
            # Could use this to shift hue of all objects
            # Implementation depends on specific visual goals
            
            self.spectral_info_label.setText(f"Spectral: Centroid {centroid:.0f}Hz")
            
        except Exception as e:
            print(f"Error handling spectral centroid: {e}")
    
    def _on_spectral_rolloff(self, rolloff):
        """Handle spectral rolloff for brightness control."""
        try:
            # Map rolloff to brightness/opacity
            normalized_rolloff = np.clip(
                (rolloff - self.config.AUDIO_FREQUENCY_RANGE[0]) / 
                (self.config.AUDIO_FREQUENCY_RANGE[1] - self.config.AUDIO_FREQUENCY_RANGE[0]), 
                0, 1
            )
            
            # Could use this to control global brightness
            # Implementation depends on specific visual goals
            
        except Exception as e:
            print(f"Error handling spectral rolloff: {e}")
    
    def _fade_audio_influence(self):
        """Fade out audio color influence effects."""
        self.audio_color_influence *= 0.3
        if self.audio_color_influence > 0.01:
            # Continue fading
            QTimer.singleShot(50, self._fade_audio_influence)
        else:
            self.audio_color_influence = 0.0
            # Reset object opacities
            if self.scene_manager:
                for obj_id, visual_obj in self.scene_manager.objects.items():
                    visual_obj._update_composite_properties()
                    self.scene_manager._update_object_visual(obj_id)
    
    def _update_scene_display(self):
        """Update scene information display."""
        if self.scene_manager:
            summary = self.scene_manager.get_scene_summary()
            active_objects = summary['active_objects']
            total_notes = summary['total_active_notes']
            
            if total_notes > 0:
                note_info = []
                for obj_id, obj_info in summary['objects'].items():
                    if obj_info['active_notes'] > 0:
                        note_info.append(f"{obj_id}({obj_info['active_notes']})")
                
                self.active_notes_label.setText(f"Active: {', '.join(note_info)} | Total: {total_notes}")
                self.scene_summary_label.setText(f"Scene: {active_objects}/{summary['total_objects']} objects active")
            else:
                self.active_notes_label.setText("Active Notes: None")
                self.scene_summary_label.setText(f"Scene: {summary['total_objects']} objects ready")
    
    def _clear_all_notes(self):
        """Clear all notes from scene manager."""
        if self.scene_manager:
            self.scene_manager.clear_all_notes()
            self._update_scene_display()
    
    def _cleanup_expired_elements(self):
        """Clean up expired notes and update performance."""
        if self.scene_manager:
            self.scene_manager.cleanup_expired_notes(self.config.NOTE_TIMEOUT)
            self._update_scene_display()
    
    def _frame_update(self):
        """Called every frame for performance monitoring."""
        if self.profiler:
            self.profiler.record_frame()
    
    def _show_config_dialog(self):
        """Show advanced configuration dialog."""
        if self.config_dialog is None:
            self.config_dialog = AdvancedConfigDialog(self.config, self)
            self.config_dialog.settings_changed.connect(self._on_config_changed)
        
        self.config_dialog.show()
        self.config_dialog.raise_()
        self.config_dialog.activateWindow()
    
    def _on_config_changed(self):
        """Handle configuration changes."""
        try:
            # Update timers
            self.cleanup_timer.setInterval(self.config.CLEANUP_INTERVAL * 1000)
            self.render_timer.setInterval(int(1000 / self.config.TARGET_FPS))
            
            # Update profiler thresholds
            if self.profiler:
                # Would update profiler settings here
                pass
            
            # Restart audio analyzer if settings changed
            if self.audio_analyzer and self.audio_enabled:
                self.audio_analyzer.stop()
                QTimer.singleShot(200, lambda: self.audio_analyzer.start())
            
            self.status_bar.showMessage("Configuration updated successfully", 3000)
            
        except Exception as e:
            print(f"Error applying configuration changes: {e}")
            self.status_bar.showMessage(f"Error updating configuration: {e}", 5000)
    
    def _show_scene_config(self):
        """Show scene configuration dialog."""
        QMessageBox.information(self, "Scene Configuration", 
                              "Scene configuration dialog not yet implemented.\n"
                              "Current scene uses default note range mappings:\n\n"
                              "• Bass (C1-B2): Left sphere\n"
                              "• Melody (C3-C5): Center icosahedron\n"
                              "• Treble (C#5-C7): Right cube\n"
                              "• High (C#7-G9): Top cone")
    
    def _show_performance_monitor(self):
        """Show performance monitoring dialog."""
        if self.profiler:
            QMessageBox.information(self, "Performance Monitor", 
                                  "Performance monitoring is active.\n"
                                  "Check the status bar for real-time FPS and memory usage.\n"
                                  "Advanced performance dialog not yet implemented.")
        else:
            QMessageBox.warning(self, "Performance Monitor", 
                              "Performance monitoring not available.\n"
                              "Install psutil for performance monitoring:\n"
                              "pip install psutil")
    
    def _update_fps_display(self, fps):
        """Update FPS display in status bar."""
        if hasattr(self, 'fps_label'):
            color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
            self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _update_memory_display(self, memory_mb, memory_percent):
        """Update memory display in status bar."""
        if hasattr(self, 'memory_label'):
            color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
            self.memory_label.setText(f"<font color='{color}'>Mem: {memory_percent:.1f}%</font>")
    
    def _update_cpu_display(self, cpu_percent):
        """Update CPU display (could add to status bar)."""
        pass  # Could add CPU indicator to status bar
    
    def _show_performance_warning(self, warning):
        """Show performance warning in status bar."""
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)
    
    def closeEvent(self, event):
        """Clean shutdown of full-featured application."""
        print("Shutting down full-featured application...")
        
        try:
            # Stop all systems
            if self.midi_handler:
                print("Stopping MIDI handler...")
                self.midi_handler.stop()
        except Exception as e:
            print(f"Error stopping MIDI handler: {e}")
        
        try:
            if self.audio_analyzer:
                print("Stopping audio analyzer...")
                self.audio_analyzer.stop()
        except Exception as e:
            print(f"Error stopping audio analyzer: {e}")
        
        try:
            if self.profiler:
                print("Stopping performance monitoring...")
                self.profiler.stop_monitoring()
        except Exception as e:
            print(f"Error stopping profiler: {e}")
        
        try:
            # Stop timers
            self.cleanup_timer.stop()
            self.render_timer.stop()
        except Exception as e:
            print(f"Error stopping timers: {e}")
        
        try:
            # Close dialogs
            if self.config_dialog:
                self.config_dialog.close()
        except Exception as e:
            print(f"Error closing dialogs: {e}")
        
        print("Full-featured application shutdown complete")
        event.accept()

def main():
    print("=== Full-Featured MIDI Morphing Visualizer ===")
    print("This version includes:")
    print("• Scene Manager with multiple objects")
    print("• Note range mapping (bass, melody, treble, high)")
    print("• Advanced audio analysis with spectral features")
    print("• Performance monitoring and profiling")
    print("• Enhanced MIDI handling with channel filtering")
    print("• Advanced configuration dialogs")
    print("• Global morphing effects")
    print("")
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Full Featured")
    
    try:
        window = FullFeaturedMorphingWindow()
        window.resize(1400, 900)
        window.show()
        
        print("🎵 Full-Featured MIDI Morphing Visualizer Ready! 🎵")
        print("\nFeatures available:")
        print("• Multiple objects respond to different note ranges")
        print("• Global morphing slider affects all objects")
        print("• Advanced audio analysis with spectral features")
        print("• Performance monitoring in status bar")
        print("• Enhanced MIDI with channel filtering")
        print("• Advanced settings dialog (Advanced Settings button)")
        print("• Menu system with configuration options")
        print("")
        print("Try playing notes in different octaves to see different objects light up!")
        
        return app.exec()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Complete MIDI Morphing Visualizer - Full Featured Version
Combines working morphing with all advanced features:
- Scene Manager with multiple objects
- Note range mapping
- Performance monitoring
- Configuration dialogs
- Advanced audio analysis
- OSC output
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core dependencies
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
    from PySide6.QtGui import QAction, QFont
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✓ Core GUI dependencies available")
except ImportError as e:
    print(f"✗ Missing core dependencies: {e}")
    sys.exit(1)

# Optional dependencies
MIDI_AVAILABLE = False
try:
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✓ Pygame MIDI support available")
except ImportError:
    print("⚠ MIDI support not available")

AUDIO_AVAILABLE = False
try:
    import pyaudio
    import librosa
    AUDIO_AVAILABLE = True
    print("✓ Audio analysis available")
except ImportError:
    print("⚠ Audio analysis not available")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✓ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠ Performance monitoring not available")

# =============================================================================
# Configuration Classes
# =============================================================================

class MidiConstants:
    """MIDI protocol constants."""
    NOTE_OFF_START = 128
    NOTE_OFF_END = 143
    NOTE_ON_START = 144
    NOTE_ON_END = 159
    CC_START = 176
    CC_END = 191
    MIN_VALUE = 0
    MAX_VALUE = 127
    MODWHEEL_CC = 1

class Config:
    """Comprehensive configuration class."""
    def __init__(self):
        # Core settings
        self.MESH_RESOLUTION = 25
        self.MIDI_PORT = None
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHUNK_SIZE = 512
        self.AUDIO_ONSET_THRESHOLD = 1.5
        
        # Audio settings
        self.AUDIO_ENABLED = True
        self.AUDIO_DEVICE_INDEX = None
        self.AUDIO_CHANNELS = 1
        self.AUDIO_FFT_SIZE = 2048
        self.AUDIO_HOP_LENGTH = 512
        self.AUDIO_FREQUENCY_RANGE = (80, 8000)
        self.AUDIO_SPECTRAL_ROLLOFF = 0.85
        self.AUDIO_COLOR_STRENGTH = 1.0
        self.AUDIO_MORPH_STRENGTH = 0.2
        
        # MIDI settings
        self.VELOCITY_SENSITIVITY = 1.0
        self.NOTE_MIN = 0
        self.NOTE_MAX = 127
        self.MORPH_CC = 1
        self.NOTE_TIMEOUT = 60
        self.MIDI_CHANNEL = 0
        self.MIDI_AUTO_RECONNECT = True
        
        # Visualization settings
        self.COLOR_SATURATION = 0.8
        self.COLOR_BRIGHTNESS = 1.0
        self.MORPH_SPEED = 1.0
        self.COLOR_TRANSITION_SPEED = 0.5
        self.FLASH_DURATION = 150
        self.SMOOTH_SHADING = True
        self.WIREFRAME_MODE = False
        self.AUTO_ROTATE = False
        self.ROTATION_SPEED = 1.0
        self.DEFAULT_COLOR = [0.8, 0.8, 0.8]
        
        # Performance settings
        self.TARGET_FPS = 60
        self.VSYNC = True
        self.RENDER_QUALITY = "High"
        self.MEMORY_LIMIT = 1000
        self.CLEANUP_INTERVAL = 5
        self.FPS_WARNING = 30
        self.MEMORY_WARNING = 80
        self.CPU_WARNING = 85
        self.ENABLE_PROFILING = True
        self.VERBOSE_LOGGING = False
        self.SHOW_DEBUG_INFO = False
        
        # OSC settings
        self.OSC_IP = "127.0.0.1"
        self.OSC_PORT = 5005
        self.ENABLE_OSC = False

# =============================================================================
# Geometry and Mesh Functions (Working Version)
# =============================================================================

def create_perfectly_matched_meshes(resolution=25):
    """Create meshes with identical vertex counts for perfect morphing."""
    try:
        print(f"Creating perfectly matched meshes with resolution {resolution}...")
        
        # Create base sphere as reference
        sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
        target_points = sphere.n_points
        print(f"Target vertex count: {target_points}")
        
        meshes = {'sphere': sphere}
        
        # Create other shapes and force vertex count match
        shapes_to_create = ['cube', 'cone', 'cylinder']
        
        for shape_name in shapes_to_create:
            try:
                if shape_name == 'cube':
                    base_mesh = pv.Cube()
                elif shape_name == 'cone':
                    base_mesh = pv.Cone(resolution=resolution)
                elif shape_name == 'cylinder':
                    base_mesh = pv.Cylinder(resolution=resolution)
                else:
                    continue
                
                matched_mesh = force_vertex_count_match(base_mesh, target_points)
                if matched_mesh is not None:
                    meshes[shape_name] = matched_mesh
                    print(f"✓ {shape_name}: {matched_mesh.n_points} vertices")
                    
            except Exception as e:
                print(f"✗ Error creating {shape_name}: {e}")
        
        # Create torus by deforming sphere
        try:
            torus = create_torus_from_sphere(sphere)
            if torus.n_points == target_points:
                meshes['torus'] = torus
                print(f"✓ torus: {torus.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating torus: {e}")
        
        # Create icosahedron
        try:
            icosahedron = create_icosahedron_from_sphere(sphere)
            if icosahedron.n_points == target_points:
                meshes['icosahedron'] = icosahedron
                print(f"✓ icosahedron: {icosahedron.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating icosahedron: {e}")
        
        # Final verification
        vertex_counts = [mesh.n_points for mesh in meshes.values()]
        if len(set(vertex_counts)) == 1:
            print(f"✅ SUCCESS: All {len(meshes)} meshes have IDENTICAL vertex counts: {vertex_counts[0]}")
        else:
            print(f"⚠ Mixed vertex counts, keeping matched ones only")
            matched_meshes = {name: mesh for name, mesh in meshes.items() 
                            if mesh.n_points == target_points}
            meshes = matched_meshes
        
        return meshes
        
    except Exception as e:
        print(f"Error in mesh creation: {e}")
        return {'sphere': pv.Sphere()}

def force_vertex_count_match(mesh, target_count):
    """Force a mesh to have exactly target_count vertices."""
    try:
        current_count = mesh.n_points
        
        if current_count == target_count:
            return mesh
        
        # Ensure triangulation
        if hasattr(mesh, 'triangulate'):
            mesh = mesh.triangulate()
        
        # Subdivide if needed
        if current_count < target_count:
            while mesh.n_points < target_count * 0.9:
                try:
                    mesh = mesh.subdivide(1)
                    if mesh.n_points >= target_count * 2:
                        break
                except Exception as e:
                    print(f"Subdivision failed: {e}")
                    break
        
        # Decimate if needed
        if mesh.n_points > target_count:
            ratio = target_count / mesh.n_points
            try:
                mesh = mesh.decimate(1 - ratio)
            except Exception as e:
                print(f"Decimation failed: {e}")
                return None
        
        # Accept close matches
        if abs(mesh.n_points - target_count) / target_count < 0.1:
            return mesh
        
        return None
        
    except Exception as e:
        print(f"Force vertex match failed: {e}")
        return None

def create_torus_from_sphere(sphere):
    """Create torus by deforming sphere points."""
    points = sphere.points.copy()
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    
    major_radius = 0.7
    minor_radius = 0.3
    
    new_r = major_radius + minor_radius * np.cos(z * np.pi * 2)
    new_z = minor_radius * np.sin(z * np.pi * 2)
    
    torus_points = np.column_stack([
        new_r * np.cos(theta),
        new_r * np.sin(theta),
        new_z
    ])
    
    torus = sphere.copy()
    torus.points = torus_points
    return torus

def create_icosahedron_from_sphere(sphere):
    """Create icosahedron by projecting sphere to icosahedral faces."""
    points = sphere.points.copy()
    
    # Simple icosahedral approximation by quantizing directions
    normals = points / np.linalg.norm(points, axis=1)[:, np.newaxis]
    quantized = np.round(normals * 4) / 4
    quantized = quantized / np.linalg.norm(quantized, axis=1)[:, np.newaxis]
    
    icosahedron = sphere.copy()
    icosahedron.points = quantized
    return icosahedron

def blend_meshes(meshes, source_key, target_key, alpha):
    """Perfect mesh blending for identical vertex count meshes."""
    if source_key not in meshes or target_key not in meshes:
        raise ValueError(f"Mesh keys not found: {source_key}, {target_key}")
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    if source_mesh.n_points != target_mesh.n_points:
        raise ValueError(f"Vertex count mismatch: {source_mesh.n_points} vs {target_mesh.n_points}")
    
    source_points = source_mesh.points
    target_points = target_mesh.points
    return (1 - alpha) * source_points + alpha * target_points

# =============================================================================
# Scene Management
# =============================================================================

class LayerBlendMode(Enum):
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"

@dataclass
class NoteRange:
    min_note: int
    max_note: int
    name: str = ""
    channel: Optional[int] = None
    
    def contains(self, note: int, channel: int = None) -> bool:
        note_in_range = self.min_note <= note <= self.max_note
        channel_match = self.channel is None or self.channel == channel
        return note_in_range and channel_match

@dataclass
class VisualObject:
    id: str
    shape_type: str
    note_range: NoteRange
    position: np.ndarray
    scale: float = 1.0
    color: np.ndarray = None
    opacity: float = 1.0
    current_morph_target: str = ""
    morph_amount: float = 0.0
    active_notes: Dict[int, dict] = None
    last_activity: float = 0.0
    blend_mode: LayerBlendMode = LayerBlendMode.NORMAL
    depth_layer: int = 0
    
    def __post_init__(self):
        if self.color is None:
            self.color = np.array([0.8, 0.8, 0.8])
        if self.active_notes is None:
            self.active_notes = {}
        self.last_activity = time.time()
    
    def update_from_midi(self, note: int, velocity: float, note_on: bool = True):
        if note_on:
            range_span = self.note_range.max_note - self.note_range.min_note
            normalized_note = (note - self.note_range.min_note) / range_span if range_span > 0 else 0.5
            
            hue = normalized_note
            saturation = 0.8 + (velocity * 0.2)
            brightness = 0.6 + (velocity * 0.4)
            
            color = colorsys.hsv_to_rgb(hue, saturation, brightness)
            
            self.active_notes[note] = {
                'color': color,
                'velocity': velocity,
                'timestamp': time.time()
            }
        else:
            if note in self.active_notes:
                del self.active_notes[note]
        
        self.last_activity = time.time()
        self._update_composite_properties()
    
    def _update_composite_properties(self):
        if not self.active_notes:
            self.color = np.array([0.5, 0.5, 0.5])
            self.opacity = 0.3
            return
        
        if len(self.active_notes) == 1:
            note_info = next(iter(self.active_notes.values()))
            self.color = np.array(note_info['color'])
            self.opacity = 0.7 + (note_info['velocity'] * 0.3)
        else:
            total_color = np.array([0.0, 0.0, 0.0])
            total_weight = 0.0
            
            for note_info in self.active_notes.values():
                weight = note_info['velocity']
                color = np.array(note_info['color'])
                total_color += color * weight
                total_weight += weight
            
            if total_weight > 0:
                self.color = total_color / total_weight
                self.opacity = min(0.7 + (total_weight / len(self.active_notes) * 0.3), 1.0)

class SceneManager:
    """Advanced scene manager with multiple objects and note range mapping."""
    
    def __init__(self, initial_meshes, plotter_widget):
        self.initial_meshes = initial_meshes
        self.plotter_widget = plotter_widget
        self.objects: Dict[str, VisualObject] = {}
        self.actors: Dict[str, object] = {}
        self.meshes: Dict[str, object] = {}
        
        # Setup default note range mappings
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
        """Setup default note range mappings for different octaves."""
        mappings = [
            {
                'id': 'bass',
                'note_range': NoteRange(21, 47, "Bass (C1-B2)"),
                'shape_type': 'sphere',
                'position': np.array([-2.0, 0.0, 0.0]),
                'scale': 1.5,
                'depth_layer': 1
            },
            {
                'id': 'melody',
                'note_range': NoteRange(48, 72, "Melody (C3-C5)"),
                'shape_type': 'icosahedron' if 'icosahedron' in self.initial_meshes else 'cube',
                'position': np.array([0.0, 0.0, 0.0]),
                'scale': 1.0,
                'depth_layer': 2
            },
            {
                'id': 'treble',
                'note_range': NoteRange(73, 96, "Treble (C#5-C7)"),
                'shape_type': 'cube',
                'position': np.array([2.0, 0.0, 0.0]),
                'scale': 0.7,
                'depth_layer': 3
            },
            {
                'id': 'sparkle',
                'note_range': NoteRange(97, 127, "High (C#7-G9)"),
                'shape_type': 'cone',
                'position': np.array([0.0, 2.0, 0.0]),
                'scale': 0.5,
                'depth_layer': 4,
                'blend_mode': LayerBlendMode.ADDITIVE
            }
        ]
        
        for mapping in mappings:
            # Only create if the shape type exists
            if mapping['shape_type'] in self.initial_meshes:
                self.add_object(**mapping)
    
    def add_object(self, id: str, note_range: NoteRange, shape_type: str, 
                   position: np.ndarray = None, scale: float = 1.0, 
                   depth_layer: int = 0, blend_mode: LayerBlendMode = LayerBlendMode.NORMAL):
        
        if position is None:
            position = np.array([0.0, 0.0, 0.0])
        
        visual_obj = VisualObject(
            id=id,
            shape_type=shape_type,
            note_range=note_range,
            position=position,
            scale=scale,
            depth_layer=depth_layer,
            blend_mode=blend_mode
        )
        
        self.objects[id] = visual_obj
        
        if self.plotter_widget is not None and shape_type in self.initial_meshes:
            mesh = self.initial_meshes[shape_type].copy()
            mesh.points = mesh.points * scale + position
            
            actor_props = {
                'color': visual_obj.color,
                'opacity': visual_obj.opacity,
                'smooth_shading': True
            }
            
            if blend_mode == LayerBlendMode.ADDITIVE:
                actor_props['opacity'] = 0.7
            
            actor = self.plotter_widget.add_mesh(mesh, **actor_props)
            
            self.actors[id] = actor
            self.meshes[id] = mesh
            
            print(f"Added object '{id}' for notes {note_range.min_note}-{note_range.max_note}")
        
        return visual_obj
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        affected_objects = []
        
        for obj_id, visual_obj in self.objects.items():
            if visual_obj.note_range.contains(note, channel):
                visual_obj.update_from_midi(note, velocity, note_on)
                affected_objects.append(obj_id)
        
        for obj_id in affected_objects:
            self._update_object_visual(obj_id)
        
        return affected_objects
    
    def _update_object_visual(self, obj_id: str):
        if obj_id not in self.objects or obj_id not in self.actors:
            return
        
        visual_obj = self.objects[obj_id]
        actor = self.actors[obj_id]
        mesh = self.meshes[obj_id]
        
        self.plotter_widget.remove_actor(actor)
        
        actor_props = {
            'color': visual_obj.color,
            'opacity': visual_obj.opacity,
            'smooth_shading': True
        }
        
        if visual_obj.blend_mode == LayerBlendMode.ADDITIVE:
            actor_props['opacity'] *= 0.8
        
        new_actor = self.plotter_widget.add_mesh(mesh, **actor_props)
        self.actors[obj_id] = new_actor
    
    def apply_global_morphing(self, target_shape: str, alpha: float):
        """Apply morphing to all objects in the scene."""
        for obj_id, visual_obj in self.objects.items():
            if obj_id in self.meshes and target_shape in self.initial_meshes:
                try:
                    # Get current shape type
                    current_shape = visual_obj.shape_type
                    
                    # Blend between current and target
                    blended_points = blend_meshes(
                        self.initial_meshes,
                        current_shape,
                        target_shape,
                        alpha
                    )
                    
                    # Apply scale and position
                    transformed_points = blended_points * visual_obj.scale + visual_obj.position
                    
                    # Update mesh
                    self.meshes[obj_id].points = transformed_points
                    
                    # Update morph amount
                    visual_obj.morph_amount = alpha
                    visual_obj.current_morph_target = target_shape
                    
                except Exception as e:
                    print(f"Error morphing object {obj_id}: {e}")
        
        # Trigger render
        if self.plotter_widget:
            self.plotter_widget.render()
    
    def cleanup_expired_notes(self, timeout: float = 60.0):
        current_time = time.time()
        for visual_obj in self.objects.values():
            expired_notes = [
                note for note, info in visual_obj.active_notes.items()
                if current_time - info['timestamp'] > timeout
            ]
            
            for note in expired_notes:
                del visual_obj.active_notes[note]
            
            if expired_notes:
                visual_obj._update_composite_properties()
        
        for obj_id in self.objects.keys():
            self._update_object_visual(obj_id)
    
    def clear_all_notes(self):
        for visual_obj in self.objects.values():
            visual_obj.active_notes.clear()
            visual_obj._update_composite_properties()
        
        for obj_id in self.objects.keys():
            self._update_object_visual(obj_id)
    
    def get_scene_summary(self) -> Dict:
        summary = {
            'total_objects': len(self.objects),
            'active_objects': sum(1 for obj in self.objects.values() if obj.active_notes),
            'total_active_notes': sum(len(obj.active_notes) for obj in self.objects.values()),
            'objects': {}
        }
        
        for obj_id, visual_obj in self.objects.items():
            summary['objects'][obj_id] = {
                'note_range': f"{visual_obj.note_range.min_note}-{visual_obj.note_range.max_note}",
                'active_notes': len(visual_obj.active_notes),
                'shape_type': visual_obj.shape_type,
                'blend_mode': visual_obj.blend_mode.value,
                'depth_layer': visual_obj.depth_layer
            }
        
        return summary

# =============================================================================
# Audio Analysis (Enhanced)
# =============================================================================

class AdvancedAudioAnalyzer(QObject):
    onset_detected_signal = Signal(float)
    amplitude_signal = Signal(float)
    spectral_centroid_signal = Signal(float)
    spectral_rolloff_signal = Signal(float)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.audio = None
        self.stream = None
        self.running = False
        self.thread = None
        self.is_active = False
        
        if AUDIO_AVAILABLE:
            self.sample_rate = config.AUDIO_SAMPLE_RATE
            self.chunk_size = config.AUDIO_CHUNK_SIZE
            self.fft_size = config.AUDIO_FFT_SIZE
            self.hop_length = config.AUDIO_HOP_LENGTH
            self.audio_queue = queue.Queue()
            self.audio_buffer = np.zeros(self.fft_size)
            self.windowing_function = np.hanning(self.chunk_size)
            self.previous_onset_strength = 0.0
    
    def start(self):
        if not AUDIO_AVAILABLE or self.is_active:
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find input device
            try:
                default_device = self.audio.get_default_input_device_info()
                device_index = default_device['index']
                print(f"Using audio device: {default_device['name']}")
            except Exception:
                device_index = self._find_best_input_device()
            
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.config.AUDIO_CHANNELS,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            
            self.running = True
            self.is_active = True
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            print("✓ Advanced audio analysis started")
            return True
            
        except Exception as e:
            print(f"✗ Failed to start audio analysis: {e}")
            return False
    
    def _find_best_input_device(self):
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            return None
        except Exception:
            return None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        try:
            if status:
                logger.warning(f"Audio stream status: {status}")
            
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Audio callback error: {e}")
            return (None, pyaudio.paAbort)
    
    def _analysis_loop(self):
        while self.running:
            try:
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                self._update_audio_buffer(audio_chunk)
                self._analyze_audio()
                
            except Exception as e:
                print(f"Audio analysis error: {e}")
    
    def _update_audio_buffer(self, new_chunk):
        try:
            windowed_chunk = new_chunk * self.windowing_function
            shift_amount = len(windowed_chunk)
            self.audio_buffer[:-shift_amount] = self.audio_buffer[shift_amount:]
            self.audio_buffer[-shift_amount:] = windowed_chunk
        except Exception as e:
            logger.error(f"Buffer update error: {e}")
    
    def _analyze_audio(self):
        try:
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return
            
            features = {}
            
            # Basic amplitude features
            features['rms'] = np.sqrt(np.mean(self.audio_buffer ** 2))
            features['peak_amplitude'] = np.max(np.abs(self.audio_buffer))
            
            # Spectral analysis
            fft = np.fft.rfft(self.audio_buffer)
            magnitude_spectrum = np.abs(fft)
            power_spectrum = magnitude_spectrum ** 2
            
            freqs = np.fft.rfftfreq(len(self.audio_buffer), 1/self.sample_rate)
            
            # Filter to frequency range of interest
            freq_mask = (freqs >= self.config.AUDIO_FREQUENCY_RANGE[0]) & \
                       (freqs <= self.config.AUDIO_FREQUENCY_RANGE[1])
            
            if np.any(freq_mask):
                filtered_power = power_spectrum[freq_mask]
                filtered_freqs = freqs[freq_mask]
                
                # Spectral centroid
                if np.sum(filtered_power) > 0:
                    features['spectral_centroid'] = np.sum(filtered_freqs * filtered_power) / np.sum(filtered_power)
                    self.spectral_centroid_signal.emit(features['spectral_centroid'])
                else:
                    features['spectral_centroid'] = 0.0
                
                # Spectral rolloff
                cumsum = np.cumsum(filtered_power)
                total_energy = cumsum[-1]
                if total_energy > 0:
                    rolloff_idx = np.where(cumsum >= self.config.AUDIO_SPECTRAL_ROLLOFF * total_energy)[0]
                    if len(rolloff_idx) > 0:
                        features['spectral_rolloff'] = filtered_freqs[rolloff_idx[0]]
                        self.spectral_rolloff_signal.emit(features['spectral_rolloff'])
            
            # Onset detection
            onset_strength = np.sum(np.diff(magnitude_spectrum) ** 2)
            onset_detected = onset_strength > self.
