#!/usr/bin/env python3
"""
Create fresh Spotify token from authorization code
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

# Extract the code from the URL you provided
auth_code = "AQDUczYlWIfQsT6m1hHu8XAljpyDOrhMckmCceJ-uxzMt4VrEfs5sichX5qkXEreS--wg_jyP92wL9T3vEBHLMtoxDvf-YRTdIWnTUwL0kaSph2kqbvvV4V5st1c8ZK6nhtdqgeYBgA3VN7-ErgDmRVHw9bYuCCFvdYO591uDwRC10IVDrZW6cFm2LFCyMqW_O_9nOnrbhV2969sDEUjowFY8La7Y4OF-O6wtetiAgP3dsOfeTwlOegk1OF7ostrhq2m"

def exchange_code_for_token():
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
        token_data = response.json()
        
        # Create cache file
        cache_data = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_in': token_data['expires_in'],
            'created_at': time.time(),
            'scope': 'user-read-recently-played'
        }
        
        with open('.spotify_cache', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print("✅ Fresh token created!")
        print("💾 Token saved to .spotify_cache")
        return True
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    exchange_code_for_token()
