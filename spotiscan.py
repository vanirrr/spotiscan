import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "dc005f00915b432f9337ca49a3f7ec71"
CLIENT_SECRET = "1f8016fc15d04a708da6a01ffe750761"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

PLAYLIST_ID = "12JXbjx3Wc9h2NnWTaW06z"

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

def get_playlist_tracks(sp, playlist_id):

    # returning shit already in the playlist gg wp

    tracks = []
    results = sp.playlist_items(playlist_id, fields="items(track(id)),next")
    while results:
        for item in results["items"]:
            if item["track"]:
                tracks.append(item["track"]["id"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

    print("Fetching liked songs...")
    liked_tracks = set(get_liked_tracks(sp))

    print("Fetching existing playlist tracks...")
    playlist_tracks = set(get_playlist_tracks(sp, PLAYLIST_ID))

    to_add = list(liked_tracks - playlist_tracks)

    if not to_add:
        print("No new liked songs to add!")
        return

    CHUNK_SIZE = 100

    print(f"Adding {len(to_add)} songs to playlist...")

    for i in range(0, len(to_add), CHUNK_SIZE):
        chunk = to_add[i:i + CHUNK_SIZE]
        sp.playlist_add_items(PLAYLIST_ID, chunk)

    print("✔ Done! Playlist updated.")

if __name__ == "__main__":
    main()


