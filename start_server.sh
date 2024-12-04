#!/bin/bash

# Start the Python backend
echo "Starting Python backend..."
cd python && nohup python3 main.py &

# Start the Node.js backend
echo "Starting Node.js backend..."
cd node.js && nohup node server.js &

echo "Both servers are running!"

