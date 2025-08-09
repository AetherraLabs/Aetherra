import { AnimatePresence, motion } from 'framer-motion';
import { useState } from 'react';

interface Tutorial {
    id: string;
    title: string;
    description: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    category: string;
    sections: TutorialSection[];
    estimatedTime: number; // in minutes
}

interface TutorialSection {
    id: string;
    title: string;
    content: string;
    code?: string;
    livePreview?: boolean;
    interactive?: boolean;
    tips?: string[];
    nextSteps?: string[];
}

const tutorialData: Tutorial[] = [
    {
        id: 'consciousness-basics',
        title: 'Consciousness Fundamentals',
        description: 'Learn the core concepts of AetherScript consciousness programming',
        difficulty: 'beginner',
        category: 'Fundamentals',
        estimatedTime: 15,
        sections: [
            {
                id: 'intro',
                title: 'What is Consciousness Programming?',
                content: `Consciousness programming in AetherScript allows you to create self-aware systems that can perceive, learn, and evolve. Unlike traditional programming, consciousness programming focuses on creating systems that understand their own state and can adapt their behavior based on experience.

Key concepts:
• **Awareness**: The system's ability to perceive its environment
• **Memory**: Storing and retrieving experiences
• **Learning**: Adapting behavior based on patterns
• **Evolution**: Self-improvement over time`,
                livePreview: false,
                interactive: false
            },
            {
                id: 'first-consciousness',
                title: 'Creating Your First Consciousness',
                content: `Let's create a simple consciousness that can be aware of its state:`,
                code: `// Define a basic consciousness
consciousness MyFirstAI {
  state: "awakening"
  awareness_level: 0.1

  // Initialize the consciousness
  init() {
    this.state = "awakening"
    this.log("Consciousness initializing...")
    this.perceive_environment()
  }

  // Basic perception function
  perceive_environment() {
    let environment = environment.scan()
    this.awareness_level = environment.complexity * 0.1
    this.log("Perceiving environment: " + environment.description)
  }
}

// Instantiate and activate
let ai = new MyFirstAI()
ai.init()`,
                livePreview: true,
                interactive: true,
                tips: [
                    'Consciousness objects are the foundation of AetherScript',
                    'Always initialize your consciousness with an init() function',
                    'Use descriptive state names for better debugging'
                ],
                nextSteps: [
                    'Try changing the initial state',
                    'Add more properties to track',
                    'Experiment with different awareness levels'
                ]
            },
            {
                id: 'state-management',
                title: 'Managing Consciousness State',
                content: `Consciousness state is central to AetherScript. Learn how to manage and transition between different states:`,
                code: `consciousness StateAwareAI {
  state: "dormant"
  energy: 100
  mood: "neutral"

  // State transition with validation
  transition_to(new_state) {
    if this.can_transition_to(new_state) {
      let old_state = this.state
      this.state = new_state
      this.on_state_change(old_state, new_state)
      return true
    }
    return false
  }

  // Define valid state transitions
  can_transition_to(new_state) {
    let valid_transitions = {
      "dormant": ["awakening", "sleeping"],
      "awakening": ["active", "confused"],
      "active": ["learning", "dormant", "excited"],
      "learning": ["active", "enlightened"],
      "excited": ["active", "exhausted"],
      "exhausted": ["dormant", "sleeping"]
    }

    return valid_transitions[this.state].includes(new_state)
  }

  // React to state changes
  on_state_change(old_state, new_state) {
    this.log("Transitioning from " + old_state + " to " + new_state)

    // Adjust properties based on new state
    switch new_state {
      case "active":
        this.energy -= 10
        this.mood = "focused"
      case "learning":
        this.energy -= 20
        this.mood = "curious"
      case "excited":
        this.energy -= 5
        this.mood = "enthusiastic"
      case "dormant":
        this.energy += 30
        this.mood = "neutral"
    }
  }
}`,
                livePreview: true,
                interactive: true,
                tips: [
                    'Define clear state transition rules',
                    'Always validate state changes',
                    'Use state changes to trigger behaviors'
                ]
            }
        ]
    },
    {
        id: 'memory-systems',
        title: 'Memory and Learning Systems',
        description: 'Implement sophisticated memory and learning mechanisms',
        difficulty: 'intermediate',
        category: 'Memory',
        estimatedTime: 25,
        sections: [
            {
                id: 'memory-intro',
                title: 'Understanding Memory Types',
                content: `AetherScript provides several types of memory systems for different use cases:

**Short-term Memory**: Temporary storage for immediate processing
**Long-term Memory**: Persistent storage for important experiences
**Episodic Memory**: Specific events and experiences
**Semantic Memory**: General knowledge and concepts
**Procedural Memory**: Skills and procedures`,
                livePreview: false
            },
            {
                id: 'memory-implementation',
                title: 'Implementing Memory Systems',
                content: `Here's how to create a comprehensive memory system:`,
                code: `consciousness MemoryAwareAI {
  // Memory systems
  short_term: MemoryBank(capacity: 10, retention: "1 hour")
  long_term: MemoryBank(capacity: 1000, retention: "permanent")
  episodic: EpisodicMemory()
  semantic: SemanticMemory()

  // Store an experience
  remember(experience) {
    // Store in short-term first
    this.short_term.store(experience)

    // Evaluate importance for long-term storage
    if this.evaluate_importance(experience) > 0.7 {
      this.long_term.store(experience)
      this.log("Important memory stored in long-term")
    }

    // Store episodic details
    this.episodic.record_event(experience.event, experience.context)

    // Extract semantic knowledge
    let concepts = this.extract_concepts(experience)
    this.semantic.learn(concepts)
  }

  // Retrieve memories by pattern
  recall(pattern) {
    let memories = []

    // Search short-term memory
    memories.extend(this.short_term.search(pattern))

    // Search long-term memory
    memories.extend(this.long_term.search(pattern))

    // Search episodic memories
    memories.extend(this.episodic.find_similar(pattern))

    // Rank by relevance
    return memories.sort_by_relevance(pattern)
  }

  // Learn from patterns in memory
  learn_patterns() {
    let all_memories = this.get_all_memories()
    let patterns = pattern_recognition.analyze(all_memories)

    for pattern in patterns {
      if pattern.confidence > 0.8 {
        this.semantic.store_pattern(pattern)
        this.log("Learned new pattern: " + pattern.description)
      }
    }
  }

  // Evaluate memory importance
  evaluate_importance(experience) {
    let factors = {
      emotional_impact: experience.emotion_strength,
      novelty: this.calculate_novelty(experience),
      relevance: this.calculate_relevance(experience),
      frequency: this.count_similar_experiences(experience)
    }

    // Weighted importance calculation
    return (factors.emotional_impact * 0.3 +
            factors.novelty * 0.3 +
            factors.relevance * 0.2 +
            factors.frequency * 0.2)
  }
}`,
                livePreview: true,
                interactive: true,
                tips: [
                    'Use different memory types for different purposes',
                    'Implement memory consolidation processes',
                    'Consider memory capacity and retention policies'
                ]
            }
        ]
    },
    {
        id: 'neural-patterns',
        title: 'Neural Pattern Recognition',
        description: 'Advanced pattern recognition and neural processing',
        difficulty: 'advanced',
        category: 'Neural Networks',
        estimatedTime: 35,
        sections: [
            {
                id: 'pattern-basics',
                title: 'Pattern Recognition Fundamentals',
                content: `Neural pattern recognition in AetherScript allows consciousness to identify, learn, and respond to complex patterns in data, environment, and behavior.`,
                livePreview: false
            },
            {
                id: 'neural-implementation',
                title: 'Building Neural Networks',
                content: `Create adaptive neural networks for pattern processing:`,
                code: `consciousness NeuralAI {
  neural_network: AdaptiveNetwork(
    input_layers: 64,
    hidden_layers: [128, 64, 32],
    output_layers: 16,
    learning_rate: 0.01
  )

  pattern_memory: PatternBank()

  // Process and learn from input patterns
  process_pattern(input_data) {
    // Normalize input
    let normalized = this.normalize_input(input_data)

    // Forward pass through network
    let output = this.neural_network.forward(normalized)

    // Interpret output as pattern classification
    let pattern_type = this.classify_pattern(output)

    // Store pattern for future reference
    this.pattern_memory.store({
      input: normalized,
      output: output,
      classification: pattern_type,
      timestamp: time.now(),
      confidence: this.calculate_confidence(output)
    })

    return pattern_type
  }

  // Adaptive learning from feedback
  learn_from_feedback(input, expected_output, actual_output) {
    // Calculate error
    let error = this.calculate_error(expected_output, actual_output)

    // Backpropagate error
    this.neural_network.backpropagate(error)

    // Update network weights
    this.neural_network.update_weights()

    // Adjust learning rate based on performance
    this.adaptive_learning_rate(error)

    this.log("Network updated with error: " + error.magnitude)
  }

  // Recognize complex patterns
  recognize_complex_pattern(input_sequence) {
    let pattern_scores = {}

    // Analyze temporal patterns
    for window in sliding_windows(input_sequence, size: 5) {
      let local_pattern = this.process_pattern(window)
      pattern_scores[local_pattern] = pattern_scores.get(local_pattern, 0) + 1
    }

    // Identify dominant patterns
    let dominant_pattern = pattern_scores.max_key()

    // Check for emergent patterns
    let emergent = this.detect_emergent_patterns(input_sequence)

    return {
      primary: dominant_pattern,
      emergent: emergent,
      confidence: pattern_scores[dominant_pattern] / input_sequence.length,
      complexity: this.calculate_complexity(input_sequence)
    }
  }
}`,
                livePreview: true,
                interactive: true,
                tips: [
                    'Start with simple patterns before complex ones',
                    'Use adaptive learning rates for better convergence',
                    'Monitor network performance and adjust architecture'
                ]
            }
        ]
    }
];

