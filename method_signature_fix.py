#!/usr/bin/env python3
"""
Fix method signature mismatch for handle_note_off

The main_fixed_window.py is calling handle_note_off(note) but the method 
expects handle_note_off(note, velocity). This fixes the signature.
"""

import os
import re

def fix_handle_note_off_signature():
    """Fix the handle_note_off method signature to match how it's being called"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return False
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Create backup
    with open("visualizer.py.backup_signature", 'w') as f:
        f.write(content)
    print("✅ Created backup: visualizer.py.backup_signature")
    
    # Find the handle_note_off method and replace it
    old_signature = r'def handle_note_off\(self, note, velocity\):'
    new_signature = 'def handle_note_off(self, note, velocity=0.0):'
    
    # Replace the method signature to make velocity optional
    if re.search(old_signature, content):
        content = re.sub(old_signature, new_signature, content)
        print("✅ Fixed handle_note_off signature - made velocity optional")
    else:
        print("⚠️  handle_note_off signature not found in expected format")
        
        # Let's also try to find and fix any other signature issues
        # Look for the method and replace the entire method
        method_pattern = r'def handle_note_off\(self.*?\):'
        match = re.search(method_pattern, content)
        
        if match:
            old_method_def = match.group(0)
            new_method_def = 'def handle_note_off(self, note, velocity=0.0):'
            content = content.replace(old_method_def, new_method_def)
            print("✅ Fixed handle_note_off signature using pattern matching")
        else:
            # If we can't find it, let's replace the entire method
            method_start = content.find('def handle_note_off')
            if method_start != -1:
                # Find the end of the method
                lines = content[method_start:].split('\n')
                method_lines = []
                for i, line in enumerate(lines):
                    method_lines.append(line)
                    # Stop at next method or end of class
                    if i > 0 and line.strip() and not line.startswith('        ') and not line.startswith('    '):
                        if line.startswith('    def ') or line.startswith('class '):
                            method_lines.pop()  # Remove the next method line
                            break
                
                old_method = '\n'.join(method_lines)
                
                # Create new method with correct signature
                new_method = '''def handle_note_off(self, note, velocity=0.0):
        """Handle MIDI note off events."""
        try:
            # Remove from active notes if tracked
            if hasattr(self, 'active_notes') and note in self.active_notes:
                del self.active_notes[note]
            
            # Remove note effect and associated light
            if hasattr(self, 'active_note_effects') and note in self.active_note_effects:
                effect_info = self.active_note_effects[note]
                light_id = effect_info.get('light_id')
                
                # Remove the light
                if light_id and hasattr(self, 'lights') and light_id in self.lights:
                    try:
                        if hasattr(self, 'plotter') and self.plotter:
                            self.plotter.remove_actor(light_id)
                        del self.lights[light_id]
                    except:
                        pass
                
                del self.active_note_effects[note]
            
            # Update display
            self.update()
            
        except Exception as e:
            print(f"Error handling note off {note}: {e}")
'''
                
                content = content.replace(old_method, new_method)
                print("✅ Replaced entire handle_note_off method with correct signature")
    
    # Write the fixed file
    with open("visualizer.py", 'w') as f:
        f.write(content)
    
    return True

def verify_syntax():
    """Verify the file still has valid syntax"""
    try:
        with open("visualizer.py", 'r') as f:
            content = f.read()
        
        compile(content, "visualizer.py", "exec")
        print("✅ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

def check_method_calls():
    """Check how handle_note_off is being called in main_fixed_window.py"""
    
    if os.path.exists("main_fixed_window.py"):
        with open("main_fixed_window.py", 'r') as f:
            content = f.read()
        
        # Find all calls to handle_note_off
        calls = re.findall(r'\.handle_note_off\([^)]+\)', content)
        print("Found handle_note_off calls in main_fixed_window.py:")
        for call in calls:
            print(f"  {call}")
        
        # Check if they're calling with just note
        single_arg_calls = re.findall(r'\.handle_note_off\(\s*\w+\s*\)', content)
        if single_arg_calls:
            print(f"✅ Confirmed: {len(single_arg_calls)} calls with single argument")
            return True
    
    return False

if __name__ == "__main__":
    print("=== Fixing Method Signature Mismatch ===")
    
    # Check how the method is being called
    check_method_calls()
    
    if fix_handle_note_off_signature():
        if verify_syntax():
            print("\n🎉 SUCCESS! Method signature fixed.")
            print("\nThe fix:")
            print("- Changed handle_note_off(self, note, velocity) ")
            print("- To: handle_note_off(self, note, velocity=0.0)")
            print("- Now velocity is optional and defaults to 0.0")
            print("\nYour visualizer should now work without the TypeError!")
        else:
            print("\n❌ Syntax error after fix")
    else:
        print("\n❌ Failed to apply signature fix")
