import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Planet Data Entry Form"),
    
    # ESI input field
    html.Div([
        html.Label('ESI:'),
        dcc.Input(id='esi-input', type='text', value='')
    ]),
    
    # Magnitude input field
    html.Div([
        html.Label('Magnitude:'),
        dcc.Input(id='magnitude-input', type='text', value='')
    ]),
    
    # Mass to Jupiter input field
    html.Div([
        html.Label('Mass to Jupiter:'),
        dcc.Input(id='mass-input', type='text', value='')
    ]),
    
    # Radius to Jupiter input field
    html.Div([
        html.Label('Radius to Jupiter:'),
        dcc.Input(id='radius-input', type='text', value='')
    ]),
    
    # Incline Angle input field
    html.Div([
        html.Label('Incline Angle:'),
        dcc.Input(id='incline-input', type='text', value='')
    ]),
    
    # Distance input field
    html.Div([
        html.Label('Distance:'),
        dcc.Input(id='distance-input', type='text', value='')
    ]),
    
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0),
    
    # Output div for displaying array
    html.Div(id='output-array', style={'margin-top': '20px'})
])

# Callback to update the output when the form is submitted
@app.callback(
    Output('output-array', 'children'),
    Input('submit-button', 'n_clicks'),
    State('esi-input', 'value'),
    State('magnitude-input', 'value'),
    State('mass-input', 'value'),
    State('radius-input', 'value'),
    State('incline-input', 'value'),
    State('distance-input', 'value')
)
def update_output(n_clicks, esi, magnitude, mass, radius, incline, distance):
    if n_clicks > 0:
        # Save inputs into an array
        planet_data = [esi, magnitude, mass, radius, incline, distance]
        
        # Return the array as a string for display
        return f"Planet Data: {planet_data}"
    return ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
