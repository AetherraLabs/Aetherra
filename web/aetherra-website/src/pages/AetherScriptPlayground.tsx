import { useState } from "react";
import CodeEditor from "../components/CodeEditor";
import ScriptExecutionPanel from "../components/ScriptExecutionPanel";

const defaultScript = `// AetherScript - Consciousness Programming Language
// This is a demonstration of .aether syntax

memory.load("consciousness_state");

goal("Improve text summarization") {
  priority: high
  context: "user_request"

  // Define the improvement strategy
  strategy {
    analyze_current_performance()
    identify_bottlenecks()
    implement_optimization()
  }

  // Success criteria
  success_when {
    accuracy > 0.92
    response_time < 200ms
    user_satisfaction > 4.5
  }
}

// Plugin interaction
plugin.summarizer {
  config.max_length = 150
  config.preserve_context = true
}

// Memory management
memory.clean() {
  retention_policy: "important_only"
  max_age: "7_days"
}

reflect("Daily performance analysis") {
  metrics: ["accuracy", "speed", "user_feedback"]
  output: "insights.log"
}`;

export default function AetherScriptPlayground() {
    const [script, setScript] = useState(defaultScript);
    const [selectedExample, setSelectedExample] = useState("default");

    const examples = {
        default: defaultScript,
        basic: `// Basic AetherScript example
memory.load("basic_state");

goal("Hello World") {
  priority: low
  action: log("Hello from AetherScript!")
}`,
        plugin: `// Plugin development example
plugin.create("weather_plugin") {
  description: "Fetches weather data"

  function fetch_weather(location) {
    api.call("weather_service", {
      location: location,
      format: "json"
    })
  }

  export: ["fetch_weather"]
}`,
        memory: `// Memory management example
memory.organize() {
  // Categorize memories by importance
  important = memory.filter(importance > 0.8)
  routine = memory.filter(importance <= 0.5)

  // Archive old routine memories
  routine.archive(older_than: "30_days")

  // Boost important memories
  important.boost_retention(factor: 1.5)
}`
    };

    return (
        <div className="p-6 space-y-6">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold mb-4">⚡ AetherScript Playground</h1>
                <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                    Interactive environment for writing and testing AetherScript - the consciousness programming language.
                </p>
            </div>

            <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold">📝 Code Editor</h2>
                    <div className="flex items-center gap-4">
                        <label className="text-sm text-gray-400">Examples:</label>
                        <select
                            value={selectedExample}
                            onChange={(e) => {
                                setSelectedExample(e.target.value);
                                setScript(examples[e.target.value as keyof typeof examples]);
                            }}
                            className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                            <option value="default">Default Demo</option>
                            <option value="basic">Basic Example</option>
                            <option value="plugin">Plugin Development</option>
                            <option value="memory">Memory Management</option>
                        </select>
                    </div>
                </div>

                <CodeEditor language="aether" code={script} onChange={setScript} />
            </div>

            <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                <h2 className="text-xl font-semibold mb-4">🚀 Execution Environment</h2>
                <ScriptExecutionPanel script={script} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                    <h3 className="text-lg font-semibold mb-3">📚 AetherScript Features</h3>
                    <ul className="text-sm text-gray-300 space-y-2">
                        <li>• <strong>Goal-oriented programming</strong> - Define objectives with success criteria</li>
                        <li>• <strong>Memory management</strong> - Direct interaction with consciousness memory</li>
                        <li>• <strong>Plugin integration</strong> - Seamless plugin development and interaction</li>
                        <li>• <strong>Reflection capabilities</strong> - Built-in self-analysis and improvement</li>
                        <li>• <strong>Context awareness</strong> - Scripts adapt to current system state</li>
                    </ul>
                </div>

                <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
                    <h3 className="text-lg font-semibold mb-3">⚡ Quick Reference</h3>
                    <div className="text-sm text-gray-300 space-y-2">
                        <div><code className="bg-gray-700 px-1 rounded">goal("name")</code> - Define an objective</div>
                        <div><code className="bg-gray-700 px-1 rounded">memory.load()</code> - Load memory context</div>
                        <div><code className="bg-gray-700 px-1 rounded">plugin.name</code> - Interact with plugins</div>
                        <div><code className="bg-gray-700 px-1 rounded">reflect()</code> - Trigger self-analysis</div>
                        <div><code className="bg-gray-700 px-1 rounded">strategy { }</code> - Define action plans</div>
                    </div>
                </div>
            </div>

            <div className="bg-gradient-to-r from-purple-900 to-blue-900 p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-semibold mb-4">🧠 About AetherScript</h3>
                <p className="text-gray-200 mb-4">
                    AetherScript is a domain-specific language designed for consciousness programming.
                    It allows developers to write scripts that interact directly with Lyrixa's cognitive processes,
                    memory systems, and goal management.
                </p>
                <div className="flex gap-4">
                    <a
                        href="/contribute"
                        className="bg-white text-purple-900 px-6 py-2 rounded font-semibold hover:bg-gray-100 transition-colors"
                    >
                        Contribute to AetherScript
                    </a>
                    <a
                        href="https://github.com/AetherraLabs/Aetherra/wiki/AetherScript-Documentation"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded transition-colors"
                    >
                        View Documentation
                    </a>
                </div>
            </div>
        </div>
    );
}
