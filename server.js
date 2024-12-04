const express = require('express');
const app = express();
const PORT = 2333;

// Middleware to parse JSON request bodies
app.use(express.json());

// In-memory storage for GPS data (replace with a database in production)
const gpsDataStore = [];

// POST endpoint to add GPS data
app.post('/api/gps/', async (req, res) => {
    try {
        // Hardcoded data for testing
        const gpsEntry = { DeviceID: "12345", Latitude: 12.34, Longitude: 56.78, Timestamp: "2024-12-04T12:00:00Z" };
        gpsDataStore.push(gpsEntry); // Save to the in-memory array
    
    
        // Respond with success (using 201 for creation)
        res.status(201).json({ message: "GPS data added successfully", data: gpsEntry });
    } catch (error) {
        console.error("Error adding GPS data:", error);
        res.status(500).json({ error: "Failed to add GPS data" });
    }
});

// GET endpoint to retrieve GPS data by DeviceID

app.get('/api/gps/:DeviceID', async (req, res) => {
    try {
        const { DeviceID } = req.params;

        // Log the DeviceID to check the request
          console.log(`GET request for DeviceID: ${DeviceID}`);

        // Filter the in-memory storage for the requested DeviceID
        const deviceData = gpsDataStore.filter(data => data.DeviceID === DeviceID);

        if (deviceData.length === 0) {
            return res.status(404).json({ error: `No GPS data found for DeviceID: ${DeviceID}` });
        }

        // Respond with the data
        res.status(200).json(deviceData);
    } catch (error) {
        console.error("Error retrieving GPS data:", error);
        res.status(500).json({ error: "Failed to retrieve GPS data" });
    }
});

// Health check endpoint (optional)
app.get('/', (req, res) => {
    res.status(200).send("GPS API is running!");
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
