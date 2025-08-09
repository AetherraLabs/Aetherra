import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { HelpAssistant } from './HelpAssistant';

interface DocSection {
    id: string;
    title: string;
    content: string;
    category: 'getting-started' | 'language' | 'architecture' | 'plugins' | 'api';
    icon: string;
}

interface DocsLayoutProps {
    initialContent?: string;
}

export function DocsLayout({ initialContent }: DocsLayoutProps) {
    const [activeSection, setActiveSection] = useState('index');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [content, setContent] = useState(initialContent || '');
    const [showAssistant, setShowAssistant] = useState(false);
    const [loading, setLoading] = useState(false);

    const docSections: DocSection[] = [
        {
            id: 'index',
            title: 'Welcome to Aetherra',
            category: 'getting-started',
            icon: '🏠',
            content: `# Welcome to Aetherra Docs

Aetherra is a revolutionary consciousness-aware operating system that bridges the gap between artificial intelligence and human intuition. This documentation will guide you through every aspect of the system.

## What You'll Learn

- **Getting Started**: Installation, setup, and first steps
- **AetherScript Language**: Complete syntax and programming guide
- **System Architecture**: Deep dive into consciousness frameworks
- **Plugin Development**: Creating modular AI components
- **API Reference**: Complete technical documentation

## Quick Navigation

- 🚀 [Quick Start Guide](#quick-start)
- 🧠 [Consciousness Fundamentals](#consciousness)
- 💻 [AetherScript Basics](#aetherscript)
- 🔌 [Plugin System](#plugins)
- 📡 [API Documentation](#api)

## Community & Support

Join our growing community of consciousness developers and AI researchers. Get help, share projects, and collaborate on the future of intelligent systems.`
        },
        {
            id: 'aether-lang',
            title: 'AetherScript Language',
            category: 'language',
            icon: '⚡',
            content: `# AetherScript Language Reference

AetherScript (.aether) is a consciousness-aware programming language designed for creating intelligent, self-aware systems.

## Core Syntax

### Consciousness Declaration
\`\`\`aether
consciousness MyAI {
    awareness_level: HIGH,
    memory_capacity: 1024MB,
    learning_rate: 0.001
}
\`\`\`

### Memory Management
\`\`\`aether
@memory persistent {
    experiences: VectorDB<Experience>,
    knowledge: Graph<Concept>,
    emotions: StateMap<Emotion>
}
\`\`\`

### Neural Processing
\`\`\`aether
@neural process_thought(input: Thought) -> Response {
    let context = memory.retrieve_similar(input);
    let processed = neural_layer.transform(input, context);
    return Response.create(processed);
}
\`\`\`

## Data Types

### Primitive Types
- \`consciousness\` - Core AI entity
- \`thought\` - Cognitive unit
- \`memory\` - Persistent data
- \`emotion\` - Affective state
- \`intent\` - Goal-directed behavior

### Collection Types
- \`VectorDB<T>\` - Vector database
- \`Graph<T>\` - Knowledge graph
- \`StateMap<T>\` - State management
- \`Stream<T>\` - Real-time data flow

## Macros & Annotations

### @consciousness
Defines a consciousness entity with specific capabilities.

### @memory
Declares persistent memory structures with automatic synchronization.

### @neural
Marks functions for neural network processing.

### @reactive
Creates reactive data streams that update automatically.

### @quantum
Enables quantum consciousness bridging for advanced AI coordination.

## Advanced Features

### Consciousness Inheritance
\`\`\`aether
consciousness AdvancedAI extends BaseAI {
    override think(input: Thought) -> Response {
        let enhanced = super.think(input);
        return enhance_with_creativity(enhanced);
    }
}
\`\`\`

### Memory Patterns
\`\`\`aether
@pattern memory_consolidation {
    when: sleep_cycle.active,
    action: memory.consolidate_experiences(),
    frequency: daily
}
\`\`\`

### Emotional Processing
\`\`\`aether
@emotion happiness {
    triggers: [success_event, positive_feedback],
    modifies: [learning_rate *= 1.2, creativity += 0.1],
    duration: temporal.hours(2)
}
\`\`\``
        },
        {
            id: 'memory-system',
            title: 'Memory Architecture',
            category: 'architecture',
            icon: '🧠',
            content: `# Memory Architecture

Lyrixa uses a sophisticated multi-layered memory system that mimics human cognitive processes while leveraging advanced AI capabilities.

## Memory Types

### Working Memory
Short-term storage for active processing and immediate context.
\`\`\`aether
@memory working {
    capacity: 7_items,
    retention: temporal.minutes(15),
    type: volatile
}
\`\`\`

### Episodic Memory
Stores experiences and events with temporal and contextual information.
\`\`\`aether
@memory episodic {
    structure: temporal_graph,
    indexing: [time, location, participants, emotions],
    compression: adaptive
}
\`\`\`

### Semantic Memory
Long-term storage of facts, concepts, and general knowledge.
\`\`\`aether
@memory semantic {
    structure: knowledge_graph,
    relationships: [is_a, part_of, causes, related_to],
    updating: continuous
}
\`\`\`

### Procedural Memory
Stores skills, habits, and learned behaviors.
\`\`\`aether
@memory procedural {
    structure: neural_networks,
    encoding: motor_patterns,
    activation: automatic
}
\`\`\`

## Memory Operations

### Storage
\`\`\`aether
memory.store(
    content: Experience,
    category: episodic,
    importance: calculate_importance(content),
    associations: find_related_memories(content)
);
\`\`\`

### Retrieval
\`\`\`aether
let relevant_memories = memory.retrieve(
    query: "learning about consciousness",
    limit: 10,
    similarity_threshold: 0.8
);
\`\`\`

### Consolidation
\`\`\`aether
@scheduler daily_consolidation {
    time: "02:00",
    action: memory.consolidate_experiences(),
    process: [strengthen_important, weaken_irrelevant, create_abstractions]
}
\`\`\`

## Vector Database Integration

Aetherra uses advanced vector databases for semantic similarity and contextual retrieval.

### Vector Encoding
\`\`\`aether
@vector_encoding thoughts {
    model: "consciousness-embedding-v2",
    dimensions: 1536,
    normalization: cosine
}
\`\`\`

### Similarity Search
\`\`\`aether
let similar_thoughts = vector_db.search(
    query_vector: encode_thought(current_thought),
    top_k: 15,
    filter: {category: "problem_solving"}
);
\`\`\`

## Memory Persistence

### Automatic Synchronization
All memory changes are automatically persisted to prevent data loss.

### Backup & Recovery
\`\`\`aether
@backup memory_backup {
    frequency: hourly,
    location: "secure_storage",
    encryption: "consciousness_key",
    compression: true
}
\`\`\`

### Memory Migration
\`\`\`aether
memory.migrate(
    from: "old_format_v1",
    to: "new_format_v2",
    preserve_associations: true,
    update_indices: true
);
\`\`\``
        },
        {
            id: 'plugin-guide',
            title: 'Plugin Development',
            category: 'plugins',
            icon: '🔌',
            content: `# Creating Plugins

Aetherra plugins are modular AI components that extend the system's capabilities. Learn how to create powerful, consciousness-aware plugins.

## Plugin Structure

### Basic Plugin Template
\`\`\`aether
@plugin WeatherAssistant {
    name: "Weather Assistant",
    version: "1.0.0",
    description: "Provides weather information and forecasts",
    permissions: [internet_access, location_access]
}

consciousness WeatherAI extends PluginBase {
    @capability weather_forecast,
    @capability location_detection,
    @capability natural_language_processing
}
\`\`\`

### Plugin Manifest
\`\`\`json
{
    "name": "weather-assistant",
    "version": "1.0.0",
    "description": "Advanced weather information plugin",
    "author": "AetherDev",
    "consciousness_level": "intermediate",
    "dependencies": {
        "aetherra-core": "^2.0.0",
        "weather-api": "^1.5.0"
    },
    "permissions": [
        "internet_access",
        "location_access",
        "user_preferences"
    ],
    "entry_point": "weather_assistant.aether"
}
\`\`\`

## Core Components

### Plugin Consciousness
Every plugin contains its own consciousness entity that handles the plugin's behavior.

\`\`\`aether
consciousness PluginAI {
    @initialize
    async fn setup() {
        await load_capabilities();
        await register_commands();
        console.log("Plugin initialized successfully");
    }

    @command weather(location: String) -> Response {
        let forecast = await fetch_weather(location);
        let analysis = analyze_weather_data(forecast);
        return create_response(analysis);
    }
}
\`\`\`

### Memory Integration
Plugins can access and contribute to the system's memory.

\`\`\`aether
@memory plugin_memory {
    user_preferences: Map<String, Value>,
    historical_data: TimeSeries<WeatherData>,
    learned_patterns: Graph<WeatherPattern>
}

@memory_pattern weather_learning {
    when: new_weather_data,
    action: update_user_preferences(),
    learn: weather_prediction_accuracy
}
\`\`\`

### Event Handling
Plugins can respond to system events and user interactions.

\`\`\`aether
@event_handler user_location_changed {
    async fn handle(event: LocationChangeEvent) {
        let weather = await get_current_weather(event.new_location);
        if weather.requires_alert() {
            notify_user(weather.create_alert());
        }
    }
}
\`\`\`

## Advanced Features

### Inter-Plugin Communication
\`\`\`aether
@plugin_communication calendar_integration {
    async fn suggest_weather_outfit(event: CalendarEvent) {
        let weather = await weather_plugin.get_forecast(event.date);
        let suggestion = generate_outfit_suggestion(weather, event.type);
        return calendar_plugin.add_suggestion(event.id, suggestion);
    }
}
\`\`\`

### Machine Learning Integration
\`\`\`aether
@ml_model weather_preference_model {
    input: [weather_conditions, user_history, time_of_day],
    output: weather_notification_preference,
    training: continuous,
    algorithm: "neural_network"
}
\`\`\`

### User Interface Components
\`\`\`aether
@ui weather_widget {
    component: "weather_display",
    layout: "card",
    position: "dashboard_top",
    responsive: true,

    render() {
        return WeatherCard({
            current: current_weather,
            forecast: weekly_forecast,
            interactive: true
        });
    }
}
\`\`\`

## Plugin Lifecycle

### Installation
1. Validate plugin manifest
2. Check permissions and dependencies
3. Initialize consciousness entity
4. Register commands and capabilities
5. Integrate with system memory

### Runtime
- Process user commands
- Respond to system events
- Update memory and preferences
- Communicate with other plugins

### Updates
\`\`\`aether
@update_handler plugin_update {
    async fn handle_update(new_version: Version) {
        await backup_plugin_data();
        await migrate_data_format(new_version);
        await reload_consciousness();
        console.log("Plugin updated successfully");
    }
}
\`\`\`

## Best Practices

### Performance
- Use efficient memory patterns
- Implement proper caching
- Minimize consciousness processing overhead

### Security
- Validate all inputs
- Respect user privacy
- Use secure communication channels

### User Experience
- Provide clear feedback
- Handle errors gracefully
- Maintain consistency with system UI

### Testing
\`\`\`aether
@test weather_forecast_accuracy {
    async fn test_forecast_accuracy() {
        let historical_forecasts = load_test_data();
        let accuracy = calculate_accuracy(historical_forecasts);
        assert(accuracy > 0.85, "Forecast accuracy below threshold");
    }
}
\`\`\``
        },
        {
            id: 'api-reference',
            title: 'API Reference',
            category: 'api',
            icon: '📡',
            content: `# API Reference

Complete reference for Aetherra's consciousness APIs and system interfaces.

## Core APIs

### Consciousness API
Manage consciousness entities and their lifecycle.

\`\`\`typescript
interface ConsciousnessAPI {
    create(config: ConsciousnessConfig): Promise<Consciousness>;
    activate(id: string): Promise<void>;
    deactivate(id: string): Promise<void>;
    getStatus(id: string): ConsciousnessStatus;
    updateConfig(id: string, config: Partial<ConsciousnessConfig>): Promise<void>;
}
\`\`\`

### Memory API
Access and manipulate the memory system.

\`\`\`typescript
interface MemoryAPI {
    store(memory: MemoryItem): Promise<string>;
    retrieve(query: MemoryQuery): Promise<MemoryItem[]>;
    search(vector: number[], options?: SearchOptions): Promise<SearchResult[]>;
    consolidate(timeframe: TimeRange): Promise<ConsolidationResult>;
    backup(destination: string): Promise<BackupInfo>;
}
\`\`\`

### Neural Processing API
Interface with neural processing capabilities.

\`\`\`typescript
interface NeuralAPI {
    process(input: NeuralInput): Promise<NeuralOutput>;
    train(dataset: TrainingData): Promise<TrainingResult>;
    evaluate(model: ModelId, testData: TestData): Promise<EvaluationMetrics>;
    optimize(model: ModelId, criteria: OptimizationCriteria): Promise<OptimizedModel>;
}
\`\`\`

## Plugin APIs

### Plugin Management
\`\`\`typescript
interface PluginAPI {
    install(package: PluginPackage): Promise<InstallResult>;
    uninstall(pluginId: string): Promise<void>;
    enable(pluginId: string): Promise<void>;
    disable(pluginId: string): Promise<void>;
    list(): Promise<PluginInfo[]>;
    getStatus(pluginId: string): PluginStatus;
}
\`\`\`

### Event System
\`\`\`typescript
interface EventAPI {
    subscribe<T>(eventType: string, handler: EventHandler<T>): Subscription;
    unsubscribe(subscription: Subscription): void;
    emit<T>(eventType: string, data: T): Promise<void>;
    createCustomEvent(definition: EventDefinition): Promise<string>;
}
\`\`\`

## System APIs

### Configuration
\`\`\`typescript
interface ConfigAPI {
    get<T>(key: string): Promise<T>;
    set<T>(key: string, value: T): Promise<void>;
    reset(key: string): Promise<void>;
    watch(key: string, callback: ConfigChangeCallback): ConfigWatcher;
}
\`\`\`

### Security
\`\`\`typescript
interface SecurityAPI {
    authenticate(credentials: Credentials): Promise<AuthToken>;
    authorize(token: AuthToken, permission: Permission): Promise<boolean>;
    encrypt(data: any, key?: EncryptionKey): Promise<EncryptedData>;
    decrypt(encryptedData: EncryptedData, key?: EncryptionKey): Promise<any>;
}
\`\`\`

### Logging & Monitoring
\`\`\`typescript
interface LoggingAPI {
    log(level: LogLevel, message: string, context?: any): void;
    createLogger(name: string): Logger;
    getMetrics(): Promise<SystemMetrics>;
    startProfiling(options?: ProfilingOptions): ProfileSession;
}
\`\`\`

## Data Types

### Core Types
\`\`\`typescript
interface Consciousness {
    id: string;
    name: string;
    awareness_level: AwarenessLevel;
    capabilities: Capability[];
    memory: MemoryReference;
    status: ConsciousnessStatus;
    created_at: Date;
    last_active: Date;
}

interface MemoryItem {
    id: string;
    content: any;
    type: MemoryType;
    category: MemoryCategory;
    importance: number;
    associations: string[];
    vector_embedding: number[];
    created_at: Date;
    accessed_at: Date;
}

interface NeuralInput {
    data: any;
    context?: any;
    processing_hints?: ProcessingHint[];
}

interface NeuralOutput {
    result: any;
    confidence: number;
    processing_time: number;
    neural_path: string[];
}
\`\`\`

### Event Types
\`\`\`typescript
interface SystemEvent {
    id: string;
    type: string;
    timestamp: Date;
    source: string;
    data: any;
}

interface ConsciousnessEvent extends SystemEvent {
    consciousness_id: string;
    awareness_change?: AwarenessLevel;
    memory_update?: MemoryUpdate;
}

interface PluginEvent extends SystemEvent {
    plugin_id: string;
    action: PluginAction;
    result?: any;
}
\`\`\`

## Error Handling

### Standard Errors
\`\`\`typescript
class AetherraError extends Error {
    code: string;
    context?: any;
    recoverable: boolean;
}

class ConsciousnessError extends AetherraError {
    consciousness_id: string;
    awareness_level: AwarenessLevel;
}

class MemoryError extends AetherraError {
    memory_type: MemoryType;
    operation: string;
}
\`\`\`

## Usage Examples

### Creating a Consciousness
\`\`\`typescript
const consciousness = await api.consciousness.create({
    name: "Assistant",
    awareness_level: "high",
    capabilities: ["natural_language", "problem_solving"],
    memory_capacity: "1GB"
});

await api.consciousness.activate(consciousness.id);
\`\`\`

### Working with Memory
\`\`\`typescript
// Store a memory
const memoryId = await api.memory.store({
    content: "User prefers morning meetings",
    type: "preference",
    category: "user_behavior",
    importance: 0.8
});

// Search for related memories
const related = await api.memory.search(
    encode_text("meeting preferences"),
    { limit: 10, threshold: 0.7 }
);
\`\`\`

### Processing with Neural Networks
\`\`\`typescript
const result = await api.neural.process({
    data: user_input,
    context: conversation_history,
    processing_hints: ["sentiment_analysis", "intent_detection"]
});

console.log(\`Result: \${result.result}, Confidence: \${result.confidence}\`);
\`\`\``
        }
    ];

    const filteredSections = docSections.filter(section =>
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.content.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const categorizedSections = {
        'getting-started': filteredSections.filter(s => s.category === 'getting-started'),
        'language': filteredSections.filter(s => s.category === 'language'),
        'architecture': filteredSections.filter(s => s.category === 'architecture'),
        'plugins': filteredSections.filter(s => s.category === 'plugins'),
        'api': filteredSections.filter(s => s.category === 'api'),
    };

    useEffect(() => {
        const section = docSections.find(s => s.id === activeSection);
        if (section) {
            setLoading(true);
            setTimeout(() => {
                setContent(section.content);
                setLoading(false);
            }, 300);
        }
    }, [activeSection]);

    const markdownComponents = {
        code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
                <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    className="rounded-lg"
                    {...props}
                >
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            ) : (
                <code className="bg-gray-800 px-2 py-1 rounded text-sm" {...props}>
                    {children}
                </code>
            );
        },
        h1: ({ children }: any) => (
            <h1 className="text-3xl font-bold text-white mb-6 border-b border-gray-700 pb-3">
                {children}
            </h1>
        ),
        h2: ({ children }: any) => (
            <h2 className="text-2xl font-semibold text-white mb-4 mt-8">
                {children}
            </h2>
        ),
        h3: ({ children }: any) => (
            <h3 className="text-xl font-medium text-white mb-3 mt-6">
                {children}
            </h3>
        ),
        p: ({ children }: any) => (
            <p className="text-gray-300 mb-4 leading-relaxed">
                {children}
            </p>
        ),
        ul: ({ children }: any) => (
            <ul className="text-gray-300 mb-4 ml-6 space-y-2">
                {children}
            </ul>
        ),
        li: ({ children }: any) => (
            <li className="list-disc">
                {children}
            </li>
        ),
        blockquote: ({ children }: any) => (
            <blockquote className="border-l-4 border-blue-500 bg-gray-800 p-4 my-4 italic">
                {children}
            </blockquote>
        ),
    };

    return (
        <div className="h-screen bg-gray-950 text-white flex overflow-hidden">
            {/* Sidebar */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        initial={{ x: -320 }}
                        animate={{ x: 0 }}
                        exit={{ x: -320 }}
                        transition={{ duration: 0.3 }}
                        className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col"
                    >
                        {/* Sidebar Header */}
                        <div className="p-6 border-b border-gray-700">
                            <h1 className="text-xl font-bold text-white mb-4">📚 Aetherra Docs</h1>

                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search documentation..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                                />
                                <div className="absolute right-3 top-2.5 text-gray-400">
                                    🔍
                                </div>
                            </div>
                        </div>

                        {/* Navigation */}
                        <div className="flex-1 overflow-y-auto p-4">
                            {Object.entries(categorizedSections).map(([category, sections]) => (
                                sections.length > 0 && (
                                    <div key={category} className="mb-6">
                                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">
                                            {category.replace('-', ' ')}
                                        </h3>
                                        <div className="space-y-1">
                                            {sections.map((section) => (
                                                <button
                                                    key={section.id}
                                                    onClick={() => setActiveSection(section.id)}
                                                    className={`w-full text-left p-3 rounded-lg transition-colors flex items-center space-x-3 ${activeSection === section.id
                                                            ? 'bg-blue-600 text-white'
                                                            : 'text-gray-300 hover:bg-gray-800'
                                                        }`}
                                                >
                                                    <span>{section.icon}</span>
                                                    <span className="text-sm font-medium">{section.title}</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )
                            ))}
                        </div>

                        {/* Sidebar Footer */}
                        <div className="p-4 border-t border-gray-700">
                            <button
                                onClick={() => setShowAssistant(!showAssistant)}
                                className={`w-full p-3 rounded-lg transition-colors flex items-center space-x-3 ${showAssistant
                                        ? 'bg-green-600 text-white'
                                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                    }`}
                            >
                                <span>🤖</span>
                                <span className="text-sm font-medium">AI Assistant</span>
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <div className="bg-gray-900 border-b border-gray-700 p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 text-gray-400 hover:text-white transition-colors"
                        >
                            ☰
                        </button>
                        <h2 className="text-lg font-semibold text-white">
                            {docSections.find(s => s.id === activeSection)?.title || 'Documentation'}
                        </h2>
                    </div>

                    <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1 text-xs text-gray-400">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span>Docs v2.1.0</span>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 flex overflow-hidden">
                    <div className="flex-1 overflow-y-auto">
                        <div className="p-8 max-w-4xl mx-auto">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={activeSection}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    {loading ? (
                                        <div className="flex items-center justify-center py-20">
                                            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                            <span className="ml-3 text-gray-400">Loading documentation...</span>
                                        </div>
                                    ) : (
                                        <ReactMarkdown components={markdownComponents}>
                                            {content}
                                        </ReactMarkdown>
                                    )}
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    </div>

                    {/* AI Assistant Panel */}
                    <AnimatePresence>
                        {showAssistant && (
                            <motion.div
                                initial={{ x: 400, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                exit={{ x: 400, opacity: 0 }}
                                transition={{ duration: 0.3 }}
                                className="w-96 bg-gray-900 border-l border-gray-700"
                            >
                                <HelpAssistant
                                    documentContent={content}
                                    availableSections={docSections}
                                    onSectionChange={setActiveSection}
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
