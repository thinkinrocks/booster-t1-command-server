# Booster Platform API

A FastAPI server for processing commands.

## Features

- FastAPI framework for high performance
- Command processing endpoint at `/command`
- Automatic API documentation
- Health check endpoint
- Type-safe request/response models

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Development Mode
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Production Deployment (SystemD on Ubuntu)

For production deployment as a systemd service on Ubuntu:

```bash
sudo ./scripts/install-systemd.sh
```

This will install the server as a system service that:
- Starts automatically on boot
- Runs as a dedicated service user
- Includes automatic restart on failure
- Provides centralized logging

See [SYSTEMD_DEPLOYMENT.md](SYSTEMD_DEPLOYMENT.md) for detailed instructions.

## API Endpoints

### Root Endpoint
- **GET** `/` - Welcome message and available endpoints

### Health Check
- **GET** `/health` - Health status of the API

### Command Endpoint
- **POST** `/command` - Execute commands

#### Request Format
```json
{
  "command": "command_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

#### Response Format
```json
{
  "success": true,
  "message": "Command executed successfully",
  "data": {
    "result": "example_result"
  }
}
```

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Execute a command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ping",
    "parameters": {"message": "hello"}
  }'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/command",
    json={
        "command": "ping",
        "parameters": {"message": "hello"}
    }
)
print(response.json())
```

## Adding New Commands

To add new commands, implement the command logic in the `execute_command` function in `main.py`:

```python
@app.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    command = request.command
    parameters = request.parameters or {}
    
    if command == "your_command":
        # Implement your command logic here
        return CommandResponse(
            success=True,
            message="Command executed",
            data={"result": "your_result"}
        )
```

## Project Structure

```
booster-platform/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Next Steps

1. Implement specific command handlers
2. Add command validation and error handling
3. Add authentication/authorization if needed
4. Add database integration if needed
5. Add logging and monitoring

