/**
 * Lyrixa Core Engine - Phase 2: Intelligence Layer
 * Advanced AI assistant with plugin system and intent recognition
 *
 * Features:
 * - 🧠 Conversational Engine with context awareness
 * - 🧠 Memory System (short & long-term)
 * - 🎭 Personality Engine with swappable personalities
 * - 🔄 Context Management for multi-turn conversations
 * - 🧩 Plugin System with intelligent routing
 * - 🎯 Intent Recognition and smart response generation
 */

class LyrixaCore {
    constructor() {
        this.version = "2.1.0-phase2";
        this.status = "Phase 2: Intelligence Layer - Plugin System Active";

        // Initialize core systems
        this.memory = new MemorySystem();
        this.personality = new PersonalityEngine();
        this.context = new ContextManager();
        this.conversationId = this.generateConversationId();

        // Phase 2: Initialize advanced systems
        this.intentRecognition = null;
        this.pluginManager = null;
        this.phase2Ready = false;

        console.log("🧠 Lyrixa Core Engine Phase 2 initializing...");
        console.log(`[DISC] Version: ${this.version}`);
        console.log(`🎯 Status: ${this.status}`);
        console.log(`💬 Conversation ID: ${this.conversationId}`);

        // Initialize Phase 2 systems asynchronously
        this.initializePhase2();

        this.displayWelcomeMessage();
    }


    async initializePhase2() {
        // Wait for dependencies to load
        setTimeout(async () => {
            if (typeof IntentRecognition !== 'undefined' && typeof PluginManager !== 'undefined') {
                this.intentRecognition = new IntentRecognition();
                this.pluginManager = new PluginManager();
                this.phase2Ready = true;

                console.log("🚀 PHASE 2 SYSTEMS ACTIVE!");
                console.log("✅ Intent Recognition System loaded");
                console.log("✅ Plugin Manager with active plugins loaded");
                console.log(`✅ ${this.pluginManager.getActivePlugins().length} plugins ready for execution`);
            } else {
                console.log("⏳ Waiting for Phase 2 dependencies...");
                // Retry in 1 second
                setTimeout(() => this.initializePhase2(), 1000);
            }
        }, 100);
    }

    displayWelcomeMessage() {
        console.log(`
🎉 LYRIXA AI ASSISTANT - PHASE 2: INTELLIGENCE LAYER
====================================================
Advanced AI features now active:
✅ Context-aware conversations
✅ Persistent memory system
✅ Adaptive personality engine
✅ Multi-turn conversation support
🆕 Plugin system with intelligent routing
🆕 Intent recognition and smart responses
🆕 Code generation and analysis capabilities

Ready for intelligent assistance with plugin power! 🚀
        `);
    }

    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async processMessage(userInput, options = {}) {
        try {
            console.log(`🔄 Processing: "${userInput}"`);

            // Analyze context and intent
            const context = await this.context.analyze(userInput);
            console.log(`🧠 Context analyzed:`, context);

            // Get current personality
            const personality = this.personality.getCurrentPersonality();
            console.log(`🎭 Using personality: ${personality.name}`);

            // Recall relevant memories
            const relevantMemories = await this.memory.recall(context);
            console.log(`💾 Found ${relevantMemories.length} relevant memories`);

            // Phase 2: Use intent recognition and plugin system if available
            if (this.phase2Ready && this.intentRecognition && this.pluginManager) {
                return await this.processWithPhase2(userInput, context, relevantMemories, personality);
            } else {
                // Fallback to Phase 1 processing
                return await this.processWithPhase1(userInput, context, relevantMemories, personality);
            }

        } catch (error) {
            console.error("[ERROR] Error processing message:", error);
            return {
                text: "I apologize, but I encountered an error processing your message. Let me try to help you differently.",
                context: { error: true },
                confidence: 0.1,
                suggestedActions: ["Try rephrasing your question", "Check for any technical issues"]
            };
        }
    }

