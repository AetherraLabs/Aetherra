# NeuroHub - The AI Package Manager

NeuroHub is the AI-native package manager for consciousness programming. It provides a complete ecosystem for discovering, installing, and publishing .aetherplug modules for the aetherra platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm 8+
- Python 3.8+ (for frontend development server)

### Installation & Startup

#### Windows
```bash
# Clone or navigate to the neurohub directory
cd neurohub

# Run the startup script
start-neurohub.bat
```

#### Linux/macOS
```bash
# Make the script executable
chmod +x start-neurohub.sh

# Run the startup script
./start-neurohub.sh
```

#### Manual Setup
```bash
# Install dependencies
npm install

# Start backend API (Terminal 1)
npm start

# Start frontend server (Terminal 2)
npm run frontend
```

### Access Points
- **Frontend**: http://localhost:8080
- **API**: http://localhost:3001/api/v1
- **Health Check**: http://localhost:3001/api/health

## 🏗️ Architecture

NeuroHub consists of two main components:

### Backend API (`server.js`)
- **Express.js** REST API server
- **Plugin management** (search, publish, download)
- **User authentication** with API keys
- **File upload handling** for .aetherplug packages
- **Analytics and statistics**

### Frontend (`index.html`)
- **Modern responsive UI** with search and filtering
- **Real-time API integration** via `neurohub-client.js`
- **Plugin marketplace** with installation commands
- **User authentication** and publishing interface

## 📚 API Reference

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "your_username",
  "email": "your@email.com",
  "password": "your_password"
}
```

#### Verify API Key
```http
POST /api/v1/auth/verify
Authorization: Bearer YOUR_API_KEY
```

### Plugin Discovery

#### Search Plugins
```http
GET /api/v1/plugins/search?q=transcriber&category=audio&sort=downloads&limit=20&offset=0
```

#### Get Featured Plugins
```http
GET /api/v1/plugins/featured
```

#### Get Popular Plugins
```http
GET /api/v1/plugins/popular?limit=10
```

#### Get Specific Plugin
```http
GET /api/v1/plugins/transcriber
```

### Plugin Publishing

#### Publish New Plugin
```http
POST /api/v1/plugins/publish
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data

metadata: {
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My awesome plugin",
  "tags": ["memory", "optimization"],
  "license": "MIT",
  "repository": "https://github.com/user/plugin"
}
package: [FILE: plugin.aetherplug]
```

#### Update Plugin
```http
POST /api/v1/plugins/my-plugin/update
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data

version: "1.0.1"
package: [FILE: plugin.aetherplug]
```

### Plugin Installation

#### Download Plugin
```http
GET /api/v1/plugins/transcriber/download?version=latest
```

#### Get Plugin Statistics
```http
GET /api/v1/plugins/transcriber/stats
```

### Analytics

#### Get Overview Statistics
```http
GET /api/v1/analytics/overview
```

## 🔌 Plugin Development

### Plugin Structure
```
my-plugin/
├── aetherra-plugin.json     # Plugin metadata
├── main.aether               # Main plugin code
├── README.md               # Documentation
└── tests/                  # Test files
    └── test_main.aether
```

### Plugin Metadata (`aetherra-plugin.json`)
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My awesome aetherra plugin",
  "author": "Your Name",
  "license": "MIT",
  "tags": ["memory", "optimization"],
  "dependencies": {
    "aetherra-core": ">=2.0.0"
  },
  "main": "main.aether",
  "repository": "https://github.com/username/my-plugin"
}
```

### Publishing Process

1. **Create Account**
   ```bash
   # Register via web interface or API
   curl -X POST http://localhost:3001/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"myuser","email":"me@example.com","password":"secret"}'
   ```

2. **Package Plugin**
   ```bash
   # Create .aetherplug package (zip format)
   zip -r my-plugin.aetherplug my-plugin/
   ```

3. **Publish via Web Interface**
   - Sign in to NeuroHub
   - Click "Publish Plugin"
   - Fill in details and upload package

