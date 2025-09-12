#!/usr/bin/env python3
"""
Fix for enhanced_main_step2_particles.py Syntax Error
Removes the stray '**panel**' text causing SyntaxError on line 2225
"""

import os
import re
import sys

def fix_particles_syntax_error():
    """Fix the syntax error in enhanced_main_step2_particles.py"""
    
    filename = "enhanced_main_step2_particles.py"
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return False
    
    try:
        print(f"🔧 Fixing syntax error in {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix the specific syntax error on line 2225
        # Remove any stray text after sys.exit(main())
        content = re.sub(
            r'sys\.exit\(main\(\)\)\s*\*\*panel\*\*',
            'sys.exit(main())',
            content,
            flags=re.MULTILINE
        )
        
        # Also fix any other variations of this pattern
        content = re.sub(
            r'sys\.exit\(main\(\)\)\s*\*\*[^*]*\*\*',
            'sys.exit(main())',
            content,
            flags=re.MULTILINE
        )
        
        # Fix any standalone **panel** text that might be causing issues
        content = re.sub(
            r'\s*\*\*panel\*\*\s*',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Check if we made any changes
        if content != original_content:
            # Create backup
            backup_filename = f"{filename}.backup"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"📋 Created backup: {backup_filename}")
            
            # Write fixed content
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed syntax error in enhanced_main_step2_particles.py")
            return True
        else:
            print("ℹ️ No syntax errors found to fix")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def validate_python_syntax(filename):
    """Validate that the Python file has correct syntax."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the code
        compile(content, filename, 'exec')
        print(f"✅ {filename} has valid Python syntax")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error validating {filename}: {e}")
        return False

def check_common_syntax_issues():
    """Check for other common syntax issues in the file."""
    
    filename = "enhanced_main_step2_particles.py"
    
    if not os.path.exists(filename):
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n🔍 Checking {filename} for common syntax issues:")
        
        issues_found = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for stray markdown formatting
            if '**' in line_stripped and not line_stripped.startswith('#'):
                issues_found.append(f"Line {i}: Stray markdown formatting: {line_stripped}")
            
            # Check for unmatched parentheses at end of file
            if i > len(lines) - 10:  # Last 10 lines
                if line_stripped.startswith('sys.exit(') and not line_stripped.endswith(')'):
                    issues_found.append(f"Line {i}: Incomplete sys.exit() call: {line_stripped}")
        
        if issues_found:
            print("⚠️ Potential syntax issues found:")
            for issue in issues_found:
                print(f"   • {issue}")
        else:
            print("✅ No common syntax issues found")
            
    except Exception as e:
        print(f"❌ Error checking syntax issues: {e}")

def main():
    """Main function to fix the syntax error."""
    
    print("🔧 Enhanced Main Step 2 Particles - Syntax Error Fix")
    print("=" * 55)
    print()
    
    # Check if file exists
    if not os.path.exists("enhanced_main_step2_particles.py"):
        print("❌ enhanced_main_step2_particles.py not found in current directory")
        print("\nPlease run this script from the directory containing the file.")
        return 1
    
    # First, validate current syntax
    print("📋 Current syntax validation:")
    syntax_valid = validate_python_syntax("enhanced_main_step2_particles.py")
    
    if syntax_valid:
        print("✅ File already has valid syntax - no fix needed!")
        return 0
    
    # Check for common issues
    check_common_syntax_issues()
    
    # Apply the fix
    print("\n🔧 Applying syntax fix...")
    if fix_particles_syntax_error():
        print("\n📋 Post-fix syntax validation:")
        if validate_python_syntax("enhanced_main_step2_particles.py"):
            print("\n🎉 SUCCESS! Syntax error has been fixed.")
            print("\n🚀 You can now run the file:")
            print("   python enhanced_main_step2_particles.py")
        else:
            print("\n⚠️ Fix applied but syntax issues may remain.")
            print("Please check the file manually for any remaining issues.")
        
        return 0
    else:
        print("\n❌ Could not automatically fix the syntax error.")
        print("\n🔧 Manual fix instructions:")
        print("1. Open enhanced_main_step2_particles.py in a text editor")
        print("2. Go to line 2225 (or search for 'sys.exit(main())')")
        print("3. Remove any text after 'sys.exit(main())' on that line")
        print("4. The line should only contain: sys.exit(main())")
        print("5. Save the file and try running it again")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
