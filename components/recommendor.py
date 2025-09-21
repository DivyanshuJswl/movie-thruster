# components/recommender.py
import streamlit as st
import random
from components.utils import *

def recommend(movie, num_recommendations, genre_filter=None, randomize=False, rating_filter=None):
    if randomize:
        random_movies_list = random.sample(range(len(st.session_state.movies)), min(num_recommendations, len(st.session_state.movies)))
    else:
        movie_index = st.session_state.movies[st.session_state.movies['title'] == movie].index[0]
        distances = st.session_state.similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations + 1]
        random_movies_list = [x[0] for x in movies_list]

    # Get movie IDs
    movie_ids = [st.session_state.movies.iloc[idx].movie_id for idx in random_movies_list]
    
    # Fetch details asynchronously
    details_list = run_async(fetch_multiple_movie_details(movie_ids))
    
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_overviews = []
    recommended_movies_ratings = []
    recommended_movies_genres = []
    recommended_movies_release_date = []
    recommended_movies_ids = []

    for idx, details in zip(random_movies_list, details_list):
        poster, overview, rating, release_date, genres, budget, revenue, runtime, spokenlang, tagline, productioncomp, imdb_id, homepage = details

        # Apply genre filter if specified
        if genre_filter and genre_filter not in genres:
            continue

        # Apply rating filter if specified
        if rating_filter and rating < rating_filter:
            continue

        recommended_movies.append(st.session_state.movies.iloc[idx].title)
        recommended_movies_posters.append(poster)
        recommended_movies_overviews.append(overview)
        recommended_movies_ratings.append(rating)
        recommended_movies_genres.append(genres)
        recommended_movies_release_date.append(release_date)
        recommended_movies_ids.append(st.session_state.movies.iloc[idx].movie_id)

        # Insert the recommended movie into the database
        insert_recommendation(st.session_state.movies.iloc[idx].title, genres, rating)

    return recommended_movies, recommended_movies_posters, recommended_movies_overviews, recommended_movies_ratings, recommended_movies_genres, recommended_movies_release_date, recommended_movies_ids

def recommend_display():
    st.header("🎬 Find Similar Movies")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Searchable input for selecting a movie
        selected_movie_name = st.selectbox(
            'Select a movie:', 
            st.session_state.movies['title'].values,
            key="movie_select"
        )
    
    with col2:
        # Using slider for the number of recommendations
        num_recommendations = st.slider('Number of recommendations', min_value=1, max_value=25, value=5, key="num_recs")

    # Options
    col1, col2 = st.columns(2)
    
    with col1:
        # Checkbox for random recommendations
        randomize = st.checkbox('Recommend Random Movies', key="random_check")
    
    with col2:
        # Optional rating filter
        rating_filter = st.slider('Minimum Rating', min_value=0.0, max_value=10.0, value=5.0, step=0.5, key="rating_filter")

    if st.button('🔍 Find Recommendations', type="primary"):
        with st.spinner('Analyzing similar movies...'):
            names, posters, overviews, ratings, genres, release_date, movie_ids = recommend(
                selected_movie_name, 
                num_recommendations, 
                genre_filter=st.session_state.get('selected_genre'), 
                randomize=randomize, 
                rating_filter=rating_filter
            )
            
            if names:
                st.success(f"Found {len(names)} recommendations!")
                
                # Display movies in a responsive grid
                cols = st.columns(3)
                for i in range(len(names)):
                    with cols[i % 3]:
                        movie_card(
                            names[i],
                            posters[i],
                            ratings[i],
                            genres[i],
                            release_date[i],
                            overviews[i],
                            movie_id=movie_ids[i],
                            show_add_button=True
                        )
            else:
                st.warning("No movies match your criteria. Try adjusting your filters.")
                
            # Update recent recommendations
            st.session_state.recent_recommendations = fetch_recommendations()