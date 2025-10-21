#!/bin/bash

# Script to stop the Booster Command Server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/server.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "No PID file found. Server may not be running."
    exit 1
fi

# Read the PID
PID=$(cat "$PID_FILE")

# Check if the process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "Process with PID $PID is not running"
    rm "$PID_FILE"
    exit 1
fi

# Kill the process
echo "Stopping server with PID $PID..."
kill $PID

# Wait for the process to stop (max 10 seconds)
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Server stopped successfully"
        rm "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# If still running, force kill
echo "Server did not stop gracefully, forcing kill..."
kill -9 $PID

# Check again
if ! ps -p $PID > /dev/null 2>&1; then
    echo "Server force stopped"
    rm "$PID_FILE"
    exit 0
else
    echo "Failed to stop server"
    exit 1
fi

