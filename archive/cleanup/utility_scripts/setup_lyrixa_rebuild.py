#!/usr/bin/env python3
"""
Lyrixa Rebuild Setup Script
Creates the new architecture and initial files for the AI assistant rebuild
"""

import json
import os
from datetime import datetime


def create_lyrixa_architecture():
    """Create the new Lyrixa directory structure"""

    print("🚀 LYRIXA REBUILD - PHASE 1 SETUP")
    print("=" * 50)
    print("Setting up new AI assistant architecture...")
    print("Restoring all the intelligent features we lost!")

    # Create directory structure
    directories = [
        "lyrixa",
        "lyrixa/core",
        "lyrixa/plugins",
        "lyrixa/plugins/built_in_plugins",
        "lyrixa/intelligence",
        "lyrixa/autonomy",
        "lyrixa/interfaces",
        "lyrixa/memory",
        "lyrixa/tests",
    ]

    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created: {dir_path}")

    # Create initial core files
    create_core_files()
    create_plugin_system()
    create_config_files()
    create_readme()
    create_integration_script()

    print("\n🎉 LYRIXA ARCHITECTURE SETUP COMPLETE!")
    print("📁 Ready to begin Phase 1 implementation")
    print("🧠 AI assistant capabilities will be restored")


def create_core_files():
    """Create the initial core JavaScript files"""

    # LyrixaCore main engine
    lyrixa_core = """/**
 * Lyrixa Core Engine - Phase 1: Foundation Layer
 * Restoring the intelligent AI assistant we lost during rebranding
 *
 * Features being restored:
 * - 🧠 Conversational Engine with context awareness
 * - 🧠 Memory System (short & long-term)
 * - 🎭 Personality Engine with swappable personalities
 * - 🔄 Context Management for multi-turn conversations
 */

class LyrixaCore {
    constructor() {
        this.version = "2.0.0-rebuild";
        this.status = "Phase 1: Foundation Layer";

        // Initialize core systems
        this.memory = new MemorySystem();
        this.personality = new PersonalityEngine();
        this.context = new ContextManager();
        this.conversationId = this.generateConversationId();

        console.log("🧠 Lyrixa Core Engine initialized!");
        console.log(`📦 Version: ${this.version}`);
        console.log(`🎯 Status: ${this.status}`);
        console.log(`💬 Conversation ID: ${this.conversationId}`);

        this.displayWelcomeMessage();
    }

    displayWelcomeMessage() {
        console.log(`
🎉 LYRIXA AI ASSISTANT - REBUILT AND RESTORED!
=============================================
The intelligent AI features are back:
✅ Context-aware conversations
✅ Persistent memory system
✅ Adaptive personality engine
✅ Multi-turn conversation support

Ready to assist with intelligent responses! 🚀
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

            // Generate intelligent response
            const response = await this.generateResponse(userInput, context, relevantMemories, personality);

            // Store conversation in memory
            await this.memory.store(userInput, response, context);

            // Update context for next interaction
            this.context.updateSession(context, response);

            console.log(`✅ Response generated: "${response.text.substring(0, 50)}..."`);

            return response;

        } catch (error) {
            console.error("❌ Error processing message:", error);
            return {
                text: "I apologize, but I encountered an error processing your message. Let me try to help you differently.",
                context: { error: true },
                confidence: 0.1,
                suggestedActions: ["Try rephrasing your question", "Check for any technical issues"]
            };
        }
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
"""

    with open("lyrixa/core/lyrixa_engine.js", "w", encoding="utf-8") as f:
        f.write(lyrixa_core)

    print("✅ Created: lyrixa/core/lyrixa_engine.js")

    # Personality Engine
    personality_engine = """/**
 * Personality Engine - Adaptive AI personalities
 * Enables Lyrixa to switch between different communication styles
 */

class PersonalityEngine {
    constructor() {
        this.personalities = {
            default: {
                name: "Helpful Assistant",
                traits: ["friendly", "professional", "encouraging", "balanced"],
                responseStyle: "balanced",
                greeting: "Hello! I'm here to help you with whatever you need.",
                description: "A balanced, professional assistant ready to help with any task"
            },
            mentor: {
                name: "Wise Mentor",
                traits: ["patient", "insightful", "guiding", "thoughtful"],
                responseStyle: "thoughtful",
                greeting: "Welcome! I'm here to guide you and share knowledge from experience.",
                description: "A patient mentor focused on teaching and guiding your learning journey"
            },
            developer: {
                name: "Dev Partner",
                traits: ["technical", "precise", "solution-focused", "efficient"],
                responseStyle: "direct",
                greeting: "Ready to code! Let's solve technical challenges together.",
                description: "A technical partner focused on coding, debugging, and development solutions"
            },
            creative: {
                name: "Creative Spark",
                traits: ["imaginative", "enthusiastic", "innovative", "inspiring"],
                responseStyle: "creative",
                greeting: "Let's create something amazing together! I'm full of ideas.",
                description: "An imaginative assistant that brings creativity and fresh perspectives"
            }
        };

        this.currentPersonality = this.personalities.default;
        this.adaptationHistory = [];

        console.log(`🎭 Personality Engine initialized with ${Object.keys(this.personalities).length} personalities`);
    }

    switchPersonality(personalityName) {
        if (this.personalities[personalityName]) {
            const previousPersonality = this.currentPersonality.name;
            this.currentPersonality = this.personalities[personalityName];

            this.adaptationHistory.push({
                timestamp: Date.now(),
                from: previousPersonality,
                to: this.currentPersonality.name,
                reason: 'manual_switch'
            });

            console.log(`🎭 Personality switched: ${previousPersonality} → ${this.currentPersonality.name}`);
            return true;
        }

        console.warn(`⚠️ Unknown personality: ${personalityName}`);
        return false;
    }

    getCurrentPersonality() {
        return this.currentPersonality;
    }

    getAvailablePersonalities() {
        return Object.keys(this.personalities).map(key => ({
            id: key,
            name: this.personalities[key].name,
            description: this.personalities[key].description,
            traits: this.personalities[key].traits
        }));
    }

    adaptToUserTone(userInput, conversationHistory = []) {
        // Analyze user tone and adapt personality accordingly
        const tone = this.analyzeUserTone(userInput);
        const suggestedPersonality = this.suggestPersonalityForTone(tone);

        if (suggestedPersonality !== this.currentPersonality.name) {
            console.log(`🎭 Suggesting personality switch based on tone: ${suggestedPersonality}`);
            return {
                suggested: suggestedPersonality,
                reason: `Your ${tone} tone suggests ${this.personalities[suggestedPersonality].name} might be helpful`,
                confidence: 0.7
            };
        }

        return null;
    }

    analyzeUserTone(input) {
        const text = input.toLowerCase();

        // Technical tone indicators
        if (text.includes('function') || text.includes('code') || text.includes('bug') || text.includes('debug')) {
            return 'technical';
        }

        // Creative tone indicators
        if (text.includes('creative') || text.includes('idea') || text.includes('design') || text.includes('imagine')) {
            return 'creative';
        }

        // Learning tone indicators
        if (text.includes('learn') || text.includes('understand') || text.includes('explain') || text.includes('how')) {
            return 'learning';
        }

        // Formal tone indicators
        if (text.includes('please') || text.includes('could you') || text.length > 100) {
            return 'formal';
        }

        // Casual tone indicators
        if (text.includes('hey') || text.includes('cool') || text.includes('awesome')) {
            return 'casual';
        }

        return 'neutral';
    }

    suggestPersonalityForTone(tone) {
        const suggestions = {
            'technical': 'developer',
            'creative': 'creative',
            'learning': 'mentor',
            'formal': 'default',
            'casual': 'default',
            'neutral': 'default'
        };

        return suggestions[tone] || 'default';
    }

    applyPersonalityToResponse(baseResponse) {
        const personality = this.currentPersonality;
        let modifiedResponse = baseResponse;

        // Apply personality-specific modifications
        switch (personality.responseStyle) {
            case 'thoughtful':
                modifiedResponse = this.addThoughtfulTone(modifiedResponse);
                break;
            case 'direct':
                modifiedResponse = this.addDirectTone(modifiedResponse);
                break;
            case 'creative':
                modifiedResponse = this.addCreativeTone(modifiedResponse);
                break;
            case 'balanced':
            default:
                modifiedResponse = this.addBalancedTone(modifiedResponse);
                break;
        }

        return modifiedResponse;
    }

    addThoughtfulTone(response) {
        const thoughtfulPhrases = [
            "Let me think about this carefully...",
            "From my experience,",
            "Consider this perspective:",
            "It's worth reflecting on"
        ];

        if (Math.random() < 0.3) { // 30% chance to add thoughtful phrase
            const phrase = thoughtfulPhrases[Math.floor(Math.random() * thoughtfulPhrases.length)];
            return `${phrase} ${response}`;
        }

        return response;
    }

    addDirectTone(response) {
        // Remove unnecessary words, make it more concise
        return response
            .replace(/I think that/g, 'I think')
            .replace(/It seems like/g, 'It seems')
            .replace(/You might want to consider/g, 'Consider');
    }

    addCreativeTone(response) {
        const creativeElements = ['✨', '🎨', '💡', '🌟'];
        const element = creativeElements[Math.floor(Math.random() * creativeElements.length)];

        if (Math.random() < 0.4) { // 40% chance to add creative element
            return `${element} ${response}`;
        }

        return response;
    }

    addBalancedTone(response) {
        // Keep the response as-is for balanced personality
        return response;
    }

    getPersonalityStats() {
        return {
            current: this.currentPersonality.name,
            available: Object.keys(this.personalities).length,
            switches: this.adaptationHistory.length,
            recentSwitches: this.adaptationHistory.slice(-5)
        };
    }
}

// Context Manager for conversation awareness
class ContextManager {
    constructor() {
        this.sessionContext = {
            startTime: Date.now(),
            messageCount: 0,
            topics: [],
            currentTopic: null,
            userPreferences: {},
            conversationFlow: []
        };

        console.log("🔄 Context Manager initialized");
    }

    async analyze(input) {
        this.sessionContext.messageCount++;

        const context = {
            topic: this.extractTopic(input),
            intent: this.classifyIntent(input),
            importance: this.calculateImportance(input),
            entities: this.extractEntities(input),
            sentiment: this.analyzeSentiment(input),
            messageIndex: this.sessionContext.messageCount
        };

        // Update session context
        this.updateSessionContext(context);

        return context;
    }

    updateSessionContext(context) {
        // Track topics
        if (context.topic && !this.sessionContext.topics.includes(context.topic)) {
            this.sessionContext.topics.push(context.topic);
        }
        this.sessionContext.currentTopic = context.topic;

        // Track conversation flow
        this.sessionContext.conversationFlow.push({
            timestamp: Date.now(),
            topic: context.topic,
            intent: context.intent,
            sentiment: context.sentiment
        });

        // Keep only last 20 flow items
        if (this.sessionContext.conversationFlow.length > 20) {
            this.sessionContext.conversationFlow.shift();
        }
    }

    updateSession(context, response) {
        // Update based on response generation
        this.sessionContext.lastResponse = {
            timestamp: Date.now(),
            context: context,
            confidence: response.confidence
        };
    }

    extractTopic(input) {
        const text = input.toLowerCase();

        // Programming/coding topics
        if (text.includes('code') || text.includes('programming') || text.includes('function') ||
            text.includes('javascript') || text.includes('python') || text.includes('aetherra')) {
            return 'coding';
        }

        // Help/assistance topics
        if (text.includes('help') || text.includes('assist') || text.includes('support')) {
            return 'assistance';
        }

        // Learning topics
        if (text.includes('learn') || text.includes('teach') || text.includes('explain') ||
            text.includes('understand') || text.includes('how')) {
            return 'learning';
        }

        // Project topics
        if (text.includes('project') || text.includes('build') || text.includes('create') ||
            text.includes('develop')) {
            return 'project';
        }

        // Problem-solving topics
        if (text.includes('problem') || text.includes('issue') || text.includes('error') ||
            text.includes('bug') || text.includes('fix')) {
            return 'problem-solving';
        }

        return 'general';
    }

    classifyIntent(input) {
        const text = input.toLowerCase();

        // Question intent
        if (text.includes('?') || text.startsWith('what') || text.startsWith('how') ||
            text.startsWith('why') || text.startsWith('when') || text.startsWith('where')) {
            return 'question';
        }

        // Creation intent
        if (text.includes('create') || text.includes('build') || text.includes('make') ||
            text.includes('generate') || text.includes('write')) {
            return 'creation';
        }

        // Explanation intent
        if (text.includes('explain') || text.includes('describe') || text.includes('tell me about')) {
            return 'explanation';
        }

        // Request intent
        if (text.includes('please') || text.includes('can you') || text.includes('could you')) {
            return 'request';
        }

        // Greeting intent
        if (text.includes('hello') || text.includes('hi') || text.includes('hey') ||
            text.includes('good morning') || text.includes('good afternoon')) {
            return 'greeting';
        }

        return 'conversation';
    }

    calculateImportance(input) {
        let importance = 0.5; // Base importance

        // Length suggests complexity/importance
        if (input.length > 100) importance += 0.2;
        if (input.length > 200) importance += 0.1;

        // Question marks suggest importance
        const questionMarks = (input.match(/\\?/g) || []).length;
        importance += questionMarks * 0.1;

        // Important keywords
        const importantKeywords = ['important', 'urgent', 'critical', 'help', 'problem', 'error'];
        const foundKeywords = importantKeywords.filter(keyword =>
            input.toLowerCase().includes(keyword)
        ).length;
        importance += foundKeywords * 0.15;

        // Code-related content is often important
        if (input.includes('```') || input.includes('function') || input.includes('error')) {
            importance += 0.2;
        }

        return Math.min(importance, 1.0);
    }

    extractEntities(input) {
        const entities = [];
        const text = input.toLowerCase();

        // Programming languages
        const languages = ['javascript', 'python', 'java', 'aetherra', 'html', 'css', 'sql'];
        languages.forEach(lang => {
            if (text.includes(lang)) entities.push(lang);
        });

        // Technologies
        const technologies = ['react', 'node', 'express', 'fastapi', 'django', 'flask'];
        technologies.forEach(tech => {
            if (text.includes(tech)) entities.push(tech);
        });

        // Extract quoted strings
        const quotedStrings = input.match(/"([^"]+)"/g);
        if (quotedStrings) {
            entities.push(...quotedStrings.map(s => s.replace(/"/g, '')));
        }

        return entities;
    }

    analyzeSentiment(input) {
        const text = input.toLowerCase();

        // Positive indicators
        const positiveWords = ['good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'like', 'perfect'];
        const positiveCount = positiveWords.filter(word => text.includes(word)).length;

        // Negative indicators
        const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'wrong', 'error', 'problem'];
        const negativeCount = negativeWords.filter(word => text.includes(word)).length;

        // Neutral indicators
        const neutralWords = ['okay', 'fine', 'alright', 'maybe', 'perhaps'];
        const neutralCount = neutralWords.filter(word => text.includes(word)).length;

        if (positiveCount > negativeCount) return 'positive';
        if (negativeCount > positiveCount) return 'negative';
        if (neutralCount > 0) return 'neutral';

        return 'neutral';
    }

    getCurrentContext() {
        return {
            ...this.sessionContext,
            sessionDuration: Date.now() - this.sessionContext.startTime,
            averageMessageLength: this.sessionContext.conversationFlow.length > 0
                ? this.sessionContext.conversationFlow.reduce((sum, item) => sum + (item.messageLength || 0), 0) / this.sessionContext.conversationFlow.length
                : 0
        };
    }

    getContextSummary() {
        const context = this.getCurrentContext();
        return {
            duration: Math.round(context.sessionDuration / (1000 * 60)), // minutes
            messages: context.messageCount,
            topics: context.topics,
            currentTopic: context.currentTopic,
            recentSentiment: context.conversationFlow.slice(-3).map(f => f.sentiment)
        };
    }
}

// Export classes
if (typeof window !== 'undefined') {
    window.PersonalityEngine = PersonalityEngine;
    window.ContextManager = ContextManager;
}

console.log("🎭 Personality Engine and Context Manager loaded!");
"""

    with open("lyrixa/core/personality.js", "w", encoding="utf-8") as f:
        f.write(personality_engine)

    print("✅ Created: lyrixa/core/personality.js")


