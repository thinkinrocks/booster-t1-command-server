# Booster T1 Command Server

A FastAPI-based command server for controlling the Booster T1 humanoid robot.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)

## Overview

This server provides RESTful endpoints for robot movement control, hand gestures, and status monitoring. It supports both mock mode for development and testing, as well as real robot control via the Booster Robotics SDK.

## Features

- Movement commands (forward, backward, turn left/right)
- Hand gesture control with configurable duration
- Command queueing system
- Real-time status monitoring
- Mock mode for development without hardware
- SystemD service support for production deployment
- Interactive API documentation (Swagger UI)

## Requirements

- Python 3.7 or later
- Ubuntu 18.04+ (for systemd deployment)
- Booster Robotics SDK (for real robot control)

### Dependencies

- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- Python-multipart 0.0.6

## Installation

Clone the repository:

```bash
git clone https://github.com/thinkinrocks/booster-platform.git
cd booster-platform/booster-command-server
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Development Mode

Run in mock mode (no hardware required):

```bash
python main.py
```

Run with real robot:

```bash
export ROBOT=booster-t1
python main.py
```

The server will start at `http://localhost:8000`

### API Documentation

Interactive documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `ROBOT` | `mock`, `booster-t1` | Robot commander mode (default: `mock`) |

## API Endpoints

### Status Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/status` | GET | Robot status |
| `/commands` | GET | List available commands |

### Movement Commands

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/move-forward` | POST | Move forward for 1 second |
| `/move-backward` | POST | Move backward for 1 second |
| `/turn-left` | POST | Rotate left for 1 second |
| `/turn-right` | POST | Rotate right for 1 second |

### Hand Gestures

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/wave-hand` | POST | Wave hand with configurable duration |
| `/cancel-wave-hand` | POST | Cancel wave gesture |

### Example Requests

Health check:
```bash
curl http://localhost:8000/health
```

Move forward:
```bash
curl -X POST http://localhost:8000/move-forward
```

Wave hand for 2 seconds:
```bash
curl -X POST http://localhost:8000/wave-hand \
  -H "Content-Type: application/json" \
  -d '{"duration": 2.0}'
```

## Production Deployment

### SystemD Service

Install as a systemd service on Ubuntu:

```bash
cd booster-command-server
sudo ./scripts/install-systemd.sh
```

The service will be configured with:
- Automatic startup on boot
- Automatic restart on failure
- Dedicated service user
- Centralized logging at `/var/log/booster-command-server/`

Service management:

```bash
sudo systemctl status booster-command-server
sudo systemctl start booster-command-server
sudo systemctl stop booster-command-server
sudo systemctl restart booster-command-server
sudo journalctl -u booster-command-server -f
```

See [SYSTEMD_DEPLOYMENT.md](booster-command-server/SYSTEMD_DEPLOYMENT.md) for detailed deployment instructions.

## Project Structure

```
booster-platform/
├── booster-command-server/
│   ├── main.py
│   ├── requirements.txt
│   ├── client.html
│   ├── robot_commander/
│   │   ├── __init__.py
│   │   └── booster_t1_robot.py
│   ├── scripts/
│   │   ├── install-systemd.sh
│   │   ├── uninstall-systemd.sh
│   │   ├── start_server.sh
│   │   ├── stop_server.sh
│   │   └── booster-command-server.service
│   ├── README.md
│   ├── CLIENT_README.md
│   └── SYSTEMD_DEPLOYMENT.md
├── LICENSE
└── README.md
```

## Robot Specifications

The Booster T1 humanoid robot supports:
- Forward/backward movement and rotation
- Hand gestures (wave with open/close actions)
- Command duration: 1 second per movement command
- Automatic stop after command completion

### Command Queue

- Commands are processed sequentially
- Queue size: 1 pending command maximum
- Additional commands are skipped when queue is full
- `cancel-wave-hand` executes immediately without queueing

## Testing

Run in mock mode to test without hardware:

```bash
python main.py
```

Test commands:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/commands
curl -X POST http://localhost:8000/move-forward
curl -X POST http://localhost:8000/wave-hand \
  -H "Content-Type: application/json" \
  -d '{"duration": 1.5}'
```

## Documentation

- [Server Documentation](booster-command-server/README.md)
- [Web Client Guide](booster-command-server/CLIENT_README.md)
- [SystemD Deployment Guide](booster-command-server/SYSTEMD_DEPLOYMENT.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.
