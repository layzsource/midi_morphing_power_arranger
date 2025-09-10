"""
Fix for plotter_widget AttributeError in main_window.py
Resolves naming inconsistencies and provides proper render updates
"""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

class PlotterAttributeFix:
    """Fixes plotter attribute naming issues in the main window."""
    
    @staticmethod
    def patch_main_window(window):
        """Apply fixes to an existing main window instance."""
        
        # Fix 1: Create alias for plotter_widget if it doesn't exist
        if hasattr(window, 'plotter') and not hasattr(window, 'plotter_widget'):
            window.plotter_widget = window.plotter
            logger.info("Created plotter_widget alias")
        
        # Fix 2: Patch the animate_frame method
        original_animate = window.animate_frame if hasattr(window, 'animate_frame') else None
        
        def safe_animate_frame():
            """Safe animation frame with proper plotter reference."""
            try:
                # Update morphing if active
                if hasattr(window, 'adv_morphing') and window.adv_morphing:
                    dt = 1.0 / 60.0  # Assume 60 FPS
                    
                    # Check if morphing is properly initialized
                    if hasattr(window.adv_morphing, 'animate_morph'):
                        try:
                            window.adv_morphing.animate_morph(dt)
                        except Exception as e:
                            logger.debug(f"Morphing update skipped: {e}")
                
                # Update the plotter/renderer
                if hasattr(window, 'plotter'):
                    # Use the correct plotter reference
                    if hasattr(window.plotter, 'update'):
                        window.plotter.update()
                    elif hasattr(window.plotter, 'render'):
                        window.plotter.render()
                    elif hasattr(window.plotter, 'Render'):
                        window.plotter.Render()
                    else:
                        # Try the interactor's render method
                        if hasattr(window.plotter, 'interactor'):
                            if hasattr(window.plotter.interactor, 'Render'):
                                window.plotter.interactor.Render()
                
                elif hasattr(window, 'plotter_widget'):
                    # Fallback to plotter_widget if it exists
                    if hasattr(window.plotter_widget, 'update'):
                        window.plotter_widget.update()
                    elif hasattr(window.plotter_widget, 'render'):
                        window.plotter_widget.render()
                
            except AttributeError as e:
                # Log but don't crash - animation continues
                logger.debug(f"Animation frame attribute issue: {e}")
            except Exception as e:
                logger.error(f"Animation frame error: {e}")
        
        # Replace the animate_frame method
        window.animate_frame = safe_animate_frame
        
        # Fix 3: Ensure render timer is properly connected
        if hasattr(window, 'render_timer'):
            # Disconnect any existing connections
            try:
                window.render_timer.timeout.disconnect()
            except:
                pass
            
            # Reconnect to the safe method
            window.render_timer.timeout.connect(safe_animate_frame)
            logger.info("Render timer reconnected to safe animate_frame")
        
        logger.info("✓ Plotter attribute fixes applied")


def create_fixed_animate_frame(window):
    """Create a fixed animate_frame method for the window."""
    
    def animate_frame():
        """Animation frame with comprehensive error handling."""
        try:
            # 1. Update morphing animation if active
            if hasattr(window, 'morph_animation_active') and window.morph_animation_active:
                if hasattr(window, 'adv_morphing'):
                    try:
                        dt = 1.0 / 60.0  # 60 FPS target
                        window.adv_morphing.animate_morph(dt)
                    except ValueError as e:
                        logger.debug(f"Morphing skipped: {e}")
                        window.morph_animation_active = False
            
            # 2. Update mesh if morph slider changed
            if hasattr(window, '_update_mesh_morph'):
                try:
                    window._update_mesh_morph()
                except Exception as e:
                    logger.debug(f"Mesh update skipped: {e}")
            
            # 3. Update lights and effects
            if hasattr(window, '_update_lights'):
                try:
                    window._update_lights()
                except Exception as e:
                    logger.debug(f"Light update skipped: {e}")
            
            # 4. Render the scene - try multiple methods
            rendered = False
            
            # Try plotter first
            if hasattr(window, 'plotter'):
                plotter = window.plotter
                
                # Try different render methods
                render_methods = [
                    'update',
                    'render', 
                    'Render',
                    'iren.Render' if hasattr(plotter, 'iren') else None,
                    'interactor.Render' if hasattr(plotter, 'interactor') else None,
                    'renderWindow.Render' if hasattr(plotter, 'renderWindow') else None,
                ]
                
                for method_path in render_methods:
                    if method_path:
                        try:
                            if '.' in method_path:
                                # Handle nested attributes
                                obj = plotter
                                for attr in method_path.split('.'):
                                    obj = getattr(obj, attr)
                                obj()
                            else:
                                # Direct method
                                method = getattr(plotter, method_path, None)
                                if method:
                                    method()
                            rendered = True
                            break
                        except:
                            continue
            
            # Fallback to plotter_widget
            if not rendered and hasattr(window, 'plotter_widget'):
                try:
                    if hasattr(window.plotter_widget, 'update'):
                        window.plotter_widget.update()
                    elif hasattr(window.plotter_widget, 'render'):
                        window.plotter_widget.render()
                except:
                    pass
            
            # 5. Update status if needed
            if hasattr(window, '_update_status'):
                try:
                    window._update_status()
                except:
                    pass
                    
        except Exception as e:
            # Log error but don't stop animation
            logger.error(f"Animation frame failed: {e}", exc_info=True)
    
    return animate_frame


