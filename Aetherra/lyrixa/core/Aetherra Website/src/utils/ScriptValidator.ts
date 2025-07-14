interface ValidationError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
  type: 'syntax' | 'semantic' | 'performance';
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions: ValidationError[];
}

export class ScriptValidator {
  private aetherKeywords = [
    'lyrixa', 'neuralnet', 'memory_store', 'plugin_manager', 'reflex_engine',
    'thought_chain', 'consciousness', 'neural_pathway', 'synaptic_weight',
    'cognitive_load', 'memory_bank', 'plugin_chain', 'optimization_loop'
  ];

  private aetherFunctions = [
    'allocateMemory', 'deallocateMemory', 'loadPlugin', 'chainPlugins',
    'optimizeNeuralPathways', 'triggerReflex', 'storeThought', 'queryMemory',
    'activateConsciousness', 'processInput', 'generateOutput', 'learnPattern'
  ];

  private aetherTypes = [
    'LyrixaCore', 'NeuralNetwork', 'MemoryBank', 'PluginInterface',
    'ThoughtChain', 'ReflexEngine', 'ConsciousnessState', 'CognitiveLoad'
  ];

  public validateScript(script: string): ValidationResult {
    const lines = script.split('\n');
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    const suggestions: ValidationError[] = [];

    // Check for basic syntax issues
    this.validateSyntax(lines, errors, suggestions, warnings);
    
    // Check for semantic issues
    this.validateSemantics(lines, warnings, suggestions);
    
    // Check for performance issues
    this.validatePerformance(lines, warnings, suggestions);

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }

  public validate(script: string): Promise<ValidationResult> {
    return Promise.resolve(this.validateScript(script));
  }

  private validateSyntax(lines: string[], errors: ValidationError[], suggestions: ValidationError[], warnings: ValidationError[]): void {
    let braceCount = 0;
    let parenthesesCount = 0;
    let inString = false;
    let stringChar = '';

    lines.forEach((line, lineIndex) => {
      const trimmedLine = line.trim();
      
      // Skip empty lines and comments
      if (!trimmedLine || trimmedLine.startsWith('//')) return;

      // Check for unclosed strings
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        const prevChar = i > 0 ? line[i - 1] : '';

        if ((char === '"' || char === "'") && prevChar !== '\\') {
          if (!inString) {
            inString = true;
            stringChar = char;
          } else if (char === stringChar) {
            inString = false;
            stringChar = '';
          }
        }

        if (!inString) {
          if (char === '{') braceCount++;
          if (char === '}') braceCount--;
          if (char === '(') parenthesesCount++;
          if (char === ')') parenthesesCount--;
        }
      }

      // Check for missing semicolons (simple heuristic)
      if (trimmedLine && 
          !trimmedLine.endsWith('{') && 
          !trimmedLine.endsWith('}') && 
          !trimmedLine.endsWith(';') &&
          !trimmedLine.startsWith('//') &&
          !trimmedLine.includes('function') &&
          !trimmedLine.includes('if') &&
          !trimmedLine.includes('for') &&
          !trimmedLine.includes('while')) {
        
        suggestions.push({
          line: lineIndex + 1,
          column: line.length,
          message: 'Consider adding semicolon at end of statement',
          severity: 'info',
          type: 'syntax'
        });
      }

      // Check for undefined variables (basic check)
      const variablePattern = /(\w+)\s*\(/g;
      let match;
      while ((match = variablePattern.exec(line)) !== null) {
        const funcName = match[1];
        if (!this.aetherFunctions.includes(funcName) && 
            !['console', 'Math', 'Date', 'Array', 'Object'].includes(funcName) &&
            !funcName.startsWith('new')) {
          
          warnings.push({
            line: lineIndex + 1,
            column: match.index + 1,
            message: `Function '${funcName}' is not a recognized AetherScript function`,
            severity: 'warning',
            type: 'semantic'
          });
        }
      }
    });

    // Check for unmatched braces
    if (braceCount !== 0) {
      errors.push({
        line: lines.length,
        column: 1,
        message: `Unmatched braces: ${braceCount > 0 ? 'missing closing' : 'extra closing'} brace(s)`,
        severity: 'error',
        type: 'syntax'
      });
    }

    // Check for unmatched parentheses
    if (parenthesesCount !== 0) {
      errors.push({
        line: lines.length,
        column: 1,
        message: `Unmatched parentheses: ${parenthesesCount > 0 ? 'missing closing' : 'extra closing'} parenthesis`,
        severity: 'error',
        type: 'syntax'
      });
    }

    // Check for unclosed strings
    if (inString) {
      errors.push({
        line: lines.length,
        column: 1,
        message: 'Unclosed string literal',
        severity: 'error',
        type: 'syntax'
      });
    }
  }

