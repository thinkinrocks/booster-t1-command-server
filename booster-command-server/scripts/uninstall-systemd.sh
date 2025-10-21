#!/bin/bash

# Uninstallation script for Booster Command Server systemd service
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

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: This script must be run with sudo privileges${NC}"
    echo "Usage: sudo ./uninstall-systemd.sh"
    exit 1
fi

echo -e "${YELLOW}=== Booster Command Server SystemD Uninstallation ===${NC}\n"

# Confirm uninstallation
read -p "Are you sure you want to uninstall the Booster Command Server? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Uninstallation cancelled${NC}"
    exit 0
fi

# Step 1: Stop and disable service
echo -e "${YELLOW}[1/6] Stopping and disabling service...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    systemctl stop $SERVICE_NAME
    echo -e "${GREEN}✓ Service stopped${NC}"
fi

if systemctl is-enabled --quiet $SERVICE_NAME; then
    systemctl disable $SERVICE_NAME
    echo -e "${GREEN}✓ Service disabled${NC}"
fi

# Step 2: Remove systemd service file
echo -e "${YELLOW}[2/6] Removing systemd service file...${NC}"
if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    rm /etc/systemd/system/${SERVICE_NAME}.service
    systemctl daemon-reload
    echo -e "${GREEN}✓ Service file removed${NC}"
fi

# Step 3: Remove installation directory
echo -e "${YELLOW}[3/6] Removing installation directory...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓ Installation directory removed: $INSTALL_DIR${NC}"
fi

# Step 4: Remove log directory
echo -e "${YELLOW}[4/6] Removing log directory...${NC}"
read -p "Do you want to remove logs at $LOG_DIR? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$LOG_DIR" ]; then
        rm -rf "$LOG_DIR"
        echo -e "${GREEN}✓ Log directory removed: $LOG_DIR${NC}"
    fi
else
    echo -e "${YELLOW}✓ Log directory preserved: $LOG_DIR${NC}"
fi

# Step 5: Remove service user
echo -e "${YELLOW}[5/6] Removing service user...${NC}"
read -p "Do you want to remove the service user '$SERVICE_USER'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if id -u $SERVICE_USER > /dev/null 2>&1; then
        userdel $SERVICE_USER
        echo -e "${GREEN}✓ Service user removed: $SERVICE_USER${NC}"
    fi
else
    echo -e "${YELLOW}✓ Service user preserved: $SERVICE_USER${NC}"
fi

# Step 6: Complete
echo -e "${YELLOW}[6/6] Cleaning up...${NC}"
systemctl reset-failed
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo -e "\n${GREEN}=== Uninstallation Complete ===${NC}\n"
echo -e "${YELLOW}The Booster Command Server has been uninstalled${NC}"
echo ""

