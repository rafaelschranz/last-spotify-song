#!/usr/bin/env python3
"""
Manual OAuth handler for Spotify in Codespaces
"""

import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlencode
import base64

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CODESPACE_NAME = os.getenv('CODESPACE_NAME')

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    
    redirect_uri = f"https://{CODESPACE_NAME}-8080.app.github.dev/callback"
    
    # Prepare the token request
    token_url = "https://accounts.spotify.com/api/token"
    
    # Create basic auth header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_last_played_song(access_token):
    """Get last played song using access token"""
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Get recently played tracks
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=1"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            track = data['items'][0]['track']
            return {
                'song_name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'played_at': data['items'][0]['played_at'],
                'external_url': track['external_urls']['spotify']
            }
    return None

# Extract the code from the URL you got
auth_code = "AQAW36YwzEJA2_YlX_m9pG7hOFl6xoiWX57hhCtly_zLwc1XM2W72ZUSYUJ6nUsEfa2axdCrw1-ew4NEPcaL5VByNPVY8MKxwge88EeCkGpxX4pVIelu-qGlBlqGaC9DL864cv8h2zOVxt5lRPeULu1edAm30XQoTs1Yz5rSL3yNNznKGx4p7zNlzvqFgPNMneYD1auIgJP7WnJmdqlY53UBsUgyPYrtcMde_ZMJKtgZD1f9uh1Ok9vrnCX_r1sIH1qs"

print("🎵 Getting access token...")
token_data = exchange_code_for_token(auth_code)

if token_data:
    access_token = token_data['access_token']
    print("✅ Got access token!")
    
    print("📡 Fetching last played song...")
    song_info = get_last_played_song(access_token)
    
    if song_info:
        print("\n🎵 Last Played Song on Spotify")
        print("=" * 40)
        print(f"🎶 Song: {song_info['song_name']}")
        print(f"👨‍🎤 Artist: {song_info['artist']}")
        print(f"💿 Album: {song_info['album']}")
        print(f"⏰ Played at: {song_info['played_at']}")
        print(f"🔗 Spotify URL: {song_info['external_url']}")
        
        # Save to file
        with open('last_song.json', 'w') as f:
            json.dump(song_info, f, indent=2)
        print("\n💾 Song info saved to 'last_song.json'")
    else:
        print("❌ No recent tracks found")
else:
    print("❌ Failed to get access token")
