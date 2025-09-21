# components/emotion_recommender.py
import streamlit as st
from components.utils import *

def get_movie_details():
    st.header("🎭 Movie Recommendations Based on Emotions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Emotion selection
        emotion_options = ['Happiness', 'Sadness', 'Romance', 'Inspiration', 'Comedy', 'Excitement', 'Suspense']
        selected_emotion = st.selectbox("Select an Emotion:", emotion_options, key="emotion_select")
    
    with col2:
        # Genre selection
        genre_options = ['Animation', 'Drama', 'Romance', 'Comedy', 'Family', 'Action', 'Adventure', 'Thriller']
        selected_genre = st.selectbox("Select a Genre:", genre_options, key="genre_select")
    
    if st.button('🎯 Get Recommendations', type="primary"):
        with st.spinner('Finding the perfect movies for you...'):
            # Filter based on selected emotion and genre
            recommended_movies = st.session_state.moviesemo[
                st.session_state.moviesemo['emotions'].apply(lambda emotions: selected_emotion in emotions) |
                st.session_state.moviesemo['genres'].apply(lambda genres: selected_genre in genres)
            ].head(15)  # Limit to 15 movies
            
            # Check if there are recommended movies
            if not recommended_movies.empty:
                st.success(f"Found {len(recommended_movies)} recommendations!")
                
                # Get movie IDs
                movie_ids = []
                for _, row in recommended_movies.iterrows():
                    matching_movies = st.session_state.movies[st.session_state.movies['title'] == row['title']]
                    if not matching_movies.empty:
                        movie_index = matching_movies.index[0]
                        movie_id = st.session_state.movies.iloc[movie_index].movie_id
                        movie_ids.append(movie_id)
                
                # Fetch details asynchronously
                details_list = run_async(fetch_multiple_movie_details(movie_ids))
                
                # Display movies in a grid
                cols = st.columns(3)
                for idx, (_, row) in enumerate(recommended_movies.iterrows()):
                    if idx >= len(details_list):
                        break
                    
                    with cols[idx % 3]:
                        details = details_list[idx]
                        movie_card(
                            row['title'],
                            details[0],
                            details[2],
                            details[4],
                            details[3],
                            details[1],
                            movie_id=movie_ids[idx],
                            show_add_button=True
                        )
            else:
                st.warning("No recommendations found for this emotion and genre.")