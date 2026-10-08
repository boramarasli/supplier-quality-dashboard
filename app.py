# app.py — OEM supplier quality and just-in-time delivery dashboard
# OEM1 Type11 Award Dashboard

from pathlib import Path
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px

# Load and validate data
PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == 'app':
    PROJECT_ROOT = PROJECT_ROOT.parent

DATASET_PATH = PROJECT_ROOT / "Final_dataset_group_09.csv"
ADDITIONAL_FILES = PROJECT_ROOT / "Additional_Files"
df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully")
print(f"Available columns: {list(df.columns)}")
print(f"Dataset shape: {df.shape}")

# Handle column name variations
if 'component' in df.columns and 'category' not in df.columns:
    df['category'] = df['component']
    print("Mapped 'component' to 'category'")

# Convert data types
date_cols = ['month', 'comp_prod_date', 'veh_prod_date', 'first_fail_date', 'first_reg_date']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Handle boolean columns
bool_cols = ['has_manu_202', 'has_manu_205', 'has_failure']
for col in bool_cols:
    if col in df.columns:
        df[col] = df[col].astype(bool)
    else:
        df[col] = False
        print(f"Created missing column: {col}")

# Create has_failure if missing
if df['has_failure'].sum() == 0 and 'first_fail_date' in df.columns:
    df['has_failure'] = df['first_fail_date'].notna()
    print(f"Created has_failure from first_fail_date: {df['has_failure'].sum()} failures")

# Get categories and validate data
categories = sorted([cat for cat in df['category'].unique() if pd.notna(cat)])
print(f"Available categories: {categories}")

# Data validation
print("\nData validation:")
print(f"Records with manu_202: {df['has_manu_202'].sum()}")
print(f"Records with manu_205: {df['has_manu_205'].sum()}")
print(f"Records with failures: {df['has_failure'].sum()}")
print(f"Gearbox records: {len(df[df['category'].str.lower().str.contains('gear', na=False)])}")

# Create app with Additional_Files as assets folder
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap'
]
app = Dash(__name__, external_stylesheets=external_stylesheets, assets_folder='Additional_Files')
app.title = "OEM1 Type11 Award Dashboard"

colors = {
    'primary': '#87CEEB',
    'secondary': '#4682B4', 
    'background': '#F0F8FF',
    'white': '#FFFFFF',
    'text': '#2C3E50'
}

