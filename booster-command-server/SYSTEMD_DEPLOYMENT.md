# SystemD Deployment Guide

This guide explains how to deploy the Booster Command Server as a systemd service on Ubuntu.

## Prerequisites

- Ubuntu 18.04 or later
- Python 3.7 or later
- sudo/root access
- Internet connection (for installing dependencies)

## Quick Installation

1. Navigate to the `booster-command-server` directory:
   ```bash
   cd booster-command-server
   ```

2. Run the installation script:
   ```bash
   sudo ./scripts/install-systemd.sh
   ```

The script will:
- Create a dedicated service user (`booster`)
- Install the application to `/opt/booster-command-server`
- Set up a Python virtual environment (with access to system packages)
- Install all dependencies
- Create log directory at `/var/log/booster-command-server`
- Install and start the systemd service
- Enable the service to start on boot

**Note:** The virtual environment is created with `--system-site-packages`, allowing it to use Python packages installed system-wide (e.g., via `apt` or `pip` as root). This is useful if you have dependencies like the Booster SDK installed globally.

## Verification

After installation, verify the service is running:

```bash
# Check service status
sudo systemctl status booster-command-server

# Test the API
curl http://localhost:8000/health

# View API documentation
# Open in browser: http://localhost:8000/docs
```

## Service Management

### Start/Stop/Restart

```bash
# Start the service
sudo systemctl start booster-command-server

# Stop the service
sudo systemctl stop booster-command-server

# Restart the service
sudo systemctl restart booster-command-server

# Reload service configuration (after editing service file)
sudo systemctl daemon-reload
sudo systemctl restart booster-command-server
```

### Enable/Disable Auto-start

```bash
# Enable service to start on boot (done automatically by install script)
sudo systemctl enable booster-command-server

# Disable auto-start on boot
sudo systemctl disable booster-command-server
```

### View Status and Logs

```bash
# Check service status
sudo systemctl status booster-command-server

# View recent logs (systemd journal)
sudo journalctl -u booster-command-server

# Follow logs in real-time
sudo journalctl -u booster-command-server -f

# View logs from the last hour
sudo journalctl -u booster-command-server --since "1 hour ago"

# View application log file directly
sudo tail -f /var/log/booster-command-server/server.log
```

## Configuration

### Environment Variables

The service configuration is stored in `/etc/systemd/system/booster-command-server.service`.

To change environment variables:

1. Edit the service file:
   ```bash
   sudo nano /etc/systemd/system/booster-command-server.service
   ```

2. Modify the `Environment` lines. For example, to use the actual booster-t1 robot:
   ```ini
   Environment="ROBOT=booster-t1"
   ```

3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart booster-command-server
   ```

### Change Port

To change the port from 8000 to another port:

1. Edit the service file:
   ```bash
   sudo nano /etc/systemd/system/booster-command-server.service
   ```

2. Modify the `ExecStart` line:
   ```ini
   ExecStart=/opt/booster-command-server/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080
   ```

3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart booster-command-server
   ```

### Update Application Code

To update the application code after making changes:

1. Stop the service:
   ```bash
   sudo systemctl stop booster-command-server
   ```

2. Copy updated files to the installation directory:
   ```bash
   sudo cp -r /path/to/your/updated/files/* /opt/booster-command-server/
   ```

3. If dependencies changed, update them:
   ```bash
   cd /opt/booster-command-server
   sudo -u booster venv/bin/pip install -r requirements.txt
   ```

4. Set correct permissions:
   ```bash
   sudo chown -R booster:booster /opt/booster-command-server
   ```

5. Start the service:
   ```bash
   sudo systemctl start booster-command-server
   ```

## Uninstallation

To completely remove the service:

```bash
cd booster-command-server
sudo ./scripts/uninstall-systemd.sh
```

The uninstall script will:
- Stop and disable the service
- Remove the systemd service file
- Remove the installation directory
- Optionally remove logs
- Optionally remove the service user

## File Locations

| Item | Location |
|------|----------|
| Application | `/opt/booster-command-server/` |
| Service File | `/etc/systemd/system/booster-command-server.service` |
| Logs | `/var/log/booster-command-server/server.log` |
| Virtual Environment | `/opt/booster-command-server/venv/` |
| Service User | `booster` (system user) |

## Troubleshooting

### Service won't start

1. Check the service status for errors:
   ```bash
   sudo systemctl status booster-command-server
   ```

2. View detailed logs:
   ```bash
   sudo journalctl -u booster-command-server -n 50
   ```

3. Check for permission issues:
   ```bash
   sudo ls -la /opt/booster-command-server
   sudo ls -la /var/log/booster-command-server
   ```

### Port already in use

If port 8000 is already in use:

1. Check what's using the port:
   ```bash
   sudo lsof -i :8000
   ```

2. Either stop the conflicting service or change the port (see Configuration section above)

### Permission denied errors

Ensure correct ownership:
```bash
sudo chown -R booster:booster /opt/booster-command-server
sudo chown -R booster:booster /var/log/booster-command-server
```

### Python dependencies missing

Reinstall dependencies:
```bash
cd /opt/booster-command-server
sudo -u booster venv/bin/pip install -r requirements.txt
```

### Using System-Wide Python Packages

The virtual environment is configured with `--system-site-packages`, which means it can access packages installed system-wide. This is useful for packages like the Booster SDK that may be installed globally.

To install packages system-wide that the service can use:
```bash
# Install as root/sudo
sudo pip3 install package-name

# Or using apt for system packages
sudo apt install python3-package-name
```

To verify which packages are available to the service:
```bash
sudo -u booster /opt/booster-command-server/venv/bin/pip list
```

Packages installed in the venv will take precedence over system packages if there are version conflicts.

## Security Considerations

The systemd service includes several security hardening options:

- **NoNewPrivileges**: Prevents privilege escalation
- **PrivateTmp**: Provides isolated temporary directory
- **ProtectSystem**: Makes system directories read-only
- **ProtectHome**: Makes home directories inaccessible
- **ReadWritePaths**: Only allows writing to log directory

The service runs as a dedicated non-privileged user (`booster`) with no login shell.

## Network Access

By default, the server listens on all interfaces (`0.0.0.0:8000`). To restrict to localhost only:

1. Edit the service file:
   ```bash
   sudo nano /etc/systemd/system/booster-command-server.service
   ```

2. Change the `ExecStart` line:
   ```ini
   ExecStart=/opt/booster-command-server/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
   ```

3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart booster-command-server
   ```

## Firewall Configuration

If you have UFW (Uncomplicated Firewall) enabled and need external access:

```bash
# Allow access to port 8000
sudo ufw allow 8000/tcp

# Or allow only from specific IP
sudo ufw allow from 192.168.1.100 to any port 8000

# Check firewall status
sudo ufw status
```

## Additional Resources

- [SystemD Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)

