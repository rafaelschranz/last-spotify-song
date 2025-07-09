// Spotify Last Song App
class SpotifyLastSong {
    constructor() {
        this.loadingElement = document.getElementById('loading');
        this.errorElement = document.getElementById('error');
        this.songInfoElement = document.getElementById('song-info');
        this.refreshBtn = document.getElementById('refresh-btn');
        
        this.init();
    }
    
    init() {
        this.refreshBtn.addEventListener('click', () => this.fetchLastSong());
        
        // Check if token is configured
        if (SPOTIFY_CONFIG.accessToken === 'YOUR_SPOTIFY_ACCESS_TOKEN') {
            this.showError('Please configure your Spotify access token in config.js');
            return;
        }
        
        // Fetch last song on page load
        this.fetchLastSong();
    }
    
    showLoading() {
        this.hideAll();
        this.loadingElement.classList.remove('hidden');
        this.refreshBtn.disabled = true;
    }
    
    hideAll() {
        this.loadingElement.classList.add('hidden');
        this.errorElement.classList.add('hidden');
        this.songInfoElement.classList.add('hidden');
    }
    
    showError(message) {
        this.hideAll();
        this.errorElement.querySelector('p').textContent = message;
        this.errorElement.classList.remove('hidden');
        this.refreshBtn.disabled = false;
    }
    
    showSongInfo(songData) {
        this.hideAll();
        this.populateSongInfo(songData);
        this.songInfoElement.classList.remove('hidden');
        this.refreshBtn.disabled = false;
    }
    
    populateSongInfo(songData) {
        const track = songData.track;
        const playedAt = new Date(songData.played_at);
        
        // Update DOM elements
        document.getElementById('song-title').textContent = track.name;
        document.getElementById('artist-name').textContent = track.artists.map(artist => artist.name).join(', ');
        document.getElementById('album-title').textContent = track.album.name;
        document.getElementById('timestamp').textContent = this.formatTimestamp(playedAt);
        
        // Set album cover image
        const albumImage = document.getElementById('album-image');
        if (track.album.images && track.album.images.length > 0) {
            albumImage.src = track.album.images[0].url;
            albumImage.alt = `${track.album.name} album cover`;
        } else {
            albumImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjZjBmMGYwIi8+CjxwYXRoIGQ9Ik0xMDAgNTBMMTUwIDEwMEwxMDAgMTUwTDUwIDEwMEwxMDAgNTBaIiBmaWxsPSIjY2NjIi8+Cjwvc3ZnPgo=';
            albumImage.alt = 'No album cover available';
        }
    }
    
    formatTimestamp(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return diffInSeconds <= 1 ? 'Just now' : `${diffInSeconds} seconds ago`;
        }
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
            return diffInMinutes === 1 ? '1 minute ago' : `${diffInMinutes} minutes ago`;
        }
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) {
            return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
        }
        
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays < 30) {
            return diffInDays === 1 ? '1 day ago' : `${diffInDays} days ago`;
        }
        
        // For older dates, show the actual date
        return date.toLocaleDateString();
    }
    
    async fetchLastSong() {
        this.showLoading();
        
        try {
            const response = await fetch(SPOTIFY_CONFIG.apiUrl, {
                headers: {
                    'Authorization': `Bearer ${SPOTIFY_CONFIG.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Invalid or expired access token. Please check your config.js file.');
                } else if (response.status === 403) {
                    throw new Error('Access forbidden. Make sure your token has the user-read-recently-played scope.');
                } else if (response.status === 429) {
                    throw new Error('Rate limited. Please try again later.');
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            if (!data.items || data.items.length === 0) {
                throw new Error('No recently played songs found. Try playing a song on Spotify first.');
            }
            
            this.showSongInfo(data.items[0]);
            
        } catch (error) {
            console.error('Error fetching last song:', error);
            this.showError(error.message || 'Failed to fetch last song. Please try again.');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SpotifyLastSong();
});