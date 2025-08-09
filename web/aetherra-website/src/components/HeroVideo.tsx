export function HeroVideo() {
    return (
        <div className="w-full h-[40vh] bg-gradient-to-b from-black via-gray-900 to-black flex items-center justify-center overflow-hidden relative">
            {/* Animated background pattern */}
            <div className="absolute inset-0 opacity-20">
                <div className="w-full h-full bg-gradient-to-r from-green-500/10 via-blue-500/10 to-purple-500/10 animate-pulse"></div>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_40%,rgba(120,119,198,0.1),transparent_50%)]"></div>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(255,119,198,0.1),transparent_50%)]"></div>
            </div>

            {/* Centered content */}
            <div className="relative z-10 text-center">
                <h2 className="text-3xl font-bold mb-4 text-gray-300">
                    An operating system that thinks. A companion that learns.
                </h2>
                <p className="text-xl text-gray-400">
                    The future of neural computing is here.
                </p>
                <div className="mt-6 flex gap-4 justify-center">
                    <button className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
                        Get Started
                    </button>
                    <button className="border border-gray-500 hover:border-gray-400 text-gray-300 hover:text-white px-6 py-3 rounded-lg font-semibold transition-colors">
                        Learn More
                    </button>
                </div>
            </div>
        </div>
    );
}
