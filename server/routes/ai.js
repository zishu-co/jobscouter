const express = require('express');
const router = express.Router();

// Store courses data for AI prompts
let aiCourseData = [];

// Endpoint to receive course data for AI
router.post('/send-courses', (req, res) => {
  try {
    const { courses } = req.body;
    
    if (!courses || !Array.isArray(courses)) {
      return res.status(400).json({ error: 'Invalid course data format' });
    }
    
    // Save course data for use in AI prompts
    aiCourseData = courses;
    
    res.json({ success: true, message: 'Course data saved for AI prompts' });
  } catch (error) {
    console.error('Error handling course data for AI:', error);
    res.status(500).json({ error: 'Failed to process course data' });
  }
});

// Endpoint to get saved course data (for AI prompt generation)
router.get('/courses', (req, res) => {
  res.json(aiCourseData);
});

module.exports = router;
module.exports.getCoursesForAI = () => aiCourseData;
