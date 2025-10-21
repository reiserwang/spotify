# spotify_utils.py
import spotipy
from spotipy.exceptions import SpotifyException
import logging

logger = logging.getLogger(__name__)

def get_user_playlists(spotify):
    """Fetches the current user's playlists.

    Args:
        spotify: The authenticated Spotify client.

    Returns:
        A list of playlists or None if an error occurs.
    """
    try:
        results = spotify.current_user_playlists()
        return results
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def search_artists(spotify, keyword, search_type):
    """Searches for artists on Spotify.

    Args:
        spotify: The authenticated Spotify client.
        keyword: The search keyword.
        search_type: The type of search (e.g., 'artist').

    Returns:
        The search results or None if an error occurs.
    """
    try:
        results = spotify.search(q=f"artist:{keyword}", type=search_type, limit=50)
        return results
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_audio_features(spotify, uri):
    """Gets the audio features for a track.

    Args:
        spotify: The authenticated Spotify client.
        uri: The URI of the track.

    Returns:
        The audio features or None if an error occurs.
    """
    try:
        features = spotify.audio_features(uri)
        return features[0] if features else None
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_playlist_items(spotify, playlist_uri):
    """Gets the items in a playlist.

    Args:
        spotify: The authenticated Spotify client.
        playlist_uri: The URI of the playlist.

    Returns:
        The playlist items or None if an error occurs.
    """
    try:
        playlist_items = spotify.playlist_items(
            playlist_uri,
            offset=0,
            fields='items.track.id,items.track.name,total',
            additional_types=['track']
        )
        return playlist_items['items']
    except SpotifyException as e:
        logger.exception(f"Error processing playlist item: {e}")
        return None

def get_current_playing_track(spotify):
    """Gets the currently playing track.

    Args:
        spotify: The authenticated Spotify client.

    Returns:
        The currently playing track or None if an error occurs.
    """
    try:
        track = spotify.current_user_playing_track()
        if track is None or track['item'] is None:
            return None
        return track
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_recommendations(spotify, seed_artists, seed_tracks, limit):
    """Gets track recommendations based on seed artists and tracks.

    Args:
        spotify: The authenticated Spotify client.
        seed_artists: A list of seed artist URIs.
        seed_tracks: A list of seed track URIs.
        limit: The number of recommendations to return.

    Returns:
        The recommendations or None if an error occurs.
    """
    try:
        recommendations = spotify.recommendations(
            seed_artists=seed_artists,
            seed_tracks=seed_tracks,
            limit=limit
        )
        return recommendations
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_current_user(spotify):
    """Gets the current user's profile.

    Args:
        spotify: The authenticated Spotify client.

    Returns:
        The user profile or None if an error occurs.
    """
    try:
        user = spotify.current_user()
        return user
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_top_tracks(spotify, time_range, limit):
    """Gets the current user's top tracks.

    Args:
        spotify: The authenticated Spotify client.
        time_range: The time range ('short_term', 'medium_term', 'long_term').
        limit: The number of tracks to return.

    Returns:
        The top tracks or None if an error occurs.
    """
    try:
        results = spotify.current_user_top_tracks(time_range=time_range, limit=limit)
        return results
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_top_artists(spotify, time_range, limit):
    """Gets the current user's top artists.

    Args:
        spotify: The authenticated Spotify client.
        time_range: The time range ('short_term', 'medium_term', 'long_term').
        limit: The number of artists to return.

    Returns:
        The top artists or None if an error occurs.
    """
    try:
        results = spotify.current_user_top_artists(time_range=time_range, limit=limit)
        return results
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None

def get_recommendation_genre_seeds(spotify):
    """Gets the available genre seeds for recommendations.

    Args:
        spotify: The authenticated Spotify client.

    Returns:
        The genre seeds or None if an error occurs.
    """
    try:
        seed_genres_list = spotify.recommendation_genre_seeds()['genres']
        return seed_genres_list
    except SpotifyException as e:
        logger.exception(f"Spotify API error: {e}")
        return None
