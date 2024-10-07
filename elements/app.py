import dash
from dash.dependencies import Output, Input, State
from dash import dcc, html
from dash import dash_table
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sqlite3

app = dash.Dash(__name__)

# Machine learning model function
def should_explore_ml_model(exoplanet_data):
    """
    This function represents the machine learning model
    that will determine whether the exoplanet should be explored.
    It should return 1 (explore) or 0 (don't explore).
    """
    # Example decision logic based on dummy ML model
    if (exoplanet_data['ESI'] >= 0.93 and 
        0.1 <= exoplanet_data['Mass'] <= 0.5 and 
        0.5 <= exoplanet_data['Radius'] <= 0.8 and
        exoplanet_data['Magnitude'] < 15):
        return 1  # Explore
    else:
        return 0  # Not Explore

# Connect to the SQLite database (or MySQL/Postgres)
def connect_db():
    conn = sqlite3.connect('exoplanet_data.db')  # Replace with your database
    return conn

# Function to create the table if it doesn't exist
def create_exoplanet_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS exoplanets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Magnitude REAL,
        Distance REAL,
        ESI REAL,
        Radius REAL,
        Mass REAL,
        Inclination REAL,
        Explore INTEGER
    )''')
    conn.commit()
    conn.close()

# Fetch exoplanet data from SQL
def fetch_exoplanet_data():
    conn = connect_db()
    query = "SELECT * FROM exoplanets"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Insert new exoplanet into the SQL database
def insert_exoplanet(exoplanet_data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO exoplanets (Magnitude, Distance, ESI, Radius, Mass, Inclination, Explore)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        exoplanet_data['Magnitude'],
        exoplanet_data['Distance'],
        exoplanet_data['ESI'],
        exoplanet_data['Radius'],
        exoplanet_data['Mass'],
        exoplanet_data['Inclination'],
        exoplanet_data['Explore']
    ))
    conn.commit()
    conn.close()

# Layout for Dash app
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%', 'height': '150vh'},
    children=[
        html.H1('Exoplanets from Different Perspectives'),
        
        # User input form for new exoplanet
        html.Div([
            html.H4('Add New Exoplanet'),
            dcc.Input(id='input-magnitude', type='number', placeholder='Magnitude'),
            dcc.Input(id='input-distance', type='number', placeholder='Distance (ly)'),
            dcc.Input(id='input-esi', type='number', placeholder='ESI'),
            dcc.Input(id='input-radius', type='number', placeholder='Radius (Compared to Jupiter)'),
            dcc.Input(id='input-mass', type='number', placeholder='Mass (Compared to Jupiter)'),
            dcc.Input(id='input-inclination', type='number', placeholder='Inclination Plane'),
            html.Button('Submit Exoplanet', id='submit-exoplanet', n_clicks=0),
            html.Div(id='submission-status')  # Feedback message after submission
        ]),
        
        html.Button('Toggle View (God/Earth)', id='toggle-view'),
        html.Button('ESI', id='button-1'),
        html.Button('Orbital Period', id='button-2'),
        html.Button('Mass (Compared to Jupiter)', id='button-3'),
        
        dcc.Graph(id='exoplanet-globe', style={'width': '100%', 'height': '100%'}, config={'displayModeBar': True}),
        
        dash_table.DataTable(
            id='exoplanet-table',
            columns=[{"name": col, "id": col} for col in ['Magnitude', 'Distance', 'ESI', 'Radius', 'Mass', 'Inclination', 'Explore']],
            page_size=10,
            style_table={'overflowX': 'auto'},
        ),
        
        dcc.Interval(id='interval-component', interval=240*1000, n_intervals=0)
    ]
)

# Callback to handle new exoplanet submission
@app.callback(
    Output('submission-status', 'children'),
    Input('submit-exoplanet', 'n_clicks'),
    State('input-magnitude', 'value'),
    State('input-distance', 'value'),
    State('input-esi', 'value'),
    State('input-radius', 'value'),
    State('input-mass', 'value'),
    State('input-inclination', 'value')
)
def handle_exoplanet_submission(n_clicks, magnitude, distance, esi, radius, mass, inclination):
    if n_clicks > 0:
        # Check that all fields are filled
        if magnitude is None or distance is None or esi is None or radius is None or mass is None or inclination is None:
            return 'Please fill in all fields before submitting.'
        
        # Create exoplanet data dictionary
        exoplanet_data = {
            'Magnitude': magnitude,
            'Distance': distance,
            'ESI': esi,
            'Radius': radius,
            'Mass': mass,
            'Inclination': inclination
        }
        
        # Pass data to the machine learning model
        exoplanet_data['Explore'] = should_explore_ml_model(exoplanet_data)
        
        # Insert into the database
        insert_exoplanet(exoplanet_data)
        
        return f'Exoplanet successfully submitted!'

    return ''  # No message initially

# Callback to update the table and graph
@app.callback(
    Output('exoplanet-globe', 'figure'),
    Output('exoplanet-table', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('toggle-view', 'n_clicks'),
    Input('button-1', 'n_clicks'),
    Input('button-2', 'n_clicks'),
    Input('button-3', 'n_clicks')
)
def update_figure(n_intervals, toggle_n_clicks, btn1, btn2, btn3):
    df = fetch_exoplanet_data()

    # Convert spherical to Cartesian coordinates for 3D plot
    df['x'] = df['Distance'] * np.cos(np.radians(df['Inclination']))
    df['y'] = df['Distance'] * np.sin(np.radians(df['Inclination']))
    df['z'] = df['Distance']  # Use Distance as z-coordinate

    # Default to ESI-based colorscale
    colorscale = [[0, 'red'], [1, 'green']]
    data_name = 'ESI (1 = green, 0 = red)'
    
    planet_trace = go.Scatter3d(
        x=df['x'],
        y=df['y'], 
        z=df['z'], 
        mode='markers',
        name=data_name, 
        marker=dict(
            size=10, color=df['ESI'],
            colorscale=colorscale, opacity=0.8,
            cmin=df['ESI'].min(), cmax=df['ESI'].max()
        ),
        text=df.apply(lambda row: f"Exoplanet: {row['Explore']}<br>Distance: {row['Distance']}<br>ESI: {row['ESI']}", axis=1),
        hoverinfo='text',
    )

    # Create the figure
    fig = go.Figure(data=[planet_trace])

    # Configure the layout for the globe
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, backgroundcolor="black"),
            yaxis=dict(visible=False, backgroundcolor="black"),
            zaxis=dict(visible=False, backgroundcolor="black"),
        )
    )

    return fig, df.to_dict('records')

if __name__ == '__main__':
    create_exoplanet_table()  # Ensure table exists
    app.run_server(debug=True)
