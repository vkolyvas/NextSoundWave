/**
 * Audio/Video Player with AdBlock Support
 * Priority: YouTube Embed (with AdBlock) → Direct Audio → Invidious (last resort)
 */

class AudioPlayer {
    constructor() {
        this.audio = document.getElementById('audio-player');
        this.isPlaying = false;
        this.currentTrack = null;
        this.preloadedUrl = null;
        this.isEmbedMode = false;
        this.currentEmbedType = null; // 'youtube' or 'invidious'
        
        this.setupListeners();
    }
    
    setupListeners() {
        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButton();
        });
        
        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButton();
        });
        
        this.audio.addEventListener('ended', () => {
            this.isPlaying = false;
            this.updatePlayButton();
        });
    }
    
    /**
     * Play audio directly (from direct stream URL)
     */
    play(url) {
        this.stopEmbed();
        
        if (this.preloadedUrl === url) {
            this.audio.src = url;
            this.preloadedUrl = null;
        } else if (this.audio.src !== url) {
            this.audio.src = url;
        }
        
        this.isEmbedMode = false;
        this.currentEmbedType = null;
        this.audio.play().catch(error => {
            console.error('Audio play failed:', error);
            throw error;
        });
    }
    
    /**
     * Play YouTube embed with AdBlock
     * @param {string} embedUrl - YouTube embed URL
     * @param {HTMLElement} container - Container to embed in
     */
    playYouTubeEmbed(embedUrl, container) {
        // Stop any playing media
        this.stopEmbed();
        this.audio.pause();
        this.audio.src = '';
        
        this.isEmbedMode = true;
        this.isPlaying = true;
        this.currentEmbedType = 'youtube';
        this.updatePlayButton();
        
        // Create embed container with AdBlock
        const embedContainer = document.createElement('div');
        embedContainer.className = 'youtube-embed-container';
        embedContainer.style.cssText = `
            position: relative;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
        `;
        
        // Create iframe with AdBlock parameters
        const iframe = document.createElement('iframe');
        iframe.src = this._addAdBlockParams(embedUrl);
        iframe.setAttribute('frameborder', '0');
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
        iframe.setAttribute('allowfullscreen', 'true');
        iframe.style.cssText = `
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        `;
        
        // Add AdBlock CSS to hide ads
        const adBlockCSS = document.createElement('style');
        adBlockCSS.textContent = `
            .youtube-embed-container .ad,
            .youtube-embed-container .ads,
            .youtube-embed-container .video-ads,
            .youtube-embed-container .ytp-ad,
            .youtube-embed-container .ytp-ad-module,
            .youtube-embed-container .ytp-ad-player-overlay,
            .youtube-embed-container .ytp-ad-skip-button,
            .youtube-embed-container .ytp-ad-text,
            .youtube-embed-container .ytp-commercial,
            .youtube-embed-container .ytp-feedbaclk-action,
            .youtube-embed-container .html5-spacer,
            .youtube-embed-container .ytp-gradient-top,
            .youtube-embed-container .ytp-chrome-top,
            .youtube-embed-container .ytp-chrome-bottom,
            .youtube-embed-container .ytp-show-cards-button,
            .youtube-embed-container [data-ad-preview],
            .youtube-embed-container .ytd-mealbar-promotion-renderer,
            .youtube-embed-container .ytp-paid-content-overlay,
            .youtube-embed-container .ytp-mweb-nonmembers,
            .youtube-embed-container .ytp-storyboard-frame-preview,
            .youtube-embed-container .ytp-ce-element,
            .youtube-embed-container .ytp-cards-teaser {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                max-height: 0 !important;
                overflow: hidden !important;
            }
            .youtube-embed-container iframe {
                border: none;
            }
            .youtube-embed-container video {
                border-radius: 0 !important;
            }
        `;
        
        // Clear container and add embed
        container.innerHTML = '';
        container.appendChild(adBlockCSS);
        container.appendChild(embedContainer);
        embedContainer.appendChild(iframe);
    }
    
    /**
     * Add AdBlock parameters to YouTube URL
     */
    _addAdBlockParams(url) {
        // YouTube embed parameters that reduce ads
        const params = new URLSearchParams({
            'rel': '0',           // No related videos from other channels
            'modestbranding': '1', // Hide logo
            'iv_load_policy': '3', // Hide annotations
            'disablekb': '1',     // Disable keyboard controls
            'fs': '1',            // Allow fullscreen
            'autoplay': '1',      // Auto-play
        });
        
        return `${url}?${params.toString()}`;
    }
    
    /**
     * Play via Invidious embed (last resort - ad-free by design)
     */
    playInvidiousEmbed(embedUrl, container) {
        // Stop any playing media
        this.stopEmbed();
        this.audio.pause();
        this.audio.src = '';
        
        this.isEmbedMode = true;
        this.isPlaying = true;
        this.currentEmbedType = 'invidious';
        this.updatePlayButton();
        
        // Invidious is ad-free by design
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl;
        iframe.setAttribute('frameborder', '0');
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
        iframe.setAttribute('allowfullscreen', 'true');
        iframe.style.cssText = `
            width: 100%;
            height: 100%;
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        `;
        
        // Clear container and add iframe
        container.innerHTML = '';
        container.appendChild(iframe);
    }
    
    /**
     * Stop embed playback
     */
    stopEmbed() {
        if (this.isEmbedMode) {
            const container = document.getElementById('content-area');
            if (container) {
                container.innerHTML = '<p class="placeholder-text">Select a track to play...</p>';
            }
            this.isEmbedMode = false;
            this.currentEmbedType = null;
        }
    }
    
    pause() {
        if (this.isEmbedMode) {
            // For embeds, we can't control iframe playback
            this.isPlaying = false;
            this.updatePlayButton();
        } else {
            this.audio.pause();
        }
    }
    
    resume() {
        if (!this.isEmbedMode) {
            this.audio.play().catch(error => {
                console.error('Resume failed:', error);
            });
        }
    }
    
    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.resume();
        }
    }
    
    seek(time) {
        if (!this.isEmbedMode) {
            this.audio.currentTime = time;
        }
    }
    
    restart() {
        if (!this.isEmbedMode) {
            this.audio.currentTime = 0;
            this.audio.play();
        }
    }
    
    setVolume(volume) {
        if (!this.isEmbedMode) {
            this.audio.volume = Math.max(0, Math.min(1, volume));
        }
    }
    
    preload(url) {
        this.preloadedUrl = url;
    }
    
    get currentTime() {
        return this.isEmbedMode ? 0 : this.audio.currentTime;
    }
    
    get duration() {
        return this.isEmbedMode ? 0 : this.audio.duration;
    }
    
    updatePlayButton() {
        const btn = document.getElementById('btn-play');
        if (btn) {
            btn.textContent = this.isPlaying ? '⏸' : '▶';
        }
    }
}
