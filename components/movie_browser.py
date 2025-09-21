# components/movie_browser.py
import streamlit as st
from components.utils import *

def paging_movies():
    st.header("📚 Browse All Movies")
    
    # Search box
    search_query = st.text_input("Search movies", placeholder="Type to search...")
    
    # Filter movies based on search
    if search_query:
        filtered_movies = st.session_state.movies[st.session_state.movies['title'].str.contains(search_query, case=False)]
    else:
        filtered_movies = st.session_state.movies
    
    # Pagination
    movies_per_page = 10
    total_pages = max(1, len(filtered_movies) // movies_per_page)
    current_page = st.session_state.movie_number // movies_per_page
    
    # Page controls
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=current_page == 0):
            st.session_state.movie_number -= movies_per_page
    
    with col2:
        page = st.slider("Page", 1, total_pages, current_page + 1)
        if page != current_page + 1:
            st.session_state.movie_number = (page - 1) * movies_per_page
    
    with col3:
        if st.button("Next ➡️", disabled=current_page >= total_pages - 1):
            st.session_state.movie_number += movies_per_page
    
    # Display movies for current page
    start_idx = st.session_state.movie_number
    end_idx = min(start_idx + movies_per_page, len(filtered_movies))
    
    st.write(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_movies)} movies")
    
    # Get movie IDs for current page
    movie_ids = [filtered_movies.iloc[i].movie_id for i in range(start_idx, end_idx)]
    
    # Fetch posters asynchronously
    poster_urls = run_async(fetch_multiple_posters(movie_ids))
    
    # Display movies in a grid with add to watchlist buttons
    cols = st.columns(5)
    for i in range(start_idx, end_idx):
        with cols[i % 5]:
            poster_idx = i - start_idx
            if poster_idx < len(poster_urls):
                st.image(poster_urls[poster_idx], use_column_width=True)
            
            movie_title = filtered_movies.iloc[i].title
            movie_id = filtered_movies.iloc[i].movie_id
            
            st.caption(movie_title)
            
            if st.button("➕ Watchlist", key=f"watch_{movie_id}", use_container_width=True):
                add_to_watchlist(movie_id, movie_title)
                st.success(f"Added {movie_title} to watchlist!")