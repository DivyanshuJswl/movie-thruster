# components/watchlist.py
import streamlit as st
from components.utils import *

def show_watchlist():
    st.header("📋 My Watchlist")
    
    watchlist = get_watchlist()
    
    if not watchlist:
        st.info("Your watchlist is empty. Add some movies to get started!")
        return
    
    # Get movie details for watchlist items
    movie_ids = [item[0] for item in watchlist]
    details_list = run_async(fetch_multiple_movie_details(movie_ids))
    
    # Display watchlist
    for i, (movie_id, movie_title) in enumerate(watchlist):
        if i < len(details_list):
            details = details_list[i]
            poster_url, overview, rating, release_date, genres, budget, revenue, runtime, spoken_languages, tagline, production_companies, imdb_id, homepage = details
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.image(poster_url, width=150)
            
            with col2:
                st.subheader(movie_title)
                
                # Rating
                stars = "⭐" * int(rating / 2)
                st.caption(f"{stars} ({rating}/10)")
                
                # Genres
                if genres and genres[0] != "Unknown":
                    genres_html = " ".join([f'<span style="background-color: #f0f2f6; padding: 4px 8px; border-radius: 12px; margin: 2px; font-size: 12px;">{genre}</span>' for genre in genres])
                    st.markdown(genres_html, unsafe_allow_html=True)
                
                # Overview
                if overview and overview != "No overview available":
                    st.write(limit_overview(overview, 150))
                
                # Remove button
                if st.button("🗑️ Remove from Watchlist", key=f"remove_{movie_id}"):
                    remove_from_watchlist(movie_id)
                    st.success(f"Removed {movie_title} from watchlist!")
                    st.rerun()
        
        st.markdown("---")