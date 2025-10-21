# Booster T1 Command Server

A FastAPI-based command server for controlling the Booster T1 humanoid robot. This server provides RESTful endpoints for robot movement, hand gestures, and real-time status monitoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)

## 🚀 Features

### Robot Control
- **Movement Commands**: Forward/backward movement and left/right rotation
- **Hand Gestures**: Wave hand with configurable duration
- **Speed Control**: Configurable movement speeds (0.5 m/s forward, 0.2 m/s backward, 0.2 rad/s rotation)

### API & Server
- **RESTful API**: Clean, well-documented REST endpoints
- **Command Queueing**: Automatic command queueing when robot is busy (max queue size: 1)
- **Status Monitoring**: Real-time robot status and health check endpoints
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc
- **CORS Support**: Cross-origin request support for web clients

### Deployment Options
- **Development Mode**: Fast reload for rapid development
- **SystemD Service**: Production-ready systemd service for Ubuntu
- **Mock Mode**: Test without physical robot hardware

### Client Interface
- **Web Client**: Modern HTML/JavaScript client with real-time status
- **HTTP Client**: Simple curl-based command execution
- **Python SDK**: Direct integration using the robot commander API

## 📋 Requirements

### System Requirements
- **OS**: Ubuntu 18.04+ (for systemd deployment) or any OS with Python 3.7+
- **Python**: 3.7 or later
- **Network**: For robot control, network interface configuration required

