#!/usr/bin/env python3
"""
Comprehensive Fix for step5_complete_all_features.py Syntax Errors
This script identifies and fixes all common syntax issues in the Step 5 complete file.
"""

import os
import re
import sys
import ast
import tempfile
import shutil
from typing import List, Tuple

def validate_python_syntax(filename: str) -> Tuple[bool, str]:
    """Validate Python syntax and return detailed error info"""
    if not os.path.exists(filename):
        return False, f"File {filename} not found"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to compile the code
        ast.parse(content, filename=filename)
        return True, "Syntax is valid"
        
    except SyntaxError as e:
        error_msg = f"Syntax error on line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f"\n  Code: {e.text.strip()}"
            if hasattr(e, 'offset') and e.offset:
                error_msg += f"\n  Position: {' ' * (e.offset - 1)}^"
        return False, error_msg
    except Exception as e:
        return False, f"Parse error: {e}"

def find_syntax_issues(content: str) -> List[Tuple[int, str, str]]:
    """Find common syntax issues in the content"""
    lines = content.split('\n')
    issues = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check for stray markdown formatting
        if '**' in line and not line.startswith('#') and not line.startswith('"""'):
            if not ('"""' in line or "'''" in line):  # Not in docstring
                issues.append((i, "stray_markdown", f"Stray markdown formatting: {line_stripped}"))
        
        # Check for incomplete function calls at end of file
        if i > len(lines) - 20:  # Last 20 lines
            if ('sys.exit(' in line or 'app.exec(' in line) and not line.endswith(')'):
                issues.append((i, "incomplete_call", f"Incomplete function call: {line_stripped}"))
        
        # Check for unclosed parentheses/brackets
        open_parens = line.count('(') - line.count(')')
        open_brackets = line.count('[') - line.count(']')
        open_braces = line.count('{') - line.count('}')
        
        if open_parens != 0 or open_brackets != 0 or open_braces != 0:
            if not line_stripped.endswith('\\'):  # Not a line continuation
                issues.append((i, "unmatched_brackets", f"Potentially unmatched brackets: {line_stripped}"))
        
        # Check for misplaced comments/text after code
        if line_stripped and not line_stripped.startswith('#'):
            # Look for comments not at start of line that might be stray text
            comment_pos = line.find('#')
            if comment_pos > 0:
                before_comment = line[:comment_pos].strip()
                comment_part = line[comment_pos:].strip()
                if before_comment and not before_comment.endswith(('"', "'")):
                    # Check if comment looks like stray text (contains markdown-like patterns)
                    if '**' in comment_part or comment_part.startswith('##!/'):
                        issues.append((i, "stray_comment", f"Suspicious comment: {line_stripped}"))
    
    return issues

