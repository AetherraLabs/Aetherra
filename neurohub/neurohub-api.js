// NeuroHub API for plugin management
class NeuroHubAPI {
    constructor() {
        this.baseUrl = 'https://api.neurohub.dev';
        this.version = 'v1';
        this.apiKey = null;
    }

    // Authentication
    async authenticate(apiKey) {
        this.apiKey = apiKey;
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/auth/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                }
            });
            return response.ok;
        } catch (error) {
            console.error('Authentication failed:', error);
            return false;
        }
    }

    // Plugin Discovery
    async searchPlugins(query, filters = {}) {
        const params = new URLSearchParams({
            q: query,
            ...filters
        });

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/search?${params}`);
            return await response.json();
        } catch (error) {
            console.error('Search failed:', error);
            return { plugins: [], total: 0 };
        }
    }

    async getPlugin(name) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}`);
            return await response.json();
        } catch (error) {
            console.error('Plugin fetch failed:', error);
            return null;
        }
    }

    async getFeaturedPlugins() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/featured`);
            return await response.json();
        } catch (error) {
            console.error('Featured plugins fetch failed:', error);
            return [];
        }
    }

    async getPopularPlugins(limit = 20) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/popular?limit=${limit}`);
            return await response.json();
        } catch (error) {
            console.error('Popular plugins fetch failed:', error);
            return [];
        }
    }

    // Plugin Publishing
    async publishPlugin(pluginData, packageFile) {
        if (!this.apiKey) {
            throw new Error('Authentication required for publishing');
        }

        const formData = new FormData();
        formData.append('metadata', JSON.stringify(pluginData));
        formData.append('package', packageFile);

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/publish`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Plugin publish failed:', error);
            throw error;
        }
    }

    async updatePlugin(name, version, packageFile) {
        if (!this.apiKey) {
            throw new Error('Authentication required for updates');
        }

        const formData = new FormData();
        formData.append('version', version);
        formData.append('package', packageFile);

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/update`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('Plugin update failed:', error);
            throw error;
        }
    }

    // Plugin Installation
    async downloadPlugin(name, version = 'latest') {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/download?version=${version}`);

            if (!response.ok) {
                throw new Error(`Download failed: ${response.statusText}`);
            }

            return {
                blob: await response.blob(),
                filename: response.headers.get('Content-Disposition')?.split('filename=')[1] || `${name}.neuroplug`
            };
        } catch (error) {
            console.error('Plugin download failed:', error);
            throw error;
        }
    }

    async getInstallationStats(name) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/stats`);
            return await response.json();
        } catch (error) {
            console.error('Stats fetch failed:', error);
            return { downloads: 0, rating: 0, reviews: 0 };
        }
    }

    // User Management
    async getUserPlugins() {
        if (!this.apiKey) {
            throw new Error('Authentication required');
        }

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/user/plugins`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            return await response.json();
        } catch (error) {
            console.error('User plugins fetch failed:', error);
            return [];
        }
    }

    async getInstalledPlugins() {
        if (!this.apiKey) {
            throw new Error('Authentication required');
        }

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/user/installed`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Installed plugins fetch failed:', error);
            return [];
        }
    }

    // Reviews and Ratings
    async ratePlugin(name, rating, review = '') {
        if (!this.apiKey) {
            throw new Error('Authentication required for rating');
        }

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/rate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({ rating, review })
            });
            return await response.json();
        } catch (error) {
            console.error('Rating failed:', error);
            throw error;
        }
    }

    async getPluginReviews(name, page = 1, limit = 10) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/reviews?page=${page}&limit=${limit}`);
            return await response.json();
        } catch (error) {
            console.error('Reviews fetch failed:', error);
            return { reviews: [], total: 0 };
        }
    }

    // Categories and Tags
    async getCategories() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/categories`);
            return await response.json();
        } catch (error) {
            console.error('Categories fetch failed:', error);
            return [];
        }
    }

    async getPluginsByCategory(category, page = 1, limit = 20) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/categories/${category}/plugins?page=${page}&limit=${limit}`);
            return await response.json();
        } catch (error) {
            console.error('Category plugins fetch failed:', error);
            return { plugins: [], total: 0 };
        }
    }

    // Analytics
    async getMarketplaceStats() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/stats/marketplace`);
            return await response.json();
        } catch (error) {
            console.error('Marketplace stats fetch failed:', error);
            return {
                totalPlugins: 0,
                totalDownloads: 0,
                activeDevelopers: 0,
                averageRating: 0
            };
        }
    }

    async getPluginAnalytics(name) {
        if (!this.apiKey) {
            throw new Error('Authentication required for analytics');
        }

        try {
            const response = await fetch(`${this.baseUrl}/${this.version}/plugins/${name}/analytics`, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Plugin analytics fetch failed:', error);
            return null;
        }
    }
}

