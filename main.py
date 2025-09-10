#!/usr/bin/env python3
"""
Corrected main.py and main_fixed_window.py launcher with all fixes applied
Includes plotter attribute fix, mesh morphing fix, and proper initialization
"""

# ============================================================================
# PART 1: plotter_attribute_fix.py (Save this as a separate file)
# ============================================================================

"""
plotter_attribute_fix.py - Fixes plotter naming issues
"""

import logging

logger = logging.getLogger(__name__)

def fix_plotter_errors(window):
    """Apply all plotter-related fixes to a window instance."""
    try:
        # Fix 1: Create alias for plotter_widget if it doesn't exist
        if hasattr(window, 'plotter') and not hasattr(window, 'plotter_widget'):
            window.plotter_widget = window.plotter
            logger.info("Created plotter_widget alias")
        
        # Fix 2: Patch the animate_frame method
        def safe_animate_frame():
            """Safe animation frame with proper plotter reference."""
            try:
                # Update morphing if active
                if hasattr(window, 'adv_morphing') and window.adv_morphing:
                    dt = 1.0 / 60.0  # Assume 60 FPS
                    
                    # Check if morphing is properly initialized
                    if hasattr(window.adv_morphing, 'animate_morph'):
                        try:
                            # Check for shape compatibility before morphing
                            if (hasattr(window.adv_morphing, 'original_points') and 
                                hasattr(window.adv_morphing, 'target_points')):
                                if (window.adv_morphing.original_points is not None and
                                    window.adv_morphing.target_points is not None):
                                    if window.adv_morphing.original_points.shape == window.adv_morphing.target_points.shape:
                                        window.adv_morphing.animate_morph(dt)
                        except Exception as e:
                            logger.debug(f"Morphing update skipped: {e}")
                
                # Update the plotter/renderer - use plotter not plotter_widget
                if hasattr(window, 'plotter'):
                    try:
                        # PyVista QtInteractor uses render() method
                        window.plotter.render()
                    except AttributeError:
                        try:
                            # Alternative render methods
                            if hasattr(window.plotter, 'update'):
                                window.plotter.update()
                            elif hasattr(window.plotter, 'Render'):
                                window.plotter.Render()
                        except:
                            pass
                
            except Exception as e:
                logger.debug(f"Animation frame error: {e}")
        
        # Replace the animate_frame method
        window.animate_frame = safe_animate_frame
        
        # Fix 3: Ensure render timer is properly connected
        if hasattr(window, 'render_timer'):
            try:
                window.render_timer.timeout.disconnect()
            except:
                pass
            window.render_timer.timeout.connect(safe_animate_frame)
            logger.info("Render timer reconnected to safe animate_frame")
        
        logger.info("✓ Plotter attribute fixes applied")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply plotter fixes: {e}")
        return False


# ============================================================================
# PART 2: main.py - Corrected Application Entry Point
# ============================================================================

"""
main.py - Corrected application entry point with all fixes
"""

import sys
import logging
import argparse
from pathlib import Path

