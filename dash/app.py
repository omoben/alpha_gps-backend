from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample in-memory storage for GPS data
gpsData = [
    {"DeviceID": "Excavator_001", "Latitude": 6.3329, "Longitude": 5.6037, "Timestamp": "2024-12-16T12:00:00Z"},
    {"DeviceID": "Excavator_002", "Latitude": 6.3350, "Longitude": 5.6060, "Timestamp": "2024-12-16T12:05:00Z"}
]

@app.route('/')
def splash():
    return render_template('index.html')  # Landing page

@app.route('/map')
def map():
    return render_template('map.html')  # Map page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        pass
    return render_template('login.html')  # Login page

# Route to fetch GPS data
@app.route('/api/gps', methods=['GET'])
def get_gps_data():
    return jsonify(gpsData)  # Return the GPS data as JSON

if __name__ == '__main__':
    app.run(debug=True)

