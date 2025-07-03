// NeuroHub Frontend API Client
class NeuroHubClient {
    constructor(baseUrl = 'http://localhost:3001/api/v1') {
        this.baseUrl = baseUrl;
        this.apiKey = localStorage.getItem('neurohub_api_key');
    }

    // Authentication
    async register(username, email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Registration failed');
            }

            const data = await response.json();
            this.apiKey = data.apiKey;
            localStorage.setItem('neurohub_api_key', this.apiKey);
            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async authenticate(apiKey) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                }
            });

            if (response.ok) {
                this.apiKey = apiKey;
                localStorage.setItem('neurohub_api_key', apiKey);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Authentication error:', error);
            return false;
        }
    }

    logout() {
        this.apiKey = null;
        localStorage.removeItem('neurohub_api_key');
    }

    isAuthenticated() {
        return !!this.apiKey;
    }

    // Plugin Discovery
    async searchPlugins(query = '', filters = {}) {
        try {
            const params = new URLSearchParams({
                q: query,
                ...filters
            });

            const response = await fetch(`${this.baseUrl}/plugins/search?${params}`);

            if (!response.ok) {
                throw new Error('Search failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            return { plugins: [], total: 0 };
        }
    }

    async getFeaturedPlugins() {
        try {
            const response = await fetch(`${this.baseUrl}/plugins/featured`);

            if (!response.ok) {
                throw new Error('Failed to fetch featured plugins');
            }

            return await response.json();
        } catch (error) {
            console.error('Featured plugins error:', error);
            return [];
        }
    }

    async getPopularPlugins(limit = 20) {
        try {
            const response = await fetch(`${this.baseUrl}/plugins/popular?limit=${limit}`);

            if (!response.ok) {
                throw new Error('Failed to fetch popular plugins');
            }

            return await response.json();
        } catch (error) {
            console.error('Popular plugins error:', error);
            return [];
        }
    }

    async getPlugin(name) {
        try {
            const response = await fetch(`${this.baseUrl}/plugins/${name}`);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Plugin not found');
                }
                throw new Error('Failed to fetch plugin');
            }

            return await response.json();
        } catch (error) {
            console.error('Plugin fetch error:', error);
            throw error;
        }
    }

    // Plugin Publishing
    async publishPlugin(pluginData, packageFile) {
        if (!this.apiKey) {
            throw new Error('Authentication required for publishing');
        }

        try {
            const formData = new FormData();
            formData.append('metadata', JSON.stringify(pluginData));
            if (packageFile) {
                formData.append('package', packageFile);
            }

            const response = await fetch(`${this.baseUrl}/plugins/publish`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Publish failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Publish error:', error);
            throw error;
        }
    }

    async updatePlugin(name, version, packageFile) {
        if (!this.apiKey) {
            throw new Error('Authentication required for updates');
        }

        try {
            const formData = new FormData();
            formData.append('version', version);
            if (packageFile) {
                formData.append('package', packageFile);
            }

            const response = await fetch(`${this.baseUrl}/plugins/${name}/update`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Update failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Update error:', error);
            throw error;
        }
    }

    // Plugin Installation
    async downloadPlugin(name, version = 'latest') {
        try {
            const response = await fetch(`${this.baseUrl}/plugins/${name}/download?version=${version}`);

            if (!response.ok) {
                throw new Error(`Download failed: ${response.statusText}`);
            }

            const blob = await response.blob();
            const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || `${name}.aetherplug`;

            return { blob, filename };
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    }

    async getPluginStats(name) {
        try {
            const response = await fetch(`${this.baseUrl}/plugins/${name}/stats`);

            if (!response.ok) {
                throw new Error('Failed to fetch stats');
            }

            return await response.json();
        } catch (error) {
            console.error('Stats error:', error);
            return { downloads: 0, rating: 0, reviews: 0 };
        }
    }

    // Analytics
    async getAnalyticsOverview() {
        try {
            const response = await fetch(`${this.baseUrl}/analytics/overview`);

            if (!response.ok) {
                throw new Error('Failed to fetch analytics');
            }

            return await response.json();
        } catch (error) {
            console.error('Analytics error:', error);
            return {
                totalPlugins: 0,
                totalDownloads: 0,
                totalAuthors: 0,
                averageRating: 0
            };
        }
    }

    // Utility methods
    async downloadAndSave(name, version = 'latest') {
        try {
            const { blob, filename } = await this.downloadPlugin(name, version);

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success message
            this.showNotification(`Successfully downloaded ${name}`, 'success');
        } catch (error) {
            this.showNotification(`Download failed: ${error.message}`, 'error');
            throw error;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#00d4ff' : type === 'error' ? '#ff6b6b' : '#666'};
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(notificationStyles);

// Global instance
window.aetherHub = new NeuroHubClient();
