import React, { useEffect, useRef } from "react";

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language?: string;
}

export default function CodeEditor({ code, onChange, language = "aether" }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!textareaRef.current) return;
    textareaRef.current.value = code;
  }, [code]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Add tab support for better coding experience
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      const newValue = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end);
      textarea.value = newValue;
      onChange(newValue);

      // Move cursor to after the inserted spaces
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      }, 0);
    }
  };

  return (
    <div className="relative">
      {/* Header with language indicator */}
      <div className="flex items-center justify-between bg-aetherra-gray px-4 py-2 rounded-t-lg border-b border-zinc-700">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-zinc-400">Language:</span>
          <span className="text-xs text-aetherra-green font-mono">.{language}</span>
        </div>
      </div>

      {/* Code Editor */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full h-80 p-4 font-mono text-sm bg-aetherra-dark text-aetherra-green rounded-b-lg border border-zinc-700 focus:border-aetherra-green focus:outline-none resize-none overflow-auto"
          placeholder="// Write your .aether script here
// Example:
plugin 'neural-optimizer' {
  initialize() {
    console.log('Neural Optimizer activated');
  }
}"
          spellCheck={false}
        />
        
        {/* Line numbers overlay could be added here for enhanced experience */}
        <div className="absolute bottom-2 right-2 text-xs text-zinc-500 bg-aetherra-gray px-2 py-1 rounded">
          {code.split('\n').length} lines
        </div>
      </div>
    </div>
  );
}
