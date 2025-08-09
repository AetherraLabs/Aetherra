import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

interface Message {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    context?: string;
}

interface HelpAssistantProps {
    documentContent: string;
    availableSections: Array<{ id: string; title: string; content: string }>;
    onSectionChange: (sectionId: string) => void;
}

export function HelpAssistant({ documentContent, availableSections, onSectionChange }: HelpAssistantProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            type: 'assistant',
            content: "Hello! I'm your Aetherra documentation assistant. I can help you find information, explain concepts, and navigate the docs. What would you like to know?",
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const quickQuestions = [
        { text: "How do I get started with AetherScript?", category: "language" },
        { text: "What is consciousness in Aetherra?", category: "architecture" },
        { text: "How do I create a plugin?", category: "plugins" },
        { text: "Show me the API reference", category: "api" },
        { text: "Explain the memory system", category: "architecture" }
    ];

    const simulateAIResponse = async (userMessage: string): Promise<string> => {
        // Simulate AI processing time
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

        const lowerMessage = userMessage.toLowerCase();

        // Context-aware responses based on current document and user query
        if (lowerMessage.includes('aetherscript') || lowerMessage.includes('language')) {
            const section = availableSections.find(s => s.id === 'aether-lang');
            if (section) {
                onSectionChange('aether-lang');
                return `I've navigated you to the AetherScript Language reference. AetherScript is a consciousness-aware programming language with several key features:

• **Consciousness Declaration**: Define AI entities with \`consciousness MyAI { ... }\`
• **Memory Management**: Use \`@memory\` annotations for persistent storage
• **Neural Processing**: \`@neural\` functions for AI processing
• **Advanced Types**: Support for consciousness, thought, memory, and emotion types

The language is designed specifically for creating intelligent, self-aware systems. Would you like me to explain any specific aspect in more detail?`;
            }
        }

        if (lowerMessage.includes('memory') || lowerMessage.includes('storage')) {
            const section = availableSections.find(s => s.id === 'memory-system');
            if (section) {
                onSectionChange('memory-system');
                return `I've opened the Memory Architecture documentation. Aetherra uses a sophisticated multi-layered memory system:

• **Working Memory**: Short-term storage for active processing
• **Episodic Memory**: Stores experiences and events with context
• **Semantic Memory**: Long-term facts and knowledge storage
• **Procedural Memory**: Skills and learned behaviors

The system uses vector databases for semantic similarity and includes automatic consolidation, backup, and recovery features. What specific aspect of memory would you like to explore?`;
            }
        }

        if (lowerMessage.includes('plugin') || lowerMessage.includes('extend')) {
            const section = availableSections.find(s => s.id === 'plugin-guide');
            if (section) {
                onSectionChange('plugin-guide');
                return `I've opened the Plugin Development guide. Aetherra plugins are modular AI components that extend system capabilities:

• **Plugin Structure**: Each plugin has its own consciousness entity
• **Memory Integration**: Plugins can access and contribute to system memory
• **Event Handling**: Respond to system events and user interactions
• **Inter-Plugin Communication**: Plugins can communicate with each other

The guide includes complete examples and best practices. Would you like me to walk you through creating your first plugin?`;
            }
        }

        if (lowerMessage.includes('api') || lowerMessage.includes('reference')) {
            const section = availableSections.find(s => s.id === 'api-reference');
            if (section) {
                onSectionChange('api-reference');
                return `I've opened the complete API Reference. The Aetherra API includes:

• **Consciousness API**: Manage consciousness entities and lifecycle
• **Memory API**: Access and manipulate the memory system
• **Neural Processing API**: Interface with neural capabilities
• **Plugin API**: Install, manage, and interact with plugins
• **Event System**: Subscribe to and emit system events

Each API section includes TypeScript interfaces, usage examples, and error handling. Which API would you like to explore first?`;
            }
        }

        if (lowerMessage.includes('consciousness') || lowerMessage.includes('aware')) {
            return `Consciousness in Aetherra refers to the AI's self-awareness and ability to understand its own mental processes. Key aspects include:

• **Awareness Levels**: From basic reactive to advanced self-reflective
• **Self-Monitoring**: The ability to observe and analyze own thoughts
• **Intentionality**: Goal-directed behavior and decision making
• **Learning**: Adaptive behavior based on experience
• **Meta-Cognition**: Thinking about thinking

This is implemented through consciousness entities that can introspect, learn, and adapt their behavior. Would you like to see examples of consciousness implementation?`;
        }

        if (lowerMessage.includes('start') || lowerMessage.includes('begin') || lowerMessage.includes('tutorial')) {
            const section = availableSections.find(s => s.id === 'index');
            if (section) {
                onSectionChange('index');
                return `I've taken you to the Getting Started guide. Here's your quickstart path:

1. **Start with the Welcome page** to understand Aetherra's core concepts
2. **Learn AetherScript basics** for consciousness programming
3. **Explore the Memory System** to understand data persistence
4. **Try creating a simple plugin** to extend functionality
5. **Use the API Reference** for detailed technical implementation

Each section builds on the previous one. I recommend following this order for the best learning experience. Ready to dive in?`;
            }
        }

        if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
            return `I'm here to help you navigate the Aetherra documentation! I can:

• **Explain concepts** in simple terms
• **Navigate to relevant sections** automatically
• **Provide code examples** and usage patterns
• **Answer specific questions** about implementation
• **Guide you through tutorials** step by step

Try asking me questions like:
- "How do I create a consciousness?"
- "Explain memory types"
- "Show me plugin examples"
- "What APIs are available?"

What would you like to learn about?`;
        }

        // Generic helpful response for unrecognized queries
        return `I understand you're asking about "${userMessage}". Let me help you find the right information in the docs.

Based on your question, you might be interested in:
• **AetherScript Language** - For programming syntax and examples
• **Memory Architecture** - For data storage and retrieval
• **Plugin Development** - For extending functionality
• **API Reference** - For technical implementation details

Could you be more specific about what you'd like to learn? For example:
- Are you looking for code examples?
- Do you need installation instructions?
- Want to understand a specific concept?

I'm here to guide you through the documentation!`;
    };

    const handleSendMessage = async () => {
        if (!inputMessage.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: inputMessage,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsThinking(true);

        try {
            const response = await simulateAIResponse(inputMessage);

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: response,
                timestamp: new Date(),
                context: documentContent.slice(0, 200) + '...'
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'assistant',
                content: "I apologize, but I encountered an error processing your request. Please try asking your question in a different way.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsThinking(false);
        }
    };

    const handleQuickQuestion = (question: string) => {
        setInputMessage(question);
        setTimeout(() => handleSendMessage(), 100);
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="h-full flex flex-col bg-gray-900">
            {/* Header */}
            <div className="p-4 border-b border-gray-700">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        🤖
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">Documentation Assistant</h3>
                        <p className="text-xs text-gray-400">Powered by Aetherra AI</p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3 }}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[85%] ${message.type === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-800 text-gray-200'
                                } rounded-lg p-3`}>
                                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                    {message.content}
                                </div>
                                <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-400'
                                    }`}>
                                    {formatTime(message.timestamp)}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Thinking Indicator */}
                {isThinking && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-start"
                    >
                        <div className="bg-gray-800 rounded-lg p-3 flex items-center space-x-2">
                            <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                            <span className="text-gray-400 text-sm">Thinking...</span>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length <= 1 && (
                <div className="p-4 border-t border-gray-700">
                    <p className="text-xs text-gray-400 mb-3">Quick questions:</p>
                    <div className="space-y-2">
                        {quickQuestions.map((question, index) => (
                            <button
                                key={index}
                                onClick={() => handleQuickQuestion(question.text)}
                                className="w-full text-left text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 p-2 rounded transition-colors"
                            >
                                {question.text}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-gray-700">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Ask about Aetherra..."
                        disabled={isThinking}
                        className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={!inputMessage.trim() || isThinking}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <span className="text-sm">➤</span>
                    </button>
                </div>
            </div>
        </div>
    );
}
