import webbrowser
import os
import sys
from pathlib import Path

def launch_web_visualizer():
    """Launch the web-based MIDI visualizer in default browser."""
    visualizer_path = Path(__file__).parent / "web_visualizer.html"
    
    if visualizer_path.exists():
        # Open in default browser
        webbrowser.open(f"file://{visualizer_path.absolute()}")
        print("✅ Web visualizer launched in browser")
        print("Connect your MIDI device through the browser interface")
    else:
        print("❌ web_visualizer.html not found!")
        
if __name__ == "__main__":
    launch_web_visualizer()
