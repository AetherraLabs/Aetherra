#!/usr/bin/env python3
"""
🔮 Phase 3: Auto-Generating Panels from Aetherra State
======================================================

Dynamic GUI generation system that introspects Lyrixa's internal state
and automatically creates/updates HTML panels based on:
- Active plugins and their capabilities
- Running agents and their goals
- Memory system state and patterns
- System metrics and performance data

Architecture:
- StateIntrospector: Scans all backend systems for metadata
- PanelGenerator: Creates HTML components from state data
- LayoutManager: Arranges panels dynamically
- UpdateOrchestrator: Coordinates real-time updates
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal, QTimer, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView

logger = logging.getLogger(__name__)


@dataclass
class ComponentState:
    """Represents the state of a system component"""
    name: str
    type: str  # 'plugin', 'agent', 'memory', 'service'
    status: str  # 'active', 'idle', 'error', 'loading'
    metadata: Dict[str, Any]
    capabilities: List[str]
    last_updated: datetime
    importance: float  # 0.0-1.0 for panel prioritization


@dataclass
class PanelTemplate:
    """Template for generating a GUI panel"""
    id: str
    title: str
    component_type: str
    template_path: str
    data_bindings: Dict[str, str]
    update_frequency: int  # seconds
    priority: int  # 1=highest, 10=lowest
    auto_generated: bool = True


class StateIntrospector(QObject):
    """
    🔍 State Introspector
    ====================

    Scans all backend systems and extracts metadata for panel generation.
    Uses Lyrixa's introspection capabilities to discover system state.
    """

    state_discovered = Signal(str)  # JSON state data

    def __init__(self):
        super().__init__()
        self.backend_services = {}
        self.discovered_state = {}
        self.introspection_cache = {}

        # Auto-discovery timer
        self.discovery_timer = QTimer()
        self.discovery_timer.timeout.connect(self.introspect_all_systems)
        self.discovery_timer.start(5000)  # Every 5 seconds

    def connect_backend_services(self, services: Dict[str, Any]):
        """Connect to backend services for introspection"""
        self.backend_services = services
        logger.info(f"[INTROSPECT] State introspector connected to {len(services)} services")
        self.introspect_all_systems()

    @Slot()
    def introspect_all_systems(self):
        """Perform comprehensive state introspection"""
        try:
            new_state = {}

            # Introspect each backend service
            new_state['plugins'] = self._introspect_plugins()
            new_state['agents'] = self._introspect_agents()
            new_state['memory'] = self._introspect_memory()
            new_state['services'] = self._introspect_services()
            new_state['metrics'] = self._introspect_metrics()

            # Check if state has changed significantly
            if self._state_changed_significantly(new_state):
                self.discovered_state = new_state
                # Convert ComponentState objects to dicts for JSON serialization
                serializable_state = {
                    key: [asdict(comp) if isinstance(comp, ComponentState) else comp for comp in value]
                    if isinstance(value, list) else value
                    for key, value in new_state.items()
                }
                self.state_discovered.emit(json.dumps(serializable_state, default=str))
                logger.info("[PHASE3] State introspection: Significant changes detected")

        except Exception as e:
            logger.error(f"[ERROR] State introspection failed: {e}")

    def _introspect_plugins(self) -> List[ComponentState]:
        """Introspect plugin system state"""
        plugin_states = []
        plugin_manager = self.backend_services.get('plugin_manager')

        if plugin_manager:
            try:
                # Get plugin registry data
                if hasattr(plugin_manager, 'get_all_plugins'):
                    plugins = plugin_manager.get_all_plugins()

                    for name, plugin_info in plugins.items():
                        capabilities = []

                        # Extract capabilities from plugin metadata
                        if hasattr(plugin_info, 'capabilities'):
                            capabilities = plugin_info.capabilities
                        elif isinstance(plugin_info, dict):
                            capabilities = plugin_info.get('capabilities', [])

                        # Determine plugin status
                        status = 'active' if plugin_info.get('loaded', False) else 'idle'
                        if plugin_info.get('error'):
                            status = 'error'

                        # Calculate importance based on usage and capabilities
                        importance = min(1.0, len(capabilities) * 0.2 + 0.3)

                        state = ComponentState(
                            name=name,
                            type='plugin',
                            status=status,
                            metadata={
                                'version': plugin_info.get('version', '1.0.0'),
                                'description': plugin_info.get('description', ''),
                                'author': plugin_info.get('author', 'Unknown'),
                                'category': plugin_info.get('category', 'general'),
                                'loaded': plugin_info.get('loaded', False),
                                'error': plugin_info.get('error'),
                                'file_path': plugin_info.get('file_path', '')
                            },
                            capabilities=capabilities,
                            last_updated=datetime.now(),
                            importance=importance
                        )

                        plugin_states.append(state)

            except Exception as e:
                logger.warning(f"Plugin introspection error: {e}")

        return plugin_states

    def _introspect_agents(self) -> List[ComponentState]:
        """Introspect agent system state"""
        agent_states = []
        agent_orchestrator = self.backend_services.get('agent_orchestrator')

        if agent_orchestrator:
            try:
                # Get active agents
                if hasattr(agent_orchestrator, 'agents'):
                    agents = agent_orchestrator.agents

                    for agent_id, agent in agents.items():
                        capabilities = ['reasoning', 'goal_execution']

                        # Extract agent capabilities
                        if hasattr(agent, 'capabilities'):
                            capabilities.extend(agent.capabilities)

                        # Get current goals
                        current_goals = []
                        if hasattr(agent, 'goals'):
                            current_goals = agent.goals[:3]  # Top 3 goals

                        state = ComponentState(
                            name=f"Agent-{agent_id}",
                            type='agent',
                            status='active',
                            metadata={
                                'current_goals': current_goals,
                                'agent_type': getattr(agent, 'agent_type', 'general'),
                                'priority': getattr(agent, 'priority', 5),
                                'last_action': getattr(agent, 'last_action', None),
                                'performance_score': getattr(agent, 'performance_score', 0.5)
                            },
                            capabilities=capabilities,
                            last_updated=datetime.now(),
                            importance=0.7
                        )

                        agent_states.append(state)

            except Exception as e:
                logger.warning(f"Agent introspection error: {e}")

        return agent_states

    def _introspect_memory(self) -> List[ComponentState]:
        """Introspect memory system state"""
        memory_states = []
        memory_system = self.backend_services.get('memory_system')

        if memory_system:
            try:
                capabilities = ['storage', 'retrieval', 'pattern_recognition']

                # Get memory statistics
                stats = {}
                if hasattr(memory_system, 'get_stats'):
                    stats = memory_system.get_stats()
                elif hasattr(memory_system, 'memory'):
                    stats = {
                        'total_memories': len(getattr(memory_system, 'memory', [])),
                        'memory_types': ['episodic', 'semantic', 'procedural']
                    }

                # Analyze memory patterns
                patterns = []
                if hasattr(memory_system, 'analyze_patterns'):
                    patterns = memory_system.analyze_patterns()

                state = ComponentState(
                    name='Memory System',
                    type='memory',
                    status='active',
                    metadata={
                        'statistics': stats,
                        'patterns': patterns,
                        'compression_ratio': getattr(memory_system, 'compression_ratio', 0.0),
                        'query_performance': getattr(memory_system, 'avg_query_time', 0.0),
                        'storage_efficiency': getattr(memory_system, 'storage_efficiency', 0.8)
                    },
                    capabilities=capabilities,
                    last_updated=datetime.now(),
                    importance=0.9
                )

                memory_states.append(state)

            except Exception as e:
                logger.warning(f"Memory introspection error: {e}")

        return memory_states

    def _introspect_services(self) -> List[ComponentState]:
        """Introspect service registry state"""
        service_states = []
        service_registry = self.backend_services.get('service_registry')

        if service_registry:
            try:
                # Get registered services
                if hasattr(service_registry, 'services'):
                    services = service_registry.services

                    for service_name, service in services.items():
                        capabilities = ['service_provision']

                        # Determine service health
                        status = 'active'
                        if hasattr(service, 'health_check'):
                            try:
                                health = service.health_check()
                                status = 'active' if health else 'error'
                            except:
                                status = 'error'

                        state = ComponentState(
                            name=service_name,
                            type='service',
                            status=status,
                            metadata={
                                'service_type': type(service).__name__,
                                'uptime': getattr(service, 'uptime', 0),
                                'requests_handled': getattr(service, 'requests_count', 0),
                                'last_activity': getattr(service, 'last_activity', None)
                            },
                            capabilities=capabilities,
                            last_updated=datetime.now(),
                            importance=0.6
                        )

                        service_states.append(state)

            except Exception as e:
                logger.warning(f"Service introspection error: {e}")

        return service_states

    def _introspect_metrics(self) -> List[ComponentState]:
        """Introspect system metrics"""
        try:
            import psutil

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            state = ComponentState(
                name='System Metrics',
                type='metrics',
                status='active',
                metadata={
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available,
                    'disk_usage': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0,
                    'process_count': len(psutil.pids()),
                    'network_activity': self._get_network_activity()
                },
                capabilities=['monitoring', 'alerting'],
                last_updated=datetime.now(),
                importance=0.5
            )

            return [state]

        except Exception as e:
            logger.warning(f"Metrics introspection error: {e}")
            return []

    def _get_network_activity(self) -> Dict[str, int]:
        """Get network activity metrics"""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}

    def _state_changed_significantly(self, new_state: Dict) -> bool:
        """Check if state has changed enough to trigger panel updates"""
        if not self.discovered_state:
            return True

        # Compare component counts
        old_counts = {k: len(v) for k, v in self.discovered_state.items()}
        new_counts = {k: len(v) for k, v in new_state.items()}

        if old_counts != new_counts:
            return True

        # Check for status changes in components
        for category, components in new_state.items():
            old_components = self.discovered_state.get(category, [])

            if len(components) != len(old_components):
                return True

            # Check individual component changes
            for new_comp in components:
                matching_old = next(
                    (c for c in old_components if c.name == new_comp.name),
                    None
                )

                if not matching_old or matching_old.status != new_comp.status:
                    return True

        return False


class PanelGenerator(QObject):
    """
    🎨 Panel Generator
    =================

    Generates HTML panel components from system state data.
    Creates responsive, interactive panels that match Aetherra styling.
    """

    panel_generated = Signal(str, str)  # panel_id, html_content

    def __init__(self, panels_dir: Path):
        super().__init__()
        self.panels_dir = panels_dir
        self.templates_dir = panels_dir / 'templates'
        self.auto_generated_dir = panels_dir / 'auto_generated'

        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.auto_generated_dir.mkdir(parents=True, exist_ok=True)

        # Panel templates
        self.panel_templates = {}
        self._load_base_templates()

    def _load_base_templates(self):
        """Load base HTML templates for different component types"""

        # Plugin panel template
        self.panel_templates['plugin'] = '''
<div class="auto-panel plugin-panel" data-component="{name}" data-type="plugin">
    <div class="panel-header">
        <div class="panel-icon">{icon}</div>
        <h3>{name}</h3>
        <span class="status-badge {status}">{status}</span>
    </div>
    <div class="panel-content">
        <p class="description">{description}</p>
        <div class="capabilities">
            {capabilities_html}
        </div>
        <div class="metadata">
            <div class="meta-item">
                <span class="label">Version:</span>
                <span class="value">{version}</span>
            </div>
            <div class="meta-item">
                <span class="label">Category:</span>
                <span class="value">{category}</span>
            </div>
        </div>
        <div class="actions">
            <button class="btn btn-primary" onclick="handlePluginAction('{name}', 'configure')">
                ⚙️ Configure
            </button>
            <button class="btn btn-secondary" onclick="handlePluginAction('{name}', 'toggle')">
                {toggle_text}
            </button>
        </div>
    </div>
</div>
'''

        # Agent panel template
        self.panel_templates['agent'] = '''
<div class="auto-panel agent-panel" data-component="{name}" data-type="agent">
    <div class="panel-header">
        <div class="panel-icon">🤖</div>
        <h3>{name}</h3>
        <span class="status-badge {status}">{status}</span>
    </div>
    <div class="panel-content">
        <div class="current-goals">
            <h4>Current Goals:</h4>
            {goals_html}
        </div>
        <div class="performance">
            <div class="metric">
                <span class="label">Performance:</span>
                <div class="progress-bar">
                    <div class="progress" style="width: {performance}%"></div>
                </div>
            </div>
        </div>
        <div class="actions">
            <button class="btn btn-primary" onclick="handleAgentAction('{name}', 'add_goal')">
                ➕ Add Goal
            </button>
            <button class="btn btn-secondary" onclick="handleAgentAction('{name}', 'pause')">
                ⏸️ Pause
            </button>
        </div>
    </div>
</div>
'''

        # Memory panel template
        self.panel_templates['memory'] = '''
<div class="auto-panel memory-panel" data-component="{name}" data-type="memory">
    <div class="panel-header">
        <div class="panel-icon">🧠</div>
        <h3>{name}</h3>
        <span class="status-badge {status}">{status}</span>
    </div>
    <div class="panel-content">
        <div class="memory-stats">
            {stats_html}
        </div>
        <div class="memory-patterns">
            <h4>Recent Patterns:</h4>
            {patterns_html}
        </div>
        <div class="actions">
            <button class="btn btn-primary" onclick="handleMemoryAction('search')">
                🔍 Search
            </button>
            <button class="btn btn-secondary" onclick="handleMemoryAction('analyze')">
                📊 Analyze
            </button>
        </div>
    </div>
</div>
'''

        # Service panel template
        self.panel_templates['service'] = '''
<div class="auto-panel service-panel" data-component="{name}" data-type="service">
    <div class="panel-header">
        <div class="panel-icon">⚙️</div>
        <h3>{name}</h3>
        <span class="status-badge {status}">{status}</span>
    </div>
    <div class="panel-content">
        <div class="service-info">
            <div class="meta-item">
                <span class="label">Type:</span>
                <span class="value">{service_type}</span>
            </div>
            <div class="meta-item">
                <span class="label">Uptime:</span>
                <span class="value">{uptime}s</span>
            </div>
            <div class="meta-item">
                <span class="label">Requests:</span>
                <span class="value">{requests}</span>
            </div>
        </div>
        <div class="actions">
            <button class="btn btn-primary" onclick="handleServiceAction('{name}', 'restart')">
                🔄 Restart
            </button>
            <button class="btn btn-secondary" onclick="handleServiceAction('{name}', 'status')">
                📊 Status
            </button>
        </div>
    </div>
</div>
'''

        # Metrics panel template
        self.panel_templates['metrics'] = '''
<div class="auto-panel metrics-panel" data-component="{name}" data-type="metrics">
    <div class="panel-header">
        <div class="panel-icon">📊</div>
        <h3>{name}</h3>
        <span class="status-badge {status}">{status}</span>
    </div>
    <div class="panel-content">
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{cpu_usage}%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{memory_usage}%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{process_count}</div>
                <div class="metric-label">Processes</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{disk_usage}%</div>
                <div class="metric-label">Disk Usage</div>
            </div>
        </div>
    </div>
</div>
'''

    def generate_panels_from_state(self, state_data: Dict[str, List[ComponentState]]):
        """Generate HTML panels from introspected state data"""
        try:
            generated_panels = []

            for category, components in state_data.items():
                for component in components:
                    panel_html = self._generate_component_panel(component)
                    if panel_html:
                        panel_id = f"auto_{component.type}_{component.name.lower().replace(' ', '_')}"

                        # Save generated panel
                        panel_file = self.auto_generated_dir / f"{panel_id}.html"
                        with open(panel_file, 'w', encoding='utf-8') as f:
                            f.write(self._wrap_panel_html(panel_html, panel_id))

                        generated_panels.append((panel_id, panel_html))
                        self.panel_generated.emit(panel_id, panel_html)

            logger.info(f"[GENERATE] Generated {len(generated_panels)} panels from system state")
            return generated_panels

        except Exception as e:
            logger.error(f"[ERROR] Panel generation failed: {e}")
            return []

    def _generate_component_panel(self, component: ComponentState) -> Optional[str]:
        """Generate HTML for a single component"""
        template = self.panel_templates.get(component.type)
        if not template:
            return None

        try:
            if component.type == 'plugin':
                return self._generate_plugin_panel(component, template)
            elif component.type == 'agent':
                return self._generate_agent_panel(component, template)
            elif component.type == 'memory':
                return self._generate_memory_panel(component, template)
            elif component.type == 'service':
                return self._generate_service_panel(component, template)
            elif component.type == 'metrics':
                return self._generate_metrics_panel(component, template)

        except Exception as e:
            logger.warning(f"Error generating panel for {component.name}: {e}")
            return None

    def _generate_plugin_panel(self, component: ComponentState, template: str) -> str:
        """Generate plugin panel HTML"""
        # Get plugin icon based on capabilities
        icon = self._get_plugin_icon(component.capabilities)

        # Generate capabilities HTML
        capabilities_html = ''.join([
            f'<span class="capability-tag">{cap}</span>'
            for cap in component.capabilities[:5]  # Limit to 5 capabilities
        ])

        # Toggle button text
        toggle_text = "⏸️ Disable" if component.status == 'active' else "▶️ Enable"

        return template.format(
            name=component.name,
            icon=icon,
            status=component.status,
            description=component.metadata.get('description', 'No description available'),
            capabilities_html=capabilities_html,
            version=component.metadata.get('version', '1.0.0'),
            category=component.metadata.get('category', 'general'),
            toggle_text=toggle_text
        )

    def _generate_agent_panel(self, component: ComponentState, template: str) -> str:
        """Generate agent panel HTML"""
        # Generate goals HTML
        goals = component.metadata.get('current_goals', [])
        goals_html = ''.join([
            f'<div class="goal-item">• {goal}</div>'
            for goal in goals[:3]  # Top 3 goals
        ])

        if not goals_html:
            goals_html = '<div class="goal-item">No active goals</div>'

        # Performance percentage
        performance = int(component.metadata.get('performance_score', 0.5) * 100)

        return template.format(
            name=component.name,
            status=component.status,
            goals_html=goals_html,
            performance=performance
        )

    def _generate_memory_panel(self, component: ComponentState, template: str) -> str:
        """Generate memory panel HTML"""
        stats = component.metadata.get('statistics', {})

        # Generate stats HTML
        stats_html = ''.join([
            f'<div class="stat-item"><span class="label">{k.replace("_", " ").title()}:</span><span class="value">{v}</span></div>'
            for k, v in stats.items() if isinstance(v, (int, float, str))
        ])

        # Generate patterns HTML
        patterns = component.metadata.get('patterns', [])
        patterns_html = ''.join([
            f'<div class="pattern-item">• {pattern}</div>'
            for pattern in patterns[:3]  # Latest 3 patterns
        ])

        if not patterns_html:
            patterns_html = '<div class="pattern-item">No patterns detected</div>'

        return template.format(
            name=component.name,
            status=component.status,
            stats_html=stats_html,
            patterns_html=patterns_html
        )

    def _generate_service_panel(self, component: ComponentState, template: str) -> str:
        """Generate service panel HTML"""
        return template.format(
            name=component.name,
            status=component.status,
            service_type=component.metadata.get('service_type', 'Unknown'),
            uptime=component.metadata.get('uptime', 0),
            requests=component.metadata.get('requests_handled', 0)
        )

    def _generate_metrics_panel(self, component: ComponentState, template: str) -> str:
        """Generate metrics panel HTML"""
        metadata = component.metadata
        return template.format(
            name=component.name,
            status=component.status,
            cpu_usage=metadata.get('cpu_usage', 0),
            memory_usage=metadata.get('memory_usage', 0),
            process_count=metadata.get('process_count', 0),
            disk_usage=metadata.get('disk_usage', 0)
        )

    def _get_plugin_icon(self, capabilities: List[str]) -> str:
        """Get appropriate icon for plugin based on capabilities"""
        icon_map = {
            'memory': '🧠',
            'analysis': '📊',
            'ai': '🤖',
            'audio': '🎵',
            'visual': '👁️',
            'file': '📁',
            'network': '🌐',
            'calculation': '🧮',
            'text': '📝',
            'security': '🔒'
        }

        for capability in capabilities:
            for key, icon in icon_map.items():
                if key in capability.lower():
                    return icon

        return '🔌'  # Default plugin icon

    def _wrap_panel_html(self, panel_html: str, panel_id: str) -> str:
        """Wrap panel HTML with full page structure"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Generated Panel: {panel_id}</title>
    <link rel="stylesheet" href="../assets/style.css">
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        .auto-panel {{
            margin: 1rem;
            padding: 1rem;
            border: 1px solid var(--aetherra-border);
            border-radius: 8px;
            background: var(--aetherra-dark);
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}

        .panel-icon {{
            font-size: 1.5rem;
        }}

        .status-badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-left: auto;
        }}

        .status-badge.active {{
            background: var(--aetherra-green);
            color: black;
        }}

        .status-badge.idle {{
            background: var(--aetherra-yellow);
            color: black;
        }}

        .status-badge.error {{
            background: var(--aetherra-red);
            color: white;
        }}

        .capabilities {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem;
            margin: 0.5rem 0;
        }}

        .capability-tag {{
            background: var(--aetherra-purple);
            color: white;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-size: 0.7rem;
        }}

        .meta-item, .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 0.25rem 0;
        }}

        .actions {{
            margin-top: 1rem;
            display: flex;
            gap: 0.5rem;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }}

        .metric-card {{
            text-align: center;
            padding: 0.5rem;
            border: 1px solid var(--aetherra-border);
            border-radius: 4px;
        }}

        .metric-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--aetherra-green);
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--aetherra-gray-dark);
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress {{
            height: 100%;
            background: var(--aetherra-green);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    {panel_html}

    <script>
        // Panel interaction handlers
        function handlePluginAction(pluginName, action) {{
            if (window.bridge) {{
                window.bridge.handlePanelCommand(JSON.stringify({{
                    type: 'plugin_action',
                    payload: {{ plugin: pluginName, action: action }}
                }}));
            }}
        }}

        function handleAgentAction(agentName, action) {{
            if (window.bridge) {{
                window.bridge.handlePanelCommand(JSON.stringify({{
                    type: 'agent_command',
                    payload: {{ agent: agentName, action: action }}
                }}));
            }}
        }}

        function handleMemoryAction(action) {{
            if (window.bridge) {{
                window.bridge.handlePanelCommand(JSON.stringify({{
                    type: 'memory_query',
                    payload: {{ action: action }}
                }}));
            }}
        }}

        function handleServiceAction(serviceName, action) {{
            if (window.bridge) {{
                window.bridge.handlePanelCommand(JSON.stringify({{
                    type: 'system_command',
                    payload: {{ service: serviceName, action: action }}
                }}));
            }}
        }}

        // Connect to Qt bridge
        new QWebChannel(qt.webChannelTransport, function(channel) {{
            window.bridge = channel.objects.bridge;
        }});
    </script>
</body>
</html>'''


class LayoutManager(QObject):
    """
    📐 Layout Manager
    ================

    Manages dynamic panel layout based on component importance and relationships.
    Automatically arranges panels for optimal user experience.
    """

    layout_updated = Signal(str)  # Layout configuration JSON

    def __init__(self):
        super().__init__()
        self.current_layout = {}
        self.panel_priorities = {}
        self.layout_rules = {
            'max_columns': 3,
            'max_panels_per_view': 12,
            'priority_threshold': 0.5,
            'group_similar_types': True
        }

    def calculate_optimal_layout(self, components: List[ComponentState]) -> Dict[str, Any]:
        """Calculate optimal panel layout based on component importance"""
        try:
            # Sort components by importance
            sorted_components = sorted(components, key=lambda x: x.importance, reverse=True)

            # Filter high-priority components
            high_priority = [c for c in sorted_components if c.importance >= self.layout_rules['priority_threshold']]

            # Group by type if enabled
            if self.layout_rules['group_similar_types']:
                grouped = self._group_components_by_type(high_priority)
            else:
                grouped = {'all': high_priority}

            # Calculate grid layout
            layout = self._calculate_grid_layout(grouped)

            self.current_layout = layout
            self.layout_updated.emit(json.dumps(layout))

            return layout

        except Exception as e:
            logger.error(f"[ERROR] Layout calculation failed: {e}")
            return {}

    def _group_components_by_type(self, components: List[ComponentState]) -> Dict[str, List[ComponentState]]:
        """Group components by type for better organization"""
        groups = {}
        for component in components:
            if component.type not in groups:
                groups[component.type] = []
            groups[component.type].append(component)

        return groups

    def _calculate_grid_layout(self, grouped_components: Dict[str, List[ComponentState]]) -> Dict[str, Any]:
        """Calculate grid layout for component groups"""
        layout = {
            'sections': [],
            'total_panels': 0,
            'grid_columns': min(len(grouped_components), self.layout_rules['max_columns'])
        }

        for group_name, components in grouped_components.items():
            section = {
                'title': f"{group_name.title()} Components",
                'type': group_name,
                'panels': [],
                'importance': sum(c.importance for c in components) / len(components)
            }

            for component in components[:6]:  # Max 6 panels per section
                panel_config = {
                    'id': f"auto_{component.type}_{component.name.lower().replace(' ', '_')}",
                    'title': component.name,
                    'type': component.type,
                    'status': component.status,
                    'importance': component.importance,
                    'size': self._calculate_panel_size(component)
                }
                section['panels'].append(panel_config)
                layout['total_panels'] += 1

            layout['sections'].append(section)

        # Sort sections by importance
        layout['sections'] = sorted(layout['sections'], key=lambda x: x['importance'], reverse=True)

        return layout

    def _calculate_panel_size(self, component: ComponentState) -> str:
        """Calculate panel size based on component importance"""
        if component.importance >= 0.8:
            return 'large'
        elif component.importance >= 0.6:
            return 'medium'
        else:
            return 'small'


class UpdateOrchestrator(QObject):
    """
    🎵 Update Orchestrator
    ======================

    Coordinates real-time updates across all auto-generated panels.
    Manages update frequencies and prevents overwhelming the UI.
    """

    def __init__(self):
        super().__init__()
        self.update_queues = {}
        self.panel_update_timers = {}
        self.update_rates = {
            'plugin': 10,  # seconds
            'agent': 5,
            'memory': 15,
            'service': 20,
            'metrics': 2
        }

    def schedule_panel_updates(self, panel_configs: List[Dict[str, Any]]):
        """Schedule periodic updates for all panels"""
        for config in panel_configs:
            panel_type = config.get('type')
            panel_id = config.get('id')

            if panel_type in self.update_rates:
                update_rate = self.update_rates[panel_type]

                # Create update timer
                timer = QTimer()
                timer.timeout.connect(lambda pid=panel_id: self._update_panel(pid))
                timer.start(update_rate * 1000)  # Convert to milliseconds

                self.panel_update_timers[panel_id] = timer
                logger.debug(f"[SCHEDULE] Scheduled updates for {panel_id} every {update_rate}s")

    @Slot(str)
    def _update_panel(self, panel_id: str):
        """Update a specific panel with fresh data"""
        try:
            # This would trigger a refresh of the specific panel
            # Implementation depends on how panels are connected to data sources
            logger.debug(f"[UPDATE] Updating panel: {panel_id}")

        except Exception as e:
            logger.warning(f"Panel update failed for {panel_id}: {e}")

    def stop_all_updates(self):
        """Stop all scheduled updates"""
        for timer in self.panel_update_timers.values():
            timer.stop()
        self.panel_update_timers.clear()
        logger.info("[STOP] All panel updates stopped")


class Phase3AutoGenerator(QObject):
    """
    🔮 Phase 3: Auto-Generator Controller
    ====================================

    Main controller that orchestrates the entire auto-generation system.
    Integrates introspection, generation, layout, and updates.
    """

    panels_generated = Signal(str)  # Generated panels data
    layout_changed = Signal(str)    # Layout configuration

    def __init__(self, gui_dir: Path):
        super().__init__()
        self.gui_dir = gui_dir
        self.panels_dir = gui_dir / 'web_panels'

        # Initialize components
        self.state_introspector = StateIntrospector()
        self.panel_generator = PanelGenerator(self.panels_dir)
        self.layout_manager = LayoutManager()
        self.update_orchestrator = UpdateOrchestrator()

        # Connect signals
        self.state_introspector.state_discovered.connect(self._on_state_discovered)
        self.panel_generator.panel_generated.connect(self._on_panel_generated)
        self.layout_manager.layout_updated.connect(self._on_layout_updated)

        logger.info("[PHASE3] Auto-Generator initialized")

    def connect_backend_services(self, services: Dict[str, Any]):
        """Connect backend services to the auto-generation system"""
        self.state_introspector.connect_backend_services(services)
        logger.info(f"[CONNECT] Phase 3 connected to {len(services)} backend services")

    @Slot(str)
    def _on_state_discovered(self, state_json: str):
        """Handle new state discovery"""
        try:
            state_data = json.loads(state_json)

            # Convert dictionaries back to ComponentState objects
            components = []
            for category, component_dicts in state_data.items():
                for comp_dict in component_dicts:
                    if isinstance(comp_dict, dict):
                        # Convert dict to ComponentState
                        component = ComponentState(
                            name=comp_dict['name'],
                            type=comp_dict['type'],
                            status=comp_dict['status'],
                            metadata=comp_dict['metadata'],
                            capabilities=comp_dict['capabilities'],
                            last_updated=datetime.fromisoformat(comp_dict['last_updated']) if isinstance(comp_dict['last_updated'], str) else comp_dict['last_updated'],
                            importance=comp_dict['importance']
                        )
                        components.append(component)

            # Generate panels from state
            generated_panels = self.panel_generator.generate_panels_from_state(state_data)

            # Calculate optimal layout
            layout = self.layout_manager.calculate_optimal_layout(components)

            # Schedule updates for generated panels
            panel_configs = []
            for section in layout.get('sections', []):
                panel_configs.extend(section.get('panels', []))

            self.update_orchestrator.schedule_panel_updates(panel_configs)

            # Emit signal with generated panels data
            self.panels_generated.emit(json.dumps({
                'panels': [{'id': pid, 'html': html} for pid, html in generated_panels],
                'layout': layout,
                'timestamp': datetime.now().isoformat()
            }))

            logger.info(f"[PHASE3] Generated {len(generated_panels)} panels with dynamic layout")

        except Exception as e:
            logger.error(f"[ERROR] State discovery handling failed: {e}")

    @Slot(str, str)
    def _on_panel_generated(self, panel_id: str, html_content: str):
        """Handle individual panel generation"""
        logger.debug(f"📝 Panel generated: {panel_id}")

    @Slot(str)
    def _on_layout_updated(self, layout_json: str):
        """Handle layout updates"""
        self.layout_changed.emit(layout_json)
        logger.debug("📐 Layout updated")

    def start_auto_generation(self):
        """Start the auto-generation process"""
        logger.info("[START] Phase 3 Auto-Generation started")
        self.state_introspector.introspect_all_systems()

    def stop_auto_generation(self):
        """Stop the auto-generation process"""
        self.update_orchestrator.stop_all_updates()
        logger.info("[STOP] Phase 3 Auto-Generation stopped")
