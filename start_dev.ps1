# PowerShell script to launch both Lyrixa backend and Aetherra GUI frontend for development
# Starts backend first, then frontend, and opens the browser

# Start the Lyrixa backend (WebSocket server) in a new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd "Aetherra/memory"; py -m Aetherra.memory.quantum_web_dashboard'

Start-Sleep -Seconds 3  # Give backend time to start

# Start the React/Vite frontend in a new window
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd frontend; npm run dev'

Start-Sleep -Seconds 2

# Open the GUI in the default browser
Start-Process "http://localhost:3000/"