    async processWithPhase2(userInput, context, memories, personality) {
        console.log("🚀 Using Phase 2 processing with intent recognition and plugins");

        // Recognize intent
        const intentAnalysis = await this.intentRecognition.recognizeIntent(userInput, {
            personality: personality,
            memories: memories,
            previousIntent: context.previousIntent
        });

        console.log(`🎯 Intent recognized: ${intentAnalysis.topIntent} (${(intentAnalysis.confidence * 100).toFixed(1)}% confidence)`);

        // Execute appropriate plugin
        const pluginResult = await this.pluginManager.executePlugin(
            intentAnalysis.topIntent.replace('_', '_').includes('_') ?
                this.mapIntentToPlugin(intentAnalysis.topIntent) :
                intentAnalysis.topIntent,
            userInput,
            {
                intent: intentAnalysis,
                personality: personality,
                memories: memories,
                context: context
            }
        );

        let response;

        if (pluginResult.success) {
            // Create response from plugin result
            response = this.createResponseFromPlugin(pluginResult.result, intentAnalysis, personality);
        } else {
            // Fallback to conversation handler
            const fallbackResult = await this.pluginManager.executePlugin(
                'conversation_handler',
                userInput,
                { personality: personality, memories: memories, context: context }
            );

            response = fallbackResult.success ?
                this.createResponseFromPlugin(fallbackResult.result, intentAnalysis, personality) :
                await this.generateResponse(userInput, context, memories, personality);
        }

        // Store conversation in memory with enhanced context
        await this.memory.store(userInput, response, {
            ...context,
            intent: intentAnalysis.topIntent,
            confidence: intentAnalysis.confidence,
            pluginUsed: pluginResult.pluginId
        });

        // Update context for next interaction
        this.context.updateSession({
            ...context,
            previousIntent: intentAnalysis.topIntent
        }, response);

        console.log(`✅ Phase 2 response generated: "${response.text.substring(0, 50)}..."`);

        return response;
    }

    async processWithPhase1(userInput, context, memories, personality) {
        console.log("[DISC] Using Phase 1 fallback processing");

        // Generate intelligent response
        const response = await this.generateResponse(userInput, context, memories, personality);

        // Store conversation in memory
        await this.memory.store(userInput, response, context);

        // Update context for next interaction
        this.context.updateSession(context, response);

        console.log(`✅ Phase 1 response generated: "${response.text.substring(0, 50)}..."`);

        return response;
    }

    mapIntentToPlugin(intent) {
        const mapping = {
            'code_generation': 'code_generator',
            'code_analysis': 'code_analyzer',
            'learning_assistance': 'learning_assistant',
            'project_assistance': 'project_advisor',
            'general_chat': 'conversation_handler'
        };

        return mapping[intent] || 'conversation_handler';
    }

    createResponseFromPlugin(pluginResult, intentAnalysis, personality) {
        let responseText = "";
        let suggestedActions = [];

        if (pluginResult.type === 'code_generation') {
            responseText = `I've generated ${pluginResult.framework ? `${pluginResult.framework} ` : ''}${pluginResult.language} code for you!\n\n${pluginResult.explanation}\n\n**Features included:**\n${pluginResult.features.map(f => `• ${f}`).join('\n')}`;
            suggestedActions = ["Copy the code", "Ask for modifications", "Request explanation"];

        } else if (pluginResult.type === 'code_analysis') {
            responseText = pluginResult.analysis;
            suggestedActions = pluginResult.capabilities || [];

        } else if (pluginResult.type === 'learning_explanation') {
            responseText = `**${pluginResult.topic} Explained:**\n\n${pluginResult.explanation}`;
            if (pluginResult.examples) {
                responseText += `\n\n**Examples:**\n${pluginResult.examples.map(e => `• ${e}`).join('\n')}`;
            }
            suggestedActions = pluginResult.nextSteps || ["Ask follow-up questions", "Request examples"];

        } else if (pluginResult.type === 'project_advice') {
            responseText = `**Project Guidance:**\n\n${pluginResult.recommendations.join('\n')}`;
            suggestedActions = ["Ask about specific areas", "Request code examples", "Get implementation help"];

        } else if (pluginResult.type === 'conversation_response') {
            responseText = pluginResult.response;
            suggestedActions = ["Continue conversation", "Ask questions", "Change topic"];

        } else {
            responseText = JSON.stringify(pluginResult, null, 2);
            suggestedActions = ["Ask for clarification", "Try a different approach"];
        }

        return {
            text: responseText,
            context: {
                plugin: pluginResult.type,
                intent: intentAnalysis.topIntent,
                confidence: intentAnalysis.confidence
            },
            confidence: intentAnalysis.confidence,
            suggestedActions: suggestedActions,
            personality: personality.name,
            timestamp: new Date().toISOString(),
            pluginData: pluginResult
        };
    }

