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
    df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI (2).csv')
    # print(df)
    return df

app.layout = html.Div([
    html.H1('Exoplanets from the perspective of the HWO'),
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
    df['x'] = df['Distance'] * np.cos(np.radians(df['Latitude'])) * np.cos(np.radians(df['Longitude']))
    df['y'] = df['Distance'] * np.cos(np.radians(df['Latitude'])) * np.sin(np.radians(df['Longitude']))
    df['z'] = df['Distance'] * np.sin(np.radians(df['Latitude']))

    # Create a 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='markers',
        marker=dict(
            size= df['Radius compared to Jupiter']*100, # change 188 to find max
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
