# 🎨 Aetherra GUI Setup Guide

This guide covers the setup and development of Aetherra's unified React + Flask GUI system.

## 🏗️ Architecture Overview

Aetherra features a **dual GUI architecture**:

- **React Frontend** (`Aetherra/lyrixa_core/gui/`): Modern cyberpunk interface built with React, Vite, and Three.js
- **Flask API Server** (`Aetherra/gui/`): Python backend providing REST APIs and Socket.IO real-time communication
- **Unified Launcher** (`Aetherra/gui/launch_aetherra_gui.py`): Starts both frontend and backend together

## 🚀 Quick Setup for Contributors

### 1. Clone and Setup Python Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Aetherra.git
cd Aetherra

# Setup Python virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Node.js/React Environment

```bash
# Navigate to React frontend
cd Aetherra/lyrixa_core/gui

# Install Node.js dependencies
npm install

# Return to project root
cd ../../../
```

### 3. Launch the Unified GUI

```bash
# Start both React frontend and Flask API server
python Aetherra/gui/launch_aetherra_gui.py
```

This automatically starts:
- **React Frontend**: http://localhost:3000
- **Flask API Server**: http://localhost:8686
- **Socket.IO Connection**: Real-time communication between frontend and backend

## [TOOL] Development Workflows

### Frontend Development (React)

```bash
# Start only the React frontend (requires API server running separately)
cd Aetherra/lyrixa_core/gui
npm run dev

# The frontend will be available at http://localhost:3000
# Make sure the Flask API server is running on port 8686
```

### Backend Development (Flask)

```bash
# Start only the Flask API server
python Aetherra/gui/web_interface_server.py --debug

# The API server will be available at http://localhost:8686
# Includes Socket.IO endpoint at /socket.io/
```

### Full-Stack Development

```bash
# Start both systems together (recommended)
python Aetherra/gui/launch_aetherra_gui.py

# Both frontend and backend restart automatically on file changes
```

## 🌐 Communication Architecture

### Socket.IO Real-Time Communication

The React frontend connects to the Flask backend via Socket.IO:

- **Client**: Socket.IO client v4.8.1 (React)
- **Server**: Flask-SocketIO v5.5.1 (Python)
- **Transport**: HTTP polling → WebSocket upgrade
- **Events**: `connect`, `disconnect`, `metrics`, `chat_message`, `status`

### Connection Configuration

**React Frontend** (`AetherraGUI.jsx`):
```javascript
const socket = io("http://localhost:8686", {
    transports: ["polling", "websocket"],
    timeout: 10000,
    reconnection: false, // Manual reconnection handling
    forceNew: true
});
```

**Flask Backend** (`web_interface_server.py`):
```python
self.socketio = SocketIO(
    self.app,
    cors_allowed_origins="*",
    async_mode="threading",
    ping_timeout=60,
    ping_interval=25
)
```

## 🛠️ Troubleshooting

### Common Issues

**1. "WebSocket connection failed"**
- **Cause**: Frontend trying to connect before backend is ready
- **Solution**: The unified launcher includes a 1-second delay to ensure proper startup order

**2. "Module not found" errors**
- **Cause**: Missing Python dependencies
- **Solution**: `pip install -r requirements.txt`

**3. "npm install" failures**
- **Cause**: Missing Node.js or incompatible version
- **Solution**: Install Node.js 16+ from nodejs.org

**4. Port conflicts**
- **Cause**: Ports 3000 or 8686 already in use
- **Solution**: Stop other services or modify port configurations

### Debug Mode

Enable detailed logging:

```bash
# Flask backend with debug logging
python Aetherra/gui/web_interface_server.py --debug

# React frontend with debug info (check browser console)
cd Aetherra/lyrixa_core/gui && npm run dev
```

## 📁 File Structure

```
Aetherra/
├── gui/                          # Flask Backend
│   ├── launch_aetherra_gui.py   # 🚀 Unified launcher
│   ├── web_interface_server.py  # Flask + Socket.IO server
│   └── ...
├── lyrixa_core/
│   └── gui/                     # React Frontend
│       ├── src/
│       │   ├── AetherraGUI.jsx  # Main React component
│       │   └── ...
│       ├── package.json         # Node.js dependencies
│       └── vite.config.js       # Vite configuration
└── requirements.txt             # Python dependencies
```

## 🔄 Development Dependencies

**Python Backend**:
- Flask ≥2.3.0
- Flask-SocketIO ≥5.5.1
- Flask-CORS ≥4.0.0
- python-socketio ≥5.13.0

**Node.js Frontend**:
- React 18.2.0
- Vite 7.0.6
- socket.io-client 4.8.1
- @react-three/fiber 8.18.0
- framer-motion 11.18.2

## 🚢 Deployment Notes

For production deployment:

1. **Build React Frontend**: `npm run build`
2. **Configure CORS**: Update Flask-SocketIO origins
3. **Use Production WSGI**: Replace development server with Gunicorn
4. **Environment Variables**: Set production API keys and configurations

## 🤝 Contributing to the GUI

### Frontend Contributions
- React components in `Aetherra/lyrixa_core/gui/src/`
- Follow React best practices and use TypeScript where possible
- Test Socket.IO communication with backend

### Backend Contributions
- Flask routes and Socket.IO handlers in `Aetherra/gui/web_interface_server.py`
- Ensure CORS compatibility for development
- Test API endpoints with frontend integration

### Testing Changes
```bash
# Always test the unified system
python Aetherra/gui/launch_aetherra_gui.py

# Verify Socket.IO connection in browser console
# Check that both servers start without errors
```

---

For more information, see [CONTRIBUTING.md](../CONTRIBUTING.md) and join our Discord community!

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

