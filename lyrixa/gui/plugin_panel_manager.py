"""
Plugin Panel Manager for Lyrixa
===============================

Manages collapsible plugin panels with layout memory and resizing functionality.
Provides intuitive plugin interaction and workspace organization.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class PluginPanelManager:
    """Manages plugin panel layouts, resizing, and collapsibility."""
    
    def __init__(self, config_path: str = "lyrixa_panel_layouts.json"):
        """Initialize the plugin panel manager."""
        self.config_path = Path(config_path)
        self.panel_states = {}
        self.panel_sizes = {}
        self.layout_presets = {}
        self.active_layout = "default"
        self._load_layout_config()
        
    def _load_layout_config(self):
        """Load panel layout configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.panel_states = config.get('panel_states', {})
                    self.panel_sizes = config.get('panel_sizes', {})
                    self.layout_presets = config.get('layout_presets', {})
                    self.active_layout = config.get('active_layout', 'default')
            else:
                self._initialize_default_layouts()
        except Exception as e:
            print(f"Error loading panel layout config: {e}")
            self._initialize_default_layouts()
    
    def _initialize_default_layouts(self):
        """Initialize default panel layouts."""
        self.layout_presets = {
            "default": {
                "plugin_panel": {"collapsed": False, "width": 300, "position": "left"},
                "chat_panel": {"collapsed": False, "width": 500, "position": "center"},
                "intelligence_panel": {"collapsed": False, "width": 200, "position": "right"},
                "history_panel": {"collapsed": True, "width": 250, "position": "bottom"}
            },
            "focused_chat": {
                "plugin_panel": {"collapsed": True, "width": 300, "position": "left"},
                "chat_panel": {"collapsed": False, "width": 700, "position": "center"},
                "intelligence_panel": {"collapsed": True, "width": 200, "position": "right"},
                "history_panel": {"collapsed": True, "width": 250, "position": "bottom"}
            },
            "development": {
                "plugin_panel": {"collapsed": False, "width": 350, "position": "left"},
                "chat_panel": {"collapsed": False, "width": 450, "position": "center"},
                "intelligence_panel": {"collapsed": False, "width": 250, "position": "right"},
                "history_panel": {"collapsed": False, "width": 200, "position": "bottom"}
            }
        }
        self.panel_states = self.layout_presets["default"].copy()
        self.active_layout = "default"
        
    def save_layout_config(self):
        """Save current panel layout configuration to file."""
        try:
            config = {
                'panel_states': self.panel_states,
                'panel_sizes': self.panel_sizes,
                'layout_presets': self.layout_presets,
                'active_layout': self.active_layout
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving panel layout config: {e}")
    
    def toggle_panel_collapse(self, panel_name: str) -> bool:
        """Toggle the collapsed state of a panel."""
        if panel_name in self.panel_states:
            current_state = self.panel_states[panel_name].get('collapsed', False)
            self.panel_states[panel_name]['collapsed'] = not current_state
            self.save_layout_config()
            return not current_state
        return False
    
    def resize_panel(self, panel_name: str, new_width: int, new_height: Optional[int] = None):
        """Resize a panel and save the new dimensions."""
        if panel_name not in self.panel_states:
            self.panel_states[panel_name] = {}
        
        self.panel_states[panel_name]['width'] = new_width
        if new_height is not None:
            self.panel_states[panel_name]['height'] = new_height
        
        self.save_layout_config()
    
    def get_panel_state(self, panel_name: str) -> Dict[str, Any]:
        """Get the current state of a specific panel."""
        return self.panel_states.get(panel_name, {
            "collapsed": False,
            "width": 300,
            "position": "left"
        })
    
    def set_layout_preset(self, preset_name: str) -> bool:
        """Apply a layout preset."""
        if preset_name in self.layout_presets:
            self.panel_states = self.layout_presets[preset_name].copy()
            self.active_layout = preset_name
            self.save_layout_config()
            return True
        return False
    
    def create_custom_preset(self, preset_name: str, description: str = ""):
        """Create a custom layout preset from current panel states."""
        self.layout_presets[preset_name] = {
            **self.panel_states,
            "_description": description,
            "_created": str(datetime.now())
        }
        self.save_layout_config()
    
    def get_available_presets(self) -> List[str]:
        """Get list of available layout presets."""
        return list(self.layout_presets.keys())
    
    def get_collapsed_panels(self) -> List[str]:
        """Get list of currently collapsed panels."""
        return [
            panel for panel, state in self.panel_states.items()
            if state.get('collapsed', False)
        ]
    
    def get_panel_dimensions(self, panel_name: str) -> Tuple[int, int]:
        """Get panel dimensions (width, height)."""
        state = self.get_panel_state(panel_name)
        return (
            state.get('width', 300),
            state.get('height', 400)
        )
    
    def is_panel_collapsed(self, panel_name: str) -> bool:
        """Check if a panel is currently collapsed."""
        return self.panel_states.get(panel_name, {}).get('collapsed', False)
    
    def expand_all_panels(self):
        """Expand all collapsed panels."""
        for panel in self.panel_states:
            self.panel_states[panel]['collapsed'] = False
        self.save_layout_config()
    
    def collapse_all_panels(self):
        """Collapse all panels."""
        for panel in self.panel_states:
            self.panel_states[panel]['collapsed'] = True
        self.save_layout_config()
    
    def get_layout_summary(self) -> Dict[str, Any]:
        """Get a summary of the current layout state."""
        collapsed_count = len(self.get_collapsed_panels())
        total_panels = len(self.panel_states)
        
        return {
            "active_layout": self.active_layout,
            "total_panels": total_panels,
            "collapsed_panels": collapsed_count,
            "expanded_panels": total_panels - collapsed_count,
            "available_presets": len(self.layout_presets),
            "panel_states": self.panel_states
        }
