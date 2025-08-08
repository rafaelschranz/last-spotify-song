#!/usr/bin/env python3
"""
Spotify Last Song Fetcher with Codespace support

This version includes a simple HTTP server to handle OAuth callbacks in Codespaces.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime
import json
import http.server
import socketserver
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs
import time

# Load environment variables
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Required scopes for accessing recently played tracks
SCOPE = 'user-read-recently-played'

# Global variable to store the authorization code
auth_code = None
server_running = False

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback from Spotify"""
    
    def do_GET(self):
        global auth_code, server_running
        
        if self.path.startswith('/callback'):
            # Parse the authorization code from the URL
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <head><title>Authorization Successful</title></head>
                <body>
                <h1>Authorization Successful!</h1>
                <p>You can now close this tab and return to your terminal.</p>
                <script>window.close();</script>
                </body>
                </html>
                ''')
                server_running = False
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <head><title>Authorization Failed</title></head>
                <body>
                <h1>Authorization Failed</h1>
                <p>Please try again.</p>
                </body>
                </html>
                ''')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress server logs
        return

def start_callback_server():
    """Start a simple HTTP server to handle OAuth callbacks"""
    global server_running
    server_running = True
    
    port = 8080
    with socketserver.TCPServer(("", port), CallbackHandler) as httpd:
        print(f"🌐 Starting callback server on port {port}")
        while server_running:
            httpd.handle_request()

def setup_spotify_client():
    """
    Set up and return a Spotify client with OAuth authentication.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "Spotify credentials not found. Please check your .env file.\n"
            "Required variables: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET"
        )
    
    # Check if we're in a Codespace
    codespace_name = os.getenv('CODESPACE_NAME')
    if codespace_name and not REDIRECT_URI.startswith('https://'):
        # Update redirect URI for Codespace
        redirect_uri = f"https://{codespace_name}-8080.app.github.dev/callback"
        print(f"🔧 Detected Codespace. Using redirect URI: {redirect_uri}")
        print("⚠️  Make sure to add this URI to your Spotify app settings!")
    else:
        redirect_uri = REDIRECT_URI
    
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        cache_path=".spotify_cache",
        show_dialog=True
    )
    
    return spotipy.Spotify(auth_manager=auth_manager)

def get_last_played_song(sp):
    """
    Fetch the last played song from Spotify.
    
    Args:
        sp: Spotify client instance
        
    Returns:
        dict: Information about the last played song
    """
    try:
        # Get recently played tracks (limit=1 to get just the last one)
        results = sp.current_user_recently_played(limit=1)
        
        if not results['items']:
            return {"error": "No recently played tracks found"}
        
        # Extract the last played track
        last_track = results['items'][0]
        track = last_track['track']
        
        # Format the track information
        song_info = {
            "song_name": track['name'],
            "artist": ", ".join([artist['name'] for artist in track['artists']]),
            "album": track['album']['name'],
            "played_at": last_track['played_at'],
            "duration_ms": track['duration_ms'],
            "external_url": track['external_urls']['spotify'],
            "preview_url": track.get('preview_url'),
            "popularity": track['popularity']
        }
        
        return song_info
        
    except Exception as e:
        return {"error": f"Failed to fetch last played song: {str(e)}"}

def format_song_info(song_info):
    """
    Format song information for display.
    
    Args:
        song_info (dict): Song information dictionary
        
    Returns:
        str: Formatted song information
    """
    if "error" in song_info:
        return f"❌ Error: {song_info['error']}"
    
    # Convert played_at to readable format
    played_at = datetime.fromisoformat(song_info['played_at'].replace('Z', '+00:00'))
    local_time = played_at.strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert duration to minutes:seconds
    duration_sec = song_info['duration_ms'] // 1000
    minutes = duration_sec // 60
    seconds = duration_sec % 60
    
    output = f"""
🎵 Last Played Song on Spotify
{'=' * 40}
🎶 Song: {song_info['song_name']}
👨‍🎤 Artist: {song_info['artist']}
💿 Album: {song_info['album']}
⏰ Played at: {local_time}
⏱️  Duration: {minutes}:{seconds:02d}
📈 Popularity: {song_info['popularity']}/100
🔗 Spotify URL: {song_info['external_url']}
"""
    
    if song_info['preview_url']:
        output += f"🎧 Preview: {song_info['preview_url']}\n"
    
    return output

def main():
    """
    Main function to fetch and display the last played song.
    """
    print("🎵 Spotify Last Song Fetcher")
    print("=" * 40)
    
    try:
        # Check if we're in a Codespace and show the redirect URI
        codespace_name = os.getenv('CODESPACE_NAME')
        if codespace_name:
            redirect_uri = f"https://{codespace_name}-8080.app.github.dev/callback"
            print(f"🔧 Codespace detected!")
            print(f"📋 Add this redirect URI to your Spotify app: {redirect_uri}")
            print("=" * 40)
        
        # Start callback server in a separate thread if needed
        if codespace_name:
            server_thread = threading.Thread(target=start_callback_server, daemon=True)
            server_thread.start()
            time.sleep(1)  # Give server time to start
        
        # Set up Spotify client
        print("🔐 Authenticating with Spotify...")
        sp = setup_spotify_client()
        
        # Get last played song
        print("📡 Fetching last played song...")
        song_info = get_last_played_song(sp)
        
        # Display the result
        print(format_song_info(song_info))
        
        # Optionally save to JSON file
        if "error" not in song_info:
            with open('last_song.json', 'w') as f:
                json.dump(song_info, f, indent=2)
            print("💾 Song info saved to 'last_song.json'")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
