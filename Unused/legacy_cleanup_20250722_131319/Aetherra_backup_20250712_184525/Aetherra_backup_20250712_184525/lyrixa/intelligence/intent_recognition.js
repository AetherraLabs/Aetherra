/**
 * LYRIXA INTELLIGENCE - MIGRATION NOTICE
 * ======================================
 *
 * This JavaScript-based intent recognition system has been superseded by
 * the new Python-based Lyrixa AI Assistant architecture.
 *
 * MIGRATION COMPLETED:
 * - Intent recognition is now handled by the Python LyrixaAI class
 * - Natural language understanding integrated with .aether workflows
 * - Memory system provides context-aware intent analysis
 * - Multi-agent orchestration handles complex intents
 *
 * NEW LOCATION:
 * lyrixa/assistant.py - LyrixaAI._analyze_intent()
 *
 * TO USE NEW SYSTEM:
 * python lyrixa_launcher.py
 *
 * This file is kept for reference only.
 */

console.log("[WARN] MIGRATION NOTICE: This JavaScript intent recognition has been replaced");
console.log("🎙️ Use the new Python-based Lyrixa AI Assistant instead:");
console.log("   python lyrixa_launcher.py");

// Legacy code below - deprecated but kept for reference
// =======================================================

class IntentRecognition {
    constructor() {
        this.intents = new Map();
        this.patterns = new Map();
        this.contextHistory = [];

        this.initializeIntents();
        console.log("🧠 Intent Recognition System initialized");
    }

