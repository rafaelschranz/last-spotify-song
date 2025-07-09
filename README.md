# Last Spotify Song

A minimal web app that displays the last song you played on your Spotify account using the Spotify Web API.

![App Screenshot](https://github.com/user-attachments/assets/09a29072-1bd9-426f-b4e2-2674fbd890f6)

## Features

- 🎵 Displays your most recently played Spotify track
- 🎨 Clean, card-style design with Spotify branding
- 📱 Responsive design that works on mobile and desktop
- 🔄 Manual refresh button to fetch the latest song
- ⚡ Loading spinner with smooth animations
- 🚨 Comprehensive error handling
- 📅 Smart timestamp formatting ("5 minutes ago", "1 hour ago", etc.)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/rafaelschranz/last-spotify-song.git
   cd last-spotify-song
   ```

2. **Get your Spotify Access Token**
   - Go to the [Spotify Web API Console](https://developer.spotify.com/console/get-recently-played/)
   - Click "Get Token" and make sure `user-read-recently-played` scope is selected
   - Copy the generated access token

3. **Configure your token**
   - Open `config.js`
   - Replace `YOUR_SPOTIFY_ACCESS_TOKEN` with your actual token:
   ```javascript
   const SPOTIFY_CONFIG = {
       accessToken: 'your_actual_token_here',
       apiUrl: 'https://api.spotify.com/v1/me/player/recently-played?limit=1'
   };
   ```

4. **Run the app**
   ```bash
   # Using Python (recommended)
   python -m http.server 8000
   
   # Or using Node.js
   npx http-server
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8000`
   - Click "Refresh" to fetch your last played song

## What It Shows

The app displays:
- 🎵 **Song title**
- 👨‍🎤 **Artist name(s)**
- 💿 **Album title**
- 🖼️ **Album cover image**
- ⏰ **Timestamp** (formatted as "X minutes ago")

## Deployment

### Vercel
1. Push your code to GitHub
2. Connect your repository to [Vercel](https://vercel.com)
3. Deploy with default settings

### Netlify
1. Push your code to GitHub
2. Connect your repository to [Netlify](https://netlify.com)
3. Deploy with default settings

### Environment Variables (for deployment)
For production deployment, you can use environment variables instead of hardcoding the token:

1. Create a `.env` file (not committed to git):
   ```
   SPOTIFY_ACCESS_TOKEN=your_actual_token_here
   ```

2. Update `config.js` to use environment variables (you'll need a build process for this in a static site)

## Error Handling

The app handles various error scenarios:
- ❌ **Missing token**: Shows configuration message
- 🔒 **Invalid/expired token**: Clear error message
- 🚫 **No recent songs**: Prompts to play a song first
- 🔄 **Rate limiting**: Asks to try again later
- 🌐 **Network errors**: Generic error handling

## Technical Details

- **Pure HTML/CSS/JavaScript** - No frameworks or build process needed
- **Spotify Web API** - Uses the `/me/player/recently-played` endpoint
- **Responsive design** - Works on all screen sizes
- **Modern CSS** - Uses flexbox, CSS Grid, and animations
- **Fetch API** - Modern JavaScript for API calls

## Token Security

⚠️ **Important**: Your Spotify access token is sensitive information. 

- Never commit tokens to git (they're in `.gitignore`)
- Tokens expire after 1 hour and need to be refreshed
- For production use, implement proper OAuth flow instead of hardcoded tokens

## Browser Support

- Chrome/Edge 60+
- Firefox 55+
- Safari 12+
- Mobile browsers

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details
