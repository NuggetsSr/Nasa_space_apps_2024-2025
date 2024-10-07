import dash
from dash.dependencies import Output, Input, State
from dash import dcc, html
from dash import dash_table
import plotly.graph_objects as go
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

# Exoplanet data including galactic coordinates and other characteristics
def fetch_exoplanet_data():
    df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI (2).csv')

    def should_explore(row):
        if (row['ESI'] >= 0.93 and 
            0.1 <= row['Mass (Compared to Jupiter)'] <= 0.5 and 
            0.5 <= row['Radius compared to Jupiter'] <= 0.8 and
            row['Magnitude'] < 15):  # Adjust the magnitude threshold as needed
            return 1  # Explore
        else:
            return 0  # Not Explore

    df['Explore'] = df.apply(should_explore, axis=1)  # Create the 'Explore' label column
    return df

def generate_spherical_grid(radius, num_azimuth=24, num_polar=12):
    grid_lines = []
    phi = np.linspace(0, np.pi, num_polar)  # Polar angle
    theta = np.linspace(0, 2 * np.pi, num_azimuth)  # Azimuthal angle

    # Generate a single spherical shell
    for t in theta:
        x = radius * np.sin(phi) * np.cos(t)
        y = radius * np.sin(phi) * np.sin(t)
        z = radius * np.cos(phi)
        grid_lines.append(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines',
            line=dict(color='white', width=1),
            hoverinfo='skip',
            showlegend=False
        ))

    # Longitude lines (Azimuthal gridlines)
    for t in theta:
        x = np.outer(np.sin(np.pi / 2), np.cos(t)) * radius
        y = np.outer(np.sin(np.pi / 2), np.sin(t)) * radius
        z = np.outer(np.cos(np.linspace(0, np.pi, num_polar)), np.ones_like(t)) * radius
        grid_lines.append(go.Scatter3d(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            mode='lines',
            line=dict(color='white', width=1),
            hoverinfo='skip',
            showlegend=False
        ))

    # Latitude lines (Polar gridlines)
    for p in phi:
        x = np.outer(np.sin(p), np.cos(theta)) * radius
        y = np.outer(np.sin(p), np.sin(theta)) * radius
        z = np.outer(np.cos(p), np.ones_like(theta)) * radius
        grid_lines.append(go.Scatter3d(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            mode='lines',
            line=dict(color='white', width=1),
            hoverinfo='skip',
            showlegend=False
        ))

    return grid_lines

app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%', 'height': '150vh'},
    children=[
        html.Button('ESI', id='button-1'),
        html.Button('Orbital Period', id='button-2'),
        html.Button('Mass (Compared to Jupiter)', id='button-3'),
        html.H1('Exoplanets from the perspective of the HWO'),
        dcc.Graph(id='exoplanet-globe', style={'width': '100%', 'height': '100%'}, config={'scrollZoom': False, 'displayModeBar': True}),
        dash_table.DataTable(
            id='exoplanet-table',
            columns=[{"name": col, "id": col} for col in ['Exoplanet', 'Longitude', 'Latitude', 'ESI', 'Distance', 'Mass (Compared to Jupiter)', 'Radius compared to Jupiter']],
            page_size=10,
            style_table={'overflowX': 'auto'},
        ),
        dcc.Interval(id='interval-component', interval=240*1000, n_intervals=0),
        
    ]
)

