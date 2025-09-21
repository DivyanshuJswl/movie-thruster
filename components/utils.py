# components/utils.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import asyncio
import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pickle
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv('API_KEY', '267c1b3158c38eaca2695696fd831f59')
POSTER_PLACEHOLDER = "https://res.cloudinary.com/dh5cebjwj/image/upload/v1758476649/download_idywpr.png"
ERROR_POSTER = "https://via.placeholder.com/200x300?text=Error+Loading"

# Initialize session state variables
def init_session_state():
    for key in ['show_all_recommendations', 'movie_number', 'selected_movie_name', 
                'user_menu', 'recent_recommendations', 'poster_cache', 
                'movie_details_cache', 'movies_loaded', 'similarity_loaded',
                'movies', 'similarity', 'moviesemo']:
        if key not in st.session_state:
            if key in ['poster_cache', 'movie_details_cache']:
                st.session_state[key] = {}
            elif key == 'recent_recommendations':
                st.session_state[key] = []
            elif key in ['movies_loaded', 'similarity_loaded']:
                st.session_state[key] = False
            else:
                st.session_state[key] = None

# Initialize the database
def init_db():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recommended_movies
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT,
                genres TEXT,
                rating REAL,
                recommendation_date TEXT)''')
    
    # Create user preferences table
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                preferred_genres TEXT,
                min_rating REAL,
                created_date TEXT)''')
    
    # Create watchlist table
    c.execute('''CREATE TABLE IF NOT EXISTS watchlist
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                movie_id INTEGER,
                movie_title TEXT,
                added_date TEXT)''')
    
    conn.commit()
    conn.close()

