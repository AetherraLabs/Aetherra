export function LyrixaChat() {
    return (
        <div className="bg-zinc-900 p-4 rounded-2xl shadow-xl">
            <h2 className="text-xl font-bold mb-2">💬 Chat with Lyrixa</h2>
            <div className="bg-zinc-800 p-2 h-48 rounded overflow-y-auto">[Simulated conversation]</div>
            <input className="mt-2 w-full p-2 rounded bg-zinc-800 text-white" placeholder="Type your message..." />
        </div>
    );
}
