#!/usr/bin/env python3
"""
Fix the import error in main_fixed_window.py
Change 'blend_meshes' to 'safe_blend_meshes' in the import statement
"""

import os
import re

def fix_import_error():
    """Fix the blend_meshes import error in main_fixed_window.py"""
    
    filename = 'main_fixed_window.py'
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix the import statement
        content = re.sub(
            r'from geometry import ([^,\n]*,?\s*)*blend_meshes([^,\n]*)',
            lambda m: m.group(0).replace('blend_meshes', 'safe_blend_meshes'),
            content
        )
        
        # Also fix any usage of blend_meshes in the code
        content = re.sub(r'\bblend_meshes\b', 'safe_blend_meshes', content)
        
        if content != original_content:
            # Create backup
            backup_filename = f"{filename}.backup"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"📋 Backup created: {backup_filename}")
            
            # Write fixed version
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed import error in {filename}")
            print("   Changed 'blend_meshes' to 'safe_blend_meshes'")
            return True
        else:
            print(f"ℹ️ No import issues found in {filename}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def check_geometry_functions():
    """Check what functions are available in geometry.py"""
    
    if not os.path.exists('geometry.py'):
        print("❌ geometry.py not found")
        return
    
    try:
        with open('geometry.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find function definitions
        functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
        
        print("\n📚 Functions available in geometry.py:")
        for func in functions:
            print(f"  • {func}")
            
        # Check specifically for blend-related functions
        blend_functions = [f for f in functions if 'blend' in f.lower()]
        if blend_functions:
            print(f"\n🔀 Blend-related functions found:")
            for func in blend_functions:
                print(f"  • {func}")
                
    except Exception as e:
        print(f"❌ Error reading geometry.py: {e}")

if __name__ == "__main__":
    print("🔧 Fix Import Error Tool")
    print("=" * 40)
    
    # Check what's available in geometry.py
    check_geometry_functions()
    
    # Fix the import error
    print("\n🔨 Fixing import statement...")
    if fix_import_error():
        print("\n✅ Import error fixed!")
        print("\n🚀 Try running your application now:")
        print("   python main.py")
        print("   OR")
        print("   python main_fixed_window.py")
    else:
        print("\n🤔 No import issues found to fix")
        print("\nℹ️ Manual fix instructions:")
        print("1. Open main_fixed_window.py")
        print("2. Find the line: from geometry import ... blend_meshes ...")
        print("3. Change 'blend_meshes' to 'safe_blend_meshes'")
        print("4. Save and try running again")
    
    print("\n📋 The error occurred because:")
    print("• The function was renamed from 'blend_meshes' to 'safe_blend_meshes'")
    print("• The import statement needs to be updated to match")
