const express = require('express');
const router = express.Router();

router.post('/', async (req, res) => {
  try {
    const { message } = req.body;
    
    // Use message directly without course context
    let enhancedPrompt = message;
    
    // Use the enhanced prompt with your AI service
    // ...existing AI service call code...
    
    // Return AI response
    // ...existing response handling...
  } catch (error) {
    console.error('Chat API error:', error);
    res.status(500).json({ error: 'Error processing chat request' });
  }
});

module.exports = router;