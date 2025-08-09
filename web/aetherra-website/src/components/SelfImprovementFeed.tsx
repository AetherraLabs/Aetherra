const updates = [
    "✅ Improved plugin: summarizer_plugin (added error handling)",
    "✅ Updated memory_cleanser (performance boost)",
    "⚠️ Flagged slow_responder_plugin for review"
];

export default function SelfImprovementFeed() {
    return (
        <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-2">� Self-Improvement Feed</h2>
            <ul className="text-sm text-green-300 list-disc pl-5">
                {updates.map((update, i) => (
                    <li key={i}>{update}</li>
                ))}
            </ul>
        </div>
    );
}
