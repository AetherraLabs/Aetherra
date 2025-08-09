import { motion } from 'framer-motion';
import { useState } from 'react';

interface EditorProps {
    value: string;
    onChange: (value: string) => void;
    language?: string;
}

export function AetherScriptEditor({ value, onChange, language = 'aether' }: EditorProps) {
    const [lineNumbers, setLineNumbers] = useState(true);
    const [isDarkMode, setIsDarkMode] = useState(true);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        onChange(e.target.value);
    };

    const lines = value.split('\n').length;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="border border-gray-700 rounded-lg overflow-hidden bg-gray-900"
        >
            {/* Editor Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-300">AetherScript Editor</span>
                    <span className="text-xs text-gray-500">({language})</span>
                </div>
                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setLineNumbers(!lineNumbers)}
                        className={`text-xs px-2 py-1 rounded ${lineNumbers ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
                            }`}
                    >
                        Line #
                    </button>
                    <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className="text-xs px-2 py-1 rounded bg-gray-600 text-gray-300 hover:bg-gray-500"
                    >
                        {isDarkMode ? '☀️' : '🌙'}
                    </button>
                </div>
            </div>

            {/* Editor Body */}
            <div className="relative">
                {lineNumbers && (
                    <div className="absolute left-0 top-0 w-12 bg-gray-800 text-gray-500 text-sm leading-6 text-right pr-2 pt-2 select-none">
                        {Array.from({ length: lines }, (_, i) => (
                            <div key={i + 1} className="h-6">
                                {i + 1}
                            </div>
                        ))}
                    </div>
                )}

                <textarea
                    value={value}
                    onChange={handleInputChange}
                    className={`w-full h-64 bg-transparent text-green-300 font-mono text-sm leading-6 resize-none focus:outline-none p-2 ${lineNumbers ? 'pl-14' : 'pl-4'
                        }`}
                    placeholder="// Write your AetherScript code here...
consciousness.initialize()
memory.load('neural_patterns')
thinking.process(input_stream)

// Define neural pathway
pathway consciousness_flow {
  input: sensory_data
  process: pattern_recognition
  output: conscious_thought
}

// Execute consciousness loop
loop {
  sense()
  think()
  learn()
  evolve()
}"
                    spellCheck={false}
                    style={{
                        tabSize: 2,
                        fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
                    }}
                />
            </div>

            {/* Editor Footer */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
                <div className="flex space-x-4">
                    <span>Lines: {lines}</span>
                    <span>Characters: {value.length}</span>
                    <span>Language: {language}</span>
                </div>
                <div className="flex space-x-2">
                    <span className="text-green-400">● Syntax OK</span>
                    <span>Encoding: UTF-8</span>
                </div>
            </div>
        </motion.div>
    );
}
