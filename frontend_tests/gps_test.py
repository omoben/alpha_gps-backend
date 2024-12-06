import requests

# URL for the GET request to fetch GPS data
url = "http://localhost:2333/api/gps"

# Make a GET request to the API
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()
    print("GPS Data:", data)
else:
    print(f"Error: {response.status_code}")

