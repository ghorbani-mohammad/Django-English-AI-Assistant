# Chat History API Documentation

## Overview

This API provides comprehensive chat history management for the English AI Assistant application. It allows users to view, manage, and analyze their conversation history with the AI assistant.

## Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_jwt_access_token>
```

## Base URL

```
https://your-domain.com/api/v1/cht/
```

## Endpoints

### 1. Get Chat History for Specific Grammar Topic

**Endpoint:** `GET /history/{grammar_id}/`

**Description:** Retrieve chat history for a specific grammar topic

**Parameters:**
- `grammar_id` (path): ID of the grammar topic
- `page` (query, optional): Page number (default: 1)
- `page_size` (query, optional): Number of items per page (default: 50, max: 200)
- `message_type` (query, optional): Filter by message type (`text` or `audio`)
- `sender_type` (query, optional): Filter by sender (`user` or `ai`)
- `search` (query, optional): Search in message content and transcriptions

**Example Request:**
```bash
GET /api/v1/cht/history/123/?page=1&page_size=20&message_type=text&search=present%20perfect
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "count": 45,
  "next": "https://your-domain.com/api/v1/cht/history/123/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_name": "John Doe",
      "display_content": "Can you explain present perfect tense?",
      "message_type": "text",
      "sender_type": "user",
      "audio_file": null,
      "audio_duration": null,
      "formatted_date": "2024-01-15 14:30:25",
      "created_at": "2024-01-15T14:30:25.123456Z"
    },
    {
      "id": 2,
      "user_name": "AI Assistant",
      "display_content": "Present perfect tense is used to describe...",
      "message_type": "text",
      "sender_type": "ai",
      "audio_file": null,
      "audio_duration": null,
      "formatted_date": "2024-01-15 14:30:27",
      "created_at": "2024-01-15T14:30:27.456789Z"
    }
  ]
}
```

### 2. Get All Chat History

**Endpoint:** `GET /history/`

**Description:** Retrieve all chat history for the authenticated user across all grammar topics

**Parameters:**
- `page` (query, optional): Page number
- `page_size` (query, optional): Number of items per page
- `grammar_id` (query, optional): Filter by specific grammar topic
- `date_from` (query, optional): Filter messages from date (YYYY-MM-DD format)
- `date_to` (query, optional): Filter messages to date (YYYY-MM-DD format)

**Example Request:**
```bash
GET /api/v1/cht/history/?grammar_id=123&date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "count": 150,
  "next": "https://your-domain.com/api/v1/cht/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_email": "user@example.com",
      "user_name": "John Doe",
      "grammar": 123,
      "grammar_title": "Present Perfect Tense",
      "content": "Can you explain present perfect tense?",
      "display_content": "Can you explain present perfect tense?",
      "message_type": "text",
      "sender_type": "user",
      "audio_file": null,
      "audio_duration": null,
      "transcription": null,
      "response_id": null,
      "session_id": "1_123_20240115143025",
      "user_timezone": "UTC",
      "thumb_up": 0,
      "thumb_down": 0,
      "engagement_score": 0,
      "is_user_message": true,
      "is_ai_message": false,
      "is_audio_message": false,
      "created_at": "2024-01-15T14:30:25.123456Z",
      "updated_at": "2024-01-15T14:30:25.123456Z"
    }
  ]
}
```

### 3. Get Individual Message Details

**Endpoint:** `GET /message/{message_id}/`

**Description:** Retrieve detailed information about a specific message

**Example Request:**
```bash
GET /api/v1/cht/message/123/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "id": 123,
  "user": 1,
  "user_email": "user@example.com",
  "user_name": "John Doe",
  "grammar": 456,
  "grammar_title": "Present Perfect Tense",
  "content": "I have been studying English for 2 years",
  "display_content": "I have been studying English for 2 years",
  "message_type": "audio",
  "sender_type": "user",
  "audio_file": "https://your-domain.com/media/chat_audio/2024/01/15/audio_1_20240115_143025.wav",
  "audio_duration": 3.5,
  "transcription": "I have been studying English for 2 years",
  "response_id": null,
  "session_id": "1_456_20240115143025",
  "user_timezone": "UTC",
  "thumb_up": 2,
  "thumb_down": 0,
  "engagement_score": 2,
  "is_user_message": true,
  "is_ai_message": false,
  "is_audio_message": true,
  "created_at": "2024-01-15T14:30:25.123456Z",
  "updated_at": "2024-01-15T14:30:25.123456Z"
}
```

### 4. Update Message Engagement

**Endpoint:** `POST /message/{message_id}/engagement/`

**Description:** Add thumbs up or thumbs down to a message

**Request Body:**
```json
{
  "action": "thumb_up"  // or "thumb_down"
}
```

**Example Request:**
```bash
POST /api/v1/cht/message/123/engagement/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "action": "thumb_up"
}
```

**Example Response:**
```json
{
  "message": "Thumbs up added",
  "thumb_up": 3,
  "thumb_down": 0
}
```

### 5. Get Chat Statistics

**Endpoint:** `GET /statistics/`

**Description:** Get comprehensive statistics about user's chat activity

**Parameters:**
- `grammar_id` (query, optional): Filter by specific grammar topic
- `date_from` (query, optional): Filter from date (YYYY-MM-DD format)
- `date_to` (query, optional): Filter to date (YYYY-MM-DD format)

**Example Request:**
```bash
GET /api/v1/cht/statistics/?grammar_id=123&date_from=2024-01-01
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "total_messages": 245,
  "user_messages": 123,
  "ai_messages": 122,
  "text_messages": 200,
  "audio_messages": 45,
  "grammar_topics_discussed": 15,
  "total_thumbs_up": 45,
  "total_thumbs_down": 3,
  "engagement_score": 42,
  "recent_activity_7_days": 23
}
```

### 6. Delete Chat History

**Endpoint:** `DELETE /history/{grammar_id}/delete/`

**Description:** Soft delete all chat history for a specific grammar topic

**Example Request:**
```bash
DELETE /api/v1/cht/history/123/delete/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "message": "Chat history deleted for grammar topic: Present Perfect Tense",
  "messages_deleted": 45
}
```

### 7. Export Chat History

**Endpoint:** `GET /history/{grammar_id}/export/`

**Description:** Export all chat history for a specific grammar topic as JSON

**Example Request:**
```bash
GET /api/v1/cht/history/123/export/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "grammar_topic": "Present Perfect Tense",
  "export_date": "2024-01-15T14:30:25.123456Z",
  "total_messages": 45,
  "messages": [
    {
      "id": 1,
      "user_email": "user@example.com",
      "content": "Can you explain present perfect tense?",
      "message_type": "text",
      "sender_type": "user",
      "created_at": "2024-01-15T14:30:25.123456Z"
    }
    // ... more messages
  ]
}
```

## WebSocket Integration

The chat history is automatically saved when users interact with the WebSocket chat interface:

### WebSocket URL
```
ws://your-domain.com/chat/{grammar_id}/?token={jwt_access_token}
```

### Message Saving
- **User text messages**: Automatically saved when sent via WebSocket
- **User audio messages**: Audio file saved and transcription stored
- **AI responses**: Saved with unique response_id for engagement tracking

### Engagement via WebSocket
You can send thumbs up/down directly through WebSocket:

```json
{
  "command": "thumb-up",
  "responseId": "20240115143025"
}
```

```json
{
  "command": "thumb-down", 
  "responseId": "20240115143025"
}
```

## Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**400 Bad Request:**
```json
{
  "error": "Invalid action. Use 'thumb_up' or 'thumb_down'"
}
```

## Frontend Implementation Examples

### React.js Example

```javascript
// Chat History Hook
import { useState, useEffect } from 'react';
import axios from 'axios';

