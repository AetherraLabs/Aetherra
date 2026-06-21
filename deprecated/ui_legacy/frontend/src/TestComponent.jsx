// Simple test component to verify React is working
import { useState } from "react";

export default function TestComponent() {
    const [count, setCount] = useState(0);

    return (
        <div className="w-screen h-screen bg-gray-900 text-white flex items-center justify-center">
            <div className="text-center">
                <h1 className="text-4xl font-bold mb-4">React Test</h1>
                <p className="text-xl mb-4">Count: {count}</p>
                <button
                    onClick={() => setCount(count + 1)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Click me
                </button>
            </div>
        </div>
    );
}
