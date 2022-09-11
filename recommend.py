import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import sys
import pprint
import logging
import os
import pprint
from prettytable import PrettyTable

logger = logging.getLogger(__name__)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]



scope = "user-top-read,user-library-read"
pt_top=PrettyTable()
#pt_top.field_names=['no','name','url','genres','album cover','uri']
html_string =""

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))
ref_artists = []
for sp_range in ['short_term', 'medium_term', 'long_term']:
    results = sp.current_user_top_artists(time_range=sp_range, limit=50)
    for i, item in enumerate(results['items']):
        ref_artists.append(item['name'])
ref_artists = list(set(ref_artists))

for artist in ref_artists:
    results = sp.search(q='artist:' + artist, type='artist')
    items = results['artists']['items']
    print("artists = ",items)


    if len(items) > 0:
        artist_id = items[0]['id']
        print("artist_id = ", artist_id)
        results = sp.recommendations(seed_artists=[artist_id])
        print("recommendatons =",results)
        for track in results['tracks']:
            print(track['name'],track['artists'][0]['name'])

    html_string += pt_top.get_html_string()
    print(html_string)