### Dependencies
- FastAPI 0.104.1
- Uvicorn 0.24.0 (with standard extras)
- Pydantic 2.5.0
- Python-multipart 0.0.6
- Booster Robotics SDK (for real robot control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/thinkinrocks/booster-platform.git
cd booster-platform/booster-command-server
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Server

#### Mock Mode (No Hardware Required)

```bash
python main.py
```

#### Real Robot Mode

```bash
export ROBOT=booster-t1
python main.py
```

The server will start at `http://localhost:8000`

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Web Client**: Open `client.html` in your browser

## 📚 API Overview

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check status |
| `/status` | GET | Get robot status (type and busy state) |
| `/commands` | GET | List all available commands |

### Movement Commands

| Endpoint | Method | Description | Speed |
|----------|--------|-------------|-------|
| `/move-forward` | POST | Move forward for 1 second | 0.5 m/s |
| `/move-backward` | POST | Move backward for 1 second | 0.2 m/s |
| `/turn-left` | POST | Rotate left for 1 second | 0.2 rad/s |
| `/turn-right` | POST | Rotate right for 1 second | 0.2 rad/s |

### Hand Gesture Commands

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/wave-hand` | POST | Wave hand with configurable duration |
| `/cancel-wave-hand` | POST | Immediately cancel wave gesture |

### Example Usage

#### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get robot status
curl http://localhost:8000/status

# Move forward
curl -X POST http://localhost:8000/move-forward

# Wave hand for 2 seconds
curl -X POST http://localhost:8000/wave-hand \
  -H "Content-Type: application/json" \
  -d '{"duration": 2.0}'
```

#### Using Python

```python
import requests

# Move forward
response = requests.post("http://localhost:8000/move-forward")
print(response.json())

# Wave hand
response = requests.post(
    "http://localhost:8000/wave-hand",
    json={"duration": 2.0}
)
print(response.json())
```

#### Using the Web Client

1. Open `client.html` in your web browser
2. Configure the server URL (default: `http://localhost:8000`)
3. Click buttons to send commands to the robot
4. Monitor connection status and command feedback in real-time

## 🏗️ Project Structure

```
booster-platform/
├── booster-command-server/          # Main command server
│   ├── main.py                      # FastAPI application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── client.html                  # Web-based control interface
│   ├── robot_commander/             # Robot commander modules
│   │   ├── __init__.py             # Base commander interface and factory
│   │   └── booster_t1_robot.py     # Booster T1 robot implementation
│   ├── scripts/                     # Deployment and utility scripts
│   │   ├── install-systemd.sh      # SystemD service installation
│   │   ├── uninstall-systemd.sh    # SystemD service removal
│   │   ├── start_server.sh         # Manual server start script
│   │   ├── stop_server.sh          # Manual server stop script
│   │   ├── booster-command-server.service  # SystemD service file
│   │   └── README.md               # Scripts documentation
│   ├── README.md                   # Server-specific documentation
│   ├── CLIENT_README.md            # Web client documentation
│   └── SYSTEMD_DEPLOYMENT.md       # SystemD deployment guide
├── LICENSE                         # MIT License
└── README.md                       # This file
```

## 🔧 Production Deployment

### SystemD Service (Ubuntu)

For production deployment with automatic startup, system logging, and service management:

```bash
cd booster-command-server
sudo ./scripts/install-systemd.sh
```

This installs the server as a systemd service with:
- Automatic startup on boot
- Automatic restart on failure
- Dedicated service user (`booster`)
- Centralized logging to `/var/log/booster-command-server/`
- Security hardening features

#### Service Management

```bash
# Check status
sudo systemctl status booster-command-server

# Start/stop/restart
sudo systemctl start booster-command-server
sudo systemctl stop booster-command-server
sudo systemctl restart booster-command-server

# View logs
sudo journalctl -u booster-command-server -f
```

See [SYSTEMD_DEPLOYMENT.md](booster-command-server/SYSTEMD_DEPLOYMENT.md) for detailed instructions.

## 🛠️ Development

### Running in Development Mode

```bash
# With auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `ROBOT` | `mock` (default), `booster-t1` | Robot commander mode |

### Mock vs Real Robot Mode

#### Mock Mode (Default)
- No hardware required
- Simulates robot commands with logging
- Perfect for testing and development
- Automatically selected if `ROBOT` env var not set

#### Real Robot Mode
- Requires Booster T1 robot hardware
- Requires Booster Robotics SDK installed
- Set `ROBOT=booster-t1` environment variable
- Network interface must be configured correctly

### Adding New Commands

1. **Define the command in `RobotCommander` interface** (`robot_commander/__init__.py`):
```python
@abstractmethod
async def your_command(self, parameters: dict = {}):
    pass
```

2. **Implement in both commanders** (`MockRobotCommander` and `BoosterT1Commander`)

3. **Add API endpoint in `main.py`**:
```python
@app.post("/your-command")
async def your_command(
    robot_cmd: Annotated[RobotCommander, Depends(robot_commander)],
):
    await robot_cmd.your_command(parameters={})
    return CommandResponse(
        success=True,
        message="Your command executed",
        data=None
    )
```

## 📖 Documentation

- **[Server README](booster-command-server/README.md)**: Detailed server documentation
- **[Web Client Guide](booster-command-server/CLIENT_README.md)**: Web client usage guide
- **[SystemD Deployment](booster-command-server/SYSTEMD_DEPLOYMENT.md)**: Production deployment guide
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when server is running)

## 🤖 Robot Specifications

### Booster T1 Humanoid Robot

- **Locomotion**: Forward/backward movement and rotation
- **Hand Control**: Wave gestures with open/close actions
- **Movement Speeds**:
  - Forward: 0.5 m/s
  - Backward: 0.2 m/s (slower for safety)
  - Rotation: 0.2 rad/s (~11.5 degrees per second)
- **Command Duration**: All movement commands execute for 1 second by default
- **Safety**: Automatic stop after command completion

### Command Queue System

- Commands are processed one at a time
- Queue size: 1 (can hold one pending command)
- If queue is full, additional commands are skipped
- `cancel-wave-hand` executes immediately (bypass queue)

## 🔐 Security Notes

### Development vs Production

The default CORS configuration allows all origins:
```python
allow_origins=["*"]  # Development mode
```

For production, restrict to specific origins:
```python
allow_origins=["https://yourdomain.com"]  # Production
```

### SystemD Security Features

When deployed as a systemd service, security hardening includes:
- Non-privileged service user
- No new privileges allowed
- Private temporary directories
- Protected system directories
- Read-only system paths
- Isolated home directory

## 🧪 Testing

### Test Without Hardware

Run in mock mode to test the API without robot hardware:

```bash
python main.py
# Server starts in mock mode by default
```

### Test with curl

```bash
# Health check
curl http://localhost:8000/health

# List available commands
curl http://localhost:8000/commands

# Test movement command
curl -X POST http://localhost:8000/move-forward

# Test hand gesture
curl -X POST http://localhost:8000/wave-hand \
  -H "Content-Type: application/json" \
  -d '{"duration": 1.5}'
```

### Test with Web Client

1. Open `booster-command-server/client.html`
2. Verify connection status shows green
3. Click command buttons
4. Observe success/error notifications

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Add docstrings for new functions and classes
- Update documentation when adding features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Thinkin' Rocks Oy

## 📧 Support

- **Documentation**: See `/docs` endpoint when server is running
- **Issues**: https://github.com/thinkinrocks/booster-platform/issues
- **Contact**: See project repository for contact information

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Uvicorn](https://www.uvicorn.org/)
- Booster Robotics SDK for robot control

## 🗺️ Roadmap

### Planned Features
- [ ] WebSocket support for real-time robot state streaming
- [ ] Authentication and authorization
- [ ] Multi-robot support
- [ ] Command history and logging
- [ ] Telemetry and metrics endpoint
- [ ] Video streaming integration
- [ ] Advanced movement patterns and choreography
- [ ] Voice command integration
- [ ] Mobile app client

## 📊 Version History

### v1.0.0 (Current)
- Initial release
- Basic movement commands (forward, backward, turn left/right)
- Hand gesture control (wave hand)
- Command queueing system
- Mock and real robot modes
- FastAPI REST API
- Web client interface
- SystemD service deployment
- Comprehensive documentation

---

Made with ❤️ by Thinkin' Rocks Oy

