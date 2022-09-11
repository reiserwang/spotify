import spotipy

from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import json 
import logging
import pprint

import time
import sys


with open("credentials.json", "r") as f:
    credentials = json.load(f)


if credentials:
    client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
    client_id = credentials["SPOTIFY_CLIENT_ID"]
    client_secret = credentials["SPOTIFY_CLIENT_SECRET"]
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



if spotify:
    birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    print("=== Search URI: ", birdy_uri,"===")
    results_by_uri = spotify.artist_albums(birdy_uri, album_type='album')
    albums = results_by_uri['items']
    while results_by_uri['next']:
        results_by_uri = spotify.next(results)
        albums.extend(results['items'])
    for album in albums:
        print(album['name'])
    
    artist_name = "Alice Sara Ott"
    print("=== Search artist name: ", artist_name,"===")
    results_by_artist_name = spotify.search(q='artist:' + artist_name, type='artist')
    items = results_by_artist_name['artists']['items']
    if len(items) > 0:
        artist = items[0]
        print(artist['name'], artist['images'][0]['url'])
    search_str = 'Alice Sara Ott'
    result = spotify.search(search_str)
    pprint.pprint(result)

    scope = 'user-top-read'
    ranges = ['short_term', 'medium_term', 'long_term']

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

    for sp_range in ['short_term', 'medium_term', 'long_term']:
        print("range:", sp_range)

        results = sp.current_user_top_artists(time_range=sp_range, limit=50)

        for i, item in enumerate(results['items']):
            print(i, item['name'])
        print()

    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

    playlists = sp.user_playlists("reiser")
    for playlist in playlists['items']:
        print(playlist['name'])



    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])



    artist_name="alice sara ott"
    results = sp.search(q=artist_name, limit=50)
    tids = []
    for i, t in enumerate(results['tracks']['items']):
        print(' ', i, t['name'])
        tids.append(t['uri'])

    start = time.time()
    features = sp.audio_features(tids)
    delta = time.time() - start
    for feature in features:
        print(json.dumps(feature, indent=4))
        print()
        analysis = sp._get(feature['analysis_url'])
        print(json.dumps(analysis, indent=4))
        print()
    print("features retrieved in %.2f seconds" % (delta,))
