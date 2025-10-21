import os
import sys
from flask import Flask, session, request, redirect, send_from_directory, render_template, make_response
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import logging
import uuid
import pprint
from prettytable import PrettyTable
import html
from collections import Counter
import matplotlib.pyplot as plt
from auth_utils import get_spotify_client, handle_spotify_callback, handle_unauthenticated_user, initialize_session_uuid
from spotify_utils import get_user_playlists, search_artists, get_audio_features, get_playlist_items, get_current_playing_track, get_recommendations, get_current_user, get_top_tracks, get_top_artists, get_recommendation_genre_seeds

# Constants
TOP_ARTISTS_LIMIT = 50
TIME_RANGES = ['short_term', 'medium_term', 'long_term']
RECOMMENDATION_LIMIT = 100

# Logging setup
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__, template_folder='template', static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

# Load credentials
with open("credentials.json", "r") as f:
    credentials = json.load(f)

# Spotify setup
client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
os.environ['SPOTIPY_CLIENT_ID'] = credentials["SPOTIFY_CLIENT_ID"]
os.environ['SPOTIPY_CLIENT_SECRET'] = credentials["SPOTIFY_CLIENT_SECRET"]
os.environ['SPOTIPY_REDIRECT_URI'] = credentials["SPOTIPY_REDIRECT_URI"]

# Folders
caches_folder = './.spotify_caches/'
user_folder = './.user'

if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

# Global variables
seed_genres = []
seed_artists = []
seed_tracks = []

def session_cache_path():
    """Returns the cache path for the current session."""
    try:
        logger.info("session uuid: %s", session.get('uuid'))
    except OSError:
        logger.exception("Error accessing session UUID")
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    """Handles the main index route and Spotify authentication."""
    initialize_session_uuid()

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='user-library-read,user-read-currently-playing,playlist-modify-private,user-read-playback-state,user-modify-playback-state,user-top-read,playlist-read-private',
        cache_handler=cache_handler,
        show_dialog=True
    )

    if request.args.get("code"):
        return handle_spotify_callback(auth_manager, request.args.get("code"))

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return handle_unauthenticated_user(auth_manager)

    spotify_client = spotipy.Spotify(auth_manager=auth_manager)
    current_user = spotify_client.current_user()
    logger.info(current_user)
    
    # Create a welcome page with user info and features
    welcome_content = f"""
    <div class="welcome-section">
        <h1>Welcome back, {current_user['display_name']}!</h1>
        <p>Your intelligent Spotify companion for music discovery and analysis</p>
    </div>
    
    <div class="feature-grid">
        <div class="feature-card">
            <i class="fas fa-search"></i>
            <h3>Smart Search</h3>
            <p>Search for artists and tracks with detailed audio feature analysis</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-list"></i>
            <h3>Playlist Manager</h3>
            <p>View and manage your Spotify playlists with enhanced features</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-play"></i>
            <h3>Now Playing</h3>
            <p>See what's currently playing with audio features and recommendations</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-chart-line"></i>
            <h3>Top Tracks Analysis</h3>
            <p>Analyze your most played tracks with 3D visualizations</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-magic"></i>
            <h3>Smart Recommendations</h3>
            <p>Get personalized music recommendations based on your taste</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-user"></i>
            <h3>Profile Insights</h3>
            <p>View your Spotify profile and listening statistics</p>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-info-circle"></i> Quick Stats</h2>
        <p><strong>Account:</strong> {current_user['display_name']}</p>
        <p><strong>Followers:</strong> {current_user.get('followers', {}).get('total', 'N/A')}</p>
        <p><strong>Country:</strong> {current_user.get('country', 'N/A')}</p>
        <p><strong>Subscription:</strong> {current_user.get('product', 'N/A').title()}</p>
    </div>
    """
    
    return render_template('base.html', output=welcome_content)

