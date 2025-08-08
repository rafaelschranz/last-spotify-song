# Spotify Last Song Fetcher

A Python application to fetch your last played song from Spotify using the Spotify Web API.

## Features

- 🎵 Get your last played song from Spotify
- 📊 Display detailed song information (artist, album, duration, popularity)
- 💾 Save song data to JSON file
- 🔐 Secure OAuth 2.0 authentication
- 🎨 Beautiful console output

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - **App name**: "Last Song Fetcher" (or any name you prefer)
   - **App description**: "Get my last played song"
   - **Redirect URI**: `http://localhost:8080/callback`
5. After creating the app, copy your **Client ID** and **Client Secret**

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Spotify app credentials
# SPOTIPY_CLIENT_ID=your_actual_client_id
# SPOTIPY_CLIENT_SECRET=your_actual_client_secret
```

### 4. Setup Helper (Optional)

Run the setup script for guided configuration:

```bash
python setup.py
```

## Usage

### Get Last Played Song

```bash
python last_song.py
```

On first run, you'll be redirected to Spotify to authorize the application. After authorization, the app will display your last played song information.

### Example Output

```
🎵 Last Played Song on Spotify
========================================
🎶 Song: Bohemian Rhapsody
👨‍🎤 Artist: Queen
💿 Album: A Night at the Opera
⏰ Played at: 2025-07-14 15:30:45
⏱️  Duration: 5:55
📈 Popularity: 87/100
🔗 Spotify URL: https://open.spotify.com/track/...
🎧 Preview: https://p.scdn.co/mp3-preview/...

💾 Song info saved to 'last_song.json'
```

## Files

- `last_song.py` - Main application script
- `setup.py` - Setup helper script
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `last_song.json` - Output file with song data (created after running)

## API Reference

This application uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api) with the following endpoint:

- **Recently Played Tracks**: `GET /v1/me/player/recently-played`
- **Required Scope**: `user-read-recently-played`

## Troubleshooting

### Authentication Issues

1. Make sure your `.env` file has the correct credentials
2. Verify the redirect URI in your Spotify app matches `http://localhost:8080/callback`
3. Check that your Spotify app has the correct scopes enabled

### No Recent Tracks

- Make sure you've played music on Spotify recently
- The API only returns tracks played in the last 50 items or within the last 24 hours

### Rate Limiting

The Spotify API has rate limits. If you hit them, wait a moment before trying again.

## License

This project is open source and available under the MIT License.
