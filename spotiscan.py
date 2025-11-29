import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time

CLIENT_ID = "dc005f00915b432f9337ca49a3f7ec71"
CLIENT_SECRET = "1f8016fc15d04a708da6a01ffe750761"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = "user-library-read playlist-modify-private playlist-modify-public"


def get_liked_tracks(sp):
    liked = []
    results = sp.current_user_saved_tracks(limit=50)

    while True:
        liked.extend([item["track"]["id"] for item in results["items"]])

        if results["next"]:
            results = sp.next(results)
        else:
            break

    return liked


def batch_track_info(sp, track_ids):
    all_tracks = []

    for i in range(0, len(track_ids), 50):
        chunk = track_ids[i:i+50]
        response = sp.tracks(chunk)["tracks"]

        for t in response:
            if t: 
                artists = ", ".join(a["name"] for a in t["artists"])
                all_tracks.append({
                    "name": t["name"],
                    "artists": artists,
                })

    return all_tracks


def main():
    print("Authenticating with Spotify...")

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )
    )

    print("Authentication successful.\n")

    print("Fetching liked tracks (this may take a while)...")
    liked_tracks = get_liked_tracks(sp)
    print(f"Found {len(liked_tracks)} liked tracks.")
    
    time.sleep(1)

    print("Fetching track info (batched requests)...")
    tracks_info = batch_track_info(sp, liked_tracks)

    with open("liked_tracks.json", "w", encoding="utf-8") as f:
        json.dump(tracks_info, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Wrote {len(tracks_info)} tracks to liked_tracks.json")

    return tracks_info


if __name__ == "__main__":
    main()