    initializeIntents() {
        // Code-related intents
        this.registerIntent({
            id: 'code_generation',
            name: 'Code Generation',
            description: 'User wants to generate or create code',
            patterns: [
                /(?:write|create|generate|build|make)\s+(?:a|some|the)?\s*(?:code|function|class|script|program|app)/i,
                /(?:how\s+to\s+)?(?:code|implement|program)\s+/i,
                /(?:create|build|make)\s+(?:a|an)?\s*(?:python|javascript|react|node|fastapi|express)/i,
                /(?:show\s+me\s+)?(?:example|sample)\s+(?:code|implementation)/i
            ],
            keywords: ['write', 'create', 'generate', 'build', 'code', 'function', 'implement', 'program'],
            confidence_threshold: 0.7,
            target_plugin: 'code_generator'
        });

        this.registerIntent({
            id: 'code_analysis',
            name: 'Code Analysis',
            description: 'User wants to analyze, debug, or understand code',
            patterns: [
                /(?:analyze|check|review|debug|fix|explain|understand)\s+(?:this|my|the)?\s*code/i,
                /(?:what\s+(?:does|is)|how\s+(?:does|do))\s+(?:this|my)?\s*(?:code|function|script)/i,
                /(?:find|detect|identify)\s+(?:bugs?|errors?|issues?|problems?)/i,
                /(?:why\s+(?:doesn't|isn't|won't))\s+(?:this|my)?\s*(?:code|function|script)/i
            ],
            keywords: ['analyze', 'debug', 'fix', 'explain', 'review', 'understand', 'error', 'bug'],
            confidence_threshold: 0.7,
            target_plugin: 'code_analyzer'
        });

        this.registerIntent({
            id: 'learning_assistance',
            name: 'Learning & Teaching',
            description: 'User wants to learn or understand concepts',
            patterns: [
                /(?:teach|learn|understand|explain|what\s+is)\s+/i,
                /(?:how\s+(?:do|does|to))\s+/i,
                /(?:can\s+you\s+(?:explain|teach|show))/i,
                /(?:i\s+(?:don't|do\s+not)\s+understand)/i
            ],
            keywords: ['teach', 'learn', 'explain', 'how', 'what', 'understand', 'concept'],
            confidence_threshold: 0.6,
            target_plugin: 'learning_assistant'
        });

        this.registerIntent({
            id: 'project_assistance',
            name: 'Project Help',
            description: 'User needs help with project structure or architecture',
            patterns: [
                /(?:project|app|application|system)\s+(?:structure|architecture|design|setup)/i,
                /(?:how\s+to\s+(?:organize|structure|set\s+up))\s+(?:my|a|this)?\s*(?:project|app)/i,
                /(?:best\s+practices?|recommendations?)\s+for/i,
                /(?:folder|directory)\s+structure/i
            ],
            keywords: ['project', 'structure', 'architecture', 'organize', 'setup', 'best practices'],
            confidence_threshold: 0.7,
            target_plugin: 'project_advisor'
        });

        this.registerIntent({
            id: 'general_chat',
            name: 'General Conversation',
            description: 'General conversation or unclear intent',
            patterns: [
                /^(?:hi|hello|hey|greetings)/i,
                /^(?:how\s+are\s+you|what's\s+up)/i,
                /^(?:thank\s+you|thanks)/i
            ],
            keywords: ['hello', 'hi', 'thanks', 'chat', 'conversation'],
            confidence_threshold: 0.5,
            target_plugin: 'conversation_handler'
        });

        console.log(`🧠 Initialized ${this.intents.size} intent patterns`);
    }

    registerIntent(intentConfig) {
        this.intents.set(intentConfig.id, intentConfig);

        // Index patterns for faster lookup
        intentConfig.patterns.forEach(pattern => {
            if (!this.patterns.has(pattern)) {
                this.patterns.set(pattern, []);
            }
            this.patterns.get(pattern).push(intentConfig.id);
        });
    }

    async recognizeIntent(userInput, context = {}) {
        const startTime = performance.now();
        const analysis = {
            input: userInput,
            timestamp: Date.now(),
            context: context,
            matches: [],
            topIntent: null,
            confidence: 0,
            reasoning: []
        };

        console.log(`🧠 Analyzing intent for: "${userInput}"`);

        // Score each intent
        for (const [intentId, intent] of this.intents) {
            const score = this.scoreIntent(userInput, intent, context);

            if (score.confidence > intent.confidence_threshold) {
                analysis.matches.push({
                    intent: intentId,
                    confidence: score.confidence,
                    matches: score.matches,
                    reasoning: score.reasoning
                });
            }
        }

        // Sort by confidence
        analysis.matches.sort((a, b) => b.confidence - a.confidence);

        // Set top intent
        if (analysis.matches.length > 0) {
            analysis.topIntent = analysis.matches[0].intent;
            analysis.confidence = analysis.matches[0].confidence;
            analysis.reasoning = analysis.matches[0].reasoning;
        } else {
            // Fallback to general chat
            analysis.topIntent = 'general_chat';
            analysis.confidence = 0.3;
            analysis.reasoning = ['No specific intent matched, defaulting to general conversation'];
        }

        const endTime = performance.now();
        analysis.processingTime = endTime - startTime;

        // Store in context history
        this.contextHistory.push(analysis);
        if (this.contextHistory.length > 10) {
            this.contextHistory.shift(); // Keep last 10
        }

        console.log(`🧠 Intent recognized: ${analysis.topIntent} (${(analysis.confidence * 100).toFixed(1)}% confidence)`);
        console.log(`🧠 Processing time: ${analysis.processingTime.toFixed(2)}ms`);

        return analysis;
    }

    scoreIntent(userInput, intent, context) {
        const score = {
            confidence: 0,
            matches: [],
            reasoning: []
        };

        const lowerInput = userInput.toLowerCase();

        // Pattern matching
        let patternScore = 0;
        let patternMatches = 0;

        intent.patterns.forEach(pattern => {
            if (pattern.test(userInput)) {
                patternMatches++;
                patternScore += 0.8; // High weight for pattern matches
                score.matches.push(`Pattern: ${pattern.source}`);
                score.reasoning.push(`Matched pattern: ${pattern.source}`);
            }
        });

        // Keyword matching
        let keywordScore = 0;
        let keywordMatches = 0;

        intent.keywords.forEach(keyword => {
            if (lowerInput.includes(keyword.toLowerCase())) {
                keywordMatches++;
                keywordScore += 0.3; // Lower weight for keywords
                score.matches.push(`Keyword: ${keyword}`);
                score.reasoning.push(`Found keyword: ${keyword}`);
            }
        });

        // Context boost
        let contextBoost = 0;
        if (context.previousIntent === intent.id) {
            contextBoost = 0.2; // Boost for conversation continuity
            score.reasoning.push('Context continuity boost');
        }

        // Calculate final confidence
        const totalScore = patternScore + keywordScore + contextBoost;
        const maxPossibleScore = (intent.patterns.length * 0.8) + (intent.keywords.length * 0.3) + 0.2;

        score.confidence = Math.min(totalScore / maxPossibleScore, 1.0);

        // Apply match bonuses
        if (patternMatches > 0) {
            score.confidence *= 1.2; // Bonus for any pattern match
        }

        if (keywordMatches >= 2) {
            score.confidence *= 1.1; // Bonus for multiple keywords
        }

        // Cap at 1.0
        score.confidence = Math.min(score.confidence, 1.0);

        return score;
    }

    getContextHistory() {
        return this.contextHistory;
    }

    getAvailableIntents() {
        return Array.from(this.intents.values()).map(intent => ({
            id: intent.id,
            name: intent.name,
            description: intent.description,
            target_plugin: intent.target_plugin
        }));
    }

    // Enhanced intent recognition with learning
    learnFromFeedback(userInput, correctIntent, confidence) {
        console.log(`🧠 Learning: "${userInput}" should be "${correctIntent}" (user feedback)`);
        // In a full implementation, this would update intent patterns
        // For now, we log for future ML model training
    }
}

// Export
if (typeof window !== 'undefined') {
    window.IntentRecognition = IntentRecognition;
}