  private validateSemantics(lines: string[], warnings: ValidationError[], suggestions: ValidationError[]): void {
    let hasLyrixaCore = false;
    let memoryAllocations: number[] = [];
    let memoryDeallocations: number[] = [];

    lines.forEach((line, lineIndex) => {
      const trimmedLine = line.trim();

      // Check for LyrixaCore initialization
      if (trimmedLine.includes('new LyrixaCore')) {
        hasLyrixaCore = true;
      }

      // Track memory operations
      if (trimmedLine.includes('allocateMemory')) {
        memoryAllocations.push(lineIndex + 1);
      }
      if (trimmedLine.includes('deallocateMemory')) {
        memoryDeallocations.push(lineIndex + 1);
      }

      // Check for plugin loading without Lyrixa core
      if (trimmedLine.includes('loadPlugin') && !hasLyrixaCore) {
        warnings.push({
          line: lineIndex + 1,
          column: 1,
          message: 'Loading plugin without initializing LyrixaCore first',
          severity: 'warning',
          type: 'semantic'
        });
      }

      // Check for deprecated patterns
      if (trimmedLine.includes('var ')) {
        suggestions.push({
          line: lineIndex + 1,
          column: trimmedLine.indexOf('var ') + 1,
          message: 'Consider using "const" or "let" instead of "var"',
          severity: 'info',
          type: 'semantic'
        });
      }
    });

    // Check if LyrixaCore is used but not initialized
    const usesAetherFeatures = lines.some(line => 
      this.aetherKeywords.some(keyword => line.includes(keyword))
    );

    if (usesAetherFeatures && !hasLyrixaCore) {
      warnings.push({
        line: 1,
        column: 1,
        message: 'Using AetherScript features without initializing LyrixaCore',
        severity: 'warning',
        type: 'semantic'
      });
    }

    // Check for memory leaks
    if (memoryAllocations.length > memoryDeallocations.length) {
      suggestions.push({
        line: lines.length,
        column: 1,
        message: `Potential memory leak: ${memoryAllocations.length - memoryDeallocations.length} allocation(s) without corresponding deallocation`,
        severity: 'warning',
        type: 'performance'
      });
    }
  }

  private validatePerformance(lines: string[], warnings: ValidationError[], suggestions: ValidationError[]): void {
    let loopDepth = 0;
    let hasAsyncOperations = false;

    lines.forEach((line, lineIndex) => {
      const trimmedLine = line.trim();

      // Track loop nesting
      if (trimmedLine.includes('for') || trimmedLine.includes('while')) {
        loopDepth++;
      }
      if (trimmedLine === '}' && loopDepth > 0) {
        loopDepth--;
      }

      // Check for deeply nested loops
      if (loopDepth > 3) {
        warnings.push({
          line: lineIndex + 1,
          column: 1,
          message: 'Deeply nested loops may impact neural processing performance',
          severity: 'warning',
          type: 'performance'
        });
      }

      // Check for async operations
      if (trimmedLine.includes('await') || trimmedLine.includes('async')) {
        hasAsyncOperations = true;
      }

      // Check for large memory allocations
      const memoryMatch = trimmedLine.match(/allocateMemory\((\d+)\)/);
      if (memoryMatch) {
        const size = parseInt(memoryMatch[1]);
        if (size > 10000) {
          warnings.push({
            line: lineIndex + 1,
            column: trimmedLine.indexOf('allocateMemory') + 1,
            message: `Large memory allocation (${size} bytes) may impact performance`,
            severity: 'warning',
            type: 'performance'
          });
        }
      }

      // Suggest neural optimization for compute-intensive operations
      if (trimmedLine.includes('for') && 
          (trimmedLine.includes('neural') || trimmedLine.includes('process'))) {
        suggestions.push({
          line: lineIndex + 1,
          column: 1,
          message: 'Consider using neural vectorization for performance optimization',
          severity: 'info',
          type: 'performance'
        });
      }
    });

    // Suggest async patterns for complex scripts
    if (lines.length > 50 && !hasAsyncOperations) {
      suggestions.push({
        line: 1,
        column: 1,
        message: 'Large script detected - consider using async patterns for better neural processing',
        severity: 'info',
        type: 'performance'
      });
    }
  }
}

export const scriptValidator = new ScriptValidator();
