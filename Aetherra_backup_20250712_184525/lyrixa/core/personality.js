/**
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
        const questionMarks = (input.match(/\?/g) || []).length;
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
