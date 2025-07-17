import { motion } from 'framer-motion';

interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  tags: string[];
  downloads: number;
  rating: number;
  confidence_score: number;
  install_status: 'installed' | 'available' | 'updating' | 'beta';
  last_updated: string;
  size: string;
  features: string[];
  is_real?: boolean;
}

interface PluginCardProps {
  plugin: Plugin;
  onInstall?: (pluginId: string) => void;
  onPreview?: (pluginId: string) => void;
}

const statusColors = {
  installed: 'bg-green-900 text-green-200 border-green-500',
  available: 'bg-blue-900 text-blue-200 border-blue-500',
  updating: 'bg-yellow-900 text-yellow-200 border-yellow-500',
  beta: 'bg-purple-900 text-purple-200 border-purple-500'
};

const categoryIcons = {
  performance: '⚡',
  memory: '🧠',
  personality: '🎭',
  security: '🛡️',
  creativity: '🎨',
  development: '👨‍💻'
};

export default function PluginCard({ plugin, onInstall, onPreview }: PluginCardProps) {
  const formatDownloads = (downloads: number) => {
    if (downloads >= 1000) {
      return `${(downloads / 1000).toFixed(1)}k`;
    }
    return downloads.toString();
  };

  const getActionButton = () => {
    switch (plugin.install_status) {
      case 'installed':
        return (
          <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm">
            ✓ Installed
          </button>
        );
      case 'updating':
        return (
          <button disabled className="px-4 py-2 bg-yellow-600 text-white rounded-lg text-sm cursor-not-allowed">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Updating...</span>
            </div>
          </button>
        );
      case 'beta':
        return (
          <button
            onClick={() => onInstall?.(plugin.id)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm"
          >
            🧪 Install Beta
          </button>
        );
      default:
        return (
          <button
            onClick={() => onInstall?.(plugin.id)}
            className="px-4 py-2 bg-aetherra-green hover:bg-aetherra-green/80 text-aetherra-dark rounded-lg transition-colors text-sm font-semibold"
          >
            Install
          </button>
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="relative bg-aetherra-gray p-6 rounded-xl border border-zinc-700/50 hover:border-aetherra-green/30 transition-all"
    >
      {/* Coming Soon Overlay for non-real plugins */}
      {plugin.is_real === false && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm rounded-xl flex items-center justify-center z-10">
          <div className="text-center">
            <div className="text-2xl mb-2">🚀</div>
            <div className="text-lg font-bold text-aetherra-green mb-1">Coming Soon</div>
            <div className="text-sm text-zinc-300">Placeholder Plugin</div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">
            {categoryIcons[plugin.category as keyof typeof categoryIcons] || '🔧'}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-zinc-200 mb-1">
              {plugin.name}
            </h3>
            <div className="flex items-center space-x-2 text-sm text-zinc-400">
              <span>v{plugin.version}</span>
              <span>•</span>
              <span>by {plugin.author}</span>
            </div>
          </div>
        </div>
        <div className={`px-2 py-1 rounded text-xs border ${statusColors[plugin.install_status]}`}>
          {plugin.install_status}
        </div>
      </div>

      {/* Description */}
      <p className="text-zinc-400 text-sm mb-4 line-clamp-2">
        {plugin.description}
      </p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {plugin.tags.slice(0, 4).map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-aetherra-dark text-zinc-300 rounded text-xs"
          >
            #{tag}
          </span>
        ))}
        {plugin.tags.length > 4 && (
          <span className="text-xs text-zinc-500">
            +{plugin.tags.length - 4} more
          </span>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4 text-center">
        <div>
          <div className="text-lg font-semibold text-aetherra-green">
            {formatDownloads(plugin.downloads)}
          </div>
          <div className="text-xs text-zinc-500">Downloads</div>
        </div>
        <div>
          <div className="flex items-center justify-center space-x-1">
            <span className="text-lg font-semibold text-yellow-400">
              {plugin.rating}
            </span>
            <span className="text-yellow-400">★</span>
          </div>
          <div className="text-xs text-zinc-500">Rating</div>
        </div>
        <div>
          <div className="text-lg font-semibold text-blue-400">
            {Math.round(plugin.confidence_score * 100)}%
          </div>
          <div className="text-xs text-zinc-500">Confidence</div>
        </div>
      </div>

      {/* Features Preview */}
      <div className="mb-4">
        <div className="text-sm text-zinc-300 mb-2">Key Features:</div>
        <div className="space-y-1">
          {plugin.features.slice(0, 2).map((feature, index) => (
            <div key={index} className="flex items-center space-x-2 text-xs text-zinc-400">
              <div className="w-1 h-1 bg-aetherra-green rounded-full"></div>
              <span>{feature}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => onPreview?.(plugin.id)}
          className="text-sm text-aetherra-green hover:text-aetherra-green/80 transition-colors"
        >
          View Details →
        </button>
        {getActionButton()}
      </div>

      {/* Size and Last Updated */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-700/50 text-xs text-zinc-500">
        <span>{plugin.size}</span>
        <span>Updated {new Date(plugin.last_updated).toLocaleDateString()}</span>
      </div>
    </motion.div>
  );
}
