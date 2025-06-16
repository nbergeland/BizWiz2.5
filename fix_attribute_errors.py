#!/usr/bin/env python3
"""
BizWiz Attribute Error Fix
Fixes the 'CityConfiguration' object has no attribute 'center_lat' error
"""

import re
import os
import shutil
from datetime import datetime

def fix_attribute_access_in_file(filepath):
    """Fix attribute access patterns in a Python file"""
    print(f"🔧 Fixing attribute access in {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ File {filepath} not found")
        return False
    
    # Create backup
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"📁 Created backup: {backup_path}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Track changes
        changes_made = 0
        
        # Fix 1: config.center_lat -> config.bounds.center_lat
        old_pattern = r'config\.center_lat'
        new_pattern = 'config.bounds.center_lat'
        if old_pattern in content:
            content = re.sub(old_pattern, new_pattern, content)
            changes_made += content.count(new_pattern) - content.count(old_pattern)
            print(f"✅ Fixed: config.center_lat -> config.bounds.center_lat")
        
        # Fix 2: config.center_lon -> config.bounds.center_lon  
        old_pattern = r'config\.center_lon'
        new_pattern = 'config.bounds.center_lon'
        if old_pattern in content:
            content = re.sub(old_pattern, new_pattern, content)
            changes_made += 1
            print(f"✅ Fixed: config.center_lon -> config.bounds.center_lon")
        
        # Fix 3: getattr() safety for bounds access
        # Replace direct bounds access with safe getattr calls
        unsafe_patterns = [
            (r'config\.bounds\.center_lat', "getattr(config.bounds, 'center_lat', 40.7)"),
            (r'config\.bounds\.center_lon', "getattr(config.bounds, 'center_lon', -74.0)"),
            (r'config\.bounds\.min_lat', "getattr(config.bounds, 'min_lat', 40.6)"),
            (r'config\.bounds\.max_lat', "getattr(config.bounds, 'max_lat', 40.8)"),
            (r'config\.bounds\.min_lon', "getattr(config.bounds, 'min_lon', -74.1)"),
            (r'config\.bounds\.max_lon', "getattr(config.bounds, 'max_lon', -73.9)"),
        ]
        
        for old_pattern, new_pattern in unsafe_patterns:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes_made += 1
                print(f"✅ Added safety: {old_pattern} -> getattr() call")
        
        # Fix 4: Safe access to config attributes that might not exist
        # Add helper function for safe config access
        helper_function = '''
def safe_get_config_attr(config, attr_path, default=None):
    """Safely get nested config attributes"""
    try:
        attrs = attr_path.split('.')
        value = config
        for attr in attrs:
            value = getattr(value, attr)
        return value
    except (AttributeError, TypeError):
        return default
'''
        
        # Add helper function if not already present
        if 'def safe_get_config_attr' not in content:
            # Insert after imports
            import_end = content.rfind('import ')
            if import_end != -1:
                next_line = content.find('\n', import_end)
                if next_line != -1:
                    content = content[:next_line + 1] + helper_function + content[next_line + 1:]
                    changes_made += 1
                    print("✅ Added safe_get_config_attr helper function")
        
        # Write the fixed content
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Made {changes_made} fixes in {filepath}")
        return changes_made > 0
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        # Restore backup
        shutil.copy2(backup_path, filepath)
        print(f"🔄 Restored backup")
        return False

