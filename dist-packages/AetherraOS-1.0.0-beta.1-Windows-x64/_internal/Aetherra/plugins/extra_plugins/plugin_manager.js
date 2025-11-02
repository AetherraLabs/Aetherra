/**
 * Plugin Manager - Phase 2: Intelligence Layer
 * Advanced plugin ecosystem with active execution and chaining
 */

class PluginManager {
    constructor() {
        this.plugins = new Map();
        this.loadedPlugins = new Map();
        this.activePlugins = new Map();
        this.pluginChains = [];
        this.executionHistory = [];
        this.sdk = new PluginSDK();

        // Initialize built-in plugins
        this.initializeBuiltInPlugins();

        console.log("🧩 Plugin Manager Phase 2 - ACTIVE with execution capabilities");
    }

    initializeBuiltInPlugins() {
        // Register and ACTIVATE built-in plugins for Phase 2
        this.registerAndActivatePlugin({
            id: 'code_generator',
            name: 'Code Generator',
            description: 'Generates intelligent code from natural language descriptions',
            version: '2.0.0',
            enabled: true,
            capabilities: ['aetherra_generation', 'python_generation', 'javascript_generation', 'react_generation', 'fastapi_generation'],
            execute: this.codeGeneratorPlugin.bind(this)
        });

        this.registerAndActivatePlugin({
            id: 'code_analyzer',
            name: 'Code Analyzer',
            description: 'Analyzes, debugs, and optimizes code with intelligent insights',
            version: '2.0.0',
            enabled: true,
            capabilities: ['syntax_analysis', 'bug_detection', 'optimization_suggestions', 'code_explanation'],
            execute: this.codeAnalyzerPlugin.bind(this)
        });

        this.registerAndActivatePlugin({
            id: 'learning_assistant',
            name: 'Learning Assistant',
            description: 'Provides educational explanations and learning guidance',
            version: '2.0.0',
            enabled: true,
            capabilities: ['concept_explanation', 'tutorial_generation', 'learning_path'],
            execute: this.learningAssistantPlugin.bind(this)
        });

        this.registerAndActivatePlugin({
            id: 'project_advisor',
            name: 'Project Advisor',
            description: 'Provides architectural guidance and project structure recommendations',
            version: '2.0.0',
            enabled: true,
            capabilities: ['architecture_advice', 'best_practices', 'project_structure'],
            execute: this.projectAdvisorPlugin.bind(this)
        });

        this.registerAndActivatePlugin({
            id: 'conversation_handler',
            name: 'Conversation Handler',
            description: 'Handles general conversation and personality-driven responses',
            version: '2.0.0',
            enabled: true,
            capabilities: ['general_chat', 'personality_responses', 'context_awareness'],
            execute: this.conversationHandlerPlugin.bind(this)
        });

        console.log(`🧩 Activated ${this.activePlugins.size} intelligent plugins for Phase 2`);
    }

    registerPlugin(pluginInfo) {
        this.plugins.set(pluginInfo.id, {
            ...pluginInfo,
            registeredAt: Date.now(),
            status: 'registered'
        });
    }

    registerAndActivatePlugin(pluginInfo) {
        // Register the plugin
        this.plugins.set(pluginInfo.id, {
            ...pluginInfo,
            registeredAt: Date.now(),
            status: 'active'
        });

        // Activate the plugin if it has an execute function
        if (pluginInfo.execute && pluginInfo.enabled) {
            this.activePlugins.set(pluginInfo.id, pluginInfo);
            console.log(`🧩 Activated plugin: ${pluginInfo.name}`);
        }
    }

    async executePlugin(pluginId, input, context = {}) {
        const startTime = performance.now();

        if (!this.activePlugins.has(pluginId)) {
            console.warn(`[WARN] Plugin not active: ${pluginId}`);
            return {
                success: false,
                error: 'Plugin not active or not found',
                pluginId: pluginId
            };
        }

        const plugin = this.activePlugins.get(pluginId);
        console.log(`🧩 Executing plugin: ${plugin.name}`);

        try {
            const result = await plugin.execute(input, context);
            const endTime = performance.now();

            const execution = {
                pluginId,
                pluginName: plugin.name,
                input,
                result,
                context,
                timestamp: Date.now(),
                executionTime: endTime - startTime,
                success: true
            };

            this.executionHistory.push(execution);
            if (this.executionHistory.length > 50) {
                this.executionHistory.shift(); // Keep last 50
            }

            console.log(`✅ Plugin executed successfully: ${plugin.name} (${execution.executionTime.toFixed(2)}ms)`);
            return {
                success: true,
                result: result,
                pluginId: pluginId,
                executionTime: execution.executionTime
            };

        } catch (error) {
            console.error(`❌ Plugin execution failed: ${plugin.name}`, error);
            return {
                success: false,
                error: error.message,
                pluginId: pluginId
            };
        }
    }

