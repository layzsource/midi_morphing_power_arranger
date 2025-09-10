"""
Quick Particle Integration Fix for PySide6
This file provides a simple way to add particle effects to your existing app.
"""

def add_particles_to_main_window(main_window):
    """
    SIMPLE ONE-LINE INTEGRATION
    Add this to the END of your main window __init__ method:
    
    from quick_particle_integration import add_particles_to_main_window
    add_particles_to_main_window(self)
    """
    
    print("🎆 Quick particle integration starting...")
    
    try:
        # Import the PySide6 version of particle system
        from particle_system_pyside6 import integrate_particles_into_app
        
        # Fix the status bar issue first
        fix_status_bar_issue(main_window)
        
        # Integrate particles
        particle_integration = integrate_particles_into_app(main_window)
        
        if particle_integration:
            main_window.particle_integration = particle_integration
            print("🎉 Particle effects successfully integrated!")
            return True
        else:
            print("❌ Particle integration failed")
            return False
            
    except ImportError as e:
        print(f"⚠️ Could not import particle system: {e}")
        print("📥 Make sure particle_system_pyside6.py is in your project folder")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during particle integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_status_bar_issue(main_window):
    """
    Fix the status_bar vs statusBar naming issue.
    PySide6 uses statusBar() method, not status_bar attribute.
    """
    
    try:
        # If main_window has statusBar() method but code tries to use .status_bar
        if hasattr(main_window, 'statusBar') and not hasattr(main_window, 'status_bar'):
            # Create a property that maps to the correct method
            main_window.status_bar = main_window.statusBar()
            print("✅ Fixed status bar naming issue")
            
    except Exception as e:
        print(f"⚠️ Could not fix status bar issue: {e}")


def add_simple_particle_test_buttons(main_window):
    """
    Add simple test buttons to the main window for testing particle effects.
    Only call this AFTER particles are integrated.
    """
    
    if not hasattr(main_window, 'particle_integration'):
        print("❌ Particles not integrated - cannot add test buttons")
        return
    
    try:
        from PySide6.QtWidgets import QPushButton, QHBoxLayout
        
        # Create test buttons
        test_layout = QHBoxLayout()
        
        # Explosion test
        explosion_btn = QPushButton("💥 Test Explosion")
        explosion_btn.clicked.connect(lambda: test_explosion_effect(main_window))
        test_layout.addWidget(explosion_btn)
        
        # Burst test
        burst_btn = QPushButton("✨ Test Burst")
        burst_btn.clicked.connect(lambda: test_burst_effect(main_window))
        test_layout.addWidget(burst_btn)
        
        # Clear particles
        clear_btn = QPushButton("🧹 Clear Particles")
        clear_btn.clicked.connect(lambda: clear_all_particles(main_window))
        test_layout.addWidget(clear_btn)
        
        # Add to main layout
        if hasattr(main_window, 'layout'):
            main_window.layout.addLayout(test_layout)
            print("✅ Particle test buttons added")
        else:
            print("⚠️ Could not add test buttons - no main layout found")
            
    except Exception as e:
        print(f"⚠️ Could not add test buttons: {e}")


def test_explosion_effect(main_window):
    """Test explosion particle effect."""
    try:
        import numpy as np
        position = np.array([0, 0, 0])
        main_window.particle_integration.particle_system.emit_special_effect("explosion", position, 1.0)
        print("💥 Explosion effect triggered!")
    except Exception as e:
        print(f"Error triggering explosion: {e}")


def test_burst_effect(main_window):
    """Test burst particle effect."""
    try:
        import numpy as np
        from particle_system_pyside6 import ParticleType
        position = np.array([0, 0, 0])
        main_window.particle_integration.particle_system.emit_note_particles(60, 0.8, position, ParticleType.BURST)
        print("✨ Burst effect triggered!")
    except Exception as e:
        print(f"Error triggering burst: {e}")


def clear_all_particles(main_window):
    """Clear all particles."""
    try:
        main_window.particle_integration.particle_system.clear_all_particles()
        print("🧹 All particles cleared!")
    except Exception as e:
        print(f"Error clearing particles: {e}")


