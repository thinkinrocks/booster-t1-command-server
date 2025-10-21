#!/bin/bash

# Installation script for Booster Command Server as a systemd service
# This script must be run with sudo privileges

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="booster-command-server"
INSTALL_DIR="/opt/${SERVICE_NAME}"
LOG_DIR="/var/log/${SERVICE_NAME}"
SERVICE_USER="booster"
SERVICE_GROUP="booster"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: This script must be run with sudo privileges${NC}"
    echo "Usage: sudo ./install-systemd.sh"
    exit 1
fi

echo -e "${GREEN}=== Booster Command Server SystemD Installation ===${NC}\n"

# Step 1: Create service user and group if they don't exist
echo -e "${YELLOW}[1/8] Creating service user and group...${NC}"
if ! id -u $SERVICE_USER > /dev/null 2>&1; then
    useradd --system --no-create-home --shell /bin/false $SERVICE_USER
    echo -e "${GREEN}✓ Created user: $SERVICE_USER${NC}"
else
    echo -e "${GREEN}✓ User $SERVICE_USER already exists${NC}"
fi

# Step 2: Create installation directory
echo -e "${YELLOW}[2/8] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓ Created directory: $INSTALL_DIR${NC}"

# Step 3: Copy application files
echo -e "${YELLOW}[3/8] Copying application files...${NC}"
cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/"
# Remove scripts directory from install directory (we only need the service file)
rm -rf "$INSTALL_DIR/scripts"
echo -e "${GREEN}✓ Copied application files${NC}"

# Step 4: Create and activate virtual environment
echo -e "${YELLOW}[4/8] Setting up Python virtual environment...${NC}"
cd "$INSTALL_DIR"
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"

# Step 5: Create log directory
echo -e "${YELLOW}[5/8] Creating log directory...${NC}"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Created log directory: $LOG_DIR${NC}"

# Step 6: Set permissions
echo -e "${YELLOW}[6/8] Setting permissions...${NC}"
chown -R $SERVICE_USER:$SERVICE_GROUP "$INSTALL_DIR"
chown -R $SERVICE_USER:$SERVICE_GROUP "$LOG_DIR"
chmod 755 "$INSTALL_DIR"
echo -e "${GREEN}✓ Permissions set${NC}"

# Step 7: Install systemd service
echo -e "${YELLOW}[7/8] Installing systemd service...${NC}"
cp "$SCRIPT_DIR/${SERVICE_NAME}.service" /etc/systemd/system/
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd service installed${NC}"

# Step 8: Enable and start service
echo -e "${YELLOW}[8/8] Enabling and starting service...${NC}"
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Wait a moment for service to start
sleep 2

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✓ Service started successfully${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo -e "${YELLOW}Check status with: sudo systemctl status $SERVICE_NAME${NC}"
    exit 1
fi

echo -e "\n${GREEN}=== Installation Complete ===${NC}\n"
echo -e "Service Name: ${GREEN}${SERVICE_NAME}${NC}"
echo -e "Install Directory: ${GREEN}${INSTALL_DIR}${NC}"
echo -e "Log Directory: ${GREEN}${LOG_DIR}${NC}"
echo -e "Service User: ${GREEN}${SERVICE_USER}${NC}"
echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "  Check status:   ${GREEN}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "  Start service:  ${GREEN}sudo systemctl start ${SERVICE_NAME}${NC}"
echo -e "  Stop service:   ${GREEN}sudo systemctl stop ${SERVICE_NAME}${NC}"
echo -e "  Restart:        ${GREEN}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "  View logs:      ${GREEN}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo -e "  View log file:  ${GREEN}sudo tail -f ${LOG_DIR}/server.log${NC}"
echo -e "\n${YELLOW}API Endpoints:${NC}"
echo -e "  Base URL:       ${GREEN}http://localhost:8000${NC}"
echo -e "  Health Check:   ${GREEN}http://localhost:8000/health${NC}"
echo -e "  API Docs:       ${GREEN}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Configuration:${NC}"
echo -e "  To use booster-t1 robot instead of mock, edit:"
echo -e "  ${GREEN}/etc/systemd/system/${SERVICE_NAME}.service${NC}"
echo -e "  Change: ${GREEN}Environment=\"ROBOT=mock\"${NC} to ${GREEN}Environment=\"ROBOT=booster-t1\"${NC}"
echo -e "  Then run: ${GREEN}sudo systemctl daemon-reload && sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "\n${YELLOW}To uninstall:${NC}"
echo -e "  Run: ${GREEN}sudo ${SCRIPT_DIR}/uninstall-systemd.sh${NC}"
echo ""

