#!/usr/bin/env python3
"""
Fix all indentation issues in Python files
"""

import re
import ast

def fix_python_file(filepath):
    """Fix indentation issues in a Python file"""
    try:
        print(f"Fixing {filepath}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Check if this line needs proper indentation
            if i > 0:
                prev_line = lines[i-1].strip()
                
                # If previous line ends with : and current line isn't indented
                if (prev_line.endswith(':') and 
                    stripped and 
                    not line.startswith('    ') and 
                    not line.startswith('\t') and
                    not stripped.startswith(('except', 'elif', 'else', 'finally', 'def ', 'class '))):
                    
                    # Calculate expected indentation
                    prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                    expected_indent = prev_indent + 4
                    
                    # Apply correct indentation
                    fixed_line = ' ' * expected_indent + stripped + '\n'
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        # Try to compile to verify syntax
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print(f"✅ {filepath} - Fixed and valid")
            return True
        except SyntaxError as e:
            print(f"⚠️ {filepath} - Still has syntax issues: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    print("Fixing Python indentation issues...")
    
    files_to_fix = [
        'run_live_screen.py',
        'plive_dom_scraper.py',
        'test_system.py',
        'start_pto_chrome.py'
    ]
    
    success_count = 0
    for filepath in files_to_fix:
        if fix_python_file(filepath):
            success_count += 1
    
    print(f"\nFixed {success_count}/{len(files_to_fix)} files successfully")
    
    if success_count == len(files_to_fix):
        print("🎉 All indentation issues resolved!")
    else:
        print("⚠️ Some files still need manual fixes")

if __name__ == "__main__":
    main()
