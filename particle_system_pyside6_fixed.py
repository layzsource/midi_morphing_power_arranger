"""
Fixed Particle System for PySide6 - Compatibility Issues Resolved
This version fixes the receivers() method issue and other PySide6 compatibility problems.
"""

# Copy the entire particle system but with this fix for the setup_particle_updates_pyside6 function:

def setup_particle_updates_pyside6(main_window, particle_integration):
    """Setup particle system updates integrated with existing update loop."""
    
    # Check if there's already an update timer
    if hasattr(main_window, 'render_timer') and main_window.render_timer:
        print("🔄 Enhancing existing render timer")
        
        # Create enhanced update function - SIMPLIFIED VERSION
        def enhanced_frame_update():
            try:
                # Update particles
                particle_integration.update()
                
                # Call original frame update if it exists
                if hasattr(main_window, '_frame_update'):
                    main_window._frame_update()
                
            except Exception as e:
                print(f"Error in enhanced frame update: {e}")
        
        # Simply connect the enhanced update - don't try to access receivers()
        main_window.render_timer.timeout.connect(enhanced_frame_update)
        
    else:
        print("🆕 Creating new particle update timer")
        try:
            from PySide6.QtCore import QTimer
            particle_timer = QTimer()
            particle_timer.timeout.connect(lambda: particle_integration.update())
            particle_timer.start(16)  # ~60 FPS
            main_window.particle_timer = particle_timer
        except Exception as e:
            print(f"Error creating particle timer: {e}")


# Quick fix for the receivers() issue
def integrate_particles_into_app_fixed(main_window):
    """
    Fixed version of particle integration that avoids PySide6 compatibility issues.
    """
    
    print("🎆 Integrating particle effects system (FIXED VERSION)...")
    
    # Check for required components
    if not hasattr(main_window, 'scene_manager') or not hasattr(main_window, 'plotter_widget'):
        print("❌ Cannot integrate particles - missing scene_manager or plotter_widget")
        return None
    
    try:
        # Import the required classes
        from particle_system_pyside6 import ParticleSystemIntegration
        
        # Create the particle integration
        particle_integration = ParticleSystemIntegration(
            main_window.scene_manager,
            main_window.plotter_widget
        )
        
        print("✅ Particle system core integration complete")
        
        # Setup update loop integration - SIMPLIFIED
        try:
            # Simple connection without checking receivers
            if hasattr(main_window, 'render_timer') and main_window.render_timer:
                def particle_update():
                    try:
                        particle_integration.update()
                    except Exception as e:
                        print(f"Particle update error: {e}")
                
                main_window.render_timer.timeout.connect(particle_update)
                print("✅ Particle update loop integrated")
            else:
                print("⚠️ No render timer found - particles may not update")
        
        except Exception as e:
            print(f"⚠️ Could not integrate update loop: {e}")
        
        # Add simple status indicator
        try:
            add_particle_status_to_main_window_fixed(main_window, particle_integration)
            print("✅ Particle status integration complete")
        except Exception as e:
            print(f"⚠️ Could not integrate status: {e}")
        
        print("🎉 Particle effects system integrated!")
        print("   • MIDI notes will now trigger particle effects")
        print("   • Particles scale with note velocity and map to note colors")
        
        return particle_integration
        
    except Exception as e:
        print(f"❌ Error creating particle integration: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_particle_status_to_main_window_fixed(main_window, particle_integration):
    """Add particle status indicators to the main window - FIXED VERSION."""
    
    try:
        # Add to existing status bar
        if hasattr(main_window, 'status_bar') and main_window.status_bar:
            from PySide6.QtWidgets import QLabel
            
            # Particle count indicator
            particle_count_label = QLabel("Particles: 0")
            main_window.status_bar.addPermanentWidget(particle_count_label)
            
            # Update function
            def update_particle_status():
                try:
                    stats = particle_integration.particle_system.get_performance_stats()
                    if stats:
                        count = stats.get('active_particles', 0)
                        particle_count_label.setText(f"Particles: {count}")
                        
                        # Color code based on performance
                        if stats.get('performance_mode', False):
                            particle_count_label.setStyleSheet("color: orange;")
                        elif count > 500:
                            particle_count_label.setStyleSheet("color: red;")
                        else:
                            particle_count_label.setStyleSheet("color: green;")
                    else:
                        particle_count_label.setText("Particles: Off")
                        particle_count_label.setStyleSheet("color: gray;")
                except Exception as e:
                    print(f"Error updating particle status: {e}")
            
            # Connect to existing update timer if available
            if hasattr(main_window, 'render_timer') and main_window.render_timer:
                main_window.render_timer.timeout.connect(update_particle_status)
            
            # Store reference
            main_window.particle_count_label = particle_count_label
            
            print("✅ Particle status indicators added to status bar")
            
    except Exception as e:
        print(f"⚠️ Could not add status indicators: {e}")


# Modified quick integration function
def complete_particle_integration_fixed(main_window):
    """
    FIXED COMPLETE INTEGRATION FUNCTION
    
    Replace the call in your main_fixed_window.py __init__ method:
    
    # Replace this:
    # complete_particle_integration(self)
    
    # With this:
    # complete_particle_integration_fixed(self)
    """
    
    print("\n" + "="*60)
    print("🎆 FIXED PARTICLE EFFECTS INTEGRATION")
    print("="*60)
    
    # Step 1: Basic integration
    print("Step 1: Basic particle system integration...")
    particle_integration = integrate_particles_into_app_fixed(main_window)
    
    if not particle_integration:
        print("❌ Basic integration failed - stopping here")
        return False
    
    # Store reference
    main_window.particle_integration = particle_integration
    
    # Step 2: Add simple keyboard shortcuts
    print("\nStep 2: Adding keyboard shortcuts...")
    try:
        add_keyboard_shortcuts_fixed(main_window, particle_integration)
    except Exception as e:
        print(f"⚠️ Could not add keyboard shortcuts: {e}")
    
    print("\n" + "="*60)
    print("🎉 PARTICLE INTEGRATION COMPLETE!")
    print("="*60)
    print("\nYour MIDI notes will now trigger particle effects!")
    print("• High velocity notes = burst effects")
    print("• Medium velocity notes = spark effects") 
    print("• Low velocity notes = bloom effects")
    print("• Particle colors map to note pitch")
    print("• Use Ctrl+P to toggle particles on/off")
    print("\nEnjoy your enhanced MIDI visualizer! ✨")
    
    return True


def add_keyboard_shortcuts_fixed(main_window, particle_integration):
    """Add keyboard shortcuts for particle effects - FIXED VERSION."""
    
    try:
        from PySide6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+P: Toggle particles
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+P"), main_window)
        toggle_shortcut.activated.connect(
            lambda: toggle_particles_fixed(main_window, particle_integration)
        )
        
        # Ctrl+E: Test explosion
        explosion_shortcut = QShortcut(QKeySequence("Ctrl+E"), main_window)
        explosion_shortcut.activated.connect(
            lambda: test_explosion_effect_fixed(main_window, particle_integration)
        )
        
        # Ctrl+B: Test burst
        burst_shortcut = QShortcut(QKeySequence("Ctrl+B"), main_window)
        burst_shortcut.activated.connect(
            lambda: test_burst_effect_fixed(main_window, particle_integration)
        )
        
        # Ctrl+Shift+C: Clear particles
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), main_window)
        clear_shortcut.activated.connect(
            lambda: particle_integration.particle_system.clear_all_particles()
        )
        
        print("✅ Particle keyboard shortcuts added:")
        print("   • Ctrl+P: Toggle particles")
        print("   • Ctrl+E: Test explosion")
        print("   • Ctrl+B: Test burst")
        print("   • Ctrl+Shift+C: Clear particles")
        
    except Exception as e:
        print(f"⚠️ Could not add keyboard shortcuts: {e}")


