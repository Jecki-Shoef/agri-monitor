from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import os

app = Dash(__name__)

def filter_timeframe(df, timeframe):
    if timeframe == 'day':
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=1)
    elif timeframe == 'week':
        cutoff = pd.Timestamp.now() - pd.Timedelta(weeks=1)
    elif timeframe == 'month':
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
    else:  # year
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=365)
    
    return df[df['timestamp'] >= cutoff]

def load_and_process_data(file_path):
    try:
        # Get zone number from file path
        zone_num = int(file_path.split("Zone")[-1].split("-")[0].strip())
        print(f"\nProcessing Zone {zone_num}")
        
        df = pd.read_html(file_path, skiprows=1, decimal='.', thousands=',')[0]
        
        if zone_num == 2:
            # Select the correct columns for Zone 2
            df = df.iloc[:, [0, 1, 2, 4, 6]]  # Selecting columns A, B, C, E, G
            df.columns = ['#', 'Date', 'Time', 'Avg Temp', 'Avg Hum']
            
            temp_col = 'Avg Temp'
            hum_col = 'Avg Hum'
        
        else:
            # Handle other zones
            if zone_num == 1:
                columns = [
                    '#', 'Date', 'Time', 'Avg Temp', 'Temp S 1', 'Temp S 2', 'Avg Hum',
                    'Hum S 1', 'Hum S 2', 'Out-T Avg', 'Out-Hum Avg', 'Wind Spd Avg',
                    'Daily Rain', 'Rad Current', 'Rad Summ.', 'VPD Avg'
                ][:len(df.columns)]
                temp_col = 'Avg Temp'
                hum_col = 'Avg Hum'
            elif zone_num == 3:
                columns = ['#', 'Date', 'Time', 'Avg Temp', 'Temp S 1', 'Avg Hum', 'Hum S 1']
                temp_col = 'Avg Temp'
                hum_col = 'Avg Hum'
            elif zone_num == 4:
                columns = ['#', 'Date', 'Time', 'Temp S 1', 'Hum S 1']
                temp_col = 'Temp S 1'
                hum_col = 'Hum S 1'
            
            df.columns = columns
        
        # Convert Date and Time to strings
        df['Date'] = df['Date'].astype(str)
        df['Time'] = df['Time'].astype(str)
        
        # Convert to datetime
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M', errors='coerce')
        
        # Convert temperature and humidity to numeric
        if temp_col in df.columns:
            df[temp_col] = pd.to_numeric(df[temp_col], errors='coerce')
        if hum_col in df.columns:
            df[hum_col] = pd.to_numeric(df[hum_col], errors='coerce')
        
        return df, temp_col, hum_col
    except Exception as e:
        print(f"\nError processing file {file_path}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return None, None, None

# Define some consistent colors and styles
COLORS = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'border': '#e9ecef',
    'primary': '#007bff'
}

