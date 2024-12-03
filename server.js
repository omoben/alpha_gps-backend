const express = require('express');
const app = express();

app.get('/api/nodejs', (req, res) => {
    res.json({ message: 'Hello from Node.js!' });
});

const PORT = 2333;
app.listen(PORT, () => {
    console.log(`Node.js server running on port ${PORT}`);
});
