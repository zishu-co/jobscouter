import axios from 'axios'

// DeepSeek API configuration
const AI_API_URL = 'https://api.deepseek.com/v1/chat/completions'
const API_KEY = '' // Consider using environment variables

// Create a messages history store - can be expanded to support multiple conversations
const conversationStore = new Map();

/**
 * Sends a message to DeepSeek API using streaming response
 * 
 * @param {string} message - The user's message
 * @param {Object} jobContext - Context about the current job
 * @param {string} conversationId - Optional ID for managing multiple conversations
 * @param {function} onChunk - Callback function that receives each chunk of text as it arrives
 * @returns {Promise<Object>} - Final result when streaming completes
 */
export async function chatWithAI(message, jobContext, conversationId = 'default', onChunk) {
  try {
    // Initialize conversation if it doesn't exist
    if (!conversationStore.has(conversationId)) {
      // Start with system message containing job context
      const systemMessage = {
        role: "system", 
        content: `You are a helpful job search assistant created by 自塾. Here is information about the job: ${JSON.stringify(jobContext)}`
      };
      conversationStore.set(conversationId, [systemMessage]);
    }
    
    // Get current conversation history
    const messages = conversationStore.get(conversationId);
    
    // Add user message to history
    messages.push({ role: "user", content: message });
    
    // Make streaming API request
    const response = await fetch(AI_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: messages,
        stream: true  // Enable streaming
      })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let fullContent = '';
    
    // Process the stream
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // Decode chunk and process line by line
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim(); // Remove 'data: ' prefix
          
          if (data === '[DONE]') continue;
          
          try {
            const parsedData = JSON.parse(data);
            const contentChunk = parsedData.choices[0]?.delta?.content || '';
            
            if (contentChunk) {
              fullContent += contentChunk;
              // Call the callback with each new piece of content
              if (onChunk) onChunk(contentChunk);
            }
          } catch (e) {
            console.error('Error parsing streaming data:', e);
          }
        }
      }
    }
    
    // Add assistant's complete message to history
    messages.push({ role: "assistant", content: fullContent });
    
    // Update conversation store
    conversationStore.set(conversationId, messages);
    
    return {
      success: true,
      data: {
        reply: fullContent,
        conversationId: conversationId
      }
    };
  } catch (error) {
    console.error('AI API error:', error);
    return {
      success: false,
      error: error.message || '请求AI服务失败'
    };
  }
}

/**
 * Clear conversation history
 * 
 * @param {string} conversationId - ID of conversation to clear
 */
export function clearConversation(conversationId = 'default') {
  conversationStore.delete(conversationId);
}

/**
 * Get current conversation history
 * 
 * @param {string} conversationId - ID of conversation to retrieve
 * @returns {Array} - Conversation messages
 */
export function getConversationHistory(conversationId = 'default') {
  return conversationStore.has(conversationId) 
    ? [...conversationStore.get(conversationId)] 
    : [];
}