app.layout = html.Div([
    # Main container
    html.Div([
        # Header
        html.H1("ניטור מתקן RCK", 
                style={
                    'textAlign': 'center',
                    'fontSize': 36,
                    'fontWeight': 'bold',
                    'color': COLORS['text'],
                    'padding': '20px 0',
                    'marginBottom': '20px',
                    'borderBottom': f'2px solid {COLORS["border"]}',
                    'backgroundColor': 'white',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
        
        # Controls section
        html.Div([
            html.Label('Select Timeframe:', 
                      style={
                          'fontWeight': 'bold',
                          'marginRight': '10px',
                          'color': COLORS['text']
                      }),
            dcc.Dropdown(
                id='timeframe-dropdown',
                options=[
                    {'label': 'Last Day', 'value': 'day'},
                    {'label': 'Last Week', 'value': 'week'},
                    {'label': 'Last Month', 'value': 'month'},
                    {'label': 'Last Year', 'value': 'year'}
                ],
                value='year',
                style={
                    'width': '200px',
                    'borderRadius': '4px',
                }
            ),
            html.Div([
                html.Label('Base Directory:', 
                          style={
                              'fontWeight': 'bold',
                              'marginRight': '10px',
                              'color': COLORS['text'],
                              'marginTop': '10px'
                          }),
                html.Div([
                    dcc.Input(
                        id='base-directory-input',
                        type='text',
                        value=r'C:\RCK 29 09  24',
                        style={
                            'width': '300px',
                            'borderRadius': '4px',
                            'marginRight': '10px'
                        }
                    ),
                    html.Button(
                        'Update Path',
                        id='update-path-button',
                        style={
                            'backgroundColor': COLORS['primary'],
                            'color': 'white',
                            'border': 'none',
                            'padding': '8px 15px',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        }
                    ),
                    html.Div(id='update-status', style={'marginTop': '5px', 'color': COLORS['text']})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ])
        ], style={
            'margin': '20px',
            'padding': '15px',
            'backgroundColor': 'white',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
        }),
        
        # Graphs container
        html.Div([
            # First row of graphs
            html.Div([
                html.Div([
                    dcc.Graph(id='zone1-graph')
                ], style={
                    'width': '48%',
                    'margin': '1%',
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    dcc.Graph(id='zone2-graph')
                ], style={
                    'width': '48%',
                    'margin': '1%',
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginBottom': '20px'
            }),
            
            # Second row of graphs
            html.Div([
                html.Div([
                    dcc.Graph(id='zone3-graph')
                ], style={
                    'width': '48%',
                    'margin': '1%',
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                html.Div([
                    dcc.Graph(id='zone4-graph')
                ], style={
                    'width': '48%',
                    'margin': '1%',
                    'padding': '15px',
                    'backgroundColor': 'white',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between'
            }),
        ], style={
            'padding': '20px',
            'backgroundColor': COLORS['background']
        }),
        
        # Footer
        html.Div([
            html.H2("Developed by Jecki Shoef 2024", 
                    style={
                        'textAlign': 'center',
                        'fontSize': 28,
                        'fontWeight': 'bold',
                        'color': COLORS['text'],
                        'marginTop': '20px',
                        'marginBottom': '20px',
                        'fontFamily': 'Arial, sans-serif'
                    })
        ], style={
            'borderTop': f'2px solid {COLORS["border"]}',
            'marginTop': '40px',
            'paddingTop': '20px',
            'backgroundColor': 'white',
            'boxShadow': '0 -2px 4px rgba(0,0,0,0.05)'
        }),
        
        dcc.Interval(
            id='interval-component',
            interval=300*1000,  # 300 seconds = 5 minutes
            n_intervals=0
        )
    ], style={
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif'
    })
])

@app.callback(
    Output('update-status', 'children'),
    [Input('update-path-button', 'n_clicks')],
    [State('base-directory-input', 'value')]
)
def update_path_status(n_clicks, base_directory):
    if n_clicks is None:
        return ''
    
    try:
        if os.path.exists(base_directory):
            return f"✓ Path updated successfully"
        else:
            return f"❌ Directory not found"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.callback(
    [Output('zone1-graph', 'figure'),
     Output('zone2-graph', 'figure'),
     Output('zone3-graph', 'figure'),
     Output('zone4-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('timeframe-dropdown', 'value'),
     Input('update-path-button', 'n_clicks')],
    [State('base-directory-input', 'value')])
def update_graphs(n, timeframe, n_clicks, base_directory):
    zone_names = {
        1: "חממת טיפוח",
        2: "חממת משתלה",
        3: "חדר סבתות",
        4: "חדר השרשה משתלה"
    }
    
    file_paths = [
        os.path.join(base_directory, r'NMC-Pro Climate\History 1\History Sensors - Zone 1 - 1.xls'),
        os.path.join(base_directory, r'NMC-Pro Climate\History 1\History Sensors - Zone 2 - 1.xls'),
        os.path.join(base_directory, r'NMC-Pro Climate\History 1\History Sensors - Zone 3 - 1.xls'),
        os.path.join(base_directory, r'NMC-Pro Climate\History 1\History Sensors - Zone 4 - 1.xls')
    ]
    
    figures = []
    for i, file_path in enumerate(file_paths, 1):
        try:
            df, temp_col, hum_col = load_and_process_data(file_path)
            
            if df is not None and temp_col is not None and hum_col is not None:
                # Apply timeframe filter
                df = filter_timeframe(df, timeframe)
                
                fig = {
                    'data': [
                        go.Scatter(
                            x=df['timestamp'],
                            y=df[temp_col],
                            name='Temperature',
                            line=dict(color='red')
                        ),
                        go.Scatter(
                            x=df['timestamp'],
                            y=df[hum_col],
                            name='Humidity',
                            line=dict(color='blue')
                        )
                    ],
                    'layout': {
                        'title': {
                            'text': zone_names[i],
                            'font': {
                                'size': 24,
                                'family': 'Arial, sans-serif',
                                'weight': 'bold'
                            },
                            'y': 0.9,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        'xaxis': {'title': 'Time'},
                        'yaxis': {'title': 'Value'},
                        'height': 400,
                        'margin': {'t': 100}
                    }
                }
            else:
                fig = {
                    'data': [],
                    'layout': {
                        'title': {
                            'text': f'{zone_names[i]} - Data Unavailable',
                            'font': {
                                'size': 24,
                                'family': 'Arial, sans-serif',
                                'weight': 'bold'
                            },
                            'y': 0.9,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        'height': 400,
                        'margin': {'t': 100}
                    }
                }
        except Exception as e:
            print(f"Error creating figure for Zone {i}: {str(e)}")
            fig = {
                'data': [],
                'layout': {
                    'title': {
                        'text': f'{zone_names[i]} - Error Loading Data',
                        'font': {
                            'size': 24,
                            'family': 'Arial, sans-serif',
                            'weight': 'bold'
                        },
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    'height': 400,
                    'margin': {'t': 100}
                }
            }
        
        figures.append(fig)
    
    return figures

if __name__ == '__main__':
    app.run_server(debug=True)