def add_keyboard_shortcuts(main_window):
    """Add keyboard shortcuts for particle effects."""
    
    if not hasattr(main_window, 'particle_integration'):
        print("❌ Particles not integrated - cannot add shortcuts")
        return
    
    try:
        from PySide6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+P: Toggle particles
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+P"), main_window)
        toggle_shortcut.activated.connect(
            lambda: toggle_particles(main_window)
        )
        
        # Ctrl+E: Test explosion
        explosion_shortcut = QShortcut(QKeySequence("Ctrl+E"), main_window)
        explosion_shortcut.activated.connect(
            lambda: test_explosion_effect(main_window)
        )
        
        # Ctrl+B: Test burst
        burst_shortcut = QShortcut(QKeySequence("Ctrl+B"), main_window)
        burst_shortcut.activated.connect(
            lambda: test_burst_effect(main_window)
        )
        
        # Ctrl+Shift+C: Clear particles
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), main_window)
        clear_shortcut.activated.connect(
            lambda: clear_all_particles(main_window)
        )
        
        print("✅ Particle keyboard shortcuts added:")
        print("   • Ctrl+P: Toggle particles")
        print("   • Ctrl+E: Test explosion")
        print("   • Ctrl+B: Test burst")
        print("   • Ctrl+Shift+C: Clear particles")
        
    except Exception as e:
        print(f"⚠️ Could not add keyboard shortcuts: {e}")


def toggle_particles(main_window):
    """Toggle particle effects on/off."""
    try:
        particle_system = main_window.particle_integration.particle_system
        particle_system.render_particles = not particle_system.render_particles
        
        if particle_system.render_particles:
            print("🎆 Particle effects enabled!")
        else:
            particle_system.clear_all_particles()
            print("🚫 Particle effects disabled!")
            
    except Exception as e:
        print(f"Error toggling particles: {e}")


def get_particle_status(main_window):
    """Get current particle system status."""
    
    if not hasattr(main_window, 'particle_integration'):
        return "Not integrated"
    
    try:
        stats = main_window.particle_integration.particle_system.get_performance_stats()
        if stats:
            active = stats.get('active_particles', 0)
            emitters = stats.get('active_emitters', 0)
            performance_mode = stats.get('performance_mode', False)
            
            status = f"Active: {active} particles, {emitters} emitters"
            if performance_mode:
                status += " (Performance Mode)"
            
            return status
        else:
            return "Disabled"
            
    except Exception as e:
        return f"Error: {e}"


# Complete integration function for easy copy-paste
def complete_particle_integration(main_window):
    """
    COMPLETE INTEGRATION FUNCTION
    
    Copy this entire function and call it at the end of your main window __init__:
    
    complete_particle_integration(self)
    """
    
    print("\n" + "="*60)
    print("🎆 COMPLETE PARTICLE EFFECTS INTEGRATION")
    print("="*60)
    
    # Step 1: Basic integration
    print("Step 1: Basic particle system integration...")
    success = add_particles_to_main_window(main_window)
    
    if not success:
        print("❌ Basic integration failed - stopping here")
        return False
    
    # Step 2: Add test buttons (optional)
    print("\nStep 2: Adding test buttons...")
    try:
        add_simple_particle_test_buttons(main_window)
    except:
        print("⚠️ Could not add test buttons (optional feature)")
    
    # Step 3: Add keyboard shortcuts (optional)
    print("\nStep 3: Adding keyboard shortcuts...")
    try:
        add_keyboard_shortcuts(main_window)
    except:
        print("⚠️ Could not add keyboard shortcuts (optional feature)")
    
    # Step 4: Show status
    print("\nStep 4: Final status check...")
    status = get_particle_status(main_window)
    print(f"Particle Status: {status}")
    
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


if __name__ == "__main__":
    print("🎆 Quick Particle Integration Helper")
    print("="*40)
    print()
    print("SIMPLE INTEGRATION:")
    print("Add this ONE LINE to the end of your main window __init__:")
    print()
    print("    from quick_particle_integration import add_particles_to_main_window")
    print("    add_particles_to_main_window(self)")
    print()
    print("COMPLETE INTEGRATION:")
    print("For full features, use this ONE LINE instead:")
    print()
    print("    from quick_particle_integration import complete_particle_integration")
    print("    complete_particle_integration(self)")
    print()
    print("Make sure you have both files in your project:")
    print("• particle_system_pyside6.py")
    print("• quick_particle_integration.py")
    print()
    print("That's it! Your MIDI visualizer will have particle effects! 🎉")
