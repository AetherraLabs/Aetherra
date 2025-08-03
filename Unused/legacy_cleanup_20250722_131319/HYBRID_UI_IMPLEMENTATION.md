# Lyrixa Hybrid UI Implementation 🌟

This implementation provides a modern hybrid user interface for Lyrixa, combining the power of PySide6 desktop controls with embedded web panels for a cutting-edge user experience.

## 📁 File Structure

```
Aetherra/lyrixa/gui/
├── hybrid_window.py        # Main hybrid UI implementation
├── window_factory.py       # UI selection factory
├── style.qss              # Modern CSS styling
├── ui_config.env          # UI configuration
└── gui_window.py          # Original UI (unchanged)

aetherra_hybrid_launcher.py # Demo launcher for hybrid UI
```

## 🚀 Features

### Hybrid Architecture
- **🖥️ Desktop Shell**: Native PySide6 controls for menus, toolbars, model selection
- **🌐 Web Panels**: Embedded QWebEngineView for chat, analytics, system monitoring
- **🔌 Plugin Compatible**: Maintains all existing plugin API hooks
- **⚡ Performance**: Native performance with modern web UI flexibility

### Interface Components
- **💬 Chat Panel**: Native Qt chat interface with modern styling
- **🖥️ System Panel**: Embedded FastAPI docs and system monitoring
- **🤖 Agents Panel**: Visual agent status and management
- **📊 Performance Panel**: Real-time metrics and monitoring
- **🚀 Self-Improvement**: Future self-improvement dashboard
- **🧩 Plugins Panel**: Enhanced plugin management

## [TOOL] Configuration

### Environment Variables

| Variable                   | Values              | Description            |
| -------------------------- | ------------------- | ---------------------- |
| `LYRIXA_UI_MODE`           | `classic`, `hybrid` | UI mode selection      |
| `HYBRID_ENABLE_WEB_PANELS` | `true`, `false`     | Enable web integration |
| `HYBRID_API_PORT`          | `8007`              | FastAPI server port    |
| `HYBRID_CHAT_API_PORT`     | `8080`              | Chat API port          |

### Quick Setup

1. **Enable Hybrid UI**:
   ```bash
   set LYRIXA_UI_MODE=hybrid
   python aetherra_hybrid_launcher.py
   ```

2. **Use Classic UI** (default):
   ```bash
   python aetherra_launcher.py
   ```

## 🛠️ Implementation Details

### Drop-in Compatibility

The hybrid UI is designed as a **drop-in replacement** for the existing `LyrixaWindow`:

```python
# Original code (unchanged)
from Aetherra.lyrixa.gui.gui_window import LyrixaWindow
window = LyrixaWindow()

# Hybrid code (using factory)
from Aetherra.lyrixa.gui.window_factory import create_lyrixa_window
window = create_lyrixa_window()  # Auto-selects based on LYRIXA_UI_MODE
```

### API Compatibility

All existing methods are preserved:

```python
# These methods work identically in both UIs
window.attach_lyrixa(lyrixa_instance)
window.attach_runtime(runtime_instance)
window.attach_intelligence_stack(intelligence_stack)
window.refresh_plugin_discovery()
window.update_dashboard_metrics()
```

### Plugin Integration

Plugins continue to work unchanged:

```python
# Plugin methods preserved
window.add_plugin_editor_tab()
window.refresh_plugin_discovery()
window.update_plugin_display(plugins)
```

## 🎨 Styling

The hybrid UI includes modern styling with:

- **🎨 Modern Color Scheme**: Clean whites, blues, and grays
- **🌙 Dark Sidebar**: Professional navigation with Aetherra branding
- **💫 Smooth Animations**: Hover effects and transitions
- **📱 Responsive Design**: Adapts to different window sizes

### Custom Styling

Modify `style.qss` to customize appearance:

```css
/* Example: Change primary color */
#sendButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #your-color, stop: 1 #your-darker-color);
}
```

## 🔌 Web Integration

### Embedded Panels

The hybrid UI embeds web content using `QWebEngineView`:

```python
# System panel shows FastAPI docs
self.system_web_view.load(QUrl("http://127.0.0.1:8007/docs"))

# Future: Chat panel could embed React/Vue components
# self.chat_web_view.load(QUrl("http://127.0.0.1:3000/chat"))
```

### API Integration

Perfect for integrating with:
- **FastAPI Documentation**: Live API exploration
- **React Dashboards**: Modern analytics interfaces
- **Vue.js Components**: Interactive plugin UIs
- **Aetherra.dev**: Future web platform integration

## 📋 Development Roadmap

### Phase 1: Foundation ✅
- [x] Hybrid window implementation
- [x] Drop-in compatibility
- [x] Basic web panel integration
- [x] Modern styling system

### Phase 2: Enhanced Features 🔄
- [ ] Live chat with WebSocket integration
- [ ] Real-time performance monitoring
- [ ] Advanced plugin editor in web panel
- [ ] Custom dashboard configuration

### Phase 3: Web Platform Integration 🚀
- [ ] Aetherra.dev integration
- [ ] Cloud sync capabilities
- [ ] Multi-user collaboration
- [ ] Advanced analytics dashboards

## 🐛 Troubleshooting

### Common Issues

1. **PySide6 Import Errors**:
   ```bash
   py -m pip install PySide6
   ```

2. **WebEngine Not Working**:
   ```bash
   py -m pip install PySide6-Addons
   ```

3. **Hybrid UI Not Loading**:
   ```bash
   set LYRIXA_UI_MODE=hybrid
   echo %LYRIXA_UI_MODE%  # Verify setting
   ```

### Debug Mode

Enable debug output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Adding New Panels

1. Create panel method in `LyrixaHybridWindow`:
   ```python
   def create_my_panel(self):
       panel = QWidget()
       # Panel implementation
       return panel
   ```

2. Add to content stack:
   ```python
   self.my_panel = self.create_my_panel()
   self.content_stack.addWidget(self.my_panel)
   ```

3. Add navigation button:
   ```python
   ("🎯 My Panel", panel_index, self.show_my_panel)
   ```

### Styling Guidelines

- Use semantic object names: `#panelTitle`, `#navButton`
- Follow color scheme: Blues (#3b82f6), grays (#f8fafc)
- Include hover states for interactive elements
- Maintain 8px border radius for modern look

## 📄 License

This hybrid UI implementation is part of the Lyrixa AI Assistant project and follows the same licensing terms as the main project.

---

*Built with ❤️ for the Aetherra ecosystem*
