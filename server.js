const express = require("express");
const app = express();
const PORT = 2333;

// Middleware to parse JSON requests
app.use(express.json());

// Root route
app.get("/", (req, res) => {
  res.send("Backend server is running!");
});

// Sample route
app.get("/api/sample", (req, res) => {
  res.json({ message: "This is a sample response" });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

