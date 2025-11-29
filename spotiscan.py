import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import time
import os
from google import genai

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SCOPE = "user-library-read playlist-modify-private playlist-modify-public playlist-read-private"

def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id, fields="items.track.id,next", additional_types=["track"], limit=100)

    while True:
        for item in results.get("items", []):
            track = item.get("track")
            if track and track.get("id"):
                tracks.append(track["id"])
        if results.get("next"):
            results = sp.next(results)
        else:
            break
    return tracks

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

def roast_playlist():
    """Roast the playlist using text input instead of file upload"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    if not os.path.exists("playlist_tracks.json"):
        return "Error: playlist_tracks.json not found."
    
    try:
        with open("playlist_tracks.json", "r", encoding="utf-8") as f:
            playlist_data = json.load(f)
        
        tracks_text = playlist_data
        
        prompt = f"""
        I'm going to give you a list of songs from a Spotify playlist. 
        Your job is to ROAST this playlist in the funniest, most humiliating way possible, have a black man way of talking, like a gangsta black dude from the hood. 
        Be savage but creative and humorous. Point out any patterns, embarrassing song choices, 
        or what this playlist says about the person's music taste.
        
        Here are the tracks:
        {tracks_text}
        
        Now roast this musical disaster:
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        return response.text
        
    except Exception as e:
        try:
            response = client.models.generate_content(
                model="gemini-1.0-pro",
                contents=[prompt]
            )
            return response.text
        except:
            return f"Failed to generate roast after multiple attempts: {str(e)}"

def main():

    print("Spotiscan: random ass project i made for no reason")
    
    ascii_art = """
                                                                 
                    ▗▖     █                                ▗▖   
                    ▐▌     ▀   ▐▌        ▐▌                 ▐▌   
▝█ █▌ ▟█▙      ▗▟██▖▐▙██▖ ██  ▐███      ▐███  █▟█▌ ▟██▖▗▟██▖▐▙██▖
 █▖█ ▐▛ ▜▌     ▐▙▄▖▘▐▛ ▐▌  █   ▐▌        ▐▌   █▘   ▘▄▟▌▐▙▄▖▘▐▛ ▐▌
 ▐█▛ ▐▌ ▐▌      ▀▀█▖▐▌ ▐▌  █   ▐▌        ▐▌   █   ▗█▀▜▌ ▀▀█▖▐▌ ▐▌
  █▌ ▝█▄█▘     ▐▄▄▟▌▐▌ ▐▌▗▄█▄▖ ▐▙▄       ▐▙▄  █   ▐▙▄█▌▐▄▄▟▌▐▌ ▐▌
  █   ▝▀▘       ▀▀▀ ▝▘ ▝▘▝▀▀▀▘  ▀▀        ▀▀  ▀    ▀▀▝▘ ▀▀▀ ▝▘ ▝▘
 █▌                                                              
                                                                 
"""

    print(ascii_art)


    parser = argparse.ArgumentParser(description="Roast a Spotify playlist")
    parser.add_argument("--playlist", "-p", help="Playlist ID or URL to fetch")
    parser.add_argument("--out", "-o", default="playlist_tracks.json", help="Output JSON filename")
    args = parser.parse_args()

    print("Authenticating with Spotify...")

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=SCOPE,
            )
        )
        print("Spotify authentication successful.\n")
    except Exception as e:
        print(f"Spotify authentication failed: {e}")
        return

    playlist_id = args.playlist
    if not playlist_id:
        playlist_id = input("Enter playlist ID or URL to fetch: ").strip()

    if not playlist_id:
        print("No playlist provided. Exiting.")
        return

    print(f"Fetching tracks for playlist...")
    try:
        track_ids = get_playlist_tracks(sp, playlist_id)
        print(f"Found {len(track_ids)} tracks.")

        tracks_info = batch_track_info(sp, track_ids)

        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(tracks_info, f, indent=2, ensure_ascii=False)

        print(f"Wrote {len(tracks_info)} tracks to {args.out}")

        print("\nGenerating roast...")
        roast = roast_playlist()
        print("\n" + "="*50)
        print("PLAYLIST ROAST:")
        print("="*50)
        print(roast)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