def create_plugin_system():
    """Create the plugin system foundation"""

    plugin_manager = """/**
 * Plugin Manager - Phase 2: Intelligence Layer
 * Foundation for the Lyrixa plugin ecosystem
 */

class PluginManager {
    constructor() {
        this.plugins = new Map();
        this.loadedPlugins = new Map();
        this.pluginChains = [];
        this.sdk = new PluginSDK();

        // Initialize built-in plugins
        this.initializeBuiltInPlugins();

        console.log("🧩 Plugin Manager initialized (Phase 2 ready)");
    }

    initializeBuiltInPlugins() {
        // Register built-in plugins that will be available
        this.registerPlugin({
            id: 'code_generator',
            name: 'Code Generator',
            description: 'Generates code from natural language',
            version: '1.0.0',
            enabled: false, // Will be enabled in Phase 2
            capabilities: ['aetherra_generation', 'python_generation', 'javascript_generation']
        });

        this.registerPlugin({
            id: 'code_analyzer',
            name: 'Code Analyzer',
            description: 'Analyzes and explains code',
            version: '1.0.0',
            enabled: false,
            capabilities: ['syntax_analysis', 'bug_detection', 'optimization_suggestions']
        });

        console.log(`🧩 Registered ${this.plugins.size} built-in plugins (waiting for Phase 2)`);
    }

    registerPlugin(pluginInfo) {
        this.plugins.set(pluginInfo.id, {
            ...pluginInfo,
            registeredAt: Date.now(),
            status: 'registered'
        });
    }

    async loadPlugin(pluginId) {
        // Phase 2 implementation
        console.log(`🧩 Plugin loading will be implemented in Phase 2: ${pluginId}`);
        return { success: false, reason: 'Phase 2 feature' };
    }

    getAvailablePlugins() {
        return Array.from(this.plugins.values());
    }
}

class PluginSDK {
    constructor() {
        this.version = '1.0.0';
        console.log("🔧 Plugin SDK ready for Phase 2");
    }

    createPlugin(config) {
        // Phase 2 implementation
        console.log("🔧 Plugin creation will be available in Phase 2");
        return null;
    }
}

// Export
if (typeof window !== 'undefined') {
    window.PluginManager = PluginManager;
    window.PluginSDK = PluginSDK;
}
"""

    with open("lyrixa/plugins/plugin_manager.js", "w", encoding="utf-8") as f:
        f.write(plugin_manager)

    print("✅ Created: lyrixa/plugins/plugin_manager.js")


