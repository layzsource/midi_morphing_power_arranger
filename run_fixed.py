#!/usr/bin/env python3
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Fix geometry imports FIRST
    import geometry
    if hasattr(geometry, 'safe_blend_meshes') and not hasattr(geometry, 'blend_meshes'):
        geometry.blend_meshes = geometry.safe_blend_meshes
        logger.info("✓ Fixed geometry imports")
    
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Now import main window (after fixing geometry)
    from main_fixed_window import PerformanceAwareMainWindow
    
    # Import plotter fix if available
    try:
        from plotter_attribute_fix import fix_plotter_errors
    except:
        fix_plotter_errors = None
    
    # Create and fix window
    window = PerformanceAwareMainWindow()
    if fix_plotter_errors:
        fix_plotter_errors(window)
    
    window.show()
    window.statusBar().showMessage("Ready", 5000)
    
    print("\n✓ Application started with all fixes\n")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
