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

import matplotlib.pyplot as plt

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    #filename='app.log', 
    #filemode='a',
    stream = sys.stdout,
    format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


app = Flask(__name__, template_folder = 'template', static_url_path = '/static')
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
user_folder = './.user'

seed_genres = []
seed_artists =[]
seed_tracks = []

if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

sportify_client = spotipy.client.Spotify()

def session_cache_path():
    try:
        logger.info("session uuid:", session.get('uuid'))
    except OSError:
        logger.exception()
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    """
    # Get Session and create auth_manager (get cached token or authorize url
    """
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    logger.info("UUID: "+session.get('uuid'))
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read,user-read-currently-playing,playlist-modify-private,user-read-playback-state,user-modify-playback-state,user-top-read,playlist-read-private',
                                            cache_handler=cache_handler, 
                                            show_dialog=True)
    # spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8080/callback"))

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
    sportify_client = spotipy.Spotify(auth_manager=auth_manager)

    logger.info(type(sportify_client))

    current_user = sportify_client.current_user()
    logger.info(current_user)
    output = "You're signed in." + current_user['display_name']
    return render_template('base.html', output = output)


@app.route('/search', methods =['GET','POST'])
def search():

    keyword = request.form.get('keyword')
    type = request.form.get('type')
    #logger.info("###"+keyword+ type)


    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)


    results=spotify.search(q = "artist:"+ keyword, type=type, limit=50)

    with open('search_results.json', 'w', encoding='utf-8') as f:    
        f.write(json.dumps(results,ensure_ascii=False, indent = 4))

    logger.info(results)


    search_results_in_items = []

    for i, t in enumerate(results['artists']['items']):

        

        t["feature"] = spotify.audio_features(t['uri'])[0]
        
        
        # pitch and timbre from analyis.

        try:
            if t["feature"]['analysis_url'] is not None:
                ana_url = t["feature"]['analysis_url']
                if spotify._get(ana_url) is not None:
                    t["feature"]["analyis"] = sp._get(ana_url)
        except TypeError as e:
            #logging.exception(e)
            pass
         
        
        search_results_in_items.append(t)       

    logger.info(search_results_in_items)
    with open('search_results.json', 'w', encoding='utf-8') as f:    
        f.write(json.dumps(search_results_in_items,ensure_ascii=False, indent = 4))

    pt_top=PrettyTable()
    pt_top.format = True
    # pt_top.set_style(MSWORD_FRIENDLY)
    
    pt_top.field_names=['Image','Name', 'Genres', 'Popularity']

    logger.info(len(search_results_in_items))
    for i in range(len(search_results_in_items)):            
        pt_top.add_row(["<a href='"+search_results_in_items[i]['external_urls']['spotify']+"'>"+"<img src='"+search_results_in_items[i]['images'][1]['url']+"'></a>",
                    "<a href='"+search_results_in_items[i]['external_urls']['spotify']+"'>"+search_results_in_items[i]['name']+"</a>",
                    search_results_in_items[i]['genres'],
                    search_results_in_items[i]['popularity']
                    ])

        #logging.info(search_results_in_items[i]['external_urls']['spotify'] + search_results_in_items[i]['album']['images'][1]['url'])


    html_text = '\ufeff'+html.unescape(pt_top.get_html_string(sortby="Popularity",reversesort = True, format = True, attributes={"id":"results"}))+"</html>"
    
    
    logger.info(html_text)
    return make_response(render_template('search.html', output = html.unescape(html_text)),200, {'Content-Type':'text/html'})


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

    html_string ='\ufeff'
    pt_top=PrettyTable()
    pt_top.field_names=['no','playlist cover','name','uri','features']
    playlist_items = {}
    valence =[]
    tempo =[]
    danceability =[]
    track_name =[]
    for i, item in enumerate(results['items']):    
        # add_row() takes a list of values as an argument.  
        playlist_items = spotify.playlist_items(
            item['uri'],
            offset =0,
            fields='items.track.id,items.track.name,total',
            additional_types=['track']
        ) 
        item['tracks'] = playlist_items['items'] 
        """
        for t, track in enumerate(item['tracks']):
            # spotify.audio_features(track['item']['uri'])[0]
            # logger.info(track['track']['id'])
            track['track']['feature'] = spotify.audio_features(track['track']['id'])[0]
            tempo.append(track['track']['feature']['tempo'] )
            valence.append(track['track']['feature']['valence'] )
            danceability.append(track['track']['feature']['danceability'] )
            track_name.append(track['track']['name'])
        """
        #logger.info(playlist_items)  

        """
        fig = plt.figure(figsize = (6, 6))
        ax = plt.axes(projection ="3d")
        my_cmap = plt.get_cmap('hsv')



        # Creating plot
        sctt = ax.scatter3D(valence, tempo, danceability,
                        alpha = 0.5,   
                        cmap = my_cmap,
                        c = danceability,
                        marker ='^',
                        label = track_name
                        )
        plt.title("Features of tracks in playlist "+item['name'])
        ax.set_xlabel('Valence', fontweight ='bold')
        ax.set_ylabel('Tempo', fontweight ='bold')
        ax.set_zlabel('Danceability', fontweight ='bold')
        fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)

        # show plot
        # plt.show()
        plt.savefig('./static/'+item['uri'].replace("spotify:playlist:","")+'.png')
        """
        pt_top.add_row([
            i,
            "<a href='"+item['external_urls']['spotify']+"'>"+"<img src='"+item['images'][0]['url']+"' width='100' ></a>",
            "<a href='"+item['external_urls']['spotify']+"'>"+item['name']+"</a>",
            item['uri'],
            #filter(lambda x: x["name"],item['tracks'])
            list(x['track']['name'] for x in item['tracks'])
            #item['tracks']
            #"<img src='"+"./static/"+item['uri']+".png"+"'/>"
            ])
        #logger.info("<img src='"+"./static/"+item['uri'].replace("spotify:playlist:","")+".png"+"'/>")
    html_string += ("<h2>Public Playlist</h2><br/>"+pt_top.get_html_string(sortby="no",reversesort = False, format = True, attributes={"id":"results"}))
   
    
    
    


    return make_response(render_template('base.html', output = html.unescape(html_string)),200, {'Content-Type':'text/html'})