def toggle_particles_fixed(main_window, particle_integration):
    """Toggle particle effects on/off."""
    try:
        particle_system = particle_integration.particle_system
        particle_system.render_particles = not particle_system.render_particles
        
        if particle_system.render_particles:
            print("🎆 Particle effects enabled!")
        else:
            particle_system.clear_all_particles()
            print("🚫 Particle effects disabled!")
            
    except Exception as e:
        print(f"Error toggling particles: {e}")


def test_explosion_effect_fixed(main_window, particle_integration):
    """Test explosion particle effect."""
    try:
        import numpy as np
        position = np.array([0, 0, 0])
        particle_integration.particle_system.emit_special_effect("explosion", position, 1.0)
        print("💥 Explosion effect triggered!")
    except Exception as e:
        print(f"Error triggering explosion: {e}")


def test_burst_effect_fixed(main_window, particle_integration):
    """Test burst particle effect."""
    try:
        import numpy as np
        from particle_system_pyside6 import ParticleType
        position = np.array([0, 0, 0])
        particle_integration.particle_system.emit_note_particles(60, 0.8, position, ParticleType.BURST)
        print("✨ Burst effect triggered!")
    except Exception as e:
        print(f"Error triggering burst: {e}")


if __name__ == "__main__":
    print("🔧 FIXED Particle System PySide6")
    print("=" * 40)
    print()
    print("ISSUE FIXED: PySide6 Signal.receivers() compatibility")
    print()
    print("TO USE THE FIXED VERSION:")
    print("1. Copy this file as 'particle_system_pyside6_fixed.py'")
    print("2. In your main_fixed_window.py __init__ method, replace:")
    print()
    print("   # OLD:")
    print("   from quick_particle_integration import complete_particle_integration")
    print("   complete_particle_integration(self)")
    print()
    print("   # NEW:")
    print("   from particle_system_pyside6_fixed import complete_particle_integration_fixed")
    print("   complete_particle_integration_fixed(self)")
    print()
    print("This fixes the PySide6 compatibility issue! 🎉")