    async generateResponse(input, context, memories, personality) {
        // This is the core AI response generation
        // In Phase 1, we'll start with rule-based responses and pattern matching
        // Later phases will add more sophisticated AI

        const response = {
            text: "",
            context: context,
            confidence: 0.8,
            suggestedActions: [],
            personality: personality.name,
            timestamp: new Date().toISOString()
        };

        // Apply personality-based response generation
        if (personality.name === "Helpful Assistant") {
            response.text = this.generateHelpfulResponse(input, context, memories);
        } else if (personality.name === "Wise Mentor") {
            response.text = this.generateMentorResponse(input, context, memories);
        } else if (personality.name === "Dev Partner") {
            response.text = this.generateDevResponse(input, context, memories);
        }

        // Add memory-based context if available
        if (memories.length > 0) {
            response.text += this.addMemoryContext(memories);
        }

        // Generate suggested actions based on context
        response.suggestedActions = this.generateSuggestedActions(context);

        return response;
    }

    generateHelpfulResponse(input, context, memories) {
        const greetings = ["hello", "hi", "hey", "greetings"];
        const questions = input.includes("?");
        const helpRequests = input.toLowerCase().includes("help");

        if (greetings.some(g => input.toLowerCase().includes(g))) {
            return `Hello! I'm Lyrixa, your AI assistant. I'm here to help you with development, answer questions, and learn from our conversations. What would you like to work on today?`;
        }

        if (helpRequests) {
            return `I'd be happy to help! I can assist with code generation, answer questions, provide explanations, and remember our conversation context. What specific help do you need?`;
        }

        if (questions) {
            return `That's a great question! Based on what you're asking about "${context.topic}", let me think about this... ${this.generateTopicResponse(context.topic)}`;
        }

        return `I understand you mentioned "${input}". Let me help you with this. Based on our conversation context, I can see you're interested in ${context.topic}. How would you like me to assist?`;
    }

    generateMentorResponse(input, context, memories) {
        return `Let me share some wisdom about "${context.topic}". From my understanding of your question, here's what I think... ${this.generateThoughtfulResponse(context.topic)}. What's your experience with this so far?`;
    }

    generateDevResponse(input, context, memories) {
        if (context.topic === 'coding') {
            return `Looking at your code-related question, let's break this down technically. The best approach would be... ${this.generateTechnicalResponse(input)}. Want me to generate some code examples?`;
        }
        return `From a technical perspective, "${input}" relates to ${context.topic}. Let's solve this efficiently. What's the specific implementation you're working on?`;
    }

    generateTopicResponse(topic) {
        const responses = {
            'coding': 'I can help with programming, debugging, code generation, and best practices.',
            'assistance': 'I can provide explanations, guidance, and step-by-step help.',
            'general': 'I can discuss various topics and learn from our conversation.',
            'aetherra': 'I can help with the Aetherra programming language and its features.'
        };
        return responses[topic] || 'I can learn about this topic as we discuss it further.';
    }

    generateThoughtfulResponse(topic) {
        return `this is an interesting area that requires careful consideration. There are several approaches we could explore together`;
    }

    generateTechnicalResponse(input) {
        if (input.includes('function') || input.includes('code')) {
            return 'creating a function that handles this properly with error checking and good structure';
        }
        return 'implementing a solution that follows best practices and is maintainable';
    }

    addMemoryContext(memories) {
        if (memories.length === 1) {
            return ` I remember we discussed something similar before.`;
        } else if (memories.length > 1) {
            return ` I notice we've talked about related topics ${memories.length} times before, so I can build on that context.`;
        }
        return '';
    }

    generateSuggestedActions(context) {
        const actions = [];

        if (context.intent === 'question') {
            actions.push('Ask for clarification', 'Request examples', 'Explore related topics');
        } else if (context.intent === 'creation') {
            actions.push('Generate code', 'Create examples', 'Provide templates');
        } else if (context.intent === 'explanation') {
            actions.push('Get more details', 'See examples', 'Understand concepts');
        }

        return actions;
    }

    // Personality management
    switchPersonality(personalityName) {
        this.personality.switchPersonality(personalityName);
        return {
            text: `I've switched to my ${this.personality.getCurrentPersonality().name} personality. You'll notice I communicate differently now.`,
            context: { action: 'personality_switch' },
            confidence: 1.0
        };
    }

    // Memory management
    async getMemorySummary() {
        const summary = await this.memory.getSummary();
        return {
            text: `Here's what I remember from our conversations: ${summary.total} interactions, ${summary.topics.join(', ')} as main topics.`,
            context: { action: 'memory_summary' },
            confidence: 1.0
        };
    }

    // Context information
    getContextInfo() {
        return {
            conversationId: this.conversationId,
            currentPersonality: this.personality.getCurrentPersonality().name,
            memoryCount: this.memory.getCount(),
            sessionContext: this.context.getCurrentContext()
        };
    }
}

