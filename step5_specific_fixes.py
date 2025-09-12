#!/usr/bin/env python3
"""
Specific fixes for known Step 5 Complete Features syntax patterns
This addresses the exact issues found in your step5_complete_all_features.py file
"""

import os
import re
import sys

def fix_step5_specific_patterns():
    """Fix specific patterns found in step5_complete_all_features.py"""
    filename = "step5_complete_all_features.py"
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return False
    
    print(f"🔧 Applying specific fixes to {filename}...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Fix 1: Remove stray '**panel**' or similar markdown
        if '**panel**' in content:
            content = re.sub(r'\s*\*\*panel\*\*\s*', '', content, flags=re.MULTILINE)
            fixes_applied.append("Removed stray **panel** text")
        
        # Fix 2: Fix incomplete preset loading code
        # Pattern: value = int(preset_data[
        pattern1 = r'value = int\(preset_data\[\s*$'
        if re.search(pattern1, content, re.MULTILINE):
            # Find and complete the incomplete line
            content = re.sub(
                r'value = int\(preset_data\[\s*$',
                "value = int(preset_data.get('global_morph_factor', 50) * 100)",
                content,
                flags=re.MULTILINE
            )
            fixes_applied.append("Fixed incomplete preset loading code")
        
        # Fix 3: Fix incomplete object definitions
        # Pattern: 'note_range': (72, 95),  ##!/usr/bin/env python3
        pattern2 = r"'note_range': \(\d+, \d+\),\s*##!/usr/bin/env python3.*$"
        if re.search(pattern2, content, re.MULTILINE | re.DOTALL):
            content = re.sub(
                r"('note_range': \(\d+, \d+\),)\s*##!/usr/bin/env python3.*",
                r"\1",
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            fixes_applied.append("Fixed incomplete object definition")
        
        # Fix 4: Fix duplicate shebang lines
        shebang_count = content.count('#!/usr/bin/env python3')
        if shebang_count > 1:
            # Keep only the first shebang
            content = content.replace('#!/usr/bin/env python3', '', shebang_count - 1)
            fixes_applied.append(f"Removed {shebang_count - 1} duplicate shebang lines")
        
        # Fix 5: Fix incomplete function definitions or calls
        # Look for lines that start a function but are incomplete
        pattern3 = r'def \w+\([^)]*$'
        incomplete_defs = re.findall(pattern3, content, re.MULTILINE)
        if incomplete_defs:
            for incomplete in incomplete_defs:
                # Try to complete with a closing parenthesis and colon
                content = content.replace(incomplete, incomplete + '):\n    """Placeholder implementation"""\n    pass')
            fixes_applied.append(f"Fixed {len(incomplete_defs)} incomplete function definitions")
        
        # Fix 6: Fix hanging method chains or incomplete expressions
        # Pattern: .setWidgetResizable(Tru
        pattern4 = r'\.setWidgetResizable\(Tru\s*$'
        if re.search(pattern4, content, re.MULTILINE):
            content = re.sub(pattern4, '.setWidgetResizable(True)', content, flags=re.MULTILINE)
            fixes_applied.append("Fixed incomplete setWidgetResizable call")
        
        # Fix 7: Fix incomplete color assignments
        # Pattern: 'current_color': list(color)
        # Make sure color-related assignments are complete
        if 'list(color)' in content and 'current_color' in content:
            # This seems fine, but check for incomplete variations
            pattern5 = r"'current_color': list\(color\)\s*#.*incomplete.*$"
            if re.search(pattern5, content, re.MULTILINE):
                content = re.sub(pattern5, "'current_color': list(color),", content, flags=re.MULTILINE)
                fixes_applied.append("Fixed incomplete color assignment")
        
        # Fix 8: Fix incomplete import statements
        # Look for imports that might be cut off
        pattern6 = r'from\s+\w+\.\w+\s+import\s+\([^)]*$'
        incomplete_imports = re.findall(pattern6, content, re.MULTILINE)
        if incomplete_imports:
            fixes_applied.append(f"Warning: Found {len(incomplete_imports)} potentially incomplete imports")
        
        # Fix 9: Ensure proper file ending
        if not content.endswith('\n'):
            content += '\n'
            fixes_applied.append("Added final newline")
        
        # Fix 10: Remove any trailing incomplete code fragments at end of file
        # Look for common incomplete endings
        endings_to_remove = [
            r'step5_complete_all_features\.py\s*$',
            r'#\s*C\d+-B\d+.*$',
            r'fix_particles_syntax\.py\s*$',
            r'enhanced_main_step\d+.*\.py\s*$'
        ]
        
        for pattern in endings_to_remove:
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, '', content, flags=re.MULTILINE)
                fixes_applied.append(f"Removed trailing fragment matching {pattern}")
        
        # Apply changes if any fixes were made
        if fixes_applied:
            # Create backup
            backup_file = f"{filename}.backup"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"💾 Backup created: {backup_file}")
            
            # Write fixed content
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Applied the following fixes:")
            for fix in fixes_applied:
                print(f"   • {fix}")
            
            return True
        else:
            print("ℹ️  No specific patterns found to fix")
            return False
            
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

def validate_step5_file():
    """Validate the Step 5 file after fixes"""
    filename = "step5_complete_all_features.py"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile
        compile(content, filename, 'exec')
        print("✅ Syntax validation passed!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error still present:")
        print(f"   Line {e.lineno}: {e.msg}")
        if e.text:
            print(f"   Code: {e.text.strip()}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def show_step5_structure():
    """Show the expected structure for Step 5 file"""
    print("\n📋 EXPECTED STEP 5 STRUCTURE:")
    print("=" * 50)
    print("""
#!/usr/bin/env python3
\"\"\"
Enhanced MIDI Morphing Visualizer - Step 5 Complete
\"\"\"

# Imports
import sys
import os
# ... other imports

# Classes and functions
class CompleteMainWindow(QMainWindow):
    def __init__(self):
        # Complete initialization
        pass
    
    def _create_ui(self):
        # Complete UI creation
        pass
    
    # ... other methods

def main():
    app = QApplication(sys.argv)
    window = CompleteMainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
""")

def main():
    """Main function to run all Step 5 specific fixes"""
    print("Step 5 Complete Features - Specific Pattern Fix Tool")
    print("🎯 Targeting known syntax issues in Step 5 files")
    print("=" * 60)
    print()
    
    # Apply specific fixes
    fixes_applied = fix_step5_specific_patterns()
    
    if fixes_applied:
        print("\n📋 Validating fixed file...")
        if validate_step5_file():
            print("\n🎉 SUCCESS! Step 5 file is now syntax-correct!")
            print("\n🚀 Ready to run:")
            print("   python step5_complete_all_features.py")
        else:
            print("\n⚠️  Additional manual fixes may be needed")
            show_step5_structure()
    else:
        print("\n📋 Checking current syntax...")
        if validate_step5_file():
            print("✅ File already has correct syntax!")
        else:
            print("❌ File still has syntax errors")
            show_step5_structure()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
