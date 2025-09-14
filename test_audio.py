import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

#title 
st.title("🎵 Spotify Music Recommender")
st.markdown("Login with your Spotify account to analyze your music taste and get recommendations.")
st.write("---")

#load .env variables 
load_dotenv()

#fetch from the environment
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

#set the permissions
SCOPE = "user-library-read user-top-read user-read-private user-follow-read"

# Create a SpotifyOAuth object using client credentials and desired scopes.  
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)                                         

#generate spotify login url 
auth_url = auth_manager.get_authorize_url()

#display the login link in the streamlit 
if st.button("🔐 Connect with Spotify"):
    st.markdown(f"[Click here to log in]({auth_url})", unsafe_allow_html=True)

#ask user to paste the redirect url 
redirect_response = st.text_input("📥 Paste the full redirect url after login:")

#process it and get the access token
if st.button("Submit URL") and redirect_response:
    code = auth_manager.parse_response_code(redirect_response)
    token_info = auth_manager.get_access_token(code, as_dict=True)

    if token_info:
        access_token = token_info['access_token']
        st.success("✅ Logged in successfully!")

        sp = spotipy.Spotify(auth=access_token)

        user_profile = sp.current_user()
        st.image(user_profile['images'][0]['url'], width=100)
        st.write(f"**Welcome, {user_profile['display_name']}!** 👋")

    else:
        st.error("❌ Error logging in.")

#section: top tracks after login
st.subheader("🎵 Your Top Tracks")
sp = spotipy.Spotify(auth_manager=auth_manager)

#dropdown to select time range
time_range = st.selectbox("Choose time range:",
                          options=["short_term", "medium_term", "long_term"],
                          format_func=lambda x: {
                              "short_term": "Last 4 weeks",
                               "medium_term": "Last 6 months",
                               "long_term": "All time"
                          }[x]
    )

# Fetch total top tracks
top_tracks_data = sp.current_user_top_tracks(limit=1, time_range=time_range)
total_top_tracks = top_tracks_data['total']

st.markdown(
    f"""
    <div style="
        background-color: #1DB954;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;">
        🎵 Total Top Tracks: {total_top_tracks}
    </div>
    """,
    unsafe_allow_html=True
)

#fetch user's top tracks
top_limit = st.slider("How many top tracks do you want to see?", min_value=5, max_value=50, value=20)
top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=top_limit)

