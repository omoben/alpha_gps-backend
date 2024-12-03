const express = require('express');
const app = express();
const port = 2333;

// Middleware to parse JSON data
app.use(express.json());

// Example route
app.get('/api/sample', (req, res) => {
    res.json({ message: "Hello from Node.js backend!" });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

