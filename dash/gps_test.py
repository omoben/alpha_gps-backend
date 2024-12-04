import socketio
import time

# Create a Socket.IO client
sio = socketio.Client()

# Define the event for receiving real-time GPS data
@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.event
def gpsData(data):
    print(f"Received real-time GPS data: {data}")

# Connect to the server

sio.connect('http://localhost:2333')

# Send some test data (you can send real-time data from your GPS sys
while True:
    # Send mock GPS data every 10 seconds
    mock_data = {
        "DeviceID": "12345",
        "Latitude": 12.34,
        "Longitude": 56.78,
        "Timestamp": "2024-12-04T12:00:00Z"
    }
    sio.emit('gpsData', mock_data)
    time.sleep(10)  # Wait 10 seconds before sending the next set of data

