from types import NoneType
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import sys
import pprint
import logging
from prettytable import PrettyTable
from prettytable import MSWORD_FRIENDLY
#from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import html


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


with open("credentials.json", "r") as f:
    credentials = json.load(f)

client_credentials_manager = SpotifyClientCredentials(credentials["SPOTIFY_CLIENT_ID"], credentials["SPOTIFY_CLIENT_SECRET"])
client_id = credentials["SPOTIFY_CLIENT_ID"]
client_secret = credentials["SPOTIFY_CLIENT_SECRET"]
scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret= client_secret,scope=scope, redirect_uri="http://localhost:8888/callback"))

tids = []
song_list = []



artist_names=[
    "Ed Sheeran",
    "The Weekend",
    "Justin Bieber",
    "Taylor Swift",
    "Eminem",
    "Adele"

]

results=[]
search_results_in_items= []

x=[]
y=[]
z=[]
label=[]
for artist in artist_names:
    results=sp.search(q=artist, limit=50)

    #print(json.dumps(results,ensure_ascii=False, indent=4))
    #logging.info(json.dumps(results, indent=4))
   

    for i, t in enumerate(results['tracks']['items']):

        if t['uri']  in tids:
            assert("spotify:track:" in t['uri'])
            next

        # To-Do: remove redudent items
        del t['album']['available_markets']
        del t['album']['external_urls']
        del t['available_markets']
        del t['artists']
        tids.append(t['uri'])
        song_list.append(t['name'])
        

        t["feature"] = sp.audio_features(t['uri'])[0]
        
        """
        # pitch and timbre from analyis.

        try:
            if t["feature"]['analysis_url'] is not None:
                ana_url = t["feature"]['analysis_url']
                if sp._get(ana_url) is not None:
                    t["feature"]["analyis"] = sp._get(ana_url)
        except TypeError as e:
            #logging.exception(e)
            pass
         
        """
        search_results_in_items.append(t)
        try:
            # Interested to plot a 3D scatter plot based on danceability, tempo, and valence.
            z.append(t["feature"]["danceability"])
            x.append(t["feature"]["valence"])
            y.append(t["feature"]["tempo"])
            label.append(t["name"]) 
        except TypeError:
            pass
    
    logging.info(tids,song_list)
# Creating figure
# For printing Chinese characters: https://hoishing.medium.com/using-chinese-characters-in-matplotlib-5c49dbb6a2f7
matplotlib.rcParams['font.family'] = ['Heiti TC']

fig = plt.figure(figsize = (16, 9))
ax = plt.axes(projection ="3d")
my_cmap = plt.get_cmap('hsv')



# Creating plot
sctt = ax.scatter3D(x, y, z,
                alpha = 0.5,   
                cmap = my_cmap,
                c = z,
                marker ='^',
                label = label
                )
plt.title(artist_names)
ax.set_xlabel('Valence', fontweight ='bold')
ax.set_ylabel('Tempo', fontweight ='bold')
ax.set_zlabel('Danceability', fontweight ='bold')
fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)

# show plot
plt.show()
#plt.savefig('features.png')





#https://stackoverflow.com/questions/18337407/saving-utf-8-texts-with-json-dumps-as-utf-8-not-as-a-u-escape-sequence
# https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/


# Save search reuslts locally

json.dumps(search_results_in_items,ensure_ascii=False, indent = 4)
with open('features.json', 'w', encoding='utf-8') as f:    
    f.write(json.dumps(search_results_in_items,ensure_ascii=False, indent = 4))


"""
with open('features.json', encoding="utf8") as json_file:
    search_results_in_items = json.load(json_file)
    #logging.info(type(search_results_in_items)) #list
"""


pt_top=PrettyTable()
pt_top.format = True
pt_top.set_style(MSWORD_FRIENDLY)
"""
search_results_in_items.sort(key = lambda x: x['popularity'], reverse = True)
print("Most Popular:") 
for i in range(1):
    print(
    
    search_results_in_items[i]['popularity'],
    search_results_in_items[i]['album']['name'], 
    search_results_in_items[i]['name'],
    search_results_in_items[i]['external_urls']['spotify'],
    
    )

"""

# logging.info("len(search_results_in_items): " + str(len(search_results_in_items)))

"""
pt_top.field_names=['name','artist','tempo','key','valence','danceability','popularity','link']
try:
    for i in range(len(search_results_in_items)):
        pt_top.add_row([search_results_in_items[i]['name'], 
                    search_results_in_items[i]['album']['artists'][0]['name'],
                    search_results_in_items[i]['feature']['tempo'],
                    search_results_in_items[i]['feature']['key'],
                    search_results_in_items[i]['feature']['valence'],
                    search_results_in_items[i]['feature']['danceability'],
                    search_results_in_items[i]['popularity'],
                    "<a href='"+search_results_in_items[i]['external_urls']['spotify']] + "'>" + "<img src='"+search_results_in_items[i]['album']['images'][0]['url']+"' />"+"</a>"
        )

        logging.info(search_results_in_items[i]['external_urls']['spotify'] + search_results_in_items[i]['album']['images'][1]['url'])
"""

pt_top.field_names=['album','name','artist','tempo','key','valence','danceability','popularity']
try:
    for i in range(len(search_results_in_items)):
        
        pt_top.add_row(["<a href='"+search_results_in_items[i]['external_urls']['spotify']+"'>"+"<img src='"+search_results_in_items[i]['album']['images'][2]['url']+"'></a>",
                    "<a href='"+search_results_in_items[i]['external_urls']['spotify']+"'>"+search_results_in_items[i]['name']+"</a>",
                    "<a href='"+search_results_in_items[i]['album']['artists'][0]['external_urls']['spotify']+"'>"+search_results_in_items[i]['album']['artists'][0]['name']+"</a>",
                    search_results_in_items[i]['feature']['tempo'],
                    search_results_in_items[i]['feature']['key'],
                    search_results_in_items[i]['feature']['valence'],
                    search_results_in_items[i]['feature']['danceability'],
                    search_results_in_items[i]['popularity']]
                    )

        #logging.info(search_results_in_items[i]['external_urls']['spotify'] + search_results_in_items[i]['album']['images'][1]['url'])
except TypeError:
        pass
"""
encode().decode('utf-8)

> import sys; print(sys.getdefaultencoding())'
utf-8
# Good read!!
# https://medium.com/@kk_huang/python-%E8%BC%B8%E5%87%BA%E4%B8%AD%E6%96%87%E4%BA%82%E7%A2%BC%E5%95%8F%E9%A1%8C-c4a540b8401d
"""
html_text = '\ufeff'+"<html><head><meta charset='UTF-8'></head>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js'></script>"  \
+"<script type='text/javascript' src='http://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.9.1/jquery.tablesorter.min.js'></script>" \
+"<script>$(document).ready(function() {$('#results').tablesorter();});</script>"  \
+html.unescape(pt_top.get_html_string(sortby="popularity",reversesort = True, format = True, attributes={"id":"results"}))+"</html>"
print(html_text.encode('utf-8').decode(sys.stdout.encoding))


# https://note.nkmk.me/en/python-dict-list-sort/


#for item in search_results_in_items:

# str in python 2.x, byte in python 3.x
# https://blog.csdn.net/kz_java/article/details/115288359
# https://stackoverflow.com/questions/13837848/converting-byte-string-in-unicode-string
# https://stackoverflow.com/questions/49315872/how-to-convert-string-containing-unicode-escape-u-to-utf-8-string

# for unicode issues:
#print("Best song for dance:", song_list[danceability.index(max(danceability))].encode().decode('utf-8'))