// Memory System for persistent context and learning
class MemorySystem {
    constructor() {
        this.shortTerm = []; // Current session memories
        this.longTerm = this.loadLongTermMemory(); // Persistent memories
        this.patterns = new Map(); // Learned patterns
        this.maxShortTerm = 50; // Limit short-term memory

        console.log(`💾 Memory System initialized with ${this.longTerm.length} long-term memories`);
    }

    async store(input, output, context) {
        const memory = {
            id: this.generateMemoryId(),
            timestamp: Date.now(),
            input: input,
            output: output.text,
            context: context,
            importance: this.calculateImportance(input, output, context),
            session: true
        };

        // Add to short-term memory
        this.shortTerm.push(memory);

        // Manage short-term memory size
        if (this.shortTerm.length > this.maxShortTerm) {
            this.shortTerm.shift(); // Remove oldest
        }

        // Decide if important enough for long-term storage
        if (memory.importance > 0.6) {
            memory.session = false;
            this.longTerm.push(memory);
            this.saveLongTermMemory();
            console.log(`💾 Stored important memory: "${input.substring(0, 30)}..."`);
        }

        // Learn patterns
        this.updatePatterns(memory);
    }

    async recall(context) {
        const allMemories = [...this.shortTerm, ...this.longTerm];

        // Find relevant memories based on context similarity
        const relevant = allMemories.filter(memory =>
            this.calculateRelevance(memory, context) > 0.3
        );

        // Sort by relevance and recency
        relevant.sort((a, b) => {
            const relevanceA = this.calculateRelevance(a, context);
            const relevanceB = this.calculateRelevance(b, context);
            const recencyA = (Date.now() - a.timestamp) / (1000 * 60 * 60); // Hours ago
            const recencyB = (Date.now() - b.timestamp) / (1000 * 60 * 60);

            return (relevanceB + (1 / (recencyB + 1))) - (relevanceA + (1 / (recencyA + 1)));
        });

        return relevant.slice(0, 5); // Return top 5 relevant memories
    }

    calculateImportance(input, output, context) {
        let importance = 0.3; // Base importance

        // Length suggests complexity
        if (input.length > 50) importance += 0.2;
        if (output.text.length > 100) importance += 0.2;

        // Context factors
        if (context.intent === 'creation') importance += 0.3;
        if (context.topic === 'coding') importance += 0.2;

        // Keywords that suggest importance
        const importantKeywords = ['important', 'remember', 'save', 'project', 'error', 'problem'];
        if (importantKeywords.some(keyword => input.toLowerCase().includes(keyword))) {
            importance += 0.3;
        }

        return Math.min(importance, 1.0);
    }

    calculateRelevance(memory, context) {
        let relevance = 0;

        // Topic similarity
        if (memory.context.topic === context.topic) relevance += 0.4;

        // Intent similarity
        if (memory.context.intent === context.intent) relevance += 0.3;

        // Keyword overlap
        const memoryWords = memory.input.toLowerCase().split(' ');
        const contextWords = context.entities.map(e => e.toLowerCase());
        const overlap = memoryWords.filter(word => contextWords.includes(word)).length;
        relevance += (overlap / Math.max(memoryWords.length, contextWords.length)) * 0.3;

        return relevance;
    }

    updatePatterns(memory) {
        // Simple pattern learning - track topic-intent combinations
        const pattern = `${memory.context.topic}-${memory.context.intent}`;
        const count = this.patterns.get(pattern) || 0;
        this.patterns.set(pattern, count + 1);
    }

    generateMemoryId() {
        return 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
    }

    loadLongTermMemory() {
        try {
            const stored = localStorage.getItem('lyrixa_memory');
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.warn("Could not load long-term memory:", e);
            return [];
        }
    }

    saveLongTermMemory() {
        try {
            localStorage.setItem('lyrixa_memory', JSON.stringify(this.longTerm));
        } catch (e) {
            console.warn("Could not save long-term memory:", e);
        }
    }

    getCount() {
        return {
            shortTerm: this.shortTerm.length,
            longTerm: this.longTerm.length,
            total: this.shortTerm.length + this.longTerm.length
        };
    }

    async getSummary() {
        const allMemories = [...this.shortTerm, ...this.longTerm];
        const topics = [...new Set(allMemories.map(m => m.context.topic))];

        return {
            total: allMemories.length,
            topics: topics,
            patterns: Array.from(this.patterns.entries()).sort((a, b) => b[1] - a[1]).slice(0, 3)
        };
    }
}

// Export for use in the main application
if (typeof window !== 'undefined') {
    window.LyrixaCore = LyrixaCore;
    window.MemorySystem = MemorySystem;
}

console.log("🧠 Lyrixa Core Engine loaded successfully!");