# Insert recommended movie data into the database
def insert_recommendation(movie_title, genres, rating):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("INSERT INTO recommended_movies (movie_title, genres, rating, recommendation_date) VALUES (?, ?, ?, ?)",
            (movie_title, ', '.join(genres), rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Fetch the last recommended movies from the database
def fetch_recommendations(limit=10):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT movie_title, genres, rating, recommendation_date FROM recommended_movies ORDER BY id DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data

# Fetch all recommendations from the database
def fetch_all_recommendations():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT movie_title, genres, rating, recommendation_date FROM recommended_movies ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

# Clear all recommended movies from the database
def clear_recommendations():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("DELETE FROM recommended_movies")
    conn.commit()
    conn.close()

# Add movie to watchlist
def add_to_watchlist(movie_id, movie_title):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    # Using a default user_id for simplicity
    c.execute("INSERT INTO watchlist (user_id, movie_id, movie_title, added_date) VALUES (?, ?, ?, ?)",
            ("default_user", movie_id, movie_title, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Get watchlist
def get_watchlist():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT movie_id, movie_title FROM watchlist WHERE user_id = ? ORDER BY added_date DESC", ("default_user",))
    data = c.fetchall()
    conn.close()
    return data

# Remove from watchlist
def remove_from_watchlist(movie_id):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", ("default_user", movie_id))
    conn.commit()
    conn.close()

# Save user preferences
def save_user_preferences(preferred_genres, min_rating):
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    # Using a default user_id for simplicity
    c.execute("INSERT OR REPLACE INTO user_preferences (user_id, preferred_genres, min_rating, created_date) VALUES (?, ?, ?, ?)",
            ("default_user", ','.join(preferred_genres), min_rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Get user preferences
def get_user_preferences():
    conn = sqlite3.connect("movies.db")
    c = conn.cursor()
    c.execute("SELECT preferred_genres, min_rating FROM user_preferences WHERE user_id = ? ORDER BY id DESC LIMIT 1", ("default_user",))
    data = c.fetchone()
    conn.close()
    
    if data:
        return data[0].split(','), data[1]
    return [], 5.0

# Function to display the pie chart of genres
def display_genre_pie_chart(recommendations):
    genre_count = {}
    for rec in recommendations:
        genres = rec[1].split(', ')
        for genre in genres:
            if genre in genre_count:
                genre_count[genre] += 1
            else:
                genre_count[genre] = 1

    genre_labels = list(genre_count.keys())
    genre_values = list(genre_count.values())

    # Plotting the pie chart
    if genre_labels:
        fig = px.pie(values=genre_values, names=genre_labels, title="Recommended Movies by Genre")
        st.plotly_chart(fig)
    else:
        st.info("No genre data available to display.")

# Load data with caching
@st.cache_resource
def load_data():
    movies_dict = pickle.load(open('data/movie_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    
    similarity = pickle.load(open('data/similarity.pkl', 'rb'))
    
    from data.emo import movies_data
    moviesemo = pd.DataFrame(movies_data)
    moviesemo['emotions'] = moviesemo['emotions'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    moviesemo['genres'] = moviesemo['genres'].apply(lambda x: eval(x) if isinstance(x, str) else x)
    
    return movies_df, similarity, moviesemo

# Async function to fetch movie details
async def fetch_movie_details_async(movie_id, session):
    # Check cache first
    if movie_id in st.session_state.movie_details_cache:
        return st.session_state.movie_details_cache[movie_id]
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {'api_key': API_KEY}
    
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                
                # Default values if data is missing
                poster_path = "https://image.tmdb.org/t/p/w780/" + data.get('poster_path', '') if data.get('poster_path') else POSTER_PLACEHOLDER
                
                result = (
                    poster_path,
                    data.get('overview', 'No overview available'),
                    data.get('vote_average', 0.0),
                    data.get('release_date', 'Unknown'),
                    [genre['name'] for genre in data.get('genres', [])],
                    data.get('budget', 0),
                    data.get('revenue', 0),
                    data.get('runtime', 0),
                    [lang['name'] for lang in data.get('spoken_languages', [])],
                    data.get('tagline', 'No tagline available'),
                    [comp['name'] for comp in data.get('production_companies', [])],
                    data.get('imdb_id', ''),
                    data.get('homepage', '')
                )
                
                # Cache the result
                st.session_state.movie_details_cache[movie_id] = result
                return result
            else:
                raise Exception(f"HTTP error: {response.status}")
                
    except Exception as e:
        result = (
            POSTER_PLACEHOLDER,
            "Details temporarily unavailable",
            0.0,
            "2000-01-01",
            ["Unknown"],
            0,
            0,
            0,
            ["Unknown"],
            "No tagline available",
            ["Unknown"],
            "",
            ""
        )
        st.session_state.movie_details_cache[movie_id] = result
        return result

# Async function to fetch multiple movie details
async def fetch_multiple_movie_details(movie_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_movie_details_async(movie_id, session) for movie_id in movie_ids]
        results = await asyncio.gather(*tasks)
        return results

# Function to run async code from sync context
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Async function to fetch posters
async def fetch_posters_async(movie_id, session):
    # Check cache first
    if movie_id in st.session_state.poster_cache:
        return st.session_state.poster_cache[movie_id]
    
    url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {'api_key': API_KEY}
    
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                
                if 'poster_path' in data and data['poster_path']:
                    poster_url = "https://image.tmdb.org/t/p/w780/" + data['poster_path']
                    st.session_state.poster_cache[movie_id] = poster_url
                    return poster_url
                else:
                    st.session_state.poster_cache[movie_id] = POSTER_PLACEHOLDER
                    return POSTER_PLACEHOLDER
            else:
                raise Exception(f"HTTP error: {response.status}")
                
    except Exception as e:
        st.session_state.poster_cache[movie_id] = ERROR_POSTER
        return ERROR_POSTER

# Async function to fetch multiple posters
async def fetch_multiple_posters(movie_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_posters_async(movie_id, session) for movie_id in movie_ids]
        results = await asyncio.gather(*tasks)
        return results

# Movie card component for consistent UI
def movie_card(movie_title, poster_url, rating, genres, release_date, overview, width=200, movie_id=None, show_add_button=False):
    with st.container():
        # Card container with border
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0; height: 100%;">
            <h4 style="margin-top: 0; margin-bottom: 8px; font-size: 16px;">{movie_title}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(poster_url, width=width)
            
            if show_add_button and movie_id:
                if st.button("➕ Add to Watchlist", key=f"add_{movie_id}", use_container_width=True):
                    add_to_watchlist(movie_id, movie_title)
                    st.success(f"Added {movie_title} to watchlist!")
        
        with col2:
            # Rating with stars
            stars = "⭐" * int(rating / 2)
            st.caption(f"{stars} ({rating}/10)")
            
            # Genres as tags
            if genres and genres[0] != "Unknown":
                genres_html = " ".join([f'<span style="background-color: #f0f2f6; padding: 2px 6px; border-radius: 8px; margin: 1px; font-size: 10px; display: inline-block;">{genre}</span>' for genre in genres[:2]])
                st.markdown(genres_html, unsafe_allow_html=True)
            
            # Release date
            if release_date != "Unknown":
                try:
                    release_date_formatted = datetime.strptime(release_date, "%Y-%m-%d").strftime("%d %b %Y")
                    st.caption(f"Released: {release_date_formatted}")
                except:
                    st.caption(f"Released: {release_date}")
            
            # Overview with expander
            if overview and overview != "No overview available":
                limited_overview = limit_overview(overview, 80)
                st.caption(limited_overview)

# Limit overview text
def limit_overview(overview, char_limit=100):
    if not overview or overview == "No overview available":
        return "No overview available"
        
    if len(overview) <= char_limit:
        return overview

    truncated = overview[:char_limit]
    sentence_end = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))

    if sentence_end != -1:
        return truncated[:sentence_end + 1]  # Include the punctuation

    word_boundary = truncated.rfind(' ')
    if word_boundary != -1:
        return truncated[:word_boundary] + "..."

    return truncated + "..."