# Layout
app.layout = html.Div([
    # Header with logo from Additional_Files
    html.Div([
        html.Img(
            src='/assets/logo.png',
            style={'height': '60px', 'marginRight': '15px'}
        ),
        html.Div([
            html.H1("OEM1 Type11 Award Dashboard", 
                   style={'margin': '0', 'color': colors['white'], 'fontSize': '2.2em'}),
            html.P("Supplier Quality & Just-in-Time Delivery Analysis", 
                   style={'margin': '5px 0 0 0', 'color': colors['white']})
        ])
    ], style={
        'backgroundColor': colors['primary'],
        'padding': '20px',
        'display': 'flex',
        'alignItems': 'center',
        'fontFamily': 'Source Sans Pro'
    }),
    
    # Component selection
    html.Div([
        html.H3("Select Parts (Components)", style={'color': colors['text'], 'marginBottom': '10px'}),
        dcc.Checklist(
            id='component-checklist',
            options=[{'label': cat.title(), 'value': cat} for cat in categories],
            value=categories,
            inline=True
        )
    ], style={
        'padding': '20px',
        'backgroundColor': colors['background'],
        'fontFamily': 'Source Sans Pro'
    }),
    
    # Market share section
    html.Div([
        html.H2("Market Share Analysis - Company 205 vs Competitors", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        
        html.Div([
            html.Div([
                html.Label("Display Mode:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.RadioItems(
                    id='market-share-mode',
                    options=[
                        {'label': ' Absolute Numbers', 'value': 'absolute'},
                        {'label': ' Percentage', 'value': 'percentage'}
                    ],
                    value='percentage',
                    inline=True,
                    style={'marginBottom': '15px'}
                ),
                dcc.Graph(id='market-share-chart', style={'height': '400px'})
            ], style={'width': '65%', 'display': 'inline-block'}),
            
            html.Div([
                html.H4("Marketing Slogan", style={'color': colors['text'], 'marginBottom': '15px'}),
                html.Div(id='gearbox-slogan', style={
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'color': colors['secondary'],
                    'padding': '15px',
                    'backgroundColor': colors['white'],
                    'border': f'2px solid {colors["primary"]}',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'minHeight': '60px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center'
                })
            ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '15px'})
        ])
    ], style={
        'padding': '20px', 
        'backgroundColor': colors['white'], 
        'margin': '10px',
        'fontFamily': 'Source Sans Pro'
    }),
    
    # Quality analysis
    html.Div([
        html.H2("Error Frequency Analysis", style={'color': colors['text'], 'marginBottom': '20px'}),
        dcc.Graph(id='quality-chart', style={'height': '400px'})
    ], style={
        'padding': '20px', 
        'backgroundColor': colors['white'], 
        'margin': '10px',
        'fontFamily': 'Source Sans Pro'
    }),
    
    # JIT analysis  
    html.Div([
        html.H2("Just-in-Time Delivery Performance", style={'color': colors['text'], 'marginBottom': '10px'}),
        html.P("(2013-2015 Engines and Circuits Only)", 
               style={'color': colors['text'], 'fontStyle': 'italic', 'marginBottom': '15px'}),
        html.Div([
            html.Label("Select observation period:", style={'marginRight': '10px'}),
            dcc.DatePickerRange(
                id='jit-date-range',
                start_date='2013-01-01',
                end_date='2015-12-31',
                display_format='YYYY-MM-DD'
            )
        ], style={'marginBottom': '15px'}),
        dcc.Graph(id='jit-chart', style={'height': '400px'})
    ], style={
        'padding': '20px', 
        'backgroundColor': colors['white'], 
        'margin': '10px',
        'fontFamily': 'Source Sans Pro'
    }),
    
    # Dataset table
    html.Div([
        html.H2("Dataset Preview", style={'color': colors['text'], 'marginBottom': '20px'}),
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'Vehicle ID', 'id': 'vehicle'},
                {'name': 'Component', 'id': 'category'},
                {'name': 'Supplier', 'id': 'supplier_manu'},
                {'name': 'Has Manu 205', 'id': 'has_manu_205'},
                {'name': 'Has Manu 202', 'id': 'has_manu_202'},
                {'name': 'Has Failure', 'id': 'has_failure'},
                {'name': 'Month', 'id': 'month'},
                {'name': 'Delivery Days', 'id': 'delivery_days'}
            ],
            data=df.head(150).to_dict('records'),
            page_size=12,
            style_cell={'textAlign': 'left', 'fontFamily': 'Source Sans Pro'},
            style_header={'backgroundColor': colors['primary'], 'color': 'white', 'fontWeight': 'bold'}
        )
    ], style={
        'padding': '20px', 
        'backgroundColor': colors['white'], 
        'margin': '10px',
        'fontFamily': 'Source Sans Pro'
    })
    
], style={'fontFamily': 'Source Sans Pro', 'backgroundColor': colors['background']})

# Callbacks

