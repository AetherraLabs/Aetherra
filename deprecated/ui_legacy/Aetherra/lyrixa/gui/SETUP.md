# Lyrixa GUI - Installation & Setup Guide

## Quick Start

### 1. Install Dependencies

```powershell
cd "d:\Aetherra Project\Aetherra\lyrixa\gui"
npm install
```

### 2. Run Development Server

```powershell
npm run dev
```

The GUI will be available at `http://localhost:3000`

### 3. Build for Production

```powershell
npm run build
```

## Project Structure

```
gui/
├── src/
│   ├── components/
│   │   └── ui/           # shadcn/ui components
│   │       ├── card.tsx
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── tabs.tsx
│   │       ├── progress.tsx
│   │       ├── badge.tsx
│   │       └── dialog.tsx
│   ├── lib/
│   │   └── utils.ts      # Utility functions
│   ├── App.tsx           # Main application component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.js    # Tailwind CSS config
├── vite.config.ts        # Vite config
└── README.md             # Documentation
```

## Features Implemented

### ✅ Fixed Bugs from Original Document

1. **ParticleField Canvas Null Check**: Added proper null checking for canvas element
2. **RotatingSigil useRef**: Fixed missing initial value for useRef
3. **Enter Key Support**: Added onKeyDown handler to chat input for Enter key
4. **Button States**: Added disabled states for approve/deny buttons after action
5. **Progress Bar Width**: Fixed homeostasis progress bars with explicit width
6. **Settings Route**: Added missing settings panel implementation
7. **Capitalization**: Fixed agent names to be properly capitalized
8. **TypeScript Errors**: Resolved all type issues

### 🎨 UI Components

- **Dashboard**: System overview with health metrics, charts, and quick actions
- **Chat**: Real-time messaging interface with Lyrixa
- **Memory**: QFAC/Concept/Episodic visualization with coherence stats
- **Agents**: Agent orchestrator with capability registry
- **Kernel**: Queue metrics, HMR status, and performance monitoring
- **STORM**: Shadow mode with OT/sheaf/TDA evidence tags
- **Self-Improvement**: Suggestion workflow with approve/deny/apply
- **Homeostasis**: Health score and system actuators
- **Security**: Policy and signing status
- **.aether Scripts**: Workflow/Policy/Trace viewer
- **Settings**: Configuration panel (placeholder)

### 🎮 Interactive Features

- **Command Palette**: Press `Ctrl+K` (or `⌘K` on Mac) to open
- **Sound Effects**: UI interactions have subtle audio feedback
- **Particle Field**: Interactive background with mouse tracking
- **3D Visualization**: Rotating holo-core using React Three Fiber
- **Real-time Charts**: Throughput and latency visualization using Recharts

## Backend Integration

### API Endpoints (to be connected)

Configure these in `vite.config.ts` proxy settings:

- `POST /api/lyrixa/chat` - Chat interface
- `GET /api/ai/stream` - SSE v2 streaming
- `GET /api/agents` - Agent status
- `GET /api/memory/status` - Memory coherence & narratives
- `GET /api/kernel/status` - Kernel queues and metrics
- `GET /api/homeostasis/health` - Health score
- `GET /api/security/policy` - Security settings

### Environment Variables

Create a `.env` file in the gui directory:

```env
VITE_API_BASE_URL=http://localhost:3012
VITE_ENABLE_DEV_TOOLS=true
```

## Development

### Adding New Components

```tsx
import { YourComponent } from '@/components/ui/your-component'
```

### Styling with Tailwind

The project uses Tailwind CSS with Aetherra brand colors:

- Primary Green: `#00ff88` (emerald-400/500)
- Dark Background: `#070708`
- Card Background: `#0b0b0c`

### Framer Motion Animations

All animations use smooth cubic transitions matching Aetherra's design language.

## Troubleshooting

### Port Already in Use

If port 3000 is taken, modify `vite.config.ts`:

```ts
server: {
  port: 3001, // Change to available port
  ...
}
```

### Build Errors

Clear cache and reinstall:

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

## Next Steps

1. **Connect to Backend**: Wire up API endpoints to real Aetherra services
2. **Authentication**: Add token-based auth for secure access
3. **WebSocket Integration**: Real-time updates for kernel/agents/memory
4. **State Management**: Consider Redux or Zustand for complex state
5. **Testing**: Add unit tests with Vitest and integration tests with Playwright
6. **Accessibility**: Improve ARIA labels and keyboard navigation
7. **Performance**: Optimize bundle size and lazy load routes

## License

See main Aetherra project LICENSE
