"""
🎨 PLUGIN CONFIDENCE GUI INTEGRATION
==================================

GUI components for displaying plugin confidence and safety information
in the Lyrixa interface. Provides visual indicators, warnings, and 
interactive confidence dashboards.

Features:
- Real-time confidence scoring display
- Visual risk level indicators  
- Interactive safety warnings
- Plugin recommendation system
- Confidence trends dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

# Import confidence system
try:
    from lyrixa.core.plugin_confidence_system import PluginScorer
    from lyrixa.core.plugin_confidence_integration import ConfidenceEnhancedPluginSystem
    CONFIDENCE_SYSTEM_AVAILABLE = True
except ImportError:
    CONFIDENCE_SYSTEM_AVAILABLE = False


class PluginConfidenceWidget(ttk.Frame):
    """Widget for displaying plugin confidence information."""
    
    def __init__(self, parent, plugin_name: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.plugin_name = plugin_name
        self.confidence_score = 0.0
        self.risk_level = "UNKNOWN"
        self.safety_score = 0.0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the confidence widget UI."""
        
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Plugin name label
        self.name_label = ttk.Label(main_frame, text=self.plugin_name, 
                                   font=('Arial', 10, 'bold'))
        self.name_label.pack(anchor='w')
        
        # Confidence score frame
        score_frame = ttk.Frame(main_frame)
        score_frame.pack(fill='x', pady=2)
        
        ttk.Label(score_frame, text="Confidence:").pack(side='left')
        
        self.confidence_bar = ttk.Progressbar(score_frame, mode='determinate')
        self.confidence_bar.pack(side='left', fill='x', expand=True, padx=5)
        
        self.confidence_label = ttk.Label(score_frame, text="0%")
        self.confidence_label.pack(side='right')
        
        # Risk indicator
        risk_frame = ttk.Frame(main_frame)
        risk_frame.pack(fill='x', pady=2)
        
        ttk.Label(risk_frame, text="Risk Level:").pack(side='left')
        self.risk_label = ttk.Label(risk_frame, text="UNKNOWN")
        self.risk_label.pack(side='right')
        
        # Details button
        self.details_button = ttk.Button(main_frame, text="Details", 
                                        command=self.show_details)
        self.details_button.pack(pady=2)
        
    def update_confidence(self, confidence_score: float, risk_level: str, 
                         safety_score: float, analysis: Optional[Dict] = None):
        """Update the confidence display."""
        
        self.confidence_score = confidence_score
        self.risk_level = risk_level
        self.safety_score = safety_score
        self.analysis = analysis
        
        # Update progress bar
        self.confidence_bar['value'] = confidence_score * 100
        
        # Update confidence label
        self.confidence_label.config(text=f"{confidence_score:.1%}")
        
        # Update risk label with color coding
        self.risk_label.config(text=risk_level)
        
        if risk_level == 'CRITICAL':
            self.risk_label.config(foreground='red')
        elif risk_level == 'HIGH':
            self.risk_label.config(foreground='orange')
        elif risk_level == 'MEDIUM':
            self.risk_label.config(foreground='yellow')
        else:
            self.risk_label.config(foreground='green')
    
    def show_details(self):
        """Show detailed confidence analysis."""
        if hasattr(self, 'analysis') and self.analysis:
            ConfidenceDetailsDialog(self, self.plugin_name, self.analysis)
        else:
            messagebox.showinfo("Details", f"No detailed analysis available for {self.plugin_name}")


