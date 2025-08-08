#!/usr/bin/env python3
"""
Create Spotify authentication cache for real-time updates
"""

import os
import requests
import json
import base64
import time
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
CODESPACE_NAME = os.getenv('CODESPACE_NAME')

def create_auth_cache():
    """Create authentication cache for web app"""
    
    redirect_uri = f"https://{CODESPACE_NAME}-8080.app.github.dev/callback"
    
    print("🔑 Spotify Authentication for Real-time Updates")
    print("=" * 50)
    print()
    print("To enable real-time updates, we need to get a fresh access token.")
    print()
    print("1. Visit this URL to authorize:")
    auth_url = f"https://accounts.spotify.com/authorize?"
    auth_url += f"client_id={CLIENT_ID}"
    auth_url += f"&response_type=code"
    auth_url += f"&redirect_uri={redirect_uri}"
    auth_url += f"&scope=user-read-recently-played"
    
    print(f"   {auth_url}")
    print()
    print("2. After authorization, you'll be redirected to a page that says 'This page can't be found'")
    print("3. Copy the FULL URL from your browser address bar and paste it below")
    print()
    
    callback_url = input("Paste the full callback URL here: ").strip()
    
    # Extract the authorization code
    if '?code=' in callback_url:
        auth_code = callback_url.split('?code=')[1].split('&')[0]
    else:
        print("❌ No authorization code found in URL")
        return False
    
    # Exchange code for token
    token_url = "https://accounts.spotify.com/api/token"
    
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
        token_data = response.json()
        
        # Create cache file for web app
        cache_data = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_in': token_data['expires_in'],
            'created_at': time.time(),
            'scope': 'user-read-recently-played'
        }
        
        with open('.spotify_cache', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print("✅ Authentication successful!")
        print("💾 Token cached for web app")
        print("🔄 Web app will now show real-time updates")
        print()
        print("🌐 Restart the web app to enable real-time mode:")
        print("   python web_app.py")
        
        return True
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    create_auth_cache()
