#!/usr/bin/env python3
"""
Export last played Spotify song to docs/last_song.json for GitHub Pages
"""
import os
import json
import requests
import base64
import time
from dotenv import load_dotenv

def load_spotify_token():
    # Try to load from .spotify_cache (created by manual_auth.py or auth_setup.py)
    try:
        with open('.spotify_cache', 'r') as f:
            cache = json.load(f)
            access_token = cache.get('access_token')
            refresh_token = cache.get('refresh_token')
            expires_in = cache.get('expires_in', 3600)
            created_at = cache.get('created_at', time.time())
            
            # Check if token is expired
            if time.time() >= created_at + expires_in:
                print("🔄 Access token expired, refreshing...")
                new_token = refresh_access_token(refresh_token)
                if new_token:
                    return new_token
                else:
                    print("❌ Failed to refresh token. Please re-authenticate.")
                    return None
            return access_token
    except Exception as e:
        print(f"❌ Could not load Spotify token: {e}")
        return None

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token"""
    load_dotenv()
    CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        
        # Update the cache file with new token
        cache_data = {
            'access_token': token_data['access_token'],
            'refresh_token': refresh_token,  # Keep the same refresh token
            'expires_in': token_data['expires_in'],
            'created_at': time.time(),
            'scope': 'user-read-recently-played'
        }
        
        with open('.spotify_cache', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print("✅ Token refreshed successfully!")
        return token_data['access_token']
    else:
        print(f"❌ Token refresh failed: {response.status_code}")
        return None

def get_last_played_song(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = 'https://api.spotify.com/v1/me/player/recently-played?limit=1'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Spotify API error: {resp.status_code}")
        return None
    data = resp.json()
    if not data.get('items'):
        print("❌ No recently played tracks found.")
        return None
    item = data['items'][0]
    track = item['track']
    # Get genres from artist
    artist_id = track['artists'][0]['id']
    artist_resp = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers=headers)
    genres = []
    if artist_resp.status_code == 200:
        genres = artist_resp.json().get('genres', [])
    # Format output
    return {
        'song_name': track['name'],
        'artist': ', '.join([a['name'] for a in track['artists']]),
        'album': track['album']['name'],
        'cover_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'genres': genres[:3] if genres else ['Unknown'],
        'duration_ms': track['duration_ms'],
        'popularity': track['popularity'],
        'release_date': track['album']['release_date'],
        'external_url': track['external_urls']['spotify'],
        'preview_url': track.get('preview_url'),
        'played_at': item['played_at'],
        'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

def main():
    load_dotenv()
    access_token = load_spotify_token()
    if not access_token:
        print("❌ No valid Spotify access token. Exiting.")
        exit(1)
    song = get_last_played_song(access_token)
    if not song:
        print("❌ Could not fetch last played song.")
        exit(1)
    os.makedirs('docs', exist_ok=True)
    with open('docs/last_song.json', 'w') as f:
        json.dump(song, f, indent=2)
    print("✅ Last played song exported to docs/last_song.json")

if __name__ == "__main__":
    main()
