// Send chat to AI without course context
async function sendChatToAI(message) {
  // Create request without course context
  const requestBody = {
    message
  };
  
  // Send to your actual chat API endpoint
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  
  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }
  
  return response.json();
}