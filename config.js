// Spotify API Configuration
// Replace 'YOUR_SPOTIFY_ACCESS_TOKEN' with your actual Spotify access token
// You can get this token from the Spotify Web API Console: https://developer.spotify.com/console/get-recently-played/
// Make sure your token has the 'user-read-recently-played' scope

const SPOTIFY_CONFIG = {
    accessToken: 'YOUR_SPOTIFY_ACCESS_TOKEN',
    apiUrl: 'https://api.spotify.com/v1/me/player/recently-played?limit=1'
};

// Alternative: If you prefer to use environment variables (for deployment)
// You can also create a .env file and use:
// const SPOTIFY_CONFIG = {
//     accessToken: process.env.SPOTIFY_ACCESS_TOKEN || 'YOUR_SPOTIFY_ACCESS_TOKEN',
//     apiUrl: 'https://api.spotify.com/v1/me/player/recently-played?limit=1'
// };