import sys
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMenuBar,
    QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
from PySide6.QtGui import QAction
from pyvistaqt import QtInteractor
import pyvista as pv

from config import Config
from geometry import create_initial_meshes, blend_meshes
from performance_monitoring import PerformanceProfiler, PerformanceDialog, performance_monitor
from config_dialog import ConfigurationDialog
from scene_manager import SceneManager
from scene_config_dialog import SceneConfigurationDialog

# MIDI imports
try:
    import pygame
    import pygame.midi
    MIDI_AVAILABLE = True
    print("Using pygame for MIDI support")
except ImportError:
    MIDI_AVAILABLE = False
    print("pygame not available - MIDI disabled")

# Audio imports
try:
    import pyaudio
    AUDIO_AVAILABLE = True
    print("Audio analysis available")
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio libraries not available - audio analysis disabled")

logger = logging.getLogger(__name__)

class MidiHandler(QObject):
    note_on_signal = Signal(int, float)
    note_off_signal = Signal(int)
    cc_signal = Signal(int, float)
    
    def __init__(self):
        super().__init__()
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
            
            device_id = self._find_device(device_name)
            if device_id is None:
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"Connected to MIDI device: {device_name}")
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start MIDI: {e}")
            self._cleanup_midi()
            return False
    
    def _find_device(self, preferred_name=None):
        try:
            device_count = pygame.midi.get_count()
            
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
        
        if 144 <= status <= 159:  # Note On
            if data2 > 0:
                velocity = data2 / 127.0
                self.note_on_signal.emit(data1, velocity)
            else:
                self.note_off_signal.emit(data1)
        elif 128 <= status <= 143:  # Note Off
            self.note_off_signal.emit(data1)
        elif 176 <= status <= 191:  # Control Change
            cc_value = data2 / 127.0
            self.cc_signal.emit(data1, cc_value)
    
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
        print("Stopping MIDI handler...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self._cleanup_midi()
        print("MIDI handler stopped")

class SceneMorphingMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Interface - Scene Manager")
        
        # Initialize performance profiler
        self.profiler = PerformanceProfiler(self.config)
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.scene_manager = None
        self.performance_dialog = None
        self.config_dialog = None
        self.scene_config_dialog = None
        
        # Setup components
        self.midi_handler = MidiHandler()
        
        # Initialize everything
        self._initialize_visualization()
        self._setup_ui()
        self._setup_menu()
        self._setup_midi()
        self._setup_performance_monitoring()
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(5000)
        
        # Frame timing for FPS calculation
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._frame_update)
        self.render_timer.start(16)
    
    def _initialize_visualization(self):
        # Create meshes first
        self.initial_meshes = create_initial_meshes(self.config.MESH_RESOLUTION)
        logger.info(f"Created {len(self.initial_meshes)} meshes")
        
        # Initialize scene manager (plotter will be set later)
        self.scene_manager = SceneManager(self.initial_meshes, None)
        print("Scene manager initialized")
    
    def _finalize_visualization_setup(self):
        # Set the plotter widget
        self.scene_manager.plotter_widget = self.plotter_widget
        
        # Clear any default objects and recreate with proper plotter
        for obj_id in list(self.scene_manager.objects.keys()):
            self.scene_manager.remove_object(obj_id)
        
        # Recreate default scene
        self.scene_manager._setup_default_mappings()
        
        # Reset camera
        self.plotter_widget.reset_camera()
        
        self.status_bar.showMessage("Ready - Multi-object scene with note range mapping active")
    
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Loading...")
        
        # Performance indicators
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --")
        self.status_bar.addPermanentWidget(self.fps_label)
        self.status_bar.addPermanentWidget(self.memory_label)

        # Initialize plotter
        self.plotter_widget = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter_widget)

        # UI Controls
        self.target_shape_combo = QComboBox()
        self.target_shape_combo.addItems(sorted(list(self.initial_meshes.keys())))
        self.layout.addWidget(QLabel("Target Shape:"))
        self.layout.addWidget(self.target_shape_combo)

        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setMinimum(0)
        self.morph_slider.setMaximum(100)
        self.layout.addWidget(QLabel("Morph Blend (CC#1):"))
        self.layout.addWidget(self.morph_slider)
        
        # Control buttons
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        self.scene_config_button = QPushButton("Scene Configuration")
        self.scene_config_button.clicked.connect(self._show_scene_config_dialog)
        self.layout.addWidget(self.scene_config_button)
        
        self.config_button = QPushButton("Settings")
        self.config_button.clicked.connect(self._show_config_dialog)
        self.layout.addWidget(self.config_button)
        
        self.performance_button = QPushButton("Show Performance Monitor")
        self.performance_button.clicked.connect(self._show_performance_dialog)
        self.layout.addWidget(self.performance_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        # Clear button
        self.clear_all_button = QPushButton("Clear All Notes")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.layout.addWidget(self.clear_all_button)
        
        # Finalize visualization setup
        self._finalize_visualization_setup()
        
        # Connect UI signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
    
    def _setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        config_action = QAction("Settings...", self)
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
        scene_config_action.triggered.connect(self._show_scene_config_dialog)
        scene_config_action.setShortcut("Ctrl+Shift+S")
        view_menu.addAction(scene_config_action)
        
        # Performance menu
        perf_menu = menubar.addMenu("Performance")
        
        show_monitor_action = QAction("Show Performance Monitor", self)
        show_monitor_action.triggered.connect(self._show_performance_dialog)
        perf_menu.addAction(show_monitor_action)
    
    def _setup_midi(self):
        if not MIDI_AVAILABLE:
            return
        
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if self.midi_handler.start(self.config.MIDI_PORT):
            print("MIDI connected")
    
    def _setup_performance_monitoring(self):
        self.profiler.fps_updated.connect(self._update_fps_status)
        self.profiler.memory_updated.connect(self._update_memory_status)
        self.profiler.performance_warning.connect(self._show_performance_warning)
        
        self.profiler.start_monitoring()
    
    def _frame_update(self):
        self.profiler.start_frame()
        self.profiler.end_frame()
    
    def _on_midi_note_on(self, note, velocity):
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, velocity, True)
                
                if affected_objects:
                    print(f"Note ON: {note} -> Objects: {', '.join(affected_objects)}")
                    self._update_scene_display()
                else:
                    print(f"Note ON: {note} - No objects in range")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, 0, False)
                
                if affected_objects:
                    print(f"Note OFF: {note} -> Objects: {', '.join(affected_objects)}")
                    self._update_scene_display()
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        if cc_number == 1:  # Mod wheel
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
    
    def _update_scene_display(self):
        if self.scene_manager:
            summary = self.scene_manager.get_scene_summary()
            total_notes = summary['total_active_notes']
            
            if total_notes > 0:
                note_info = []
                for obj_id, obj_info in summary['objects'].items():
                    if obj_info['active_notes'] > 0:
                        note_info.append(f"{obj_id}({obj_info['active_notes']})")
                
                self.notes_label.setText(f"Active: {', '.join(note_info)} | Total Notes: {total_notes}")
            else:
                self.notes_label.setText("Active Notes: None")
    
    def _cleanup_expired_elements(self):
        if self.scene_manager:
            self.scene_manager.cleanup_expired_notes(60.0)
            self._update_scene_display()
    
    def _clear_all(self):
        if self.scene_manager:
            self.scene_manager.clear_all_notes()
            self._update_scene_display()
    
    def _reconnect_midi(self):
        print("Reconnecting MIDI...")
        self.midi_handler.stop()
        QTimer.singleShot(100, self._do_midi_reconnect)
    
    def _do_midi_reconnect(self):
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected successfully", 3000)
            print("MIDI reconnected successfully")
        else:
            self.status_bar.showMessage("MIDI reconnection failed", 3000)
            print("MIDI reconnection failed")
    
    def _test_morph(self):
        """Test morphing function directly."""
        print("=== TESTING MORPH FUNCTION ===")
        print(f"Scene manager exists: {self.scene_manager is not None}")
        if self.scene_manager:
            print(f"Objects in scene: {list(self.scene_manager.objects.keys())}")
            print(f"Meshes in scene: {list(self.scene_manager.meshes.keys())}")
            print(f"Actors in scene: {list(self.scene_manager.actors.keys())}")
        
        current_value = self.morph_slider.value()
        current_target = self.target_shape_combo.currentText()
        print(f"Current slider value: {current_value}")
        print(f"Current target shape: {current_target}")
        print("Calling morph function with 50%...")
        self.on_morph_slider_change(50)
        print("=== END TEST ===")
    
    def on_morph_slider_change(self, value):
        alpha = value / 100.0
        
        if self.scene_manager:
            for obj_id, visual_obj in self.scene_manager.objects.items():
                if hasattr(visual_obj, 'morph_amount'):
                    visual_obj.morph_amount = alpha
            
            self.scene_manager.render_frame()
    
    def on_target_shape_change(self, target_key):
        if target_key in self.initial_meshes:
            if self.scene_manager:
                for visual_obj in self.scene_manager.objects.values():
                    visual_obj.current_morph_target = target_key
                
                self.on_morph_slider_change(self.morph_slider.value())
    
    def _show_config_dialog(self):
        if self.config_dialog is None:
            self.config_dialog = ConfigurationDialog(self.config, self)
            self.config_dialog.settings_changed.connect(self._on_settings_changed)
        
        self.config_dialog.show()
        self.config_dialog.raise_()
        self.config_dialog.activateWindow()
    
    def _on_settings_changed(self):
        """Handle settings changes from configuration dialog."""
        try:
            # Update performance monitoring thresholds
            if hasattr(self.config, 'FPS_WARNING'):
                self.profiler.fps_warning_threshold = self.config.FPS_WARNING
            if hasattr(self.config, 'MEMORY_WARNING'):
                self.profiler.memory_warning_threshold = self.config.MEMORY_WARNING
            if hasattr(self.config, 'CPU_WARNING'):
                self.profiler.cpu_warning_threshold = self.config.CPU_WARNING
            
            # Update cleanup interval
            if hasattr(self.config, 'CLEANUP_INTERVAL'):
                self.cleanup_timer.setInterval(self.config.CLEANUP_INTERVAL * 1000)
            
            # Update render timer for FPS target
            if hasattr(self.config, 'TARGET_FPS'):
                target_interval = int(1000 / self.config.TARGET_FPS)
                self.render_timer.setInterval(target_interval)
            
            # Update mesh resolution if changed
            if hasattr(self.config, 'MESH_RESOLUTION'):
                old_resolution = getattr(self, '_last_mesh_resolution', 50)
                if old_resolution != self.config.MESH_RESOLUTION:
                    self._recreate_meshes()
                    self._last_mesh_resolution = self.config.MESH_RESOLUTION
            
            # Save settings to persistent storage
            self.config.save_to_settings(self.settings)
            
            self.status_bar.showMessage("Settings updated successfully", 3000)
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            self.status_bar.showMessage(f"Error updating settings: {e}", 5000)
    
    def _recreate_meshes(self):
        """Recreate meshes with new resolution."""
        try:
            # Store current state
            current_morph = self.morph_slider.value() / 100.0
            
            # Recreate meshes with new resolution
            self.initial_meshes = create_initial_meshes(self.config.MESH_RESOLUTION)
            
            if self.scene_manager:
                # Update scene manager with new meshes
                self.scene_manager.initial_meshes = self.initial_meshes
                
                # Recreate all objects with new resolution
                objects_to_recreate = []
                for obj_id, visual_obj in list(self.scene_manager.objects.items()):
                    # Store object configuration
                    config = {
                        'note_range': visual_obj.note_range,
                        'shape_type': visual_obj.shape_type,
                        'position': visual_obj.position.copy(),
                        'scale': visual_obj.scale,
                        'depth_layer': visual_obj.depth_layer,
                        'blend_mode': visual_obj.blend_mode
                    }
                    objects_to_recreate.append((obj_id, config))
                    
                    # Remove old object
                    self.scene_manager.remove_object(obj_id)
                
                # Recreate all objects
                for obj_id, config in objects_to_recreate:
                    self.scene_manager.add_object(
                        id=obj_id,
                        note_range=config['note_range'],
                        shape_type=config['shape_type'],
                        position=config['position'],
                        scale=config['scale'],
                        depth_layer=config['depth_layer'],
                        blend_mode=config['blend_mode']
                    )
            
            print(f"Meshes recreated with resolution: {self.config.MESH_RESOLUTION}")
            
        except Exception as e:
            print(f"Error recreating meshes: {e}")
    
    def _show_scene_config_dialog(self):
        if not self.scene_manager:
            QMessageBox.warning(self, "Scene Manager", "Scene manager not initialized. Please restart the application.")
            return
        
        if self.scene_config_dialog is None:
            self.scene_config_dialog = SceneConfigurationDialog(self.scene_manager, self)
        
        self.scene_config_dialog.show()
        self.scene_config_dialog.raise_()
        self.scene_config_dialog.activateWindow()
    
    def _show_performance_dialog(self):
        if self.performance_dialog is None:
            self.performance_dialog = PerformanceDialog(self.profiler, self)
        
        self.performance_dialog.show()
        self.performance_dialog.raise_()
        self.performance_dialog.activateWindow()
    
    def _update_fps_status(self, fps):
        color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
        self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _update_memory_status(self, memory_mb, memory_percent):
        color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
        self.memory_label.setText(f"<font color='{color}'>Mem: {memory_percent:.1f}%</font>")
    
    def _show_performance_warning(self, warning):
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)
    
    def closeEvent(self, event):
        print("Shutting down application...")
        
        try:
            if self.midi_handler:
                self.midi_handler.stop()
        except Exception as e:
            print(f"Error stopping MIDI handler: {e}")
        
        try:
            self.profiler.stop_monitoring()
        except Exception as e:
            print(f"Error stopping performance monitoring: {e}")
        
        try:
            self.cleanup_timer.stop()
            self.render_timer.stop()
        except Exception as e:
            print(f"Error stopping timers: {e}")
        
        try:
            if self.performance_dialog:
                self.performance_dialog.close()
            if self.config_dialog:
                self.config_dialog.close()
            if self.scene_config_dialog:
                self.scene_config_dialog.close()
        except Exception as e:
            print(f"Error closing dialogs: {e}")
        
        print("Application shutdown complete")
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = SceneMorphingMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
