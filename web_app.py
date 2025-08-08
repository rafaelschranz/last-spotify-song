#!/usr/bin/env python3
"""
Real-time Spotify Last Song Fetcher with Web Interface

This version automatically updates with your recently played songs every 30 seconds,
fetches enhanced song details including cover art and genres,
and serves a beautiful web interface to display the information.
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
import base64
from flask import Flask, render_template, jsonify
import threading
import time

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CODESPACE_NAME = os.getenv('CODESPACE_NAME')

app = Flask(__name__)

# Global variables for real-time updates
latest_song_data = None
user_access_token = None
token_expires_at = 0

def load_saved_token():
    """Load the saved access token from authentication"""
    global user_access_token, token_expires_at
    
    # Try to load from .spotify_cache (spotipy cache)
    try:
        with open('.spotify_cache', 'r') as f:
            cache = json.load(f)
            user_access_token = cache.get('access_token')
            expires_in = cache.get('expires_in', 3600)
            created_at = cache.get('created_at', time.time())
            token_expires_at = created_at + expires_in
            
            # Check if token is still valid
            if time.time() >= token_expires_at:
                print("⚠️ User token expired. Using fallback to last saved song.")
                return False
            return True
    except FileNotFoundError:
        print("⚠️ No user token found. Using fallback to last saved song.")
        return False

def get_recently_played():
    """Get recently played tracks from Spotify using user token"""
    global user_access_token
    
    if not user_access_token:
        return None
        
    headers = {'Authorization': f'Bearer {user_access_token}'}
    
    # Get recently played tracks (limit 1 for most recent)
    response = requests.get(
        'https://api.spotify.com/v1/me/player/recently-played?limit=1', 
        headers=headers
    )
    
    if response.status_code == 401:
        print("🔄 User token expired")
        return None
    elif response.status_code != 200:
        print(f"❌ Error fetching recent plays: {response.status_code}")
        return None
    
    data = response.json()
    if not data.get('items'):
        return None
        
    item = data['items'][0]
    track = item['track']
    
    # Get enhanced track details
    return get_enhanced_track_details(track['id'], item['played_at'])

def get_enhanced_track_details(track_id, played_at):
    """Get enhanced track details including genres"""
    # Use client credentials for public track data
    token = get_spotify_token()
    if not token:
        return None
        
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get detailed track information
    track_response = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)
    
    if track_response.status_code != 200:
        return None
    
    track_data = track_response.json()
    
    # Get artist details for genres
    artist_id = track_data['artists'][0]['id']
    artist_response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers=headers)
    
    genres = []
    if artist_response.status_code == 200:
        artist_data = artist_response.json()
        genres = artist_data.get('genres', [])
    
    # Format duration
    duration_ms = track_data['duration_ms']
    duration_sec = duration_ms // 1000
    minutes = duration_sec // 60
    seconds = duration_sec % 60
    
    # Get the highest quality cover image
    cover_images = track_data['album']['images']
    cover_url = cover_images[0]['url'] if cover_images else None
    
    return {
        "song_name": track_data['name'],
        "artist": ", ".join([artist['name'] for artist in track_data['artists']]),
        "album": track_data['album']['name'],
        "cover_image": cover_url,
        "genres": genres[:3] if genres else ["Unknown"],
        "duration": f"{minutes}:{seconds:02d}",
        "popularity": track_data['popularity'],
        "release_date": track_data['album']['release_date'],
        "external_url": track_data['external_urls']['spotify'],
        "preview_url": track_data.get('preview_url'),
        "played_at": played_at,
        "last_updated": datetime.now().isoformat()
    }

def background_updater():
    """Background thread to update song data periodically"""
    global latest_song_data
    
    while True:
        try:
            # Try to get real-time data first
            new_data = get_recently_played()
            
            if new_data:
                # Check if it's a new song
                if (latest_song_data is None or 
                    latest_song_data.get('song_name') != new_data.get('song_name') or
                    latest_song_data.get('played_at') != new_data.get('played_at')):
                    latest_song_data = new_data
                    print(f"🎵 New song: {new_data['song_name']} by {new_data['artist']}")
                else:
                    # Same song, just update timestamp
                    if latest_song_data:
                        latest_song_data['last_updated'] = datetime.now().isoformat()
            else:
                # Fallback to static data if real-time fails
                if latest_song_data is None:
                    static_data = get_enhanced_song_info_fallback()
                    if static_data and 'error' not in static_data:
                        latest_song_data = static_data
                        latest_song_data['last_updated'] = datetime.now().isoformat()
                        print(f"🎵 Using saved song: {static_data['song_name']} by {static_data['artist']}")
                        
        except Exception as e:
            print(f"❌ Update error: {e}")
        
        # Wait 30 seconds before next update
        time.sleep(30)
def get_spotify_token():
    """Get Spotify access token using client credentials flow"""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def get_enhanced_song_info_fallback():
    """Fallback to get song info from saved file"""
    try:
        with open('last_song.json', 'r') as f:
            basic_info = json.load(f)
    except FileNotFoundError:
        return {"error": "No song data found. Please run authentication first."}
    
    # Get enhanced details for the saved song
    track_url = basic_info.get('external_url', '')
    if '/track/' in track_url:
        track_id = track_url.split('/track/')[1].split('?')[0]
        return get_enhanced_track_details(track_id, basic_info.get('played_at', ''))
    else:
        return {"error": "Invalid track URL"}

def get_enhanced_song_info(access_token):
    """Legacy function - now redirects to real-time data"""
    global latest_song_data
    
    if latest_song_data:
        return latest_song_data
    else:
        return get_enhanced_song_info_fallback()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/last-song')
def api_last_song():
    """API endpoint to get real-time last song data"""
    global latest_song_data
    
    if latest_song_data is None:
        # Try to get initial data
        latest_song_data = get_recently_played()
        
        if latest_song_data is None:
            # Fallback to saved data
            token = get_spotify_token()
            if token:
                fallback_data = get_enhanced_song_info_fallback()
                if fallback_data and 'error' not in fallback_data:
                    latest_song_data = fallback_data
                    latest_song_data['last_updated'] = datetime.now().isoformat()
                else:
                    return jsonify({"error": "No song data available. Please run authentication and play some music."})
            else:
                return jsonify({"error": "Failed to authenticate with Spotify"})
    
    return jsonify(latest_song_data)

@app.route('/api/status')
def api_status():
    """Get update status and connection info"""
    global user_access_token, latest_song_data
    
    is_connected = user_access_token is not None and time.time() < token_expires_at
    
    return jsonify({
        "real_time_connected": is_connected,
        "has_data": latest_song_data is not None,
        "token_expires_at": token_expires_at if is_connected else None,
        "last_update": latest_song_data.get('last_updated') if latest_song_data else None,
        "update_interval": "30 seconds",
        "mode": "real-time" if is_connected else "static"
    })

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Try to load user authentication token
    has_user_token = load_saved_token()
    
    if has_user_token:
        print("✅ User authentication found - enabling real-time updates")
        # Start background updater for real-time data
        updater_thread = threading.Thread(target=background_updater, daemon=True)
        updater_thread.start()
        
        # Get initial data
        latest_song_data = get_recently_played()
        if latest_song_data:
            print(f"🎵 Currently playing: {latest_song_data['song_name']} by {latest_song_data['artist']}")
    else:
        print("⚠️ No user authentication - using static mode")
        print("💡 Run 'python manual_auth.py' for real-time updates")
    
    # Check if we're in Codespace
    if CODESPACE_NAME:
        print(f"🌐 Starting web server...")
        print(f"🔗 Open: https://{CODESPACE_NAME}-5000.app.github.dev/")
        if has_user_token:
            print(f"🔄 Real-time updates every 30 seconds")
        else:
            print(f"📊 Static mode - shows last saved song")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("🌐 Starting web server at http://localhost:5000")
        if has_user_token:
            print("🔄 Real-time updates every 30 seconds")
        else:
            print("📊 Static mode - shows last saved song")
        app.run(host='0.0.0.0', port=5000, debug=False)
