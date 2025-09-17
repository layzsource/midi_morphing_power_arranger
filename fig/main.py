#!/usr/bin/env python3
"""
MMPA (Midi Morphing Power Arranger) - Main Entry Point
The Language of Signals Becoming Form

Professional-grade audiovisual synthesis engine for live performance,
education, and creative exploration.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from core.app import EnhancedApplication

def setup_logging():
    """Configure logging for MMPA."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mmpa.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point for MMPA."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting MMPA - Midi Morphing Power Arranger")
    logger.info("The Language of Signals Becoming Form")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MMPA - Midi Morphing Power Arranger")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MMPA Project")

    # Set application attributes for better performance
    app.setAttribute(Qt.AA_UseDesktopOpenGL)
    app.setAttribute(Qt.AA_ShareOpenGLContexts)

    try:
        # Create and launch the enhanced application
        enhanced_app = EnhancedApplication()
        enhanced_app.show()

        logger.info("MMPA initialized successfully")
        return app.exec()

    except Exception as e:
        logger.error(f"Failed to start MMPA: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())