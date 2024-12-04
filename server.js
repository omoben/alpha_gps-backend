const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Middleware to parse JSON request bodies
app.use(express.json());

let gpsData = [];

app.post('/api/gps', (req, res) => {
  const { DeviceID, Latitude, Longitude, Timestamp } = req.body;

  // Validate incoming data
  if (!DeviceID || !Latitude || !Longitude || !Timestamp) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  // Add GPS data to the array
  gpsData.push({ DeviceID, Latitude, Longitude, Timestamp });

  // Emit real-time updates to all connected clients
  io.emit('gpsData', { DeviceID, Latitude, Longitude, Timestamp });

  return res.status(201).json({
    message: 'GPS data added successfully',
    data: { DeviceID, Latitude, Longitude, Timestamp }
  });
});

app.get('/api/gps/:DeviceID', (req, res) => {
  const { DeviceID } = req.params;
  const data = gpsData.filter(item => item.DeviceID === DeviceID);

  if (data.length === 0) {
    return res.status(404).json({ error: `No GPS data found for DeviceID: 
${DeviceID}` });
  }

  return res.status(200).json(data);
});

// Serve the frontend files if any
// app.use(express.static('frontend_directory'));

// Start the server
const PORT = process.env.PORT || 2333;
server.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

