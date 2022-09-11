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

type = ['album','track','artist','genre']
"""
https://developer.spotify.com/documentation/web-api/reference/#/operations/search
"""
def spsearch(name, type):
    if type == "artist":
        results = sp.search(q='artist:' + name, type='artist',limit = 50)
        items = results['artists']['items']
        return items

    if type == "track":
        results = sp.search(q='track:'+name, type='track', limit = 50)
        items = results['tracks']['items']
        """
        for a in results['tracks']["items"]:
        image = a["album"]["images"][1]["url"]
        """
        return items
    if type == "album":
        results = sp.search(q='album:'+name, type='album', limit = 50)
        items = results['albums']['items']
        return items





test_artist = spsearch("Alice Sara Ott", "artist")
test_track = spsearch("chopin fantaisie","track")
test_album = spsearch("Ghibli","album")

print(json.dumps(test_artist, indent=4).encode('utf8'))
print()
print(json.dumps(test_track, indent=4).encode('utf8'))
print()
print(json.dumps(test_album, indent=4).encode('utf8'))

"""
pprint.pprint(test_artist)
pprint.pprint(test_track)
pprint.pprint(test_album)
"""