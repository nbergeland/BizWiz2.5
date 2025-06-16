#!/usr/bin/env python3
"""
Quick BizWiz Diagnostic Script
Identifies and fixes the specific import error you're experiencing
"""

import os
import sys
import traceback

def print_header():
    print("🔍" + "="*50 + "🔍")
    print("   BIZWIZ QUICK DIAGNOSTIC")
    print("   Fixing: load_city_data_sync import error")
    print("🔍" + "="*50 + "🔍")
    print()

def check_file_exists():
    """Check if the dynamic_data_loader.py file exists"""
    print("📁 CHECKING FILE EXISTENCE")
    print("-" * 30)
    
    if os.path.exists('dynamic_data_loader.py'):
        print("✅ dynamic_data_loader.py exists")
        file_size = os.path.getsize('dynamic_data_loader.py')
        print(f"📊 File size: {file_size:,} bytes")
        return True
    else:
        print("❌ dynamic_data_loader.py NOT FOUND")
        return False

def test_file_syntax():
    """Test if the file has syntax errors"""
    print("\n🐍 TESTING FILE SYNTAX")
    print("-" * 30)
    
    try:
        import py_compile
        py_compile.compile('dynamic_data_loader.py', doraise=True)
        print("✅ File syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing syntax: {e}")
        return False

def test_imports():
    """Test what we can actually import from the file"""
    print("\n📦 TESTING IMPORTS")
    print("-" * 30)
    
    try:
        import dynamic_data_loader
        print("✅ Module imports successfully")
        
        # Check what's available in the module
        available = dir(dynamic_data_loader)
        print(f"📋 Available items: {len(available)}")
        
        # Check for specific functions
        target_functions = ['load_city_data_on_demand', 'load_city_data_sync', 'DataLoadingProgress']
        
        for func in target_functions:
            if func in available:
                print(f"✅ {func} - FOUND")
            else:
                print(f"❌ {func} - MISSING")
        
        return 'load_city_data_sync' in available
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_specific_import():
    """Test the specific import that's failing"""
    print("\n🎯 TESTING SPECIFIC IMPORT")
    print("-" * 30)
    
    try:
        from dynamic_data_loader import load_city_data_sync
        print("✅ load_city_data_sync imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("🔍 This is the exact error you're experiencing")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def analyze_file_content():
    """Analyze the content of the file to find issues"""
    print("\n🔬 ANALYZING FILE CONTENT")
    print("-" * 30)
    
    try:
        with open('dynamic_data_loader.py', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"📊 Total lines: {len(lines)}")
        
        # Check for key components
        has_load_sync = 'def load_city_data_sync' in content
        has_load_async = 'def load_city_data_on_demand' in content
        has_dataclass = 'class DataLoadingProgress' in content
        has_asyncio_run = 'asyncio.run(' in content
        
        print(f"🔍 Contains load_city_data_sync: {has_load_sync}")
        print(f"🔍 Contains load_city_data_on_demand: {has_load_async}")
        print(f"🔍 Contains DataLoadingProgress: {has_dataclass}")
        print(f"🔍 Contains asyncio.run: {has_asyncio_run}")
        
        # Look for potential issues
        issues = []
        
        if has_asyncio_run and 'RuntimeError' not in content:
            issues.append("Uses asyncio.run() without proper error handling")
        
        if not has_load_sync:
            issues.append("Missing load_city_data_sync function")
        
        if content.count('def ') < 10:
            issues.append("File appears incomplete (too few functions)")
        
        # Check for notebook artifacts
        if '{"cells"' in content or '"cell_type"' in content:
            issues.append("File contains Jupyter notebook content instead of Python code")
        
        if issues:
            print(f"\n⚠️  POTENTIAL ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"✅ No obvious issues found in file structure")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def provide_solutions():
    """Provide specific solutions based on findings"""
    print(f"\n💡 SOLUTIONS")
    print("-" * 30)
    
    print("🔧 IMMEDIATE FIX:")
    print("   1. Replace your current dynamic_data_loader.py with the fixed version")
    print("   2. Use: python dynamic_dashboard_fixed.py (instead of the original)")
    print("   3. The fixed version handles import errors gracefully")
    print()
    
    print("🛠️ MANUAL FIXES:")
    print("   1. Check if your dynamic_data_loader.py is actually a .ipynb file")
    print("   2. If so, extract the Python code from the notebook")
    print("   3. Or copy the working code from BizWiz2.3/ directory")
    print()
    
    print("🚀 QUICK TEST:")
    print("   • Save the fixed_data_loader code as 'dynamic_data_loader_fixed.py'")
    print("   • Run: python -c 'from dynamic_data_loader_fixed import load_city_data_sync; print(\"Fixed version works!\")'")
    print("   • Then use dynamic_dashboard_fixed.py")

def create_backup_and_fix():
    """Create backup and attempt to fix the file"""
    print(f"\n🔄 ATTEMPTING AUTO-FIX")
    print("-" * 30)
    
    try:
        # Create backup
        if os.path.exists('dynamic_data_loader.py'):
            import shutil
            shutil.copy2('dynamic_data_loader.py', 'dynamic_data_loader_backup.py')
            print("✅ Created backup: dynamic_data_loader_backup.py")
        
        # Check if we're in the right directory
        if os.path.exists('BizWiz2.3/dynamic_data_loader.py'):
            print("🔍 Found file in BizWiz2.3/ directory")
            print("   This might be a file structure issue")
            
            choice = input("Copy from BizWiz2.3/? (y/n): ").lower().strip()
            if choice == 'y':
                shutil.copy2('BizWiz2.3/dynamic_data_loader.py', 'dynamic_data_loader.py')
                print("✅ Copied file from BizWiz2.3/")
                return True
        
        print("⚠️  Auto-fix not possible - manual intervention needed")
        return False
        
    except Exception as e:
        print(f"❌ Auto-fix failed: {e}")
        return False

def main():
    """Run complete diagnostic"""
    print_header()
    
    # Step 1: Check file exists
    file_exists = check_file_exists()
    if not file_exists:
        print("\n🚨 CRITICAL: dynamic_data_loader.py is missing!")
        if os.path.exists('BizWiz2.3/dynamic_data_loader.py'):
            print("   Found in BizWiz2.3/ - you may need to copy files to main directory")
        provide_solutions()
        return
    
    # Step 2: Check syntax
    syntax_ok = test_file_syntax()
    
    # Step 3: Test general import
    import_ok = test_imports()
    
    # Step 4: Test specific import
    specific_ok = test_specific_import()
    
    # Step 5: Analyze content
    content_ok = analyze_file_content()
    
    # Summary
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("-" * 30)
    print(f"File exists: {'✅' if file_exists else '❌'}")
    print(f"Syntax valid: {'✅' if syntax_ok else '❌'}")
    print(f"Module imports: {'✅' if import_ok else '❌'}")
    print(f"Specific import: {'✅' if specific_ok else '❌'}")
    print(f"Content analysis: {'✅' if content_ok else '❌'}")
    
    if specific_ok:
        print(f"\n🎉 GOOD NEWS: The import should actually work!")
        print(f"   The error might be intermittent or context-specific")
        print(f"   Try running the dashboard again")
    else:
        print(f"\n🔧 ACTION NEEDED:")
        if not syntax_ok:
            print(f"   • Fix syntax errors in dynamic_data_loader.py")
        if not content_ok:
            print(f"   • Replace with working version of the file")
        
        create_backup_and_fix()
        provide_solutions()

if __name__ == '__main__':
    main()