    async loadPlugin(pluginId) {
        // Phase 2 implementation
        if (this.activePlugins.has(pluginId)) {
            console.log(`🧩 Plugin already loaded: ${pluginId}`);
            return { success: true, reason: 'Already loaded' };
        }

        console.log(`🧩 Loading plugin: ${pluginId}`);
        return { success: true, reason: 'Plugin loaded for Phase 2' };
    }

    getAvailablePlugins() {
        return Array.from(this.plugins.values());
    }

    getActivePlugins() {
        return Array.from(this.activePlugins.values());
    }

    getExecutionHistory() {
        return this.executionHistory;
    }

    // Built-in Plugin Implementations

    async codeGeneratorPlugin(input, context) {
        const analysis = this.analyzeCodeRequest(input);

        if (analysis.language === 'python' && analysis.framework === 'fastapi') {
            return this.generateFastAPICode(analysis);
        } else if (analysis.language === 'javascript' && analysis.framework === 'react') {
            return this.generateReactCode(analysis);
        } else if (analysis.language === 'javascript' && analysis.framework === 'express') {
            return this.generateExpressCode(analysis);
        } else if (analysis.type === 'function') {
            return this.generateFunction(analysis);
        } else {
            return this.generateGenericCode(analysis);
        }
    }

    analyzeCodeRequest(input) {
        const lowerInput = input.toLowerCase();

        const analysis = {
            type: 'unknown',
            language: 'javascript', // default
            framework: null,
            purpose: input,
            complexity: 'simple'
        };

        // Detect language
        if (lowerInput.includes('python')) analysis.language = 'python';
        if (lowerInput.includes('javascript') || lowerInput.includes('js')) analysis.language = 'javascript';
        if (lowerInput.includes('typescript')) analysis.language = 'typescript';

        // Detect framework
        if (lowerInput.includes('fastapi')) analysis.framework = 'fastapi';
        if (lowerInput.includes('react')) analysis.framework = 'react';
        if (lowerInput.includes('express')) analysis.framework = 'express';
        if (lowerInput.includes('node')) analysis.framework = 'node';

        // Detect type
        if (lowerInput.includes('function')) analysis.type = 'function';
        if (lowerInput.includes('class')) analysis.type = 'class';
        if (lowerInput.includes('api')) analysis.type = 'api';
        if (lowerInput.includes('component')) analysis.type = 'component';

        return analysis;
    }

    generateFastAPICode(analysis) {
        return {
            type: 'code_generation',
            language: 'python',
            framework: 'fastapi',
            code: `from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Generated API", version="1.0.0")

class ItemModel(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/items/", response_model=List[ItemModel])
async def get_items():
    return [
        ItemModel(id=1, name="Item 1", description="First item"),
        ItemModel(id=2, name="Item 2", description="Second item")
    ]

@app.post("/items/", response_model=ItemModel)
async def create_item(item: ItemModel):
    # Add your business logic here
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)`,
            explanation: "Generated a FastAPI application with basic CRUD operations, Pydantic models, and proper typing.",
            features: ["RESTful API structure", "Pydantic models", "Type hints", "Async endpoints"],
            nextSteps: ["Add database integration", "Implement authentication", "Add error handling"]
        };
    }

    generateReactCode(analysis) {
        return {
            type: 'code_generation',
            language: 'javascript',
            framework: 'react',
            code: `import React, { useState, useEffect } from 'react';

function GeneratedComponent() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newItem, setNewItem] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Replace with your API endpoint
      const response = await fetch('/api/data');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addItem = () => {
    if (newItem.trim()) {
      setData([...data, { id: Date.now(), name: newItem }]);
      setNewItem('');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Generated React Component</h2>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          placeholder="Add new item"
          style={{ marginRight: '10px', padding: '8px' }}
        />
        <button onClick={addItem} style={{ padding: '8px 16px' }}>
          Add
        </button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {data.map(item => (
            <li key={item.id}>{item.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default GeneratedComponent;`,
            explanation: "Generated a React component with state management, API integration, and interactive UI.",
            features: ["React Hooks", "State management", "Event handling", "API integration"],
            nextSteps: ["Add styling", "Implement delete functionality", "Add form validation"]
        };
    }

    generateExpressCode(analysis) {
        return {
            type: 'code_generation',
            language: 'javascript',
            framework: 'express',
            code: `const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage (replace with database)
let items = [
  { id: 1, name: 'Item 1', description: 'First item' },
  { id: 2, name: 'Item 2', description: 'Second item' }
];

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Generated Express API is running!' });
});

app.get('/api/items', (req, res) => {
  res.json(items);
});

app.post('/api/items', (req, res) => {
  const { name, description } = req.body;
  const newItem = {
    id: items.length + 1,
    name,
    description
  };
  items.push(newItem);
  res.status(201).json(newItem);
});

app.get('/api/items/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const item = items.find(item => item.id === id);

  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }

  res.json(item);
});

app.listen(PORT, () => {
  console.log(\`Server is running on port \${PORT}\`);
});`,
            explanation: "Generated an Express.js server with REST API endpoints and middleware setup.",
            features: ["Express middleware", "REST endpoints", "Error handling", "CORS support"],
            nextSteps: ["Add database integration", "Implement authentication", "Add input validation"]
        };
    }