// Plugin Manager for local installation
class PluginManager {
    constructor() {
        this.installedPlugins = new Map();
        this.pluginDirectory = './plugins/';
        this.api = new NeuroHubAPI();
    }

    async install(name, version = 'latest') {
        try {
            console.log(`Installing ${name}@${version}...`);

            // Download plugin
            const download = await this.api.downloadPlugin(name, version);

            // Extract and validate
            const plugin = await this.extractPlugin(download);

            // Install dependencies
            await this.installDependencies(plugin.manifest.dependencies || []);

            // Register plugin
            this.installedPlugins.set(name, {
                ...plugin,
                installedAt: new Date().toISOString(),
                version: plugin.manifest.version
            });

            console.log(`✅ Successfully installed ${name}@${plugin.manifest.version}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to install ${name}:`, error.message);
            return false;
        }
    }

    async uninstall(name) {
        try {
            if (!this.installedPlugins.has(name)) {
                throw new Error(`Plugin ${name} is not installed`);
            }

            // Remove plugin files
            await this.removePluginFiles(name);

            // Unregister plugin
            this.installedPlugins.delete(name);

            console.log(`✅ Successfully uninstalled ${name}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to uninstall ${name}:`, error.message);
            return false;
        }
    }

    async update(name) {
        try {
            const installed = this.installedPlugins.get(name);
            if (!installed) {
                throw new Error(`Plugin ${name} is not installed`);
            }

            const latest = await this.api.getPlugin(name);
            if (latest.version === installed.version) {
                console.log(`${name} is already up to date (${installed.version})`);
                return true;
            }

            console.log(`Updating ${name} from ${installed.version} to ${latest.version}...`);

            // Backup current version
            await this.backupPlugin(name);

            // Install new version
            await this.install(name, latest.version);

            console.log(`✅ Successfully updated ${name} to ${latest.version}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to update ${name}:`, error.message);
            await this.restorePlugin(name); // Rollback on failure
            return false;
        }
    }

    list() {
        console.log('\n📦 Installed Plugins:\n');
        if (this.installedPlugins.size === 0) {
            console.log('No plugins installed.');
            return;
        }

        for (const [name, plugin] of this.installedPlugins) {
            console.log(`${name}@${plugin.version}`);
            console.log(`  📄 ${plugin.manifest.description}`);
            console.log(`  📅 Installed: ${new Date(plugin.installedAt).toLocaleDateString()}`);
            console.log('');
        }
    }

    async search(query) {
        try {
            const results = await this.api.searchPlugins(query);
            console.log(`\n🔍 Search results for "${query}":\n`);

            for (const plugin of results.plugins) {
                console.log(`${plugin.name}@${plugin.version}`);
                console.log(`  📄 ${plugin.description}`);
                console.log(`  📦 ${plugin.downloads} downloads`);
                console.log(`  ⭐ ${plugin.rating}/5.0 rating`);
                console.log(`  💻 neurocode install ${plugin.name}`);
                console.log('');
            }
        } catch (error) {
            console.error('Search failed:', error.message);
        }
    }

    // Helper methods
    async extractPlugin(download) {
        // Implementation for extracting .neuroplug files
        // This would handle ZIP extraction and validation
        return {
            manifest: {}, // Parsed neurocode-plugin.json
            files: {}     // Extracted files
        };
    }

    async installDependencies(dependencies) {
        // Recursively install plugin dependencies
        for (const dep of dependencies) {
            if (!this.installedPlugins.has(dep.name)) {
                await this.install(dep.name, dep.version);
            }
        }
    }

    async removePluginFiles(name) {
        // Remove plugin directory and files
    }

    async backupPlugin(name) {
        // Create backup of current plugin version
    }

    async restorePlugin(name) {
        // Restore plugin from backup
    }
}

// Export for Node.js or browser usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NeuroHubAPI, PluginManager };
} else {
    window.NeuroHubAPI = NeuroHubAPI;
    window.PluginManager = PluginManager;
}
