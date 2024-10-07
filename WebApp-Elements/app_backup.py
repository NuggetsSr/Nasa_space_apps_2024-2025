import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
from dash import dash_table
import plotly.graph_objects as go
import pandas as pd
import numpy as np  # Import NumPy

app = dash.Dash(__name__)

# Exoplanet data including galactic coordinates and other characteristics
def fetch_exoplanet_data():
    data = {
        'Exoplanet': ["Teegarden's Star b", 'Wolf 1069 b', 'TOI-700 d', 'GJ 1002 b', 'GJ 273 b', 'TOI-715 b', 'TOI-2257 b', 'Proxima Cen b', 
                      'GJ 1002 c', 'TOI-700 e', 'GJ 367 d', 'GJ 357 d', 'GJ 180 c', 'LP 890-9 c', 'GJ 433 d', 'HD 40307 g', 'GJ 1061 c', 
                      'GJ 163 c', 'GJ 682 b', 'TRAPPIST-1 d', 'GJ 667 C f', 'GJ 1061 d', 'HD 216520 c', 'GJ 514 b', 'GJ 667 C c'],# 'Kepler-1701 b'],
        'Galactic Longitude': [213.46, 177.77, 218.03, 347.59, 226.57, 277.38, 91.03, 311.88, 347.59, 218.03, 286.38, 317.29, 202.19, 44.09, 
                               317.51, 253.72, 336.15, 284.19, 358.41, 272.16, 42.44, 336.15, 1.92, 356.78, 42.44], #48.92],
        'Galactic Latitude': [59.42, -0.01, -62.56, -12.11, 5.68, -35.83, 12.66, -0.23, -12.11, -62.56, -44.48, 12.42, -58.83, -41.53, 
                              59.57, -51.29, -48.48, -22.51, -7.16, -62.17, -9.15, -48.48, -37.45, -10.95, -9.15],# 13.33],
        'ESI': [0.95, 0.94, 0.93, 0.92, 0.91, 0.91, 0.91, 0.91, 0.91, 0.9, 0.9, 0.89, 0.89, 0.89, 0.89, 0.89, 0.88, 0.88, 0.88, 0.88, 0.88, 
                0.88, 0.87, 0.87, 0.87],# 0.87],
        'Distance (ly)': [12.5, 31.2, 101.4, 16.1, 12.3, 167.2, 188, 4.2, 16.1, 101.4, 31.5, 31.3, 39.3, 105.5, 29.9, 42.2, 12, 48.9, 16.5, 
                          39.6, 23.6, 12, 84.6, 28.7, 23.6],# 1487],
        'Mass (Compared to Jupiter)': [0.003, 0.012, 0.026, 0.003, 0.003, 0.016, 0.01, 0.002, 0.003, 0.026, 0.004, 0.022, 0.012, 0.02, 0.009, 
                                       0.021, 0.005, 0.014, 0.016, 0.021, 0.015, 0.005, 0.023, 0.014, 0.019], #0.016],
    }
    df = pd.DataFrame(data)
    return df

app.layout = html.Div([
    html.H1('Exoplanets in the Night Sky'),
    dcc.Graph(id='exoplanet-globe'),
    dash_table.DataTable(
        id='exoplanet-table',
        columns=[{"name": col, "id": col} for col in ['Exoplanet', 'Galactic Longitude', 'Galactic Latitude', 'ESI', 'Distance (ly)', 'Mass (Compared to Jupiter)']],
        page_size=10,  # Number of rows to display per page
        style_table={'overflowX': 'auto'},
    ),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Refresh every minute (for live data or updates)
        n_intervals=0
    )
])

@app.callback(
    Output('exoplanet-globe', 'figure'),
    Output('exoplanet-table', 'data'),  # Output for the DataTable
    [Input('interval-component', 'n_intervals')]
)
def update_figure(n):
    df = fetch_exoplanet_data()

    # Convert galactic coordinates (longitudes and latitudes) to 3D Cartesian coordinates
    df['x'] = df['Distance (ly)'] * np.cos(np.radians(df['Galactic Latitude'])) * np.cos(np.radians(df['Galactic Longitude']))
    df['y'] = df['Distance (ly)'] * np.cos(np.radians(df['Galactic Latitude'])) * np.sin(np.radians(df['Galactic Longitude']))
    df['z'] = df['Distance (ly)'] * np.sin(np.radians(df['Galactic Latitude']))

    # Create a 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['ESI'],  # Use ESI to represent color/size
            colorscale='Viridis',
            opacity=0.8
        ),
        text=df['Exoplanet'],  # Hover text shows exoplanet name
        hoverinfo='text'
    )])

    # Adjust layout to simulate viewing exoplanets in 3D space
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=0.00001581, y=0.00001581, z=0.00001581)  # Set camera to give a good view of the 3D space
            ),
        ),
        title="Exoplanets in the Night Sky"
    )

    return fig, df.to_dict('records')  # Return the DataFrame as a list of records for the table

if __name__ == '__main__':
    app.run_server(debug=True)
