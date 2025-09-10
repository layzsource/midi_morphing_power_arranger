from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, 
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, 
    QGroupBox, QGridLayout, QListWidget, QListWidgetItem, QFormLayout,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, 
    QHeaderView, QColorDialog, QSlider, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
import json
from scene_manager import NoteRange, LayerBlendMode, CompositionRule, VisualObject
import numpy as np

class NoteRangeWidget(QWidget):
    """Widget for configuring a single note range mapping."""
    
    range_changed = Signal()
    
    def __init__(self, note_range=None, available_shapes=None):
        super().__init__()
        self.available_shapes = available_shapes or ["sphere", "cube", "cone", "icosahedron", "torus"]
        
        self._setup_ui()
        
        if note_range:
            self.load_note_range(note_range)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with name and enabled checkbox
        header_layout = QHBoxLayout()
        
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        header_layout.addWidget(self.enabled_check)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Range name...")
        header_layout.addWidget(self.name_edit)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Note range configuration
        range_group = QGroupBox("MIDI Note Range")
        range_layout = QGridLayout(range_group)
        
        # Min note
        range_layout.addWidget(QLabel("Min Note:"), 0, 0)
        self.min_note_spin = QSpinBox()
        self.min_note_spin.setRange(0, 127)
        self.min_note_spin.setValue(60)
        self.min_note_spin.valueChanged.connect(self._on_range_changed)
        range_layout.addWidget(self.min_note_spin, 0, 1)
        
        self.min_note_label = QLabel("C4")
        range_layout.addWidget(self.min_note_label, 0, 2)
        
        # Max note
        range_layout.addWidget(QLabel("Max Note:"), 1, 0)
        self.max_note_spin = QSpinBox()
        self.max_note_spin.setRange(0, 127)
        self.max_note_spin.setValue(72)
        self.max_note_spin.valueChanged.connect(self._on_range_changed)
        range_layout.addWidget(self.max_note_spin, 1, 1)
        
        self.max_note_label = QLabel("C5")
        range_layout.addWidget(self.max_note_label, 1, 2)
        
        # MIDI Channel
        range_layout.addWidget(QLabel("MIDI Channel:"), 2, 0)
        self.channel_combo = QComboBox()
        self.channel_combo.addItem("All Channels", None)
        for i in range(1, 17):
            self.channel_combo.addItem(f"Channel {i}", i)
        range_layout.addWidget(self.channel_combo, 2, 1, 1, 2)
        
        layout.addWidget(range_group)
        
        # Visual properties
        visual_group = QGroupBox("Visual Properties")
        visual_layout = QGridLayout(visual_group)
        
        # Shape
        visual_layout.addWidget(QLabel("Shape:"), 0, 0)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(self.available_shapes)
        visual_layout.addWidget(self.shape_combo, 0, 1)
        
        # Position
        visual_layout.addWidget(QLabel("Position X:"), 1, 0)
        self.pos_x_spin = QDoubleSpinBox()
        self.pos_x_spin.setRange(-10.0, 10.0)
        self.pos_x_spin.setSingleStep(0.1)
        visual_layout.addWidget(self.pos_x_spin, 1, 1)
        
        visual_layout.addWidget(QLabel("Position Y:"), 2, 0)
        self.pos_y_spin = QDoubleSpinBox()
        self.pos_y_spin.setRange(-10.0, 10.0)
        self.pos_y_spin.setSingleStep(0.1)
        visual_layout.addWidget(self.pos_y_spin, 2, 1)
        
        visual_layout.addWidget(QLabel("Position Z:"), 3, 0)
        self.pos_z_spin = QDoubleSpinBox()
        self.pos_z_spin.setRange(-10.0, 10.0)
        self.pos_z_spin.setSingleStep(0.1)
        visual_layout.addWidget(self.pos_z_spin, 3, 1)
        
        # Scale
        visual_layout.addWidget(QLabel("Scale:"), 4, 0)
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 5.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(1.0)
        visual_layout.addWidget(self.scale_spin, 4, 1)
        
        # Depth layer
        visual_layout.addWidget(QLabel("Depth Layer:"), 5, 0)
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 10)
        self.depth_spin.setValue(1)
        visual_layout.addWidget(self.depth_spin, 5, 1)
        
        # Blend mode
        visual_layout.addWidget(QLabel("Blend Mode:"), 6, 0)
        self.blend_combo = QComboBox()
        for mode in LayerBlendMode:
            self.blend_combo.addItem(mode.value.title(), mode)
        visual_layout.addWidget(self.blend_combo, 6, 1)
        
        layout.addWidget(visual_group)
        
        # Connect signals
        self.min_note_spin.valueChanged.connect(self._update_note_labels)
        self.max_note_spin.valueChanged.connect(self._update_note_labels)
        self._update_note_labels()
    
    def _note_to_name(self, note):
        """Convert MIDI note number to note name."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note // 12) - 1
        note_name = note_names[note % 12]
        return f"{note_name}{octave}"
    
    def _update_note_labels(self):
        """Update note name labels."""
        min_note = self.min_note_spin.value()
        max_note = self.max_note_spin.value()
        
        self.min_note_label.setText(self._note_to_name(min_note))
        self.max_note_label.setText(self._note_to_name(max_note))
        
        # Ensure min <= max
        if min_note > max_note:
            self.max_note_spin.setValue(min_note)
    
    def _on_range_changed(self):
        """Handle range change."""
        self.range_changed.emit()
    
    def get_note_range_config(self):
        """Get the current configuration as a dictionary."""
        return {
            'enabled': self.enabled_check.isChecked(),
            'name': self.name_edit.text() or f"Notes {self.min_note_spin.value()}-{self.max_note_spin.value()}",
            'min_note': self.min_note_spin.value(),
            'max_note': self.max_note_spin.value(),
            'channel': self.channel_combo.currentData(),
            'shape': self.shape_combo.currentText(),
            'position': [self.pos_x_spin.value(), self.pos_y_spin.value(), self.pos_z_spin.value()],
            'scale': self.scale_spin.value(),
            'depth_layer': self.depth_spin.value(),
            'blend_mode': self.blend_combo.currentData()
        }
    
    def load_note_range(self, config):
        """Load configuration into the widget."""
        if isinstance(config, dict):
            self.enabled_check.setChecked(config.get('enabled', True))
            self.name_edit.setText(config.get('name', ''))
            self.min_note_spin.setValue(config.get('min_note', 60))
            self.max_note_spin.setValue(config.get('max_note', 72))
            
            # Set channel
            channel = config.get('channel')
            for i in range(self.channel_combo.count()):
                if self.channel_combo.itemData(i) == channel:
                    self.channel_combo.setCurrentIndex(i)
                    break
            
            # Set shape
            shape = config.get('shape', 'sphere')
            index = self.shape_combo.findText(shape)
            if index >= 0:
                self.shape_combo.setCurrentIndex(index)
            
            # Set position
            position = config.get('position', [0, 0, 0])
            self.pos_x_spin.setValue(position[0])
            self.pos_y_spin.setValue(position[1])
            self.pos_z_spin.setValue(position[2])
            
            self.scale_spin.setValue(config.get('scale', 1.0))
            self.depth_spin.setValue(config.get('depth_layer', 1))
            
            # Set blend mode
            blend_mode = config.get('blend_mode', LayerBlendMode.NORMAL)
            if isinstance(blend_mode, str):
                blend_mode = LayerBlendMode(blend_mode)
            
            for i in range(self.blend_combo.count()):
                if self.blend_combo.itemData(i) == blend_mode:
                    self.blend_combo.setCurrentIndex(i)
                    break

class SceneConfigurationDialog(QDialog):
    """Dialog for configuring the scene with note range mappings."""
    
    scene_updated = Signal()
    
    def __init__(self, scene_manager, parent=None):
        super().__init__(parent)
        self.scene_manager = scene_manager
        self.setWindowTitle("Scene Configuration")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._load_current_scene()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Note Range Mappings tab
        self._create_mappings_tab()
        
        # Composition Rules tab
        self._create_composition_tab()
        
        # Advanced Settings tab
        self._create_advanced_tab()
        
        # Presets tab
        self._create_presets_tab()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Configuration")
        self.test_button.clicked.connect(self._test_configuration)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_configuration)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _create_mappings_tab(self):
        """Create the note range mappings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header_layout.addWidget(QLabel("Note Range Mappings:"))
        header_layout.addStretch()
        
        self.add_range_button = QPushButton("Add Range")
        self.add_range_button.clicked.connect(self._add_note_range)
        header_layout.addWidget(self.add_range_button)
        
        self.remove_range_button = QPushButton("Remove Selected")
        self.remove_range_button.clicked.connect(self._remove_selected_range)
        header_layout.addWidget(self.remove_range_button)
        
        layout.addLayout(header_layout)
        
        # Scrollable list of note range widgets
        self.ranges_layout = QVBoxLayout()
        self.range_widgets = []
        
        # Scroll area would be better here, but for simplicity using direct layout
        layout.addLayout(self.ranges_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Note Mappings")
    
    def _create_composition_tab(self):
        """Create the composition rules tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Composition Rules
        rules_group = QGroupBox("Composition Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        self.independent_check = QCheckBox("Independent Objects")
        self.independent_check.setToolTip("Objects don't interact with each other")
        self.independent_check.setChecked(True)
        rules_layout.addWidget(self.independent_check)
        
        self.harmonic_check = QCheckBox("Harmonic Interaction")
        self.harmonic_check.setToolTip("Objects respond to harmonic relationships")
        rules_layout.addWidget(self.harmonic_check)
        
        self.rhythmic_check = QCheckBox("Rhythmic Synchronization")
        self.rhythmic_check.setToolTip("Objects sync to rhythm")
        rules_layout.addWidget(self.rhythmic_check)
        
        self.spatial_check = QCheckBox("Spatial Interaction")
        self.spatial_check.setToolTip("Objects affect each other spatially")
        rules_layout.addWidget(self.spatial_check)
        
        layout.addWidget(rules_group)
        
        # Global Settings
        global_group = QGroupBox("Global Settings")
        global_layout = QFormLayout(global_group)
        
        # Global blend mode
        self.global_blend_combo = QComboBox()
        for mode in LayerBlendMode:
            self.global_blend_combo.addItem(mode.value.title(), mode)
        global_layout.addRow("Global Blend Mode:", self.global_blend_combo)
        
        # Depth sorting
        self.depth_sorting_check = QCheckBox("Enable Depth Sorting")
        self.depth_sorting_check.setChecked(True)
        global_layout.addRow(self.depth_sorting_check)
        
        layout.addWidget(global_group)
        
        # Visual Interaction Settings
        interaction_group = QGroupBox("Interaction Strength")
        interaction_layout = QFormLayout(interaction_group)
        
        # Harmonic interaction strength
        self.harmonic_strength = QDoubleSpinBox()
        self.harmonic_strength.setRange(0.0, 2.0)
        self.harmonic_strength.setSingleStep(0.1)
        self.harmonic_strength.setValue(0.5)
        interaction_layout.addRow("Harmonic Strength:", self.harmonic_strength)
        
        # Spatial interaction range
        self.spatial_range = QDoubleSpinBox()
        self.spatial_range.setRange(0.1, 10.0)
        self.spatial_range.setSingleStep(0.1)
        self.spatial_range.setValue(2.0)
        interaction_layout.addRow("Spatial Range:", self.spatial_range)
        
        layout.addWidget(interaction_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Composition")
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Physics Settings
        physics_group = QGroupBox("Physics Simulation")
        physics_layout = QFormLayout(physics_group)
        
        self.physics_enabled = QCheckBox("Enable Physics")
        physics_layout.addRow(self.physics_enabled)
        
        # Gravity
        self.gravity_x = QDoubleSpinBox()
        self.gravity_x.setRange(-1.0, 1.0)
        self.gravity_x.setSingleStep(0.01)
        self.gravity_x.setValue(0.0)
        physics_layout.addRow("Gravity X:", self.gravity_x)
        
        self.gravity_y = QDoubleSpinBox()
        self.gravity_y.setRange(-1.0, 1.0)
        self.gravity_y.setSingleStep(0.01)
        self.gravity_y.setValue(-0.1)
        physics_layout.addRow("Gravity Y:", self.gravity_y)
        
        self.gravity_z = QDoubleSpinBox()
        self.gravity_z.setRange(-1.0, 1.0)
        self.gravity_z.setSingleStep(0.01)
        self.gravity_z.setValue(0.0)
        physics_layout.addRow("Gravity Z:", self.gravity_z)
        
        # Damping
        self.damping = QDoubleSpinBox()
        self.damping.setRange(0.0, 1.0)
        self.damping.setSingleStep(0.01)
        self.damping.setValue(0.95)
        physics_layout.addRow("Damping:", self.damping)
        
        layout.addWidget(physics_group)
        
        # Animation Settings
        animation_group = QGroupBox("Animation Settings")
        animation_layout = QFormLayout(animation_group)
        
        # Fade timeout
        self.fade_timeout = QSpinBox()
        self.fade_timeout.setRange(1, 300)
        self.fade_timeout.setValue(60)
        self.fade_timeout.setSuffix(" seconds")
        animation_layout.addRow("Note Fade Timeout:", self.fade_timeout)
        
        # Transition speed
        self.transition_speed = QDoubleSpinBox()
        self.transition_speed.setRange(0.1, 5.0)
        self.transition_speed.setSingleStep(0.1)
        self.transition_speed.setValue(1.0)
        animation_layout.addRow("Transition Speed:", self.transition_speed)
        
        layout.addWidget(animation_group)
        
        # Performance Settings
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        # Max objects
        self.max_objects = QSpinBox()
        self.max_objects.setRange(1, 50)
        self.max_objects.setValue(10)
        performance_layout.addRow("Max Objects:", self.max_objects)
        
        # Update rate
        self.update_rate = QSpinBox()
        self.update_rate.setRange(10, 120)
        self.update_rate.setValue(60)
        self.update_rate.setSuffix(" Hz")
        performance_layout.addRow("Update Rate:", self.update_rate)
        
        layout.addWidget(performance_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Advanced")
    
    def _create_presets_tab(self):
        """Create the presets management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preset list
        presets_group = QGroupBox("Scene Presets")
        presets_layout = QVBoxLayout(presets_group)
        
        self.presets_list = QListWidget()
        self._populate_presets_list()
        presets_layout.addWidget(self.presets_list)
        
        # Preset buttons
        preset_buttons = QHBoxLayout()
        
        self.load_preset_button = QPushButton("Load Preset")
        self.load_preset_button.clicked.connect(self._load_preset)
        preset_buttons.addWidget(self.load_preset_button)
        
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self._save_preset)
        preset_buttons.addWidget(self.save_preset_button)
        
        self.delete_preset_button = QPushButton("Delete Preset")
        self.delete_preset_button.clicked.connect(self._delete_preset)
        preset_buttons.addWidget(self.delete_preset_button)
        
        presets_layout.addLayout(preset_buttons)
        layout.addWidget(presets_group)
        
        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QHBoxLayout(file_group)
        
        self.import_button = QPushButton("Import Scene")
        self.import_button.clicked.connect(self._import_scene)
        file_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("Export Scene")
        self.export_button.clicked.connect(self._export_scene)
        file_layout.addWidget(self.export_button)
        
        layout.addWidget(file_group)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "Presets")
    
    def _populate_presets_list(self):
        """Populate the presets list with built-in presets."""
        presets = [
            "Piano (4 Octaves)",
            "Orchestral (Full Range)",
            "Electronic (3 Layers)",
            "Ambient (Sparse)",
            "Jazz (Complex)",
            "Single Object (Legacy)"
        ]
        
        for preset in presets:
            self.presets_list.addItem(preset)
    
    def _add_note_range(self):
        """Add a new note range widget."""
        available_shapes = list(self.scene_manager.initial_meshes.keys())
        range_widget = NoteRangeWidget(available_shapes=available_shapes)
        range_widget.range_changed.connect(self._on_range_changed)
        
        # Set default values based on existing ranges
        existing_ranges = len(self.range_widgets)
        default_min = 60 + (existing_ranges * 12)
        default_max = min(127, default_min + 11)
        
        range_widget.min_note_spin.setValue(default_min)
        range_widget.max_note_spin.setValue(default_max)
        range_widget.name_edit.setText(f"Range {existing_ranges + 1}")
        
        # Set position offset
        range_widget.pos_x_spin.setValue(existing_ranges * 1.5 - 2.0)
        
        self.range_widgets.append(range_widget)
        self.ranges_layout.addWidget(range_widget)
    
    def _remove_selected_range(self):
        """Remove the last range widget (for simplicity)."""
        if self.range_widgets:
            widget = self.range_widgets.pop()
            self.ranges_layout.removeWidget(widget)
            widget.deleteLater()
    
    def _on_range_changed(self):
        """Handle changes in note ranges."""
        # Could add validation here
        pass
    
    def _load_current_scene(self):
        """Load the current scene configuration into the dialog."""
        # Load composition rules
        rules = self.scene_manager.composition_rules
        self.independent_check.setChecked(CompositionRule.INDEPENDENT in rules)
        self.harmonic_check.setChecked(CompositionRule.HARMONIC in rules)
        self.rhythmic_check.setChecked(CompositionRule.RHYTHMIC in rules)
        self.spatial_check.setChecked(CompositionRule.SPATIAL in rules)
        
        # Load global settings
        blend_mode = self.scene_manager.global_blend_mode
        for i in range(self.global_blend_combo.count()):
            if self.global_blend_combo.itemData(i) == blend_mode:
                self.global_blend_combo.setCurrentIndex(i)
                break
        
        self.depth_sorting_check.setChecked(self.scene_manager.depth_sorting)
        self.physics_enabled.setChecked(self.scene_manager.physics_enabled)
        
        # Load gravity settings
        gravity = self.scene_manager.gravity
        self.gravity_x.setValue(gravity[0])
        self.gravity_y.setValue(gravity[1])
        self.gravity_z.setValue(gravity[2])
        
        self.damping.setValue(self.scene_manager.damping)
        
        # Load existing objects as range widgets
        for obj_id, visual_obj in self.scene_manager.objects.items():
            config = {
                'enabled': True,
                'name': visual_obj.note_range.name or obj_id,
                'min_note': visual_obj.note_range.min_note,
                'max_note': visual_obj.note_range.max_note,
                'channel': visual_obj.note_range.channel,
                'shape': visual_obj.shape_type,
                'position': visual_obj.position.tolist(),
                'scale': visual_obj.scale,
                'depth_layer': visual_obj.depth_layer,
                'blend_mode': visual_obj.blend_mode
            }
            
            available_shapes = list(self.scene_manager.initial_meshes.keys())
            range_widget = NoteRangeWidget(config, available_shapes)
            range_widget.range_changed.connect(self._on_range_changed)
            
            self.range_widgets.append(range_widget)
            self.ranges_layout.addWidget(range_widget)
    
    def _apply_configuration(self):
        """Apply the current configuration to the scene manager."""
        try:
            # Clear existing objects
            for obj_id in list(self.scene_manager.objects.keys()):
                self.scene_manager.remove_object(obj_id)
            
            # Add configured objects
            for i, range_widget in enumerate(self.range_widgets):
                config = range_widget.get_note_range_config()
                
                if not config['enabled']:
                    continue
                
                note_range = NoteRange(
                    min_note=config['min_note'],
                    max_note=config['max_note'],
                    name=config['name'],
                    channel=config['channel']
                )
                
                obj_id = f"range_{i}"
                self.scene_manager.add_object(
                    id=obj_id,
                    note_range=note_range,
                    shape_type=config['shape'],
                    position=np.array(config['position']),
                    scale=config['scale'],
                    depth_layer=config['depth_layer'],
                    blend_mode=config['blend_mode']
                )
            
            # Apply composition rules
            rules = []
            if self.independent_check.isChecked():
                rules.append(CompositionRule.INDEPENDENT)
            if self.harmonic_check.isChecked():
                rules.append(CompositionRule.HARMONIC)
            if self.rhythmic_check.isChecked():
                rules.append(CompositionRule.RHYTHMIC)
            if self.spatial_check.isChecked():
                rules.append(CompositionRule.SPATIAL)
            
            self.scene_manager.composition_rules = rules
            
            # Apply global settings
            self.scene_manager.global_blend_mode = self.global_blend_combo.currentData()
            self.scene_manager.depth_sorting = self.depth_sorting_check.isChecked()
            self.scene_manager.physics_enabled = self.physics_enabled.isChecked()
            
            # Apply physics settings
            self.scene_manager.gravity = np.array([
                self.gravity_x.value(),
                self.gravity_y.value(),
                self.gravity_z.value()
            ])
            self.scene_manager.damping = self.damping.value()
            
            # Emit signal
            self.scene_updated.emit()
            
            QMessageBox.information(self, "Success", "Scene configuration applied successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply configuration:\n{str(e)}")
    
    def _test_configuration(self):
        """Test the current configuration."""
        try:
            # Validate note ranges
            ranges = []
            for range_widget in self.range_widgets:
                config = range_widget.get_note_range_config()
                if config['enabled']:
                    ranges.append((config['min_note'], config['max_note'], config['name']))
            
            # Check for overlaps
            overlaps = []
            for i, (min1, max1, name1) in enumerate(ranges):
                for j, (min2, max2, name2) in enumerate(ranges[i+1:], i+1):
                    if not (max1 < min2 or max2 < min1):  # Ranges overlap
                        overlaps.append(f"{name1} and {name2}")
            
            messages = []
            if overlaps:
                messages.append("⚠️ Overlapping ranges detected:")
                messages.extend([f"  - {overlap}" for overlap in overlaps])
                messages.append("")
            
            messages.append(f"✓ {len(ranges)} active note ranges configured")
            
            if not ranges:
                messages.append("⚠️ No active note ranges configured")
            
            # Validate shapes
            available_shapes = set(self.scene_manager.initial_meshes.keys())
            for range_widget in self.range_widgets:
                config = range_widget.get_note_range_config()
                if config['enabled'] and config['shape'] not in available_shapes:
                    messages.append(f"✗ Invalid shape: {config['shape']}")
            
            messages.append(f"✓ Physics: {'Enabled' if self.physics_enabled.isChecked() else 'Disabled'}")
            
            result_dialog = QMessageBox(self)
            result_dialog.setWindowTitle("Configuration Test")
            result_dialog.setText("Configuration Test Results:")
            result_dialog.setDetailedText("\n".join(messages))
            result_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Failed to test configuration:\n{str(e)}")
    
    def _reset_to_defaults(self):
        """Reset to default configuration."""
        reply = QMessageBox.question(
            self, 
            "Reset Configuration", 
            "Reset to default note range mappings? This will clear all current settings.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear existing ranges
            for widget in self.range_widgets:
                self.ranges_layout.removeWidget(widget)
                widget.deleteLater()
            self.range_widgets.clear()
            
            # Add default ranges
            defaults = [
                {'name': 'Bass', 'min': 21, 'max': 47, 'shape': 'sphere', 'pos': [-2, 0, 0], 'scale': 1.5},
                {'name': 'Melody', 'min': 48, 'max': 72, 'shape': 'icosahedron', 'pos': [0, 0, 0], 'scale': 1.0},
                {'name': 'Treble', 'min': 73, 'max': 96, 'shape': 'cube', 'pos': [2, 0, 0], 'scale': 0.7},
                {'name': 'High', 'min': 97, 'max': 127, 'shape': 'cone', 'pos': [0, 2, 0], 'scale': 0.5}
            ]
            
            available_shapes = list(self.scene_manager.initial_meshes.keys())
            
            for default in defaults:
                config = {
                    'enabled': True,
                    'name': default['name'],
                    'min_note': default['min'],
                    'max_note': default['max'],
                    'channel': None,
                    'shape': default['shape'],
                    'position': default['pos'],
                    'scale': default['scale'],
                    'depth_layer': len(self.range_widgets) + 1,
                    'blend_mode': LayerBlendMode.NORMAL
                }
                
                range_widget = NoteRangeWidget(config, available_shapes)
                range_widget.range_changed.connect(self._on_range_changed)
                
                self.range_widgets.append(range_widget)
                self.ranges_layout.addWidget(range_widget)
    
    def _load_preset(self):
        """Load a preset configuration."""
        current_item = self.presets_list.currentItem()
        if not current_item:
            return
        
        preset_name = current_item.text()
        QMessageBox.information(self, "Preset", f"Loading preset: {preset_name}\n(Preset loading not yet implemented)")
    
    def _save_preset(self):
        """Save current configuration as a preset."""
        QMessageBox.information(self, "Preset", "Preset saving not yet implemented")
    
    def _delete_preset(self):
        """Delete selected preset."""
        current_item = self.presets_list.currentItem()
        if not current_item:
            return
        
        QMessageBox.information(self, "Preset", "Preset deletion not yet implemented")
    
    def _import_scene(self):
        """Import scene configuration from file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Scene Configuration",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                self.scene_manager.load_configuration(filename)
                self.reject()  # Close dialog and reload from scene manager
                QMessageBox.information(self, "Import", f"Scene imported from {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import scene:\n{str(e)}")
    
    def _export_scene(self):
        """Export current scene configuration to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Scene Configuration",
            f"scene_config_{int(__import__('time').time())}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                # Apply current configuration first
                self._apply_configuration()
                self.scene_manager.save_configuration(filename)
                QMessageBox.information(self, "Export", f"Scene exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export scene:\n{str(e)}")
    
    def accept(self):
        """Accept and apply configuration."""
        self._apply_configuration()
        super().accept()