@app.callback(
    Output('market-share-chart', 'figure'),
    [Input('market-share-mode', 'value'), Input('component-checklist', 'value')]
)
def update_market_share(mode, selected_components):
    if not selected_components:
        selected_components = categories
    
    filtered_df = df[df['category'].isin(selected_components)]
    
    if len(filtered_df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data for selected components", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    market_data = filtered_df.groupby(['month', 'has_manu_205']).size().reset_index(name='count')
    
    if mode == 'percentage':
        total_by_month = market_data.groupby('month')['count'].transform('sum')
        market_data['value'] = (market_data['count'] / total_by_month * 100).fillna(0)
        y_label = 'Market Share (%)'
    else:
        market_data['value'] = market_data['count']
        y_label = 'Count'
    
    fig = go.Figure()
    
    # Company 205
    company_205 = market_data[market_data['has_manu_205'] == True]
    if not company_205.empty:
        fig.add_trace(go.Bar(
            x=company_205['month'],
            y=company_205['value'],
            name='Company 205',
            marker_color=colors['secondary']
        ))
    
    # Competitors
    competitors = market_data[market_data['has_manu_205'] == False]
    if not competitors.empty:
        fig.add_trace(go.Bar(
            x=competitors['month'],
            y=competitors['value'],
            name='Competitors',
            marker_color=colors['primary']
        ))
    
    fig.update_layout(
        barmode='stack',
        xaxis_title='Month',
        yaxis_title=y_label,
        font_family='Source Sans Pro',
        plot_bgcolor='white'
    )
    
    return fig

@app.callback(
    Output('gearbox-slogan', 'children'),
    Input('component-checklist', 'value')
)
def update_slogan(selected_components):
    # Find gearbox components (case-insensitive)
    gearbox_mask = df['category'].str.lower().str.contains('gear', na=False)
    gearbox_data = df[gearbox_mask]
    
    if len(gearbox_data) == 0:
        return "No gearbox data found in dataset"
    
    total_gearboxes = len(gearbox_data)
    
    # Count gearboxes that have parts from manufacturer 202
    gearboxes_with_202 = len(gearbox_data[gearbox_data['has_manu_202'] == True])
    
    print(f"Slogan calculation: {total_gearboxes} total gearboxes, {gearboxes_with_202} with manu 202")
    
    if gearboxes_with_202 == 0:
        # If no gearboxes have 202, check if the data makes sense
        # This could mean the has_manu_202 column is not set correctly
        return "No gearboxes contain parts from manufacturer 202"
    
    ratio = total_gearboxes / gearboxes_with_202
    return f"There is a part of 202 in every {ratio:.1f} gearbox"

@app.callback(
    Output('quality-chart', 'figure'),
    Input('component-checklist', 'value')
)
def update_quality_chart(selected_components):
    if not selected_components:
        selected_components = categories
    
    filtered_df = df[df['category'].isin(selected_components)]
    
    if len(filtered_df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data for selected components", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Count errors by supplier group and category
    error_counts = filtered_df.groupby(['supplier_manu', 'category', 'has_manu_205'])['has_failure'].sum().reset_index()
    error_counts['supplier_group'] = error_counts['has_manu_205'].map({True: 'Company 205', False: 'Competitors'})
    
    if len(error_counts) == 0 or error_counts['has_failure'].sum() == 0:
        fig = go.Figure()
        fig.add_annotation(text="No failure data for selected components", 
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    if len(selected_components) == 1:
        # Single component - simple bar chart by supplier group
        simple_data = error_counts.groupby('supplier_group')['has_failure'].sum().reset_index()
        fig = px.bar(simple_data, x='supplier_group', y='has_failure', 
                    color='supplier_group',
                    color_discrete_map={'Company 205': colors['secondary'], 'Competitors': colors['primary']})
    else:
        # Multiple components - stacked by category
        fig = px.bar(error_counts, x='supplier_group', y='has_failure', color='category',
                    title="Error Frequency (Stacked by Component)")
    
    fig.update_layout(
        xaxis_title='Supplier Group',
        yaxis_title='Number of Failures',
        font_family='Source Sans Pro',
        plot_bgcolor='white'
    )
    
    return fig

@app.callback(
    Output('jit-chart', 'figure'),
    [Input('jit-date-range', 'start_date'), Input('jit-date-range', 'end_date')]
)
def update_jit_chart(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter for JIT criteria: 2013-2015, engines and circuits only
    jit_mask = (
        (df['comp_prod_date'].dt.year.between(2013, 2015)) &
        (df['category'].str.lower().isin(['engine', 'circuit'])) &
        (df['delivery_days'].notna()) &
        (df['comp_prod_date'] >= start_date) &
        (df['comp_prod_date'] <= end_date)
    )
    
    jit_data = df[jit_mask]
    
    print(f"JIT analysis: {len(jit_data)} records found for period {start_date.date()} to {end_date.date()}")
    
    if len(jit_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No JIT delivery data available for selected period<br>(Requires 2013-2015 engines/circuits with delivery times)",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(font_family='Source Sans Pro')
        return fig
    
    # Calculate delivery performance by supplier
    delivery_stats = jit_data.groupby('supplier_manu').agg({
        'delivery_days': ['mean', 'median', 'count']
    }).round(1)
    
    delivery_stats.columns = ['avg_days', 'median_days', 'count']
    delivery_stats = delivery_stats.reset_index().sort_values('median_days')
    
    # Create bar chart
    fig = px.bar(delivery_stats, x='supplier_manu', y='median_days',
                hover_data=['avg_days', 'count'],
                title=f"JIT Delivery Performance (Median Days) - {len(jit_data)} records")
    
    fig.update_layout(
        xaxis_title='Supplier',
        yaxis_title='Median Delivery Days',
        font_family='Source Sans Pro',
        plot_bgcolor='white'
    )
    
    # Highlight best performer (lowest delivery time)
    if len(delivery_stats) > 0:
        colors_list = [colors['secondary'] if i == 0 else colors['primary'] for i in range(len(delivery_stats))]
        fig.update_traces(marker_color=colors_list)
    
    return fig

if __name__ == '__main__':
    print("\nStarting Dash application...")
    print("Dashboard will be available at: http://127.0.0.1:8050")
    app.run(debug=True, port=8050)