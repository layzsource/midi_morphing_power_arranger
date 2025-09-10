# Quick fix for main.py
# The error is on line 407 in main.py

# FIND this line (around line 407):
# window.status_bar.showMessage("MIDI Morphing Visualizer - Ready", 5000)

# REPLACE with:
# window.statusBar().showMessage("MIDI Morphing Visualizer - Ready", 5000)

# Here's a script to automatically fix it:

import os
import re

def fix_main_py():
    """Fix the status_bar reference in main.py"""
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found")
        return False
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix the status_bar reference
        content = re.sub(
            r'window\.status_bar\.showMessage\(',
            'window.statusBar().showMessage(',
            content
        )
        
        if content != original_content:
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed status_bar reference in main.py")
            return True
        else:
            print("ℹ️ No status_bar references found in main.py")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing main.py: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing main.py status_bar reference")
    
    if fix_main_py():
        print("\n✅ Fixed! Try running your application now:")
        print("   python main.py")
    else:
        print("\n🔧 Manual fix needed:")
        print("1. Open main.py")
        print("2. Find line with: window.status_bar.showMessage")
        print("3. Replace with: window.statusBar().showMessage")
        print("4. Save and run: python main.py")
