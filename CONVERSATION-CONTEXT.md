# Conversation Context Management

## Overview

The Doctor Procedures Bedrock App now supports **intelligent conversation context management** to maintain continuity across multiple interactions with the AI assistant. This feature addresses the stateless nature of Lambda functions by storing conversation history in the frontend and sending relevant context with each request.

## Features

### 🧠 **Context-Aware Conversations**
- **Automatic Context Storage**: Every user message and AI response is stored in the frontend's conversation history
- **Context Transmission**: Recent conversation history (last 6 messages) is sent with each new request to provide context
- **Intent Detection**: The system automatically detects whether Bedrock successfully mapped the user's intent to a specific action
- **Visual Indicators**: Different visual cues show whether messages were processed as specific intents or general conversation

### 📊 **Visual Context Indicators**

#### Message Types:
- **🟢 Intent Mapped**: Green border and checkmark - request successfully mapped to a specific action (add procedure, get quote, show history)
- **🟡 General Conversation**: Yellow border - conversational responses that maintain context for future questions  
- **🔴 Error**: Red border - system errors or failures

#### Context Information:
- **Header Display**: Shows current number of context messages stored
- **Context Counter**: Real-time display of conversation length
- **Clear Context Button**: Allows users to reset conversation history when needed

### 🔄 **Context Management**

#### Automatic Features:
- **Context Limiting**: Automatically limits context to last 40 messages (20 exchanges) to prevent payload size issues
- **Smart Context Building**: Builds enhanced prompts that include recent conversation history
- **Session Persistence**: Maintains context throughout the browser session

#### Manual Controls:
- **Clear Context**: Users can manually clear conversation history with the "Clear Context" button
- **Context Status**: Real-time display of how many messages are stored in context

## Technical Implementation

### Frontend (React)

```javascript
// Conversation history storage
const [conversationHistory, setConversationHistory] = useState([]);

// Enhanced API call with context
const response = await apiClient.chatWithAgent(inputMessage, sessionId, conversationHistory);

// Context structure
{
  role: 'user|assistant',
  content: 'message content',
  timestamp: 'ISO timestamp',
  intentMapped: true|false
}
```

### Backend (Lambda)

```python
# Context processing in intent mapper
conversation_history = request_body.get('conversationHistory', [])
recent_context = conversation_history[-6:]  # Last 3 exchanges

# Enhanced prompt building
context_summary = "Previous conversation context:\n"
for msg in recent_context:
    role = "User" if msg.get('role') == 'user' else "Assistant"
    content = msg.get('content', '')[:200]
    context_summary += f"{role}: {content}\n"

enhanced_prompt = f"{context_summary}\nCurrent question: {user_text}"
```

### Intent Detection

```python
# Heuristic-based intent detection
intent_mapped = True
if any(phrase in completion.lower() for phrase in [
    "i don't understand", "i'm not sure", "could you clarify", 
    "i don't have enough information", "i'm not able to", 
    "sorry, i don't", "i can't", "that's not something i can"
]):
    intent_mapped = False
```

## Usage Examples

### Scenario 1: Contextual Follow-up Questions

**User**: "Show me Dr. Johnson's procedure history"
**AI**: ✅ *Intent recognized* - [Shows procedure history]

**User**: "What's the average cost for those procedures?"
**AI**: 💭 *Using context* - "Based on Dr. Johnson's procedures I just showed you, the average cost is..."

### Scenario 2: General Conversation with Context

**User**: "Hi, I'm new to using this system"
**AI**: 💭 *General conversation* - "Welcome! I can help you manage doctor procedures..."

**User**: "What can you help me with?"
**AI**: 💭 *Using context* - "Since you mentioned you're new, let me explain..."

### Scenario 3: Context Reset

**User**: Clicks "Clear Context" button
**AI**: 🔄 "Conversation context has been cleared. I'll start fresh with your next question."

## Benefits

### For Users:
- **Natural Conversations**: Can ask follow-up questions without repeating context
- **Better Understanding**: AI maintains awareness of previous discussion
- **Visual Feedback**: Clear indicators of how messages are being processed
- **Control**: Ability to reset context when changing topics

### For System:
- **Improved Accuracy**: Context helps Bedrock provide more relevant responses
- **Reduced Repetition**: Users don't need to repeat information
- **Better Intent Recognition**: Context helps disambiguate user requests
- **Debugging Support**: Visual indicators help identify processing issues

## Configuration

### Context Limits:
- **Message History**: Last 40 messages (20 exchanges)
- **Context Transmission**: Last 6 messages per request
- **Message Length**: 200 characters per message in context summary

### Visual Styling:
- **Intent Mapped**: Green borders, success indicators
- **General Conversation**: Yellow borders, context indicators  
- **Errors**: Red borders, error indicators
- **Context Status**: Header displays and input area indicators

## Future Enhancements

### Planned Features:
- **Persistent Context**: Store conversation history in DynamoDB for cross-session persistence
- **Smart Context Summarization**: Use AI to summarize long conversations
- **Topic Detection**: Automatically detect topic changes and suggest context resets
- **Context Search**: Allow users to search through conversation history
- **Export Conversations**: Download conversation history for record keeping

### Advanced Context Features:
- **Entity Extraction**: Identify and maintain key entities (doctor names, procedures, etc.)
- **Intent Confidence Scoring**: More sophisticated intent detection
- **Context Relevance Scoring**: Prioritize most relevant context messages
- **Multi-user Context**: Support for multiple concurrent conversations

## Troubleshooting

### Common Issues:

1. **Context Not Working**: Check that conversation history is being stored in frontend state
2. **Large Payloads**: Context automatically limits to prevent API payload size issues
3. **Intent Detection**: Yellow indicators show when messages are treated as general conversation
4. **Memory Usage**: Context automatically cleans up old messages to prevent memory issues

### Debug Information:
- Check browser console for context transmission logs
- Use visual indicators to understand message processing
- Monitor context counter in header for storage verification
- CloudWatch logs show context usage in Lambda functions

## API Changes

### Request Format:
```json
{
  "text": "user message",
  "sessionId": "session-id",
  "conversationHistory": [
    {
      "role": "user",
      "content": "previous message",
      "timestamp": "2025-08-01T10:00:00.000Z"
    }
  ]
}
```

### Response Format:
```json
{
  "response": "AI response",
  "sessionId": "session-id",
  "intentMapped": true,
  "contextUsed": true,
  "originalMessage": "user message"
}
```

This conversation context system transforms the Doctor Procedures Bedrock App from a stateless request-response system into an intelligent, context-aware conversational interface that can maintain continuity and provide more natural interactions.
