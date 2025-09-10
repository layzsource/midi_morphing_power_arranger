#!/usr/bin/env python3
"""
Fix for main_fixed_window.py status bar references
This script will fix ALL status_bar references in main_fixed_window.py
"""

import os
import re

def fix_main_fixed_window_py():
    """Fix all status_bar references in main_fixed_window.py"""
    
    filename = 'main_fixed_window.py'
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # All the status_bar patterns to fix
        replacements = [
            # Remove status bar creation (these should not exist in PySide6)
            (r'\s*self\.status_bar = QStatusBar\(\)\s*\n', ''),
            (r'\s*self\.setStatusBar\(self\.status_bar\)\s*\n', ''),
            
            # Replace method calls - the main issue
            (r'self\.status_bar\.showMessage\(', 'self.statusBar().showMessage('),
            (r'self\.status_bar\.addPermanentWidget\(', 'self.statusBar().addPermanentWidget('),
            (r'self\.status_bar\.clearMessage\(\)', 'self.statusBar().clearMessage()'),
            (r'self\.status_bar\.removeWidget\(', 'self.statusBar().removeWidget('),
            (r'self\.status_bar\.addWidget\(', 'self.statusBar().addWidget('),
        ]
        
        changes_made = 0
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made += len(re.findall(pattern, content))
                content = new_content
        
        if content != original_content:
            # Create backup
            backup_filename = f"{filename}.backup"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"📋 Backup created: {backup_filename}")
            
            # Write fixed version
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {changes_made} status bar references in {filename}")
            return True
        else:
            print(f"ℹ️ No status bar issues found in {filename}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def manual_fix_instructions():
    """Provide manual fix instructions for main_fixed_window.py"""
    
    print("\n🔧 MANUAL FIX INSTRUCTIONS for main_fixed_window.py:")
    print("If the automatic fix doesn't work, manually replace these:")
    print()
    print("1. Find ALL instances of 'self.status_bar.' and replace with 'self.statusBar().'")
    print("   Examples:")
    print("   OLD: self.status_bar.showMessage(...)")
    print("   NEW: self.statusBar().showMessage(...)")
    print()
    print("   OLD: self.status_bar.addPermanentWidget(...)")
    print("   NEW: self.statusBar().addPermanentWidget(...)")
    print()
    print("2. Remove these lines if they exist:")
    print("   self.status_bar = QStatusBar()")
    print("   self.setStatusBar(self.status_bar)")
    print()
    print("3. In PySide6, QMainWindow has a built-in statusBar() method")
    print("   You don't need to create your own status_bar attribute")

if __name__ == "__main__":
    print("🔧 Fixing Status Bar References in main_fixed_window.py")
    print("=" * 60)
    
    if fix_main_fixed_window_py():
        print(f"\n🚀 Fixed! Try running your application now:")
        print("   python main_fixed_window.py")
        print("   OR")
        print("   python main.py")
        
    else:
        print("\n🤔 No automatic fixes applied")
        manual_fix_instructions()
    
    print("\n📋 After fixing, you should have:")
    print("• No more status_bar attribute errors")
    print("• Working status bar with performance monitoring")
    print("• Enhanced scene manager with morphing capabilities")
    print("• Particle effects integration (if enabled)")