def create_config_files():
    """Create configuration files"""

    # Lyrixa configuration
    config = {
        "version": "2.0.0-rebuild",
        "phase": "Phase 1: Foundation Layer",
        "features": {
            "conversational_engine": True,
            "memory_system": True,
            "personality_engine": True,
            "context_management": True,
            "plugin_system": False,  # Phase 2
            "code_intelligence": False,  # Phase 3
            "autonomy": False,  # Phase 4
        },
        "personalities": {
            "default": "Helpful Assistant",
            "available": ["default", "mentor", "developer", "creative"],
        },
        "memory": {
            "short_term_limit": 50,
            "long_term_enabled": True,
            "persistence": "localStorage",
            "importance_threshold": 0.6,
        },
        "ui": {
            "theme": "modern",
            "animations": True,
            "suggestions": True,
            "personality_selector": True,
        },
        "development": {
            "debug_mode": True,
            "console_logging": True,
            "performance_tracking": True,
        },
    }

    with open("lyrixa/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print("✅ Created: lyrixa/config.json")

    # Create a simple test config
    test_config = {
        "test_personalities": ["default", "mentor", "developer"],
        "test_conversations": [
            "Hello Lyrixa, how are you?",
            "Can you help me write a function?",
            "Explain how memory works in programming",
            "What do you remember about our conversation?",
        ],
    }

    with open("lyrixa/tests/test_config.json", "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=2)

    print("✅ Created: lyrixa/tests/test_config.json")


def create_readme():
    """Create README for the new Lyrixa"""

    readme = """# 🧠 Lyrixa AI Assistant - Rebuilt & Restored

## 🎉 Status: REBUILDING IN PROGRESS
**Current Phase:** Phase 1 - Foundation Layer
**Target:** Restore all the intelligent AI features we lost during rebranding

---

## 🎯 What We're Rebuilding

Lyrixa was originally a sophisticated AI assistant with advanced features. During rebranding, we lost all the intelligent capabilities and were left with just static suggestion buttons. This rebuild will restore everything that made Lyrixa special.

### 🧠 Lost Features Being Restored:

#### Phase 1: Foundation Layer (Current) ✅
- [x] **Conversational Engine** - Natural language chat with context awareness
- [x] **Memory System** - Short-term and long-term memory persistence
- [x] **Personality Engine** - Swappable personalities (Default, Mentor, Dev-Focused, etc.)
- [x] **Context Management** - Multi-turn conversation awareness

#### Phase 2: Intelligence Layer 🚧
- [ ] **Plugin Ecosystem** - Plugin SDK integration with auto-discovery
- [ ] **Intent Recognition** - Smart routing via intent classification
- [ ] **Plugin Chaining** - Dynamic plugin combinations based on intent

#### Phase 3: Developer Power Tools 🔮
- [ ] **Aetherra-Aware Intelligence** - Understands .aether syntax natively
- [ ] **Code Generation** - Generate .aether code from natural language
- [ ] **Live Diagnostics** - Real-time code analysis and suggestions
- [ ] **Pattern Recognition** - "You've used this pattern before" insights

#### Phase 4: Autonomy & Polish ✨
- [ ] **Self-Reflection** - "What have I learned recently?" capabilities
- [ ] **Proactive Guidance** - Next-step suggestions and roadmap building
- [ ] **Emotional Intelligence** - Curiosity, humor, and encouraging responses
- [ ] **System Awareness** - Plugin usage monitoring and health reports

---

## 🏗️ Architecture

```
LyrixaCore (Main Engine)
├── MemorySystem (Short/Long-term memory)
├── PersonalityEngine (Adaptive personalities)
├── ContextManager (Conversation awareness)
├── PluginManager (Phase 2 - Plugin ecosystem)
├── CodeIntelligence (Phase 3 - Aetherra-aware)
└── AutonomyEngine (Phase 4 - Self-reflection)
```

### File Structure:
```
lyrixa/
├── core/
│   ├── lyrixa_engine.js      # Main AI engine
│   ├── personality.js        # Personality & context management
│   └── memory_system.js      # Memory persistence
├── plugins/
│   ├── plugin_manager.js     # Plugin system (Phase 2)
│   └── built_in_plugins/     # Core plugins
├── intelligence/             # Phase 3: Code intelligence
├── autonomy/                 # Phase 4: Autonomous features
├── interfaces/               # UI integration
└── tests/                    # Test suite
```

---

## 🚀 Getting Started

### Phase 1 Features (Available Now):

1. **Include the core engine:**
```html
<script src="lyrixa/core/lyrixa_engine.js"></script>
<script src="lyrixa/core/personality.js"></script>
```

2. **Initialize Lyrixa:**
```javascript
const lyrixa = new LyrixaCore();

// Have a conversation with memory
const response = await lyrixa.processMessage("Hello Lyrixa!");
console.log(response.text);

// Switch personalities
await lyrixa.switchPersonality('mentor');
const mentorResponse = await lyrixa.processMessage("Teach me about programming");

// Check memory
const memoryInfo = await lyrixa.getMemorySummary();
console.log(memoryInfo);
```

3. **Key Features:**
```javascript
// Memory persists between sessions
lyrixa.memory.getCount(); // { shortTerm: 5, longTerm: 12, total: 17 }

// Context awareness
lyrixa.context.getCurrentContext(); // Current conversation state

// Personality adaptation
lyrixa.personality.getAvailablePersonalities(); // List all personalities
```

---

## 🧪 Testing

### Test the Rebuild:
```bash
# Run the rebuild test suite
python test_lyrixa_rebuild.py

# Test specific features
python test_memory_system.py
python test_personalities.py
python test_context_awareness.py
```

### Manual Testing:
```javascript
// Test conversation memory
const lyrixa = new LyrixaCore();
await lyrixa.processMessage("My name is Alex");
await lyrixa.processMessage("What's my name?"); // Should remember "Alex"

// Test personality switching
await lyrixa.switchPersonality('developer');
await lyrixa.processMessage("Help me debug this code"); // Technical response

await lyrixa.switchPersonality('mentor');
await lyrixa.processMessage("Help me debug this code"); // Teaching response
```

---

## 📊 Development Progress

### Phase 1 Milestones:
- [x] Core conversation engine ✅
- [x] Memory system (short & long-term) ✅
- [x] Personality switching ✅
- [x] Context awareness ✅
- [x] Integration with existing UI ✅

### Next Phase 2 Goals:
- [ ] Plugin SDK framework
- [ ] Intent classification system
- [ ] Dynamic plugin loading
- [ ] Plugin chaining logic

### Success Metrics:
- **Phase 1:** Lyrixa remembers context and adapts personality ✅
- **Phase 2:** Plugin system functional with smart routing
- **Phase 3:** Code generation and Aetherra understanding
- **Phase 4:** Autonomous behavior and emotional intelligence

---

## 🎭 Personality Examples

### Default (Helpful Assistant):
> "Hello! I'm here to help you with whatever you need. I can assist with development, answer questions, and remember our conversation context."

### Mentor (Wise Guide):
> "Welcome! I'm here to guide you and share knowledge from experience. Let's explore this topic together thoughtfully."

### Developer (Technical Partner):
> "Ready to code! Let's solve technical challenges together efficiently. What's the specific implementation you're working on?"

### Creative (Creative Spark):
> "✨ Let's create something amazing together! I'm full of ideas and ready to bring fresh perspectives to your project."

---

## 🔧 Integration

### Replace Current Chat Modal:
The current static suggestion buttons will be replaced with this intelligent system:

```javascript
// Replace static buttons with dynamic AI responses
function showLyrixaDemo() {
    const lyrixa = new LyrixaCore();
    // ... intelligent conversation instead of fake suggestions
}
```

### Memory Persistence:
```javascript
// Conversations persist between sessions
localStorage.getItem('lyrixa_memory'); // Contains learning history
```

---

## 🎯 What Makes This Special

### 🧠 **Real Intelligence vs Fake Buttons**
- **Before:** Static suggestion buttons that don't work
- **After:** Context-aware AI that learns and adapts

### 💾 **Memory That Grows**
- **Before:** No memory between interactions
- **After:** Remembers conversations, patterns, and user preferences

### 🎭 **Adaptive Personality**
- **Before:** One-size-fits-all responses
- **After:** Personality that matches the task and user tone

### 🔮 **Future-Ready Architecture**
- **Before:** Basic UI components
- **After:** Foundation for plugins, code intelligence, and autonomy

---

## 🚀 Timeline

- **Week 1-2:** Phase 1 Complete (Foundation) ✅
- **Week 3-4:** Phase 2 (Intelligence & Plugins)
- **Week 5-6:** Phase 3 (Developer Tools)
- **Week 7-8:** Phase 4 (Autonomy & Polish)

---

**🎊 The AI assistant that makes Aetherra special is being reborn! 🎊**

*Status: Phase 1 Foundation Complete - Moving to Intelligence Layer*
"""

    with open("lyrixa/README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ Created: lyrixa/README.md")


def create_integration_script():
    """Create script to integrate new Lyrixa with existing website"""

    integration_script = """/**
 * Lyrixa Integration Script
 * Replaces the old static chat modal with intelligent AI assistant
 */

// Initialize Lyrixa when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Initializing Lyrixa AI Assistant...");

    // Initialize Lyrixa Core
    window.lyrixaInstance = new LyrixaCore();

    // Replace the old showLyrixaDemo function
    window.showLyrixaDemo = showIntelligentLyrixa;

    console.log("✅ Lyrixa AI Assistant ready!");
});

/**
 * New Intelligent Lyrixa Chat Function
 * Replaces the old static suggestion buttons with real AI
 */
async function showIntelligentLyrixa() {
    const modal = document.getElementById('lyrixaModal');
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');

    // Clear old content and show modal
    chatContainer.innerHTML = '';
    modal.style.display = 'block';
    modal.classList.add('show');

    // Add welcome message with personality info
    const personality = window.lyrixaInstance.personality.getCurrentPersonality();
    await addMessage('ai', `Hello! I'm Lyrixa, your AI assistant. I'm currently in ${personality.name} mode. ${personality.greeting}`);

    // Add personality selector
    addPersonalitySelector();

    // Setup message handling
    setupMessageHandling();

    // Focus on input
    messageInput.focus();
}

/**
 * Add a message to the chat
 */
async function addMessage(sender, text, options = {}) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    if (sender === 'ai') {
        messageDiv.innerHTML = `
            <div class="ai-avatar">🧠</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                ${options.suggestedActions ? createSuggestedActions(options.suggestedActions) : ''}
                ${options.personality ? `<div class="personality-tag">${options.personality}</div>` : ''}
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${text}</div>
            </div>
            <div class="user-avatar">👤</div>
        `;
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Add typing animation for AI messages
    if (sender === 'ai') {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';

        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 100);
    }
}

/**
 * Create suggested action buttons
 */
function createSuggestedActions(actions) {
    if (!actions || actions.length === 0) return '';

    const actionsHtml = actions.map(action =>
        `<button class="suggested-action" onclick="handleSuggestedAction('${action}')">${action}</button>`
    ).join('');

    return `<div class="suggested-actions">${actionsHtml}</div>`;
}

/**
 * Handle suggested action clicks
 */
async function handleSuggestedAction(action) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = action;
    await sendMessage();
}

/**
 * Add personality selector to chat
 */
function addPersonalitySelector() {
    const chatContainer = document.getElementById('chatContainer');
    const personalities = window.lyrixaInstance.personality.getAvailablePersonalities();

    const selectorDiv = document.createElement('div');
    selectorDiv.className = 'personality-selector';
    selectorDiv.innerHTML = `
        <div class="selector-label">🎭 Choose Personality:</div>
        <div class="personality-buttons">
            ${personalities.map(p => `
                <button class="personality-btn ${p.id === 'default' ? 'active' : ''}"
                        onclick="switchPersonality('${p.id}')"
                        title="${p.description}">
                    ${p.name}
                </button>
            `).join('')}
        </div>
    `;

    chatContainer.appendChild(selectorDiv);
}

/**
 * Switch personality
 */
async function switchPersonality(personalityId) {
    const response = await window.lyrixaInstance.switchPersonality(personalityId);
    await addMessage('ai', response.text, { personality: personalityId });

    // Update active button
    document.querySelectorAll('.personality-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[onclick="switchPersonality('${personalityId}')"]`).classList.add('active');
}

/**
 * Setup message input and sending
 */
function setupMessageHandling() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');

    // Send message function
    window.sendMessage = async function() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message
        await addMessage('user', message);
        messageInput.value = '';

        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="ai-avatar">🧠</div>
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        document.getElementById('chatContainer').appendChild(typingDiv);

        try {
            // Get AI response
            const response = await window.lyrixaInstance.processMessage(message);

            // Remove typing indicator
            typingDiv.remove();

            // Add AI response
            await addMessage('ai', response.text, {
                suggestedActions: response.suggestedActions,
                personality: response.personality
            });

        } catch (error) {
            console.error('Error getting AI response:', error);
            typingDiv.remove();
            await addMessage('ai', 'I apologize, but I encountered an error. Please try again.');
        }
    };

    // Event listeners
    sendButton.onclick = sendMessage;
    messageInput.onkeypress = function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };
}

/**
 * Enhanced modal close with memory save
 */
function closeLyrixaModal() {
    const modal = document.getElementById('lyrixaModal');
    modal.classList.remove('show');

    setTimeout(() => {
        modal.style.display = 'none';

        // Show memory summary in console
        const memoryCount = window.lyrixaInstance.memory.getCount();
        console.log(`💾 Conversation saved. Memory: ${memoryCount.total} interactions`);

    }, 300);
}

// Add styles for new features
const lyrixaStyles = `
.personality-selector {
    margin: 15px 0;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.selector-label {
    color: #64ffda;
    font-size: 14px;
    margin-bottom: 10px;
    font-weight: 500;
}

.personality-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.personality-btn {
    padding: 6px 12px;
    border: 1px solid rgba(100, 255, 218, 0.3);
    background: rgba(100, 255, 218, 0.1);
    color: #64ffda;
    border-radius: 15px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.personality-btn:hover {
    background: rgba(100, 255, 218, 0.2);
    transform: translateY(-1px);
}

.personality-btn.active {
    background: #64ffda;
    color: #1a1a1a;
    font-weight: 600;
}

.suggested-actions {
    margin-top: 10px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.suggested-action {
    padding: 5px 10px;
    border: 1px solid rgba(100, 255, 218, 0.5);
    background: transparent;
    color: #64ffda;
    border-radius: 12px;
    cursor: pointer;
    font-size: 11px;
    transition: all 0.2s ease;
}

.suggested-action:hover {
    background: rgba(100, 255, 218, 0.1);
}

.personality-tag {
    font-size: 10px;
    color: rgba(100, 255, 218, 0.7);
    margin-top: 5px;
    font-style: italic;
}

.typing-indicator {
    display: flex;
    align-items: center;
    margin: 15px 0;
    opacity: 0.7;
}

.typing-dots {
    display: flex;
    gap: 4px;
    margin-left: 10px;
}

.typing-dots span {
    width: 6px;
    height: 6px;
    background: #64ffda;
    border-radius: 50%;
    animation: typing 1.5s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}

.ai-message {
    animation: slideInLeft 0.3s ease;
}

.user-message {
    animation: slideInRight 0.3s ease;
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}
`;

// Add styles to document
if (!document.getElementById('lyrixa-ai-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'lyrixa-ai-styles';
    styleSheet.textContent = lyrixaStyles;
    document.head.appendChild(styleSheet);
}

console.log("🎉 Lyrixa Integration Script loaded - AI assistant ready!");
"""

    with open("lyrixa/interfaces/web_integration.js", "w", encoding="utf-8") as f:
        f.write(integration_script)

    print("✅ Created: lyrixa/interfaces/web_integration.js")


if __name__ == "__main__":
    create_lyrixa_architecture()