const useChatHistory = (grammarId, token) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async (page = 1, filters = {}) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        ...filters
      });
      
      const response = await axios.get(
        `/api/v1/cht/history/${grammarId}/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      setMessages(response.data.results);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch chat history');
    } finally {
      setLoading(false);
    }
  };

  const addEngagement = async (messageId, action) => {
    try {
      await axios.post(
        `/api/v1/cht/message/${messageId}/engagement/`,
        { action },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Refresh the message or update state
      fetchHistory();
    } catch (err) {
      console.error('Failed to add engagement:', err);
    }
  };

  return {
    messages,
    loading,
    error,
    fetchHistory,
    addEngagement
  };
};

// Usage in component
const ChatHistoryComponent = ({ grammarId, token }) => {
  const { messages, loading, error, fetchHistory, addEngagement } = useChatHistory(grammarId, token);

  useEffect(() => {
    fetchHistory();
  }, [grammarId]);

  const handleThumbsUp = (messageId) => {
    addEngagement(messageId, 'thumb_up');
  };

  const handleThumbsDown = (messageId) => {
    addEngagement(messageId, 'thumb_down');
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="chat-history">
      {messages.map(message => (
        <div key={message.id} className={`message ${message.sender_type}`}>
          <div className="message-content">
            {message.is_audio_message && message.audio_file && (
              <audio controls>
                <source src={message.audio_file} type="audio/wav" />
              </audio>
            )}
            <p>{message.display_content}</p>
          </div>
          
          {message.is_ai_message && (
            <div className="engagement-buttons">
              <button onClick={() => handleThumbsUp(message.id)}>
                👍 {message.thumb_up}
              </button>
              <button onClick={() => handleThumbsDown(message.id)}>
                👎 {message.thumb_down}
              </button>
            </div>
          )}
          
          <small>{message.formatted_date}</small>
        </div>
      ))}
    </div>
  );
};
```

### Vue.js Example

```javascript
// Chat History Composable
import { ref, reactive } from 'vue';
import axios from 'axios';

export function useChatHistory() {
  const messages = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const pagination = reactive({
    page: 1,
    totalPages: 1,
    hasNext: false,
    hasPrevious: false
  });

  const fetchHistory = async (grammarId, token, filters = {}) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axios.get(`/api/v1/cht/history/${grammarId}/`, {
        params: {
          page: pagination.page,
          ...filters
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      messages.value = response.data.results;
      pagination.hasNext = !!response.data.next;
      pagination.hasPrevious = !!response.data.previous;
      pagination.totalPages = Math.ceil(response.data.count / 50);
      
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch chat history';
    } finally {
      loading.value = false;
    }
  };

  const getStatistics = async (token, grammarId = null) => {
    try {
      const params = grammarId ? { grammar_id: grammarId } : {};
      const response = await axios.get('/api/v1/cht/statistics/', {
        params,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to fetch statistics');
    }
  };

  return {
    messages,
    loading,
    error,
    pagination,
    fetchHistory,
    getStatistics
  };
}
```

## Message Types and Structure

### Text Message
```json
{
  "message_type": "text",
  "sender_type": "user",
  "content": "User's text message",
  "audio_file": null,
  "transcription": null
}
```

### Audio Message
```json
{
  "message_type": "audio", 
  "sender_type": "user",
  "content": "Transcribed text from audio",
  "audio_file": "https://domain.com/media/chat_audio/2024/01/15/audio_file.wav",
  "audio_duration": 3.5,
  "transcription": "Transcribed text from audio"
}
```

### AI Response Message
```json
{
  "message_type": "text",
  "sender_type": "ai", 
  "content": "AI assistant response",
  "response_id": "20240115143025",
  "thumb_up": 2,
  "thumb_down": 0
}
```

## Rate Limiting

Currently, there are no specific rate limits implemented, but consider implementing client-side throttling for:
- Message engagement actions (thumbs up/down)
- Frequent history fetching
- Statistics requests

## Security Notes

1. **Authentication Required**: All endpoints require valid JWT tokens
2. **User Isolation**: Users can only access their own chat history
3. **Soft Deletion**: Messages are soft-deleted, not permanently removed
4. **File Security**: Audio files are stored securely and require authentication

## Support

For technical issues or questions about the API, please contact the backend development team or refer to the main application documentation. 