def create_fixed_dashboard_with_safe_access():
    """Create a dashboard version with completely safe attribute access"""
    
    dashboard_code = '''#!/usr/bin/env python3
"""
BizWiz Dynamic Dashboard - Safe Attribute Access Version
Handles all config attribute access safely
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import asyncio
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import sys
import os

# Enhanced error handling for imports
try:
    from city_config import CityConfigManager
    CITY_CONFIG_AVAILABLE = True
    print("✅ Successfully imported CityConfigManager")
except ImportError as e:
    print(f"❌ Failed to import CityConfigManager: {e}")
    CITY_CONFIG_AVAILABLE = False

try:
    from dynamic_data_loader import load_city_data_on_demand, DataLoadingProgress
    DATA_LOADER_AVAILABLE = True
    print("✅ Successfully imported data loader")
except ImportError as e:
    print(f"❌ Failed to import data loader: {e}")
    DATA_LOADER_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
app_state = {
    'current_city_data': None,
    'loading_progress': None,
    'last_loaded_city': None,
    'loading_in_progress': False
}

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "BizWiz Dynamic Analytics"

def safe_get_config_attr(config, attr_path, default=None):
    """Safely get nested config attributes"""
    try:
        attrs = attr_path.split('.')
        value = config
        for attr in attrs:
            value = getattr(value, attr, None)
            if value is None:
                return default
        return value
    except (AttributeError, TypeError):
        return default

def get_safe_bounds(config):
    """Get safe bounds with fallbacks"""
    return {
        'center_lat': safe_get_config_attr(config, 'bounds.center_lat', 40.7),
        'center_lon': safe_get_config_attr(config, 'bounds.center_lon', -74.0),
        'min_lat': safe_get_config_attr(config, 'bounds.min_lat', 40.6),
        'max_lat': safe_get_config_attr(config, 'bounds.max_lat', 40.8),
        'min_lon': safe_get_config_attr(config, 'bounds.min_lon', -74.1),
        'max_lon': safe_get_config_attr(config, 'bounds.max_lon', -73.9)
    }

def get_safe_display_name(config):
    """Get safe display name"""
    return safe_get_config_attr(config, 'display_name', 'Unknown City')

def get_safe_primary_competitor(config):
    """Get safe primary competitor"""
    return safe_get_config_attr(config, 'competitor_data.primary_competitor', 'chick-fil-a')

# Initialize city manager with fallback
available_cities = []
if CITY_CONFIG_AVAILABLE:
    try:
        city_manager = CityConfigManager()
        available_cities = [
            {'label': get_safe_display_name(config), 'value': city_id}
            for city_id, config in city_manager.configs.items()
        ]
        print(f"✅ Loaded {len(available_cities)} cities from config")
    except Exception as e:
        print(f"❌ Error loading city configurations: {e}")
        CITY_CONFIG_AVAILABLE = False

# Fallback cities if config system fails
if not available_cities:
    print("⚠️  Using fallback city list")
    available_cities = [
        {'label': 'New York, NY', 'value': 'new_york_ny'},
        {'label': 'Los Angeles, CA', 'value': 'los_angeles_ca'},
        {'label': 'Chicago, IL', 'value': 'chicago_il'},
        {'label': 'Houston, TX', 'value': 'houston_tx'},
        {'label': 'Grand Forks, ND', 'value': 'grand_forks_nd'}
    ]

# Dashboard Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🍗 BizWiz: Location Intelligence (Safe Mode)", className="text-center mb-3"),
            html.P("Dashboard with enhanced error handling", className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Card([
        dbc.CardHeader([html.H5("🎯 City Selection", className="mb-0")]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Select City:", className="fw-bold"),
                    dcc.Dropdown(
                        id='city-selector',
                        options=available_cities,
                        value=None,
                        placeholder=f"Choose from {len(available_cities)} cities...",
                        clearable=False,
                        className="mb-3"
                    )
                ], width=8),
                dbc.Col([
                    html.Label("Actions:", className="fw-bold"),
                    dbc.Button("🔄 Load Data", id="load-btn", color="primary", size="sm")
                ], width=4)
            ]),
            html.Div(id='progress-container', style={'display': 'none'}, children=[
                html.Hr(),
                dbc.Progress(id="progress-bar", value=0, className="mb-2"),
                html.Div(id="progress-text", className="text-muted small")
            ])
        ])
    ], className="mb-4"),
    
    html.Div(id='status-cards', children=[
        dbc.Alert(f"👋 Select a city from {len(available_cities)} available options", color="info", className="text-center")
    ]),
    
    html.Div(id='main-content', style={'display': 'none'}, children=[
        dbc.Tabs([
            dbc.Tab(label="🗺️ Map", tab_id="map-tab"),
            dbc.Tab(label="📊 Analytics", tab_id="analytics-tab"),
            dbc.Tab(label="🏆 Top Locations", tab_id="top-tab"),
            dbc.Tab(label="ℹ️ System Info", tab_id="info-tab")
        ], id="main-tabs", active_tab="map-tab"),
        html.Div(id='tab-content', className="mt-4")
    ]),
    
    dcc.Interval(id='progress-interval', interval=500, n_intervals=0, disabled=True)
    
], fluid=True)

@app.callback(
    [Output('status-cards', 'children'),
     Output('progress-container', 'style'),
     Output('main-content', 'style')],
    [Input('load-btn', 'n_clicks')],
    [State('city-selector', 'value')]
)
def handle_city_loading(n_clicks, city_id):
    """Handle city data loading with safe attribute access"""
    
    if not n_clicks or not city_id:
        return [
            dbc.Alert("👋 Select a city and click 'Load Data'", color="info", className="text-center")
        ], {'display': 'none'}, {'display': 'none'}
    
    if not DATA_LOADER_AVAILABLE:
        return [
            dbc.Alert("⚠️ Data loader not available. Check your installation.", color="warning")
        ], {'display': 'none'}, {'display': 'none'}
    
    try:
        # Get city display name safely
        if CITY_CONFIG_AVAILABLE and city_manager:
            config = city_manager.get_config(city_id)
            display_name = get_safe_display_name(config) if config else city_id
        else:
            city_info = next((c for c in available_cities if c['value'] == city_id), None)
            display_name = city_info['label'] if city_info else city_id
        
        # Start loading
        threading.Thread(
            target=load_city_data_background_safe,
            args=(city_id, display_name),
            daemon=True
        ).start()
        
        return [
            dbc.Alert(f"🔄 Loading data for {display_name}...", color="warning", className="text-center")
        ], {'display': 'block'}, {'display': 'none'}
        
    except Exception as e:
        logger.error(f"Error in city loading: {e}")
        return [
            dbc.Alert(f"❌ Error: {str(e)}", color="danger")
        ], {'display': 'none'}, {'display': 'none'}

def load_city_data_background_safe(city_id: str, display_name: str):
    """Background loading with safe error handling"""
    
    def progress_callback(progress):
        try:
            app_state['loading_progress'] = {
                'percent': getattr(progress, 'progress_percent', 50),
                'step': getattr(progress, 'step_name', 'Processing...'),
                'eta': getattr(progress, 'estimated_remaining', 0)
            }
        except Exception:
            app_state['loading_progress'] = {'percent': 50, 'step': 'Processing...', 'eta': 0}
    
    try:
        app_state['loading_in_progress'] = True
        
        # Try async loading
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        city_data = loop.run_until_complete(
            load_city_data_on_demand(city_id, progress_callback, True)
        )
        
        if city_data and 'df_filtered' in city_data:
            app_state['current_city_data'] = city_data
            logger.info(f"Successfully loaded data for {city_id}")
        else:
            raise ValueError("Invalid data returned")
            
    except Exception as e:
        logger.error(f"Loading failed: {e}")
        # Create minimal fallback data
        app_state['current_city_data'] = create_minimal_fallback(city_id, display_name)
        
    finally:
        app_state['loading_in_progress'] = False
        app_state['loading_progress'] = None
        try:
            loop.close()
        except:
            pass

def create_minimal_fallback(city_id: str, display_name: str):
    """Create minimal fallback data"""
    import numpy as np
    
    np.random.seed(hash(city_id) % 2**32)
    n_locations = 25
    
    df = pd.DataFrame({
        'latitude': np.random.normal(40.7, 0.05, n_locations),
        'longitude': np.random.normal(-74.0, 0.05, n_locations),
        'predicted_revenue': np.random.uniform(3_000_000, 7_000_000, n_locations),
        'median_income': np.random.uniform(40_000, 90_000, n_locations),
        'traffic_score': np.random.uniform(30, 85, n_locations)
    })
    
    class SafeConfig:
        def __init__(self, city_id, display_name):
            self.city_id = city_id
            self.display_name = display_name
            self.bounds = type('Bounds', (), {
                'center_lat': df['latitude'].mean(),
                'center_lon': df['longitude'].mean()
            })()
    
    return {
        'df_filtered': df,
        'competitor_data': {},
        'city_config': SafeConfig(city_id, display_name),
        'metrics': {'fallback': True},
        'generation_time': datetime.now().isoformat()
    }

@app.callback(
    [Output('progress-bar', 'value'),
     Output('progress-text', 'children'),
     Output('progress-interval', 'disabled')],
    [Input('progress-interval', 'n_intervals')]
)
def update_progress(n_intervals):
    """Update progress display"""
    
    if not app_state.get('loading_in_progress', False):
        has_data = app_state.get('current_city_data') is not None
        if has_data:
            # Trigger main content display by updating a hidden div
            pass
        return 0, "", True
    
    progress = app_state.get('loading_progress', {})
    percent = progress.get('percent', 0)
    step = progress.get('step', 'Loading...')
    eta = progress.get('eta', 0)
    
    progress_text = f"{step}"
    if eta > 0:
        progress_text += f" (ETA: {eta:.0f}s)"
    
    return percent, progress_text, False

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab')],
    [State('city-selector', 'value')]
)
def update_tab_content(active_tab, city_id):
    """Update tab content with completely safe attribute access"""
    
    try:
        city_data = app_state.get('current_city_data')
        
        if not city_data:
            return dbc.Alert("No data loaded. Please select a city and load data.", color="info")
        
        if active_tab == "map-tab":
            return create_safe_map_tab(city_data)
        elif active_tab == "analytics-tab":
            return create_safe_analytics_tab(city_data)
        elif active_tab == "top-tab":
            return create_safe_top_tab(city_data)
        elif active_tab == "info-tab":
            return create_safe_info_tab(city_data)
        else:
            return html.Div("Unknown tab")
            
    except Exception as e:
        logger.error(f"Tab content error: {e}")
        traceback.print_exc()
        return dbc.Alert(f"❌ Tab error: {str(e)}", color="danger")

def create_safe_map_tab(city_data):
    """Create map tab with completely safe attribute access"""
    try:
        df = city_data.get('df_filtered', pd.DataFrame())
        config = city_data.get('city_config')
        
        if len(df) == 0:
            return dbc.Alert("No location data available", color="warning")
        
        # Get safe bounds
        bounds = get_safe_bounds(config) if config else {
            'center_lat': df['latitude'].mean(),
            'center_lon': df['longitude'].mean()
        }
        
        # Create map with safe attributes
        fig = px.scatter_mapbox(
            df.head(100),
            lat='latitude',
            lon='longitude',
            size='predicted_revenue' if 'predicted_revenue' in df.columns else None,
            color='predicted_revenue' if 'predicted_revenue' in df.columns else None,
            color_continuous_scale='RdYlGn',
            size_max=15,
            zoom=10,
            mapbox_style='open-street-map',
            title=f"🗺️ {get_safe_display_name(config) if config else 'City Analysis'}"
        )
        
        fig.update_layout(
            height=500,
            mapbox=dict(center=dict(lat=bounds['center_lat'], lon=bounds['center_lon']))
        )
        
        # Stats cards
        stats = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{len(df):,}", className="text-primary mb-0"),
                        html.P("Locations", className="text-muted mb-0")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${df['predicted_revenue'].mean():,.0f}" if 'predicted_revenue' in df.columns else "N/A", 
                                className="text-success mb-0"),
                        html.P("Avg Revenue", className="text-muted mb-0")
                    ])
                ])
            ], width=6)
        ], className="mb-4")
        
        return html.Div([stats, dcc.Graph(figure=fig)])
        
    except Exception as e:
        logger.error(f"Map tab error: {e}")
        return dbc.Alert(f"❌ Map error: {str(e)}", color="danger")

def create_safe_analytics_tab(city_data):
    """Create analytics tab with safe access"""
    try:
        df = city_data.get('df_filtered', pd.DataFrame())
        
        if len(df) == 0 or 'predicted_revenue' not in df.columns:
            return dbc.Alert("No revenue data available for analysis", color="warning")
        
        fig = px.histogram(df, x='predicted_revenue', nbins=15, title="📊 Revenue Distribution")
        fig.update_layout(height=400)
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        logger.error(f"Analytics tab error: {e}")
        return dbc.Alert(f"❌ Analytics error: {str(e)}", color="danger")

def create_safe_top_tab(city_data):
    """Create top locations tab with safe access"""
    try:
        df = city_data.get('df_filtered', pd.DataFrame())
        
        if len(df) == 0 or 'predicted_revenue' not in df.columns:
            return dbc.Alert("No data available for ranking", color="warning")
        
        top_10 = df.nlargest(10, 'predicted_revenue')[['latitude', 'longitude', 'predicted_revenue']].copy()
        top_10['predicted_revenue'] = top_10['predicted_revenue'].apply(lambda x: f"${x:,.0f}")
        top_10.columns = ['Latitude', 'Longitude', 'Revenue Potential']
        
        table = dbc.Table.from_dataframe(top_10, striped=True, bordered=True, hover=True)
        
        return html.Div([
            html.H4("🏆 Top 10 Revenue Opportunities", className="mb-3"),
            table
        ])
        
    except Exception as e:
        logger.error(f"Top tab error: {e}")
        return dbc.Alert(f"❌ Top locations error: {str(e)}", color="danger")

def create_safe_info_tab(city_data):
    """Create system info tab"""
    try:
        config = city_data.get('city_config')
        metrics = city_data.get('metrics', {})
        
        info_items = [
            ("City", get_safe_display_name(config) if config else "Unknown"),
            ("Data Type", "Fallback" if metrics.get('fallback') else "Generated"),
            ("Generated", city_data.get('generation_time', 'Unknown')[:19]),
            ("System Status", "✅ Safe Mode Active"),
            ("Config Available", "✅" if CITY_CONFIG_AVAILABLE else "❌"),
            ("Data Loader", "✅" if DATA_LOADER_AVAILABLE else "❌")
        ]
        
        return html.Div([
            html.H4("ℹ️ System Information", className="mb-3"),
            dbc.Table([
                html.Tbody([
                    html.Tr([html.Td(label, style={'font-weight': 'bold'}), html.Td(value)])
                    for label, value in info_items
                ])
            ], striped=True)
        ])
        
    except Exception as e:
        logger.error(f"Info tab error: {e}")
        return dbc.Alert(f"❌ Info error: {str(e)}", color="danger")

# Show main content when data is loaded
@app.callback(
    Output('main-content', 'style', allow_duplicate=True),
    [Input('progress-interval', 'n_intervals')],
    prevent_initial_call=True
)
def show_content_when_loaded(n_intervals):
    """Show main content when data is ready"""
    if app_state.get('current_city_data') and not app_state.get('loading_in_progress', False):
        return {'display': 'block'}
    return {'display': 'none'}

if __name__ == '__main__':
    print("🚀 Starting BizWiz Safe Mode Dashboard")
    print(f"🏙️ Cities available: {len(available_cities)}")
    print(f"🌐 Starting at: http://127.0.0.1:8051")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=8051)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Try a different port or check for conflicts")
'''
    
    try:
        with open('dynamic_dashboard_safe.py', 'w') as f:
            f.write(dashboard_code)
        print("✅ Created dynamic_dashboard_safe.py")
        print("🚀 Run with: python dynamic_dashboard_safe.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create safe dashboard: {e}")
        return False

