#!/usr/bin/env python3
"""
Setup script for Spotify Last Song Fetcher

This script helps you set up your Spotify app credentials.
"""

import os
import webbrowser

def setup_spotify_app():
    """
    Guide user through setting up a Spotify app.
    """
    print("🎵 Spotify App Setup Guide")
    print("=" * 40)
    print()
    
    print("To use this application, you need to create a Spotify app:")
    print()
    print("1. Go to: https://developer.spotify.com/dashboard/")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create an App'")
    print("4. Fill in the app details:")
    print("   - App name: 'Last Song Fetcher' (or any name you prefer)")
    print("   - App description: 'Get my last played song'")
    print("   - Redirect URI: 'http://localhost:8080/callback'")
    print("5. After creating the app, click on it to see your credentials")
    print("6. Copy the 'Client ID' and 'Client Secret'")
    print()
    
    # Ask if user wants to open the dashboard
    open_browser = input("Would you like to open the Spotify Developer Dashboard? (y/n): ").lower().strip()
    if open_browser in ['y', 'yes']:
        webbrowser.open('https://developer.spotify.com/dashboard/')
        print("🌐 Opening Spotify Developer Dashboard in your browser...")
    
    print()
    print("📝 After creating your app, create a .env file with your credentials:")
    print()
    print("Copy the .env.example file to .env and fill in your credentials:")
    print("  cp .env.example .env")
    print()
    print("Then edit the .env file with your actual credentials.")
    print()

def check_env_file():
    """
    Check if .env file exists and has required variables.
    """
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and add your Spotify credentials.")
        return False
    
    # Read .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_client_id_here' in content or 'your_client_secret_here' in content:
        print("⚠️  .env file exists but contains placeholder values.")
        print("Please update .env with your actual Spotify app credentials.")
        return False
    
    print("✅ .env file looks good!")
    return True

def main():
    """
    Main setup function.
    """
    print("🚀 Welcome to Spotify Last Song Fetcher Setup!")
    print()
    
    if check_env_file():
        print("You're all set! Run 'python last_song.py' to get your last played song.")
    else:
        setup_spotify_app()

if __name__ == "__main__":
    main()
