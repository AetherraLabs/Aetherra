import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { ScriptValidator } from '../utils/ScriptValidator';

interface AutoCompleteItem {
    text: string;
    type: 'keyword' | 'method' | 'variable' | 'snippet';
    description: string;
    insertText: string;
}

interface AutoCompleteHelperProps {
    script: string;
    cursorPosition: { line: number; column: number };
    onInsert: (text: string) => void;
    isVisible: boolean;
    onClose: () => void;
}

export function AutoCompleteHelper({
    script,
    cursorPosition,
    onInsert,
    isVisible,
    onClose
}: AutoCompleteHelperProps) {
    const [suggestions, setSuggestions] = useState<AutoCompleteItem[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);

    useEffect(() => {
        if (isVisible) {
            generateSuggestions();
        }
    }, [script, cursorPosition, isVisible]);

    const generateSuggestions = () => {
        const lines = script.split('\n');
        const currentLine = lines[cursorPosition.line - 1] || '';
        const beforeCursor = currentLine.substring(0, cursorPosition.column);

        const suggestions: AutoCompleteItem[] = [];

        // Get completions from validator
        const validatorSuggestions = ScriptValidator.getCompletions(
            script,
            cursorPosition.line,
            cursorPosition.column
        );

        validatorSuggestions.forEach(suggestion => {
            if (suggestion.includes('()')) {
                suggestions.push({
                    text: suggestion,
                    type: 'method',
                    description: `Execute ${suggestion}`,
                    insertText: suggestion
                });
            } else {
                suggestions.push({
                    text: suggestion,
                    type: 'keyword',
                    description: `AetherScript keyword: ${suggestion}`,
                    insertText: suggestion
                });
            }
        });

        // Add code snippets
        const snippets = getCodeSnippets(beforeCursor);
        suggestions.push(...snippets);

        // Add context-aware suggestions
        const contextSuggestions = getContextualSuggestions(beforeCursor, currentLine);
        suggestions.push(...contextSuggestions);

        setSuggestions(suggestions.slice(0, 10)); // Limit to 10 suggestions
        setSelectedIndex(0);
    };

    const getCodeSnippets = (beforeCursor: string): AutoCompleteItem[] => {
        const snippets: AutoCompleteItem[] = [];

        if (beforeCursor.includes('pathway') || beforeCursor.trim() === '') {
            snippets.push({
                text: 'pathway template',
                type: 'snippet',
                description: 'Create a new consciousness pathway',
                insertText: `pathway consciousness_flow {
  input: sensory_data
  process: pattern_recognition
  output: conscious_thought

  feedback: learning_signals
  adaptation: weight_updates
}`
            });
        }

        if (beforeCursor.includes('loop') || beforeCursor.trim() === '') {
            snippets.push({
                text: 'consciousness loop',
                type: 'snippet',
                description: 'Main consciousness processing loop',
                insertText: `loop {
  data = sense()
  thought = think(data)
  learn(thought, data)
  evolve()
}`
            });
        }

        if (beforeCursor.includes('neural') || beforeCursor.trim() === '') {
            snippets.push({
                text: 'neural network',
                type: 'snippet',
                description: 'Define a neural network structure',
                insertText: `neural network pattern_recognizer {
  layers: [input(256), hidden(128), output(64)]
  activation: relu
  learning_rate: 0.001
}`
            });
        }

        return snippets;
    };

    const getContextualSuggestions = (beforeCursor: string, currentLine: string): AutoCompleteItem[] => {
        const suggestions: AutoCompleteItem[] = [];

        // Variable suggestions based on context
        if (beforeCursor.includes('=') && !currentLine.includes('memory.')) {
            suggestions.push({
                text: 'sensory_data',
                type: 'variable',
                description: 'Input from sensory systems',
                insertText: 'sensory_data'
            });
            suggestions.push({
                text: 'neural_patterns',
                type: 'variable',
                description: 'Stored neural pattern data',
                insertText: 'neural_patterns'
            });
        }

        // Method parameter suggestions
        if (beforeCursor.includes('memory.load(')) {
            suggestions.push({
                text: '"neural_patterns"',
                type: 'variable',
                description: 'Load neural pattern database',
                insertText: '"neural_patterns"'
            });
            suggestions.push({
                text: '"consciousness_state"',
                type: 'variable',
                description: 'Load consciousness state data',
                insertText: '"consciousness_state"'
            });
        }

        if (beforeCursor.includes('plugins.activate(')) {
            suggestions.push({
                text: '"pattern_learner"',
                type: 'variable',
                description: 'Activate pattern learning plugin',
                insertText: '"pattern_learner"'
            });
            suggestions.push({
                text: '"memory_manager"',
                type: 'variable',
                description: 'Activate memory management plugin',
                insertText: '"memory_manager"'
            });
        }

        return suggestions;
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!isVisible) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1));
                break;
            case 'ArrowUp':
                e.preventDefault();
                setSelectedIndex(prev => Math.max(prev - 1, 0));
                break;
            case 'Enter':
            case 'Tab':
                e.preventDefault();
                if (suggestions[selectedIndex]) {
                    onInsert(suggestions[selectedIndex].insertText);
                    onClose();
                }
                break;
            case 'Escape':
                e.preventDefault();
                onClose();
                break;
        }
    };

    const getTypeIcon = (type: AutoCompleteItem['type']) => {
        switch (type) {
            case 'keyword': return '🔤';
            case 'method': return '⚡';
            case 'variable': return '📊';
            case 'snippet': return '📝';
            default: return '•';
        }
    };

    const getTypeColor = (type: AutoCompleteItem['type']) => {
        switch (type) {
            case 'keyword': return 'text-blue-400';
            case 'method': return 'text-green-400';
            case 'variable': return 'text-yellow-400';
            case 'snippet': return 'text-purple-400';
            default: return 'text-gray-400';
        }
    };

    useEffect(() => {
        const handleGlobalKeyDown = (e: KeyboardEvent) => {
            if (isVisible) {
                handleKeyDown(e as any);
            }
        };

        document.addEventListener('keydown', handleGlobalKeyDown);
        return () => document.removeEventListener('keydown', handleGlobalKeyDown);
    }, [isVisible, selectedIndex, suggestions]);

    return (
        <AnimatePresence>
            {isVisible && suggestions.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.15 }}
                    className="absolute z-50 bg-gray-800 border border-gray-600 rounded-lg shadow-xl max-w-md w-80"
                    style={{
                        top: `${cursorPosition.line * 24 + 40}px`,
                        left: `${Math.min(cursorPosition.column * 8, window.innerWidth - 350)}px`
                    }}
                >
                    <div className="p-2">
                        <div className="text-xs text-gray-400 mb-2 px-2">
                            Suggestions ({suggestions.length})
                        </div>
                        <div className="max-h-64 overflow-y-auto space-y-1">
                            {suggestions.map((suggestion, index) => (
                                <motion.div
                                    key={`${suggestion.text}-${index}`}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.02 }}
                                    className={`px-3 py-2 rounded cursor-pointer transition-colors ${index === selectedIndex
                                            ? 'bg-blue-600 text-white'
                                            : 'hover:bg-gray-700 text-gray-300'
                                        }`}
                                    onClick={() => {
                                        onInsert(suggestion.insertText);
                                        onClose();
                                    }}
                                >
                                    <div className="flex items-center space-x-2">
                                        <span className="text-sm">{getTypeIcon(suggestion.type)}</span>
                                        <div className="flex-1 min-w-0">
                                            <div className={`font-mono text-sm ${index === selectedIndex ? 'text-white' : getTypeColor(suggestion.type)
                                                }`}>
                                                {suggestion.text}
                                            </div>
                                            <div className={`text-xs ${index === selectedIndex ? 'text-blue-100' : 'text-gray-500'
                                                } truncate`}>
                                                {suggestion.description}
                                            </div>
                                        </div>
                                        <div className={`text-xs px-2 py-1 rounded ${index === selectedIndex
                                                ? 'bg-blue-500 text-white'
                                                : 'bg-gray-600 text-gray-300'
                                            }`}>
                                            {suggestion.type}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    <div className="border-t border-gray-600 px-3 py-2 bg-gray-750">
                        <div className="text-xs text-gray-400 flex items-center justify-between">
                            <span>↑↓ Navigate • Enter/Tab Insert • Esc Close</span>
                            <span className="text-blue-400">Ctrl+Space</span>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