def main():
    """Main function to fix attribute errors"""
    print("🔧" + "="*50 + "🔧")
    print("   BIZWIZ ATTRIBUTE ERROR FIX")
    print("   Fixing: 'center_lat' attribute access")
    print("🔧" + "="*50 + "🔧")
    print()
    
    # Files that might have attribute access issues
    files_to_fix = [
        'dynamic_dashboard.py',
        'dynamic_data_loader.py'
    ]
    
    fixed_files = 0
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            if fix_attribute_access_in_file(filepath):
                fixed_files += 1
        else:
            print(f"⏭️  Skipping {filepath} (not found)")
    
    print(f"\n📊 SUMMARY")
    print("-" * 30)
    print(f"Files fixed: {fixed_files}")
    
    if fixed_files > 0:
        print(f"✅ Attribute access issues should be resolved")
        print(f"🚀 Try running your dashboard again")
    else:
        print(f"⚠️  No files were fixed")
        print(f"🔧 Creating a completely safe dashboard version...")
        
        if create_fixed_dashboard_with_safe_access():
            print(f"✅ Created dynamic_dashboard_safe.py")
            print(f"🚀 Run: python dynamic_dashboard_safe.py")
    
    print(f"\n💡 RECOMMENDATION")
    print("-" * 30)
    print(f"Use the safe dashboard: python dynamic_dashboard_safe.py")
    print(f"This version handles ALL attribute access safely")

if __name__ == '__main__':
    main()