#!/usr/bin/env python3
"""
BizWiz 2.3 → 2.5 Migration Fix Script
This script will diagnose and fix the common issues when migrating BizWiz
"""

import os
import sys
import subprocess
import shutil
import yaml
from pathlib import Path

def print_header():
    """Print diagnostic header"""
    print("🔧" + "="*60 + "🔧")
    print("    BIZWIZ 2.3 → 2.5 MIGRATION FIX")
    print("    Diagnostic and Repair Tool")
    print("🔧" + "="*60 + "🔧")
    print()

def check_file_structure():
    """Check and diagnose file structure issues"""
    print("📁 CHECKING FILE STRUCTURE")
    print("-" * 30)
    
    # Expected files in current directory
    expected_files = {
        'city_config.py': 'City configuration system',
        'dynamic_data_loader.py': 'Data loading engine', 
        'dynamic_dashboard.py': 'Dashboard application',
        'generate_usa_cities.py': 'City database generator',
        'requirements_dynamic.txt': 'Dependencies',
        'usa_city_configs.yaml': 'City database (generated)'
    }
    
    issues = []
    for file, description in expected_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - MISSING - {description}")
            issues.append(file)
    
    # Check for old 2.3 structure
    if os.path.exists('BizWiz2.3'):
        print(f"\n📂 Found old BizWiz2.3 directory:")
        for file in expected_files.keys():
            old_path = f"BizWiz2.3/{file}"
            if os.path.exists(old_path):
                print(f"   📄 {old_path} exists")
    
    return issues

def fix_file_structure():
    """Fix file structure by copying from BizWiz2.3 if needed"""
    print(f"\n🔧 FIXING FILE STRUCTURE")
    print("-" * 30)
    
    if not os.path.exists('BizWiz2.3'):
        print("❌ BizWiz2.3 directory not found - cannot auto-fix")
        return False
    
    files_to_copy = [
        'city_config.py',
        'dynamic_data_loader.py', 
        'dynamic_dashboard.py',
        'generate_usa_cities.py',
        'requirements_dynamic.txt'
    ]
    
    copied = 0
    for file in files_to_copy:
        source = f"BizWiz2.3/{file}"
        dest = file
        
        if os.path.exists(source) and not os.path.exists(dest):
            try:
                shutil.copy2(source, dest)
                print(f"✅ Copied {source} → {dest}")
                copied += 1
            except Exception as e:
                print(f"❌ Failed to copy {file}: {e}")
        elif os.path.exists(dest):
            print(f"⏭️  {file} already exists, skipping")
        else:
            print(f"❌ {source} not found")
    
    print(f"\n📊 Copied {copied} files")
    return copied > 0

def check_city_database():
    """Check city database status"""
    print(f"\n🏙️ CHECKING CITY DATABASE")
    print("-" * 30)
    
    yaml_file = 'usa_city_configs.yaml'
    
    if not os.path.exists(yaml_file):
        print(f"❌ {yaml_file} not found")
        return False
    
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'cities' not in data:
            print(f"❌ {yaml_file} has invalid structure")
            return False
        
        city_count = len(data['cities'])
        print(f"✅ {yaml_file} found with {city_count} cities")
        
        if city_count < 50:
            print(f"⚠️  Warning: Only {city_count} cities (expected 200+)")
            return False
        
        # Check for key cities
        test_cities = ['new_york_ny', 'los_angeles_ca', 'chicago_il', 'grand_forks_nd']
        found_cities = []
        for city in test_cities:
            if city in data['cities']:
                found_cities.append(city)
        
        print(f"✅ Found {len(found_cities)}/{len(test_cities)} test cities: {found_cities}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading {yaml_file}: {e}")
        return False