st.subheader("🎵 Your Top Tracks")
for idx, item in enumerate(top_tracks['items'], start=1):
    track_name = item['name']
    artist_name = item['artists'][0]['name']
    album_image = item['album']['images'][0]['url']
    track_url = item['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(album_image, width=60)
    with col2:
        st.markdown(f"**{idx}.** [{track_name}]({track_url}) by {artist_name}")

#display liked songs
st.subheader("❤️ Your Liked Songs")
liked_total_data = sp.current_user_saved_tracks(limit=1)
total_liked = liked_total_data['total']

st.markdown(
    f"""
    <div style="
        background-color: #1DB954;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;">
        ❤️ Total Liked Songs: {total_liked}
    </div>
    """,
    unsafe_allow_html=True
)

liked_limit =  st.slider("How many Liked songs do you want to see?", min_value=5, max_value=total_liked, value=20)
liked_songs = sp.current_user_saved_tracks(limit=liked_limit)

for idx, item in enumerate(liked_songs['items'], start=1):
    track = item['track']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    album_image = track['album']['images'][0]['url']
    track_url = track['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(album_image, width=60)
    with col2:
        st.markdown(f"**{idx}.** [{track_name}]({track_url}) by {artist_name}")

# ==========================
# 🎵 USER PLAYLISTS SECTION
# ==========================
st.subheader("📂 Your Playlists")

user_id = sp.current_user()['id']
playlists = sp.user_playlists(user_id)

total_playlists = playlists['total']
st.markdown(
    f"""
    <div style="
        background-color: #1DB954;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;">
        📂 Total Playlists: {total_playlists}
    </div>
    """,
    unsafe_allow_html=True
)

playlist_limit = st.slider("How many playlists do you want to see?",
                           min_value=5, 
                           max_value=total_playlists, 
                           value=10)

for idx, playlist in enumerate(playlists['items'][:playlist_limit],start=1):
    playlist_name = playlist['name']
    playlist_url = playlist['external_urls']['spotify']
    playlist_tracks = playlist['tracks']['total']
    playlist_image = playlist['images'][0]['url'] if playlist['images'] else None

    col1, col2 = st.columns([1, 4])
    with col1:
        if playlist_image:
            st.image(playlist_image, width=60)
        else:
            st.image("https://i.imgur.com/8sZQ9Bp.png", width=60)
    with col2:
        st.markdown(f"**{idx}.**[{playlist_name}]({playlist_url}) — {playlist_tracks} tracks")

# ========================
# 🎤 Display Top Artists
# ========================
st.subheader("🌟 Your Top Artists")

artist_time_range = st.selectbox(
    "🎯 Select Time Range for Your Top Artists",
    options=["short_term", "medium_term", "long_term"],
    format_func=lambda x: {
        "short_term": "Last 4 Weeks",
        "medium_term": "Last 6 Months",
        "long_term": "All Time"
    }[x]
)

artist_limit = st.slider("How many top artists do you want to see?", min_value=5, max_value=50, value=10)

top_artists = sp.current_user_top_artists(limit=artist_limit, time_range=artist_time_range)

st.markdown(
    f"""
    <div style="
        background-color: #1DB954;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;">
        🎤 Total Top Artists: {artist_limit}
    </div>
    """,
    unsafe_allow_html=True
)

for idx, artist in enumerate(top_artists["items"], start=1):
    artist_name = artist['name']
    artist_image = artist['images'][0]['url'] if artist['images'] else "https://i.imgur.com/8sZQ9Bp.png"
    artist_url = artist['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(artist_image, width=60)
    with col2:
        st.markdown(f"**{idx}.**[{artist_name}]({artist_url})")

# ======================
# 💎 Your Saved Artists
# ======================
st.subheader("💎 Your Saved Artists")

saved_artists_data = sp.current_user_followed_artists(limit=50)
saved_artists = saved_artists_data['artists']['items']

total_saved_artists = saved_artists_data['artists']['total']

st.markdown(
    f"""
    <div style="
        background-color: #1DB954;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;">
        💎 Total Saved Artists: {total_saved_artists}  
    </div>
    """,
    unsafe_allow_html=True
)

saved_limit = st.slider("How many saved artists do you want to see?", min_value=5, max_value=min(50, total_saved_artists), value=20)

for idx, artist in enumerate(saved_artists[:saved_limit], start=1):
    artist_name = artist['name']
    artist_image = artist['images'][0]['url'] if artist['images'] else "https://i.imgur.com/8sZQ9Bp.png"
    artist_url = artist['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(artist_image, width=60)
    with col2:
        st.markdown(f"**{idx}.**[{artist_name}]({artist_url})")

# ======================
# 📊 Save User Data
# ======================
def fetch_and_save_user_data(sp, top_tracks, liked_songs, top_artists, playlists, save_dir="data"):
    os.makedirs(save_dir, exist_ok=True)

    track_df = pd.DataFrame(top_tracks['items'])
    liked_df = pd.DataFrame(liked_songs['items'])
    artist_df = pd.DataFrame(top_artists['items'])
    playlist_df = pd.DataFrame(playlists['items'])

    track_df.to_csv(os.path.join(save_dir, "top_tracks.csv"), index=False)
    liked_df.to_csv(os.path.join(save_dir, "liked_songs.csv"), index=False)
    artist_df.to_csv(os.path.join(save_dir, "top_artists.csv"), index=False)
    playlist_df.to_csv(os.path.join(save_dir, "playlists.csv"), index=False)

    track_ids = track_df["id"].dropna().tolist()

    liked_ids = []
    if "track" in liked_df.columns:
        for _, row in liked_df.iterrows():
            if isinstance(row["track"], dict) and row["track"].get("id"):
                liked_ids.append(row["track"]["id"])

    all_track_ids = list(set(track_ids + liked_ids))
    pd.DataFrame({"track_id": all_track_ids}).to_csv(
        os.path.join(save_dir, "track_ids.csv"), index=False
    )

    artist_ids = artist_df["id"].dropna().tolist()
    pd.DataFrame({"artist_id": artist_ids}).to_csv(
        os.path.join(save_dir, "artist_ids.csv"), index=False
    )

    return track_df, liked_df, artist_df, playlist_df, all_track_ids, artist_ids

track_df, liked_df, artist_df, playlist_df, track_ids, artist_ids = fetch_and_save_user_data(
    sp, top_tracks, liked_songs, top_artists, playlists
)

# ======================
# 🎵 Spotify Recommender
# ======================
def recommend_spotify(sp, track_df, artist_df, limit=10, manual_artist=None, manual_track=None):
    seed_artists = []
    seed_tracks = []

    if manual_artist:
        seed_artists = [manual_artist]
    else:
        seed_artists = artist_df["id"].dropna().tolist()[:2]

    if manual_track:
        seed_tracks = [manual_track]
    else:
        seed_tracks = track_df["id"].dropna().tolist()[:2]

    # Safety: Spotify requires at least one seed
    if not seed_artists and not seed_tracks:
        return []

    recs = sp.recommendations(
        seed_artists=seed_artists if seed_artists else None,
        seed_tracks=seed_tracks if seed_tracks else None,
        limit=limit
    )

    results = []
    for t in recs["tracks"]:
        results.append({
            "id": t["id"],
            "name": t["name"],
            "artist": ", ".join([a["name"] for a in t["artists"]]),
            "url": t["external_urls"]["spotify"],
            "preview": t.get("preview_url"),
            "image": t["album"]["images"][0]["url"] if t["album"]["images"] else None
        })
    return results


# ======================
# 🎛 Recommendations UI
# ======================
st.header("🎵 Recommendations")

num_recs = st.slider("Number of recommendations", 5, 20, 10)

# Collect all available artists from top artists, liked songs, and playlists
artist_options = {artist['name']: artist['id'] for artist in top_artists["items"]}

for item in liked_songs['items']:
    track = item['track']
    for a in track['artists']:
        artist_options[a['name']] = a['id']

for playlist in playlists['items']:
    playlist_tracks = sp.playlist_tracks(playlist['id'], limit=20)
    for item in playlist_tracks['items']:
        track = item['track']
        if track and track.get('artists'):
            for a in track['artists']:
                artist_options[a['name']] = a['id']

# Collect all available tracks from top tracks, liked songs, and playlists
track_options = {track['name']: track['id'] for track in top_tracks['items']}

for item in liked_songs['items']:
    track = item['track']
    track_options[track['name']] = track['id']

for playlist in playlists['items']:
    playlist_tracks = sp.playlist_tracks(playlist['id'], limit=20)
    for item in playlist_tracks['items']:
        track = item['track']
        if track:
            track_options[track['name']] = track['id']

manual_artist = st.selectbox("Pick a seed artist (optional)", ["None"] + sorted(artist_options.keys()))
manual_track = st.selectbox("Pick a seed track (optional)", ["None"] + sorted(track_options.keys()))

if st.button("Get Recommendations"):
    selected_artist_id = artist_options.get(manual_artist) if manual_artist != "None" else None
    selected_track_id = track_options.get(manual_track) if manual_track != "None" else None

    recs = recommend_spotify(sp, track_df, artist_df, limit=num_recs, manual_artist=selected_artist_id, manual_track=selected_track_id)

    if recs:
        st.subheader("Recommended Songs 🎶")
        for idx, rec in enumerate(recs, start=1):
            col1, col2 = st.columns([1, 3])
            with col1:
                if rec.get("image"):
                    st.image(rec["image"], width=80)
            with col2:
                st.markdown(f"**{idx}. {rec['name']}** by {rec['artist']}")
                if rec.get("url"):
                    st.markdown(f"[▶️ Listen on Spotify]({rec['url']})")
                if rec.get("preview"):
                    st.audio(rec["preview"], format="audio/mp3")
    else:
        st.info("No recommendations found. Try again!")