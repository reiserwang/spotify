import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import pprint

with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret, redirect_uri="http://localhost:8888/callback"))

album_name = "Dance Monkey"

results_by_album_name = sp.search(q='album:' + album_name, type='album')
items = results_by_album_name['tracks']['items']['album']
pprint.pprint(items)
"""
if len(items) > 0:
    album = items[0]
    print(album['name'], album['images'][0]['url'])
 """
"""
search_str = 'album: Dance Monkey'
result = sp.search(search_str)
pprint.pprint(result)
"""
