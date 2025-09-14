import pandas as pd
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import random

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
# This will handle login, token exchange, and redirect handling.    
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
st.markdown(
    """
    <h4 style='color: #1DB954; font-weight: bold;'>
        🎯 Select Time Range for Your Top Tracks
    </h4>
    """,
    unsafe_allow_html=True
)
time_range = st.selectbox("Choose time range:",
                          options=["short_term", "medium_term", "long_term"],
                          format_func=lambda x: {
                              "short_term": "Last 4 weeks",
                               "medium_term": "Last 6 months",
                               "long_term": "All time"
                          }[x]
    )

# Fetch total top tracks (just to count them)
top_tracks_data = sp.current_user_top_tracks(limit=1, time_range=time_range)
total_top_tracks = top_tracks_data['total']

# Styled total count box
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

#fetch user's top tracks based on selected time range
top_limit = st.slider("How many top tracks do you want to see?", min_value=5, max_value=50, value=20)
#sp = spotipy.Spotify(auth_manager=auth_manager)
top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=top_limit)

#display top tracks
st.subheader("🎵 Your Top Tracks")
for idx, item in enumerate(top_tracks['items'], start=1):
    track_name = item['name']
    artist_name = item['artists'][0]['name']
    album_image = item['album']['images'][0]['url']
    track_url = item['external_urls']['spotify']  # Link to the track on Spotify

    # Create two columns: one for the image, one for text
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.image(album_image, width=60)  # Small album cover
    
    with col2:
        # Bold number + clickable song name, normal artist name
        st.markdown(f"**{idx}.** [{track_name}]({track_url}) by {artist_name}")

#display liked songs
st.subheader("❤️ Your Liked Songs")

#fetch all liked songs first to get the total count 
liked_total_data = sp.current_user_saved_tracks(limit=1)
total_liked = liked_total_data['total']

#show total liked songs
# Styled total liked songs box
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

#slider to select number of liked songs to display
liked_limit =  st.slider("How many Liked songs do you want to see?", min_value=5, max_value=total_liked, value=20)
#fetch liked songs from spotify 
liked_songs = sp.current_user_saved_tracks(limit=liked_limit) #you can increase your limits

for idx, item in enumerate(liked_songs['items'], start=1):
    track = item['track']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    album_image = track['album']['images'][0]['url']
    track_url = track['external_urls']['spotify']  # Link to the track on Spotify

    #layout with columns
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(album_image, width=60)  # Small album cover
    
    with col2:
        # Bold number + clickable song name, normal artist name
        st.markdown(f"**{idx}.** [{track_name}]({track_url}) by {artist_name}")

# ==========================
# 🎵 USER PLAYLISTS SECTION
# ==========================
st.subheader("📂 Your Playlists")

#get the current user ID
user_id = sp.current_user()['id']
#fetch the playlists for that user id
playlists = sp.user_playlists(user_id)

#show the total playlists count 
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
#slider to select number of playlists to display
playlist_limit = st.slider("How many playlists do you want to see?",
                           min_value=5, 
                           max_value=total_playlists, 
                           value=10)

#display the playlists
for idx, playlist in enumerate(playlists['items'][:playlist_limit],start=1):
    playlist_name = playlist['name']
    playlist_url = playlist['external_urls']['spotify']
    playlist_tracks = playlist['tracks']['total']
    playlist_image = playlist['images'][0]['url'] if playlist['images'] else None

    col1, col2 = st.columns([1, 4])
    with col1:
        if playlist_image:
            st.image(playlist_image, width=60)  # Small playlist cover
        else:
            st.image("https://i.imgur.com/8sZQ9Bp.png", width=60)
    
    with col2:
        st.markdown(f"**{idx}.**[{playlist_name}]({playlist_url}) — {playlist_tracks} tracks")

# ========================
# 🎤 Display Top Artists
# ========================
st.subheader("🌟 Your Top Artists")

# Time range selection
artist_time_range = st.selectbox(
    "🎯 Select Time Range for Your Top Artists",
    options=["short_term", "medium_term", "long_term"],
    format_func=lambda x: {
        "short_term": "Last 4 Weeks",
        "medium_term": "Last 6 Months",
        "long_term": "All Time"
    }[x]
)
# Slider for how many to display
artist_limit = st.slider("How many top artists do you want to see?", min_value=5, max_value=50, value=10)

#fetch the artists
#top_artists = sp.current_user_top_artists(limit=20, time_range=artist_time_range)

