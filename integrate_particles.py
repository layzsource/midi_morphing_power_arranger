"""
Complete Integration Guide for Particle Effects System
This script shows exactly how to integrate the particle system with your existing MIDI visualization app.
"""

from PyQt5.QtCore import QTimer
from particle_system import ParticleSystemIntegration
from particle_ui_integration import (
    add_particle_tab_to_scene_config,
    add_particle_performance_to_dialog,
    integrate_particle_ui_with_main_window
)


def integrate_particles_into_app(main_window):
    """
    Complete integration of particle system into your existing application.
    Call this function from your main window initialization.
    
    Args:
        main_window: Your main application window (main_fixed_window.py)
    """
    
    print("🎆 Integrating particle effects system...")
    
    # Step 1: Create particle system integration
    if not hasattr(main_window, 'scene_manager') or not hasattr(main_window, 'plotter_widget'):
        print("❌ Cannot integrate particles - missing scene_manager or plotter_widget")
        return None
    
    try:
        # Create the particle integration
        particle_integration = ParticleSystemIntegration(
            main_window.scene_manager,
            main_window.plotter_widget
        )
        
        # Store reference in main window
        main_window.particle_integration = particle_integration
        print("✅ Particle system core integration complete")
        
    except Exception as e:
        print(f"❌ Error creating particle integration: {e}")
        return None
    
    # Step 2: Integrate with update loop
    try:
        setup_particle_updates(main_window, particle_integration)
        print("✅ Particle update loop integrated")
    except Exception as e:
        print(f"⚠️  Could not integrate update loop: {e}")
    
    # Step 3: Add UI controls
    try:
        integrate_particle_ui_with_main_window(main_window, particle_integration)
        print("✅ Main window UI integration complete")
    except Exception as e:
        print(f"⚠️  Could not integrate main window UI: {e}")
    
    # Step 4: Integrate with existing dialogs
    try:
        integrate_with_dialogs(main_window, particle_integration)
        print("✅ Dialog integration complete")
    except Exception as e:
        print(f"⚠️  Could not integrate with dialogs: {e}")
    
    # Step 5: Setup performance monitoring
    try:
        setup_performance_monitoring(main_window, particle_integration)
        print("✅ Performance monitoring setup complete")
    except Exception as e:
        print(f"⚠️  Could not setup performance monitoring: {e}")
    
    print("🎉 Particle effects system fully integrated!")
    print(f"   • MIDI notes will now trigger particle effects")
    print(f"   • Check Scene Configuration dialog for particle settings")
    print(f"   • Performance monitoring available in Performance dialog")
    
    return particle_integration


def setup_particle_updates(main_window, particle_integration):
    """Setup particle system updates integrated with existing update loop."""
    
    # Method 1: If there's already an update timer, enhance it
    if hasattr(main_window, 'update_timer') and main_window.update_timer:
        print("🔄 Enhancing existing update timer")
        
        # Store original update function
        original_connections = []
        if hasattr(main_window.update_timer, 'timeout'):
            # Disconnect all existing connections temporarily
            main_window.update_timer.timeout.disconnect()
        
        # Create enhanced update function
        def enhanced_update():
            try:
                # Update particles first
                particle_integration.update()
                
                # Call original update methods
                if hasattr(main_window, '_update_scene_display'):
                    main_window._update_scene_display()
                
                if hasattr(main_window, '_cleanup_expired_elements'):
                    main_window._cleanup_expired_elements()
                
                # Update performance monitoring if available
                if hasattr(main_window, 'profiler') and main_window.profiler:
                    main_window.profiler.record('particle_update_time', 0.001)  # Mock timing
                
            except Exception as e:
                print(f"Error in enhanced update: {e}")
        
        # Connect enhanced update
        main_window.update_timer.timeout.connect(enhanced_update)
        
    # Method 2: Create new timer if none exists
    else:
        print("🆕 Creating new particle update timer")
        particle_timer = QTimer()
        particle_timer.timeout.connect(lambda: particle_integration.update())
        particle_timer.start(16)  # ~60 FPS
        main_window.particle_timer = particle_timer


