/**
 * API Client - Communication with backend
 */

class APIClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    async resolve(url) {
        return await this.request('/resolve', {
            method: 'POST',
            body: JSON.stringify({ url })
        });
    }
    
    async search(query, limit = 20) {
        return await this.request(`/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    }
    
    async healthCheck() {
        return await this.request('/health');
    }
}
