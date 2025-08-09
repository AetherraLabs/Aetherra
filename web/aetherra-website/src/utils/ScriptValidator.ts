// ScriptValidator.ts - Validates .aether scripts and warns about errors or missing fields

export interface ValidationError {
    line: number;
    column: number;
    type: 'error' | 'warning' | 'info';
    message: string;
    code: string;
}

export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
    warnings: ValidationError[];
    suggestions: ValidationError[];
}

export class ScriptValidator {
    private static readonly KEYWORDS = [
        'consciousness', 'memory', 'pathway', 'loop', 'sense', 'think', 'learn',
        'evolve', 'neural', 'pattern', 'awareness', 'input', 'output', 'process',
        'feedback', 'adaptation', 'plugin', 'chain', 'activate', 'store', 'recall'
    ];

    private static readonly REQUIRED_FUNCTIONS = [
        'consciousness.initialize', 'memory.load', 'sense', 'think', 'learn'
    ];

    private static readonly CONSCIOUSNESS_PATTERNS = [
        /consciousness\.initialize\(\)/,
        /memory\.load\(['"][^'"]*['"]\)/,
        /pathway\s+\w+\s*{/,
        /loop\s*{/,
        /plugins\.activate\(['"][^'"]*['"]\)/
    ];

    static validate(script: string): ValidationResult {
        const lines = script.split('\n');
        const errors: ValidationError[] = [];
        const warnings: ValidationError[] = [];
        const suggestions: ValidationError[] = [];

        let hasConsciousnessInit = false;
        let hasMemoryLoad = false;
        let hasMainLoop = false;
        let openBraces = 0;
        let pathwayCount = 0;

        lines.forEach((line, lineIndex) => {
            const trimmedLine = line.trim();
            const lineNumber = lineIndex + 1;

            // Skip comments and empty lines
            if (trimmedLine.startsWith('//') || trimmedLine === '') return;

            // Check for syntax errors
            this.checkSyntaxErrors(line, lineNumber, errors);

            // Check for required initializations
            if (trimmedLine.includes('consciousness.initialize()')) {
                hasConsciousnessInit = true;
            }

            if (trimmedLine.includes('memory.load(')) {
                hasMemoryLoad = true;
            }

            if (trimmedLine.includes('loop {')) {
                hasMainLoop = true;
            }

            // Count pathway definitions
            if (trimmedLine.includes('pathway ')) {
                pathwayCount++;
            }

            // Track brace matching
            openBraces += (line.match(/{/g) || []).length;
            openBraces -= (line.match(/}/g) || []).length;

            // Check for best practices
            this.checkBestPractices(line, lineNumber, warnings, suggestions);
        });

        // Check for required components
        if (!hasConsciousnessInit) {
            errors.push({
                line: 1,
                column: 1,
                type: 'error',
                message: 'Missing required consciousness.initialize() call',
                code: 'MISSING_CONSCIOUSNESS_INIT'
            });
        }

        if (!hasMemoryLoad) {
            warnings.push({
                line: 1,
                column: 1,
                type: 'warning',
                message: 'Consider adding memory.load() for neural patterns',
                code: 'MISSING_MEMORY_LOAD'
            });
        }

        if (!hasMainLoop) {
            suggestions.push({
                line: 1,
                column: 1,
                type: 'info',
                message: 'Consider adding a main consciousness loop for continuous operation',
                code: 'SUGGEST_MAIN_LOOP'
            });
        }

        // Check brace matching
        if (openBraces !== 0) {
            errors.push({
                line: lines.length,
                column: 1,
                type: 'error',
                message: `Unmatched braces: ${openBraces > 0 ? 'missing closing' : 'missing opening'} brace(s)`,
                code: 'UNMATCHED_BRACES'
            });
        }

        // Performance suggestions
        if (pathwayCount > 5) {
            suggestions.push({
                line: 1,
                column: 1,
                type: 'info',
                message: `Consider optimizing ${pathwayCount} pathways for better performance`,
                code: 'OPTIMIZE_PATHWAYS'
            });
        }

        const allErrors = [...errors, ...warnings, ...suggestions];

        return {
            isValid: errors.length === 0,
            errors,
            warnings,
            suggestions
        };
    }

    private static checkSyntaxErrors(line: string, lineNumber: number, errors: ValidationError[]) {
        const trimmedLine = line.trim();

        // Check for unterminated strings
        const quotes = (trimmedLine.match(/"/g) || []).length;
        if (quotes % 2 !== 0) {
            errors.push({
                line: lineNumber,
                column: trimmedLine.indexOf('"') + 1,
                type: 'error',
                message: 'Unterminated string literal',
                code: 'UNTERMINATED_STRING'
            });
        }

        // Check for invalid function calls
        const functionCallPattern = /(\w+)\.(\w+)\(/g;
        let match;
        while ((match = functionCallPattern.exec(trimmedLine)) !== null) {
            const [, object, method] = match;
            if (!this.isValidMethodCall(object, method)) {
                errors.push({
                    line: lineNumber,
                    column: match.index + 1,
                    type: 'error',
                    message: `Unknown method: ${object}.${method}()`,
                    code: 'UNKNOWN_METHOD'
                });
            }
        }

        // Check for undefined variables
        const variablePattern = /\b(\w+)\s*=/g;
        while ((match = variablePattern.exec(trimmedLine)) !== null) {
            const [, variable] = match;
            if (this.KEYWORDS.includes(variable)) {
                errors.push({
                    line: lineNumber,
                    column: match.index + 1,
                    type: 'error',
                    message: `Cannot assign to reserved keyword: ${variable}`,
                    code: 'RESERVED_KEYWORD'
                });
            }
        }
    }

    private static checkBestPractices(line: string, lineNumber: number, warnings: ValidationError[], suggestions: ValidationError[]) {
        const trimmedLine = line.trim();

        // Check for magic numbers
        const numberPattern = /\b\d{3,}\b/g;
        let match;
        while ((match = numberPattern.exec(trimmedLine)) !== null) {
            suggestions.push({
                line: lineNumber,
                column: match.index + 1,
                type: 'info',
                message: `Consider using a named constant instead of magic number: ${match[0]}`,
                code: 'MAGIC_NUMBER'
            });
        }

        // Check for long lines
        if (line.length > 100) {
            suggestions.push({
                line: lineNumber,
                column: 80,
                type: 'info',
                message: 'Consider breaking long lines for better readability',
                code: 'LONG_LINE'
            });
        }

        // Check for missing error handling
        if (trimmedLine.includes('memory.load(') && !trimmedLine.includes('try')) {
            warnings.push({
                line: lineNumber,
                column: 1,
                type: 'warning',
                message: 'Consider adding error handling for memory operations',
                code: 'MISSING_ERROR_HANDLING'
            });
        }

        // Check for performance issues
        if (trimmedLine.includes('loop {') && trimmedLine.includes('memory.load(')) {
            warnings.push({
                line: lineNumber,
                column: 1,
                type: 'warning',
                message: 'Loading memory inside loop may cause performance issues',
                code: 'PERFORMANCE_WARNING'
            });
        }
    }

    private static isValidMethodCall(object: string, method: string): boolean {
        const validMethods: Record<string, string[]> = {
            consciousness: ['initialize', 'process', 'evolve', 'status'],
            memory: ['load', 'store', 'recall', 'clear', 'optimize'],
            plugins: ['activate', 'deactivate', 'chain', 'status'],
            neural: ['connect', 'train', 'predict', 'optimize'],
            pathway: ['create', 'activate', 'process', 'optimize'],
            console: ['log', 'warn', 'error', 'info']
        };

        return validMethods[object]?.includes(method) ?? false;
    }

    static getCompletions(script: string, line: number, column: number): string[] {
        const lines = script.split('\n');
        const currentLine = lines[line - 1] || '';
        const beforeCursor = currentLine.substring(0, column);

        // Method completions
        if (beforeCursor.includes('consciousness.')) {
            return ['initialize()', 'process()', 'evolve()', 'status()'];
        }
        if (beforeCursor.includes('memory.')) {
            return ['load()', 'store()', 'recall()', 'clear()', 'optimize()'];
        }
        if (beforeCursor.includes('plugins.')) {
            return ['activate()', 'deactivate()', 'chain()', 'status()'];
        }

        // Keyword completions
        const partialWord = beforeCursor.split(/\s/).pop() || '';
        return this.KEYWORDS.filter(keyword =>
            keyword.toLowerCase().startsWith(partialWord.toLowerCase())
        );
    }

    static formatScript(script: string): string {
        const lines = script.split('\n');
        let indentLevel = 0;
        const indentSize = 2;

        return lines.map(line => {
            const trimmedLine = line.trim();

            if (trimmedLine === '') return '';

            // Decrease indent for closing braces
            if (trimmedLine === '}') {
                indentLevel = Math.max(0, indentLevel - 1);
            }

            const formattedLine = ' '.repeat(indentLevel * indentSize) + trimmedLine;

            // Increase indent for opening braces
            if (trimmedLine.endsWith('{')) {
                indentLevel++;
            }

            return formattedLine;
        }).join('\n');
    }
}
