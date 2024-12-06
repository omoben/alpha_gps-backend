import dash
import dash_leaflet as dl
from dash import html
from dash import Dash

# Initialize the Dash app
app = Dash(__name__)

# Layout with Map Component
app.layout = html.Div([
    html.H1("GPS Tracking Dashboard", style={"textAlign": "center"}),
    dl.Map(center=[12.34, 56.78], zoom=10, children=[
        dl.TileLayer(),  # Base map layer
        dl.Marker(position=[12.34, 56.78], children=[
            dl.Tooltip("DeviceID: 12345"),  # Tooltip with device info
            dl.Popup("Latitude: 12.34, Longitude: 56.78"),  # Popup with more details
        ])
    ], style={'width': '100%', 'height': '500px'}),
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)

