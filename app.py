import os
import sys
from flask import Flask, session, request, redirect, send_from_directory, render_template, make_response
from flask_session import Session

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import logging
import uuid

import pprint
from prettytable import PrettyTable
import html

from collections import Counter
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    #filename='app.log', 
    #filemode='a',
    stream = sys.stdout,
    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


app = Flask(__name__, template_folder = 'template')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
os.environ['SPOTIPY_CLIENT_ID'] = credentials["SPOTIFY_CLIENT_ID"]
os.environ['SPOTIPY_CLIENT_SECRET'] = credentials["SPOTIFY_CLIENT_SECRET"]
os.environ['SPOTIPY_REDIRECT_URI'] = credentials["SPOTIPY_REDIRECT_URI"]
caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    try:
        logger.info("session uuid:", session.get('uuid'))
    except OSError:
        logger.exception()
    return caches_folder + session.get('uuid')



@app.route('/')
def index():

    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read,user-read-currently-playing,playlist-modify-private,user-read-playback-state,user-modify-playback-state',
                                            cache_handler=cache_handler, 
                                            show_dialog=True)
    #spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

    """
    https://community.spotify.com/t5/Spotify-for-Developers/Authorization-Code-Flow-don-t-want-to-cache-tokens/td-p/4989228
    """
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_cached_token()
        token_info = auth_manager.get_access_token(request.args.get('code'), as_dict = True, check_cache=False)
        logger.info(token_info)
        return redirect('/')

    # Step 3. Signed in, display data
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        logger.info(auth_url)
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'
    
    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    current_user = spotify.current_user()
    logger.info(current_user)
    output = "You're signed in." + current_user['display_name']
    return render_template('base.html', output = output)




@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError:
        logger.exception()
    session.pop("token_info", None)
    return redirect('/')

@app.route('/player')
def player():
    return render_template('player.html')

@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # Debug
    results = json.dumps(spotify.current_user_playlists(), ensure_ascii=False, indent=4)
    with open('playlist.json', 'w', encoding='utf-8') as f:    
        pprint.pprint(spotify.current_user_playlists(), f) 
    #

    results = spotify.current_user_playlists()

    html_string ='\ufeff'+"<html><head><meta charset='UTF-8'></head>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js'></script>" \
+"<script>$(document).ready(function() {$('#results').tablesorter();});</script>"
    pt_top=PrettyTable()
    pt_top.field_names=['no','playlist cover','name','uri']

    for i, item in enumerate(results['items']):    
        # add_row() takes a list of values as an argument.  

        pt_top.add_row([
            i,
            "<a href='"+item['external_urls']['spotify']+"'>"+"<img src='"+item['images'][0]['url']+"' width='100' ></a>",
            "<a href='"+item['external_urls']['spotify']+"'>"+item['name']+"</a>",
            item['uri']
            ])
    html_string += pt_top.get_html_string(sortby="no",reversesort = False, format = True, attributes={"id":"results"})
    
    return make_response(render_template('base.html', output = html.unescape(html_string)),200, {'Content-Type':'text/html'})


@app.route('/current_playing')
def current_playing():


    scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')
    #spotify = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    
    html_string ='\ufeff'+"<html><head><meta charset='UTF-8'></head>"  \
            +"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>"  \
            +"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js'></script>" \
            +"<script>$(document).ready(function() {$('#results').tablesorter();});</script>"
    
 

        
    track = spotify.current_user_playing_track()
    if track is not None:
        track['item']["feature"] = spotify.audio_features(track['item']['uri'])[0]
        current_track = {}
        current_track['name'] = track['item']['name']
        current_track['url'] = track['item']['external_urls']['spotify']
        current_track['album_name'] = track['item']['album']['name']
        current_track['album_image'] = track['item']['album']['images'][0]['url']
        current_track['album_url'] = track['item']['album']['external_urls']['spotify']
        current_track['artist_name'] = track['item']['artists'][0]['name']
        current_track['artist_url'] = track['item']['artists'][0]['external_urls']['spotify']
        current_track['feature'] = track['item']['feature']
        """
        #debug
        """
        with open('current_playing.json', 'w', encoding='utf-8') as f:    
            pprint.pprint(track, f) 




        pt_top=PrettyTable()
        pt_top.field_names=['cover','track name', 'album name','artist','feature']
                
        pt_top.add_row([
                
                "<a href='"+current_track['album_url']+"'>"+"<img src='"+current_track['album_image']+"' width='100' ></a>",
                "<a href='"+current_track['url']+"'>"+current_track['name']+"</a>",
                "<a href='"+current_track['album_url']+"'>"+current_track['album_name']+"</a>",
                "<a href='"+current_track['artist_url']+"'>"+current_track['artist_name']+"</a>",
                current_track['feature']
            ])




        html_string += pt_top.get_html_string(format = True, attributes={"id":"results"})
        return make_response(render_template('base.html', output = html.unescape(html_string)),200, {'Content-Type':'text/html'})
       
    return f"No track currently playing."