# Quick fix to be called from main.py or directly
def fix_plotter_errors(window):
    """Apply all plotter-related fixes to a window instance."""
    try:
        # Apply attribute fixes
        PlotterAttributeFix.patch_main_window(window)
        
        # Create and set fixed animate_frame
        window.animate_frame = create_fixed_animate_frame(window)
        
        # Ensure timer is running
        if hasattr(window, 'render_timer'):
            if not window.render_timer.isActive():
                window.render_timer.start(16)  # ~60 FPS
        
        logger.info("✓ All plotter fixes applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply plotter fixes: {e}")
        return False


# Monkey patch for the class itself
def patch_enhanced_main_window_class():
    """Patch the EnhancedMainWindow class to fix the issue permanently."""
    
    import sys
    import importlib
    
    try:
        # Try to import the main_window module
        if 'main_window' in sys.modules:
            main_window_module = sys.modules['main_window']
        else:
            main_window_module = importlib.import_module('main_window')
        
        # Get the EnhancedMainWindow class
        if hasattr(main_window_module, 'EnhancedMainWindow'):
            EnhancedMainWindow = main_window_module.EnhancedMainWindow
            
            # Store original __init__
            original_init = EnhancedMainWindow.__init__
            
            # Create patched __init__
            def patched_init(self, *args, **kwargs):
                # Call original init
                original_init(self, *args, **kwargs)
                
                # Apply fixes after initialization
                fix_plotter_errors(self)
            
            # Replace __init__
            EnhancedMainWindow.__init__ = patched_init
            
            logger.info("✓ EnhancedMainWindow class patched")
            return True
            
    except Exception as e:
        logger.error(f"Failed to patch class: {e}")
        return False


# Standalone fix function for immediate use
def immediate_fix():
    """Immediate fix to be run from Python console or script."""
    
    import sys
    from PySide6.QtWidgets import QApplication
    
    # Get the application instance
    app = QApplication.instance()
    if not app:
        logger.error("No QApplication instance found")
        return False
    
    # Find main windows
    windows_fixed = 0
    for widget in app.topLevelWidgets():
        if hasattr(widget, 'plotter') or hasattr(widget, 'plotter_widget'):
            logger.info(f"Found window to fix: {widget.__class__.__name__}")
            if fix_plotter_errors(widget):
                windows_fixed += 1
    
    if windows_fixed > 0:
        logger.info(f"✓ Fixed {windows_fixed} window(s)")
        return True
    else:
        logger.warning("No windows found to fix")
        return False


# Integration code for main.py
def integrate_plotter_fix(main_py_path="main.py"):
    """Generate integration code for main.py."""
    
    integration_code = '''
# Add this after imports in main.py:
from plotter_attribute_fix import fix_plotter_errors, patch_enhanced_main_window_class

# Add this before creating the main window:
patch_enhanced_main_window_class()

# Or add this after creating the main window:
window = EnhancedMainWindow()  # or PerformanceAwareMainWindow()
fix_plotter_errors(window)
'''
    
    print("Integration Instructions:")
    print("=" * 60)
    print(integration_code)
    print("=" * 60)
    
    return integration_code


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Plotter Attribute Fix Utility")
    print("-" * 40)
    
    # Try immediate fix
    print("Attempting immediate fix...")
    if immediate_fix():
        print("✓ Immediate fix applied")
    else:
        print("ℹ No running application found")
    
    # Show integration instructions
    print("\n" + "=" * 40)
    integrate_plotter_fix()