@app.route('/search', methods=['GET', 'POST'])
def search():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    keyword = request.form.get('keyword')
    search_type = request.form.get('type')

    results = search_artists(spotify, keyword, search_type)
    if results is None:
        return "Error searching for artists", 500

    search_results_in_items = []
    for item in results['artists']['items']:
        try:
            item["feature"] = get_audio_features(spotify, item['uri'])
            if item["feature"] and item["feature"]['analysis_url'] is not None:
                ana_url = item["feature"]['analysis_url']
                item["feature"]["analyis"] = spotify._get(ana_url)
        except (TypeError, spotipy.exceptions.SpotifyException) as e:
            logger.exception(f"Error processing item: {e}")

        search_results_in_items.append(item)

    logger.info(search_results_in_items)

    pt_top = PrettyTable()
    pt_top.format = True
    pt_top.field_names = ['Image', 'Name', 'Genres', 'Popularity']

    for item in search_results_in_items:
        pt_top.add_row([
            f"<a href='{item['external_urls']['spotify']}'><img src='{item['images'][1]['url']}'></a>",
            f"<a href='{item['external_urls']['spotify']}'>{item['name']}</a>",
            item['genres'],
            item['popularity']
        ])

    if not search_results_in_items:
        no_results_html = '''
        <div class="message">
            <i class="fas fa-search"></i> No results found for your search. Try different keywords or search type.
        </div>
        '''
        return make_response(render_template('search.html', output=no_results_html), 200, {'Content-Type': 'text/html'})
    
    html_text = pt_top.get_html_string(sortby="Popularity", reversesort=True, format=True, attributes={"id": "results"})
    logger.info(html_text)
    return make_response(render_template('search.html', output=html.unescape(html_text)), 200, {'Content-Type': 'text/html'})

@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError:
        logger.exception("Error removing session cache")
    session.pop("token_info", None)
    return redirect('/')

@app.route('/player')
def player():
    return render_template('player.html')

@app.route('/playlists')
def playlists():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    results = get_user_playlists(spotify)
    if results is None:
        return "Error getting playlists", 500

    html_string = '\ufeff'
    pt_top = PrettyTable()
    pt_top.field_names = ['no', 'playlist cover', 'name', 'uri', 'features']

    for i, item in enumerate(results['items']):
        playlist_items = get_playlist_items(spotify, item['uri'])
        if playlist_items is None:
            continue
        item['tracks'] = playlist_items
        pt_top.add_row([
            i,
            f"<a href='{item['external_urls']['spotify']}'><img src='{item['images'][0]['url']}' width='100' ></a>",
            f"<a href='{item['external_urls']['spotify']}'>{item['name']}</a>",
            item['uri'],
            [x['track']['name'] for x in item['tracks']]
        ])

    html_string += f'''
    <div class="welcome-section">
        <h1><i class="fas fa-list"></i> My Playlists</h1>
        <p>Explore your Spotify playlists with enhanced track information</p>
    </div>
    <h2><i class="fas fa-music"></i> Your Playlists</h2>
    {pt_top.get_html_string(sortby='no', reversesort=False, format=True, attributes={'id': 'results'})}
    '''
    return make_response(render_template('base.html', output=html.unescape(html_string)), 200, {'Content-Type': 'text/html'})

