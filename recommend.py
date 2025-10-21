import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import logging
from prettytable import PrettyTable

# Configure logging
logger = logging.getLogger(__name__)

# Load credentials
with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]

# Spotify authentication
scope = "user-top-read,user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri="http://localhost:8888/callback"))

# Initialize PrettyTable
pt_top = PrettyTable()

# Fetch user's top artists across different time ranges
ref_artists = set()
for sp_range in ['short_term', 'medium_term', 'long_term']:
    results = sp.current_user_top_artists(time_range=sp_range, limit=50)
    ref_artists.update(item['name'] for item in results['items'])

# Fetch recommendations for each artist
html_string = ""
for artist in ref_artists:
    search_results = sp.search(q=f'artist:{artist}', type='artist')
    items = search_results['artists']['items']

    if items:
        artist_id = items[0]['id']
        recommendations = sp.recommendations(seed_artists=[artist_id])

        for track in recommendations['tracks']:
            print(f"Track: {track['name']} | Artist: {track['artists'][0]['name']}")

    # Generate HTML string from PrettyTable (if needed)
    html_string += pt_top.get_html_string()

# Print the final HTML string
print(html_string)