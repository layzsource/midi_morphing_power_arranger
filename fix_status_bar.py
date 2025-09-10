#!/usr/bin/env python3
"""
Complete fix for all status_bar references in the project.
This script will find and fix ALL status_bar issues automatically.
"""

import os
import re

def fix_all_status_bar_references():
    """Fix all status_bar references in all Python files."""
    
    files_to_fix = [
        'main_fixed_window.py',
        'main.py',
        'performance_monitoring.py',
        'config_dialog.py',
        'dialogs.py'
    ]
    
    fixed_files = []
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            if fix_status_bar_in_file(filename):
                fixed_files.append(filename)
                
    return fixed_files

def fix_status_bar_in_file(filepath):
    """Fix status_bar references in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # All the status_bar patterns to fix
        replacements = [
            # Remove status bar creation (these should not exist in PySide6)
            (r'\s*self\.status_bar = QStatusBar\(\)\s*\n', ''),
            (r'\s*self\.setStatusBar\(self\.status_bar\)\s*\n', ''),
            
            # Replace method calls
            (r'self\.status_bar\.showMessage\(', 'self.statusBar().showMessage('),
            (r'self\.status_bar\.addPermanentWidget\(', 'self.statusBar().addPermanentWidget('),
            (r'self\.status_bar\.clearMessage\(\)', 'self.statusBar().clearMessage()'),
            (r'self\.status_bar\.removeWidget\(', 'self.statusBar().removeWidget('),
            (r'self\.status_bar\.addWidget\(', 'self.statusBar().addWidget('),
            
            # Fix any window.status_bar references (from main.py)
            (r'window\.status_bar\.showMessage\(', 'window.statusBar().showMessage('),
            (r'window\.status_bar\.addPermanentWidget\(', 'window.statusBar().addPermanentWidget('),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed status bar references in {filepath}")
            return True
        else:
            print(f"ℹ️ No status bar issues found in {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def manual_fix_instructions():
    """Provide manual fix instructions."""
    
    print("\n🔧 MANUAL FIX INSTRUCTIONS:")
    print("If the automatic fix doesn't work, manually replace these:")
    print()
    print("1. In main_fixed_window.py, find line 390:")
    print("   OLD: self.status_bar.showMessage(...)")
    print("   NEW: self.statusBar().showMessage(...)")
    print()
    print("2. In _setup_ui method, remove these lines if they exist:")
    print("   self.status_bar = QStatusBar()")
    print("   self.setStatusBar(self.status_bar)")
    print()
    print("3. Replace ALL occurrences of:")
    print("   self.status_bar.  →  self.statusBar().")
    print("   window.status_bar.  →  window.statusBar().")

if __name__ == "__main__":
    print("🔧 Complete Status Bar Fix Tool")
    print("This fixes ALL status_bar references in your project\n")
    
    fixed_files = fix_all_status_bar_references()
    
    if fixed_files:
        print(f"\n✅ Fixed status bar issues in {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"   • {file}")
        
        print(f"\n🚀 Try running your application now:")
        print("   python main.py")
        
    else:
        print("\n🤔 No automatic fixes applied")
        manual_fix_instructions()
    
    print("\n📋 Quick Test:")
    print("After fixing, you should be able to:")
    print("• Start the application without status_bar errors")
    print("• See the enhanced scene manager with 4 objects")
    print("• Use the morph slider to transform shapes")
    print("• Use keyboard shortcuts (1-4 for presets)")
