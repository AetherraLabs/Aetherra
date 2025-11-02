# Aetherra WebSocket & SSE Streaming API

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This document describes Aetherra's real-time streaming APIs for bidirectional communication between clients and the Aetherra Hub. These APIs enable real-time AI interactions, consciousness state monitoring, and system event streaming.

## Purpose and scope

- Establish WebSocket connections for bidirectional communication
- Stream Server-Sent Events (SSE) for server-to-client updates
- Receive AI chat responses in real-time
- Monitor consciousness state changes
- Subscribe to system events and metrics

## API Overview

Aetherra provides two primary streaming mechanisms:

| Protocol      | Use Case                        | Direction       | Advantages                         | Limitations    |
| ------------- | ------------------------------- | --------------- | ---------------------------------- | -------------- |
| **WebSocket** | Interactive chat, bidirectional | Bidirectional   | Full duplex, low latency           | More complex   |
| **SSE**       | Monitoring, notifications       | Server → Client | Simple, HTTP-based, auto-reconnect | Unidirectional |

---

## WebSocket API

### Connection Endpoint

```
ws://localhost:3001/api/ai/stream_ws
wss://aetherra.ai/api/ai/stream_ws  # Production (TLS)
```

### Connection Lifecycle

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ 1. WebSocket Upgrade Request
     ├────────────────────────────────────▶
     │                              ┌─────┴────┐
     │                              │ Aetherra │
     │                              │   Hub    │
     │ 2. 101 Switching Protocols   │          │
     ◀────────────────────────────────┤          │
     │                              └─────┬────┘
     │
     │ 3. Send message (JSON)
     ├────────────────────────────────────▶
     │
     │ 4. Receive chunks (JSON)
     ◀────────────────────────────────────┤
     │
     │ 5. Receive final message
     ◀────────────────────────────────────┤
     │
     │ 6. Close connection
     ├────────────────────────────────────▶
     │
```

### Authentication

**Query parameter:**
```
ws://localhost:3001/api/ai/stream_ws?token=YOUR_API_TOKEN
```

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:3001/api/ai/stream_ws?token=abc123');
```

### Message Protocol

#### Client → Server Messages

**Chat message request:**
```json
{
  "type": "chat",
  "prompt": "What is the current system health?",
  "session_id": "optional-session-id",
  "stream": true,
  "options": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "model": "default"
  }
}
```

**Ping message (keepalive):**
```json
{
  "type": "ping"
}
```

**Subscribe to consciousness state:**
```json
{
  "type": "subscribe",
  "channel": "consciousness"
}
```

#### Server → Client Messages

**Message chunk (streaming response):**
```json
{
  "type": "chunk",
  "content": "The current system health is ",
  "delta": "The current system health is ",
  "session_id": "sess_abc123",
  "chunk_index": 0
}
```

**Final message (completion):**
```json
{
  "type": "complete",
  "content": "The current system health is excellent with a score of 0.92.",
  "session_id": "sess_abc123",
  "total_chunks": 15,
  "metrics": {
    "response_time_ms": 1234,
    "tokens_generated": 42,
    "model_used": "gpt-4"
  }
}
```

**Error message:**
```json
{
  "type": "error",
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT",
  "retry_after": 60
}
```

**Pong message (keepalive response):**
```json
{
  "type": "pong",
  "timestamp": 1730476800
}
```

**Consciousness state update:**
```json
{
  "type": "consciousness",
  "state": "reflecting",
  "health_score": 0.92,
  "timestamp": 1730476800,
  "details": {
    "active_tasks": 3,
    "memory_usage_mb": 256,
    "uptime_hours": 48.5
  }
}
```

### Client Examples

#### JavaScript (Browser)