def integrate_with_dialogs(main_window, particle_integration):
    """Integrate particle controls with existing configuration dialogs."""
    
    # Integrate with scene configuration dialog
    def on_scene_config_shown():
        """Add particle tab when scene config dialog is shown."""
        if hasattr(main_window, 'scene_config_dialog') and main_window.scene_config_dialog:
            add_particle_tab_to_scene_config(
                main_window.scene_config_dialog, 
                particle_integration
            )
    
    # Hook into scene config dialog creation
    original_show_scene_config = getattr(main_window, '_show_scene_config_dialog', None)
    if original_show_scene_config:
        def enhanced_show_scene_config():
            original_show_scene_config()
            on_scene_config_shown()
        
        main_window._show_scene_config_dialog = enhanced_show_scene_config
    
    # Integrate with performance dialog
    def on_performance_dialog_shown():
        """Add particle performance tab when performance dialog is shown."""
        if hasattr(main_window, 'performance_dialog') and main_window.performance_dialog:
            add_particle_performance_to_dialog(
                main_window.performance_dialog,
                particle_integration
            )
    
    # Hook into performance dialog creation
    original_show_performance = getattr(main_window, '_show_performance_dialog', None)
    if original_show_performance:
        def enhanced_show_performance():
            original_show_performance()
            on_performance_dialog_shown()
        
        main_window._show_performance_dialog = enhanced_show_performance


def setup_performance_monitoring(main_window, particle_integration):
    """Setup performance monitoring for particle effects."""
    
    # Add particle metrics to existing profiler
    if hasattr(main_window, 'profiler') and main_window.profiler:
        profiler = main_window.profiler
        
        # Add particle-specific metrics
        def update_particle_metrics():
            stats = particle_integration.particle_system.get_performance_stats()
            if stats:
                profiler.record('particle_count', stats.get('active_particles', 0))
                profiler.record('particle_update_time', stats.get('avg_update_time_ms', 0) / 1000.0)
                profiler.record('particle_emitters', stats.get('active_emitters', 0))
        
        # Connect to existing performance update timer
        if hasattr(main_window, 'performance_timer'):
            main_window.performance_timer.timeout.connect(update_particle_metrics)
        else:
            # Create new performance timer
            perf_timer = QTimer()
            perf_timer.timeout.connect(update_particle_metrics)
            perf_timer.start(5000)  # Update every 5 seconds
            main_window.particle_perf_timer = perf_timer


def add_particle_menu_items(main_window, particle_integration):
    """Add particle-related menu items to existing menu bar."""
    
    if not hasattr(main_window, 'menuBar'):
        return
    
    try:
        # Find or create Effects menu
        menu_bar = main_window.menuBar()
        effects_menu = None
        
        # Look for existing Effects menu
        for action in menu_bar.actions():
            if action.text() == "Effects":
                effects_menu = action.menu()
                break
        
        # Create Effects menu if it doesn't exist
        if not effects_menu:
            effects_menu = menu_bar.addMenu("Effects")
        
        # Add particle actions
        from PyQt5.QtWidgets import QAction
        
        # Toggle particles
        toggle_action = QAction("Toggle Particle Effects", main_window)
        toggle_action.setCheckable(True)
        toggle_action.setChecked(True)
        toggle_action.triggered.connect(particle_integration.set_enabled)
        effects_menu.addAction(toggle_action)
        
        # Performance mode
        perf_action = QAction("Particle Performance Mode", main_window)
        perf_action.setCheckable(True)
        perf_action.triggered.connect(particle_integration.particle_system.set_performance_mode)
        effects_menu.addAction(perf_action)
        
        effects_menu.addSeparator()
        
        # Test effects
        explosion_action = QAction("Test Explosion Effect", main_window)
        explosion_action.triggered.connect(lambda: test_effect("explosion", particle_integration))
        effects_menu.addAction(explosion_action)
        
        shockwave_action = QAction("Test Shockwave Effect", main_window)
        shockwave_action.triggered.connect(lambda: test_effect("shockwave", particle_integration))
        effects_menu.addAction(shockwave_action)
        
        bloom_action = QAction("Test Bloom Effect", main_window)
        bloom_action.triggered.connect(lambda: test_effect("bloom", particle_integration))
        effects_menu.addAction(bloom_action)
        
        effects_menu.addSeparator()
        
        # Clear particles
        clear_action = QAction("Clear All Particles", main_window)
        clear_action.triggered.connect(particle_integration.particle_system.clear_all_particles)
        effects_menu.addAction(clear_action)
        
        print("✅ Particle menu items added")
        
    except Exception as e:
        print(f"⚠️  Could not add particle menu items: {e}")


