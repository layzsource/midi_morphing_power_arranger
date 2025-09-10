# Quick fix for PyQt5/PySide6 compatibility issues
# Save this as qt_fix.py and run it to update your files

import os
import re

def fix_qt_imports_in_file(filepath):
    """Fix PyQt5 imports to PySide6 in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Store original content to check if changes are made
        original_content = content
        
        # Replace PyQt5 imports with PySide6
        replacements = [
            # Main PyQt5 to PySide6 replacements
            (r'from PyQt5\.QtWidgets import', 'from PySide6.QtWidgets import'),
            (r'from PyQt5\.QtCore import', 'from PySide6.QtCore import'),
            (r'from PyQt5\.QtGui import', 'from PySide6.QtGui import'),
            (r'import PyQt5\.QtWidgets', 'import PySide6.QtWidgets'),
            (r'import PyQt5\.QtCore', 'import PySide6.QtCore'),
            (r'import PyQt5\.QtGui', 'import PySide6.QtGui'),
            
            # Signal import differences
            (r'from PyQt5\.QtCore import pyqtSignal', 'from PySide6.QtCore import Signal'),
            (r'pyqtSignal', 'Signal'),
            
            # Some method name differences
            (r'\.exec_\(\)', '.exec()'),
        ]
        
        # Apply replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed Qt imports in: {filepath}")
            return True
        else:
            print(f"ℹ️ No Qt imports to fix in: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def fix_project_qt_imports():
    """Fix Qt imports in all Python files in the current directory."""
    
    # Files to check and fix
    python_files = [
        'scene_config_dialog.py',
        'config_dialog.py', 
        'dialogs.py',
        'performance_monitoring.py',
        'enhanced_scene_manager.py',
        'scene_manager_integration.py',
        'scene_manager.py',
        'main_window.py',
        'main_fixed_window.py'
    ]
    
    fixed_files = []
    
    for filename in python_files:
        if os.path.exists(filename):
            if fix_qt_imports_in_file(filename):
                fixed_files.append(filename)
        else:
            print(f"⚠️ File not found: {filename}")
    
    if fixed_files:
        print(f"\n🎉 Fixed Qt imports in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"   • {file}")
    else:
        print("\n✅ All files already have correct Qt imports")
    
    return len(fixed_files)

if __name__ == "__main__":
    print("🔧 Qt Compatibility Fix Tool")
    print("This tool converts PyQt5 imports to PySide6 imports\n")
    
    fixed_count = fix_project_qt_imports()
    
    if fixed_count > 0:
        print(f"\n✅ Successfully fixed {fixed_count} files")
        print("You can now run your application with:")
        print("   python main.py")
    else:
        print("\n✅ No files needed fixing")
        
    print("\nIf you still get import errors, check that these files exist:")
    print("   • enhanced_scene_manager.py")
    print("   • scene_manager_integration.py")
