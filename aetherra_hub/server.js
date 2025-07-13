const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Storage for uploaded plugins
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, './uploads/');
    },
    filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${crypto.randomBytes(6).toString('hex')}-${file.originalname}`;
        cb(null, uniqueName);
    }
});

const upload = multer({ storage });

// In-memory data store (in production, use a proper database)
let plugins = [
    {
        id: 'transcriber',
        name: 'transcriber',
        version: '2.1.0',
        description: 'Advanced AI speech-to-text with consciousness-aware context understanding and emotional tone detection.',
        tags: ['audio', 'transcription', 'nlp', 'consciousness'],
        downloads: 45200,
        rating: 4.8,
        author: 'aether_audio_team',
        createdAt: '2025-01-15T10:30:00Z',
        updatedAt: '2025-06-20T14:22:00Z',
        size: '2.3MB',
        license: 'MIT',
        repository: 'https://github.com/aether_audio_team/transcriber',
        dependencies: ['aetherra-core>=2.0.0'],
        featured: true
    },
    {
        id: 'optimizer',
        name: 'optimizer',
        version: '1.5.3',
        description: 'Intelligent performance optimizer that learns from your AI\'s behavioral patterns and automatically tunes execution.',
        tags: ['performance', 'optimization', 'learning', 'adaptive'],
        downloads: 32800,
        rating: 4.9,
        author: 'quantum_dev',
        createdAt: '2025-02-01T09:15:00Z',
        updatedAt: '2025-06-25T11:45:00Z',
        size: '1.8MB',
        license: 'Apache-2.0',
        repository: 'https://github.com/quantum_dev/optimizer',
        dependencies: ['aetherra-core>=1.8.0'],
        featured: true
    },
    {
        id: 'reflector',
        name: 'reflector',
        version: '3.0.1',
        description: 'Deep self-reflection module enabling AI systems to analyze their own thought processes and improve decision-making.',
        tags: ['reflection', 'consciousness', 'meta-cognition', 'analysis'],
        downloads: 28500,
        rating: 4.7,
        author: 'consciousness_lab',
        createdAt: '2025-01-20T16:00:00Z',
        updatedAt: '2025-06-18T13:30:00Z',
        size: '3.1MB',
        license: 'GPL-3.0',
        repository: 'https://github.com/consciousness_lab/reflector',
        dependencies: ['aetherra-core>=2.1.0', 'aether-analytics>=1.0.0'],
        featured: true
    },
    {
        id: 'memory-palace',
        name: 'memory-palace',
        version: '1.8.2',
        description: 'Advanced spatial memory organization system inspired by the method of loci for enhanced long-term recall.',
        tags: ['memory', 'spatial', 'organization', 'recall'],
        downloads: 21300,
        rating: 4.6,
        author: 'memory_architects',
        createdAt: '2025-03-10T12:20:00Z',
        updatedAt: '2025-06-22T09:15:00Z',
        size: '2.7MB',
        license: 'MIT',
        repository: 'https://github.com/memory_architects/memory-palace',
        dependencies: ['aetherra-core>=2.0.0'],
        featured: false
    },
    {
        id: 'emotion-engine',
        name: 'emotion-engine',
        version: '2.3.0',
        description: 'Sophisticated emotional intelligence module with real-time sentiment analysis and empathetic response generation.',
        tags: ['emotion', 'empathy', 'sentiment', 'psychology'],
        downloads: 38700,
        rating: 4.8,
        author: 'emotional_ai',
        createdAt: '2025-01-30T14:45:00Z',
        updatedAt: '2025-06-28T16:10:00Z',
        size: '4.2MB',
        license: 'MIT',
        repository: 'https://github.com/emotional_ai/emotion-engine',
        dependencies: ['aetherra-core>=2.0.0', 'sentiment-analyzer>=1.5.0'],
        featured: true
    },
    {
        id: 'vision-processor',
        name: 'vision-processor',
        version: '1.9.1',
        description: 'Multi-modal visual analysis with consciousness-level understanding of context, objects, and spatial relationships.',
        tags: ['vision', 'analysis', 'multimodal', 'spatial'],
        downloads: 42100,
        rating: 4.9,
        author: 'vision_systems',
        createdAt: '2025-02-15T11:30:00Z',
        updatedAt: '2025-06-26T15:20:00Z',
        size: '5.8MB',
        license: 'Apache-2.0',
        repository: 'https://github.com/vision_systems/vision-processor',
        dependencies: ['aetherra-core>=2.1.0', 'cv-toolkit>=2.0.0'],
        featured: true
    },
    {
        id: 'goal-tracker',
        name: 'goal-tracker',
        version: '2.0.4',
        description: 'Intelligent goal management system with automated progress tracking and adaptive milestone adjustment.',
        tags: ['goals', 'tracking', 'planning', 'adaptive'],
        downloads: 19800,
        rating: 4.5,
        author: 'planning_ai',
        createdAt: '2025-03-05T10:00:00Z',
        updatedAt: '2025-06-24T12:40:00Z',
        size: '1.9MB',
        license: 'MIT',
        repository: 'https://github.com/planning_ai/goal-tracker',
        dependencies: ['aetherra-core>=1.9.0'],
        featured: false
    },
    {
        id: 'learning-accelerator',
        name: 'learning-accelerator',
        version: '1.6.7',
        description: 'Meta-learning enhancement that improves the AI\'s ability to learn new tasks faster through experience transfer.',
        tags: ['learning', 'meta-learning', 'transfer', 'acceleration'],
        downloads: 25400,
        rating: 4.7,
        author: 'learning_lab',
        createdAt: '2025-02-28T13:15:00Z',
        updatedAt: '2025-06-21T14:55:00Z',
        size: '3.4MB',
        license: 'BSD-3-Clause',
        repository: 'https://github.com/learning_lab/learning-accelerator',
        dependencies: ['aetherra-core>=2.0.0', 'ml-toolkit>=1.2.0'],
        featured: false
    }
];

let users = [];
let apiKeys = new Map();

// Helper functions
function generateApiKey() {
    return crypto.randomBytes(32).toString('hex');
}

function formatDownloads(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// Routes

// Authentication endpoints
app.post('/api/v1/auth/register', async (req, res) => {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    const existingUser = users.find(u => u.username === username || u.email === email);
    if (existingUser) {
        return res.status(409).json({ error: 'User already exists' });
    }

    const apiKey = generateApiKey();
    const user = {
        id: crypto.randomUUID(),
        username,
        email,
        createdAt: new Date().toISOString(),
        apiKey
    };

    users.push(user);
    apiKeys.set(apiKey, user);

    res.json({
        message: 'Registration successful',
        apiKey,
        user: { id: user.id, username: user.username, email: user.email }
    });
});

app.post('/api/v1/auth/verify', (req, res) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Invalid authorization header' });
    }

    const apiKey = authHeader.slice(7);
    const user = apiKeys.get(apiKey);

    if (!user) {
        return res.status(401).json({ error: 'Invalid API key' });
    }

    res.json({ valid: true, user: { id: user.id, username: user.username } });
});

// Plugin discovery endpoints
app.get('/api/v1/plugins/search', (req, res) => {
    const { q, category, sort, limit = 20, offset = 0 } = req.query;
    let filteredPlugins = [...plugins];

    // Search by query
    if (q) {
        const query = q.toLowerCase();
        filteredPlugins = filteredPlugins.filter(plugin =>
            plugin.name.toLowerCase().includes(query) ||
            plugin.description.toLowerCase().includes(query) ||
            plugin.tags.some(tag => tag.toLowerCase().includes(query)) ||
            plugin.author.toLowerCase().includes(query)
        );
    }

    // Filter by category
    if (category && category !== 'all') {
        filteredPlugins = filteredPlugins.filter(plugin =>
            plugin.tags.some(tag => tag.toLowerCase().includes(category.toLowerCase()))
        );
    }

    // Sort results
    switch (sort) {
        case 'downloads':
            filteredPlugins.sort((a, b) => b.downloads - a.downloads);
            break;
        case 'rating':
            filteredPlugins.sort((a, b) => b.rating - a.rating);
            break;
        case 'recent':
            filteredPlugins.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
            break;
        default:
            // Default to relevance (featured first, then downloads)
            filteredPlugins.sort((a, b) => {
                if (a.featured !== b.featured) return b.featured - a.featured;
                return b.downloads - a.downloads;
            });
    }

    // Pagination
    const startIndex = parseInt(offset);
    const endIndex = startIndex + parseInt(limit);
    const paginatedPlugins = filteredPlugins.slice(startIndex, endIndex);

    // Format for response
    const formattedPlugins = paginatedPlugins.map(plugin => ({
        ...plugin,
        downloads: formatDownloads(plugin.downloads)
    }));

    res.json({
        plugins: formattedPlugins,
        total: filteredPlugins.length,
        limit: parseInt(limit),
        offset: parseInt(offset)
    });
});

app.get('/api/v1/plugins/featured', (req, res) => {
    const featuredPlugins = plugins
        .filter(plugin => plugin.featured)
        .sort((a, b) => b.downloads - a.downloads)
        .map(plugin => ({
            ...plugin,
            downloads: formatDownloads(plugin.downloads)
        }));

    res.json(featuredPlugins);
});

app.get('/api/v1/plugins/popular', (req, res) => {
    const { limit = 20 } = req.query;

    const popularPlugins = plugins
        .sort((a, b) => b.downloads - a.downloads)
        .slice(0, parseInt(limit))
        .map(plugin => ({
            ...plugin,
            downloads: formatDownloads(plugin.downloads)
        }));

    res.json(popularPlugins);
});

app.get('/api/v1/plugins/:name', (req, res) => {
    const { name } = req.params;
    const plugin = plugins.find(p => p.name === name);

    if (!plugin) {
        return res.status(404).json({ error: 'Plugin not found' });
    }

    res.json({
        ...plugin,
        downloads: formatDownloads(plugin.downloads)
    });
});

// Plugin publishing endpoints
app.post('/api/v1/plugins/publish', upload.single('package'), (req, res) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Authentication required' });
    }

    const apiKey = authHeader.slice(7);
    const user = apiKeys.get(apiKey);

    if (!user) {
        return res.status(401).json({ error: 'Invalid API key' });
    }

    try {
        const metadata = JSON.parse(req.body.metadata);
        const { name, version, description, tags, license, repository, dependencies } = metadata;

        if (!name || !version || !description) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        // Check if plugin already exists
        const existingPlugin = plugins.find(p => p.name === name);
        if (existingPlugin) {
            return res.status(409).json({ error: 'Plugin already exists. Use update endpoint.' });
        }

        const newPlugin = {
            id: name,
            name,
            version,
            description,
            tags: tags || [],
            downloads: 0,
            rating: 0,
            author: user.username,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            size: req.file ? `${(req.file.size / 1024 / 1024).toFixed(1)}MB` : '0MB',
            license: license || 'MIT',
            repository: repository || '',
            dependencies: dependencies || [],
            featured: false,
            filename: req.file ? req.file.filename : null
        };

        plugins.push(newPlugin);

        res.json({
            message: 'Plugin published successfully',
            plugin: {
                ...newPlugin,
                downloads: formatDownloads(newPlugin.downloads)
            }
        });
    } catch (error) {
        res.status(400).json({ error: 'Invalid metadata format' });
    }
});

app.post('/api/v1/plugins/:name/update', upload.single('package'), (req, res) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Authentication required' });
    }

    const apiKey = authHeader.slice(7);
    const user = apiKeys.get(apiKey);

    if (!user) {
        return res.status(401).json({ error: 'Invalid API key' });
    }

    const { name } = req.params;
    const { version } = req.body;

    const pluginIndex = plugins.findIndex(p => p.name === name);
    if (pluginIndex === -1) {
        return res.status(404).json({ error: 'Plugin not found' });
    }

    const plugin = plugins[pluginIndex];
    if (plugin.author !== user.username) {
        return res.status(403).json({ error: 'Not authorized to update this plugin' });
    }

    // Update plugin
    plugins[pluginIndex] = {
        ...plugin,
        version: version || plugin.version,
        updatedAt: new Date().toISOString(),
        size: req.file ? `${(req.file.size / 1024 / 1024).toFixed(1)}MB` : plugin.size,
        filename: req.file ? req.file.filename : plugin.filename
    };

    res.json({
        message: 'Plugin updated successfully',
        plugin: {
            ...plugins[pluginIndex],
            downloads: formatDownloads(plugins[pluginIndex].downloads)
        }
    });
});

// Plugin installation endpoints
app.get('/api/v1/plugins/:name/download', (req, res) => {
    const { name } = req.params;
    const { version = 'latest' } = req.query;

    const plugin = plugins.find(p => p.name === name);
    if (!plugin) {
        return res.status(404).json({ error: 'Plugin not found' });
    }

    // Increment download count
    plugin.downloads += 1;

    // In a real implementation, serve the actual file
    res.set({
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${name}-${plugin.version}.aetherplug"`
    });

    // For demo purposes, send a placeholder
    res.send(`# ${plugin.name} v${plugin.version}\n# aetherra Plugin Package\n# Download simulated for demo`);
});