@app.route('/current_playing')
def current_playing():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    track = get_current_playing_track(spotify)
    if track is None:
        return "No track currently playing."

    track['item']["feature"] = get_audio_features(spotify, track['item']['uri'])
    if track['item']["feature"] is None:
        return "Error getting audio features", 500

    current_track = {
        'name': track['item']['name'],
        'url': track['item']['external_urls']['spotify'],
        'album_name': track['item']['album']['name'],
        'album_image': track['item']['album']['images'][0]['url'],
        'album_url': track['item']['album']['external_urls']['spotify'],
        'artist_name': track['item']['artists'][0]['name'],
        'artist_url': track['item']['artists'][0]['external_urls']['spotify'],
        'feature': track['item']['feature']
    }

    current_track['recommendations'] = get_recommendations(spotify, [track['item']['artists'][0]['uri']], [current_track['url']], 20)
    if current_track['recommendations'] is None:
        return "Error getting recommendations", 500

    logger.info(json.dumps(current_track['feature'], indent=4))

    pt_top = PrettyTable()
    pt_top.field_names = ['cover', 'track name', 'album name', 'artist', 'tempo', 'danceability', 'valence', 'feature']
    pt_top.add_row([
        f"<a href='{current_track['album_url']}'><img src='{current_track['album_image']}' width='100' ></a>",
        f"<a href='{current_track['url']}'>{current_track['name']}</a>",
        f"<a href='{current_track['album_url']}'>{current_track['album_name']}</a>",
        f"<a href='{current_track['artist_url']}'>{current_track['artist_name']}</a>",
        current_track['feature']['tempo'],
        current_track['feature']['danceability'],
        current_track['feature']['valence'],
        current_track['feature']
    ])

    html_string = '''
    <div class="welcome-section">
        <h1><i class="fas fa-music"></i> Currently Playing</h1>
        <p>Track analysis and personalized recommendations</p>
    </div>
    ''' + pt_top.get_html_string(format=True) + '<h2><i class="fas fa-magic"></i> Recommended Tracks</h2>'

    pt_recommend = PrettyTable()
    pt_recommend.field_names = ['album', 'name', 'artist', 'tempo', 'danceability', 'valence', 'feature']
    track_uris = [rec['uri'] for rec in current_track['recommendations']['tracks']]
    features = spotify.audio_features(track_uris)
    for i, rec in enumerate(current_track['recommendations']['tracks']):
        rec['feature'] = features[i]
        seed_tracks.append(rec['uri'].replace("spotify:track:", ""))
        del (rec['album']['available_markets'])
        pt_recommend.add_row([
            f"<a href='{rec['album']['external_urls']['spotify']}'><img src='{rec['album']['images'][1]['url']}' width='100' ></a>",
            f"<a href='{rec['external_urls']['spotify']}'>{rec['name']}</a>",
            f"<a href='{rec['artists'][0]['external_urls']['spotify']}'>{rec['artists'][0]['name']}</a>",
            rec['feature']['tempo'],
            rec['feature']['danceability'],
            rec['feature']['valence'],
            rec['feature']
        ])

    html_string += pt_recommend.get_html_string(format=True, sortby="valence", reversesort=False, attributes={"id": "results"})
    return make_response(render_template('base.html', output=html.unescape(html_string)), 200, {'Content-Type': 'text/html'})

@app.route('/current_user')
def current_user():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    user = get_current_user(spotify)
    if user is None:
        return "Error getting user profile", 500

    html_string = '\ufeff' + f"<a href='{user['external_urls']['spotify']}'> <img src='{user['images'][0]['url']}'/>{user['display_name']}</a>"
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('base.html', output=html_string), 200, headers)

