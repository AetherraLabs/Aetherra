import { useEffect, useRef } from "react";

interface CodeEditorProps {
    code: string;
    onChange: (code: string) => void;
    language?: string;
}

export default function CodeEditor({ code, onChange, language = "javascript" }: CodeEditorProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!textareaRef.current) return;
        textareaRef.current.value = code;
    }, [code]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        // Add tab support for better code editing
        if (e.key === 'Tab') {
            e.preventDefault();
            const target = e.currentTarget as HTMLTextAreaElement;
            const start = target.selectionStart;
            const end = target.selectionEnd;
            const value = target.value;

            target.value = value.substring(0, start) + '  ' + value.substring(end);
            target.selectionStart = target.selectionEnd = start + 2;
            onChange(target.value);
        }
    };

    return (
        <div className="border border-gray-700 rounded-lg overflow-hidden">
            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    </div>
                    <span className="text-sm text-gray-400 ml-2">
                        script.{language === 'aether' ? 'aether' : 'js'}
                    </span>
                </div>
                <div className="text-xs text-gray-500">
                    {language === 'aether' ? 'AetherScript' : 'JavaScript'}
                </div>
            </div>

            <div className="relative">
                <textarea
                    ref={textareaRef}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="w-full h-80 p-4 font-mono text-sm bg-black text-green-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder={language === 'aether' ? '// Write your .aether script here...' : '// Write your code here...'}
                    spellCheck={false}
                />

                {/* Line numbers overlay */}
                <div className="absolute top-4 left-2 text-xs text-gray-600 pointer-events-none font-mono leading-5">
                    {Array.from({ length: 20 }, (_, i) => (
                        <div key={i + 1}>{i + 1}</div>
                    ))}
                </div>
            </div>
        </div>
    );
}