```javascript
class AetherraWebSocketClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.messageHandlers = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.url}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('Connected to Aetherra');
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('Disconnected from Aetherra');
      };
    });
  }

  handleMessage(message) {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message);
    }
  }

  on(messageType, handler) {
    this.messageHandlers.set(messageType, handler);
  }

  sendChat(prompt, options = {}) {
    const message = {
      type: 'chat',
      prompt,
      stream: true,
      session_id: options.sessionId || `sess_${Date.now()}`,
      options: {
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1000,
      }
    };
    this.ws.send(JSON.stringify(message));
  }

  subscribe(channel) {
    this.ws.send(JSON.stringify({
      type: 'subscribe',
      channel
    }));
  }

  ping() {
    this.ws.send(JSON.stringify({ type: 'ping' }));
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const client = new AetherraWebSocketClient(
  'ws://localhost:3001/api/ai/stream_ws',
  'your_api_token'
);

await client.connect();

// Handle streaming responses
let fullResponse = '';
client.on('chunk', (msg) => {
  fullResponse += msg.delta;
  console.log('Received:', msg.delta);
});

client.on('complete', (msg) => {
  console.log('Full response:', fullResponse);
  console.log('Metrics:', msg.metrics);
});

client.on('error', (msg) => {
  console.error('Error:', msg.error);
});

// Subscribe to consciousness updates
client.subscribe('consciousness');
client.on('consciousness', (msg) => {
  console.log('Consciousness state:', msg.state, msg.health_score);
});

// Send a chat message
client.sendChat('What is the meaning of existence?');

// Keepalive ping every 30 seconds
setInterval(() => client.ping(), 30000);
```

#### Python (websocket-client)

```python
import json
import websocket
import threading
import time

class AetherraWebSocketClient:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.ws = None
        self.message_handlers = {}
        self.connected = False

    def connect(self):
        ws_url = f"{self.url}?token={self.token}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        # Run in background thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

        # Wait for connection
        for _ in range(50):
            if self.connected:
                return True
            time.sleep(0.1)
        return False

    def _on_open(self, ws):
        print("Connected to Aetherra")
        self.connected = True

    def _on_message(self, ws, message):
        try:
            msg = json.loads(message)
            self._handle_message(msg)
        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")

    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print("Disconnected from Aetherra")
        self.connected = False

    def _handle_message(self, message):
        msg_type = message.get('type')
        handler = self.message_handlers.get(msg_type)
        if handler:
            handler(message)

    def on(self, message_type, handler):
        self.message_handlers[message_type] = handler

    def send_chat(self, prompt, session_id=None, **options):
        message = {
            'type': 'chat',
            'prompt': prompt,
            'stream': True,
            'session_id': session_id or f"sess_{int(time.time())}",
            'options': {
                'temperature': options.get('temperature', 0.7),
                'max_tokens': options.get('max_tokens', 1000),
            }
        }
        self.ws.send(json.dumps(message))

    def subscribe(self, channel):
        self.ws.send(json.dumps({
            'type': 'subscribe',
            'channel': channel
        }))

    def ping(self):
        self.ws.send(json.dumps({'type': 'ping'}))

    def close(self):
        if self.ws:
            self.ws.close()

# Usage
client = AetherraWebSocketClient(
    'ws://localhost:3001/api/ai/stream_ws',
    'your_api_token'
)

if client.connect():
    # Handle streaming responses
    full_response = []

    def on_chunk(msg):
        full_response.append(msg['delta'])
        print(f"Received: {msg['delta']}", end='', flush=True)

    def on_complete(msg):
        print(f"\n\nFull response: {''.join(full_response)}")
        print(f"Metrics: {msg['metrics']}")

    def on_error(msg):
        print(f"Error: {msg['error']}")

    client.on('chunk', on_chunk)
    client.on('complete', on_complete)
    client.on('error', on_error)

    # Send chat message
    client.send_chat('What is the current system health?')

    # Keep alive
    time.sleep(30)
    client.close()
```

---

## Server-Sent Events (SSE) API

### Connection Endpoint

```
GET /api/ai/stream
GET /api/consciousness/stream
GET /api/events/stream
```

