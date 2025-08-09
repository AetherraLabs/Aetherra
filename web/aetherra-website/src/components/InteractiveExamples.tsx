import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface CodeExample {
    id: string;
    title: string;
    description: string;
    category: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    code: string;
    expectedOutput?: string;
    explanation: string;
    concepts: string[];
    modifications: Modification[];
}

interface Modification {
    id: string;
    title: string;
    description: string;
    codeChange: string;
    expectedResult: string;
}

interface ExecutionResult {
    success: boolean;
    output?: string;
    error?: string;
    executionTime?: number;
    memoryUsage?: number;
    warnings?: string[];
}

const codeExamples: CodeExample[] = [
    {
        id: 'basic-consciousness',
        title: 'Basic Consciousness Creation',
        description: 'Create and initialize a simple consciousness entity',
        category: 'Fundamentals',
        difficulty: 'beginner',
        code: `// Create a basic consciousness
consciousness SimpleAI {
  state: "dormant"
  awareness: 0.0
  energy: 100

  // Initialization
  init() {
    this.state = "awakening"
    this.awareness = 0.3
    this.log("Consciousness activated!")
    return this
  }

  // Basic thinking process
  think(input) {
    this.energy -= 5
    this.awareness += 0.1

    if this.awareness > 1.0 {
      this.awareness = 1.0
    }

    return "Processing: " + input + " (awareness: " + this.awareness + ")"
  }
}

// Create and use the consciousness
let ai = new SimpleAI()
ai.init()
let result = ai.think("What is consciousness?")
console.log(result)`,
        expectedOutput: `Consciousness activated!
Processing: What is consciousness? (awareness: 0.4)`,
        explanation: `This example demonstrates the basic structure of an AetherScript consciousness. Key concepts:
• Consciousness definition with state properties
• Initialization method to set up the entity
• State modification through methods
• Energy and awareness as core metrics`,
        concepts: ['consciousness', 'state management', 'initialization', 'basic methods'],
        modifications: [
            {
                id: 'add-emotions',
                title: 'Add Emotional State',
                description: 'Add an emotion property that changes with awareness',
                codeChange: `// Add this property after energy:
emotion: "neutral"

// Add this in the think method after awareness update:
if this.awareness > 0.7 {
  this.emotion = "curious"
} else if this.awareness > 0.5 {
  this.emotion = "interested"
}`,
                expectedResult: 'The consciousness will now track and update emotional states based on awareness levels'
            },
            {
                id: 'energy-management',
                title: 'Energy Recovery',
                description: 'Add a rest method to recover energy',
                codeChange: `// Add this method to the consciousness:
rest() {
  this.energy += 20
  this.state = "resting"
  this.log("Resting... energy restored to " + this.energy)

  if this.energy > 100 {
    this.energy = 100
  }
}`,
                expectedResult: 'The consciousness can now recover energy through resting'
            }
        ]
    },
    {
        id: 'memory-system',
        title: 'Memory Storage and Retrieval',
        description: 'Implement a consciousness with memory capabilities',
        category: 'Memory',
        difficulty: 'intermediate',
        code: `consciousness MemoryAI {
  state: "learning"
  memories: MemoryBank(capacity: 50, type: "episodic")
  knowledge: SemanticMemory()

  init() {
    this.state = "active"
    this.memories.configure({
      compression: true,
      priority_weighting: true
    })
    return this
  }

  // Store an experience
  remember(experience, importance = 0.5) {
    let memory_entry = {
      content: experience,
      timestamp: time.now(),
      importance: importance,
      context: this.get_current_context(),
      emotional_weight: this.calculate_emotional_impact(experience)
    }

    this.memories.store(memory_entry)

    // Extract knowledge
    let concepts = this.extract_concepts(experience)
    this.knowledge.learn(concepts)

    this.log("Memory stored: " + experience.substring(0, 30) + "...")
    return memory_entry.id
  }

  // Recall memories by pattern
  recall(query, limit = 5) {
    let memories = this.memories.search(query, {
      semantic_search: true,
      temporal_relevance: true,
      importance_threshold: 0.3
    })

    // Rank by relevance
    memories = memories.sort((a, b) => b.relevance - a.relevance)

    return memories.slice(0, limit).map(m => ({
      content: m.content,
      relevance: m.relevance,
      age: time.since(m.timestamp)
    }))
  }

  // Learn patterns from memories
  consolidate_learning() {
    let all_memories = this.memories.get_all()
    let patterns = pattern_recognition.analyze(all_memories)

    for pattern in patterns {
      if pattern.confidence > 0.8 {
        this.knowledge.store_pattern(pattern)
      }
    }

    return patterns.length
  }

  // Helper methods
  get_current_context() {
    return {
      state: this.state,
      recent_activity: this.memories.get_recent(5),
      environment: environment.current_state()
    }
  }

  calculate_emotional_impact(experience) {
    // Simple sentiment analysis
    let positive_words = ["good", "great", "amazing", "wonderful", "success"]
    let negative_words = ["bad", "terrible", "awful", "failure", "error"]

    let score = 0.5 // neutral
    for word in positive_words {
      if experience.includes(word) { score += 0.1 }
    }
    for word in negative_words {
      if experience.includes(word) { score -= 0.1 }
    }

    return Math.max(0, Math.min(1, score))
  }

  extract_concepts(experience) {
    // Extract key concepts from experience
    let words = experience.toLowerCase().split(" ")
    let concepts = words.filter(word => word.length > 3)
    return concepts.unique()
  }
}

// Usage example
let memory_ai = new MemoryAI()
memory_ai.init()

// Store some experiences
memory_ai.remember("I learned about neural networks today", 0.8)
memory_ai.remember("Had a great conversation about AI consciousness", 0.9)
memory_ai.remember("Debugging was frustrating but I solved the problem", 0.6)

// Recall memories
let recalled = memory_ai.recall("learning")
console.log("Recalled memories:", recalled)

// Consolidate learning
let patterns_found = memory_ai.consolidate_learning()
console.log("Patterns discovered:", patterns_found)`,
        expectedOutput: `Memory stored: I learned about neural networks...
Memory stored: Had a great conversation about...
Memory stored: Debugging was frustrating but...
Recalled memories: [
  {content: "I learned about neural networks today", relevance: 0.85, age: "2 seconds"},
  {content: "Had a great conversation about AI consciousness", relevance: 0.72, age: "1 second"}
]
Patterns discovered: 3`,
        explanation: `This example shows advanced memory management in AetherScript:
• Multiple memory types (episodic and semantic)
• Importance-based storage with emotional weighting
• Semantic search capabilities
• Pattern recognition and learning consolidation
• Context-aware memory formation`,
        concepts: ['memory systems', 'pattern recognition', 'semantic search', 'learning consolidation'],
        modifications: [
            {
                id: 'forgetting',
                title: 'Implement Forgetting',
                description: 'Add selective forgetting based on age and importance',
                codeChange: `// Add this method:
forget_old_memories() {
  let cutoff_time = time.now() - duration("1 week")
  let forgotten = this.memories.remove_where(memory =>
    memory.timestamp < cutoff_time && memory.importance < 0.3
  )
  this.log("Forgot " + forgotten.length + " old memories")
}`,
                expectedResult: 'The AI will now forget old, unimportant memories to manage capacity'
            }
        ]
    },
    {
        id: 'neural-learning',
        title: 'Neural Network Learning',
        description: 'Implement a consciousness with adaptive neural processing',
        category: 'Neural Networks',
        difficulty: 'advanced',
        code: `consciousness NeuralLearner {
  state: "training"
  network: AdaptiveNetwork({
    layers: [64, 128, 64, 32, 16],
    activation: "relu",
    learning_rate: 0.001,
    dropout: 0.2
  })

  training_data: DataSet()
  performance_history: []
  learning_rate_scheduler: AdaptiveLR(initial: 0.001)

  init() {
    this.state = "ready"
    this.network.initialize_weights("xavier")
    this.setup_training_pipeline()
    return this
  }

  // Train on new data
  learn(input_data, target_output, validation_split = 0.2) {
    this.state = "learning"

    // Prepare data
    let [train_data, val_data] = this.split_data(input_data, target_output, validation_split)

    let epoch = 0
    let best_loss = Infinity
    let patience = 10
    let patience_counter = 0

    while epoch < 1000 && patience_counter < patience {
      // Training phase
      let train_loss = this.train_epoch(train_data)

      // Validation phase
      let val_loss = this.validate(val_data)

      // Update learning rate
      this.learning_rate_scheduler.step(val_loss)

      // Early stopping
      if val_loss < best_loss {
        best_loss = val_loss
        patience_counter = 0
        this.network.save_checkpoint()
      } else {
        patience_counter++
      }

      // Record performance
      this.performance_history.push({
        epoch: epoch,
        train_loss: train_loss,
        val_loss: val_loss,
        learning_rate: this.learning_rate_scheduler.current_lr
      })

      epoch++

      if epoch % 10 == 0 {
        this.log("Epoch " + epoch + ": train_loss=" + train_loss.toFixed(4) +
                 ", val_loss=" + val_loss.toFixed(4))
      }
    }

    this.state = "trained"
    return {
      epochs_trained: epoch,
      final_loss: best_loss,
      converged: patience_counter < patience
    }
  }

  // Process new input
  process(input) {
    let normalized_input = this.normalize(input)
    let output = this.network.forward(normalized_input)

    // Apply post-processing
    let processed_output = this.denormalize(output)

    // Update internal state based on processing
    this.update_internal_state(input, processed_output)

    return processed_output
  }

  // Adaptive processing with feedback
  process_with_feedback(input, expected_output = null) {
    let output = this.process(input)

    if expected_output != null {
      // Calculate error and learn
      let error = this.calculate_error(output, expected_output)
      this.backpropagate(error)

      // Adjust confidence based on error
      let confidence = 1.0 - Math.min(1.0, error.magnitude)

      return {
        output: output,
        confidence: confidence,
        error: error.magnitude,
        learned: true
      }
    }

    return {
      output: output,
      confidence: this.estimate_confidence(output),
      learned: false
    }
  }

  // Analyze learning progress
  analyze_performance() {
    if this.performance_history.length == 0 {
      return { status: "no_training_data" }
    }

    let recent_performance = this.performance_history.slice(-10)
    let avg_recent_loss = recent_performance.reduce((sum, p) => sum + p.val_loss, 0) / recent_performance.length

    let first_loss = this.performance_history[0].val_loss
    let improvement = (first_loss - avg_recent_loss) / first_loss

    let learning_trend = this.calculate_trend(recent_performance.map(p => p.val_loss))

    return {
      total_epochs: this.performance_history.length,
      improvement_percentage: improvement * 100,
      current_loss: avg_recent_loss,
      learning_trend: learning_trend, // 'improving', 'stable', 'degrading'
      converged: Math.abs(learning_trend) < 0.001
    }
  }

  // Helper methods
  train_epoch(data) {
    let total_loss = 0
    let batch_size = 32

    for batch in data.batches(batch_size) {
      let loss = this.network.train_batch(batch.inputs, batch.targets)
      total_loss += loss
    }

    return total_loss / data.size()
  }

  validate(data) {
    let total_loss = 0

    for sample in data {
      let output = this.network.forward(sample.input)
      let loss = this.calculate_loss(output, sample.target)
      total_loss += loss
    }

    return total_loss / data.size()
  }

  estimate_confidence(output) {
    // Estimate confidence based on output distribution
    let entropy = this.calculate_entropy(output)
    return 1.0 - entropy / Math.log(output.length)
  }

  calculate_trend(values) {
    if values.length < 2 return 0

    let sum_x = values.length * (values.length + 1) / 2
    let sum_y = values.reduce((a, b) => a + b, 0)
    let sum_xy = values.reduce((sum, y, x) => sum + y * (x + 1), 0)
    let sum_x2 = values.length * (values.length + 1) * (2 * values.length + 1) / 6

    let slope = (values.length * sum_xy - sum_x * sum_y) / (values.length * sum_x2 - sum_x * sum_x)
    return slope
  }
}

// Usage example
let neural_ai = new NeuralLearner()
neural_ai.init()

// Generate training data
let training_inputs = generate_sample_data(1000, 64)
let training_targets = generate_sample_targets(1000, 16)

// Train the network
let training_result = neural_ai.learn(training_inputs, training_targets)
console.log("Training completed:", training_result)

// Test processing
let test_input = generate_sample_data(1, 64)[0]
let result = neural_ai.process_with_feedback(test_input)
console.log("Processing result:", result)

// Analyze performance
let analysis = neural_ai.analyze_performance()
console.log("Performance analysis:", analysis)`,
        expectedOutput: `Epoch 10: train_loss=0.4523, val_loss=0.4891
Epoch 20: train_loss=0.3421, val_loss=0.3892
...
Training completed: {epochs_trained: 85, final_loss: 0.1234, converged: true}
Processing result: {output: [0.23, 0.67, ...], confidence: 0.89, error: 0.11, learned: true}
Performance analysis: {total_epochs: 85, improvement_percentage: 78.5, current_loss: 0.1234, learning_trend: 'stable', converged: true}`,
        explanation: `This advanced example demonstrates neural network integration in consciousness:
• Adaptive neural network with configurable architecture
• Training with validation and early stopping
• Learning rate scheduling and optimization
• Real-time learning with feedback
• Performance monitoring and analysis
• Confidence estimation for outputs`,
        concepts: ['neural networks', 'adaptive learning', 'performance monitoring', 'confidence estimation'],
        modifications: [
            {
                id: 'transfer-learning',
                title: 'Add Transfer Learning',
                description: 'Enable loading pre-trained weights and fine-tuning',
                codeChange: `// Add this method:
load_pretrained(model_path, freeze_layers = 0) {
  let pretrained_weights = load_model(model_path)
  this.network.load_weights(pretrained_weights, freeze_layers)
  this.log("Loaded pretrained model, froze " + freeze_layers + " layers")
}`,
                expectedResult: 'The network can now leverage pre-trained knowledge for faster learning'
            }
        ]
    },
    {
        id: 'pattern-evolution',
        title: 'Evolutionary Pattern Learning',
        description: 'Implement consciousness that evolves its pattern recognition',
        category: 'Evolution',
        difficulty: 'advanced',
        code: `consciousness EvolutionaryAI {
  state: "evolving"
  population: GeneticPopulation(size: 50)
  pattern_library: PatternLibrary()
  generation: 0
  fitness_history: []

  init() {
    this.state = "ready"
    this.initialize_population()
    this.setup_evolution_parameters()
    return this
  }

  // Initialize genetic population
  initialize_population() {
    for i in range(this.population.size) {
      let individual = this.create_random_pattern_recognizer()
      this.population.add(individual)
    }
    this.log("Initialized population of " + this.population.size + " individuals")
  }

  // Evolve pattern recognition capabilities
  evolve(training_data, generations = 100) {
    this.state = "evolving"

    for gen in range(generations) {
      this.generation = gen

      // Evaluate fitness of all individuals
      let fitness_scores = this.evaluate_population(training_data)

      // Selection
      let selected = this.tournament_selection(fitness_scores, selection_pressure: 0.7)

      // Crossover and mutation
      let new_population = []
      while new_population.length < this.population.size {
        let parent1 = selected.random()
        let parent2 = selected.random()

        let [child1, child2] = this.crossover(parent1, parent2)

        child1 = this.mutate(child1, mutation_rate: 0.1)
        child2 = this.mutate(child2, mutation_rate: 0.1)

        new_population.push(child1, child2)
      }

      // Replace population
      this.population.replace(new_population.slice(0, this.population.size))

      // Track progress
      let best_fitness = Math.max(...fitness_scores)
      let avg_fitness = fitness_scores.reduce((a, b) => a + b, 0) / fitness_scores.length

      this.fitness_history.push({
        generation: gen,
        best_fitness: best_fitness,
        avg_fitness: avg_fitness,
        diversity: this.calculate_diversity()
      })

      if gen % 10 == 0 {
        this.log("Generation " + gen + ": best=" + best_fitness.toFixed(3) +
                 ", avg=" + avg_fitness.toFixed(3))
      }

      // Early termination if converged
      if this.check_convergence() {
        this.log("Evolution converged at generation " + gen)
        break
      }
    }

    this.state = "evolved"
    return this.get_best_individual()
  }

  // Recognize patterns using evolved capabilities
  recognize_pattern(input_data) {
    let best_individual = this.get_best_individual()
    let recognition_results = []

    // Apply multiple pattern recognizers
    for recognizer in this.population.top(5) {
      let result = recognizer.process(input_data)
      recognition_results.push({
        pattern: result.pattern,
        confidence: result.confidence,
        features: result.features
      })
    }

    // Ensemble decision
    let consensus = this.calculate_consensus(recognition_results)

    // Learn from successful recognitions
    if consensus.confidence > 0.8 {
      this.pattern_library.add_successful_pattern(consensus.pattern)
    }

    return consensus
  }

  // Adapt to new pattern types
  adapt_to_new_patterns(new_pattern_data) {
    this.state = "adapting"

    // Evaluate current population on new patterns
    let adaptation_scores = this.evaluate_adaptation(new_pattern_data)

    // Identify individuals that adapt well
    let adaptable_individuals = this.population.filter((ind, i) => adaptation_scores[i] > 0.5)

    if adaptable_individuals.length < this.population.size * 0.3 {
      // Trigger rapid evolution for adaptation
      this.rapid_adaptation_evolution(new_pattern_data, generations: 20)
    } else {
      // Fine-tune existing population
      this.fine_tune_adaptation(new_pattern_data)
    }

    this.state = "adapted"
  }

  // Helper methods
  create_random_pattern_recognizer() {
    return PatternRecognizer({
      feature_extractors: this.random_feature_extractors(),
      classifier: this.random_classifier(),
      preprocessing: this.random_preprocessing(),
      weights: this.random_weights()
    })
  }

  evaluate_population(data) {
    let scores = []
    for individual in this.population.individuals {
      let score = this.evaluate_individual(individual, data)
      scores.push(score)
    }
    return scores
  }

  evaluate_individual(individual, data) {
    let correct = 0
    let total = data.length

    for sample in data {
      let result = individual.process(sample.input)
      if result.pattern == sample.expected_pattern {
        correct++
      }
    }

    let accuracy = correct / total
    let complexity_penalty = individual.complexity() * 0.01

    return accuracy - complexity_penalty
  }

  tournament_selection(fitness_scores, selection_pressure) {
    let selected = []
    let tournament_size = Math.max(2, Math.floor(this.population.size * 0.1))

    for i in range(this.population.size) {
      let tournament = []
      for j in range(tournament_size) {
        let idx = Math.floor(Math.random() * this.population.size)
        tournament.push({individual: this.population.individuals[idx], fitness: fitness_scores[idx]})
      }

      tournament.sort((a, b) => b.fitness - a.fitness)
      selected.push(tournament[0].individual)
    }

    return selected
  }

  crossover(parent1, parent2) {
    // Combine features from both parents
    let child1_features = parent1.features.slice(0, parent1.features.length / 2)
                         .concat(parent2.features.slice(parent2.features.length / 2))

    let child2_features = parent2.features.slice(0, parent2.features.length / 2)
                         .concat(parent1.features.slice(parent1.features.length / 2))

    return [
      this.create_individual_from_features(child1_features),
      this.create_individual_from_features(child2_features)
    ]
  }

  mutate(individual, mutation_rate) {
    if Math.random() < mutation_rate {
      // Randomly modify one component
      let component = ["features", "classifier", "preprocessing"].random()
      individual.mutate_component(component)
    }
    return individual
  }

  calculate_consensus(results) {
    let pattern_votes = {}
    let total_confidence = 0

    for result in results {
      pattern_votes[result.pattern] = (pattern_votes[result.pattern] || 0) + result.confidence
      total_confidence += result.confidence
    }

    let best_pattern = Object.keys(pattern_votes).reduce((a, b) =>
      pattern_votes[a] > pattern_votes[b] ? a : b
    )

    return {
      pattern: best_pattern,
      confidence: pattern_votes[best_pattern] / total_confidence,
      votes: pattern_votes
    }
  }
}

// Usage example
let evo_ai = new EvolutionaryAI()
evo_ai.init()

// Generate training data
let pattern_data = generate_pattern_dataset(1000)

// Evolve pattern recognition
let best_recognizer = evo_ai.evolve(pattern_data, generations: 50)
console.log("Evolution completed, best fitness:", best_recognizer.fitness)

// Test pattern recognition
let test_pattern = generate_test_pattern()
let recognition = evo_ai.recognize_pattern(test_pattern)
console.log("Pattern recognition result:", recognition)

// Adapt to new patterns
let new_patterns = generate_new_pattern_types(100)
evo_ai.adapt_to_new_patterns(new_patterns)
console.log("Adaptation completed")`,
        expectedOutput: `Initialized population of 50 individuals
Generation 10: best=0.672, avg=0.423
Generation 20: best=0.789, avg=0.567
Generation 30: best=0.845, avg=0.678
Evolution converged at generation 34
Evolution completed, best fitness: 0.845
Pattern recognition result: {pattern: "spiral", confidence: 0.87, votes: {...}}
Adaptation completed`,
        explanation: `This example showcases evolutionary consciousness development:
• Genetic algorithm for evolving pattern recognition
• Population-based learning with selection and mutation
• Adaptive evolution for new pattern types
• Ensemble decision making from multiple recognizers
• Convergence detection and early stopping
• Continuous adaptation to new environments`,
        concepts: ['evolutionary algorithms', 'genetic programming', 'adaptive systems', 'ensemble learning'],
        modifications: [
            {
                id: 'multi-objective',
                title: 'Multi-Objective Evolution',
                description: 'Evolve for both accuracy and efficiency simultaneously',
                codeChange: `// Modify evaluate_individual method:
evaluate_individual(individual, data) {
  let accuracy = this.calculate_accuracy(individual, data)
  let efficiency = 1.0 / individual.processing_time()
  let simplicity = 1.0 / individual.complexity()

  // Multi-objective fitness
  return {
    accuracy: accuracy,
    efficiency: efficiency,
    simplicity: simplicity,
    combined: accuracy * 0.6 + efficiency * 0.3 + simplicity * 0.1
  }
}`,
                expectedResult: 'Evolution will optimize for multiple objectives simultaneously'
            }
        ]
    }
];

