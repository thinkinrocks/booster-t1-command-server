#!/bin/bash

# Script to start the Booster Command Server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/server.pid"
LOG_FILE="$SCRIPT_DIR/server.log"

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Server is already running with PID $PID"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Start the server in the background
echo "Starting Booster Command Server..."
nohup python3 main.py > "$LOG_FILE" 2>&1 &

# Save the PID
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Give it a moment to start
sleep 2

# Check if the process is still running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "Server started successfully with PID $SERVER_PID"
    echo "Logs are being written to: $LOG_FILE"
    echo "To stop the server, run: ./stop_server.sh"
else
    echo "Failed to start server. Check $LOG_FILE for errors"
    rm "$PID_FILE"
    exit 1
fi

