#!/usr/bin/env python3
"""
Fix profiler.py issues:
1. Add missing performance_monitor decorator
2. Fix PerformanceProfiler initialization issue with max_samples
"""

import os
import re

def fix_profiler_py():
    """Fix the profiler.py file."""
    
    filename = 'profiler.py'
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Add missing performance_monitor decorator at the top
        performance_monitor_decorator = '''
def performance_monitor(func):
    """Decorator for monitoring function performance."""
    def wrapper(*args, **kwargs):
        # Simple performance monitoring wrapper
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            # Could log this if needed
        return result
    return wrapper

'''
        
        # Check if performance_monitor already exists
        if 'def performance_monitor(' not in content:
            # Add after imports but before the PerformanceProfiler class
            import_section_end = content.find('class PerformanceProfiler')
            if import_section_end != -1:
                content = content[:import_section_end] + performance_monitor_decorator + content[import_section_end:]
        
        # Fix 2: Fix the PerformanceProfiler initialization issue
        # The issue is that Config might not have max_samples, or it's not being passed correctly
        
        # Find the problematic line in __init__
        init_pattern = r'def __init__\(self, max_samples: int = 1000\):'
        if re.search(init_pattern, content):
            # Fix the PerformanceProfiler __init__ method
            fixed_init = '''def __init__(self, config=None, max_samples=1000):
        """Initialize performance profiler with proper error handling."""
        # Handle config parameter properly
        if hasattr(config, 'max_samples'):
            self.max_samples = config.max_samples
        elif isinstance(config, int):
            self.max_samples = config  # Backward compatibility
        else:
            self.max_samples = max_samples  # Default value
        
        # Ensure max_samples is an integer
        if not isinstance(self.max_samples, int):
            self.max_samples = max_samples'''
            
            # Replace the problematic __init__ definition
            content = re.sub(
                r'def __init__\(self, max_samples: int = 1000\):',
                fixed_init,
                content
            )
        
        # Fix 3: Also fix the deque initialization line specifically
        content = re.sub(
            r'self\.system_metrics = deque\(maxlen=max_samples\)',
            'self.system_metrics = deque(maxlen=self.max_samples)',
            content
        )
        
        # Fix 4: Make sure other deque calls use self.max_samples
        content = re.sub(
            r'deque\(maxlen=max_samples\)',
            'deque(maxlen=self.max_samples)',
            content
        )
        
        if content != original_content:
            # Create backup
            backup_filename = f"{filename}.backup"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"📋 Backup created: {backup_filename}")
            
            # Write fixed version
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed profiler issues in {filename}")
            return True
        else:
            print(f"ℹ️ No profiler issues found to fix in {filename}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")
        return False

def manual_fix_instructions():
    """Provide manual fix instructions."""
    
    print("\n🔧 MANUAL FIX INSTRUCTIONS for profiler.py:")
    print("If the automatic fix doesn't work, manually make these changes:")
    print()
    print("1. ADD the performance_monitor decorator near the top of the file:")
    print('''
def performance_monitor(func):
    """Decorator for monitoring function performance."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)  # Simple pass-through for now
    return wrapper
''')
    print()
    print("2. CHANGE the PerformanceProfiler __init__ method:")
    print("   OLD: def __init__(self, max_samples: int = 1000):")
    print("   NEW: def __init__(self, config=None, max_samples=1000):")
    print()
    print("3. ADD proper parameter handling in __init__:")
    print('''
    if hasattr(config, 'max_samples'):
        self.max_samples = config.max_samples
    elif isinstance(config, int):
        self.max_samples = config
    else:
        self.max_samples = max_samples
        
    if not isinstance(self.max_samples, int):
        self.max_samples = 1000
''')

if __name__ == "__main__":
    print("🔧 Profiler Fix Tool")
    print("=" * 40)
    
    if fix_profiler_py():
        print("\n✅ Profiler issues fixed!")
        print("\n🚀 Try running your application now:")
        print("   python main_fixed_window.py")
    else:
        print("\n🤔 No automatic fixes applied")
        manual_fix_instructions()
    
    print("\n📋 Issues that were fixed:")
    print("• Added missing performance_monitor decorator")
    print("• Fixed PerformanceProfiler initialization parameter handling")
    print("• Fixed deque maxlen parameter errors")
    print("• Added proper config parameter support")