export function InteractiveExamples() {
    const [selectedExample, setSelectedExample] = useState<CodeExample | null>(null);
    const [modifiedCode, setModifiedCode] = useState('');
    const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
    const [isExecuting, setIsExecuting] = useState(false);
    const [activeModification, setActiveModification] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterDifficulty, setFilterDifficulty] = useState<string>('all');
    const [filterCategory, setFilterCategory] = useState<string>('all');

    const difficulties = ['all', 'beginner', 'intermediate', 'advanced'];
    const categories = ['all', ...Array.from(new Set(codeExamples.map(ex => ex.category)))];

    const filteredExamples = codeExamples.filter(example => {
        const matchesSearch = example.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            example.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesDifficulty = filterDifficulty === 'all' || example.difficulty === filterDifficulty;
        const matchesCategory = filterCategory === 'all' || example.category === filterCategory;

        return matchesSearch && matchesDifficulty && matchesCategory;
    });

    useEffect(() => {
        if (selectedExample) {
            setModifiedCode(selectedExample.code);
            setExecutionResult(null);
            setActiveModification(null);
        }
    }, [selectedExample]);

    const executeCode = async (code: string) => {
        setIsExecuting(true);
        setExecutionResult(null);

        // Simulate code execution
        await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));

        // Simulate different execution outcomes
        const outcomes = [
            {
                success: true,
                output: selectedExample?.expectedOutput || "Execution completed successfully",
                executionTime: 245 + Math.random() * 500,
                memoryUsage: 12.5 + Math.random() * 20,
                warnings: Math.random() > 0.7 ? ["Performance could be optimized"] : []
            },
            {
                success: false,
                error: "NameError: 'undefined_variable' is not defined at line 23",
                executionTime: 89,
                memoryUsage: 5.2
            },
            {
                success: true,
                output: "Modified execution result with enhanced output",
                executionTime: 156,
                memoryUsage: 8.7,
                warnings: ["Consciousness safety check: All parameters within safe ranges"]
            }
        ];

        // Choose outcome based on code complexity
        const outcome = code.includes('error') || code.includes('undefined')
            ? outcomes[1]
            : outcomes[Math.random() > 0.8 ? 2 : 0];

        setExecutionResult(outcome);
        setIsExecuting(false);
    };

    const applyModification = (modification: Modification) => {
        if (!selectedExample) return;

        let newCode = selectedExample.code;

        // Simple code modification simulation
        if (modification.id === 'add-emotions') {
            newCode = newCode.replace(
                'energy: 100',
                'energy: 100\n  emotion: "neutral"'
            );
            newCode = newCode.replace(
                'this.awareness = 1.0\n    }',
                `this.awareness = 1.0\n    }\n    \n    if this.awareness > 0.7 {\n      this.emotion = "curious"\n    } else if this.awareness > 0.5 {\n      this.emotion = "interested"\n    }`
            );
        }

        setModifiedCode(newCode);
        setActiveModification(modification.id);
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'text-green-400 bg-green-600/20';
            case 'intermediate': return 'text-yellow-400 bg-yellow-600/20';
            case 'advanced': return 'text-red-400 bg-red-600/20';
            default: return 'text-gray-400 bg-gray-600/20';
        }
    };

    if (!selectedExample) {
        return (
            <div className="h-full flex flex-col">
                {/* Header */}
                <div className="bg-gray-900 border-b border-gray-700 p-6">
                    <h1 className="text-3xl font-bold text-white mb-2">Interactive Code Examples</h1>
                    <p className="text-gray-400">
                        Click and run AetherScript examples to see consciousness programming in action
                    </p>
                </div>

                {/* Filters */}
                <div className="bg-gray-900 border-b border-gray-700 p-4">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1">
                            <input
                                type="text"
                                placeholder="Search examples..."
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

                {/* Examples Grid */}
                <div className="flex-1 p-6 overflow-y-auto">
                    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        <AnimatePresence>
                            {filteredExamples.map((example) => (
                                <motion.div
                                    key={example.id}
                                    layout
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    transition={{ duration: 0.3 }}
                                    className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-colors cursor-pointer"
                                    onClick={() => setSelectedExample(example)}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <h3 className="font-bold text-white text-lg">{example.title}</h3>
                                        <span className={`text-xs px-2 py-1 rounded ${getDifficultyColor(example.difficulty)}`}>
                                            {example.difficulty}
                                        </span>
                                    </div>

                                    <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                                        {example.description}
                                    </p>

                                    <div className="mb-4">
                                        <div className="text-xs text-blue-400 mb-2">{example.category}</div>
                                        <div className="flex flex-wrap gap-1">
                                            {example.concepts.slice(0, 3).map(concept => (
                                                <span
                                                    key={concept}
                                                    className="bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded"
                                                >
                                                    {concept}
                                                </span>
                                            ))}
                                            {example.concepts.length > 3 && (
                                                <span className="text-gray-400 text-xs">
                                                    +{example.concepts.length - 3}
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <span className="text-gray-400 text-sm">
                                            {example.modifications.length} modifications
                                        </span>
                                        <span className="text-blue-400 text-sm">
                                            Run Example →
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>

                    {filteredExamples.length === 0 && (
                        <div className="text-center py-12">
                            <div className="text-4xl mb-4">💻</div>
                            <h3 className="text-xl font-bold text-white mb-2">No examples found</h3>
                            <p className="text-gray-400">
                                Try adjusting your search criteria or browse all examples
                            </p>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-gray-900 border-b border-gray-700 p-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setSelectedExample(null)}
                            className="text-blue-400 hover:text-blue-300"
                        >
                            ← Back to Examples
                        </button>
                        <div>
                            <h1 className="text-xl font-bold text-white">{selectedExample.title}</h1>
                            <p className="text-gray-400 text-sm">{selectedExample.description}</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded ${getDifficultyColor(selectedExample.difficulty)}`}>
                            {selectedExample.difficulty}
                        </span>
                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                            {selectedExample.category}
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Code Editor */}
                <div className="flex-1 flex flex-col">
                    <div className="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-700">
                        <span className="text-green-400 font-mono text-sm">AetherScript Editor</span>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => executeCode(modifiedCode)}
                                disabled={isExecuting}
                                className={`px-4 py-1 rounded text-sm font-medium transition-colors ${isExecuting
                                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                        : 'bg-green-600 hover:bg-green-700 text-white'
                                    }`}
                            >
                                {isExecuting ? '🔄 Running...' : '▶️ Run Code'}
                            </button>
                            <button
                                onClick={() => setModifiedCode(selectedExample.code)}
                                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-1 rounded text-sm transition-colors"
                            >
                                🔄 Reset
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 relative">
                        <textarea
                            value={modifiedCode}
                            onChange={(e) => setModifiedCode(e.target.value)}
                            className="w-full h-full p-4 bg-black text-green-400 font-mono text-sm resize-none border-none outline-none"
                            style={{
                                textShadow: '0 0 5px currentColor',
                                background: 'radial-gradient(ellipse at center, rgba(0,255,0,0.03) 0%, rgba(0,0,0,1) 100%)'
                            }}
                        />
                        {/* Scanlines effect */}
                        <div
                            className="absolute inset-0 pointer-events-none opacity-20"
                            style={{
                                background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,0,0.1) 2px, rgba(0,255,0,0.1) 4px)'
                            }}
                        ></div>
                    </div>

                    {/* Output Panel */}
                    {executionResult && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-gray-900 border-t border-gray-700 p-4"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-white font-semibold">
                                    {executionResult.success ? '✅ Execution Result' : '❌ Execution Error'}
                                </span>
                                {executionResult.executionTime && (
                                    <span className="text-gray-400 text-sm">
                                        ⚡ {executionResult.executionTime.toFixed(0)}ms | 🧠 {executionResult.memoryUsage?.toFixed(1)}MB
                                    </span>
                                )}
                            </div>

                            <div className={`p-3 rounded font-mono text-sm ${executionResult.success ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'
                                }`}>
                                <pre className="whitespace-pre-wrap">
                                    {executionResult.success ? executionResult.output : executionResult.error}
                                </pre>
                            </div>

                            {executionResult.warnings && executionResult.warnings.length > 0 && (
                                <div className="mt-2 p-3 bg-yellow-900/30 text-yellow-300 rounded">
                                    <div className="font-semibold mb-1">⚠️ Warnings:</div>
                                    {executionResult.warnings.map((warning, index) => (
                                        <div key={index} className="text-sm">• {warning}</div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    )}
                </div>

                {/* Sidebar */}
                <div className="w-80 bg-gray-900 border-l border-gray-700 flex flex-col">
                    {/* Explanation */}
                    <div className="p-4 border-b border-gray-700">
                        <h3 className="font-semibold text-white mb-2">📖 Explanation</h3>
                        <div className="text-sm text-gray-300 space-y-2">
                            <div className="whitespace-pre-line">{selectedExample.explanation}</div>
                        </div>
                    </div>

                    {/* Concepts */}
                    <div className="p-4 border-b border-gray-700">
                        <h3 className="font-semibold text-white mb-2">🎯 Concepts</h3>
                        <div className="flex flex-wrap gap-2">
                            {selectedExample.concepts.map(concept => (
                                <span
                                    key={concept}
                                    className="bg-blue-600/20 text-blue-300 text-xs px-2 py-1 rounded"
                                >
                                    {concept}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Modifications */}
                    <div className="flex-1 overflow-y-auto">
                        <div className="p-4">
                            <h3 className="font-semibold text-white mb-3">🔧 Try These Modifications</h3>
                            <div className="space-y-3">
                                {selectedExample.modifications.map((modification) => (
                                    <div
                                        key={modification.id}
                                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${activeModification === modification.id
                                                ? 'border-blue-500 bg-blue-600/20'
                                                : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                                            }`}
                                        onClick={() => applyModification(modification)}
                                    >
                                        <h4 className="font-semibold text-white text-sm mb-1">
                                            {modification.title}
                                        </h4>
                                        <p className="text-gray-300 text-xs mb-2">
                                            {modification.description}
                                        </p>
                                        <p className="text-gray-400 text-xs">
                                            Expected: {modification.expectedResult}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