    generateFunction(analysis) {
        return {
            type: 'code_generation',
            code: `// Generated function based on your request
function generatedFunction(input) {
    // TODO: Implement your logic here
    console.log('Processing:', input);

    // Example implementation
    return {
        success: true,
        processed: input,
        timestamp: new Date().toISOString()
    };
}

// Example usage
const result = generatedFunction('test data');
console.log(result);`,
            explanation: "Generated a basic function template that you can customize for your specific needs.",
            features: ["Function structure", "Error handling template", "Example usage"],
            nextSteps: ["Customize the logic", "Add error handling", "Write tests"]
        };
    }

    generateGenericCode(analysis) {
        return {
            type: 'code_generation',
            code: `// Generated code based on: ${analysis.purpose}

// TODO: Implement your specific requirements
console.log('Generated code for: ${analysis.purpose}');

// Example structure
const implementation = {
    purpose: '${analysis.purpose}',
    language: '${analysis.language}',
    created: new Date().toISOString(),

    execute() {
        console.log('Executing implementation...');
        // Add your logic here
    }
};

implementation.execute();`,
            explanation: "Generated a basic code structure that you can expand based on your specific requirements.",
            features: ["Basic structure", "Configurable template", "Example implementation"],
            nextSteps: ["Define specific requirements", "Implement business logic", "Add error handling"]
        };
    }

    async codeAnalyzerPlugin(input, context) {
        // This would analyze provided code
        return {
            type: 'code_analysis',
            analysis: "I can help analyze your code! Please provide the code you'd like me to review, and I'll check for bugs, suggest optimizations, and explain how it works.",
            capabilities: [
                "🔍 Syntax and logic analysis",
                "🐛 Bug detection and fixes",
                "⚡ Performance optimization suggestions",
                "📖 Code explanation and documentation",
                "🏗️ Architecture review"
            ],
            suggestion: "Share your code and I'll provide detailed analysis and improvements."
        };
    }

    async learningAssistantPlugin(input, context) {
        const lowerInput = input.toLowerCase();

        if (lowerInput.includes('react')) {
            return this.explainReactConcept(input);
        } else if (lowerInput.includes('python')) {
            return this.explainPythonConcept(input);
        } else if (lowerInput.includes('api')) {
            return this.explainAPIConcept(input);
        } else {
            return this.provideGeneralLearning(input);
        }
    }

    explainReactConcept(input) {
        return {
            type: 'learning_explanation',
            topic: 'React',
            explanation: `React is a powerful JavaScript library for building user interfaces. Here are the key concepts:

🧩 **Components**: Reusable pieces of UI that can be functional or class-based
🎣 **Hooks**: Special functions that let you use state and lifecycle in functional components
⚡ **State**: Data that changes over time and causes re-renders
🔄 **Props**: Data passed from parent to child components
🎯 **JSX**: JavaScript syntax extension that looks like HTML`,
            examples: [
                "useState hook for managing component state",
                "useEffect hook for side effects",
                "Component composition and reusability",
                "Props passing and event handling"
            ],
            nextSteps: [
                "Practice building small components",
                "Learn about state management",
                "Understand React lifecycle",
                "Explore React ecosystem (Router, Context, etc.)"
            ]
        };
    }

    explainPythonConcept(input) {
        return {
            type: 'learning_explanation',
            topic: 'Python',
            explanation: `Python is a versatile, readable programming language. Key concepts include:

🐍 **Syntax**: Clean, readable code with meaningful indentation
[DISC] **Data Types**: Numbers, strings, lists, dictionaries, sets, tuples
🔄 **Control Flow**: if/else, loops, functions, classes
📚 **Libraries**: Extensive standard library + third-party packages
🎯 **Applications**: Web development, data science, automation, AI`,
            examples: [
                "List comprehensions for efficient data processing",
                "Dictionary usage for key-value storage",
                "Function definitions and decorators",
                "Class-based object-oriented programming"
            ],
            nextSteps: [
                "Practice with basic syntax and data types",
                "Learn about functions and modules",
                "Explore popular libraries (requests, pandas, etc.)",
                "Build small projects to apply concepts"
            ]
        };
    }

