const express = require('express');
const app = express();
const aiRoutes = require('./routes/ai');

// Register routes
app.use('/api/ai', aiRoutes);

module.exports = app;