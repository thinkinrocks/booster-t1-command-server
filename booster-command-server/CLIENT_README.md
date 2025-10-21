# Booster Platform HTTP Client

A simple, modern HTML client for controlling the Booster robot's hand movements.

## Features

- 🎨 **Modern UI**: Clean, gradient-based design with smooth animations
- ⚙️ **Configurable Backend**: Easy server URL configuration
- 🔄 **Real-time Status**: Live connection status and command feedback
- 📱 **Responsive**: Works on desktop and mobile devices
- ✨ **User-friendly**: Clear visual feedback for all actions

## Quick Start

### 1. Start the Server

First, make sure your Booster command server is running:

```bash
cd /home/yerzhan/projects/thinkinrocks/booster-platform/booster-command-server
python main.py
```

The server will start on `http://localhost:8000` by default.

### 2. Open the Client

Simply open `client.html` in your web browser:

```bash
# Option 1: Open directly
xdg-open client.html

# Option 2: Serve with Python's built-in server
python -m http.server 8080
# Then visit http://localhost:8080/client.html
```

### 3. Configure the Server URL

1. In the "Server Configuration" section, enter your server URL
2. Default is `http://localhost:8000`
3. For remote servers, use the appropriate IP/hostname (e.g., `http://192.168.1.100:8000`)

### 4. Control the Robot

- Click **"👋 Wave Hand"** to send a wave hand command
- Click **"✋ Cancel Wave Hand"** to cancel the wave hand action

## Features in Detail

### Connection Status

The client automatically checks the server connection:
- ✓ **Green**: Connected to server
- ✗ **Red**: Cannot connect to server
- Auto-checks every 5 seconds

### Command Feedback

When you send a command:
- **Loading state**: Shows a spinner while processing
- **Success**: Green notification with success message
- **Error**: Red notification with error details
- Auto-dismisses after 3 seconds on success

### Server Configuration

The server URL is configurable in real-time:
- Change the URL without reloading the page
- Supports any HTTP/HTTPS endpoint
- Connection status updates automatically

## Troubleshooting

### "Cannot connect to server"

1. Verify the server is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check the server URL is correct in the client

3. Ensure CORS is enabled (already configured in the server)

### Commands not working

1. Check the server logs for errors
2. Verify the robot client is properly initialized
3. Ensure the network interface is configured correctly

## Technical Details

### API Endpoints Used

- `GET /health` - Health check for connection status
- `POST /command` - Send commands to the robot

### Command Format

The client sends commands in this format:

```json
{
  "command": "wave-hand",
  "parameters": {}
}
```

## Customization

You can customize the client by editing `client.html`:

- **Colors**: Modify the gradient colors in the `<style>` section
- **Server URL**: Change the default value in the input field
- **Polling Interval**: Adjust the `setInterval` value (currently 5000ms)

## Browser Compatibility

Works with all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

## Security Notes

The current CORS configuration (`allow_origins=["*"]`) is suitable for development but should be restricted in production:

```python
# Production example
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

