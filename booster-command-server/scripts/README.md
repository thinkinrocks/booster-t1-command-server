# Scripts Directory

This directory contains various scripts for managing the Booster Command Server.

## Scripts

### SystemD Deployment (Production)

- **`install-systemd.sh`** - Installs the server as a systemd service on Ubuntu
  - Creates a dedicated service user
  - Installs to `/opt/booster-command-server`
  - Enables automatic startup on boot
  - Usage: `sudo ./scripts/install-systemd.sh`
  - See [SYSTEMD_DEPLOYMENT.md](../SYSTEMD_DEPLOYMENT.md) for details

- **`uninstall-systemd.sh`** - Uninstalls the systemd service
  - Stops and disables the service
  - Removes installation directory
  - Optionally removes logs and service user
  - Usage: `sudo ./scripts/uninstall-systemd.sh`

- **`booster-command-server.service`** - SystemD service configuration file
  - Used by the installation script
  - Defines service behavior and security settings

### Development Scripts

- **`start_server.sh`** - Starts the server in development mode
  - Runs the server in the background using nohup
  - Creates a PID file for process management
  - Logs to `server.log` in the project directory
  - Usage: `./scripts/start_server.sh`

- **`stop_server.sh`** - Stops the development server
  - Gracefully stops the server started with `start_server.sh`
  - Attempts graceful shutdown, then force-kills if necessary
  - Removes PID file
  - Usage: `./scripts/stop_server.sh`

## Usage

### For Production (SystemD)

1. Install the service:
   ```bash
   cd booster-command-server
   sudo ./scripts/install-systemd.sh
   ```

2. Manage the service:
   ```bash
   sudo systemctl start booster-command-server
   sudo systemctl stop booster-command-server
   sudo systemctl status booster-command-server
   ```

### For Development

1. Start the server:
   ```bash
   cd booster-command-server
   ./scripts/start_server.sh
   ```

2. Stop the server:
   ```bash
   ./scripts/stop_server.sh
   ```

## File Permissions

All scripts should be executable. To make them executable:
```bash
chmod +x scripts/*.sh
```

