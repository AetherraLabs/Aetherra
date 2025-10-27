# Lyrixa GUI

Modern, futuristic GUI for the Aetherra Lyrixa AI system.

## Overview

This GUI provides a comprehensive interface for interacting with Lyrixa, featuring:

- **Aetherra-branded shell**: Sticky top bar with teal flame vibe and "CODE AWAKENED" tagline
- **Sidebar navigation**: Overview, Chat, Memory, Agents, Kernel, STORM, Self-Improvement, Homeostasis, Security, .aether Scripts, Settings
- **Real-time dashboards**: Kernel queues/DLQ, Agent Orchestrator states, Memory coherence & narratives
- **Interactive panels**: Chat interface, memory visualization, agent monitoring, and more

## Tech Stack

- **React** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Framer Motion** for animations
- **Recharts** for data visualization
- **React Three Fiber** for 3D visualizations

## Installation

```bash
cd Aetherra/lyrixa/gui
npm install
```

## Development

```bash
npm run dev
```

## Building for Production

```bash
npm run build
```

## Integration with Aetherra Backend

The GUI is designed to connect to the following endpoints:

- **Chat**: `POST /api/lyrixa/chat` or `/api/ai/stream` (SSE v2)
- **Agents**: Hub/Agents API when enabled
- **Memory**: AetherraMemoryEngineAdvanced status & narratives endpoints
- **Kernel**: `/api/kernel/status`, `/metrics` when Hub is present
- **Homeostasis/Maintenance**: health + actuator bridges
- **Security**: Surface strict/lenient modes

## Design Philosophy

- **Colors**: Aetherra Green (#00ff88), dark backgrounds (#0a0a0a)
- **Animations**: Smooth cubic transitions
- **Layout**: Mirrors the Project Overview services and feature flags
- **UX**: Optimized to "draw positive attention" with clean spacing and rounded-2xl cards

## Features

### Dashboard
- System health metrics
- Throughput and latency charts
- Night Cycle progress
- Quick actions

### Chat
- Real-time message streaming
- Auto-approve toggle for suggestions
- Command palette (⌘K / Ctrl+K)

### Memory
- QFAC/Concept/Episodic visualization
- Coherence statistics
- Memory narratives

### Agents
- Agent capability registry
- Task flow monitoring
- Real-time status updates

### Kernel
- Queue metrics (HMR, retries, DLQ)
- Performance monitoring
- Maintenance controls

### STORM (Shadow Mode)
- OT/sheaf/TDA evidence tags
- TT-rank caps
- Shadow divergence tracking

### Self-Improvement
- Proposed changes from introspection
- Risk assessment
- Approve/deny workflow
- Auto-apply approved changes

### Homeostasis
- Health score visualization
- System setpoints
- Actuator controls

### Security
- Script signing status
- Network policy display
- Prompt injection defense monitoring

### .aether Scripts
- Workflow viewer
- Policy configuration
- Execution trace

## License

See main Aetherra project LICENSE
