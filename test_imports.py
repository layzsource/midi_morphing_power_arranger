import sys
import traceback

def test_import(module_name):
    try:
        if module_name == "config":
            from config import Config
            config = Config()
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "exceptions":
            from exceptions import MeshCreationError
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "profiler":
            from profiler import profiler, profile_function
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "geometry":
            from geometry import create_initial_meshes, blend_meshes
            print(f"✓ {module_name} imported successfully")
            # Test mesh creation
            meshes = create_initial_meshes(20)  # Low resolution for speed
            print(f"✓ Created {len(meshes)} meshes successfully")
            return True
        elif module_name == "midi_osc":
            from midi_osc import IntegratedMidiOscThread
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "audio":
            from audio import AudioAnalysisThread
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "dialogs":
            from dialogs import ConfigDialog, PerformanceDialog
            print(f"✓ {module_name} imported successfully")
            return True
        elif module_name == "main_window":
            from main_window import MainWindow
            print(f"✓ {module_name} imported successfully")
            return True
            
    except Exception as e:
        print(f"✗ {module_name} failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    modules = ["exceptions", "config", "profiler", "geometry", "midi_osc", "audio", "dialogs", "main_window"]
    
    for module in modules:
        print(f"\nTesting {module}...")
        test_import(module)
        print("-" * 40)