app.get('/api/v1/plugins/:name/stats', (req, res) => {
    const { name } = req.params;
    const plugin = plugins.find(p => p.name === name);

    if (!plugin) {
        return res.status(404).json({ error: 'Plugin not found' });
    }

    res.json({
        downloads: plugin.downloads,
        rating: plugin.rating,
        reviews: Math.floor(plugin.downloads * 0.1), // Simulate review count
        weeklyDownloads: Math.floor(plugin.downloads * 0.15),
        monthlyDownloads: Math.floor(plugin.downloads * 0.6)
    });
});

// Analytics endpoints
app.get('/api/v1/analytics/overview', (req, res) => {
    const totalPlugins = plugins.length;
    const totalDownloads = plugins.reduce((sum, plugin) => sum + plugin.downloads, 0);
    const totalAuthors = new Set(plugins.map(p => p.author)).size;
    const averageRating = plugins.reduce((sum, plugin) => sum + plugin.rating, 0) / plugins.length;

    res.json({
        totalPlugins,
        totalDownloads,
        totalAuthors,
        averageRating: Math.round(averageRating * 10) / 10,
        formattedDownloads: formatDownloads(totalDownloads)
    });
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('API Error:', error);
    res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Create uploads directory if it doesn't exist
const initializeServer = async () => {
    try {
        await fs.mkdir('./uploads', { recursive: true });
        console.log('Uploads directory ready');
    } catch (error) {
        console.error('Failed to create uploads directory:', error);
    }
};

// Start server
initializeServer().then(() => {
    app.listen(PORT, () => {
        console.log(`🚀 aetherhub API server running on port ${PORT}`);
        console.log(`📊 Serving ${plugins.length} plugins from ${new Set(plugins.map(p => p.author)).size} authors`);
        console.log(`🌐 API available at http://localhost:${PORT}/api/v1`);
    });
});

module.exports = app;
