# Personalized Intelligent Music Selection Service

## Description
We aim to create a **personalized intelligent music selection service** that <mark>tailors recommendations based on user preferences, context, and physiological data, using machine learning algorithms</mark> to analyze music features. Users can choose music streams from familiar artists optimized for activities like dancing (with a preferred tempo) or focused work/study. By integrating **physiological and environmental sensors**, the service can synchronize music beats with the user’s heart rate or adjust music intensity to match environmental factors such as lighting or noise levels.

## Architecture and Flow

### Overview
The architecture of this project is designed to leverage Spotify's API for music data and recommendations, integrate user preferences, and optionally incorporate physiological and environmental data for enhanced personalization. Below is a high-level overview of the architecture and flow:

1. **User Authentication**:
   - Users authenticate with Spotify using OAuth 2.0 via the `Spotipy` library.
   - The authentication process generates an access token, enabling secure access to Spotify's API.

2. **Data Retrieval**:
   - The application fetches the user's top artists and tracks across different time ranges (`short_term`, `medium_term`, `long_term`) using Spotify's `current_user_top_artists` and `current_user_top_tracks` endpoints.
   - Audio features (e.g., tempo, danceability, valence) are retrieved for tracks using Spotify's `audio_features` endpoint.

3. **Recommendation Engine**:
   - Based on the user's top artists, the application fetches recommendations using Spotify's `recommendations` endpoint.
   - Recommendations are tailored by seeding the engine with artist IDs, track IDs, or genres.

4. **Data Processing**:
   - The retrieved data is processed and analyzed to match user preferences (e.g., tempo for dancing, valence for mood).
   - Clustering algorithms (e.g., k-means) can be applied to group tracks based on features like tempo and valence.

5. **Visualization and Interaction**:
   - A front-end interface (web-based or integrated into Teams) displays the recommendations.
   - Features include:
     - Interactive scatter plots (e.g., tempo vs. valence) for track selection.
     - Playlists optimized for specific activities (e.g., dancing, studying).
     - Real-time adjustments based on physiological or environmental data (e.g., heart rate, noise levels).

6. **Output**:
   - The final output includes:
     - A playlist of recommended tracks.
     - Visualizations (e.g., scatter plots, music color mapping).
     - Optional HTML reports generated using `PrettyTable`.

