# 🚀 Lyrixa GUI - Startup Guide

## Quick Start (Development Mode)

### Prerequisites
- Python 3.11+ with Aetherra dependencies installed
- Node.js 18+ with npm
- Frontend dependencies installed (`npm install` in this directory)

### Step 1: Start the Backend (Hub AI API)

**Option A: Using VS Code Task (Recommended)**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Run Task"
3. Select: **"Run Hub (AI API 3012)"**

**Option B: Using Terminal**
```powershell
# From workspace root (d:\Aetherra Project)
python tools/run_hub_ai_api.py --port 3012
```

**Expected Output:**
```
[OK] Hub with AI API on http://127.0.0.1:3012
AI API enabled: AETHERRA_AI_API_ENABLED=1 AETHERRA_AI_API_STREAM=1
```

The backend will be running on `http://localhost:3012` and provide these endpoints:
- `/health` - Health check
- `/api/kernel/status` - Kernel status
- `/api/kernel/metrics` - Kernel metrics
- `/api/agents` - Agent list
- `/api/memory/status` - Memory status
- `/api/homeostasis/status` - Homeostasis status
- `/api/run` - Execute .aether scripts
- And many more...

### Step 2: Start the Frontend (Vite Dev Server)

**Using Terminal:**
```powershell
# Navigate to GUI directory
cd Aetherra\lyrixa\gui

# Start Vite dev server
npm run dev
```

**Expected Output:**
```
VITE v5.0.0  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### Step 3: Verify Connectivity

1. **Check Backend Health:**
   ```powershell
   curl http://localhost:3012/health
   ```
   Expected: `{"status": "healthy"}` or similar

2. **Open Frontend:**
   - Navigate to: `http://localhost:3000`
   - The Lyrixa GUI should load with the holographic interface

3. **Test All Panels:**
   Navigate through each panel and verify data loads:
   - ✅ **Dashboard** - System status, subsystem health, activity feed
   - ✅ **Kernel** - Kernel metrics, task queue
   - ✅ **Agents** - Active agents list
   - ✅ **Memory** - Memory metrics, event audit
   - ✅ **Maintenance** - Scheduled tasks, logs
   - ✅ **Homeostasis** - Homeostasis status and metrics
   - ✅ **Security** - Alerts, policy configuration
   - ✅ **.aether Scripts** - Script library and execution
   - ✅ **Settings** - All 5 configuration tabs
   - ✅ **Network** - (if implemented)
   - ✅ **Audit** - (if implemented)

### Step 4: Monitor Console

**Backend Console:**
- Should show incoming API requests as you navigate the GUI
- Example: `GET /api/kernel/status` returns `200 OK`

**Browser Console (F12):**
- Should show no errors
- Check Network tab for successful API calls (all should return 200/201)

---

## Configuration

### Port Configuration

**Current Setup:**
- **Frontend:** `http://localhost:3000` (Vite dev server)
- **Backend:** `http://localhost:3012` (Hub AI API)
- **Proxy:** Vite proxies `/api/*` → `http://localhost:3012`

**Why Port 3012?**
The Vite proxy in `vite.config.ts` is hardcoded to port 3012:
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:3012',
      changeOrigin: true,
    },
  },
}
```

**To Change Ports:**
1. Update `vite.config.ts` → `server.proxy['/api'].target`
2. Update `App.tsx` → `settingsConfig.api.backendUrl` (default value)
3. Start backend with new port: `python tools/run_hub_ai_api.py --port YOUR_PORT`

### Settings Panel

The Settings panel in the GUI allows runtime configuration:
- **API Settings:** Backend URL, timeout, retry attempts, CORS
- **Appearance:** Theme, accent color, font size, animations
- **Notifications:** Enable/disable, sound, duration, filters
- **Performance:** Poll interval, caching, data retention
- **Developer:** Debug mode, trace, verbose logging, mock data

All settings are persisted to `localStorage`.

---

## Troubleshooting

### Backend Won't Start

**Error:** `Address already in use`
- **Cause:** Port 3012 is already in use
- **Solution:**
  ```powershell
  # Find process using port 3012
  netstat -ano | findstr :3012

  # Kill the process (replace PID with actual process ID)
  taskkill /PID <PID> /F
  ```

**Error:** `ModuleNotFoundError: No module named 'aetherra_hub'`
- **Cause:** Aetherra dependencies not installed
- **Solution:** Install dependencies from workspace root:
  ```powershell
  pip install -e .
  ```

### Frontend Won't Start

**Error:** `Cannot find module 'vite'`
- **Cause:** Dependencies not installed
- **Solution:**
  ```powershell
  npm install
  ```

**Error:** `Port 3000 is already in use`
- **Cause:** Another process is using port 3000
- **Solution:** Kill the process or use a different port:
  ```powershell
  npm run dev -- --port 3001
  ```

### API Requests Failing

**Symptom:** Red toast notifications, "Failed to fetch" errors in console

**Check 1: Backend Running?**
```powershell
curl http://localhost:3012/health
```
If this fails, backend is not running.

**Check 2: CORS Issues?**
- Vite proxy should handle this automatically
- Check browser console for CORS errors
- Verify `vite.config.ts` proxy has `changeOrigin: true`

**Check 3: Incorrect Port?**
- Frontend expects backend on 3012 (via Vite proxy)
- Verify backend started on port 3012
- Check Settings panel → API → Backend URL matches

### No Data in Panels

**Symptom:** Panels load but show "No data" or empty states

**Possible Causes:**
1. **Backend endpoints not implemented yet** - Some endpoints may return mock data or 404
2. **Aetherra OS not running** - Hub needs the OS components (Kernel, Memory, etc.) running
3. **API polling disabled** - Check Settings → Performance → Poll Interval

**Solution:**
- For full functionality, start the complete Aetherra OS first:
  ```powershell
  python aetherra_os_launcher.py --mode full -v
  ```
- Then start Hub and Frontend

---

## Production Build

### Build for Production

```powershell
# From Aetherra/lyrixa/gui
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```powershell
npm run preview
```

