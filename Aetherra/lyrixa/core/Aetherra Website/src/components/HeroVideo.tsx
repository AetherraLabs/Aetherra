export function HeroVideo() {
  return (
    <div className="w-full h-[40vh] bg-gradient-to-br from-aetherra-dark via-green-900/20 to-aetherra-dark flex items-center justify-center overflow-hidden relative">
      {/* Neural Network Animation Background */}
      <div className="absolute inset-0 opacity-30">
        <div className="w-full h-full bg-gradient-to-r from-transparent via-aetherra-green/10 to-transparent animate-pulse"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMiIgZmlsbD0iIzAwZmY4OCIgZmlsbC1vcGFjaXR5PSIwLjMiLz4KPC9zdmc+')] animate-pulse"></div>
      </div>
      
      {/* Animated Neural Connections */}
      <div className="absolute inset-0">
        <div className="w-full h-full bg-gradient-to-t from-aetherra-dark/80 to-transparent"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="w-32 h-32 border border-aetherra-green/30 rounded-full animate-ping"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 border border-aetherra-green/50 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      {/* Central Neural Node */}
      <div className="relative z-10 text-center">
        <div className="w-4 h-4 bg-aetherra-green rounded-full mx-auto mb-4 animate-pulse shadow-lg shadow-aetherra-green/50"></div>
        <div className="text-aetherra-green/70 text-sm font-mono">Neural Processing Active</div>
      </div>
    </div>
  );
}
