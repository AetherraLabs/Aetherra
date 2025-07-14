import React, { useState, useRef, useEffect } from 'react'

interface AetherScriptEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
}

export default function AetherScriptEditor({ value, onChange, onExecute }: AetherScriptEditorProps) {
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      onExecute();
    }
    
    // Tab support
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget as HTMLTextAreaElement;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      const newValue = value.substring(0, start) + '  ' + value.substring(end);
      onChange(newValue);
      
      // Reset cursor position
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    }
  };

  const updateCursorPosition = () => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      const text = textarea.value.substring(0, textarea.selectionStart);
      const lines = text.split('\n');
      setCursorPosition({
        line: lines.length,
        column: lines[lines.length - 1].length + 1
      });
    }
  };

  const getLineNumbers = () => {
    const lines = value.split('\n');
    return lines.map((_, index) => index + 1);
  };

  const highlightSyntax = (code: string) => {
    const keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'import', 'export', 'plugin', 'memory', 'neural', 'async', 'await'];
    const operators = ['=', '+', '-', '*', '/', '==', '!=', '<=', '>=', '<', '>', '&&', '||'];
    const aetherKeywords = ['lyrixa', 'neuralnet', 'memory_store', 'plugin_manager', 'reflex_engine', 'thought_chain'];
    
    let highlighted = code;
    
    // Highlight Aetherra-specific keywords
    aetherKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      highlighted = highlighted.replace(regex, `<span class="text-aetherra-green font-semibold">${keyword}</span>`);
    });
    
    // Highlight standard keywords
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      highlighted = highlighted.replace(regex, `<span class="text-blue-400 font-semibold">${keyword}</span>`);
    });
    
    // Highlight strings
    highlighted = highlighted.replace(/"([^"]*)"/g, '<span class="text-yellow-400">"$1"</span>');
    highlighted = highlighted.replace(/'([^']*)'/g, '<span class="text-yellow-400">\'$1\'</span>');
    
    // Highlight comments
    highlighted = highlighted.replace(/\/\/(.*)$/gm, '<span class="text-gray-500 italic">//$1</span>');
    highlighted = highlighted.replace(/\/\*([\s\S]*?)\*\//g, '<span class="text-gray-500 italic">/*$1*/</span>');
    
    return highlighted;
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 rounded-xl border border-gray-700">
      {/* Editor Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700 bg-gray-800 rounded-t-xl">
        <div className="flex items-center space-x-3">
          <span className="text-aetherra-green font-semibold">📝 AetherScript Editor</span>
          <span className="text-xs text-gray-400">Advanced .aether IDE</span>
        </div>
        <div className="flex items-center space-x-3 text-xs text-gray-400">
          <span>Line {cursorPosition.line}, Col {cursorPosition.column}</span>
          <button
            onClick={onExecute}
            className="px-3 py-1 bg-aetherra-green text-black rounded font-semibold hover:bg-green-400 transition-colors"
            title="Ctrl+Enter to execute"
          >
            ▶ Execute
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 flex">
        {/* Line Numbers */}
        <div className="bg-gray-800 p-3 text-right text-xs text-gray-500 font-mono border-r border-gray-700 min-w-[50px]">
          {getLineNumbers().map(num => (
            <div key={num} className="leading-6">
              {num}
            </div>
          ))}
        </div>

        {/* Code Editor */}
        <div className="flex-1 relative">
          {/* Syntax Highlighting Overlay */}
          <div 
            className="absolute inset-0 p-3 font-mono text-sm leading-6 pointer-events-none whitespace-pre-wrap text-transparent"
            style={{ zIndex: 1 }}
            dangerouslySetInnerHTML={{ __html: highlightSyntax(value) }}
          />
          
          {/* Actual Textarea */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onSelect={updateCursorPosition}
            onClick={updateCursorPosition}
            className="w-full h-full p-3 bg-transparent text-transparent caret-white font-mono text-sm leading-6 resize-none outline-none"
            style={{ zIndex: 2 }}
            placeholder="// Write your .aether script here..."
            spellCheck={false}
          />
        </div>
      </div>

      {/* Status Bar */}
      <div className="p-2 bg-gray-800 border-t border-gray-700 rounded-b-xl">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <span>📄 {value.split('\n').length} lines</span>
            <span>📝 {value.length} chars</span>
            <span>🧠 AetherScript v2.1</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-aetherra-green rounded-full"></span>
            <span>Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
}