# Fetch top artists from Spotify
top_artists = sp.current_user_top_artists(limit=artist_limit, time_range=artist_time_range)
# Styled total count box
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
#display artist info
for idx, artist in enumerate(top_artists["items"], start=1):
    artist_name = artist['name']
    artist_image = artist['images'][0]['url'] if artist['images'] else "https://i.imgur.com/8sZQ9Bp.png"
    artist_url = artist['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        if artist_image:
            st.image(artist_image, width=60)
        else:
            st.image("https://i.imgur.com/8sZQ9Bp.png", width=60)
    with col2:
        st.markdown(f"**{idx}.**[{artist_name}]({artist_url})")

# ======================
# 🎤 Your Saved Artists
# ======================
st.subheader("💎 Your Saved Artists")

#fetch saved artists
saved_artists_data = sp.current_user_followed_artists(limit=50)
saved_artists = saved_artists_data['artists']['items']

#total saved artists count
total_saved_artists = saved_artists_data['artists']['total']

# Styled total count box
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

#slider to select how many artists to display
saved_limit = st.slider("How many saved artists do you want to see?", min_value=5, max_value=min(50, total_saved_artists), value=20)

#show saved artists
for idx, artist in enumerate(saved_artists[:saved_limit], start=1):
    artist_name = artist['name']
    artist_image = artist['images'][0]['url'] if artist['images'] else "https://i.imgur.com/8sZQ9Bp.png"
    artist_url = artist['external_urls']['spotify']

    col1, col2 = st.columns([1, 4])
    with col1:
        if artist_image:
            st.image(artist_image, width=60)
    with col2:
        st.markdown(f"**{idx}.**[{artist_name}]({artist_url})")

# ======================
# Save User Data + IDs
# ======================
def fetch_and_save_user_data(sp, top_tracks, liked_songs, top_artists, playlists, save_dir="data"):
    """
    Fetches user data, saves raw datasets, and also collects Track & Artist IDs for recommendations.
    """

    # prepare a folder for saving
    os.makedirs(save_dir, exist_ok=True)

    # --- Convert each dataset to DataFrame ---
    track_df = pd.DataFrame(top_tracks['items'])
    liked_df = pd.DataFrame(liked_songs['items'])
    artist_df = pd.DataFrame(top_artists['items'])
    playlist_df = pd.DataFrame(playlists['items'])

    # --- Save raw datasets ---
    track_df.to_csv(os.path.join(save_dir, "top_tracks.csv"), index=False)
    liked_df.to_csv(os.path.join(save_dir, "liked_songs.csv"), index=False)
    artist_df.to_csv(os.path.join(save_dir, "top_artists.csv"), index=False)
    playlist_df.to_csv(os.path.join(save_dir, "playlists.csv"), index=False)

    print("✅ Raw DataFrames saved to CSV")
    print(f"   • Top Tracks: {len(track_df)} rows")
    print(f"   • Liked Songs: {len(liked_df)} rows")
    print(f"   • Top Artists: {len(artist_df)} rows")
    print(f"   • Playlists: {len(playlist_df)} rows")

    # --- Collect Track IDs (from top tracks + liked songs) ---
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
    print(f"🎵 Saved {len(all_track_ids)} unique track IDs → track_ids.csv")

    # --- Collect Artist IDs ---
    artist_ids = artist_df["id"].dropna().tolist()
    pd.DataFrame({"artist_id": artist_ids}).to_csv(
        os.path.join(save_dir, "artist_ids.csv"), index=False
    )
    print(f"👩‍🎤 Saved {len(artist_ids)} artist IDs → artist_ids.csv")

    return track_df, liked_df, artist_df, playlist_df, all_track_ids, artist_ids

track_df, liked_df, artist_df, playlist_df, track_ids, artist_ids = fetch_and_save_user_data(
    sp, top_tracks, liked_songs, top_artists, playlists
)

# ======================
# 🟡 Step 2: Dataset Prep
# ======================
def build_final_dataset(track_df, liked_df, artist_df):
    """
    Build a metadata-only dataset (since audio features are blocked in dev mode).
    Includes: track popularity, release year, artist popularity, and genres.
    """
    # 🎵 Collect track IDs
    track_ids = track_df['id'].dropna().tolist()

    liked_ids = []
    if 'track' in liked_df.columns:
        liked_ids = liked_df['track'].dropna().apply(
            lambda x: eval(x)['id'] if isinstance(x, str) else None
        ).dropna().tolist()

    all_track_ids = list(set(track_ids + liked_ids))
    print(f"🎶 Total unique tracks: {len(all_track_ids)}")

    # 📝 Extract release year
    if "album.release_date" in track_df.columns:
        track_df['release_year'] = pd.to_datetime(
            track_df['album.release_date'], errors='coerce'
        ).dt.year

    # 🎤 Merge artist popularity + genres
    if "id" in artist_df.columns:
        artist_meta = artist_df[['id', 'popularity', 'genres']].rename(
            columns={'id': 'artist_id', 'popularity': 'artist_popularity'}
        )

        # Simplify artist column (some are dicts/lists)
        def get_first_artist(artist_field):
            if isinstance(artist_field, list) and len(artist_field) > 0:
                return artist_field[0]['id'] if isinstance(artist_field[0], dict) else artist_field[0]
            return None

        if "artists" in track_df.columns:
            track_df['artist_id'] = track_df['artists'].apply(get_first_artist)

        # Final merge
        final_df = track_df.merge(artist_meta, on="artist_id", how="left")
    else:
        final_df = track_df.copy()

    # 💾 Save to CSV
    if not os.path.exists("data"):
        os.makedirs("data")
    final_df.to_csv("data/final_tracks.csv", index=False)

    print("✅ Final dataset saved → data/final_tracks.csv")
    print(f"   Rows: {len(final_df)} | Columns: {len(final_df.columns)}")
    print(final_df.head())  # quick preview
    return final_df

final_df = build_final_dataset(track_df, liked_df, artist_df)

# ======================
# 👩‍🎤 Recommend by Similar Artists
# ======================
def recommend_by_artists(sp, artist_df, limit=10):
    """
    Recommend tracks based on related artists.
    Returns a list of dicts with track info for UI display.
    """
    recs = []
    for artist_id in artist_df["id"].dropna().unique()[:5]:
        try:
            related = sp.artist_related_artists(artist_id)
            for ra in related["artists"][:2]:
                top_tracks = sp.artist_top_tracks(ra["id"])
                for t in top_tracks["tracks"][:2]:
                    recs.append({
                        "id": t["id"],
                        "name": t["name"],
                        "artist": ", ".join([a["name"] for a in t["artists"]]),
                        "url": t["external_urls"]["spotify"],
                        "preview": t.get("preview_url"),
                        "image": t["album"]["images"][0]["url"] if t["album"]["images"] else None
                    })
                    if len(recs) >= limit:
                        return recs
        except Exception as e:
            print(f"⚠️ Failed artist rec for {artist_id}: {e}")
    return recs[:limit]


# ======================
# 🎵 Spotify Recommendations API
# ======================
def recommend_spotify(sp, track_df, artist_df, limit=10):
    """
    Recommend tracks using Spotify's recommendations API.
    Returns a list of dicts with track info for UI display.
    """
    seed_artists = artist_df["id"].dropna().tolist()[:2]
    seed_tracks = track_df["id"].dropna().tolist()[:2]

    try:
        recs = sp.recommendations(
            seed_artists=seed_artists,
            seed_tracks=seed_tracks,
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
    except Exception as e:
        print(f"⚠️ Spotify recs failed: {e}")
        return []


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ======================
# 🎯 Content-Based Recommender
# ======================
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_content_based(final_df, seed_track, limit=10):
    """
    Recommend songs similar to a seed track using cosine similarity on text features.
    Returns a list of dicts with UI-friendly info.
    """
    if "name" not in final_df.columns or "artist_name" not in final_df.columns:
        return []

    # Combine track name + artist name as text
    final_df["combined"] = final_df["name"].fillna("") + " " + final_df["artist_name"].fillna("")

    # Vectorize
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(final_df["combined"])

    # Find the seed track index
    try:
        idx = final_df[final_df["name"] == seed_track].index[0]
    except IndexError:
        return []

    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    sim_indices = cosine_sim.argsort()[-limit-1:-1][::-1]  # exclude the seed itself

    recs = []
    for i in sim_indices:
        row = final_df.iloc[i]
        recs.append({
            "id": row.get("id"),
            "name": row.get("name"),
            "artist": row.get("artist_name"),
            "url": row["external_urls"]["spotify"] if isinstance(row.get("external_urls"), dict) else None,
            "preview": row.get("preview_url"),
            "image": row["album"]["images"][0]["url"] if isinstance(row.get("album"), dict) and row["album"].get("images") else None
        })

    return recs


import numpy as np

# ======================
# 🌀 Smart Mix Recommender
# ======================
def smart_mix(sp, final_df, track_df, artist_df, seed_track=None, limit=10):
    """
    Hybrid recommender: combine content-based + Spotify API + similar artists.
    Returns a list of dicts with UI-friendly info.
    """
    recs = []

    # Content-based part
    if seed_track:
        cb_recs = recommend_content_based(final_df, seed_track, limit=limit//3)
        recs.extend(cb_recs)

    # Spotify picks
    api_recs = recommend_spotify(sp, track_df, artist_df, limit=limit//3)
    recs.extend(api_recs)

    # Similar artists
    artist_recs = recommend_by_artists(sp, artist_df, limit=limit//3)
    recs.extend(artist_recs)

    # Deduplicate by track id
    seen = set()
    unique_recs = []
    for r in recs:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique_recs.append(r)

    return unique_recs[:limit]


# ======================
# 🎛 Update Streamlit UI
# ======================
st.header("🎵 Recommendations")

mode = st.selectbox("Choose a recommendation mode", [
    "Content-Based (Cosine Similarity)",
    "Smart Mix"
])
num_recs = st.slider("Number of recommendations", 5, 20, 10)

if mode in ["Content-Based (Cosine Similarity)", "Smart Mix"]:
    seed_track = st.selectbox("Pick a seed track", final_df["name"].dropna().unique())
else:
    seed_track = None

if st.button("Get Recommendations"):
    if mode == "Content-Based (Cosine Similarity)" and seed_track:
        recs = recommend_content_based(final_df, seed_track, limit=num_recs)

    elif mode == "Smart Mix":
        recs = smart_mix(sp, final_df, track_df, artist_df, seed_track=seed_track, limit=num_recs)

    else:
        recs = []
    # --- 🎧 Display Recommendations ---
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
        st.info("No recommendations found. Try another mode.")

 