def regenerate_city_database():
    """Regenerate the city database"""
    print(f"\n🔄 REGENERATING CITY DATABASE")
    print("-" * 30)
    
    if not os.path.exists('generate_usa_cities.py'):
        print("❌ generate_usa_cities.py not found")
        return False
    
    try:
        print("🔄 Running generate_usa_cities.py...")
        result = subprocess.run([
            sys.executable, 'generate_usa_cities.py'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ City database regenerated successfully")
            print("📊 Output:", result.stdout[-200:] if result.stdout else "No output")
            return True
        else:
            print("❌ City database generation failed")
            print("Error:", result.stderr[-200:] if result.stderr else "No error details")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ City generation timed out (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running generator: {e}")
        return False

def test_imports():
    """Test critical imports"""
    print(f"\n🐍 TESTING IMPORTS")
    print("-" * 30)
    
    imports_to_test = [
        ('city_config', 'CityConfigManager'),
        ('dynamic_data_loader', 'load_city_data_on_demand'),
        ('dynamic_dashboard', 'app')
    ]
    
    import_errors = []
    for module, item in imports_to_test:
        try:
            exec(f"from {module} import {item}")
            print(f"✅ {module}.{item}")
        except ImportError as e:
            print(f"❌ {module}.{item} - {e}")
            import_errors.append((module, item, str(e)))
        except Exception as e:
            print(f"❌ {module}.{item} - Unexpected error: {e}")
            import_errors.append((module, item, str(e)))
    
    return len(import_errors) == 0

def test_city_config_loading():
    """Test if city configuration loads properly"""
    print(f"\n🏙️ TESTING CITY CONFIG LOADING")
    print("-" * 30)
    
    try:
        from city_config import CityConfigManager
        
        manager = CityConfigManager()
        city_count = len(manager.configs)
        
        print(f"✅ CityConfigManager loaded successfully")
        print(f"📊 {city_count} cities configured")
        
        if city_count < 50:
            print(f"⚠️  Warning: Only {city_count} cities (expected 200+)")
            return False
        
        # Test search functionality
        test_results = manager.search_cities('new york')
        print(f"🔍 Search test ('new york'): {len(test_results)} results")
        
        # Test getting specific city
        test_city = list(manager.configs.keys())[0]
        config = manager.get_config(test_city)
        print(f"🎯 Config test: {config.display_name if config else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ City config loading failed: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print(f"\n📦 CHECKING DEPENDENCIES")
    print("-" * 30)
    
    required_packages = [
        'dash', 'dash_bootstrap_components', 'plotly', 
        'pandas', 'numpy', 'scikit-learn', 'aiohttp', 
        'requests', 'pyyaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    
    return True

def create_minimal_test_dashboard():
    """Create a minimal test dashboard to verify basic functionality"""
    print(f"\n🧪 CREATING MINIMAL TEST DASHBOARD")
    print("-" * 30)
    
    test_dashboard_code = '''#!/usr/bin/env python3
"""
Minimal BizWiz Test Dashboard
Tests basic functionality without full feature set
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Test data
test_data = pd.DataFrame({
    'city': ['New York', 'Los Angeles', 'Chicago'],
    'population': [8336817, 3979576, 2693976],
    'lat': [40.7128, 34.0522, 41.8781],
    'lon': [-74.0060, -118.2437, -87.6298]
})

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("🧪 BizWiz Test Dashboard", className="text-center mb-4"),
    
    dbc.Alert("This is a minimal test dashboard to verify basic functionality", 
              color="info", className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=px.scatter_mapbox(
                    test_data, 
                    lat='lat', lon='lon', 
                    size='population',
                    hover_name='city',
                    mapbox_style='open-street-map',
                    title="Test Cities Map",
                    zoom=3
                )
            )
        ], width=12)
    ]),
    
    html.Hr(),
    
    html.P("If you can see this dashboard, basic functionality is working!", 
           className="text-center")
])

if __name__ == '__main__':
    print("🚀 Starting test dashboard on http://127.0.0.1:8052")
    app.run_server(debug=True, host='127.0.0.1', port=8052)
'''
    
    try:
        with open('test_minimal_dashboard.py', 'w') as f:
            f.write(test_dashboard_code)
        print("✅ Created test_minimal_dashboard.py")
        print("🚀 Run with: python test_minimal_dashboard.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create test dashboard: {e}")
        return False

def create_fix_suggestions():
    """Create specific fix suggestions based on common issues"""
    print(f"\n💡 FIX SUGGESTIONS")
    print("-" * 30)
    
    suggestions = [
        "1. 🔧 IMMEDIATE FIXES:",
        "   • Run this script: python fix_bizwiz_migration.py",
        "   • Test basic imports: python -c 'from city_config import CityConfigManager; print(len(CityConfigManager().configs))'",
        "   • Test minimal dashboard: python test_minimal_dashboard.py",
        "",
        "2. 📦 DEPENDENCY ISSUES:",
        "   • Reinstall requirements: pip install -r requirements_dynamic.txt",
        "   • Upgrade packages: pip install --upgrade dash plotly pandas",
        "",
        "3. 🏙️ CITY DATABASE ISSUES:",
        "   • Regenerate database: python generate_usa_cities.py", 
        "   • Check file exists: ls -la usa_city_configs.yaml",
        "   • Validate YAML: python -c 'import yaml; print(len(yaml.safe_load(open(\"usa_city_configs.yaml\"))[\"cities\"]))'",
        "",
        "4. 🐛 DASHBOARD ISSUES:",
        "   • Check port conflicts: lsof -i :8051",
        "   • Run with different port: python dynamic_dashboard.py --port 8052",
        "   • Check Python path: which python",
        "",
        "5. 📁 FILE STRUCTURE ISSUES:",
        "   • Ensure all files are in current directory (not BizWiz2.3/)",
        "   • Check file permissions: ls -la *.py",
        "   • Verify imports work: python -c 'import dynamic_dashboard'"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

def run_full_diagnostic():
    """Run complete diagnostic and fix routine"""
    print_header()
    
    # Step 1: Check file structure
    missing_files = check_file_structure()
    
    # Step 2: Fix file structure if needed
    if missing_files:
        print(f"\n⚠️  Found {len(missing_files)} missing files")
        if input("🔧 Attempt to copy files from BizWiz2.3? (y/n): ").lower() == 'y':
            fix_file_structure()
    
    # Step 3: Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print(f"\n⚠️  Install missing dependencies first!")
        return False
    
    # Step 4: Check city database
    db_ok = check_city_database()
    if not db_ok:
        print(f"\n⚠️  City database issue detected")
        if input("🔄 Regenerate city database? (y/n): ").lower() == 'y':
            regenerate_city_database()
    
    # Step 5: Test imports
    imports_ok = test_imports()
    
    # Step 6: Test city config
    config_ok = test_city_config_loading()
    
    # Step 7: Create test dashboard
    create_minimal_test_dashboard()
    
    # Summary
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("-" * 30)
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"City Database: {'✅' if check_city_database() else '❌'}")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"City Config: {'✅' if config_ok else '❌'}")
    
    # Provide next steps
    if all([deps_ok, imports_ok, config_ok]):
        print(f"\n🎉 SYSTEM APPEARS HEALTHY!")
        print(f"🚀 Try running: python dynamic_dashboard.py")
    else:
        create_fix_suggestions()
    
    return True

if __name__ == '__main__':
    run_full_diagnostic()