def fix_syntax_issues(content: str) -> str:
    """Apply automatic fixes to common syntax issues"""
    original_content = content
    
    # Fix 1: Remove stray markdown formatting outside of strings/comments
    # This is the most common issue - stray **text** patterns
    lines = content.split('\n')
    fixed_lines = []
    
    in_docstring = False
    docstring_delimiter = None
    
    for line in lines:
        stripped = line.strip()
        
        # Track docstring state
        if '"""' in line or "'''" in line:
            if not in_docstring:
                in_docstring = True
                docstring_delimiter = '"""' if '"""' in line else "'''"
            elif docstring_delimiter in line:
                in_docstring = False
                docstring_delimiter = None
        
        # Skip fixing if we're in a docstring or comment
        if in_docstring or stripped.startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Fix stray markdown patterns
        fixed_line = line
        
        # Remove stray **text** patterns that are not in strings
        if '**' in line and not ('"""' in line or "'''" in line):
            # Simple approach: remove **text** patterns that look like stray markdown
            fixed_line = re.sub(r'\s*\*\*[^*\n]*\*\*\s*', '', line)
            
        # Fix common end-of-file syntax issues
        if 'sys.exit(main())' in fixed_line:
            # Ensure it ends properly
            fixed_line = re.sub(r'sys\.exit\(main\(\)\).*', 'sys.exit(main())', fixed_line)
        
        if 'app.exec()' in fixed_line:
            # Ensure it ends properly
            fixed_line = re.sub(r'app\.exec\(\).*', 'return app.exec()', fixed_line)
        
        fixed_lines.append(fixed_line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix 2: Remove any trailing incomplete code fragments
    content = re.sub(r'#!/usr/bin/env python3\s*$', '', content)
    content = re.sub(r'#\s*C5-B6.*$', '', content, flags=re.MULTILINE)
    
    # Fix 3: Ensure proper file ending
    content = content.rstrip() + '\n'
    
    return content

def create_backup(filename: str) -> str:
    """Create a backup of the file"""
    backup_name = f"{filename}.backup_{int(time.time())}"
    shutil.copy2(filename, backup_name)
    return backup_name

def fix_step5_complete_file():
    """Main function to fix step5_complete_all_features.py"""
    filename = "step5_complete_all_features.py"
    
    print("🔧 Step 5 Complete Features - Syntax Fix Tool")
    print("=" * 60)
    print()
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ {filename} not found in current directory")
        print("\nAvailable Python files:")
        for file in os.listdir('.'):
            if file.endswith('.py'):
                print(f"  • {file}")
        return False
    
    print(f"📋 Checking syntax in {filename}...")
    
    # Initial syntax validation
    is_valid, error_msg = validate_python_syntax(filename)
    
    if is_valid:
        print("✅ File already has valid syntax - no fix needed!")
        return True
    
    print(f"❌ Syntax issues found:")
    print(f"   {error_msg}")
    print()
    
    # Read content and analyze issues
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Analyzing common syntax issues...")
    issues = find_syntax_issues(content)
    
    if issues:
        print(f"⚠️  Found {len(issues)} potential issues:")
        for line_no, issue_type, description in issues:
            print(f"   Line {line_no}: {issue_type} - {description}")
        print()
    
    # Create backup
    backup_file = create_backup(filename)
    print(f"💾 Created backup: {backup_file}")
    
    # Apply fixes
    print("🔧 Applying automatic fixes...")
    fixed_content = fix_syntax_issues(content)
    
    # Write fixed content
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # Validate the fix
    print("📋 Validating fixed file...")
    is_valid, error_msg = validate_python_syntax(filename)
    
    if is_valid:
        print("✅ SUCCESS! Syntax errors have been fixed.")
        print(f"🚀 You can now run: python {filename}")
        return True
    else:
        print("⚠️  Some syntax issues may remain:")
        print(f"   {error_msg}")
        print(f"📁 Original file backed up as: {backup_file}")
        return False

def manual_fix_instructions():
    """Provide manual fix instructions for common issues"""
    print("\n🛠️  MANUAL FIX INSTRUCTIONS:")
    print("=" * 50)
    print()
    print("If automatic fixes didn't work, try these manual steps:")
    print()
    print("1. REMOVE STRAY TEXT:")
    print("   Look for lines with **text** that aren't in comments")
    print("   Remove any loose text like '**panel**' or similar")
    print()
    print("2. FIX INCOMPLETE FUNCTION CALLS:")
    print("   Find lines ending with 'sys.exit(main()' or 'app.exec('")
    print("   Make sure they end with ')' properly")
    print()
    print("3. CHECK FILE ENDING:")
    print("   The file should end with:")
    print("   if __name__ == '__main__':")
    print("       sys.exit(main())")
    print()
    print("4. REMOVE DUPLICATE CODE:")
    print("   Look for repeated import statements or class definitions")
    print()
    print("5. CHECK INDENTATION:")
    print("   Make sure all code blocks are properly indented")
    print("   Use 4 spaces, not tabs")

def main():
    """Main entry point"""
    import time
    
    print("Step 5 Complete All Features - Comprehensive Syntax Fix")
    print("🎆 This tool fixes ALL common syntax errors in Step 5 files")
    print()
    
    success = fix_step5_complete_file()
    
    if not success:
        manual_fix_instructions()
        return 1
    
    print()
    print("🎉 STEP 5 COMPLETE FILE IS NOW READY!")
    print("=" * 50)
    print("✅ All syntax errors fixed")
    print("✅ File ready to run")
    print("✅ Backup created for safety")
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Run: python step5_complete_all_features.py")
    print("   2. Test all the advanced features")
    print("   3. Enjoy your complete MIDI morphing visualizer!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