Serves the production build on `http://localhost:4173`.

---

## Development Workflow

### Hot Module Replacement (HMR)

Vite provides instant HMR:
1. Edit `src/App.tsx` or any component
2. Save the file
3. Browser updates instantly without full reload
4. State is preserved (React Fast Refresh)

### API Polling

The GUI uses `useApiPoll` hook for live data:
- Default interval: 5 seconds (configurable in Settings)
- Automatically stops when panel is not visible
- Resumes when panel becomes active

### State Management

- All state is in `App.tsx` using `useState` hooks
- Settings persist to `localStorage`
- No external state management (Redux, Zustand, etc.)

### Icon Library

Uses **Lucide React** for all icons:
```typescript
import { Home, Settings, Shield } from 'lucide-react';
```

Browse available icons: https://lucide.dev/icons

---

## API Endpoints Reference

### Core Endpoints (Used by GUI)

| Endpoint                             | Method | Description             | Panel                  |
| ------------------------------------ | ------ | ----------------------- | ---------------------- |
| `/health`                            | GET    | Health check            | All (connection test)  |
| `/api/kernel/status`                 | GET    | Kernel status           | Dashboard, Kernel      |
| `/api/kernel/metrics`                | GET    | Kernel metrics          | Dashboard, Kernel      |
| `/api/agents`                        | GET    | List active agents      | Agents                 |
| `/api/memory/status`                 | GET    | Memory status           | Memory                 |
| `/api/memory/audit`                  | GET    | Memory event audit      | Memory                 |
| `/api/maintenance/status`            | GET    | Maintenance status      | Maintenance            |
| `/api/homeostasis/status`            | GET    | Homeostasis status      | Dashboard, Homeostasis |
| `/api/homeostasis/metrics/snapshot`  | GET    | Homeostasis metrics     | Homeostasis            |
| `/api/homeostasis/actuators/execute` | POST   | Execute actuator        | Homeostasis            |
| `/api/run`                           | POST   | Execute .aether script  | Scripts                |
| `/api/status/{job_id}`               | GET    | Script execution status | Scripts                |
| `/api/cancel/{job_id}`               | POST   | Cancel script execution | Scripts                |

### Security Endpoints (Planned)

| Endpoint               | Method | Description         |
| ---------------------- | ------ | ------------------- |
| `/api/security/alerts` | GET    | Get security alerts |
| `/api/security/policy` | GET    | Get complete policy |
| `/api/security/scan`   | POST   | Run security scan   |
| `/api/security/mode`   | PUT    | Set security mode   |

---

## Next Steps

- [ ] Implement missing backend endpoints (security, network, audit)
- [ ] Add WebSocket support for real-time updates
- [ ] Add authentication/authorization
- [ ] Add error boundary for graceful error handling
- [ ] Add loading skeletons for better UX
- [ ] Add unit tests for components
- [ ] Add E2E tests with Playwright
- [ ] Add accessibility improvements (ARIA labels, keyboard nav)

---

## Support

For issues, questions, or contributions:
- Check `docs/` in workspace root
- Review `docs/AETHERRA_MASTER_MAP.md` for architecture
- See `CONTRIBUTING.md` for contribution guidelines

---

**Last Updated:** 2025-01-28
**Version:** GUI v1.0-beta
**Compatible with:** Aetherra OS v0.9+