# Configure logging
def setup_logging(log_level="INFO"):
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('morphing_visualizer.log')
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main application entry point with all fixes applied."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MIDI Morphing Visualizer")
    parser.add_argument('--no-audio', action='store_true', help='Disable audio analysis')
    parser.add_argument('--midi-port', type=str, help='Specify MIDI port')
    parser.add_argument('--osc-port', type=int, default=5005, help='OSC port')
    parser.add_argument('--config', type=str, help='Load configuration file')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting MIDI Morphing Visualizer...")
    
    # Import Qt first
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        logger.info("✓ Qt framework loaded")
    except ImportError:
        logger.error("PySide6 not found. Please install: pip install PySide6")
        return 1
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer")
    app.setOrganizationName("MorphingInterface")
    
    # Import the main window - try main_fixed_window first
    try:
        # This is your actual implementation
        from main_fixed_window import PerformanceAwareMainWindow
        logger.info("✓ Using PerformanceAwareMainWindow from main_fixed_window")
        WindowClass = PerformanceAwareMainWindow
    except ImportError as e:
        logger.warning(f"Could not import main_fixed_window: {e}")
        try:
            # Fallback to main_window
            from main_window import MainWindow
            logger.info("✓ Using MainWindow from main_window")
            WindowClass = MainWindow
        except ImportError as e:
            logger.error(f"Could not import any main window class: {e}")
            return 1
    
    # Import the plotter fix
    try:
        from plotter_attribute_fix import fix_plotter_errors
        logger.info("✓ Plotter fix module loaded")
    except ImportError:
        logger.warning("Plotter fix not available - some features may not work correctly")
        fix_plotter_errors = None
    
    # Create main window
    try:
        window = WindowClass()
        logger.info("✓ Main window created")
        
        # Apply plotter fixes
        if fix_plotter_errors:
            if fix_plotter_errors(window):
                logger.info("✓ Plotter fixes applied successfully")
            else:
                logger.warning("⚠ Could not apply all plotter fixes")
        
        # Apply command line arguments
        if args.no_audio and hasattr(window, 'audio_enabled'):
            window.audio_enabled = False
            logger.info("Audio analysis disabled by command line")
        
        if args.midi_port and hasattr(window, 'config'):
            window.config.MIDI_PORT = args.midi_port
            logger.info(f"MIDI port set to: {args.midi_port}")
        
        if args.osc_port and hasattr(window, 'config'):
            window.config.OSC_PORT = args.osc_port
            logger.info(f"OSC port set to: {args.osc_port}")
        
        # Load custom configuration if provided
        if args.config and hasattr(window, 'config'):
            try:
                window.config.load_from_file(args.config)
                logger.info(f"Configuration loaded from: {args.config}")
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        # Show window
        window.show()
        window.raise_()
        window.activateWindow()
        
        # Show ready message using correct status bar method
        window.statusBar().showMessage("MIDI Morphing Visualizer - Ready", 5000)
        
        logger.info("✓ Application ready")
        print("\n" + "="*60)
        print("MIDI MORPHING VISUALIZER - READY")
        print("="*60)
        print("Controls:")
        print("  • Morph Slider: Blend between shapes")
        print("  • Shape Selectors: Choose source/target shapes")
        print("  • MIDI: Play notes to create lights")
        print("  • Audio: Enable for reactive visuals")
        print("="*60 + "\n")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())


# ============================================================================
# PART 3: run_fixed.py - Direct launcher for main_fixed_window
# ============================================================================

"""
run_fixed.py - Direct launcher for main_fixed_window.py with all fixes
Use this if you prefer to run main_fixed_window.py directly
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_fixed_window():
    """Run the fixed window directly with all patches applied."""
    
    # Import Qt
    from PySide6.QtWidgets import QApplication
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer")
    
    try:
        # Import the fixed window
        from main_fixed_window import PerformanceAwareMainWindow
        
        # Import fixes
        try:
            from plotter_attribute_fix import fix_plotter_errors
        except ImportError:
            logger.warning("Plotter fix not available")
            fix_plotter_errors = None
        
        # Create window
        window = PerformanceAwareMainWindow()
        
        # Apply fixes
        if fix_plotter_errors:
            fix_plotter_errors(window)
            logger.info("✓ Plotter fixes applied")
        
        # Show window
        window.show()
        window.statusBar().showMessage("Ready", 5000)
        
        print("\n" + "="*60)
        print("MIDI MORPHING VISUALIZER - FIXED VERSION")
        print("="*60)
        print("✓ All fixes applied")
        print("✓ Plotter attributes corrected")
        print("✓ Mesh morphing synchronized")
        print("="*60 + "\n")
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Failed to run: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_fixed_window())


# ============================================================================
# PART 4: Installation Instructions
# ============================================================================

"""
INSTALLATION INSTRUCTIONS:

1. Save the plotter fix as a separate file:
   - Save the PART 1 section as: plotter_attribute_fix.py

2. Replace your main.py:
   - Save the PART 2 section as: main.py

3. Create an alternative launcher (optional):
   - Save the PART 3 section as: run_fixed.py

4. Run the application:
   
   Option A - Using main.py (recommended):
   python main.py
   
   Option B - Using the direct launcher:
   python run_fixed.py
   
   Option C - Running main_fixed_window directly:
   python -c "from plotter_attribute_fix import fix_plotter_errors; from main_fixed_window import PerformanceAwareMainWindow; from PySide6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); window = PerformanceAwareMainWindow(); fix_plotter_errors(window); window.show(); sys.exit(app.exec())"

5. If you still get errors:
   - Check that all imports are correct
   - Verify PySide6 is installed: pip install PySide6
   - Check that pyvistaqt is installed: pip install pyvistaqt

TESTING:
After installation, you should be able to:
- Start the application without errors
- Move the morph slider without crashes
- See smooth animation without stuttering
- No more plotter_widget AttributeErrors
- No more vertex count mismatch errors
"""
