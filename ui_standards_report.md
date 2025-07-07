# UI Standards Verification Report

Total issues found: 286

## Emoji Issues: 283

| File | Line | Content |
| ---- | ---- | ------- |
| analytics_dashboard.py | 559 | `title_label = QLabel("📊 Analytics Dashboard")` |
| analytics_dashboard.py | 566 | `self.refresh_btn = QPushButton("🔄 Refresh")` |
| analytics_dashboard.py | 570 | `self.export_btn = QPushButton("📊 Export")` |
| analytics_dashboard.py | 624 | `prod_group = QGroupBox("🎯 Productivity Metrics")` |
| analytics_dashboard.py | 643 | `pattern_group = QGroupBox("🔍 Pattern Analysis")` |
| analytics_dashboard.py | 661 | `suggestion_group = QGroupBox("💡 Suggestion Effe...` |
| analytics_dashboard.py | 693 | `tab_widget.addTab(self.productivity_chart, "📈 P...` |
| analytics_dashboard.py | 697 | `tab_widget.addTab(self.pattern_chart, "🔍 Patter...` |
| analytics_dashboard.py | 701 | `tab_widget.addTab(self.suggestion_chart, "💡 Sug...` |
| configuration_manager_old.py | 582 | `export_btn = QPushButton("📊 Export All Settings")` |
| configuration_manager_old.py | 586 | `export_partial_btn = QPushButton("📄 Export User...` |
| configuration_manager_old.py | 597 | `import_btn = QPushButton("📥 Import Settings")` |
| configuration_manager_old.py | 608 | `backup_btn = QPushButton("💾 Create Backup")` |
| configuration_manager_old.py | 612 | `restore_btn = QPushButton("🔄 Restore from Backup")` |
| configuration_manager_old.py | 628 | `reset_btn = QPushButton("🔄 Reset to Defaults")` |
| configuration_manager_old.py | 907 | `header_label = QLabel("⚙️ Configuration Manager")` |
| configuration_manager_old.py | 918 | `self.tab_widget.addTab(self.preferences_tab, "👤...` |
| configuration_manager_old.py | 923 | `self.tab_widget.addTab(self.anticipation_tab, "...` |
| configuration_manager_old.py | 927 | `self.tab_widget.addTab(self.data_tab, "💾 Data M...` |
| configuration_manager_old.py | 934 | `save_btn = QPushButton("💾 Save Changes")` |
| configuration_manager_old.py | 938 | `apply_btn = QPushButton("✅ Apply Settings")` |
| configuration_manager_old.py | 944 | `cancel_btn = QPushButton("❌ Discard Changes")` |
| debug_console_widget.py | 2 | `🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET` |
| debug_console_widget.py | 45 | `🐛🔍 LYRIXA DEBUG CONSOLE GUI WIDGET` |
| debug_console_widget.py | 84 | `🐛🔍 Debug Console Widget` |
| debug_console_widget.py | 103 | `self.setWindowTitle("🐛 Lyrixa Debug Console")` |
| debug_console_widget.py | 114 | `title_label = QLabel("🐛🔍 Lyrixa Debug Console")` |
| debug_console_widget.py | 133 | `self.export_btn = QPushButton("📁 Export Session")` |
| debug_console_widget.py | 138 | `self.clear_btn = QPushButton("🗑️ Clear History")` |
| debug_console_widget.py | 149 | `self.cognitive_state_label = QLabel("😴 IDLE")` |
| debug_console_widget.py | 182 | `current_group = QGroupBox("👁️ Current Perception")` |
| debug_console_widget.py | 202 | `history_group = QGroupBox("📊 Perception History")` |
| debug_console_widget.py | 214 | `self.tab_widget.addTab(tab, "👁️ Perception")` |
| debug_console_widget.py | 222 | `current_group = QGroupBox("🧠 Current Thought Pr...` |
| debug_console_widget.py | 238 | `history_group = QGroupBox("📚 Thought History")` |
| debug_console_widget.py | 249 | `self.tab_widget.addTab(tab, "🧠 Thoughts")` |
| debug_console_widget.py | 257 | `matrix_group = QGroupBox("⚖️ Decision Matrix")` |
| debug_console_widget.py | 268 | `recent_group = QGroupBox("📋 Recent Decisions")` |
| debug_console_widget.py | 279 | `self.tab_widget.addTab(tab, "⚖️ Decisions")` |
| debug_console_widget.py | 287 | `metrics_group = QGroupBox("📊 Performance Metrics")` |
| debug_console_widget.py | 314 | `logs_group = QGroupBox("📈 Performance Logs")` |
| debug_console_widget.py | 325 | `self.tab_widget.addTab(tab, "📊 Performance")` |
| debug_console_widget.py | 343 | `"idle": "😴",` |
| debug_console_widget.py | 344 | `"analyzing": "🔍",` |
| debug_console_widget.py | 345 | `"reasoning": "🧠",` |
| debug_console_widget.py | 346 | `"deciding": "⚖️",` |
| debug_console_widget.py | 347 | `"executing": "⚡",` |
| debug_console_widget.py | 348 | `"learning": "📚",` |
| debug_console_widget.py | 349 | `"reflecting": "💭",` |
| debug_console_widget.py | 352 | `emoji = state_emoji.get(state.value, "🤖")` |
| debug_console_widget.py | 399 | `f"✅ Completed: {latest_thought.final_decision}"` |
| debug_console_widget.py | 403 | `f"🔄 Active: {latest_thought.thought_id}"` |
| debug_console_widget.py | 432 | `status = "✅" if thought.final_decision else "🔄"` |
| debug_console_widget.py | 467 | `matrix_text += f"🎯 Latest Decision Matrix ({tho...` |
| debug_console_widget.py | 475 | `"🥇"` |
| debug_console_widget.py | 477 | `else "🥈"` |
| debug_console_widget.py | 479 | `else "🥉"` |
| debug_console_widget.py | 481 | `else "📋"` |
| debug_console_widget.py | 549 | `print(f"🐛 Debug level changed to: {level.name}")` |
| debug_console_widget.py | 551 | `print(f"🐛 Invalid debug level: {level_name}")` |
| debug_console_widget.py | 557 | `print(f"🐛 Debug session exported to: {filepath}")` |
| debug_console_widget.py | 566 | `print("🐛 Debug history cleared")` |
| debug_console_widget.py | 582 | `print("🐛 Debug Console: Running in headless mode")` |
| debug_console_widget.py | 589 | `🐛 **DEBUG CONSOLE STATUS**` |
| debug_console_widget.py | 603 | `🧠 **LATEST THOUGHT PROCESS**` |
| debug_console_widget.py | 613 | `print(f"\n✅ Final Decision: {analysis['final_de...` |
| enhanced_analytics.py | 128 | `header = QLabel("📊 Real-Time Productivity Monit...` |
| enhanced_analytics.py | 160 | `self.energy_indicator = self.create_trend_indic...` |
| enhanced_analytics.py | 161 | `self.creativity_indicator = self.create_trend_i...` |
| enhanced_analytics.py | 162 | `self.balance_indicator = self.create_trend_indi...` |
| enhanced_analytics.py | 171 | `insights_group = QGroupBox("💡 Quick Insights")` |
| enhanced_analytics.py | 234 | `if trend == "↗":` |
| enhanced_analytics.py | 236 | `elif trend == "↘":` |
| enhanced_analytics.py | 295 | `insights.append("🎯 Excellent focus! You're in t...` |
| enhanced_analytics.py | 297 | `insights.append("⚠️ Focus seems low. Consider a...` |
| enhanced_analytics.py | 300 | `insights.append("🏆 Great progress on your goals!")` |
| enhanced_analytics.py | 302 | `insights.append("📈 Consider reviewing your goal...` |
| enhanced_analytics.py | 305 | `insights.append("😊 Mood is stable and positive.")` |
| enhanced_analytics.py | 307 | `insights.append("🌱 Mood fluctuations detected. ...` |
| enhanced_analytics.py | 310 | `insights.append("📊 All metrics looking good!")` |
| enhanced_analytics.py | 346 | `header = QLabel("🤖 Agent Usage & Optimization")` |
| enhanced_analytics.py | 386 | `features_group = QGroupBox("🎯 Feature Usage Bre...` |
| enhanced_analytics.py | 401 | `recommendations_group = QGroupBox("💡 Optimizati...` |
| enhanced_analytics.py | 473 | `"• High error rate detected. Consider reviewing...` |
| enhanced_analytics.py | 478 | `"• Response times are elevated. Check system pe...` |
| enhanced_analytics.py | 483 | `"• User satisfaction could be improved. Review ...` |
| enhanced_analytics.py | 492 | `f"• Most used feature: {max_feature[0]} ({max_f...` |
| enhanced_analytics.py | 495 | `f"• Least used feature: {min_feature[0]} ({min_...` |
| enhanced_analytics.py | 498 | `"• Consider promoting underutilized features or...` |
| enhanced_analytics.py | 503 | `"• All metrics look good! Keep up the excellent...` |
| enhanced_analytics.py | 528 | `header = QLabel("📈 Lyrixa Enhanced Analytics Da...` |
| enhanced_analytics.py | 539 | `tab_widget.addTab(productivity_widget, "📊 Real-...` |
| enhanced_analytics.py | 543 | `tab_widget.addTab(agent_widget, "🤖 Agent Analyt...` |
| enhanced_analytics.py | 546 | `goals_widget = QLabel("🎯 Goals & Achievements a...` |
| enhanced_analytics.py | 549 | `tab_widget.addTab(goals_widget, "🎯 Goals & Achi...` |
| enhanced_analytics.py | 552 | `patterns_widget = QLabel("🧠 Behavioral Patterns...` |
| enhanced_analytics.py | 555 | `tab_widget.addTab(patterns_widget, "🧠 Behaviora...` |
| enhanced_analytics.py | 562 | `refresh_btn = QPushButton("🔄 Refresh Data")` |
| enhanced_analytics.py | 566 | `export_btn = QPushButton("📊 Export Report")` |
| enhanced_lyrixa.py | 52 | `print("🎙️ Enhanced Lyrixa Window initialized")` |
| enhanced_lyrixa.py | 81 | `print("✅ Enhanced Lyrixa Window ready with Phas...` |
| enhanced_lyrixa.py | 119 | `print("✅ Qt GUI framework detected")` |
| enhanced_lyrixa.py | 122 | `print("⚠️ PySide6 not available - running in co...` |
| enhanced_lyrixa.py | 143 | `print("✅ Real Lyrixa AI system initialized")` |
| enhanced_lyrixa.py | 152 | `print(f"⚠️ Could not initialize Lyrixa AI: {e}")` |
| enhanced_lyrixa.py | 168 | `print("🐛 Debug Console widget initialized")` |
| enhanced_lyrixa.py | 169 | `print("   ✅ Real-time cognitive state monitoring")` |
| enhanced_lyrixa.py | 170 | `print("   ✅ Thought process introspection")` |
| enhanced_lyrixa.py | 171 | `print("   ✅ Decision matrix analysis")` |
| enhanced_lyrixa.py | 174 | `print(f"⚠️ Could not initialize Debug Console: ...` |
| enhanced_lyrixa.py | 189 | `print("🧠 Phase 1 Advanced Memory System integra...` |
| enhanced_lyrixa.py | 190 | `print("   ✅ Vector embeddings enabled")` |
| enhanced_lyrixa.py | 191 | `print("   ✅ Confidence modeling active")` |
| enhanced_lyrixa.py | 192 | `print("   ✅ Reflexive analysis ready")` |
| enhanced_lyrixa.py | 199 | `print(f"⚠️ Could not initialize Advanced Memory...` |
| enhanced_lyrixa.py | 209 | `print("🔮 Anticipation Engine initialized")` |
| enhanced_lyrixa.py | 212 | `print("ℹ️ Phase 3 GUI components will be initia...` |
| enhanced_lyrixa.py | 215 | `print(f"⚠️ Error in Phase 3 initialization: {e}")` |
| enhanced_lyrixa.py | 221 | `print("ℹ️ Phase 3 GUI components not available")` |
| enhanced_lyrixa.py | 226 | `print("📊 Analytics Dashboard initialized")` |
| enhanced_lyrixa.py | 230 | `print("💡 Suggestion Notification System initial...` |
| enhanced_lyrixa.py | 234 | `print("⚙️ Configuration Manager initialized")` |
| enhanced_lyrixa.py | 238 | `print("⚡ Performance Monitor initialized")` |
| enhanced_lyrixa.py | 242 | `print("🧠 Intelligence Layer Widget initialized")` |
| enhanced_lyrixa.py | 248 | `print("✅ Phase 3 GUI components integrated succ...` |
| enhanced_lyrixa.py | 251 | `print(f"⚠️ Error initializing Phase 3 GUI compo...` |
| enhanced_lyrixa.py | 263 | `print("🔗 Connecting anticipation engine to noti...` |
| enhanced_lyrixa.py | 270 | `print("✅ Anticipation engine connected to notif...` |
| enhanced_lyrixa.py | 273 | `print(f"⚠️ Error connecting anticipation to not...` |
| enhanced_lyrixa.py | 310 | `print("🐛 Debug console not available")` |
| enhanced_lyrixa.py | 388 | `print("✅ Enhanced main window layout created")` |
| enhanced_lyrixa.py | 424 | `header = QLabel("🧠 Memory Graph - Live Context")` |
| enhanced_lyrixa.py | 435 | `"Memory graph will display here...\n• Semantic ...` |
| enhanced_lyrixa.py | 455 | `header = QLabel("🤔 Lyrixa Thinks... (Live Feed)")` |
| enhanced_lyrixa.py | 474 | `self.think_feed.append("🚀 Lyrixa system startin...` |
| enhanced_lyrixa.py | 475 | `self.think_feed.append("🧠 Memory system initial...` |
| enhanced_lyrixa.py | 476 | `self.think_feed.append("🔮 Anticipation engine r...` |
| enhanced_lyrixa.py | 478 | `self.think_feed.append("📊 Analytics dashboard a...` |
| enhanced_lyrixa.py | 480 | `self.think_feed.append("💡 Notification system r...` |
| enhanced_lyrixa.py | 497 | `tab_widget.addTab(feedback_tab, "📡 Live Feedback")` |
| enhanced_lyrixa.py | 501 | `tab_widget.addTab(suggestions_tab, "💡 Suggestio...` |
| enhanced_lyrixa.py | 505 | `tab_widget.addTab(analytics_tab, "📊 Analytics")` |
| enhanced_lyrixa.py | 509 | `tab_widget.addTab(config_tab, "⚙️ Config")` |
| enhanced_lyrixa.py | 513 | `tab_widget.addTab(performance_tab, "⚡ Performan...` |
| enhanced_lyrixa.py | 638 | `self.sync_status_label = QLabel("Sync: ✅ Active")` |
| enhanced_lyrixa.py | 670 | `print("⏱️ Real-time updates activated (2s inter...` |
| enhanced_lyrixa.py | 719 | `print(f"⚠️ Real-time update error: {e}")` |
| enhanced_lyrixa.py | 748 | `print(f"⚠️ Component update error: {e}")` |
| enhanced_lyrixa.py | 754 | `print("🔄 Initializing Phase 4 state management....` |
| enhanced_lyrixa.py | 767 | `print("✅ Phase 4 state management initialized")` |
| enhanced_lyrixa.py | 769 | `print(f"⚠️ Phase 4 initialization error: {e}")` |
| enhanced_lyrixa.py | 774 | `print("👁️ Enhanced Lyrixa Window shown - activa...` |
| enhanced_lyrixa.py | 789 | `print(f"⚠️ Show activation error: {e}")` |
| enhanced_lyrixa.py | 794 | `print("🔄 Shutting down Phase 4 components...")` |
| enhanced_lyrixa.py | 810 | `print("✅ Phase 4 components shut down gracefully")` |
| enhanced_lyrixa.py | 812 | `print(f"⚠️ Shutdown error: {e}")` |
| enhanced_lyrixa.py | 825 | `print("🔗 Memory bindings established")` |
| enhanced_lyrixa.py | 827 | `print(f"⚠️ Memory binding error: {e}")` |
| enhanced_lyrixa.py | 833 | `print("⏱️ Real-time updates started")` |
| enhanced_lyrixa.py | 835 | `print(f"⚠️ Real-time update start error: {e}")` |
| enhanced_lyrixa.py | 841 | `print("⏹️ Real-time updates stopped")` |
| enhanced_lyrixa.py | 843 | `print(f"⚠️ Real-time update stop error: {e}")` |
| enhanced_lyrixa.py | 849 | `print("💾 Phase 4 state saved")` |
| enhanced_lyrixa.py | 851 | `print(f"⚠️ State save error: {e}")` |
| enhanced_lyrixa.py | 902 | `print("⚠️ Failed to create Qt window - falling ...` |
| enhanced_lyrixa.py | 912 | `print("🔄 Closing Enhanced Lyrixa Window...")` |
| enhanced_lyrixa.py | 924 | `print("✅ Enhanced Lyrixa Window closed")` |
| intelligence_layer.py | 206 | `header = QLabel("🧠 Memory Context Graph")` |
| intelligence_layer.py | 240 | `self.auto_layout_btn = QPushButton("🔄 Auto Layo...` |
| intelligence_layer.py | 244 | `self.filter_btn = QPushButton("🎯 Filter Nodes")` |
| intelligence_layer.py | 248 | `self.cluster_btn = QPushButton("🔗 Auto Cluster")` |
| intelligence_layer.py | 253 | `self.zoom_in_btn = QPushButton("🔍 Zoom In")` |
| intelligence_layer.py | 257 | `self.zoom_out_btn = QPushButton("🔍 Zoom Out")` |
| intelligence_layer.py | 261 | `self.reset_view_btn = QPushButton("🎯 Reset View")` |
| intelligence_layer.py | 482 | `self.header_label = QLabel("🤔 Lyrixa Thinks...")` |
| intelligence_layer.py | 487 | `self.thinking_indicator = QLabel("●")` |
| intelligence_layer.py | 585 | `self.thoughts_area.setText("💭 Waiting for conte...` |
| intelligence_layer.py | 594 | `confidence_bar = "▓" * int(thought.confidence *...` |
| intelligence_layer.py | 604 | `thoughts_text += f"    → {', '.join(thought.sug...` |
| intelligence_layer.py | 665 | `header = QLabel("📅 Interaction Timeline")` |
| intelligence_layer.py | 692 | `label = QLabel(f"● {mood.title()}")` |
| intelligence_layer.py | 793 | `header_label = QLabel("🧠 Lyrixa Intelligence La...` |
| intelligence_layer.py | 955 | `print("🧪 Testing GUI Intelligence Layer")` |
| intelligence_layer.py | 959 | `print("⚠️ PySide6 not available - GUI test skip...` |
| intelligence_layer.py | 971 | `print("✅ Intelligence Layer created and display...` |
| intelligence_layer.py | 972 | `print("📊 Demo data generation started")` |
| intelligence_layer.py | 973 | `print("🔄 Live thinking animation active")` |
| live_feedback_loop.py | 654 | `{"type": "thumbs_up", "label": "👍", "action": "...` |
| live_feedback_loop.py | 655 | `{"type": "thumbs_down", "label": "👎", "action":...` |
| live_feedback_loop.py | 656 | `{"type": "edit", "label": "✏️", "action": "edit...` |
| live_feedback_loop.py | 657 | `{"type": "dismiss", "label": "✖️", "action": "d...` |
| performance_monitor.py | 382 | `self.status_label = QLabel("●")` |
| performance_monitor.py | 426 | `header_label = QLabel("📊 Detailed Metrics")` |
| performance_monitor.py | 496 | `header_label = QLabel("🗃️ Database Performance")` |
| performance_monitor.py | 516 | `test_btn = QPushButton("🔍 Test Database Perform...` |
| performance_monitor.py | 635 | `title_label = QLabel("⚡ Performance Monitor")` |
| performance_monitor.py | 646 | `self.start_btn = QPushButton("▶ Start")` |
| performance_monitor.py | 650 | `self.stop_btn = QPushButton("⏸ Stop")` |
| suggestion_notifications.py | 137 | `priority_label = QLabel("●")` |
| suggestion_notifications.py | 170 | `accept_btn = QPushButton("✓ Accept")` |
| suggestion_notifications.py | 189 | `reject_btn = QPushButton("✗ Reject")` |
| suggestion_notifications.py | 208 | `dismiss_btn = QPushButton("— Later")` |
| suggestion_notifications.py | 303 | `header_label = QLabel("💡 Suggestions")` |
| suggestion_notifications.py | 479 | `header_label = QLabel("📋 Suggestion History")` |
| suggestion_notifications.py | 504 | `"✓" if suggestion.accepted else "✗" if suggesti...` |
| web_mobile_support.py | 496 | `f"🏆 Achievement Unlocked!",` |
| web_mobile_support.py | 505 | `"💡 Smart Suggestion",` |
| web_mobile_support.py | 524 | `{"id": "quick_note", "label": "Quick Note", "ic...` |
| web_mobile_support.py | 525 | `{"id": "break_reminder", "label": "Schedule Bre...` |
| web_mobile_support.py | 526 | `{"id": "focus_mode", "label": "Focus Mode", "ic...` |
| web_mobile_support.py | 527 | `{"id": "sync_now", "label": "Sync Now", "icon":...` |
| unified\context_bridge.py | 9 | `- Phase 1 Memory → Phase 4 Intelligence: semant...` |
| unified\context_bridge.py | 10 | `- Phase 2 Anticipation → Phase 3 Notifications:...` |
| unified\context_bridge.py | 11 | `- Phase 3 Performance Monitor → Phase 4 Analyti...` |
| unified\context_bridge.py | 12 | `- Phase 4 Feedback → Phase 2+1 Systems: user_pr...` |
| unified\context_bridge.py | 80 | `logger.info("🔗 ContextBridge initialized")` |
| unified\context_bridge.py | 87 | `logger.info(f"✅ Registered {phase_name} compone...` |
| unified\context_bridge.py | 93 | `logger.error(f"❌ Failed to register {phase_name...` |
| unified\context_bridge.py | 99 | `# Memory → Intelligence: semantic events, conte...` |
| unified\context_bridge.py | 105 | `# Anticipation → Notifications: pending suggest...` |
| unified\context_bridge.py | 116 | `# Performance → Analytics: resource trends, CPU...` |
| unified\context_bridge.py | 125 | `# Intelligence → Memory+Anticipation: user pref...` |
| unified\context_bridge.py | 134 | `logger.warning(f"⚠️ Binding setup failed for {p...` |
| unified\context_bridge.py | 141 | `logger.info(f"🔔 Subscribed to {event_type.value}")` |
| unified\context_bridge.py | 173 | `logger.error(f"❌ Event handler error: {e}")` |
| unified\context_bridge.py | 175 | `logger.debug(f"📡 Emitted {event_type.value}: {s...` |
| unified\context_bridge.py | 181 | `"""Handle Memory → Intelligence communication."""` |
| unified\context_bridge.py | 192 | `logger.debug("🧠 Memory → Intelligence data rout...` |
| unified\context_bridge.py | 194 | `logger.error(f"❌ Memory→Intelligence routing fa...` |
| unified\context_bridge.py | 197 | `"""Handle Anticipation → Notifications communic...` |
| unified\context_bridge.py | 208 | `logger.debug("🔮 Anticipation → Notifications da...` |
| unified\context_bridge.py | 210 | `logger.error(f"❌ Anticipation→Notifications rou...` |
| unified\context_bridge.py | 213 | `"""Handle Performance Monitor → Analytics commu...` |
| unified\context_bridge.py | 224 | `logger.debug("⚡ Performance → Analytics data ro...` |
| unified\context_bridge.py | 226 | `logger.error(f"❌ Performance→Analytics routing ...` |
| unified\context_bridge.py | 229 | `"""Handle Feedback → Memory+Anticipation commun...` |
| unified\context_bridge.py | 247 | `logger.debug("💭 Feedback → Systems data routed")` |
| unified\context_bridge.py | 249 | `logger.error(f"❌ Feedback→Systems routing faile...` |
| unified\context_bridge.py | 269 | `logger.error(f"❌ Memory preference update faile...` |
| unified\context_bridge.py | 287 | `logger.debug("🔄 Phase synchronization completed")` |
| unified\context_bridge.py | 290 | `logger.error(f"❌ Phase sync failed: {e}")` |
| unified\context_bridge.py | 349 | `f"🧹 Event history cleaned, kept {len(self.event...` |
| unified\main.py | 22 | `print("🚀 LYRIXA UNIFIED GUI LAUNCHER")` |
| unified\main.py | 32 | `print("✅ Qt GUI framework available")` |
| unified\main.py | 34 | `print("⚠️ Qt not available - will run in headle...` |
| unified\main.py | 44 | `print("✅ Lyrixa core components loaded")` |
| unified\main.py | 46 | `print(f"❌ Error importing Lyrixa components: {e}")` |
| unified\main.py | 73 | `print("🧠 Initializing Phase 1 Advanced Memory S...` |
| unified\main.py | 78 | `print("✅ Advanced Memory System ready")` |
| unified\main.py | 81 | `print(f"❌ Memory system initialization failed: ...` |
| unified\main.py | 87 | `print("🔮 Initializing Phase 2 Anticipation Engi...` |
| unified\main.py | 94 | `print("✅ Anticipation Engine ready")` |
| unified\main.py | 97 | `print(f"❌ Anticipation engine initialization fa...` |
| unified\main.py | 103 | `print("⚠️ Running in headless mode - no GUI ava...` |
| unified\main.py | 107 | `print("🖥️ Initializing Qt GUI Application...")` |
| unified\main.py | 125 | `print("✅ GUI Application ready")` |
| unified\main.py | 128 | `print(f"❌ GUI initialization failed: {e}")` |
| unified\main.py | 134 | `print("🔗 Setting up cross-phase communication...")` |
| unified\main.py | 190 | `print("✅ Cross-phase communication established")` |
| unified\main.py | 193 | `print(f"❌ Communication setup failed: {e}")` |
| unified\main.py | 199 | `print("⚠️ Real-time integration requires Qt - u...` |
| unified\main.py | 203 | `print("⏱️ Setting up real-time integration...")` |
| unified\main.py | 215 | `print("✅ Real-time integration active")` |
| unified\main.py | 218 | `print(f"❌ Real-time setup failed: {e}")` |
| unified\main.py | 250 | `print(f"⚠️ Real-time update error: {e}")` |
| unified\main.py | 255 | `print("🔄 Starting async initialization flow...")` |
| unified\main.py | 267 | `print("⚠️ GUI initialization failed - continuin...` |
| unified\main.py | 275 | `print("✅ All systems initialized successfully!")` |
| unified\main.py | 279 | `print(f"❌ Async initialization failed: {e}")` |
| unified\main.py | 286 | `print("❌ GUI components not available")` |
| unified\main.py | 290 | `print("🎨 Launching GUI mode...")` |
| unified\main.py | 294 | `print("🎉 Lyrixa GUI is now running!")` |
| unified\main.py | 301 | `print(f"👋 GUI closed with exit code: {exit_code}")` |
| unified\main.py | 305 | `print(f"❌ GUI execution failed: {e}")` |
| unified\main.py | 311 | `print("🖥️ Running in headless server mode...")` |
| unified\main.py | 329 | `print("\n🛑 Shutdown requested...")` |
| unified\main.py | 332 | `print("👋 Headless mode shutdown complete")` |
| unified\main.py | 336 | `print(f"❌ Headless execution failed: {e}")` |
| unified\main.py | 344 | `print("❌ Initialization failed")` |
| unified\main.py | 354 | `print(f"❌ Launch failed: {e}")` |
| unified\main.py | 376 | `print("🧪 Running initialization test...")` |
| unified\main.py | 379 | `print("✅ All systems initialized successfully!")` |
| unified\main.py | 382 | `print("❌ Initialization test failed!")` |

## Unsupported Css Issues: 1

| File | Line | Content |
| ---- | ---- | ------- |
| intelligence_layer.py | 555 | `background-color: qlineargradient(` |

## Chat Bubble Issues: 1

| File | Line | Content |
| ---- | ---- | ------- |
| enhanced_analytics.py | 206 | `border-radius: 50px;` |

## Inconsistent Spacing Issues: 1

| File | Line | Content |
| ---- | ---- | ------- |
| enhanced_analytics.py | 424 | `margin: 5px;` |