4. **Publish via API**
   ```bash
   curl -X POST http://localhost:3001/api/v1/plugins/publish \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -F 'metadata={"name":"my-plugin","version":"1.0.0","description":"My plugin"}' \
     -F 'package=@my-plugin.aetherplug'
   ```

## 💻 Frontend Integration

### Using the NeuroHub Client

```javascript
// Initialize client
const neuroHub = new NeuroHubClient();

// Search plugins
const results = await neuroHub.searchPlugins('transcriber');

// Download plugin
await neuroHub.downloadAndSave('transcriber');

// Authenticate user
await neuroHub.authenticate('your-api-key');

// Publish plugin
await neuroHub.publishPlugin(metadata, packageFile);
```

### Custom Integration

```html
<script src="neurohub-client.js"></script>
<script>
  window.aetherHub.getFeaturedPlugins()
    .then(plugins => {
      console.log('Featured plugins:', plugins);
    });
</script>
```

## 🛠️ Development

### Running in Development Mode

```bash
# Backend with auto-reload
npm run dev

# Frontend with auto-reload
npm run frontend

# Run tests
npm test

# Lint code
npm run lint
```

### File Structure

```
neurohub/
├── server.js              # Backend API server
├── neurohub-client.js     # Frontend API client
├── index.html            # Main web interface
├── package.json          # Dependencies & scripts
├── start-neurohub.bat    # Windows startup script
├── start-neurohub.sh     # Linux/macOS startup script
├── uploads/              # Plugin package uploads
└── README.md            # This documentation
```

### Configuration

#### Environment Variables
```bash
PORT=3001                 # API server port
NODE_ENV=development      # Environment mode
MAX_FILE_SIZE=50MB       # Max plugin package size
```

#### API Configuration
```javascript
// In neurohub-client.js
const neuroHub = new NeuroHubClient('http://localhost:3001/api/v1');
```

## 🔐 Security

### API Key Management
- API keys are generated during user registration
- Store securely and never expose in client-side code
- Use HTTPS in production environments

### File Upload Security
- File size limits enforced
- File type validation for .aetherplug packages
- Secure file storage in uploads directory

### Rate Limiting
- API endpoints are rate-limited to prevent abuse
- Authentication required for publishing operations

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   NODE_ENV=production
   PORT=3001
   ```

2. **Database Migration**
   ```bash
   # Replace in-memory storage with persistent database
   # PostgreSQL, MongoDB, or SQLite recommended
   ```

3. **File Storage**
   ```bash
   # Use cloud storage (AWS S3, Google Cloud Storage)
   # Configure in server.js
   ```

4. **Reverse Proxy**
   ```nginx
   # nginx configuration
   server {
       listen 80;
       server_name neurohub.yourdomain.com;

       location /api/ {
           proxy_pass http://localhost:3001;
       }

       location / {
           root /path/to/neurohub;
           index index.html;
       }
   }
   ```

### Cloud Deployment

#### Docker
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  neurohub:
    build: .
    ports:
      - "3001:3001"
    volumes:
      - ./uploads:/app/uploads
    environment:
      - NODE_ENV=production
```

## 📊 Analytics & Monitoring

### Built-in Analytics
- Plugin download statistics
- User registration metrics
- Popular plugins tracking
- Author contribution metrics

### Health Monitoring
```bash
# Check API health
curl http://localhost:3001/api/health

# Response
{
  "status": "healthy",
  "timestamp": "2025-06-30T12:00:00Z",
  "version": "1.0.0"
}
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Standards
- Follow JavaScript ES6+ standards
- Use consistent indentation (2 spaces)
- Add comments for complex logic
- Write tests for new features

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Documentation**: [aetherra.dev/docs](https://aetherra.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/Zyonic88/aetherra/issues)
- **Community**: [aetherra Community](https://aetherra.dev/community)

---

**NeuroHub** - Empowering the future of AI-consciousness programming through collaborative plugin development.
