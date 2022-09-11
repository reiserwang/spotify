import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import sys
import pprint
import logging

logging.basicConfig(level=logging.INFO,stream = sys.stdout)


with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]
scope = "user-library-read, user-read-currently-playing"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))



def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None


def show_recommendations_for_artist(artist):
    results = sp.recommendations(seed_artists=[artist['id']])
    for track in results['tracks']:
        logging.info('Recommendation: %s - %s', track['name'],
                    track['artists'][0]['name'])

def main():
    cp = sp.currently_playing()
    if cp is not None:
        logging.info("#41: \n"+json.dumps(cp, indent = 4))

        results = []
        cp_info = {
            'album_uri' : (cp['item']['album']['uri']).replace("spotify:",""),
            'artist_id': (cp['item']['artists'][0]['id']),
            'track_uri' : (cp['item']['uri']).replace("spotify:","")
        }
        logging.info("#49: \n"+ str(cp_info))
        #results.append(sp.search(q= cp_info['album_uri'], type="track", limit = 50))
        #results.append(sp.search(q= cp_info['artist_id'], type="track", limit = 50))
        results.append(sp.recommendations(seed_artists = [cp_info['artist_id']],limit = 50))
        
        #logging.info("#53: \n" + json.dumps(results, indent = 4))
        if not results:
            for i, t in enumerate(results[i]['tracks']):
                if not t:
                    for x, y in enumerate(t[x]):
                        # To-Do: remove redudent items
                        del y['album']['available_markets']                    
                        del y['available_markets']
                        del y['artists']

                        y['feature'] = sp.audio_features[y['uri']]
                        tids.append(t['uri']) #"uri": "spotify:track:7wEql4SrP9nL5U4zxmcrVM"
                        song_list.append(t['name'])        

        logging.info("#68: \n" +json.dumps(results, indent = 4))

    else:
        logging.info("No tracks playing")



if __name__ == '__main__':
    main()