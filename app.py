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

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

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
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                                cache_handler=cache_handler, 
                                               show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_cached_token()
        return redirect('/')

    # Step 3. Signed in, display data
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'
    
    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    current_user = spotify.current_user()
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
    output = json.dumps(spotify.current_user_playlists())
    return render_template('base.html', output = output) 


@app.route('/current_playing')
def current_playing():


    scope = "user-read-playback-state,user-modify-playback-state"

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    res=sp.devices()
    pprint.pprint(res)
    track = spotify.current_user_playing_track()
    if not track is None:
        return render_template('base.html', output = track)
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


    scope = "user-top-read"
    html_string ='\ufeff'
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results =  spotify.current_user_top_artists(time_range='short_term', limit=50)
    #return render_template('base.html', output = json.dumps(results)) 


    # User Top Artists and Tracks
    ranges = ['short_term', 'medium_term', 'long_term']

    for sp_range in ['short_term', 'medium_term', 'long_term']:
        html_string += f'<h2>{sp_range}</h2>'
        pt_top=PrettyTable()
        pt_top.field_names=['no','name','url','genres','album cover','uri']
        results = spotify.current_user_top_artists(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            pt_top.add_row([i, item['name'], item['external_urls']['spotify'],item['genres'],item['images'][0]['url'],item['uri']])

        html_string += pt_top.get_html_string(sortby="no",reversesort = False, format = True, attributes={"id":"results"})

    return render_template('base.html', output = html.unescape(html_string))


@app.route('/recommended_artists') 
def recommended_artists(): 
    scope = "user-top-read,user-library-read"
    pt_top=PrettyTable()
    #pt_top.field_names=['no','name','url','genres','album cover','uri']
    html_string =""
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    ref_artists = []
    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_artists(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            ref_artists.append(item['name'])
    ref_artists = list(set(ref_artists))

    for artist in ref_artists:
        results = sp.search(q='artist:' + artist, type='artist')
        items = results['artists']['items']
        logger.debug("artists = ",items)
        if len(items) > 0:
            artist_id = items[0]['id']
            logger.debug("artist_id = ", artist_id)
            results = sp.recommendations(seed_artists=[artist_id])
            logger.debug("recommendatons =")
            for track in results['tracks']:
                pt_top.add_row(track['name'],track['artists'][0]['name'])

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