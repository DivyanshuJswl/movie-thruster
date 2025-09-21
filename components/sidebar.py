# components/sidebar.py
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3

def make_sidebar():
    with st.sidebar:
        st.title("🎬 Movie-Thruster")
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        menu_options = ['Dashboard', 'Recommend Similar Movies', 'Recommend by Emotions', 'Movie Details', 
                       'Browse All Movies', 'My Watchlist', 'My Preferences']
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=['search-heart', 'emoji-smile', 'info-circle', 'film', 'bookmark', 'gear', 'bar-chart'],
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "orange", "font-size": "14px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#852222"},
                "nav-link-selected": {"background-color": "#ff4b4b"},
            }
        )
        
        st.session_state.user_menu = selected
        
        st.markdown("---")
        
        # Quick filters
        st.subheader("Quick Filters")
        genre_options = ['Action', 'Comedy', 'Drama', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Thriller']
        selected_genre = st.selectbox('Filter by Genre', ['All Genres'] + genre_options)
        min_rating = st.slider('Minimum Rating', 0.0, 10.0, 5.0, 0.5)
        
        st.session_state.selected_genre = selected_genre if selected_genre != 'All Genres' else None
        st.session_state.min_rating = min_rating
        
        st.markdown("---")
        
        # Stats
        st.subheader("Stats")
        conn = sqlite3.connect("movies.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM recommended_movies")
        total_recommendations = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM watchlist WHERE user_id = ?", ("default_user",))
        watchlist_count = c.fetchone()[0]
        conn.close()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Recommendations", total_recommendations)
        with col2:
            st.metric("My Watchlist", watchlist_count)
        
        st.markdown("---")
        st.caption("Made with ❤️ using Streamlit")