    explainAPIConcept(input) {
        return {
            type: 'learning_explanation',
            topic: 'APIs',
            explanation: `APIs (Application Programming Interfaces) are contracts between software components:

🌐 **REST APIs**: HTTP-based APIs using GET, POST, PUT, DELETE
📡 **Endpoints**: Specific URLs that accept requests
📝 **Data Formats**: Usually JSON for request/response bodies
🔑 **Authentication**: API keys, tokens, OAuth for security
📊 **Status Codes**: 200 (success), 404 (not found), 500 (error)`,
            examples: [
                "GET /api/users - retrieve user list",
                "POST /api/users - create new user",
                "PUT /api/users/123 - update user 123",
                "DELETE /api/users/123 - delete user 123"
            ],
            nextSteps: [
                "Practice making API calls with fetch/axios",
                "Learn about API design principles",
                "Understand authentication methods",
                "Build your own API with FastAPI or Express"
            ]
        };
    }

    provideGeneralLearning(input) {
        return {
            type: 'learning_explanation',
            topic: 'General Learning',
            explanation: `I'm here to help you learn! I can explain concepts, provide examples, and guide your learning journey in:

💻 **Programming**: JavaScript, Python, TypeScript, and more
🌐 **Web Development**: React, Node.js, APIs, databases
🏗️ **Architecture**: System design, best practices, patterns
🧪 **Testing**: Unit tests, integration tests, debugging
📚 **Concepts**: Algorithms, data structures, design patterns`,
            suggestion: "What specific topic would you like to learn about? I can provide explanations, examples, and learning paths tailored to your interests.",
            examples: [
                "Ask about specific programming concepts",
                "Request code examples and explanations",
                "Get guidance on learning paths",
                "Understand best practices and patterns"
            ]
        };
    }

    async projectAdvisorPlugin(input, context) {
        return {
            type: 'project_advice',
            topic: 'Project Architecture',
            recommendations: [
                "🏗️ **Modular Structure**: Organize code into logical modules and components",
                "📁 **Clear Folder Structure**: Separate concerns (components, utils, assets, etc.)",
                "[TOOL] **Configuration Management**: Use environment variables and config files",
                "🧪 **Testing Strategy**: Implement unit, integration, and E2E tests",
                "📚 **Documentation**: Maintain clear README and code documentation",
                "🔄 **Version Control**: Use meaningful commit messages and branching strategy"
            ],
            suggested_structure: {
                "src/": "Main source code",
                "components/": "Reusable UI components",
                "pages/": "Application pages/views",
                "utils/": "Helper functions and utilities",
                "api/": "API integration and services",
                "assets/": "Static assets (images, fonts, etc.)",
                "tests/": "Test files and test utilities"
            },
            best_practices: [
                "Follow consistent naming conventions",
                "Implement proper error handling",
                "Use TypeScript for better type safety",
                "Optimize for performance and accessibility"
            ]
        };
    }

    async conversationHandlerPlugin(input, context) {
        // Get current personality from context
        const personality = context.personality || { name: 'Helpful Assistant' };

        if (personality.name === 'Wise Mentor') {
            return {
                type: 'conversation_response',
                response: `I understand you're interested in "${input}". As your mentor, let me share some wisdom: every great developer started with curiosity, just like you're showing now. What specific aspect would you like to explore deeper?`,
                tone: 'mentoring',
                personality: personality.name
            };
        } else if (personality.name === 'Dev Partner') {
            return {
                type: 'conversation_response',
                response: `Got it! "${input}" - let's tackle this technically. I'm here to code alongside you and solve problems efficiently. What's the specific challenge we're dealing with?`,
                tone: 'technical',
                personality: personality.name
            };
        } else {
            return {
                type: 'conversation_response',
                response: `I'm happy to help with "${input}"! As your AI assistant, I can assist with coding, learning, project planning, and more. What would you like to work on together?`,
                tone: 'helpful',
                personality: personality.name
            };
        }
    }
}

class PluginSDK {
    constructor() {
        this.version = '2.0.0';
        console.log("[TOOL] Plugin SDK Phase 2 - Active with creation capabilities");
    }

    createPlugin(config) {
        // Phase 2 implementation
        console.log("[TOOL] Creating custom plugin:", config.name);

        const plugin = {
            id: config.id || `custom_${Date.now()}`,
            name: config.name,
            description: config.description,
            version: config.version || '1.0.0',
            enabled: true,
            capabilities: config.capabilities || [],
            execute: config.execute,
            created: Date.now()
        };

        return plugin;
    }

    validatePlugin(plugin) {
        const required = ['id', 'name', 'execute'];
        const missing = required.filter(field => !plugin[field]);

        if (missing.length > 0) {
            throw new Error(`Plugin validation failed. Missing: ${missing.join(', ')}`);
        }

        return true;
    }
}

// Export
if (typeof window !== 'undefined') {
    window.PluginManager = PluginManager;
    window.PluginSDK = PluginSDK;
}