@app.route('/current_user')
def current_user():

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user = spotify.current_user()    
    html_string = '\ufeff'+"<a href='"+user['external_urls']['spotify']+"'> <img src='"+user['images'][0]['url']+"'/>" + user['display_name'] + "</a>"
    
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('base.html', output = html_string),200, headers)
    #https://stackoverflow.com/questions/19315567/returning-rendered-template-with-flask-restful-shows-html-in-browser
    """Sometimes it is necessary to set additional headers in a view. 
    Because views do not have to return response objects but can return a value that is converted into a response object by Flask itself, 
    it becomes tricky to add headers to it. This function can be called instead of using a return and you will get a response object which 
    you can use to attach headers."""

@app.route('/my_top')
def my_top():
    
    """
    # Find my top artists and tracks in ranges = ['short_term', 'medium_term', 'long_term']

    """
    scope = "user-top-read"
    html_string ='\ufeff'+"<html><head><meta charset='UTF-8'></head>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js'></script>" \
+"<script>$(document).ready(function() {$('#results').tablesorter();});</script>"
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))


    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    # User Top Artists and Tracks
    ranges = ['short_term', 'medium_term', 'long_term']
    genres_list = []
    genres_dict = {}
    for sp_range in ['short_term', 'medium_term', 'long_term']:
        html_string += f'<h2>{sp_range}</h2>'
        pt_top=PrettyTable()
        pt_top.field_names=['no','cover','name','genres','uri']
        results = spotify.current_user_top_artists(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            #pt_top.add_row([i, item['name'], item['external_urls']['spotify'],item['genres'],item['images'][2]['url'],item['uri']])
            pt_top.add_row([
                i,
                "<a href='"+item['external_urls']['spotify']+"'>"+"<img src='"+item['images'][2]['url']+"' width='100' ></a>",
                "<a href='"+item['external_urls']['spotify']+"'>"+item['name']+"</a>",
                item['genres'],
                item['uri']
            ])
            for genre in item['genres']:
                genres_list.append(genre)        
        
        


        html_string += pt_top.get_html_string(sortby="no",reversesort = False, format = True, attributes={"id":"results"})

    top_10={}
    genres_dict = dict(zip(list(genres_list),[list(genres_list).count(i) for i in list(genres_list)]))
    # Python3: In Python 2.x - .items() returned a list of (key, value) pairs. 
    # In Python 3.x, .items() is now an itemview object. So, list(dict.items()) is required for what was dict.items() in Python 2.x.
    # top_10 = sorted(genres_dict,key = lambda x: x[1][:10])

    top_10 = (Counter(genres_dict)).most_common(10)

    logging.info(top_10)
    pt_summary=PrettyTable()
    pt_summary.field_names=['Genre','Count']
    for (k,v) in top_10:
        pt_summary.add_row([k,v])

    html_string += "<br/><h2> Your Most Played Genres </h2>"
    html_string += pt_summary.get_html_string(format = True, attributes={"id":"results"})

    #https://stackoverflow.com/questions/19315567/returning-rendered-template-with-flask-restful-shows-html-in-browser
    return make_response(render_template('base.html', output = html.unescape(html_string)))


@app.route('/recommended') 
def recommended(): 

    """"
    # Discover new artists - Retrive Sportify's recommended tracks beased on my top artists sp_range in ['short_term', 'medium_term', 'long_term']
    # Find similar tracks based on currently playing (valence, tempo, danceability)
    """
    #scope = "user-top-read,user-library-read"
    pt_top=PrettyTable()
    #pt_top.field_names=['no','name','url','genres','album cover','uri']
    html_string ='\ufeff'+"<html><head><meta charset='UTF-8'></head>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js'></script>" \
+"<script>$(document).ready(function() {$('#results').tablesorter();});</script>"
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

    #sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    sp = spotipy.Spotify(auth_manager=auth_manager)
    ref_artists = []

    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_artists(time_range=sp_range, limit=5)
        print(results)
        for i, item in enumerate(results['items']):
            ref_artists.append(item['uri'])
    #ref_artists = list(set(ref_artists))
    print(ref_artists)

    for artist in ref_artists:
        results = sp.search(q=artist, type='artist')
        items = results['artists']['items']
        """
        #debug
        """
        with open('recommend.json', 'w', encoding='utf-8') as f:   
            print(ref_artists, file = f) 
            pprint.pprint(results, f) 

        if len(items) > 0:
            artist_id = items[0]['id']
            logger.debug("artist_id = ", artist_id)
            results = sp.recommendations(seed_artists=[artist_id])
            logger.debug("recommendatons =")
            for track in results['tracks']:
                pt_top.add_row(track['name'],track['artists'][0]['name'])
    output = ""
    output += pt_top.get_html_string()
    #return f'{html_string}'
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('base.html', output = output), 200, headers )



@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    #app.run(threaded=True, port=int(SPOTIPY_REDIRECT_URI.split(":")[-1]))
    app.run(threaded=True, port=8080, debug=True)