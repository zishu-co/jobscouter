const { getStoredCourseInfo } = require('../routes/chat');

// When building your prompt for the AI, include the course information:
function buildPromptWithContext(userMessage) {
  const courseInfo = getStoredCourseInfo();
  let prompt = userMessage;
  
  // Add course information to the prompt if available
  if (courseInfo && courseInfo.length > 0) {
    const courseContext = courseInfo.map(course => 
      `Course: ${course.name}, Description: ${course.description || 'N/A'}`
    ).join('\n');
    
    prompt = `
Context information:
--- Course Information ---
${courseContext}
--- End Course Information ---

User message: ${userMessage}
    `.trim();
  }
  
  return prompt;
}

module.exports = { buildPromptWithContext };