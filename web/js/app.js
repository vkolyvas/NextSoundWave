/**
 * NextSoundWave - YouTube Music Inspired Application
 */

class NextSoundWaveApp {
    constructor() {
        this.api = new APIClient();
        this.player = new AudioPlayer();
        this.currentTrack = null;
        this.relatedVideos = [];
        this.queue = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupPlayerListeners();
        this.renderHomeView();
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
        
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.navigateTo(page);
            });
        });
        
        // Player controls
        document.getElementById('btn-play').addEventListener('click', () => {
            this.togglePlay();
        });
        
        document.getElementById('btn-prev').addEventListener('click', () => {
            this.playPrevious();
        });
        
        document.getElementById('btn-next').addEventListener('click', () => {
            this.playNext();
        });
        
        document.getElementById('btn-shuffle').addEventListener('click', () => {
            this.toggleShuffle();
        });
        
        document.getElementById('btn-repeat').addEventListener('click', () => {
            this.toggleRepeat();
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
            this.updateVolumeIcon(e.target.value);
        });
        
        // Like button
        document.getElementById('like-btn').addEventListener('click', () => {
            this.toggleLike();
        });
        
        // Queue toggle
        document.getElementById('btn-queue').addEventListener('click', () => {
            this.toggleQueue();
        });
    }
    
    setupPlayerListeners() {
        const audio = this.player.audio;
        
        if (!audio) return;
        
        audio.addEventListener('loadedmetadata', () => {
            this.updateTimeDisplay();
        });
        
        audio.addEventListener('timeupdate', () => {
            this.updateTimeDisplay();
            this.updateProgress();
        });
        
        audio.addEventListener('ended', () => {
            this.onTrackEnded();
        });
        
        audio.addEventListener('error', (e) => {
            console.error('Playback error:', e);
        });
    }
    
    navigateTo(page) {
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });
        
        // Hide search results, show appropriate view
        document.getElementById('search-results').classList.add('hidden');
        document.getElementById('hero-section').classList.remove('hidden');
        document.getElementById('featured-section').classList.remove('hidden');
        
        switch(page) {
            case 'home':
                this.renderHomeView();
                break;
            case 'explore':
                this.renderExploreView();
                break;
            case 'library':
                this.renderLibraryView();
                break;
        }
    }
    
    renderHomeView() {
        const quickPicks = document.getElementById('quick-picks-list');
        const featured = document.getElementById('featured-list');
        
        quickPicks.innerHTML = `
            <div class="music-card" data-id="demo1">
                <div class="card-artwork">
                    <img src="https://picsum.photos/200" alt="Lofi Dreams">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Lofi Dreams</div>
                    <div class="card-subtitle">Chill Vibes</div>
                </div>
            </div>
            <div class="music-card" data-id="demo2">
                <div class="card-artwork">
                    <img src="https://picsum.photos/201" alt="Night Drive">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Night Drive</div>
                    <div class="card-subtitle">Synthwave Mix</div>
                </div>
            </div>
            <div class="music-card" data-id="demo3">
                <div class="card-artwork">
                    <img src="https://picsum.photos/202" alt="Focus Mode">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Focus Mode</div>
                    <div class="card-subtitle">Ambient Study</div>
                </div>
            </div>
            <div class="music-card" data-id="demo4">
                <div class="card-artwork">
                    <img src="https://picsum.photos/203" alt="Workout Energy">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Workout Energy</div>
                    <div class="card-subtitle">High Tempo</div>
                </div>
            </div>
            <div class="music-card" data-id="demo5">
                <div class="card-artwork">
                    <img src="https://picsum.photos/204" alt="Morning Coffee">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Morning Coffee</div>
                    <div class="card-subtitle">Acoustic Chill</div>
                </div>
            </div>
        `;
        
        featured.innerHTML = `
            <div class="music-card" data-id="demo6">
                <div class="card-artwork">
                    <img src="https://picsum.photos/205" alt="Top 50">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Top 50: Global</div>
                    <div class="card-subtitle">YouTube Music</div>
                </div>
            </div>
            <div class="music-card" data-id="demo7">
                <div class="card-artwork">
                    <img src="https://picsum.photos/206" alt="New Releases">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">New Releases</div>
                    <div class="card-subtitle">This Week</div>
                </div>
            </div>
            <div class="music-card" data-id="demo8">
                <div class="card-artwork">
                    <img src="https://picsum.photos/207" alt="Viral Hits">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Viral Hits</div>
                    <div class="card-subtitle">Trending Now</div>
                </div>
            </div>
            <div class="music-card" data-id="demo9">
                <div class="card-artwork">
                    <img src="https://picsum.photos/208" alt="Indie Gems">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Indie Gems</div>
                    <div class="card-subtitle">Discover Weekly</div>
                </div>
            </div>
            <div class="music-card" data-id="demo10">
                <div class="card-artwork">
                    <img src="https://picsum.photos/209" alt="Classic Rock">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Classic Rock</div>
                    <div class="card-subtitle">Legends</div>
                </div>
            </div>
            <div class="music-card" data-id="demo11">
                <div class="card-artwork">
                    <img src="https://picsum.photos/210" alt="Jazz Classics">
                    <div class="card-play-btn"><span class="material-icons">play_arrow</span></div>
                </div>
                <div class="card-info">
                    <div class="card-title">Jazz Classics</div>
                    <div class="card-subtitle">Essential</div>
                </div>
            </div>
        `;
        
        this.attachCardListeners();
    }
    
    renderExploreView() {
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <section class="hero-section">
                <div class="hero-content">
                    <h1 class="hero-title">Explore</h1>
                    <p class="hero-subtitle">Discover new music</p>
                </div>
            </section>
            <section class="content-section">
                <h2 class="section-title">Genres</h2>
                <div class="grid-scroll" id="genres-grid">
                    <div class="genre-card" data-genre="Pop"><div class="genre-artwork"><img src="https://picsum.photos/230"></div><div class="genre-name">Pop</div></div>
                    <div class="genre-card" data-genre="Rock"><div class="genre-artwork"><img src="https://picsum.photos/231"></div><div class="genre-name">Rock</div></div>
                    <div class="genre-card" data-genre="Hip Hop"><div class="genre-artwork"><img src="https://picsum.photos/232"></div><div class="genre-name">Hip Hop</div></div>
                    <div class="genre-card" data-genre="Electronic"><div class="genre-artwork"><img src="https://picsum.photos/233"></div><div class="genre-name">Electronic</div></div>
                    <div class="genre-card" data-genre="Jazz"><div class="genre-artwork"><img src="https://picsum.photos/234"></div><div class="genre-name">Jazz</div></div>
                    <div class="genre-card" data-genre="Classical"><div class="genre-artwork"><img src="https://picsum.photos/235"></div><div class="genre-name">Classical</div></div>
                </div>
            </section>
        `;
        
        document.querySelectorAll('.genre-card').forEach(card => {
            card.addEventListener('click', () => {
                const genre = card.dataset.genre;
                this.search(genre);
            });
        });
    }
    
    renderLibraryView() {
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <section class="hero-section">
                <div class="hero-content">
                    <h1 class="hero-title">Library</h1>
                    <p class="hero-subtitle">Your music collection</p>
                </div>
            </section>
            <section class="content-section">
                <h2 class="section-title">Recently played</h2>
                <div class="horizontal-scroll" id="recently-played">
                    <div class="music-card horizontal-card" data-id="recent1"><div class="card-artwork"><img src="https://picsum.photos/240"><div class="card-play-btn"><span class="material-icons">play_arrow</span></div></div><div class="card-info"><div class="card-title">Favorites</div><div class="card-subtitle">Your top songs</div></div></div>
                    <div class="music-card horizontal-card" data-id="recent2"><div class="card-artwork"><img src="https://picsum.photos/241"><div class="card-play-btn"><span class="material-icons">play_arrow</span></div></div><div class="card-info"><div class="card-title">Mix 1</div><div class="card-subtitle">Recommended</div></div></div>
                    <div class="music-card horizontal-card" data-id="recent3"><div class="card-artwork"><img src="https://picsum.photos/242"><div class="card-play-btn"><span class="material-icons">play_arrow</span></div></div><div class="card-info"><div class="card-title">Mix 2</div><div class="card-subtitle">Discover Weekly</div></div></div>
                    <div class="music-card horizontal-card" data-id="recent4"><div class="card-artwork"><img src="https://picsum.photos/243"><div class="card-play-btn"><span class="material-icons">play_arrow</span></div></div><div class="card-info"><div class="card-title">Mix 3</div><div class="card-subtitle">Daily Mix</div></div></div>
                    <div class="music-card horizontal-card" data-id="recent5"><div class="card-artwork"><img src="https://picsum.photos/244"><div class="card-play-btn"><span class="material-icons">play_arrow</span></div></div><div class="card-info"><div class="card-title">History</div><div class="card-subtitle">Recently played</div></div></div>
                </div>
            </section>
            <section class="content-section">
                <h2 class="section-title">Your playlists</h2>
                <div class="grid-scroll" id="playlists-grid">
                    <div class="music-card create-playlist-card" id="create-playlist">
                        <div class="card-artwork create-artwork"><span class="material-icons">add</span></div>
                        <div class="card-info"><div class="card-title">Create playlist</div><div class="card-subtitle">New playlist</div></div>
                    </div>
                </div>
            </section>
        `;
        
        document.getElementById('create-playlist').addEventListener('click', () => {
            this.createPlaylist();
        });
        
        this.attachCardListeners();
    }
    
    attachCardListeners() {
        document.querySelectorAll('.music-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = card.dataset.id;
                this.playCard(id);
            });
        });
    }
    
    async playCard(id) {
        // For demo, create a track
        const track = {
            id: id,
            title: 'Demo Track ' + id,
            artist: 'Demo Artist',
            duration: 180,
            thumbnail: 'https://picsum.photos/200'
        };
        await this.playTrack(track);
    }
    
    async playTrack(track) {
        this.currentTrack = track;
        this.updatePlayerUI(track);
        this.addToQueue(track);
        this.isPlaying = true;
        this.updatePlayPauseButton();
    }
    
    async search(query) {
        // Hide home views, show search
        document.getElementById('hero-section').classList.add('hidden');
        document.getElementById('featured-section').classList.add('hidden');
        document.getElementById('search-results').classList.remove('hidden');
        
        try {
            const results = await this.api.search(query);
            this.renderSearchResults(results, query);
        } catch (error) {
            console.error('Search failed:', error);
            document.getElementById('search-results-grid').innerHTML = `
                <div class="search-no-results">
                    <p>Search failed. Please try again.</p>
                </div>
            `;
        }
    }
    
    renderSearchResults(results, query) {
        const grid = document.getElementById('search-results-grid');
        
        if (!results || !results.results || results.results.length === 0) {
            grid.innerHTML = `<div class="search-no-results"><p>No results found for "${this.escapeHtml(query)}"</p></div>`;
            return;
        }
        
        grid.innerHTML = results.results.map(item => `
            <div class="search-result-card" data-id="${item.id}" data-title="${this.escapeHtml(item.title)}">
                <div class="search-result-thumb">
                    <img src="https://img.youtube.com/vi/${item.id}/120.jpg" alt="${this.escapeHtml(item.title)}" onerror="this.src='https://picsum.photos/80'">
                </div>
                <div class="search-result-info">
                    <div class="search-result-title">${this.escapeHtml(item.title)}</div>
                    <div class="search-result-subtitle">Song</div>
                    <div class="search-result-meta">${this.formatDuration(item.duration)}</div>
                </div>
            </div>
        `).join('');
        
        grid.querySelectorAll('.search-result-card').forEach(card => {
            card.addEventListener('click', async () => {
                const id = card.dataset.id;
                const title = card.dataset.title;
                const result = results.results.find(r => r.id === id);
                await this.playTrack({
                    id: id,
                    title: title || result.title,
                    artist: 'Unknown Artist',
                    duration: result.duration,
                    thumbnail: `https://img.youtube.com/vi/${id}/120.jpg`
                });
            });
        });
    }
    
    addToQueue(track) {
        const exists = this.queue.find(t => t.id === track.id);
        if (!exists) {
            this.queue.push(track);
            this.renderQueue();
        }
    }
    
    renderQueue() {
        const queueList = document.getElementById('queue-list');
        
        if (this.queue.length === 0) {
            queueList.innerHTML = '<p class="placeholder-text">Queue is empty</p>';
            return;
        }
        
        queueList.innerHTML = this.queue.map((track, index) => `
            <div class="queue-item ${index === this.currentIndex ? 'active' : ''}" data-index="${index}">
                <div class="queue-thumb"><img src="${track.thumbnail || 'https://picsum.photos/48'}" alt="${this.escapeHtml(track.title)}"></div>
                <div class="queue-info">
                    <div class="queue-title">${this.escapeHtml(track.title)}</div>
                    <div class="queue-artist">${this.escapeHtml(track.artist || 'Unknown')}</div>
                </div>
            </div>
        `).join('');
        
        queueList.querySelectorAll('.queue-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.currentIndex = index;
                this.playTrack(this.queue[index]);
            });
        });
    }
    
    togglePlay() {
        this.isPlaying = !this.isPlaying;
        this.updatePlayPauseButton();
    }
    
    playPrevious() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.playTrack(this.queue[this.currentIndex]);
        } else {
            this.player.restart();
        }
    }
    
    playNext() {
        if (this.queue.length > 0 && this.currentIndex < this.queue.length - 1) {
            this.currentIndex++;
            this.playTrack(this.queue[this.currentIndex]);
        }
    }
    
    onTrackEnded() {
        this.playNext();
    }
    
    toggleShuffle() {
        document.getElementById('btn-shuffle').classList.toggle('active');
    }
    
    toggleRepeat() {
        const btn = document.getElementById('btn-repeat');
        const icon = btn.querySelector('.material-icons');
        btn.classList.toggle('active');
        icon.textContent = btn.classList.contains('active') ? 'repeat_one' : 'repeat';
    }
    
    toggleLike() {
        const btn = document.getElementById('like-btn');
        const icon = btn.querySelector('.material-icons');
        icon.textContent = icon.textContent === 'thumb_up' ? 'thumb_up_off_alt' : 'thumb_up';
        icon.style.color = icon.textContent === 'thumb_up' ? 'var(--ytm-brand-red)' : '';
    }
    
    toggleQueue() {
        document.getElementById('right-panel').classList.toggle('hidden');
    }
    
    updatePlayerUI(track) {
        document.getElementById('player-track-title').textContent = track.title;
        document.getElementById('player-artist').textContent = track.artist || 'Unknown Artist';
        
        const thumbnail = document.getElementById('player-thumbnail');
        thumbnail.src = track.thumbnail;
        thumbnail.classList.remove('hidden');
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
        const fill = document.getElementById('progress-fill');
        if (fill) fill.style.width = `${progress || 0}%`;
    }
    
    updatePlayPauseButton() {
        const btn = document.getElementById('btn-play');
        const icon = btn.querySelector('.material-icons');
        icon.textContent = this.isPlaying ? 'pause' : 'play_arrow';
    }
    
    updateVolumeIcon(volume) {
        const icon = document.getElementById('volume-icon');
        if (volume == 0) icon.textContent = 'volume_off';
        else if (volume < 50) icon.textContent = 'volume_down';
        else icon.textContent = 'volume_up';
    }
    
    formatDuration(seconds) {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    createPlaylist() {
        const name = prompt('Enter playlist name:');
        if (name) {
            alert(`Playlist "${name}" created!`);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NextSoundWaveApp();
});