@app.callback(
    Output('exoplanet-globe', 'figure'),
    Output('exoplanet-table', 'data'),
    [Input('interval-component', 'n_intervals'),
     Input('button-1', 'n_clicks'),
     Input('button-2', 'n_clicks'),
     Input('button-3', 'n_clicks')],
    [State('exoplanet-globe', 'relayoutData')]
)
def update_figure(n_intervals, btn1, btn2, btn3, relayoutData):
    df = fetch_exoplanet_data()

    # Convert spherical to Cartesian coordinates for 3D plot
    df['x'] = df['Distance'] * np.cos(np.radians(df['Latitude'])) * np.cos(np.radians(df['Longitude']))
    df['y'] = df['Distance'] * np.cos(np.radians(df['Latitude'])) * np.sin(np.radians(df['Longitude']))
    df['z'] = df['Distance'] * np.sin(np.radians(df['Latitude']))

    # Custom hover text
    marker_size = 100 / (df['Distance'] + 1) * 5
    marker_size = np.clip(marker_size, 15, None)

    # Default to ESI-based colorscale
    colorscale = [[0, 'red'], [1, 'green']]
    data_name = 'ESI (1 = green, 0 = red)'
    df['hover_text'] = df.apply(lambda row: f"Exoplanet: {row['Exoplanet']}<br>Longitude: {row['Longitude']:.2f}°<br>Latitude: {row['Latitude']:.2f}°<br>Distance: {row['Distance']:.2f} light years<br>ESI: {row['ESI']}", axis=1)
    data_color_col = df['ESI']

    # Identify which button was clicked using callback context
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'button-1'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Change to Orbital Period-based colorscale if button 2 is clicked
    if button_id == 'button-2':
        colorscale = [[0, 'blue'], [1, 'orange']]
        data_name = 'Orbital Period (days)'
        data_color_col = df['Orbital Period (days)']
        df['hover_text'] = df.apply(lambda row: f"Exoplanet: {row['Exoplanet']}<br>Longitude: {row['Longitude']:.2f}°<br>Latitude: {row['Latitude']:.2f}°<br>Distance: {row['Distance']:.2f} light years<br>Orbital Period: {row['Orbital Period (days)']}", axis=1)

    # Switch to Mass-based colorscale if button 3 is clicked
    elif button_id == 'button-3':
        colorscale = [[0, 'purple'], [1, 'yellow']]
        data_name = 'Mass (Compared to Jupiter)'
        data_color_col = df['Mass (Compared to Jupiter)']
        df['hover_text'] = df.apply(lambda row: f"Exoplanet: {row['Exoplanet']}<br>Longitude: {row['Longitude']:.2f}°<br>Latitude: {row['Latitude']:.2f}°<br>Distance: {row['Distance']:.2f} light years<br>Mass (Compared to Jupiter): {row['Mass (Compared to Jupiter)']}", axis=1)

    planet_trace = go.Scatter3d(
        x=df['x'],
        y=df['y'], 
        z=df['z'], 
        mode='markers',
        name=data_name, 
        marker=dict(
            size=marker_size, color=data_color_col,
            colorscale=colorscale, opacity=0.8,
            cmin=min(data_color_col), cmax=max(data_color_col)
        ),
        text=df['hover_text'], 
        hoverinfo='text',
    )

    grid_lines = generate_spherical_grid(4000)

    fig = go.Figure(data=[planet_trace] + grid_lines)

    camera = dict(eye=dict(x=0.00001581, y=0.00001581, z=0.00001581), 
                  center=dict(x=0, y=0, z=0),
                  up = dict(x=0.5,y=0.5, z=0))
    if isinstance(relayoutData, dict) and 'scene.camera' in relayoutData:
        camera = relayoutData['scene.camera']

    fig.update_layout(
        modebar_remove=['pan','zoom3d','pan3d', 'resetCameraDefault3d'],
        margin=dict(l=10, r=10,b=20),
        clickmode='event+select',
        paper_bgcolor='black',
        font_color="white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        scene=dict(
            xaxis=dict(visible=False,backgroundcolor='black'),
            yaxis=dict(visible=False,backgroundcolor='black'), 
            zaxis=dict(visible=False,backgroundcolor='black'), 
            camera=camera,
            dragmode = 'turntable'
        ),
        title="Exoplanets in the Night Sky"
    )

    return fig, df.to_dict('records')

if __name__ == '__main__':  
    app.run_server(debug=True, port=8051)
