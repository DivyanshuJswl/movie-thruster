# components/movie_details.py
import streamlit as st
from datetime import datetime
from components.utils import *

def movie_description():
    st.header("ℹ️ Movie Details")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_movie_name = st.selectbox(
            'Select a movie:', 
            st.session_state.movies['title'].values,
            key="detail_select"
        )
    
    with col2:
        if st.button('Get Details', type="primary"):
            with st.spinner('Fetching movie details...'):
                matching_movies = st.session_state.movies[st.session_state.movies['title'] == selected_movie_name]
                if not matching_movies.empty:
                    movie_index = matching_movies.index[0]
                    movie_id = st.session_state.movies.iloc[movie_index].movie_id
                    details = run_async(fetch_multiple_movie_details([movie_id]))[0]
                    
                    if details:
                        poster_url, overview, rating, release_date, genres, budget, revenue, runtime, spoken_languages, tagline, production_companies, imdb_id, homepage = details
                        
                        # Display movie details in a nice layout
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.image(poster_url, use_column_width=True)
                            
                            # Add to watchlist button
                            if st.button("➕ Add to Watchlist", use_container_width=True):
                                add_to_watchlist(movie_id, selected_movie_name)
                                st.success(f"Added {selected_movie_name} to watchlist!")
                        
                        with col2:
                            st.markdown(f"# {selected_movie_name}")
                            
                            if tagline and tagline != "No tagline available":
                                st.markdown(f"*{tagline}*")
                            
                            # Rating
                            stars = "⭐" * int(rating / 2)
                            st.markdown(f"### {stars} {rating}/10")
                            
                            # Details in columns
                            col11, col12, col13 = st.columns(3)
                            
                            with col11:
                                st.metric("Runtime", f"{runtime} min" if runtime else "Unknown")
                            
                            with col12:
                                if release_date and release_date != "Unknown":
                                    try:
                                        release_date_formatted = datetime.strptime(release_date, "%Y-%m-%d").strftime("%d %b %Y")
                                        st.metric("Release Date", release_date_formatted)
                                    except:
                                        st.metric("Release Date", release_date)
                                else:
                                    st.metric("Release Date", "Unknown")
                            
                            with col13:
                                st.metric("Budget", f"${budget:,}" if budget else "Unknown")
                            
                            # Genres
                            st.markdown("#### Genres")
                            if genres and genres[0] != "Unknown":
                                genres_html = " ".join([f'<span style="background-color: #f0f2f6; padding: 4px 8px; border-radius: 12px; margin: 2px; font-size: 12px;">{genre}</span>' for genre in genres])
                                st.markdown(genres_html, unsafe_allow_html=True)
                            
                            # Overview
                            st.markdown("#### Overview")
                            st.write(overview)
                            
                            # Additional details in expanders
                            with st.expander("Production Details"):
                                if production_companies and production_companies[0] != "Unknown":
                                    st.write("**Production Companies:**", ", ".join(production_companies))
                                else:
                                    st.write("Production company information not available.")
                                
                                if spoken_languages and spoken_languages[0] != "Unknown":
                                    st.write("**Languages:**", ", ".join(spoken_languages))
                                else:
                                    st.write("Language information not available.")
                                
                                if revenue:
                                    st.write("**Revenue:**", f"${revenue:,}")
                                    
                            # External links
                            if imdb_id:
                                st.markdown(f"[View on IMDb](https://www.imdb.com/title/{imdb_id})")
                            if homepage:
                                st.markdown(f"[Official Website]({homepage})")
                else:
                    st.error("Movie details not found.")