@app.route('/my_top')
def my_top():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    html_string = '\ufeff'
    tempo = []
    valence = []
    danceability = []
    track_name = []

    results = get_top_tracks(spotify, 'short_term', 50)
    if results is None:
        return "Error getting top tracks", 500

    for item in results['items']:
        del (item['album']['available_markets'])
        del (item['available_markets'])
        item['feature'] = get_audio_features(spotify, item['uri'])
        if item['feature'] is None:
            return "Error getting audio features", 500
        tempo.append(item['feature']['danceability'])
        valence.append(item['feature']['valence'])
        danceability.append(item['feature']['danceability'])
        track_name.append(item['name'])

    fig = plt.figure(figsize=(16, 9))
    ax = plt.axes(projection="3d")
    my_cmap = plt.get_cmap('hsv')

    sctt = ax.scatter3D(valence, tempo, danceability,
                        alpha=0.5,
                        cmap=my_cmap,
                        c=danceability,
                        marker='^',
                        label=track_name
                        )
    plt.title("User's Recent Top Tracks")
    ax.set_xlabel('Valence', fontweight='bold')
    ax.set_ylabel('Tempo', fontweight='bold')
    ax.set_zlabel('Danceability', fontweight='bold')
    fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=5)
    plt.show()

    genres_list = []
    genres_dict = {}
    fav_artists = []
    artist = {}
    pt_top = PrettyTable()
    pt_top.field_names = ['no', 'cover', 'name', 'genres', 'uri']
    pt_top.title = "Most Played Artist"

    for sp_range in TIME_RANGES:
        results = get_top_artists(spotify, sp_range, TOP_ARTISTS_LIMIT)
        if results is None:
            return "Error getting top artists", 500
        pt_top.add_row([sp_range, "", "", "", ""])

        for i, item in enumerate(results['items']):
            pt_top.add_row([
                i + 1,
                f"<a href='{item['external_urls']['spotify']}'><img src='{item['images'][2]['url']}' width='100' ></a>",
                f"<a href='{item['external_urls']['spotify']}'>{item['name']}</a>",
                item['genres'],
                item['uri']
            ])
            artist['term'] = sp_range
            artist['rank'] = i
            artist['name'] = item['name']
            artist['uri'] = item['uri']
            artist['genres'] = item['genres']
            fav_artists.append(artist)
            artist = {}
            for genre in item['genres']:
                genres_list.append(genre)

    html_string += pt_top.get_html_string(format=True, attributes={"id": "results"})
    html_string += "</div>"

    top_10 = {}
    genres_dict = dict(zip(list(genres_list), [list(genres_list).count(i) for i in list(genres_list)]))
    top_10 = Counter(genres_dict).most_common(10)
    logger.info(top_10)
    seed_artists = fav_artists

    logging.info(top_10)

    pt_summary = PrettyTable()
    genre_key = []
    genre_value = []
    pt_summary.field_names = ['Genre', 'Count']
    for (k, v) in top_10:
        pt_summary.add_row([k, v])
        genre_key.append(k)
        seed_genres.append(k)
        genre_value.append(v)

    fig1, ax1 = plt.subplots()
    ax1.pie(genre_value, labels=genre_key, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.savefig('./static/top_genres.png')

    html_string += "<br/><h2> Your Most Played Genres </h2>"
    html_string += pt_summary.get_html_string(format=True, attributes={"id": "results"})
    html_string += "<img src='./static/top_genres.png'/>"

    return make_response(render_template('base.html', output=html.unescape(html_string)))

@app.route('/recommended')
def recommended():
    spotify = get_spotify_client(session_cache_path())
    if spotify is None:
        return redirect('/')

    pt_top = PrettyTable()
    html_string = '\ufeff'

    for sp_range in TIME_RANGES:
        results = get_top_artists(spotify, sp_range, 5)
        if results is None:
            return "Error getting top artists", 500
        for item in results['items']:
            seed_artists.append(item['uri'].replace("spotify:artist:", ""))
    logger.info(seed_artists)

    seed_genres_list = get_recommendation_genre_seeds(spotify)
    if seed_genres_list is None:
        return "Error getting genre seeds", 500
    logger.info("seed_genres = " + str(seed_genres_list))
    logger.info("seed_artists = " + str(seed_artists))
    logger.info("seed_tracks = " + str(seed_tracks))

    results = get_recommendations(spotify, seed_artists, seed_tracks, RECOMMENDATION_LIMIT)
    if results is None:
        return "Error getting recommendations", 500
    logger.info(results)

    for track in results['tracks']:
        pt_top.add_row([track['name'], track['artists'][0]['name']])
    output = pt_top.get_html_string()
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('base.html', output=output), 200, headers)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(threaded=True, port=8080, debug=True)
