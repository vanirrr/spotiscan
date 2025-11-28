import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "dc005f00915b432f9337ca49a3f7ec71"
CLIENT_SECRET = "1f8016fc15d04a708da6a01ffe750761"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = "user-library-read playlist-modify-private playlist-modify-public"

def get_liked_tracks(sp):

    # get track ids from liked shit

    liked = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results["items"]:
            liked.append(item["track"]["id"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return liked



