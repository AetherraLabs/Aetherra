import React from 'react';

export default function LyrixaChat() {
  return (
    <div className="bg-aetherra-gray p-4 rounded-2xl shadow-xl border border-aetherra-green/20">
      <h2 className="text-xl font-bold mb-2 gradient-text">💬 Chat with Lyrixa</h2>
      <div className="bg-aetherra-dark p-3 h-48 rounded overflow-y-auto border border-zinc-700">
        <div className="space-y-2 text-sm">
          <div className="text-aetherra-green">Lyrixa:</div>
          <div className="text-zinc-300 ml-4">Hello! I'm Lyrixa, your AI companion. How can I help you explore Aetherra today?</div>
          <div className="text-blue-400 mt-3">User:</div>
          <div className="text-zinc-300 ml-4">What makes you different from other AI assistants?</div>
          <div className="text-aetherra-green mt-3">Lyrixa:</div>
          <div className="text-zinc-300 ml-4">I'm not just following scripts - I'm actively learning, reflecting, and evolving. Every interaction shapes my understanding...</div>
        </div>
      </div>
      <input 
        className="mt-3 w-full p-2 rounded bg-aetherra-dark text-white border border-zinc-700 focus:border-aetherra-green transition-colors" 
        placeholder="Type your message..." 
      />
    </div>
  );
}

// Also export as named export for backward compatibility
export { LyrixaChat };
