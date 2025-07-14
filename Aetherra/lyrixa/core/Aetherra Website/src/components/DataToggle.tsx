import React, { useState } from 'react'

interface DataToggleProps {
  onModeChange: (isLive: boolean) => void;
}

export default function DataToggle({ onModeChange }: DataToggleProps) {
  const [isLive, setIsLive] = useState(false);

  const handleToggle = () => {
    const newMode = !isLive;
    setIsLive(newMode);
    onModeChange(newMode);
  };

  return (
    <div className="flex items-center space-x-3 p-4 bg-gray-900 rounded-xl border border-gray-700">
      <span className="text-sm font-medium text-gray-300">Data Source:</span>
      
      <button
        onClick={handleToggle}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-aetherra-green focus:ring-offset-2 focus:ring-offset-gray-800 ${
          isLive ? 'bg-aetherra-green' : 'bg-gray-600'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            isLive ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      
      <div className="flex space-x-2 text-sm">
        <span className={`${!isLive ? 'text-aetherra-green font-bold' : 'text-gray-400'}`}>
          🎭 Simulated
        </span>
        <span className="text-gray-500">|</span>
        <span className={`${isLive ? 'text-aetherra-green font-bold' : 'text-gray-400'}`}>
          ⚡ Live Backend
        </span>
      </div>
      
      <div className="ml-4 text-xs text-gray-500">
        {isLive ? (
          <span className="flex items-center">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
            Connected to real Lyrixa instance
          </span>
        ) : (
          <span className="flex items-center">
            <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
            Using demo data for showcase
          </span>
        )}
      </div>
    </div>
  );
}
