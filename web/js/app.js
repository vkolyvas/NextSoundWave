/**
 * NextSoundWave - Main Application Orchestrator
 */

class NextSoundWaveApp {
    constructor() {
        this.api = new APIClient();
        this.player = new AudioPlayer();
        this.currentTrack = null;
        this.relatedVideos = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupPlayerListeners();
    }
    
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    await this.search(query);
                }
            }
        });
        
        // Player controls
        document.getElementById('btn-play').addEventListener('click', () => {
            this.player.togglePlay();
        });
        
        document.getElementById('btn-prev').addEventListener('click', () => {
            this.playPrevious();
        });
        
        document.getElementById('btn-next').addEventListener('click', () => {
            this.playNext();
        });
        
        // Progress bar
        const progressBar = document.getElementById('progress-bar');
        progressBar.addEventListener('input', (e) => {
            const time = (e.target.value / 100) * this.player.duration;
            this.player.seek(time);
        });
        
        // Volume slider
        const volumeSlider = document.getElementById('volume-slider');
        volumeSlider.addEventListener('input', (e) => {
            this.player.setVolume(e.target.value / 100);
        });
    }
    
    setupPlayerListeners() {
        const audio = this.player.audio;
        
        audio.addEventListener('loadedmetadata', () => {
            this.updateTimeDisplay();
        });
        
        audio.addEventListener('timeupdate', () => {
            this.updateTimeDisplay();
            this.updateProgress();
            this.checkGaplessPlayback();
        });
        
        audio.addEventListener('ended', () => {
            this.playNext();
        });
        
        audio.addEventListener('error', (e) => {
            console.error('Playback error:', e);
            this.showError('Failed to play track');
        });
    }
    
    async search(query) {
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = '<p>Searching...</p>';
        
        try {
            const results = await this.api.search(query);
            this.renderSearchResults(results);
        } catch (error) {
            contentArea.innerHTML = `<p class="error">Search failed: ${error.message}</p>`;
        }
    }
    
    renderSearchResults(results) {
        const contentArea = document.getElementById('content-area');
        
        if (!results || results.length === 0) {
            contentArea.innerHTML = '<p>No results found</p>';
            return;
        }
        
        const html = `
            <h2>Search Results for "${results.query}"</h2>
            <div class="search-results">
                ${results.results.map(item => `
                    <div class="result-card" data-id="${item.id}">
                        <img class="result-thumbnail" src="${item.thumbnail || ''}" alt="">
                        <div class="result-info">
                            <div class="result-title">${this.escapeHtml(item.title)}</div>
                            <div class="result-duration">${this.formatDuration(item.duration)}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        contentArea.innerHTML = html;
        
        // Add click handlers
        contentArea.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', async () => {
                const videoId = card.dataset.id;
                await this.playVideo(videoId);
            });
        });
    }
    
    async playVideo(videoId) {
        try {
            // Resolve the video
            const track = await this.api.resolve(`https://www.youtube.com/watch?v=${videoId}`);
            
            // Update player UI
            this.updatePlayerUI(track);
            
            // Playback priority: YouTube Embed (AdBlock) → Direct Audio → Invidious (last resort)
            const contentArea = document.getElementById('content-area');
            
            if (track.embed_url) {
                // PRIMARY: YouTube embed with AdBlock
                this.player.playYouTubeEmbed(track.embed_url, contentArea);
            } else if (track.audio_url) {
                // FALLBACK: Direct audio stream
                this.player.play(track.audio_url);
            } else if (track.invidious_url) {
                // LAST RESORT: Invidious embed (ad-free by design)
                this.player.playInvidiousEmbed(track.invidious_url, contentArea);
            } else {
                throw new Error('No playable URL available');
            }
            
            // Store related videos
            this.relatedVideos = track.related || [];
            this.renderRelatedVideos();
            
        } catch (error) {
            this.showError(`Failed to play: ${error.message}`);
        }
    }
    
    updatePlayerUI(track) {
        document.getElementById('player-track-title').textContent = track.title;
        document.getElementById('player-artist').textContent = 'YouTube';
        
        const thumbnail = document.getElementById('player-thumbnail');
        thumbnail.src = `https://img.youtube.com/vi/${track.id}/56.jpg`;
        thumbnail.classList.remove('hidden');
        
        document.getElementById('btn-play').textContent = '⏸';
    }
    
    renderRelatedVideos() {
        const container = document.getElementById('related-videos');
        
        if (!this.relatedVideos.length) {
            container.innerHTML = '<p class="placeholder-text">No related videos</p>';
            return;
        }
        
        container.innerHTML = this.relatedVideos.map(video => `
            <div class="related-video-item" data-id="${video.id}">
                <div class="related-info">
                    <div class="related-title">${this.escapeHtml(video.title)}</div>
                    <div class="related-duration">${this.formatDuration(video.duration)}</div>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        container.querySelectorAll('.related-video-item').forEach(item => {
            item.addEventListener('click', async () => {
                const videoId = item.dataset.id;
                await this.playVideo(videoId);
            });
        });
    }
    
    playPrevious() {
        // For MVP: restart current track
        this.player.restart();
    }
    
    playNext() {
        if (this.relatedVideos.length > 0) {
            // Play the first related video
            const nextVideo = this.relatedVideos[0];
            this.playVideo(nextVideo.id);
        }
    }
    
    checkGaplessPlayback() {
        // Gapless pre-fetch logic (T-15s)
        const remaining = this.player.duration - this.player.currentTime;
        
        if (remaining <= 15 && this.relatedVideos.length > 0) {
            const nextVideo = this.relatedVideos[0];
            // Pre-fetch next track URL in background
            this.api.resolve(`https://www.youtube.com/watch?v=${nextVideo.id}`)
                .then(track => {
                    this.player.preload(track.audio_url);
                })
                .catch(() => {
                    // Ignore pre-fetch errors
                });
        }
    }
    
    updateTimeDisplay() {
        const current = this.player.currentTime;
        const duration = this.player.duration || 0;
        
        document.getElementById('current-time').textContent = this.formatDuration(current);
        document.getElementById('total-time').textContent = this.formatDuration(duration);
    }
    
    updateProgress() {
        const progress = (this.player.currentTime / this.player.duration) * 100;
        document.getElementById('progress-bar').value = progress || 0;
    }
    
    showError(message) {
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `<p class="error">${this.escapeHtml(message)}</p>`;
    }
    
    formatDuration(seconds) {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NextSoundWaveApp();
});
