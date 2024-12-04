# Python module for API interaction

import requests

BASE_URL = "http://localhost:2333/api/gps"

def add_gps_data(device_id, latitude, longitude, timestamp):
    payload = {
        "DeviceID": device_id,
        "Latitude": latitude,
        "Longitude": longitude,
        "Timestamp": timestamp,
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        if response.status_code == 201:
            print("GPS data added successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_gps_data(device_id):
    try:
        response = requests.get(f"{BASE_URL}/{device_id}")
        if response.status_code == 200:
            print("GPS data retrieved successfully!")
            return response.json()
        elif response.status_code == 404:
            print(f"No GPS data found for DeviceID: {device_id}")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

