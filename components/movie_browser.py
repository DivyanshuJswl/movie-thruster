# components/movie_browser.py
import streamlit as st
from components.utils import *

def paging_movies():
    st.header("📚 Browse All Movies")
    # Use get() with default value to ensure movie_number is always an integer
    movie_number = st.session_state.get('movie_number', 0) or 0    
    movies_per_page = 10
    # Search box
    search_query = st.text_input("Search movies", placeholder="Type to search...")
    
    # Filter movies based on search
    if search_query:
        filtered_movies = st.session_state.movies[st.session_state.movies['title'].str.contains(search_query, case=False)]
    else:
        filtered_movies = st.session_state.movies
    
    # Handle case when there are no movies
    if len(filtered_movies) == 0:
        st.info("No movies found matching your search.")
        return
    
    # Pagination
    total_pages = max(1, (len(filtered_movies) - 1) // movies_per_page + 1)
    current_page = movie_number // movies_per_page
    
    # Ensure movie_number doesn't exceed bounds
    if movie_number >= len(filtered_movies):
        movie_number = 0
        st.session_state.movie_number = 0
        current_page = 0
    
    # Page controls
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=current_page == 0):
            st.session_state.movie_number = max(0, movie_number - movies_per_page)
            st.rerun()
    
    with col2:
        page = st.slider("Page", 1, total_pages, current_page + 1)
        if page != current_page + 1:
            st.session_state.movie_number = (page - 1) * movies_per_page
            st.rerun()
    
    with col3:
        if st.button("Next ➡️", disabled=current_page >= total_pages - 1):
            st.session_state.movie_number = min(len(filtered_movies) - movies_per_page, movie_number + movies_per_page)
            st.rerun()
    
    # Update local variable after potential changes
    movie_number = st.session_state.get('movie_number', 0) or 0
    
    # Display movies for current page
    start_idx = movie_number
    end_idx = min(start_idx + movies_per_page, len(filtered_movies))
    
    st.write(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_movies)} movies")
    
    # Get movie IDs for current page
    movie_ids = [filtered_movies.iloc[i].movie_id for i in range(start_idx, end_idx)]
    
    # Fetch posters asynchronously
    poster_urls = run_async(fetch_multiple_posters(movie_ids))
    
    # Display movies in a grid with add to watchlist buttons
    cols = st.columns(5)
    for i in range(start_idx, end_idx):
        col_idx = (i - start_idx) % 5
        with cols[col_idx]:
            poster_idx = i - start_idx
            if poster_idx < len(poster_urls) and poster_urls[poster_idx]:
                st.image(poster_urls[poster_idx], use_column_width=True)
            else:
                st.write("No poster available")
            
            movie_title = filtered_movies.iloc[i].title
            movie_id = filtered_movies.iloc[i].movie_id
            
            st.caption(movie_title)
            
            if st.button("➕ Watchlist", key=f"watch_{movie_id}_{i}", use_container_width=True):
                add_to_watchlist(movie_id, movie_title)
                st.success(f"Added {movie_title} to watchlist!")