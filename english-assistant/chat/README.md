# Chat WebSocket API with JWT Authentication

## Overview

The chat WebSocket provides real-time AI assistance for English language learning. It requires JWT authentication and supports both text and audio interactions.

## Authentication

The WebSocket connection requires a valid JWT access token to be passed as a query parameter.

### Connection URL Format
```ws://your-domain/chat/<grammar_id>/?token=<jwt_access_token>
```

### Example Connection
```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."; // Your JWT access token
const grammarId = "123"; // Grammar topic ID
const ws = new WebSocket(`ws://localhost:9080/chat/${grammarId}/?token=${token}`);
```

## Getting JWT Token

Before connecting to the WebSocket, you need to obtain a JWT token through the authentication API:

1. **Generate OTP**:
   ```bash
   POST /api/v1/auth/generate-otp/
   {
     "email": "user@example.com"
   }
   ```

2. **Verify OTP and get tokens**:
   ```bash
   POST /api/v1/auth/verify-otp/
   {
     "email": "user@example.com",
     "otp_code": "123456"
   }
   ```

3. **Use the access token** from the response for WebSocket connection.

## WebSocket Events

### Connection Events

- **Connection Success**: WebSocket opens successfully
- **Authentication Failure**: Connection closes with code `4001` if token is invalid or missing

### Message Format

All messages are JSON formatted:

```json
{
  "error": false,
  "message": "AI response text",
  "id": "response_id"
}
```

### Sending Messages

#### Text Message
```json
{
  "data": "Your English question here"
}
```

#### Audio Message
```json
{
  "audio": "data:audio/wav;base64,UklGRiQAAABXQVZFZm10..."
}
```

#### Ping (Keep-alive)
```json
{
  "command": "ping"
}
```

## Error Handling

### Authentication Errors
- **Code 4001**: Unauthorized - Invalid or missing JWT token
- **Connection Refused**: Token validation failed

### Message Errors
- Invalid JSON format will be logged and ignored
- Audio transcription errors are handled gracefully

## Audio Features

### Speech-to-Text
- Supports audio input in base64 format
- Uses OpenAI Whisper for transcription
- Responds with transcribed text before processing

### Text-to-Speech
- AI responses can be converted to speech
- Streaming audio delivery
- Uses OpenAI TTS with "alloy" voice

## Grammar Context

The WebSocket uses the `grammar_id` from the URL to provide context-aware assistance:

- Retrieves grammar topic from database
- Provides specialized help for specific grammar rules
- Falls back to general English assistance if grammar not found

## Example Usage

### JavaScript Client
```javascript
class ChatClient {
    constructor(grammarId, token) {
        this.grammarId = grammarId;
        this.token = token;
        this.ws = null;
    }

    connect() {
        const url = `ws://localhost:9080/chat/${this.grammarId}/?token=${this.token}`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log("Connected to chat");
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.message === "completed.") {
                console.log("Response complete");
            } else {
                console.log("AI:", data.message);
            }
        };

        this.ws.onclose = (event) => {
            if (event.code === 4001) {
                console.error("Authentication failed");
            } else {
                console.log("Connection closed");
            }
        };

        this.ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    sendMessage(text) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ data: text }));
        }
    }

    sendAudio(audioBase64) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ audio: audioBase64 }));
        }
    }

    ping() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ command: "ping" }));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage
const client = new ChatClient("123", "your_jwt_token");
client.connect();
client.sendMessage("Help me with present perfect tense");
```

### Python Client
```python
import asyncio
import websockets
import json

async def chat_client(grammar_id, token):
    uri = f"ws://localhost:9080/chat/{grammar_id}/?token={token}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to chat")
            
            # Send a message
            await websocket.send(json.dumps({
                "data": "Explain the difference between 'have been' and 'had been'"
            }))
            
            # Listen for responses
            async for message in websocket:
                data = json.loads(message)
                if data.get("message") == "completed.":
                    print("Response complete")
                    break
                else:
                    print(f"AI: {data.get('message', '')}")
                    
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 4001:
            print("Authentication failed")
        else:
            print(f"Connection closed: {e}")

# Usage
asyncio.run(chat_client("123", "your_jwt_token"))
```

## Security Notes

- JWT tokens have a 3-day expiration period
- Use HTTPS/WSS in production environments
- Token should be kept secure and not logged
- Invalid tokens result in immediate connection termination

## Rate Limiting

- Currently no rate limiting implemented
- Consider implementing rate limiting for production use
- OpenAI API has its own rate limits that apply

## Deployment

The WebSocket service runs on a separate port (9080) and should be proxied through nginx:

```nginx
location /chat/ {
    proxy_pass http://127.0.0.1:9080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
``` 