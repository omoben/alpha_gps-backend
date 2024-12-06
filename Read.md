# Alpha GPS - Version 0.0.1

## Features
- **Frontend**: Dash application displaying GPS data on a map using `dash-leaflet`.
- **Backend**: Node.js API for handling GPS data (POST and GET requests).
- **Dockerized**: Fully containerized for easy deployment.

# Documenting Version 0.0.1

## Description of Work Done:
Frontend: Implemented a Dash-based UI with dash-leaflet for GPS tracking, displaying static coordinates with map markers.
Backend: Set up a Node.js API with basic routes to accept and fetch GPS data, tested API endpoints using Python.
Integration: Verified frontend interaction with backend API for fetching and displaying GPS data.
Dockerization: Encapsulated the project in a Docker container for easy deployment and version control.
Version Tag: Tagged as 0.0.1 for the initial working implementation.


# Usage

## Running with Docker
1. Pull the Docker image:
## docker pull <your_dockerhub_username>/alpha_gps:0.0.1
2. Run the container:
## docker run -p 8050:8050 <your_dockerhub_username>/alpha_gps:0.0.1
3. Access the app at: [http://127.0.0.1:8050](http://127.0.0.1:8050)

## Notes
- This version displays static GPS data. Future versions will dynamically fetch live GPS updates from the API.
