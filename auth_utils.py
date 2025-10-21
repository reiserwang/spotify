# auth_utils.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from flask import session, redirect
import uuid

logger = logging.getLogger(__name__)

def create_spotify_oauth(cache_handler, scope, show_dialog=True):
    """Creates and returns a SpotifyOAuth object."""
    return SpotifyOAuth(
        scope=scope,
        cache_handler=cache_handler,
        show_dialog=show_dialog
    )

def handle_spotify_callback(auth_manager, code):
    """Handles the callback from Spotify's authorization page."""
    token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)
    logger.info(token_info)
    return redirect('/')

def handle_unauthenticated_user(auth_manager):
    """Handles users who are not yet authenticated."""
    auth_url = auth_manager.get_authorize_url()
    logger.info(auth_url)
    return f'<h2><a href="{auth_url}">Sign in</a></h2>'

def get_spotify_client(session_cache_path, scope='user-library-read,user-read-currently-playing,playlist-modify-private,user-read-playback-state,user-modify-playback-state,user-top-read,playlist-read-private', show_dialog=True):
    """Gets or creates a Spotify client for the current session."""
    if 'spotify_client' not in session:
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = create_spotify_oauth(cache_handler, scope, show_dialog)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return None  # Or redirect to login
        session['spotify_client'] = spotipy.Spotify(auth_manager=auth_manager)
    return session['spotify_client']

def initialize_session_uuid():
    """Initializes the session UUID if it doesn't exist."""
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
    logger.info("UUID: " + session.get('uuid'))