### Connection Setup

**HTTP Request:**
```http
GET /api/ai/stream HTTP/1.1
Host: localhost:3001
Accept: text/event-stream
Authorization: Bearer YOUR_API_TOKEN
Cache-Control: no-cache
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

### Event Format

SSE events follow the standard format:

```
event: message
data: {"type": "chunk", "content": "Hello", "delta": "Hello"}

event: message
data: {"type": "chunk", "content": "Hello world", "delta": " world"}

event: complete
data: {"type": "complete", "content": "Hello world", "total_chunks": 2}
```

**Event types:**
- `message` - Regular streaming message (chunk, error, etc.)
- `complete` - Stream completion
- `error` - Error occurred
- `ping` - Keepalive ping

### Chat Streaming Endpoint

**POST /api/ai/stream**

Send a chat message and receive streaming response via SSE.

**Request:**
```http
POST /api/ai/stream HTTP/1.1
Host: localhost:3001
Content-Type: application/json
Accept: text/event-stream
Authorization: Bearer YOUR_API_TOKEN

{
  "prompt": "Explain quantum computing",
  "stream": true,
  "session_id": "sess_123",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response stream:**
```
event: message
data: {"type": "chunk", "content": "Quantum", "delta": "Quantum", "chunk_index": 0}

event: message
data: {"type": "chunk", "content": "Quantum computing", "delta": " computing", "chunk_index": 1}

event: message
data: {"type": "chunk", "content": "Quantum computing uses", "delta": " uses", "chunk_index": 2}

...

event: complete
data: {"type": "complete", "content": "Quantum computing uses quantum mechanical phenomena...", "total_chunks": 45}
```

### Consciousness State Streaming

**GET /api/consciousness/stream**

Stream real-time consciousness state updates.

**Request:**
```http
GET /api/consciousness/stream HTTP/1.1
Host: localhost:3001
Accept: text/event-stream
Authorization: Bearer YOUR_API_TOKEN
```

**Response stream:**
```
event: consciousness
data: {"state": "reflecting", "health_score": 0.92, "timestamp": 1730476800}

event: consciousness
data: {"state": "active", "health_score": 0.94, "timestamp": 1730476830}

event: consciousness
data: {"state": "resting", "health_score": 0.91, "timestamp": 1730476860}
```

### System Events Streaming

**GET /api/events/stream**

Stream system events and notifications.

**Request:**
```http
GET /api/events/stream?categories=homeostasis,self_improvement HTTP/1.1
Host: localhost:3001
Accept: text/event-stream
Authorization: Bearer YOUR_API_TOKEN
```

**Response stream:**
```
event: homeostasis
data: {"category": "homeostasis", "event": "health_check", "score": 0.89, "timestamp": 1730476800}

event: self_improvement
data: {"category": "self_improvement", "event": "proposal_created", "proposal_id": "prop_123", "timestamp": 1730476815}

event: self_improvement
data: {"category": "self_improvement", "event": "proposal_approved", "proposal_id": "prop_123", "timestamp": 1730476820}
```

### Client Examples

#### JavaScript (Browser)

```javascript
class AetherraSSEClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.eventSource = null;
    this.eventHandlers = new Map();
  }

  connect() {
    const urlWithToken = `${this.url}?token=${this.token}`;
    this.eventSource = new EventSource(urlWithToken);

    this.eventSource.onopen = () => {
      console.log('SSE connection established');
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      if (this.eventSource.readyState === EventSource.CLOSED) {
        console.log('Connection closed, attempting to reconnect...');
      }
    };

    // Handle different event types
    this.eventSource.addEventListener('message', (e) => {
      this.handleEvent('message', JSON.parse(e.data));
    });

    this.eventSource.addEventListener('complete', (e) => {
      this.handleEvent('complete', JSON.parse(e.data));
    });

    this.eventSource.addEventListener('consciousness', (e) => {
      this.handleEvent('consciousness', JSON.parse(e.data));
    });

    this.eventSource.addEventListener('error', (e) => {
      this.handleEvent('error', JSON.parse(e.data));
    });
  }

  handleEvent(eventType, data) {
    const handler = this.eventHandlers.get(eventType);
    if (handler) {
      handler(data);
    }
  }

  on(eventType, handler) {
    this.eventHandlers.set(eventType, handler);
  }

  close() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }
}

// Usage for chat streaming
async function streamChat(prompt) {
  const response = await fetch('http://localhost:3001/api/ai/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Authorization': 'Bearer your_token'
    },
    body: JSON.stringify({
      prompt: prompt,
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.type === 'chunk') {
          process.stdout.write(data.delta);
        } else if (data.type === 'complete') {
          console.log('\n\nCompleted!');
        }
      }
    }
  }
}

// Usage for consciousness monitoring
const consciousnessClient = new AetherraSSEClient(
  'http://localhost:3001/api/consciousness/stream',
  'your_token'
);

consciousnessClient.on('consciousness', (data) => {
  console.log(`State: ${data.state}, Health: ${data.health_score}`);
});

consciousnessClient.connect();
```

#### Python (sseclient-py)

```python
import json
import requests
from sseclient import SSEClient

class AetherraSSEClient:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }

    def stream(self, callback):
        """Stream events and call callback for each event"""
        response = requests.get(
            self.url,
            headers=self.headers,
            stream=True
        )

        client = SSEClient(response)
        for event in client.events():
            try:
                data = json.loads(event.data)
                callback(event.event, data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse event: {e}")

    def stream_chat(self, prompt, callback, **options):
        """Stream chat response"""
        response = requests.post(
            f"{self.url.replace('/consciousness/stream', '')}/api/ai/stream",
            headers=self.headers,
            json={
                'prompt': prompt,
                'stream': True,
                **options
            },
            stream=True
        )

        client = SSEClient(response)
        for event in client.events():
            try:
                data = json.loads(event.data)
                callback(event.event, data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse event: {e}")

# Usage for consciousness monitoring
def handle_consciousness(event_type, data):
    if event_type == 'consciousness':
        print(f"State: {data['state']}, Health: {data['health_score']}")

client = AetherraSSEClient(
    'http://localhost:3001/api/consciousness/stream',
    'your_token'
)
client.stream(handle_consciousness)

# Usage for chat streaming
def handle_chat(event_type, data):
    if event_type == 'message' and data['type'] == 'chunk':
        print(data['delta'], end='', flush=True)
    elif event_type == 'complete':
        print(f"\n\nCompleted in {data.get('metrics', {}).get('response_time_ms')}ms")

chat_client = AetherraSSEClient(
    'http://localhost:3001',
    'your_token'
)
chat_client.stream_chat('What is quantum computing?', handle_chat)
```

#### curl Example

```bash
# SSE chat streaming
curl -N -H "Accept: text/event-stream" \
     -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello Aetherra", "stream": true}' \
     http://localhost:3001/api/ai/stream

# Consciousness monitoring
curl -N -H "Accept: text/event-stream" \
     -H "Authorization: Bearer your_token" \
     http://localhost:3001/api/consciousness/stream

# System events
curl -N -H "Accept: text/event-stream" \
     -H "Authorization: Bearer your_token" \
     "http://localhost:3001/api/events/stream?categories=homeostasis,self_improvement"
```

---

## Error Handling

### Connection Errors

**401 Unauthorized:**
```json
{
  "type": "error",
  "error": "Invalid or missing authentication token",
  "code": "AUTH_REQUIRED"
}
```

**429 Rate Limited:**
```json
{
  "type": "error",
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT",
  "retry_after": 60
}
```

**503 Service Unavailable:**
```json
{
  "type": "error",
  "error": "Service temporarily unavailable",
  "code": "SERVICE_UNAVAILABLE",
  "retry_after": 30
}
```

### Reconnection Strategy

**Exponential backoff:**
```javascript
class ReconnectingClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
  }

  connect() {
    try {
      this.ws = new WebSocket(`${this.url}?token=${this.token}`);

      this.ws.onopen = () => {
        console.log('Connected');
        this.reconnectDelay = 1000; // Reset delay
      };

      this.ws.onclose = () => {
        console.log('Disconnected, reconnecting...');
        setTimeout(() => this.connect(), this.reconnectDelay);

        // Exponential backoff
        this.reconnectDelay = Math.min(
          this.reconnectDelay * 2,
          this.maxReconnectDelay
        );
      };

      this.ws.onerror = (error) => {
        console.error('Error:', error);
      };
    } catch (error) {
      console.error('Connection failed:', error);
      setTimeout(() => this.connect(), this.reconnectDelay);
    }
  }
}
```

---

## Performance Considerations

### Connection Limits

- **Max concurrent WebSocket connections per client:** 5
- **Max concurrent SSE connections per client:** 10
- **Message rate limit:** 100 messages/minute per connection
- **Max message size:** 1 MB

### Keepalive

**WebSocket ping/pong:**
- Client should send ping every 30 seconds
- Server responds with pong
- Connection closed if no ping received for 60 seconds

**SSE keepalive:**
- Server sends comment lines every 15 seconds
- Browser automatically reconnects on disconnect

### Buffering

**Client-side buffering:**
```javascript
class BufferedClient {
  constructor() {
    this.buffer = [];
    this.maxBufferSize = 100;
  }

  handleChunk(chunk) {
    this.buffer.push(chunk);

    if (this.buffer.length >= this.maxBufferSize) {
      this.flushBuffer();
    }
  }

  flushBuffer() {
    const content = this.buffer.join('');
    this.renderContent(content);
    this.buffer = [];
  }
}
```

---

## Security Best Practices

### Authentication

- Always use HTTPS/WSS in production
- Store tokens securely (not in localStorage)
- Rotate tokens regularly
- Use separate tokens for different clients

### Rate Limiting

- Respect rate limit headers
- Implement exponential backoff
- Queue messages client-side if needed

### Input Validation

- Validate all client messages
- Sanitize prompt content
- Limit message sizes
- Filter malicious payloads

---

## Monitoring and Debugging

### Connection State Monitoring

```javascript
class MonitoredClient {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.metrics = {
      connectTime: null,
      messageCount: 0,
      errorCount: 0,
      reconnectCount: 0
    };
  }

  connect() {
    const startTime = Date.now();
    this.ws = new WebSocket(`${this.url}?token=${this.token}`);

    this.ws.onopen = () => {
      this.metrics.connectTime = Date.now() - startTime;
      console.log(`Connected in ${this.metrics.connectTime}ms`);
    };

    this.ws.onmessage = () => {
      this.metrics.messageCount++;
    };

    this.ws.onerror = () => {
      this.metrics.errorCount++;
    };

    this.ws.onclose = () => {
      this.metrics.reconnectCount++;
      console.log('Metrics:', this.metrics);
    };
  }
}
```

### Logging

```javascript
// Enable debug logging
const ws = new WebSocket('ws://localhost:3001/api/ai/stream_ws?token=abc123&debug=1');

// Log all messages
ws.onmessage = (event) => {
  console.log('[RECV]', new Date().toISOString(), event.data);
};

ws.send = ((original) => {
  return function(data) {
    console.log('[SEND]', new Date().toISOString(), data);
    return original.call(this, data);
  };
})(ws.send);
```

---

## Related Documentation

- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - REST API documentation
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Connection troubleshooting
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment
- [AETHERRA_SECURITY_SYSTEM.md](./AETHERRA_SECURITY_SYSTEM.md) - Security best practices

---

Status: ✅ Complete - Comprehensive WebSocket and SSE streaming API documentation

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