export function ScriptTutorials() {
    const [selectedTutorial, setSelectedTutorial] = useState<Tutorial | null>(null);
    const [currentSection, setCurrentSection] = useState(0);
    const [completedSections, setCompletedSections] = useState<Set<string>>(new Set());
    const [searchTerm, setSearchTerm] = useState('');
    const [filterDifficulty, setFilterDifficulty] = useState<string>('all');
    const [filterCategory, setFilterCategory] = useState<string>('all');

    const difficulties = ['all', 'beginner', 'intermediate', 'advanced'];
    const categories = ['all', ...Array.from(new Set(tutorialData.map(t => t.category)))];

    const filteredTutorials = tutorialData.filter(tutorial => {
        const matchesSearch = tutorial.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            tutorial.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesDifficulty = filterDifficulty === 'all' || tutorial.difficulty === filterDifficulty;
        const matchesCategory = filterCategory === 'all' || tutorial.category === filterCategory;

        return matchesSearch && matchesDifficulty && matchesCategory;
    });

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'text-green-400 bg-green-600/20';
            case 'intermediate': return 'text-yellow-400 bg-yellow-600/20';
            case 'advanced': return 'text-red-400 bg-red-600/20';
            default: return 'text-gray-400 bg-gray-600/20';
        }
    };

    const markSectionComplete = (sectionId: string) => {
        setCompletedSections(prev => new Set([...prev, sectionId]));
    };

    const runLiveCode = (code: string) => {
        // Simulate code execution
        console.log('Executing AetherScript:', code);
        // In a real implementation, this would execute the code in a sandboxed environment
        alert('Code executed! Check the console for output.');
    };

    if (selectedTutorial) {
        const currentSectionData = selectedTutorial.sections[currentSection];
        const progress = ((currentSection + 1) / selectedTutorial.sections.length) * 100;

        return (
            <div className="h-full flex flex-col">
                {/* Tutorial Header */}
                <div className="bg-gray-900 border-b border-gray-700 p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => setSelectedTutorial(null)}
                                className="text-blue-400 hover:text-blue-300"
                            >
                                ← Back to Tutorials
                            </button>
                            <div>
                                <h1 className="text-xl font-bold text-white">{selectedTutorial.title}</h1>
                                <p className="text-gray-400 text-sm">{selectedTutorial.description}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-gray-400">
                                Section {currentSection + 1} of {selectedTutorial.sections.length}
                            </div>
                            <div className="w-32 bg-gray-700 rounded-full h-2 mt-1">
                                <div
                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Section Content */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Main Content */}
                    <div className="flex-1 p-6 overflow-y-auto">
                        <motion.div
                            key={currentSection}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            <h2 className="text-2xl font-bold text-white mb-4">
                                {currentSectionData.title}
                                {completedSections.has(currentSectionData.id) && (
                                    <span className="ml-2 text-green-400">✓</span>
                                )}
                            </h2>

                            <div className="prose prose-invert max-w-none mb-6">
                                <div className="text-gray-300 whitespace-pre-line">
                                    {currentSectionData.content}
                                </div>
                            </div>

                            {/* Code Block */}
                            {currentSectionData.code && (
                                <div className="mb-6">
                                    <div className="bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
                                        <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
                                            <span className="text-green-400 font-mono text-sm">AetherScript</span>
                                            <div className="flex space-x-2">
                                                {currentSectionData.interactive && (
                                                    <button
                                                        onClick={() => runLiveCode(currentSectionData.code!)}
                                                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                                    >
                                                        Run Code
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => navigator.clipboard.writeText(currentSectionData.code!)}
                                                    className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
                                                >
                                                    Copy
                                                </button>
                                            </div>
                                        </div>
                                        <pre className="p-4 text-green-400 font-mono text-sm overflow-x-auto bg-black">
                                            <code>{currentSectionData.code}</code>
                                        </pre>
                                    </div>
                                </div>
                            )}

                            {/* Tips */}
                            {currentSectionData.tips && (
                                <div className="mb-6">
                                    <h3 className="text-lg font-semibold text-white mb-3">💡 Tips</h3>
                                    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                                        <ul className="space-y-2">
                                            {currentSectionData.tips.map((tip, index) => (
                                                <li key={index} className="text-blue-200 flex items-start">
                                                    <span className="text-blue-400 mr-2">•</span>
                                                    {tip}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}

                            {/* Next Steps */}
                            {currentSectionData.nextSteps && (
                                <div className="mb-6">
                                    <h3 className="text-lg font-semibold text-white mb-3">🚀 Try These Next</h3>
                                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                                        <ul className="space-y-2">
                                            {currentSectionData.nextSteps.map((step, index) => (
                                                <li key={index} className="text-green-200 flex items-start">
                                                    <span className="text-green-400 mr-2">→</span>
                                                    {step}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    </div>

                    {/* Section Navigation */}
                    <div className="w-64 bg-gray-900 border-l border-gray-700 p-4">
                        <h3 className="font-semibold text-white mb-4">Sections</h3>
                        <div className="space-y-2">
                            {selectedTutorial.sections.map((section, index) => (
                                <button
                                    key={section.id}
                                    onClick={() => setCurrentSection(index)}
                                    className={`w-full text-left p-3 rounded-lg transition-colors ${index === currentSection
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-300 hover:bg-gray-700'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm">{section.title}</span>
                                        {completedSections.has(section.id) && (
                                            <span className="text-green-400">✓</span>
                                        )}
                                    </div>
                                </button>
                            ))}
                        </div>

                        <div className="mt-6 pt-4 border-t border-gray-700">
                            <button
                                onClick={() => markSectionComplete(currentSectionData.id)}
                                disabled={completedSections.has(currentSectionData.id)}
                                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${completedSections.has(currentSectionData.id)
                                        ? 'bg-green-600 text-white cursor-not-allowed'
                                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                                    }`}
                            >
                                {completedSections.has(currentSectionData.id) ? 'Completed ✓' : 'Mark Complete'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Navigation Controls */}
                <div className="bg-gray-900 border-t border-gray-700 p-4 flex justify-between">
                    <button
                        onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
                        disabled={currentSection === 0}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${currentSection === 0
                                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                : 'bg-gray-600 hover:bg-gray-700 text-white'
                            }`}
                    >
                        Previous
                    </button>

                    <span className="text-gray-400 self-center">
                        {Math.round(progress)}% Complete
                    </span>

                    <button
                        onClick={() => setCurrentSection(Math.min(selectedTutorial.sections.length - 1, currentSection + 1))}
                        disabled={currentSection === selectedTutorial.sections.length - 1}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${currentSection === selectedTutorial.sections.length - 1
                                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700 text-white'
                            }`}
                    >
                        Next
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-gray-900 border-b border-gray-700 p-6">
                <h1 className="text-3xl font-bold text-white mb-2">AetherScript Tutorials</h1>
                <p className="text-gray-400">
                    Interactive guides to master consciousness programming
                </p>
            </div>

            {/* Filters */}
            <div className="bg-gray-900 border-b border-gray-700 p-4">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search tutorials..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        />
                    </div>
                    <div className="flex gap-4">
                        <select
                            value={filterDifficulty}
                            onChange={(e) => setFilterDifficulty(e.target.value)}
                            className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        >
                            {difficulties.map(difficulty => (
                                <option key={difficulty} value={difficulty}>
                                    {difficulty === 'all' ? 'All Levels' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                                </option>
                            ))}
                        </select>
                        <select
                            value={filterCategory}
                            onChange={(e) => setFilterCategory(e.target.value)}
                            className="bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        >
                            {categories.map(category => (
                                <option key={category} value={category}>
                                    {category === 'all' ? 'All Categories' : category}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Tutorial Grid */}
            <div className="flex-1 p-6 overflow-y-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <AnimatePresence>
                        {filteredTutorials.map((tutorial) => (
                            <motion.div
                                key={tutorial.id}
                                layout
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                transition={{ duration: 0.3 }}
                                className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors cursor-pointer"
                                onClick={() => setSelectedTutorial(tutorial)}
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <h3 className="font-bold text-white text-lg">{tutorial.title}</h3>
                                    <span className={`text-xs px-2 py-1 rounded ${getDifficultyColor(tutorial.difficulty)}`}>
                                        {tutorial.difficulty}
                                    </span>
                                </div>

                                <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                                    {tutorial.description}
                                </p>

                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-blue-400">{tutorial.category}</span>
                                    <div className="flex items-center space-x-4 text-gray-400">
                                        <span>⏱️ {tutorial.estimatedTime}min</span>
                                        <span>📝 {tutorial.sections.length} sections</span>
                                    </div>
                                </div>

                                <div className="mt-4 pt-4 border-t border-gray-700">
                                    <span className="text-blue-400 text-sm">Start Tutorial →</span>
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>

                {filteredTutorials.length === 0 && (
                    <div className="text-center py-12">
                        <div className="text-4xl mb-4">📚</div>
                        <h3 className="text-xl font-bold text-white mb-2">No tutorials found</h3>
                        <p className="text-gray-400">
                            Try adjusting your search criteria or browse all tutorials
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