@app.route('/current_playing')
def current_playing():


    scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing, user-top-read"

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')
    #spotify = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    
    html_string ='\ufeff'
    
 

        
    track = spotify.current_user_playing_track()
    logger.info("******"+json.dumps(track, indent=4))

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
    
    
    logger.info(seed_genres)
    current_track['recommendations'] = spotify.recommendations(seed_artists = [track['item']['artists'][0]['uri']], seed_tracks=[current_track['url']],limit = 20)


    """
    #debug
    """

    logger.info(json.dumps(current_track['feature'], indent =4))
    with open('.user/current_playing.json', 'w', encoding='utf-8') as f:    
        json.dump(current_track, f, indent=4) 




    pt_top=PrettyTable()
    pt_top.field_names=['cover','track name', 'album name','artist','tempo','danceability','valence','feature', ]
            
    pt_top.add_row([
            
            "<a href='"+current_track['album_url']+"'>"+"<img src='"+current_track['album_image']+"' width='100' ></a>",
            "<a href='"+current_track['url']+"'>"+current_track['name']+"</a>",
            "<a href='"+current_track['album_url']+"'>"+current_track['album_name']+"</a>",
            "<a href='"+current_track['artist_url']+"'>"+current_track['artist_name']+"</a>",
            current_track['feature']['tempo'],
            current_track['feature']['danceability'],
            current_track['feature']['valence'],
            current_track['feature']
        ])



    html_string += pt_top.get_html_string(format = True)
    html_string +='<h2>Recommendations</h2>'

    """
    # To-Do - add recommendation code 


    """


    pt_recommend = PrettyTable()
    pt_recommend.field_names=['album','name','artist','tempo','danceability','valence','feature']
    for i, rec in enumerate(current_track['recommendations']['tracks']):
        
        if spotify.audio_features(rec['uri'])[0] is not None:
            rec['feature'] = spotify.audio_features(rec['uri'])[0]
        
        seed_tracks.append(rec['uri'].replace("spotify:track:",""))
        del(rec['album']['available_markets'])
        
        logger.info(len(rec))
        logger.info(rec)
        pt_recommend.add_row([
            "<a href='"+rec['album']['external_urls']['spotify']+"'>"+"<img src='"+rec['album']['images'][1]['url']+"' width='100' ></a>",
            "<a href='"+rec['external_urls']['spotify']+"'>"+rec['name']+"</a>",
            "<a href='"+rec['artists'][0]['external_urls']['spotify']+"'>"+rec['artists'][0]['name']+"</a>",
            rec['feature']['tempo'],
            rec['feature']['danceability'],
            rec['feature']['valence'],
            rec['feature']
        ])

    html_string += pt_recommend.get_html_string(format = True, sortby="valence",reversesort = False, attributes={"id":"results"})
   
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
    html_string ='\ufeff'
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

    
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')


    # Recent Top Tracks

    ranges = ['short_term']
    tempo = []
    valence = []
    danceability = []
    track_name = []
    for sp_range in ranges:
        results = spotify.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            del(item['album']['available_markets'])
            del(item['available_markets'])
            item['feature'] = spotify.audio_features(item['uri'])[0]
            tempo.append(item['feature']['danceability'])
            valence.append(item['feature']['valence'])
            danceability.append(item['feature']['danceability'])
            track_name.append(item['name'])
    with open('./.user/top_tracks.json', 'w', encoding='utf-8') as f:  
        json.dump(results, f, indent = 4)

    fig = plt.figure(figsize = (16, 9))
    ax = plt.axes(projection ="3d")
    my_cmap = plt.get_cmap('hsv')



    # Creating plot
    sctt = ax.scatter3D(valence, tempo, danceability,
                    alpha = 0.5,   
                    cmap = my_cmap,
                    c = danceability,
                    marker ='^',
                    label = track_name
                    )
    plt.title("User's Recent Top Tracks")
    ax.set_xlabel('Valence', fontweight ='bold')
    ax.set_ylabel('Tempo', fontweight ='bold')
    ax.set_zlabel('Danceability', fontweight ='bold')
    fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)

    # show plot
    plt.show()

    # User Top Artists and Tracks
    ranges = ['short_term', 'medium_term', 'long_term']
    genres_list = []
    genres_dict = {}
    fav_artists = []
    artist= {}
    pt_top=PrettyTable()
    pt_top.field_names=['no','cover','name','genres','uri']
    pt_top.title = "Most Played Artist"
    #html_string += f'<h2>{sp_range}</h2><div class="collapsible_section>'

    for sp_range in ['short_term', 'medium_term', 'long_term']:
        #https://www.w3schools.com/howto/howto_js_collapsible.asp
        #html_string += f'<button type="button" class="collapsible"><h2>{sp_range}</h2></button><div class="collapsible_section>"'
        results = spotify.current_user_top_artists(time_range=sp_range, limit=50)
        pt_top.add_row([sp_range,"","","",""])
        
        for i, item in enumerate(results['items']):
            #pt_top.add_row([i, item['name'], item['external_urls']['spotify'],item['genres'],item['images'][2]['url'],item['uri']])
            pt_top.add_row([
                i+1,
                "<a href='"+item['external_urls']['spotify']+"'>"+"<img src='"+item['images'][2]['url']+"' width='100' ></a>",
                "<a href='"+item['external_urls']['spotify']+"'>"+item['name']+"</a>",
                item['genres'],
                item['uri']
            ])
            artist['term'] = sp_range
            artist['rank'] = i
            artist['name'] = item['name']
            artist['uri'] = item['uri']
            artist['genres']=item['genres']
            fav_artists.append(artist)
            artist={}
            for genre in item['genres']:
                genres_list.append(genre)        
        
        


        #html_string += pt_top.get_html_string(sortby="no",reversesort = False, format = True, attributes={"id":"results"})
    html_string += pt_top.get_html_string(format = True, attributes={"id":"results"})
    html_string += "</div>"

    top_10={}
    genres_dict = dict(zip(list(genres_list),[list(genres_list).count(i) for i in list(genres_list)]))
    # Python3: In Python 2.x - .items() returned a list of (key, value) pairs. 
    # In Python 3.x, .items() is now an itemview object. So, list(dict.items()) is required for what was dict.items() in Python 2.x.
    # top_10 = sorted(genres_dict,key = lambda x: x[1][:10])

    top_10 = Counter(genres_dict).most_common(10)
    logger.info(top_10)
    seed_artists = fav_artists

    with open('./.user/fav_artists.json', 'w', encoding='utf-8') as f:   
            json.dump(fav_artists, f, indent=4) 

    logging.info(top_10)
    with open('./.user/top_genres.json', 'w', encoding='utf-8') as f:   
            json.dump(genres_dict, f, indent=4) 


    pt_summary=PrettyTable()
    genre_key=[]
    genre_value=[]
    pt_summary.field_names=['Genre','Count']
    for (k,v) in top_10:
        pt_summary.add_row([k,v])
        genre_key.append(k)
        seed_genres.append(k)
        genre_value.append(v)
        

    """
    Plotting
    """

    fig1, ax1 = plt.subplots()
    ax1.pie(genre_value, labels=genre_key, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.savefig('./static/top_genres.png')

    html_string += "<br/><h2> Your Most Played Genres </h2>"
    html_string += pt_summary.get_html_string(format = True, attributes={"id":"results"})
    html_string += "<img src='./static/top_genres.png'/>"

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
    html_string ='\ufeff'
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.debug("False: auth_manager.validate_token(cache_handler.get_cached_token()")
        return redirect('/')

   
    sp = spotipy.Spotify(auth_manager=auth_manager)


    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_artists(time_range=sp_range, limit=5)
        # logger.info(results)
        for i, item in enumerate(results['items']):
            seed_artists.append(item['uri'].replace("spotify:artist:",""))
    logger.info(seed_artists)

    

    
    seed_genres = sp.recommendation_genre_seeds()['genres']
    logger.info("seed_genres = " + str(seed_genres))
    logger.info("seed_artists = " + str(seed_artists))
    logger.info("seed_tracks = " +  str(seed_tracks))
   
    results = sp.recommendations(seed_tracks= seed_tracks, seed_genres=seed_genres, seed_artists=seed_artists, limit = 100)
    logger.info(results)
    with open('./.user/recommend.json', 'w', encoding='utf-8') as f:  
        json.dump(results, f, indent = 4)
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