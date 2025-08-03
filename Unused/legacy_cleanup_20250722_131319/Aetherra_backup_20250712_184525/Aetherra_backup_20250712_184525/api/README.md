# Aetherra Script Execution API

A FastAPI-based REST API for executing and managing `.aether` scripts in the Aetherra OS environment.

## 🎯 Overview

This API provides a robust interface for:
- **Executing .aether scripts** asynchronously
- **Monitoring job status** and retrieving results
- **Managing script execution** with cancellation support
- **Listing available scripts** and system statistics

## 📁 Project Structure

```
Aetherra/api/
├── aether_server.py        # Main FastAPI application
├── job_controller.py       # Job execution orchestration
├── job_store.py           # In-memory job state management
├── models.py              # Pydantic request/response models
├── run_server.py          # Server startup script
├── test_api.py            # API testing client
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r Aetherra/api/requirements.txt
```

### 2. Start the API Server

```bash
python Aetherra/api/run_server.py
```

The server will start on `http://localhost:8000`

### 3. Explore the API

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 API Endpoints

### Core Endpoints

| Method | Endpoint           | Description                       |
| ------ | ------------------ | --------------------------------- |
| `POST` | `/run`             | Execute a .aether script          |
| `GET`  | `/status/{job_id}` | Get job status and results        |
| `POST` | `/cancel/{job_id}` | Cancel a running job              |
| `GET`  | `/jobs`            | List jobs with optional filtering |

### Utility Endpoints

| Method   | Endpoint        | Description                    |
| -------- | --------------- | ------------------------------ |
| `GET`    | `/health`       | API health check               |
| `GET`    | `/scripts`      | List available .aether scripts |
| `GET`    | `/stats`        | System statistics              |
| `DELETE` | `/jobs/cleanup` | Clean up old completed jobs    |

## [TOOL] Usage Examples

### Execute a Script

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "goal_autopilot.aether",
    "parameters": {"scan_interval": "30 minutes"},
    "context": {"priority": "high"}
  }'
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "script_name": "goal_autopilot.aether",
  "started_at": "2025-07-07T12:00:00Z"
}
```

### Check Job Status

```bash
curl "http://localhost:8000/status/123e4567-e89b-12d3-a456-426614174000"
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "script_name": "goal_autopilot.aether",
  "status": "completed",
  "output": {
    "processed": 5,
    "resumed": 2,
    "escalated": 1
  },
  "started_at": "2025-07-07T12:00:00Z",
  "completed_at": "2025-07-07T12:05:00Z"
}
```

### List Jobs

```bash
curl "http://localhost:8000/jobs?status=completed&limit=10"
```

### List Available Scripts

```bash
curl "http://localhost:8000/scripts"
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python Aetherra/api/test_api.py
```

This will test all API endpoints and verify functionality.

## 📊 Job Status States

| Status      | Description                         |
| ----------- | ----------------------------------- |
| `pending`   | Job created but not yet started     |
| `running`   | Job currently executing             |
| `completed` | Job finished successfully           |
| `failed`    | Job failed with an error            |
| `cancelled` | Job was cancelled before completion |

## 🔒 Error Handling

The API provides detailed error responses with appropriate HTTP status codes:

- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Job or script not found
- `500 Internal Server Error` - Server-side errors

Example error response:
```json
{
  "error": "ScriptNotFound",
  "message": "The specified script was not found",
  "details": {"script_name": "nonexistent.aether"}
}
```

## ⚙️ Configuration

### Environment Variables

- `AETHERRA_API_HOST` - Server host (default: `0.0.0.0`)
- `AETHERRA_API_PORT` - Server port (default: `8000`)
- `AETHERRA_SCRIPT_PATH` - Path to .aether scripts

### Script Discovery

The API automatically discovers `.aether` scripts in:
- `Aetherra/system/`
- `Aetherra/scripts/system/`

## [TOOL] Development

### Adding New Endpoints

1. Define request/response models in `models.py`
2. Add endpoint function to `aether_server.py`
3. Update tests in `test_api.py`

### Customizing Script Execution

Modify the `AetherScriptRunner` class in `job_controller.py` to integrate with your specific .aether runtime implementation.

## 🏗️ Architecture

### Components

- **FastAPI Server** (`aether_server.py`) - HTTP API layer
- **Job Controller** (`job_controller.py`) - Business logic orchestration
- **Job Store** (`job_store.py`) - In-memory state management
- **Script Runner** - .aether script execution engine

### Flow

1. **Request** → FastAPI receives script execution request
2. **Job Creation** → Controller creates job with unique ID
3. **Async Execution** → Script runs in background thread
4. **Status Updates** → Job store tracks progress and results
5. **Response** → Client polls for status and retrieves results

## 🔮 Future Enhancements

- **Database Integration** - Replace in-memory store with persistent storage
- **Authentication** - Add API key or OAuth authentication
- **Rate Limiting** - Implement request rate limiting
- **Webhooks** - Notify external services of job completion
- **Distributed Execution** - Scale across multiple workers
- **Enhanced Monitoring** - Metrics, logging, and observability

## 📝 License

Part of the Aetherra OS project. See main project LICENSE for details.

---

**🎉 Ready to execute .aether scripts via REST API!**