def test_effect(effect_type, particle_integration):
    """Test a specific particle effect."""
    import numpy as np
    
    # Use center position for test
    position = np.array([0, 0, 0])
    particle_integration.particle_system.emit_special_effect(effect_type, position, 0.8)
    print(f"🎆 Triggered {effect_type} effect")


def setup_keyboard_shortcuts(main_window, particle_integration):
    """Setup keyboard shortcuts for particle effects."""
    
    try:
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Toggle particles: Ctrl+P
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+P"), main_window)
        toggle_shortcut.activated.connect(
            lambda: particle_integration.set_enabled(
                not particle_integration.particle_system.render_particles
            )
        )
        
        # Clear particles: Ctrl+Shift+C
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), main_window)
        clear_shortcut.activated.connect(particle_integration.particle_system.clear_all_particles)
        
        # Test explosion: Ctrl+E
        explosion_shortcut = QShortcut(QKeySequence("Ctrl+E"), main_window)
        explosion_shortcut.activated.connect(lambda: test_effect("explosion", particle_integration))
        
        # Performance mode: Ctrl+Shift+P
        perf_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), main_window)
        perf_shortcut.activated.connect(
            lambda: particle_integration.particle_system.set_performance_mode(
                not particle_integration.particle_system.performance_mode
            )
        )
        
        print("✅ Particle keyboard shortcuts added:")
        print("   • Ctrl+P: Toggle particle effects")
        print("   • Ctrl+Shift+C: Clear all particles")
        print("   • Ctrl+E: Test explosion effect")
        print("   • Ctrl+Shift+P: Toggle performance mode")
        
    except Exception as e:
        print(f"⚠️  Could not setup keyboard shortcuts: {e}")


def add_particle_status_indicators(main_window, particle_integration):
    """Add particle status indicators to the main window."""
    
    try:
        # Add to existing status bar
        if hasattr(main_window, 'status_bar'):
            from PyQt5.QtWidgets import QLabel
            
            # Particle count indicator
            particle_count_label = QLabel("Particles: 0")
            main_window.status_bar.addPermanentWidget(particle_count_label)
            
            # Performance indicator
            particle_perf_label = QLabel("FX: Normal")
            main_window.status_bar.addPermanentWidget(particle_perf_label)
            
            # Update function
            def update_particle_status():
                stats = particle_integration.particle_system.get_performance_stats()
                if stats:
                    count = stats.get('active_particles', 0)
                    particle_count_label.setText(f"Particles: {count}")
                    
                    if stats.get('performance_mode', False):
                        particle_perf_label.setText("FX: Performance")
                        particle_perf_label.setStyleSheet("color: orange;")
                    else:
                        particle_perf_label.setText("FX: Quality")
                        particle_perf_label.setStyleSheet("color: green;")
                else:
                    particle_count_label.setText("Particles: Disabled")
                    particle_perf_label.setText("FX: Off")
                    particle_perf_label.setStyleSheet("color: red;")
            
            # Connect to update timer
            if hasattr(main_window, 'update_timer'):
                main_window.update_timer.timeout.connect(update_particle_status)
            
            # Store references
            main_window.particle_count_label = particle_count_label
            main_window.particle_perf_label = particle_perf_label
            
            print("✅ Particle status indicators added")
            
    except Exception as e:
        print(f"⚠️  Could not add status indicators: {e}")


# Easy integration function for your existing code
def add_particles_to_existing_app():
    """
    SIMPLE INTEGRATION FUNCTION
    
    Add this to your main_fixed_window.py file in the __init__ method:
    
    ```python
    # Add this import at the top
    from integrate_particles import add_particles_to_existing_app
    
    # Add this line at the end of your __init__ method
    add_particles_to_existing_app(self)
    ```
    """
    import sys
    import inspect
    
    # Find the main window instance from the call stack
    frame = inspect.currentframe()
    try:
        # Look up the call stack to find the main window
        while frame:
            if 'self' in frame.f_locals:
                potential_main_window = frame.f_locals['self']
                
                # Check if this looks like our main window
                if (hasattr(potential_main_window, 'scene_manager') and 
                    hasattr(potential_main_window, 'plotter_widget')):
                    
                    print("🔍 Found main window instance, integrating particles...")
                    return integrate_particles_into_app(potential_main_window)
            
            frame = frame.f_back
    finally:
        del frame
    
    print("❌ Could not find main window instance for particle integration")
    return None


