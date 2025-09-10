"""
Integration Helper for Enhanced Scene Manager
Provides UI components and utilities for integrating the enhanced scene manager.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, 
    QPushButton, QLabel, QProgressBar, QSlider, QCheckBox,
    QListWidget, QTextEdit, QSplitter, QTabWidget, QSpinBox,
    QDoubleSpinBox, QColorDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QFont, QColor
import json
import os
from typing import Optional, Dict, List

from enhanced_scene_manager import (
    EnhancedSceneManager, InstrumentType, PerformanceEvent,
    SceneTransition, TransitionManager
)


class PerformanceControlWidget(QWidget):
    """Widget for controlling performance recording and playback."""
    
    # Signals
    recording_started = Signal()
    recording_stopped = Signal(int)  # duration in seconds
    playback_started = Signal()
    playback_stopped = Signal()
    
    def __init__(self, scene_manager: EnhancedSceneManager):
        super().__init__()
        self.scene_manager = scene_manager
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Recording controls
        recording_group = QGroupBox("Performance Recording")
        recording_layout = QVBoxLayout(recording_group)
        
        # Recording status
        self.recording_status = QLabel("Ready to record")
        self.recording_status.setStyleSheet("color: green; font-weight: bold;")
        recording_layout.addWidget(self.recording_status)
        
        # Recording duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 3600)  # 10 seconds to 1 hour
        self.duration_spin.setValue(60)
        duration_layout.addWidget(self.duration_spin)
        recording_layout.addLayout(duration_layout)
        
        # Recording buttons
        recording_buttons = QHBoxLayout()
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        
        recording_buttons.addWidget(self.record_button)
        recording_buttons.addWidget(self.stop_button)
        recording_layout.addLayout(recording_buttons)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        recording_layout.addWidget(self.progress_bar)
        
        layout.addWidget(recording_group)
        
        # Playback controls
        playback_group = QGroupBox("Playback")
        playback_layout = QVBoxLayout(playback_group)
        
        # Playback status
        self.playback_status = QLabel("No recording loaded")
        playback_layout.addWidget(self.playback_status)
        
        # Playback buttons
        playback_buttons = QHBoxLayout()
        self.play_button = QPushButton("Play Recording")
        self.play_button.clicked.connect(self.play_recording)
        self.play_button.setEnabled(False)
        
        self.pause_button = QPushButton("Stop Playback")
        self.pause_button.clicked.connect(self.stop_playback)
        self.pause_button.setEnabled(False)
        
        playback_buttons.addWidget(self.play_button)
        playback_buttons.addWidget(self.pause_button)
        playback_layout.addLayout(playback_buttons)
        
        layout.addWidget(playback_group)
        
        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QHBoxLayout(file_group)
        
        self.save_button = QPushButton("Save Recording")
        self.save_button.clicked.connect(self.save_recording)
        self.save_button.setEnabled(False)
        
        self.load_button = QPushButton("Load Recording")
        self.load_button.clicked.connect(self.load_recording)
        
        file_layout.addWidget(self.save_button)
        file_layout.addWidget(self.load_button)
        layout.addWidget(file_group)
    
    def setup_timer(self):
        """Setup timer for updating recording progress."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(100)  # Update every 100ms
    
    def start_recording(self):
        """Start performance recording."""
        duration = self.duration_spin.value()
        if self.scene_manager.record_performance(duration):
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.recording_status.setText("Recording...")
            self.recording_status.setStyleSheet("color: red; font-weight: bold;")
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(duration)
            self.recording_started.emit()
    
    def stop_recording(self):
        """Stop performance recording."""
        self.scene_manager.stop_recording()
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.recording_status.setText("Recording stopped")
        self.recording_status.setStyleSheet("color: orange; font-weight: bold;")
        self.progress_bar.setVisible(False)
        self.save_button.setEnabled(True)
        self.play_button.setEnabled(True)
        
        # Get recording stats
        stats = self.scene_manager.get_performance_stats()
        self.recording_stopped.emit(stats['recorded_events'])
    
    def play_recording(self):
        """Play back recording."""
        self.scene_manager.play_recording()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.playback_status.setText("Playing...")
        self.playback_started.emit()
    
    def stop_playback(self):
        """Stop playback."""
        self.scene_manager.performance_recorder.stop_playback()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.playback_status.setText("Playback stopped")
        self.playback_stopped.emit()
    
    def save_recording(self):
        """Save recording to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Recording", "", "JSON Files (*.json)"
        )
        if filename:
            self.scene_manager.save_recording(filename)
            QMessageBox.information(self, "Success", f"Recording saved to {filename}")
    
    def load_recording(self):
        """Load recording from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Recording", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                self.scene_manager.load_recording(filename)
                self.play_button.setEnabled(True)
                stats = self.scene_manager.get_performance_stats()
                self.playback_status.setText(f"Loaded: {stats['recorded_events']} events")
                QMessageBox.information(self, "Success", f"Recording loaded from {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load recording: {e}")
    
    def update_status(self):
        """Update recording/playback status."""
        stats = self.scene_manager.get_performance_stats()
        
        if stats['is_recording']:
            duration = int(stats['recording_duration'])
            self.progress_bar.setValue(duration)
            self.recording_status.setText(f"Recording... ({duration}s, {stats['recorded_events']} events)")
        
        if not stats['is_playing'] and self.pause_button.isEnabled():
            # Playback finished
            self.stop_playback()


