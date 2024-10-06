import dash
from dash import dcc, html
from dash.dependencies import Output, Input
from dash import dash_table
import pandas as pd
import numpy as np
import base64
import plotly.graph_objects as go

app = dash.Dash(__name__)

# Function to fetch exoplanet data
def fetch_exoplanet_data():
    df = pd.read_csv('Exoplanets Info - Exoplanet_Data_Sorted_by_ESI (2).csv')
    return df

# Load GLB file
def load_glb(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode('utf-8')
    return f"data:application/octet-stream;base64,{encoded}"

# Function to generate a spherical grid
def generate_spherical_grid(radius, num_azimuth=24, num_polar=12):
    grid_lines = []
    phi = np.linspace(0, np.pi, num_polar)
    theta = np.linspace(0, 2 * np.pi, num_azimuth)

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

# Layout of the app
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%', 'height': '100vh'}, children=[
    html.H1('Exoplanets from the perspective of the HWO'),
    dcc.Graph(id='exoplanet-globe', style={'width': '100%', 'height': '1000%'}),
    dash_table.DataTable(
        id='exoplanet-table',
        columns=[
            {"name": col, "id": col} for col in ['Exoplanet', 'Galactic Longitude', 'Galactic Latitude', 'ESI', 'Distance (ly)', 'Mass (Compared to Jupiter)']
        ],
        page_size=10,
        style_table={'overflowX': 'auto'},
    ),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,
        n_intervals=0
    ),
    html.Div(id='3d-viewer', style={'width': '100%', 'height': '600px'})  # For 3D viewer
])

# Callback to update the exoplanet globe and table
@app.callback(
    Output('exoplanet-globe', 'figure'),
    Output('exoplanet-table', 'data'),
    Output('3d-viewer', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_figure(n):
    df = fetch_exoplanet_data()

    # Spherical coordinates transformation
    df['r'] = df['Distance']
    df['theta'] = np.degrees(df['Longitude'])
    df['phi'] = np.degrees(90 - df['Latitude'])

    df['x'] = df['r'] * np.sin(np.radians(df['phi'])) * np.cos(np.radians(df['theta']))
    df['y'] = df['r'] * np.sin(np.radians(df['phi'])) * np.sin(np.radians(df['theta']))
    df['z'] = df['r'] * np.cos(np.radians(df['phi']))

    df['hover_text'] = df.apply(lambda row: 
        f"Exoplanet: {row['Exoplanet']}<br>Longitude: {row['Longitude']:.2f}°<br>Latitude: {row['Latitude']:.2f}°<br>Distance: {row['Distance']:.2f} ly", axis=1)

    # Create planet scatter plot
    planet_trace = go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='markers',
        marker=dict(
            size=df['Magnitude'],
            color=df['ESI'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=df['hover_text'],
        hoverinfo='text'
    )

    grid_lines = generate_spherical_grid(4000)

    fig = go.Figure(data=[planet_trace] + grid_lines)

    fig.update_layout(
        clickmode='event+select',
        paper_bgcolor='black',
        font_color="white",
        scene=dict(
            xaxis=dict(visible=False, backgroundcolor='black'),
            yaxis=dict(visible=False, backgroundcolor='black'),
            zaxis=dict(visible=False, backgroundcolor='black'),
            camera=dict(
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=0, z=0)
            ),
        ),
        title="Exoplanets in the Night Sky"
    )

    # Include Three.js to render the GLB model
    glb_data = load_glb('assets/pythonplanet.glb')
    viewer = html.Div([
        html.Script(src='https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'),  # Load Three.js
        html.Script(src='https://threejs.org/examples/js/loaders/GLTFLoader.js'),  # Load GLTFLoader
        html.Div(id='threejs-scene', style={'width': '100%', 'height': '600px'}),
        html.Script(f"""
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer();
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.getElementById('threejs-scene').appendChild(renderer.domElement);
            const loader = new THREE.GLTFLoader();
            loader.load('{glb_data}', function(gltf) {{
                scene.add(gltf.scene);
                camera.position.z = 5;
                const animate = function () {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }};
                animate();
            }});
        """)
    ])

    return fig, df.to_dict('records'), viewer

if __name__ == '__main__':
    app.run_server(debug=True)