### Architecture Diagram
```plaintext
+-------------------+       +-------------------+       +-------------------+
|   User Interface  | <---> |  Recommendation   | <---> |  Spotify API       |
| (Web/Teams/CLI)   |       |     Engine        |       | (Data Retrieval)   |
+-------------------+       +-------------------+       +-------------------+
        ^                           ^                           ^
        |                           |                           |
        |                           |                           |
+-------------------+       +-------------------+       +-------------------+
| Physiological/Env |       |  Data Processing  |       |  Authentication   |
| Sensor Data       |       | (Clustering, etc) |       | (OAuth 2.0)       |
+-------------------+       +-------------------+       +-------------------+
'''

## Objectives (TBD)
- Prototyping Music recommendation and selection service based on Spotify's API, particularly Features APIs that includes [danceability, tempo, energy, and valence](https://www.therecordindustry.io/analyzing-spotify-audio-features), with user text inputs (artist name, scenario or preference) on Azure Web App.
- A front-end (*web or integrated into Teams*) containing web-based player, user search (**by artist, genre, or album name**) and a list (playlist) of songs fitting to users' choice based on features. e.g.:
    - [ ] hign vibes, calm scenario relevant to **valence** in feature api.
    - [ ] playlist for dancing (**danceability**) with similar tempo (**tempo**) or vides (**valence**) through clustering algorithms (e.g. k-means) 
    - [ ]  find next optimal tracks based on currently playing (based on **tempo**, **valence**, **related artists**, **genre**) 
    - [ ] a x-y scatter plot with **tempo** and **valence** so users can choose which song to play from the interactive UI (jJvascript is better for web).
    - [ ] mapping songs with **key** and [Music Color Wheel](https://warrenmars.com/visual_art/theory/colour_wheel/music_colours/music_colours.htm) 
    - [ ] Analysis how a music is differently interpreted by artists (e.g. classical or jazee music) and more interesting data analysis with whatever tools (numpy, Excel, PoewrBI)
    
       *More details <a href="#tldr">TL;DR</a>*

- App development on smartphone and wearable devices (for example: iOS and watch OS)
- Implement own audio feature algorithm on Azure Machine Learning Service and expanding to more [musical tone characteristics](https://en.wikipedia.org/wiki/Musical_tone) such as [key](https://en.wikipedia.org/wiki/Pitch_class) and timbre.
    *Spotify API provides pitch and timbre in web api*
    *For data-lovers, check out the [json file in Teams channel](https://microsoftapc.sharepoint.com/:u:/t/Hack1963/EQ2DT4ZYPJ1CoLfJhECag-QBZZXJ4k23bBqpHp-DX4QBuA?e=xlmpbL) generated by features.py which contains Spotify feature data for* 


    ~~~~
    artist_names=[
        "Ed Sheeran",
        "The Weekend",
        "Justin Bieber",
        "Taylor Swift",
        "Eminem",
        "Adele"
    ]
    ~~~~

## How to use the (nasty) code
Currently Sportify's web-based authenitcation (using cached token, which is stored under **./spotify_caches/<*UUID*>** by default) is used for ID/credential required by API and data permission. In case there are still hard-coded ID/credential codes, change following in **credentials.json.example** and rename it to **credentials.json**

``` json
{
    "SPOTIFY_CLIENT_ID" : "<YOUR_SPOTIFY_CLIENT_ID>",
    "SPOTIFY_CLIENT_SECRET" : "<YOUR_SPOTIFY_CLIENT_SECRET>",
    "SPOTIPY_REDIRECT_URI": "http://localhost:8080"
}
```

## Resources
- [Spotify API](https://developer.spotify.com) 
   (**Note**: Subscription and developer key required)
- Python wrapper: [Spotipy](https://github.com/plamere/spotipy)
- [Spotify audio analysis samples](https://developer.spotify.com/community/showcase/spotify-audio-analysis/)



## Reference
1. [Analyzing Spotify Audio Features](https://www.therecordindustry.io/analyzing-spotify-audio-features/)

<hr>

## <a name="tldr"></a>TL;DR

Here is a sample JSON response from an API search. Analysis of broader samples reveals correlations between certain features, such as "energy" and "loudness," and "tempo" and "valence," while "acousticness" and "energy" show a negative correlation. Music with a tempo of 160 BPM or higher tends to have greater danceability, particularly in Western pop. Different music genres exhibit distinct patterns in scatter plots. A basic Python analysis might look like this:

<table frame="vsides">
    <thead>
        <tr>
            <th>album</th>
            <th>name</th>
            <th>artist</th>
            <th>tempo</th>
            <th>key</th>
            <th>valence</th>
            <th>danceability</th>
            <th>popularity</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><a href="https://open.spotify.com/track/5m1i6hq7dmRlp3c1utE48L"><img src="https://i.scdn.co/image/ab67616d000048512c34b754c9f4fb50c37e6982"></a></td>
            <td><a href="https://open.spotify.com/track/5m1i6hq7dmRlp3c1utE48L">水平線</a></td>
            <td><a href="https://open.spotify.com/artist/6rs1KAoQnFalSqSU4LTh8g">back number</a></td>
            <td>145.867</td>
            <td>10</td>
            <td>0.436</td>
            <td>0.419</td>
            <td>73</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/3f4fc8c8unrQeKecmUPEDR"><img src="https://i.scdn.co/image/ab67616d00004851f8fa082806184fcb032d8e0a"></a></td>
            <td><a href="https://open.spotify.com/track/3f4fc8c8unrQeKecmUPEDR">Warriors</a></td>
            <td><a href="https://open.spotify.com/artist/47mIJdHORyRerp4os813jD">League of Legends</a></td>
            <td>185.121</td>
            <td>1</td>
            <td>0.0412</td>
            <td>0.14</td>
            <td>70</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/29Y7wbrOvQlAwZQJM51ugW"><img src="https://i.scdn.co/image/ab67616d00004851f2a5b943d459d18e68a52801"></a></td>
            <td><a href="https://open.spotify.com/track/29Y7wbrOvQlAwZQJM51ugW">Survivor</a></td>
            <td><a href="https://open.spotify.com/artist/4SGDDnlwi5G42HTGzYl2Fc">2WEI</a></td>
            <td>132.941</td>
            <td>7</td>
            <td>0.0947</td>
            <td>0.348</td>
            <td>68</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/6ts1KCOudfDYXYfyWtq0k1"><img src="https://i.scdn.co/image/ab67616d00004851ac1a5a83790ba13920affe1e"></a></td>
            <td><a href="https://open.spotify.com/track/6ts1KCOudfDYXYfyWtq0k1">おもかげ (produced by Vaundy)</a></td>
            <td><a href="https://open.spotify.com/artist/45ft4DyTCEJfQwTBHXpdhM">milet</a></td>
            <td>207.906</td>
            <td>8</td>
            <td>0.713</td>
            <td>0.488</td>
            <td>66</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/10Eyo4juZQFthKqlJgGMdp"><img src="https://i.scdn.co/image/ab67616d00004851ae51734d04ef431b65a09a9a"></a></td>
            <td><a href="https://open.spotify.com/track/10Eyo4juZQFthKqlJgGMdp">怪盗</a></td>
            <td><a href="https://open.spotify.com/artist/6rs1KAoQnFalSqSU4LTh8g">back number</a></td>
            <td>114.028</td>
            <td>7</td>
            <td>0.8</td>
            <td>0.636</td>
            <td>64</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/3l2O4IuJ4DFEfUwDdWyPnf"><img src="https://i.scdn.co/image/ab67616d000048515083e995f26ad0e8915cf876"></a></td>
            <td><a href="https://open.spotify.com/track/3l2O4IuJ4DFEfUwDdWyPnf">Walkin' In My Lane</a></td>
            <td><a href="https://open.spotify.com/artist/45ft4DyTCEJfQwTBHXpdhM">milet</a></td>
            <td>190.107</td>
            <td>7</td>
            <td>0.342</td>
            <td>0.604</td>
            <td>63</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/2jdbZGFp8KVTuk0YxDNL4l"><img src="https://i.scdn.co/image/ab67616d00004851783ed3c2af46af7ab7c671c0"></a></td>
            <td><a href="https://open.spotify.com/track/2jdbZGFp8KVTuk0YxDNL4l">高嶺の花子さん</a></td>
            <td><a href="https://open.spotify.com/artist/6rs1KAoQnFalSqSU4LTh8g">back number</a></td>
            <td>137.977</td>
            <td>9</td>
            <td>0.343</td>
            <td>0.54</td>
            <td>63</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/4FMz2RFrbDGzJO7K4D0vS3"><img src="https://i.scdn.co/image/ab67616d00004851ce51ffc5c742ed217779cb9d"></a></td>
            <td><a href="https://open.spotify.com/track/4FMz2RFrbDGzJO7K4D0vS3">HAPPY BIRTHDAY</a></td>
            <td><a href="https://open.spotify.com/artist/6rs1KAoQnFalSqSU4LTh8g">back number</a></td>
            <td>145.988</td>
            <td>11</td>
            <td>0.535</td>
            <td>0.482</td>
            <td>62</td>
        </tr>
        <tr>
            <td><a href="https://open.spotify.com/track/2iI556oF2qwtac9r1RzrXo"><img src="https://i.scdn.co/image/ab67616d00004851550c8aec89803c37428579b6"></a></td>
            <td><a href="https://open.spotify.com/track/2iI556oF2qwtac9r1RzrXo">The Call</a></td>
            <td><a href="https://open.spotify.com/artist/47mIJdHORyRerp4os813jD">League of Legends</a></td>
            <td>132.709</td>
            <td>5</td>
            <td>0.115</td>
            <td>0.203</td>
            <td>62</td>
        </tr>
    </tbody>
</table>