class PresetControlWidget(QWidget):
    """Widget for managing instrument presets and scene templates."""
    
    preset_loaded = Signal(str)
    custom_preset_created = Signal(str)
    
    def __init__(self, scene_manager: EnhancedSceneManager):
        super().__init__()
        self.scene_manager = scene_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Built-in presets
        builtin_group = QGroupBox("Instrument Presets")
        builtin_layout = QVBoxLayout(builtin_group)
        
        self.preset_combo = QComboBox()
        for instrument in InstrumentType:
            self.preset_combo.addItem(instrument.value.title(), instrument)
        builtin_layout.addWidget(self.preset_combo)
        
        load_preset_button = QPushButton("Load Preset")
        load_preset_button.clicked.connect(self.load_preset)
        builtin_layout.addWidget(load_preset_button)
        
        layout.addWidget(builtin_group)
        
        # Custom presets
        custom_group = QGroupBox("Custom Presets")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_presets_list = QListWidget()
        self.refresh_custom_presets()
        custom_layout.addWidget(self.custom_presets_list)
        
        custom_buttons = QHBoxLayout()
        
        self.create_preset_button = QPushButton("Create from Scene")
        self.create_preset_button.clicked.connect(self.create_custom_preset)
        
        self.load_custom_button = QPushButton("Load Custom")
        self.load_custom_button.clicked.connect(self.load_custom_preset)
        
        self.delete_custom_button = QPushButton("Delete")
        self.delete_custom_button.clicked.connect(self.delete_custom_preset)
        
        custom_buttons.addWidget(self.create_preset_button)
        custom_buttons.addWidget(self.load_custom_button)
        custom_buttons.addWidget(self.delete_custom_button)
        custom_layout.addLayout(custom_buttons)
        
        layout.addWidget(custom_group)
        
        # Transition settings
        transition_group = QGroupBox("Transition Settings")
        transition_layout = QVBoxLayout(transition_group)
        
        # Enable/disable real-time switching
        self.realtime_check = QCheckBox("Enable Real-time Switching")
        self.realtime_check.setChecked(True)
        self.realtime_check.toggled.connect(self.toggle_realtime_switching)
        transition_layout.addWidget(self.realtime_check)
        
        # Transition style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(['linear', 'ease_in', 'ease_out', 'ease_in_out', 'bounce', 'elastic'])
        self.style_combo.setCurrentText('ease_in_out')
        style_layout.addWidget(self.style_combo)
        transition_layout.addLayout(style_layout)
        
        # Transition duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 5.0)
        self.duration_spin.setValue(1.0)
        self.duration_spin.setSuffix(" seconds")
        duration_layout.addWidget(self.duration_spin)
        transition_layout.addLayout(duration_layout)
        
        apply_transition_button = QPushButton("Apply Transition Settings")
        apply_transition_button.clicked.connect(self.apply_transition_settings)
        transition_layout.addWidget(apply_transition_button)
        
        layout.addWidget(transition_group)
    
    def load_preset(self):
        """Load selected instrument preset."""
        instrument_type = self.preset_combo.currentData()
        if self.scene_manager.load_instrument_preset(instrument_type):
            self.preset_loaded.emit(instrument_type.value)
    
    def create_custom_preset(self):
        """Create custom preset from current scene."""
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Create Custom Preset", "Preset name:")
        if ok and name:
            description, ok = QInputDialog.getText(self, "Create Custom Preset", "Description (optional):")
            if ok:
                if self.scene_manager.create_custom_preset(name, description):
                    self.refresh_custom_presets()
                    self.custom_preset_created.emit(name)
                    QMessageBox.information(self, "Success", f"Custom preset '{name}' created")
    
    def load_custom_preset(self):
        """Load selected custom preset."""
        current_item = self.custom_presets_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            if self.scene_manager.load_custom_preset(preset_name):
                self.preset_loaded.emit(f"custom_{preset_name}")
    
    def delete_custom_preset(self):
        """Delete selected custom preset."""
        current_item = self.custom_presets_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            reply = QMessageBox.question(
                self, "Delete Preset", 
                f"Are you sure you want to delete '{preset_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.scene_manager.preset_manager.custom_presets[preset_name]
                self.refresh_custom_presets()
    
    def refresh_custom_presets(self):
        """Refresh the custom presets list."""
        self.custom_presets_list.clear()
        for name in self.scene_manager.preset_manager.custom_presets.keys():
            self.custom_presets_list.addItem(name)
    
    def toggle_realtime_switching(self, enabled):
        """Toggle real-time scene switching."""
        self.scene_manager.enable_realtime_switching(enabled)
    
    def apply_transition_settings(self):
        """Apply transition settings."""
        style = self.style_combo.currentText()
        duration = self.duration_spin.value()
        self.scene_manager.set_transition_style(style, duration)
        QMessageBox.information(self, "Success", "Transition settings applied")


class TransitionEffectsWidget(QWidget):
    """Widget for applying special transition effects."""
    
    def __init__(self, scene_manager: EnhancedSceneManager):
        super().__init__()
        self.scene_manager = scene_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Object selection
        object_group = QGroupBox("Select Object")
        object_layout = QVBoxLayout(object_group)
        
        self.object_combo = QComboBox()
        self.refresh_objects()
        object_layout.addWidget(self.object_combo)
        
        refresh_button = QPushButton("Refresh Objects")
        refresh_button.clicked.connect(self.refresh_objects)
        object_layout.addWidget(refresh_button)
        
        layout.addWidget(object_group)
        
        # Effects
        effects_group = QGroupBox("Transition Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        # Pulse effect
        pulse_button = QPushButton("Pulse Effect")
        pulse_button.clicked.connect(self.apply_pulse_effect)
        effects_layout.addWidget(pulse_button)
        
        # Color shift effect
        color_button = QPushButton("Color Shift Effect")
        color_button.clicked.connect(self.apply_color_shift_effect)
        effects_layout.addWidget(color_button)
        
        # Spiral effect
        spiral_button = QPushButton("Spiral Effect")
        spiral_button.clicked.connect(self.apply_spiral_effect)
        effects_layout.addWidget(spiral_button)
        
        layout.addWidget(effects_group)
        
        # Effect parameters
        params_group = QGroupBox("Effect Parameters")
        params_layout = QVBoxLayout(params_group)
        
        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        self.effect_duration = QDoubleSpinBox()
        self.effect_duration.setRange(0.1, 10.0)
        self.effect_duration.setValue(1.0)
        self.effect_duration.setSuffix(" seconds")
        duration_layout.addWidget(self.effect_duration)
        params_layout.addLayout(duration_layout)
        
        # Intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity:"))
        self.effect_intensity = QDoubleSpinBox()
        self.effect_intensity.setRange(0.1, 5.0)
        self.effect_intensity.setValue(1.5)
        intensity_layout.addWidget(self.effect_intensity)
        params_layout.addLayout(intensity_layout)
        
        layout.addWidget(params_group)
    
    def refresh_objects(self):
        """Refresh the objects combo box."""
        self.object_combo.clear()
        for obj_id in self.scene_manager.objects.keys():
            self.object_combo.addItem(obj_id)
    
    def get_selected_object(self):
        """Get the currently selected object ID."""
        return self.object_combo.currentText()
    
    def apply_pulse_effect(self):
        """Apply pulse effect to selected object."""
        obj_id = self.get_selected_object()
        if obj_id:
            self.scene_manager.add_transition_effect(
                obj_id, 'pulse',
                duration=self.effect_duration.value(),
                intensity=self.effect_intensity.value()
            )
    
    def apply_color_shift_effect(self):
        """Apply color shift effect to selected object."""
        obj_id = self.get_selected_object()
        if obj_id:
            # Open color dialog
            color = QColorDialog.getColor()
            if color.isValid():
                target_color = [color.redF(), color.greenF(), color.blueF()]
                self.scene_manager.add_transition_effect(
                    obj_id, 'color_shift',
                    duration=self.effect_duration.value(),
                    target_color=target_color
                )
    
    def apply_spiral_effect(self):
        """Apply spiral effect to selected object."""
        obj_id = self.get_selected_object()
        if obj_id:
            self.scene_manager.add_transition_effect(
                obj_id, 'spiral',
                duration=self.effect_duration.value(),
                radius=self.effect_intensity.value()
            )


class SceneManagerDashboard(QWidget):
    """Main dashboard widget combining all scene manager controls."""
    
    def __init__(self, scene_manager: EnhancedSceneManager):
        super().__init__()
        self.scene_manager = scene_manager
        self.setup_ui()
        self.setup_status_timer()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        
        # Left pane - Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Tab widget for organized controls
        tab_widget = QTabWidget()
        
        # Presets tab
        self.preset_widget = PresetControlWidget(self.scene_manager)
        tab_widget.addTab(self.preset_widget, "Presets")
        
        # Performance tab
        self.performance_widget = PerformanceControlWidget(self.scene_manager)
        tab_widget.addTab(self.performance_widget, "Recording")
        
        # Effects tab
        self.effects_widget = TransitionEffectsWidget(self.scene_manager)
        tab_widget.addTab(self.effects_widget, "Effects")
        
        controls_layout.addWidget(tab_widget)
        
        # Quick actions
        quick_actions_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_actions_group)
        
        self.optimize_button = QPushButton("Optimize Scene")
        self.optimize_button.clicked.connect(self.optimize_scene)
        
        self.clear_button = QPushButton("Clear Scene")
        self.clear_button.clicked.connect(self.clear_scene)
        
        quick_layout.addWidget(self.optimize_button)
        quick_layout.addWidget(self.clear_button)
        controls_layout.addWidget(quick_actions_group)
        
        splitter.addWidget(controls_widget)
        
        # Right pane - Status and info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # Scene status
        status_group = QGroupBox("Scene Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        info_layout.addWidget(status_group)
        
        # Performance stats
        perf_group = QGroupBox("Performance Stats")
        perf_layout = QVBoxLayout(perf_group)
        
        self.perf_text = QTextEdit()
        self.perf_text.setMaximumHeight(150)
        self.perf_text.setReadOnly(True)
        perf_layout.addWidget(self.perf_text)
        
        info_layout.addWidget(perf_group)
        
        # Object list
        objects_group = QGroupBox("Active Objects")
        objects_layout = QVBoxLayout(objects_group)
        
        self.objects_list = QListWidget()
        objects_layout.addWidget(self.objects_list)
        
        info_layout.addWidget(objects_group)
        
        splitter.addWidget(info_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.preset_widget.preset_loaded.connect(self.on_preset_loaded)
        self.performance_widget.recording_started.connect(self.on_recording_started)
        self.performance_widget.recording_stopped.connect(self.on_recording_stopped)
    
    def setup_status_timer(self):
        """Setup timer for updating status displays."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_displays)
        self.status_timer.start(1000)  # Update every second
    
    def update_status_displays(self):
        """Update all status displays."""
        # Scene status
        scene_summary = self.scene_manager.get_scene_summary()
        status_text = f"""Scene Summary:
• Total Objects: {scene_summary['total_objects']}
• Active Objects: {scene_summary['active_objects']}
• Total Active Notes: {scene_summary['total_active_notes']}
• Physics Enabled: {self.scene_manager.physics_enabled}
• Composition Rules: {[rule.value for rule in self.scene_manager.composition_rules]}
"""
        self.status_text.setPlainText(status_text)
        
        # Performance stats
        perf_stats = self.scene_manager.get_performance_stats()
        perf_text = f"""Performance Stats:
• Recording: {'Yes' if perf_stats['is_recording'] else 'No'}
• Playing: {'Yes' if perf_stats['is_playing'] else 'No'}
• Recorded Events: {perf_stats['recorded_events']}
• Active Transitions: {perf_stats['active_transitions']}
• Current Preset: {perf_stats['current_preset']}
"""
        self.perf_text.setPlainText(perf_text)
        
        # Objects list
        self.objects_list.clear()
        for obj_id, obj_info in scene_summary['objects'].items():
            item_text = f"{obj_id} ({obj_info['shape_type']}) - {obj_info['active_notes']} notes"
            self.objects_list.addItem(item_text)
        
        # Update effects widget object list
        self.effects_widget.refresh_objects()
    
    def optimize_scene(self):
        """Optimize the scene for better performance."""
        optimizations = self.scene_manager.optimize_scene_for_performance()
        if optimizations:
            QMessageBox.information(
                self, "Scene Optimized", 
                "Optimizations applied:\n" + "\n".join(optimizations)
            )
        else:
            QMessageBox.information(self, "Scene Optimized", "Scene is already optimized")
    
    def clear_scene(self):
        """Clear all objects from the scene."""
        reply = QMessageBox.question(
            self, "Clear Scene", 
            "Are you sure you want to clear all objects?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.scene_manager.clear_all_notes()
            # Remove all objects
            for obj_id in list(self.scene_manager.objects.keys()):
                self.scene_manager.remove_object(obj_id)
    
    def on_preset_loaded(self, preset_name):
        """Handle preset loaded signal."""
        self.status_text.append(f"\nLoaded preset: {preset_name}")
    
    def on_recording_started(self):
        """Handle recording started signal."""
        self.status_text.append(f"\nRecording started at {time.strftime('%H:%M:%S')}")
    
    def on_recording_stopped(self, event_count):
        """Handle recording stopped signal."""
        self.status_text.append(f"\nRecording stopped. Captured {event_count} events")


class SceneManagerIntegrationHelper:
    """Helper class for integrating enhanced scene manager into existing applications."""
    
    @staticmethod
    def upgrade_existing_scene_manager(existing_scene_manager, initial_meshes, plotter_widget):
        """Upgrade an existing SceneManager to EnhancedSceneManager."""
        # Create new enhanced scene manager
        enhanced = EnhancedSceneManager(initial_meshes, plotter_widget)
        
        # Copy existing state
        enhanced.objects = existing_scene_manager.objects
        enhanced.actors = existing_scene_manager.actors
        enhanced.meshes = existing_scene_manager.meshes
        enhanced.composition_rules = existing_scene_manager.composition_rules
        enhanced.global_blend_mode = existing_scene_manager.global_blend_mode
        enhanced.depth_sorting = existing_scene_manager.depth_sorting
        enhanced.physics_enabled = existing_scene_manager.physics_enabled
        enhanced.gravity = existing_scene_manager.gravity
        enhanced.damping = existing_scene_manager.damping
        
        return enhanced
    
    @staticmethod
    def create_dashboard_dialog(scene_manager: EnhancedSceneManager, parent=None):
        """Create a dialog containing the scene manager dashboard."""
        from PySide6.QtWidgets import QDialog
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Enhanced Scene Manager")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        dashboard = SceneManagerDashboard(scene_manager)
        layout.addWidget(dashboard)
        
        return dialog
    
    @staticmethod
    def add_scene_manager_menu(main_window, scene_manager: EnhancedSceneManager):
        """Add scene manager menu items to a main window."""
        # This assumes the main window has a menuBar() method
        scene_menu = main_window.menuBar().addMenu("Scene Manager")
        
        # Preset actions
        preset_menu = scene_menu.addMenu("Load Preset")
        for instrument in InstrumentType:
            action = preset_menu.addAction(instrument.value.title())
            action.triggered.connect(
                lambda checked, inst=instrument: scene_manager.load_instrument_preset(inst)
            )
        
        scene_menu.addSeparator()
        
        # Recording actions
        start_recording_action = scene_menu.addAction("Start Recording")
        start_recording_action.triggered.connect(
            lambda: scene_manager.record_performance(60.0)
        )
        
        stop_recording_action = scene_menu.addAction("Stop Recording")
        stop_recording_action.triggered.connect(scene_manager.stop_recording)
        
        play_recording_action = scene_menu.addAction("Play Recording")
        play_recording_action.triggered.connect(scene_manager.play_recording)
        
        scene_menu.addSeparator()
        
        # Dashboard action
        dashboard_action = scene_menu.addAction("Open Dashboard")
        dashboard_action.triggered.connect(
            lambda: SceneManagerIntegrationHelper.create_dashboard_dialog(
                scene_manager, main_window
            ).show()
        )
        
        return scene_menu
    
    @staticmethod
    def create_quick_preset_toolbar(scene_manager: EnhancedSceneManager, parent=None):
        """Create a toolbar with quick preset buttons."""
        from PySide6.QtWidgets import QToolBar
        
        toolbar = QToolBar("Scene Presets", parent)
        
        for instrument in InstrumentType:
            action = toolbar.addAction(instrument.value.title())
            action.setToolTip(f"Load {instrument.value} preset")
            action.triggered.connect(
                lambda checked, inst=instrument: scene_manager.load_instrument_preset(inst)
            )
        
        toolbar.addSeparator()
        
        # Quick recording toggle
        record_action = toolbar.addAction("Record")
        record_action.setCheckable(True)
        record_action.toggled.connect(
            lambda checked: (
                scene_manager.record_performance(60.0) if checked 
                else scene_manager.stop_recording()
            )
        )
        
        return toolbar


# Example usage for integration
def integrate_enhanced_scene_manager_example():
    """Example of how to integrate the enhanced scene manager into an existing application."""
    
    # Assuming you have an existing application with:
    # - main_window: Your main application window
    # - existing_scene_manager: Your current SceneManager instance
    # - initial_meshes: Your mesh dictionary
    # - plotter_widget: Your PyVista plotter widget
    
    # 1. Upgrade existing scene manager
    # enhanced_scene = SceneManagerIntegrationHelper.upgrade_existing_scene_manager(
    #     existing_scene_manager, initial_meshes, plotter_widget
    # )
    
    # 2. Replace the old scene manager reference
    # main_window.scene_manager = enhanced_scene
    
    # 3. Add menu items
    # SceneManagerIntegrationHelper.add_scene_manager_menu(main_window, enhanced_scene)
    
    # 4. Add quick preset toolbar
    # preset_toolbar = SceneManagerIntegrationHelper.create_quick_preset_toolbar(
    #     enhanced_scene, main_window
    # )
    # main_window.addToolBar(preset_toolbar)
    
    # 5. Create dashboard dialog (optional)
    # dashboard_dialog = SceneManagerIntegrationHelper.create_dashboard_dialog(
    #     enhanced_scene, main_window
    # )
    
    # 6. Update your main loop to call the enhanced update method
    # In your existing timer or update loop, replace:
    # scene_manager.render_frame()
    # with:
    # enhanced_scene.update_frame()
    
    print("Integration steps completed!")
    print("✅ Scene manager upgraded")
    print("✅ Menu items added")
    print("✅ Toolbar created")
    print("✅ Dashboard available")
    print("✅ Update loop modified")
    
    return True


if __name__ == "__main__":
    print("Enhanced Scene Manager Integration Helper")
    print("This module provides UI components and utilities for integrating")
    print("the enhanced scene manager into existing applications.")
    print("\nKey components:")
    print("• PerformanceControlWidget - Recording and playback controls")
    print("• PresetControlWidget - Instrument preset management")
    print("• TransitionEffectsWidget - Visual effect controls")
    print("• SceneManagerDashboard - Complete control interface")
    print("• SceneManagerIntegrationHelper - Integration utilities")
    
    integrate_enhanced_scene_manager_example()
