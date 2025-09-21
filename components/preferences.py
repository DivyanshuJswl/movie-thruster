# components/preferences.py
import streamlit as st
from components.utils import *

def show_preferences():
    st.header("⚙️ My Preferences")
    
    # Get current preferences
    preferred_genres, min_rating = get_user_preferences()
    
    # Preference form
    with st.form("preferences_form"):
        st.subheader("Set Your Preferences")
        
        # Genre preferences
        genre_options = ['Action', 'Comedy', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Thriller', 
                         'Adventure', 'Sci-Fi', 'Animation', 'Crime', 'Documentary', 'Family', 'Western']
        selected_genres = st.multiselect(
            "Preferred Genres:",
            options=genre_options,
            default=preferred_genres
        )
        
        # Minimum rating
        min_rating = st.slider(
            "Minimum Rating:",
            min_value=0.0,
            max_value=10.0,
            value=min_rating,
            step=0.5
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Preferences")
        
        if submitted:
            save_user_preferences(selected_genres, min_rating)
            st.success("Preferences saved successfully!")
    
    st.markdown("---")
    
    # Recommendation based on preferences
    st.subheader("Recommendations Based on Your Preferences")
    
    if st.button("Get Personalized Recommendations"):
        with st.spinner('Finding movies that match your preferences...'):
            # Get all movies that match preferences
            recommended_movies = []
            recommended_movies_ids = []
            
            for idx, row in st.session_state.movies.iterrows():
                movie_id = row.movie_id
                details = run_async(fetch_multiple_movie_details([movie_id]))[0]
                
                if details:
                    poster, overview, rating, release_date, genres, budget, revenue, runtime, spokenlang, tagline, productioncomp, imdb_id, homepage = details
                    
                    # Check if movie matches preferences
                    matches_genre = not selected_genres or any(genre in selected_genres for genre in genres)
                    matches_rating = rating >= min_rating
                    
                    if matches_genre and matches_rating:
                        recommended_movies.append({
                            'title': row.title,
                            'poster': poster,
                            'rating': rating,
                            'genres': genres,
                            'release_date': release_date,
                            'overview': overview,
                            'id': movie_id
                        })
                        
                        if len(recommended_movies) >= 12:  # Limit to 12 recommendations
                            break
            
            if recommended_movies:
                st.success(f"Found {len(recommended_movies)} movies that match your preferences!")
                
                # Display movies in a grid
                cols = st.columns(3)
                for i, movie in enumerate(recommended_movies):
                    with cols[i % 3]:
                        movie_card(
                            movie['title'],
                            movie['poster'],
                            movie['rating'],
                            movie['genres'],
                            movie['release_date'],
                            movie['overview'],
                            movie_id=movie['id'],
                            show_add_button=True
                        )
            else:
                st.warning("No movies match your preferences. Try adjusting your criteria.")