class ConfidenceDetailsDialog:
    """Dialog showing detailed confidence analysis."""
    
    def __init__(self, parent, plugin_name: str, analysis: Dict):
        self.parent = parent
        self.plugin_name = plugin_name
        self.analysis = analysis
        
        self.create_dialog()
        
    def create_dialog(self):
        """Create the details dialog."""
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Confidence Analysis - {self.plugin_name}")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Overview tab
        self.create_overview_tab(notebook)
        
        # Safety analysis tab
        self.create_safety_tab(notebook)
        
        # Runtime metrics tab
        self.create_runtime_tab(notebook)
        
        # Recommendations tab
        self.create_recommendations_tab(notebook)
        
        # Close button
        close_button = ttk.Button(self.dialog, text="Close", 
                                 command=self.dialog.destroy)
        close_button.pack(pady=5)
    
    def create_overview_tab(self, notebook):
        """Create overview tab."""
        
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Overview")
        
        # Confidence score
        ttk.Label(frame, text="Overall Confidence Score:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        ttk.Label(frame, text=f"{self.analysis['confidence_score']:.1%}", 
                 font=('Arial', 14)).pack(anchor='w', padx=20)
        
        # Risk level
        ttk.Label(frame, text="Risk Level:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        risk_level = self.analysis['safety_analysis']['risk_level']
        ttk.Label(frame, text=risk_level, font=('Arial', 14)).pack(anchor='w', padx=20)
        
        # Safety score
        ttk.Label(frame, text="Safety Score:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        safety_score = self.analysis['safety_analysis']['safety_score']
        ttk.Label(frame, text=f"{safety_score:.1f}/100", 
                 font=('Arial', 14)).pack(anchor='w', padx=20)
        
        # Timestamp
        ttk.Label(frame, text="Analysis Time:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        ttk.Label(frame, text=self.analysis['timestamp'], 
                 font=('Arial', 10)).pack(anchor='w', padx=20)
    
    def create_safety_tab(self, notebook):
        """Create safety analysis tab."""
        
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Safety Analysis")
        
        # Create scrollable text area
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_area = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap='word')
        text_area.pack(fill='both', expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Add safety analysis content
        safety = self.analysis['safety_analysis']
        
        text_area.insert('end', f"Safety Score: {safety['safety_score']:.1f}/100\\n\\n")
        text_area.insert('end', f"Risk Level: {safety['risk_level']}\\n\\n")
        
        if safety['issues']:
            text_area.insert('end', "ISSUES FOUND:\\n")
            for i, issue in enumerate(safety['issues'], 1):
                text_area.insert('end', f"{i}. {issue['type']} ({issue['severity']})\\n")
                text_area.insert('end', f"   {issue['message']}\\n")
                if 'line' in issue:
                    text_area.insert('end', f"   Line: {issue['line']}\\n")
                text_area.insert('end', "\\n")
        
        if safety['warnings']:
            text_area.insert('end', "WARNINGS:\\n")
            for i, warning in enumerate(safety['warnings'], 1):
                text_area.insert('end', f"{i}. {warning['type']} ({warning['severity']})\\n")
                text_area.insert('end', f"   {warning['message']}\\n")
                text_area.insert('end', "\\n")
        
        text_area.config(state='disabled')
    
    def create_runtime_tab(self, notebook):
        """Create runtime metrics tab."""
        
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Runtime Metrics")
        
        metrics = self.analysis.get('runtime_metrics', {})
        
        if metrics:
            ttk.Label(frame, text=f"Total Executions: {metrics.get('total_executions', 0)}", 
                     font=('Arial', 10)).pack(anchor='w', pady=2)
            ttk.Label(frame, text=f"Success Rate: {metrics.get('success_rate', 0):.1%}", 
                     font=('Arial', 10)).pack(anchor='w', pady=2)
            ttk.Label(frame, text=f"Average Execution Time: {metrics.get('avg_execution_time', 0):.3f}s", 
                     font=('Arial', 10)).pack(anchor='w', pady=2)
            ttk.Label(frame, text=f"Error Frequency: {metrics.get('error_frequency', 0):.1%}", 
                     font=('Arial', 10)).pack(anchor='w', pady=2)
        else:
            ttk.Label(frame, text="No runtime metrics available", 
                     font=('Arial', 10)).pack(anchor='w', pady=20)
    
    def create_recommendations_tab(self, notebook):
        """Create recommendations tab."""
        
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Recommendations")
        
        recommendations = self.analysis.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                ttk.Label(frame, text=f"{i}. {rec['type']}", 
                         font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
                ttk.Label(frame, text=f"   {rec['message']}", 
                         font=('Arial', 10)).pack(anchor='w', padx=20)
        else:
            ttk.Label(frame, text="No recommendations available", 
                     font=('Arial', 10)).pack(anchor='w', pady=20)


class PluginConfidenceDashboard(ttk.Frame):
    """Main dashboard for plugin confidence management."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        if CONFIDENCE_SYSTEM_AVAILABLE:
            self.confidence_system = ConfidenceEnhancedPluginSystem()
        else:
            self.confidence_system = None
        
        self.plugin_widgets = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dashboard UI."""
        
        # Title
        title_label = ttk.Label(self, text="Plugin Confidence Dashboard", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Refresh All", 
                  command=self.refresh_all).pack(side='left', padx=5)
        ttk.Button(toolbar, text="Export Report", 
                  command=self.export_report).pack(side='left', padx=5)
        
        # Scrollable plugin list
        self.create_plugin_list()
        
    def create_plugin_list(self):
        """Create scrollable list of plugin confidence widgets."""
        
        # Main frame with scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def add_plugin_widget(self, plugin_name: str) -> PluginConfidenceWidget:
        """Add a plugin confidence widget to the dashboard."""
        
        widget = PluginConfidenceWidget(self.scrollable_frame, plugin_name)
        widget.pack(fill='x', pady=2)
        
        self.plugin_widgets[plugin_name] = widget
        return widget
        
    def update_plugin_confidence(self, plugin_name: str, analysis: Dict):
        """Update confidence display for a plugin."""
        
        if plugin_name not in self.plugin_widgets:
            self.add_plugin_widget(plugin_name)
            
        widget = self.plugin_widgets[plugin_name]
        widget.update_confidence(
            analysis['confidence_score'],
            analysis['safety_analysis']['risk_level'],
            analysis['safety_analysis']['safety_score'],
            analysis
        )
    
    def refresh_all(self):
        """Refresh confidence analysis for all plugins."""
        messagebox.showinfo("Refresh", "Refreshing all plugin confidence data...")
        
    def export_report(self):
        """Export confidence report to file."""
        messagebox.showinfo("Export", "Exporting confidence report...")


# Demo application
def main():
    """Demo the plugin confidence GUI components."""
    
    root = tk.Tk()
    root.title("Plugin Confidence System - GUI Demo")
    root.geometry("800x600")
    
    # Create dashboard
    dashboard = PluginConfidenceDashboard(root)
    dashboard.pack(fill='both', expand=True)
    
    # Add some demo data
    demo_plugins = [
        {
            'name': 'Text Processor',
            'confidence': 0.95,
            'risk': 'LOW',
            'safety': 98.0
        },
        {
            'name': 'File Manager',
            'confidence': 0.65,
            'risk': 'MEDIUM',
            'safety': 75.0
        },
        {
            'name': 'Network Client',
            'confidence': 0.35,
            'risk': 'HIGH',
            'safety': 40.0
        }
    ]
    
    for plugin in demo_plugins:
        analysis = {
            'confidence_score': plugin['confidence'],
            'safety_analysis': {
                'risk_level': plugin['risk'],
                'safety_score': plugin['safety'],
                'issues': [],
                'warnings': []
            },
            'runtime_metrics': {
                'total_executions': 100,
                'success_rate': 0.95,
                'avg_execution_time': 0.1,
                'error_frequency': 0.05
            },
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        dashboard.update_plugin_confidence(plugin['name'], analysis)
    
    root.mainloop()


if __name__ == "__main__":
    main()
