# 🎵 Spotify Smart Player

A modern, intelligent Spotify companion for music discovery and analysis with a beautiful web interface.

## ✨ Features

- **🔍 Smart Search**: Search artists and tracks with detailed audio feature analysis
- **📊 Audio Analytics**: Visualize tempo, danceability, valence, and other audio features
- **🎯 Personalized Recommendations**: Get smart suggestions based on your listening history
- **📱 Modern UI**: Responsive, Spotify-inspired design that works on all devices
- **📈 Top Tracks Analysis**: 3D visualizations of your most played music
- **🎮 Web Player**: Control Spotify playback directly from the browser
- **📋 Playlist Management**: Enhanced playlist viewing with track features
- **🎨 Visual Analytics**: Interactive charts and music color mapping

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Spotify Developer Account
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <your-repo-url>
cd spotify-smart-player

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync --all-extras

# Set up credentials (see Configuration section)
cp credentials.json.example credentials.json
# Edit credentials.json with your Spotify API keys

# Run the application
python app.py
```

### Alternative Installation with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## ⚙️ Configuration

### Spotify API Setup

1. **Create a Spotify App**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create an App"
   - Fill in the app name and description
   - Note your `Client ID` and `Client Secret`

2. **Configure Redirect URI**:
   - In your Spotify app settings, add `http://localhost:8080` as a redirect URI

3. **Set up credentials**:
   ```bash
   cp credentials.json.example credentials.json
   ```
   
   Edit `credentials.json`:
   ```json
   {
       "SPOTIFY_CLIENT_ID": "your_client_id_here",
       "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
       "SPOTIPY_REDIRECT_URI": "http://localhost:8080"
   }
   ```

## 🎯 Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8080`

3. **Authenticate** with your Spotify account when prompted

4. **Explore the features**:
   - **Home**: Overview of your account and quick access to features
   - **Search**: Find artists and tracks with audio feature analysis
   - **Playlists**: View your Spotify playlists with enhanced information
   - **Now Playing**: See current track with recommendations
   - **Top Tracks**: Analyze your listening habits with 3D visualizations
   - **Discover**: Get personalized recommendations
   - **Profile**: View your Spotify profile information

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │◄──►│  Flask Backend  │◄──►│  Spotify API    │
│   (Modern UI)   │    │  (Python)       │    │  (OAuth 2.0)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Responsive    │    │  Audio Feature  │    │  User Data &    │
│   Design        │    │  Analysis       │    │  Recommendations│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **Authentication Layer**: Secure OAuth 2.0 flow with Spotify
2. **Data Processing**: Audio feature analysis and recommendation engine
3. **Visualization**: 3D plots, charts, and interactive elements
4. **Modern UI**: Responsive design with glassmorphism effects
5. **Caching**: Efficient session and token management

## 🛠️ Development

### Project Structure
```
spotify-smart-player/
├── app.py                 # Main Flask application
├── auth_utils.py          # Authentication utilities
├── spotify_utils.py       # Spotify API utilities
├── template/              # HTML templates
│   ├── base.html         # Base template with modern styling
│   ├── search.html       # Search interface
│   ├── player.html       # Web player
│   └── home.html         # Home page
├── static/               # Static assets
├── pyproject.toml        # Project configuration
├── requirements.txt      # Pip requirements
└── credentials.json      # Spotify API credentials (not in repo)
```

### Development Setup

```bash
# Install development dependencies
uv sync --all-extras

# Run with development mode
python app.py

# Code formatting
black .

# Type checking
mypy .

# Run tests
pytest
```

### Available Commands with uv

```bash
# Package management
uv add package-name          # Add new dependency
uv remove package-name       # Remove dependency
uv sync                      # Sync dependencies
uv pip list                  # List installed packages

# Development tools
uv run black .               # Format code
uv run pytest               # Run tests
uv run mypy .               # Type checking
```

## 📊 Audio Features Explained

The application analyzes various Spotify audio features:

- **Danceability** (0.0-1.0): How suitable a track is for dancing
- **Energy** (0.0-1.0): Perceptual measure of intensity and power
- **Valence** (0.0-1.0): Musical positiveness (happy vs sad)
- **Tempo** (BPM): Overall estimated tempo
- **Acousticness** (0.0-1.0): Confidence measure of acoustic content
- **Instrumentalness** (0.0-1.0): Predicts whether a track contains vocals
- **Liveness** (0.0-1.0): Detects presence of audience in recording
- **Speechiness** (0.0-1.0): Detects presence of spoken words

## 🎨 UI Features

### Modern Design Elements
- **Glassmorphism**: Translucent cards with backdrop blur
- **Gradient Backgrounds**: Spotify-inspired color schemes
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects and smooth transitions
- **Dark Theme**: Easy on the eyes for extended use

### Accessibility
- High contrast ratios for readability
- Keyboard navigation support
- Screen reader friendly markup
- Responsive font sizing

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Check your Spotify API credentials
   - Ensure redirect URI matches exactly
   - Verify your Spotify app is not in development mode restrictions

2. **Import Errors**:
   - Make sure virtual environment is activated
   - Run `uv sync` to install dependencies
   - Check Python version (3.10+ required)

3. **Port Already in Use**:
   - Change the port in `app.py`: `app.run(port=8081)`
   - Update redirect URI in Spotify app settings

4. **No Audio Features**:
   - Some tracks may not have audio features available
   - Try with popular, mainstream tracks

### Getting Help

- Check the [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api/)
- Review [Spotipy Documentation](https://spotipy.readthedocs.io/)
- Open an issue in this repository

## 📈 Performance

- **Fast Package Management**: uv provides 10-100x faster dependency resolution
- **Efficient Caching**: Session and token caching for better performance
- **Optimized Queries**: Batch API requests where possible
- **Responsive UI**: Smooth interactions with modern CSS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Format code: `black .`
5. Run type checking: `mypy .`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for music data
- [Spotipy](https://github.com/plamere/spotipy) for Python Spotify integration
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [uv](https://github.com/astral-sh/uv) for fast Python package management

## 📚 Resources

- [Spotify API Documentation](https://developer.spotify.com/documentation/)
- [Audio Features Guide](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)
- [Spotipy Examples](https://github.com/plamere/spotipy/tree/master/examples)
- [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/)

---

**Made with ❤️ for music lovers and data enthusiasts**