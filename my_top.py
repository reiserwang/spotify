import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import pprint
from prettytable import PrettyTable
from collections import Counter



with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]

scope = 'user-top-read'

# User Top Artists and Tracks
ranges = ['short_term', 'medium_term', 'long_term']

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

print("# User Top Artists and Tracks #")
genres = []
uri_collection = []
for sp_range in ['short_term', 'medium_term', 'long_term']:
    print("range:", sp_range)
    pt_top=PrettyTable()
    pt_top.field_names=['no','name','url','genres','album cover','uri']
    results = sp.current_user_top_artists(time_range=sp_range, limit=50)
    for i, item in enumerate(results['items']):
        pt_top.add_row([i, item['name'], item['external_urls']['spotify'],item['genres'],item['images'][0]['url'],item['uri']])
        print(i, item['name'], item['external_urls']['spotify'],item['genres'],item['images'][0]['url'],item['uri'])
        uri_collection.append(item['uri'])
        for genre in item['genres']:
            genres.append(genre)
    print(pt_top.get_html_string())
    pt_count=PrettyTable()
    pt_count.field_names=Counter(genres).keys()
    pt_count.add_row(Counter(genres).values())
    print(pt_count.get_html_string())
    #print(Counter(genres).keys())
    #print(Counter(genres).values())
  
"""
'items': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/67J1KP70RqsL6uAIXkscKE'},
            'followers': {'href': None, 'total': 63052},
            'genres': ['bgm'],
            'href': 'https://api.spotify.com/v1/artists/67J1KP70RqsL6uAIXkscKE',
            'id': '67J1KP70RqsL6uAIXkscKE',
            'images': [{'height': 640,
                        'url': 'https://i.scdn.co/image/ab6761610000e5eb7b84b6f688f1d59a8e7b18b5',
                        'width': 640},
                       {'height': 320,
                        'url': 'https://i.scdn.co/image/ab676161000051747b84b6f688f1d59a8e7b18b5',
                        'width': 320},
                       {'height': 160,
                        'url': 'https://i.scdn.co/image/ab6761610000f1787b84b6f688f1d59a8e7b18b5',
                        'width': 160}],
            'name': 'MUJI BGM',
            'popularity': 42,
            'type': 'artist',
            'uri': 'spotify:artist:67J1KP70RqsL6uAIXkscKE'},
    """


    #pprint.pprint(results_artists)
"""
    results_tracks = sp.current_user_top_tracks(time_range=sp_range, limit=50)
    for i, item in enumerate(results_tracks['items']):
        print(i, item['name'], '//', item['artists'][0]['name'])
    print()
    pprint.pprint(results_tracks)

"""