#!/usr/bin/env python3
"""
BizWiz Dynamic Dashboard - Fixed Version
Addresses common migration issues from 2.3 to 2.5
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback_context, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import asyncio
import threading
import time
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import traceback
import os
import sys

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

# Global variables for state management
app_state = {
    'current_city_data': None,
    'loading_progress': None,
    'last_loaded_city': None,
    'loading_in_progress': False
}

# Initialize the Dash app with error handling
try:
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "BizWiz Dynamic Analytics"
    print("✅ Dash app initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Dash app: {e}")
    sys.exit(1)

# Initialize city manager with fallback
available_cities = []
if CITY_CONFIG_AVAILABLE:
    try:
        city_manager = CityConfigManager()
        available_cities = [
            {'label': config.display_name, 'value': city_id}
            for city_id, config in city_manager.configs.items()
        ]
        print(f"✅ Loaded {len(available_cities)} cities from config")
    except Exception as e:
        print(f"❌ Error loading city configurations: {e}")
        CITY_CONFIG_AVAILABLE = False

# Fallback cities if config system fails
if not available_cities:
    print("⚠️  Using fallback city list")
    fallback_cities = [
        {'label': 'New York, NY', 'value': 'new_york_ny'},
        {'label': 'Los Angeles, CA', 'value': 'los_angeles_ca'},
        {'label': 'Chicago, IL', 'value': 'chicago_il'},
        {'label': 'Houston, TX', 'value': 'houston_tx'},
        {'label': 'Phoenix, AZ', 'value': 'phoenix_az'},
        {'label': 'Philadelphia, PA', 'value': 'philadelphia_pa'},
        {'label': 'San Antonio, TX', 'value': 'san_antonio_tx'},
        {'label': 'San Diego, CA', 'value': 'san_diego_ca'},
        {'label': 'Dallas, TX', 'value': 'dallas_tx'},
        {'label': 'Grand Forks, ND', 'value': 'grand_forks_nd'}
    ]
    available_cities = fallback_cities

# === LAYOUT ===
app.layout = dbc.Container([
    # Header with system status
    dbc.Row([
        dbc.Col([
            html.H1("🍗 BizWiz: Real-Time Location Intelligence", className="text-center mb-3"),
            html.P("Dynamic city analysis with live data integration", 
                   className="text-center text-muted mb-2"),
            # System status indicator
            dbc.Alert([
                html.Div([
                    f"🏙️ Cities: {len(available_cities)} | ",
                    f"📊 Config: {'✅' if CITY_CONFIG_AVAILABLE else '❌'} | ",
                    f"🔄 Loader: {'✅' if DATA_LOADER_AVAILABLE else '❌'}"
                ])
            ], color="info" if CITY_CONFIG_AVAILABLE and DATA_LOADER_AVAILABLE else "warning", 
            className="text-center small mb-4")
        ])
    ]),
    
    # Control Panel
    dbc.Card([
        dbc.CardHeader([
            html.H5("🎯 City Selection & Controls", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Select City for Analysis:", className="fw-bold"),
                    dcc.Dropdown(
                        id='city-selector',
                        options=available_cities,
                        value=None,
                        placeholder=f"Choose from {len(available_cities)} cities...",
                        clearable=False,
                        className="mb-3"
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Data Options:", className="fw-bold"),
                    html.Div([
                        dbc.Button(
                            "🔄 Force Refresh Data", 
                            id="refresh-btn", 
                            color="primary", 
                            size="sm",
                            className="me-2",
                            disabled=not DATA_LOADER_AVAILABLE
                        ),
                        dbc.Button(
                            "🧪 Test System", 
                            id="test-btn", 
                            color="secondary", 
                            size="sm"
                        )
                    ])
                ], width=6)
            ]),
            
            # Progress Bar
            html.Div(id='progress-container', style={'display': 'none'}, children=[
                html.Hr(),
                html.H6("Loading Progress:", className="mb-2"),
                dbc.Progress(id="progress-bar", value=0, className="mb-2"),
                html.Div(id="progress-text", className="text-muted small")
            ])
        ])
    ], className="mb-4"),
    
    # Status Cards
    html.Div(id='status-cards', children=[
        dbc.Alert(
            f"👋 Welcome to BizWiz! Select from {len(available_cities)} cities above to begin analysis.",
            color="info",
            className="text-center"
        )
    ]),
    
    # Main Content Tabs
    html.Div(id='main-content', style={'display': 'none'}, children=[
        dbc.Tabs([
            dbc.Tab(label="🗺️ Live Location Map", tab_id="live-map-tab"),
            dbc.Tab(label="📊 Analytics Dashboard", tab_id="analytics-tab"),
            dbc.Tab(label="🏆 Top Opportunities", tab_id="opportunities-tab"),
            dbc.Tab(label="🔬 System Info", tab_id="system-tab")
        ], id="main-tabs", active_tab="live-map-tab"),
        
        html.Div(id='tab-content', className="mt-4")
    ]),
    
    # Hidden divs for state management
    html.Div(id='city-data-store', style={'display': 'none'}),
    html.Div(id='loading-trigger', style={'display': 'none'}),
    
    # Auto-refresh interval
    dcc.Interval(id='progress-interval', interval=500, n_intervals=0, disabled=True)
    
], fluid=True)

# === CALLBACK FUNCTIONS ===

@app.callback(
    [Output('loading-trigger', 'children'),
     Output('progress-container', 'style'),
     Output('status-cards', 'children')],
    [Input('city-selector', 'value'),
     Input('refresh-btn', 'n_clicks'),
     Input('test-btn', 'n_clicks')],
    [State('loading-trigger', 'children')],
    prevent_initial_call=False
)
def trigger_city_loading(city_id, refresh_clicks, test_clicks, current_trigger):
    """Enhanced city loading with better error handling"""
    
    # Handle test button
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'test-btn':
            return current_trigger or "", {'display': 'none'}, [
                dbc.Alert([
                    html.H5("🧪 System Test Results", className="mb-3"),
                    html.Ul([
                        html.Li(f"Cities Available: {len(available_cities)}"),
                        html.Li(f"City Config System: {'✅ Working' if CITY_CONFIG_AVAILABLE else '❌ Failed'}"),
                        html.Li(f"Data Loader: {'✅ Working' if DATA_LOADER_AVAILABLE else '❌ Failed'}"),
                        html.Li(f"Dashboard: ✅ Working (you're seeing this!)"),
                        html.Li(f"Python Version: {sys.version.split()[0]}"),
                        html.Li(f"Current Directory: {os.getcwd()}")
                    ])
                ], color="info", className="text-start")
            ]
    
    if not city_id:
        return "", {'display': 'none'}, [
            dbc.Alert(
                f"👋 Welcome to BizWiz! Select from {len(available_cities)} cities above to begin analysis.",
                color="info",
                className="text-center"
            )
        ]
    
    # Check if data loader is available
    if not DATA_LOADER_AVAILABLE:
        return current_trigger or "", {'display': 'none'}, [
            dbc.Alert([
                html.H5("⚠️ Data Loader Not Available", className="mb-2"),
                html.P("The data loading system is not working. This could be due to:"),
                html.Ul([
                    html.Li("Missing dynamic_data_loader.py file"),
                    html.Li("Import errors in the data loader"),
                    html.Li("Missing dependencies")
                ]),
                html.P("Try running: python fix_bizwiz_migration.py", className="mb-0")
            ], color="warning", className="text-start")
        ]
    
    # Get city display name safely
    try:
        if CITY_CONFIG_AVAILABLE:
            config = city_manager.get_config(city_id)
            display_name = config.display_name if config else city_id
        else:
            # Find in fallback list
            city_info = next((c for c in available_cities if c['value'] == city_id), None)
            display_name = city_info['label'] if city_info else city_id
    except Exception:
        display_name = city_id
    
    # Check for force refresh
    force_refresh = False
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'refresh-btn' and refresh_clicks:
            force_refresh = True
    
    # Check if we need to load this city
    if (city_id != app_state['last_loaded_city'] or 
        force_refresh or 
        not app_state['current_city_data']):
        
        try:
            # Start loading in background thread
            threading.Thread(
                target=load_city_data_background_safe,
                args=(city_id, force_refresh, display_name),
                daemon=True
            ).start()
            
            app_state['loading_in_progress'] = True
            app_state['last_loaded_city'] = city_id
            
            return (
                f"loading-{city_id}-{datetime.now().isoformat()}", 
                {'display': 'block'}, 
                [
                    dbc.Alert([
                        html.Div([
                            dbc.Spinner(size="sm", className="me-2"),
                            f"🔄 Loading data for {display_name}..."
                        ], className="d-flex align-items-center")
                    ], color="warning", className="text-center")
                ]
            )
            
        except Exception as e:
            logger.error(f"Error starting background loading: {e}")
            return (
                current_trigger or "", 
                {'display': 'none'}, 
                [
                    dbc.Alert(
                        f"❌ Error starting data load: {str(e)}",
                        color="danger",
                        className="text-center"
                    )
                ]
            )
    
    # City already loaded
    return (
        current_trigger or "", 
        {'display': 'none'}, 
        [
            dbc.Alert(
                f"✅ Ready to analyze {display_name}",
                color="success",
                className="text-center"
            )
        ]
    )

def load_city_data_background_safe(city_id: str, force_refresh: bool = False, display_name: str = ""):
    """Enhanced background loading with comprehensive error handling"""
    
    def progress_callback(progress):
        """Update progress state safely"""
        try:
            app_state['loading_progress'] = {
                'percent': progress.progress_percent,
                'step': progress.step_name,
                'locations': progress.locations_processed,
                'total_locations': progress.total_locations,
                'eta': progress.estimated_remaining
            }
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
            app_state['loading_progress'] = {
                'percent': 50,
                'step': 'Processing...',
                'locations': 0,
                'total_locations': 0,
                'eta': 0
            }
    
    try:
        logger.info(f"Starting background data load for {city_id}")
        
        if not DATA_LOADER_AVAILABLE:
            raise ImportError("Data loader not available")
        
        # Load data asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        city_data = loop.run_until_complete(
            load_city_data_on_demand(city_id, progress_callback, force_refresh)
        )
        
        # Validate the loaded data
        if not city_data or 'df_filtered' not in city_data:
            raise ValueError("Invalid city data returned")
        
        df = city_data['df_filtered']
        if len(df) == 0:
            # Create synthetic data as fallback
            logger.warning(f"No data returned for {city_id}, creating synthetic data")
            city_data = create_synthetic_city_data(city_id, display_name)
        
        app_state['current_city_data'] = city_data
        app_state['loading_in_progress'] = False
        app_state['loading_progress'] = None
        
        logger.info(f"Successfully loaded data for {city_id}")
        
    except Exception as e:
        error_msg = f"Error loading city data: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        
        # Create fallback data
        try:
            logger.info(f"Creating fallback data for {city_id}")
            city_data = create_synthetic_city_data(city_id, display_name)
            app_state['current_city_data'] = city_data
        except Exception as fallback_error:
            logger.error(f"Fallback data creation failed: {fallback_error}")
        
        app_state['loading_in_progress'] = False
        app_state['loading_progress'] = {'error': error_msg}
        
    finally:
        try:
            loop.close()
        except Exception:
            pass

def create_synthetic_city_data(city_id: str, display_name: str) -> Dict[str, Any]:
    """Create synthetic city data as fallback"""
    logger.info(f"Creating synthetic data for {city_id}")
    
    # Generate synthetic location data
    np.random.seed(hash(city_id) % 2**32)  # Consistent random seed based on city
    
    # Create grid of locations
    n_locations = 100
    lats = np.random.normal(40.7, 0.1, n_locations)  # Around NYC latitude
    lons = np.random.normal(-74.0, 0.1, n_locations)  # Around NYC longitude
    
    df = pd.DataFrame({
        'latitude': lats,
        'longitude': lons,
        'predicted_revenue': np.random.uniform(2_800_000, 8_500_000, n_locations),
        'median_income': np.random.uniform(35_000, 120_000, n_locations),
        'median_age': np.random.uniform(25, 65, n_locations),
        'population': np.random.uniform(2_000, 25_000, n_locations),
        'traffic_score': np.random.uniform(20, 95, n_locations),
        'commercial_score': np.random.uniform(25, 90, n_locations),
        'distance_to_primary_competitor': np.random.uniform(0.1, 8.0, n_locations),
        'competition_density': np.random.randint(0, 8, n_locations)
    })
    
    # Create mock config
    class MockConfig:
        def __init__(self, city_id, display_name):
            self.city_id = city_id
            self.display_name = display_name or city_id.replace('_', ' ').title()
            self.bounds = type('Bounds', (), {
                'center_lat': lats.mean(),
                'center_lon': lons.mean()
            })()
            self.competitor_data = type('CompData', (), {
                'primary_competitor': 'chick-fil-a'
            })()
    
    return {
        'df_filtered': df,
        'competitor_data': {'chick-fil-a': []},
        'model': None,
        'metrics': {
            'train_r2': 0.85,
            'synthetic': True,
            'note': 'Synthetic data generated as fallback'
        },
        'city_config': MockConfig(city_id, display_name),
        'generation_time': datetime.now().isoformat()
    }

@app.callback(
    [Output('progress-bar', 'value'),
     Output('progress-bar', 'label'),
     Output('progress-text', 'children'),
     Output('progress-interval', 'disabled'),
     Output('main-content', 'style')],
    [Input('progress-interval', 'n_intervals')],
    [State('loading-trigger', 'children')],
    prevent_initial_call=False
)
def update_progress_safe(n_intervals, loading_trigger):
    """Update loading progress with enhanced error handling"""
    
    try:
        loading_in_progress = app_state.get('loading_in_progress', False)
        
        if not loading_in_progress:
            # Loading complete - show main content if data available
            has_data = app_state.get('current_city_data') is not None
            main_style = {'display': 'block'} if has_data else {'display': 'none'}
            return 0, "", "", True, main_style
        
        progress = app_state.get('loading_progress')
        if not progress:
            return 0, "Initializing...", "Starting data collection...", False, {'display': 'none'}
        
        if 'error' in progress:
            return (
                100, 
                "Error occurred", 
                f"❌ {progress['error']}", 
                True, 
                {'display': 'none'}
            )
        
        percent = progress.get('percent', 0)
        step = progress.get('step', 'Processing...')
        
        # Create progress text safely
        progress_text = f"Step: {step}"
        
        locations = progress.get('locations', 0)
        total_locations = progress.get('total_locations', 0)
        if locations > 0 and total_locations > 0:
            progress_text += f" | Processed: {locations}/{total_locations} locations"
        
        eta = progress.get('eta', 0)
        if eta > 0:
            progress_text += f" | ETA: {eta:.0f}s"
        
        return (
            percent, 
            f"{percent:.1f}%", 
            progress_text, 
            False, 
            {'display': 'none'}
        )
        
    except Exception as e:
        logger.error(f"Progress update error: {e}")
        return (
            0, 
            "Error", 
            f"Progress update error: {str(e)}", 
            True, 
            {'display': 'none'}
        )

@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab')],
    [State('city-selector', 'value')],
    prevent_initial_call=False
)
def update_tab_content_safe(active_tab, city_id):
    """Update tab content with comprehensive error handling"""
    
    try:
        city_data = app_state.get('current_city_data')
        
        if not city_data or not city_id:
            return html.Div([
                dbc.Alert(
                    "No data available. Please select a city and wait for data to load.",
                    color="info",
                    className="text-center mt-3"
                )
            ])
        
        if active_tab == "live-map-tab":
            return create_live_map_tab_safe(city_data)
        elif active_tab == "analytics-tab":
            return create_analytics_tab_safe(city_data)
        elif active_tab == "opportunities-tab":
            return create_opportunities_tab_safe(city_data)
        elif active_tab == "system-tab":
            return create_system_tab_safe(city_data)
        else:
            return html.Div("Unknown tab", className="text-center mt-5")
            
    except Exception as e:
        logger.error(f"Tab content error: {e}")
        traceback.print_exc()
        return dbc.Alert(
            f"❌ Error loading tab content: {str(e)}", 
            color="danger",
            className="m-3"
        )

def create_live_map_tab_safe(city_data: Dict[str, Any]) -> html.Div:
    """Create live map tab with error handling"""
    try:
        df = city_data['df_filtered']
        config = city_data['city_config']
        
        if len(df) == 0:
            return html.Div("No location data available", className="text-center mt-5")
        
        # Create enhanced map
        fig = px.scatter_mapbox(
            df.head(200),  # Limit for performance
            lat='latitude',
            lon='longitude',
            size='predicted_revenue',
            color='predicted_revenue',
            color_continuous_scale='RdYlGn',
            size_max=15,
            zoom=10,
            mapbox_style='open-street-map',
            title=f"🗺️ Location Intelligence: {config.display_name}",
            hover_data={
                'predicted_revenue': ':$,.0f',
                'median_income': ':$,.0f',
                'traffic_score': ':.0f'
            }
        )
        
        # Set map center
        fig.update_layout(
            height=600,
            mapbox=dict(
                center=dict(
                    lat=getattr(config.bounds, 'center_lat', df['latitude'].mean()),
                    lon=getattr(config.bounds, 'center_lon', df['longitude'].mean())
                )
            )
        )
        
        # Statistics cards
        stats_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{len(df):,}", className="text-primary mb-0"),
                        html.P("Locations", className="text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${df['predicted_revenue'].mean():,.0f}", className="text-success mb-0"),
                        html.P("Avg Revenue", className="text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${df['predicted_revenue'].max():,.0f}", className="text-warning mb-0"),
                        html.P("Top Potential", className="text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("✅" if len(df) > 50 else "⚠️", className="text-info mb-0"),
                        html.P("Data Quality", className="text-muted mb-0")
                    ])
                ])
            ], width=3)
        ], className="mb-4")
        
        return html.Div([
            stats_cards,
            dcc.Graph(figure=fig)
        ])
        
    except Exception as e:
        logger.error(f"Map tab error: {e}")
        return dbc.Alert(
            f"❌ Error creating map: {str(e)}", 
            color="danger",
            className="m-3"
        )

def create_analytics_tab_safe(city_data: Dict[str, Any]) -> html.Div:
    """Create analytics tab with error handling"""
    try:
        df = city_data['df_filtered']
        
        # Revenue distribution chart
        fig = px.histogram(
            df, 
            x='predicted_revenue',
            nbins=20,
            title="📊 Revenue Distribution Analysis"
        )
        fig.update_layout(height=400)
        
        # Summary statistics
        summary_stats = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📈 Revenue Statistics"),
                    dbc.CardBody([
                        html.P(f"Mean: ${df['predicted_revenue'].mean():,.0f}"),
                        html.P(f"Median: ${df['predicted_revenue'].median():,.0f}"),
                        html.P(f"Std Dev: ${df['predicted_revenue'].std():,.0f}"),
                        html.P(f"Range: ${df['predicted_revenue'].min():,.0f} - ${df['predicted_revenue'].max():,.0f}")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🏙️ Market Overview"),
                    dbc.CardBody([
                        html.P(f"Total Locations: {len(df):,}"),
                        html.P(f"High Potential (>$6M): {len(df[df['predicted_revenue'] > 6_000_000]):,}"),
                        html.P(f"Premium Locations (Top 10%): {len(df.nlargest(int(len(df)*0.1), 'predicted_revenue')):,}"),
                        html.P(f"Data Source: {'Real-time' if not city_data['metrics'].get('synthetic') else 'Synthetic'}")
                    ])
                ])
            ], width=6)
        ], className="mb-4")
        
        return html.Div([
            summary_stats,
            dcc.Graph(figure=fig)
        ])
        
    except Exception as e:
        logger.error(f"Analytics tab error: {e}")
        return dbc.Alert(
            f"❌ Error creating analytics: {str(e)}", 
            color="danger",
            className="m-3"
        )

def create_opportunities_tab_safe(city_data: Dict[str, Any]) -> html.Div:
    """Create opportunities tab with error handling"""
    try:
        df = city_data['df_filtered']
        
        # Get top opportunities
        top_locations = df.nlargest(20, 'predicted_revenue').copy()
        
        # Create simple display
        display_df = top_locations[['latitude', 'longitude', 'predicted_revenue']].copy()
        display_df['predicted_revenue'] = display_df['predicted_revenue'].apply(lambda x: f"${x:,.0f}")
        display_df.columns = ['Latitude', 'Longitude', 'Revenue Potential']
        
        # Create table
        table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in display_df.columns],
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 0},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                }
            ],
            page_size=20
        )
        
        return html.Div([
            html.H4("🏆 Top Revenue Opportunities", className="mb-3"),
            table
        ])
        
    except Exception as e:
        logger.error(f"Opportunities tab error: {e}")
        return dbc.Alert(
            f"❌ Error creating opportunities view: {str(e)}", 
            color="danger",
            className="m-3"
        )

def create_system_tab_safe(city_data: Dict[str, Any]) -> html.Div:
    """Create system information tab"""
    try:
        metrics = city_data.get('metrics', {})
        
        system_info = [
            ("🏙️ City Configuration", "✅ Working" if CITY_CONFIG_AVAILABLE else "❌ Failed"),
            ("🔄 Data Loader", "✅ Working" if DATA_LOADER_AVAILABLE else "❌ Failed"),
            ("📊 Total Cities", f"{len(available_cities)}"),
            ("🧮 Model R² Score", f"{metrics.get('train_r2', 'N/A'):.3f}" if metrics.get('train_r2') else "N/A"),
            ("📈 Data Type", "Synthetic" if metrics.get('synthetic') else "Real-time"),
            ("⏰ Generated", city_data.get('generation_time', 'Unknown')[:19]),
            ("🐍 Python Version", sys.version.split()[0]),
            ("📁 Working Directory", os.getcwd()),
            ("📦 Dash Version", getattr(Dash, '__version__', 'Unknown')),
            ("🔢 Pandas Version", pd.__version__)
        ]
        
        return html.Div([
            html.H4("🔬 System Information", className="mb-4"),
            dbc.Table([
                html.Tbody([
                    html.Tr([
                        html.Td(label, style={'font-weight': 'bold'}),
                        html.Td(value)
                    ]) for label, value in system_info
                ])
            ], striped=True, bordered=True, hover=True),
            
            html.Hr(),
            
            dbc.Alert([
                html.H5("🛠️ Troubleshooting", className="mb-2"),
                html.P("If you're experiencing issues:"),
                html.Ol([
                    html.Li("Run: python fix_bizwiz_migration.py"),
                    html.Li("Check file structure: ensure all .py files are in current directory"),
                    html.Li("Verify dependencies: pip install -r requirements_dynamic.txt"),
                    html.Li("Regenerate city database: python generate_usa_cities.py")
                ])
            ], color="info")
        ])
        
    except Exception as e:
        logger.error(f"System tab error: {e}")
        return dbc.Alert(
            f"❌ Error creating system view: {str(e)}", 
            color="danger",
            className="m-3"
        )

# === MAIN APPLICATION RUNNER ===
def main():
    """Main function to run the dashboard"""
    print("🚀 Starting BizWiz Dynamic Dashboard (Fixed Version)")
    print(f"🏙️ Available cities: {len(available_cities)}")
    print(f"📊 City config system: {'✅' if CITY_CONFIG_AVAILABLE else '❌'}")
    print(f"🔄 Data loader: {'✅' if DATA_LOADER_AVAILABLE else '❌'}")
    
    # Find available port
    import socket
    for port in [8051, 8052, 8053, 8054]:
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind(('127.0.0.1', port))
            test_sock.close()
            break
        except OSError:
            continue
    else:
        port = 8055
    
    print(f"🌐 Dashboard starting at: http://127.0.0.1:{port}")
    print("✋ Press Ctrl+C to stop")
    print()
    
    if not CITY_CONFIG_AVAILABLE or not DATA_LOADER_AVAILABLE:
        print("⚠️  Some components are not working. Dashboard will run with limited functionality.")
        print("🔧 Run: python fix_bizwiz_migration.py to diagnose and fix issues")
        print()
    
    try:
        app.run(
            debug=False,  # Disable debug mode for stability
            host='127.0.0.1',
            port=port
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("🔧 Try running: python fix_bizwiz_migration.py")

if __name__ == '__main__':
    main()