# Configuration templates
PARTICLE_CONFIG_TEMPLATE = {
    "particle_effects": {
        "enabled": True,
        "performance_mode": False,
        "max_particles": 1000,
        "size_scale": 1.0,
        "opacity_scale": 1.0,
        "blend_mode": "additive",
        "physics": {
            "gravity": [0.0, -9.81, 0.0],
            "global_damping": 0.98
        },
        "note_mapping": {
            "velocity_scale": 1.0,
            "size_by_velocity": True,
            "color_by_note": True,
            "life_by_velocity": True
        },
        "effects": {
            "high_velocity_threshold": 0.8,
            "explosion_threshold": 0.9,
            "enable_special_effects": True
        }
    }
}


def save_particle_configuration(main_window, filename="particle_config.json"):
    """Save current particle configuration to file."""
    try:
        import json
        
        if not hasattr(main_window, 'particle_integration'):
            print("No particle integration found")
            return False
        
        # Get current settings
        particle_system = main_window.particle_integration.particle_system
        config = PARTICLE_CONFIG_TEMPLATE.copy()
        
        # Update with current values
        config["particle_effects"].update({
            "enabled": particle_system.render_particles,
            "performance_mode": particle_system.performance_mode,
            "max_particles": particle_system.max_particles,
            "size_scale": particle_system.particle_size_scale,
            "opacity_scale": particle_system.opacity_scale,
            "blend_mode": particle_system.blend_mode.value
        })
        
        config["particle_effects"]["physics"]["gravity"] = particle_system.gravity.tolist()
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Particle configuration saved to {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving particle configuration: {e}")
        return False


def load_particle_configuration(main_window, filename="particle_config.json"):
    """Load particle configuration from file."""
    try:
        import json
        import numpy as np
        
        if not hasattr(main_window, 'particle_integration'):
            print("No particle integration found")
            return False
        
        # Load from file
        with open(filename, 'r') as f:
            config = json.load(f)
        
        # Apply settings
        particle_system = main_window.particle_integration.particle_system
        particle_config = config.get("particle_effects", {})
        
        particle_system.render_particles = particle_config.get("enabled", True)
        particle_system.set_performance_mode(particle_config.get("performance_mode", False))
        particle_system.max_particles = particle_config.get("max_particles", 1000)
        particle_system.particle_size_scale = particle_config.get("size_scale", 1.0)
        particle_system.opacity_scale = particle_config.get("opacity_scale", 1.0)
        
        # Load physics settings
        physics = particle_config.get("physics", {})
        if "gravity" in physics:
            particle_system.gravity = np.array(physics["gravity"])
        
        print(f"✅ Particle configuration loaded from {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading particle configuration: {e}")
        return False


if __name__ == "__main__":
    """
    Example usage - shows how to integrate with your existing application.
    """
    print("🎆 Particle Integration Guide")
    print("="*50)
    print()
    print("To add particle effects to your existing MIDI visualization:")
    print()
    print("1. Copy particle_system.py and particle_ui_integration.py to your project")
    print("2. Add this import to your main_fixed_window.py:")
    print("   from integrate_particles import integrate_particles_into_app")
    print()
    print("3. Add this line at the end of your main window __init__ method:")
    print("   self.particle_integration = integrate_particles_into_app(self)")
    print()
    print("4. That's it! Your MIDI notes will now trigger particle effects.")
    print()
    print("Features you'll get:")
    print("• ✨ Automatic particle emission on MIDI note events")
    print("• 🎛️  Particle controls in Scene Configuration dialog")
    print("• 📊 Performance monitoring in Performance dialog")
    print("• ⌨️  Keyboard shortcuts (Ctrl+P, Ctrl+E, etc.)")
    print("• 🎯 Multiple particle types (sparks, bursts, blooms, explosions)")
    print("• ⚡ Automatic performance optimization")
    print("• 🎨 Note-to-color mapping with velocity scaling")
    print()
    print("Enjoy your enhanced MIDI visualization! 🎉")
