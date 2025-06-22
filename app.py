from flask import Flask, render_template, request
import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Load models
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Spotify API credentials
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        return results["tracks"]["items"][0]["album"]["images"][0]["url"]
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []

    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_music_names.append(music.iloc[i[0]].song)
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))

    return recommended_music_names, recommended_music_posters

@app.route("/", methods=["GET", "POST"])
def index():
    songs = music['song'].values
    recommendations = []

    if request.method == "POST":
        selected_song = request.form.get("song")
        recommended_names, recommended_posters = recommend(selected_song)
        recommendations = zip(recommended_names, recommended_posters)

    return render_template("index.html", songs=songs, recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
