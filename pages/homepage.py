# app.py
import streamlit as st
from components.sidebar import make_sidebar
from components.utils import init_session_state, init_db, load_data
from components.recommendor import recommend_display
from components.emotion_recommendor import get_movie_details
from components.movie_browser import paging_movies
from components.movie_details import movie_description
from components.watchlist import show_watchlist
from components.preferences import show_preferences
from components.dashboard import show_dashboard

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Movie-Thruster",
    page_icon="🎬",
    initial_sidebar_state="expanded"
)

def check_authentication():
    """Check if user is properly authenticated"""
    if ('logged_in' not in st.session_state or 
        not st.session_state.logged_in or 
        'user_data' not in st.session_state):
        
        st.error("🚫 Access Denied: Please login to access Movie-Thruster")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;'>
                <h3 style='color: #495057; margin-bottom: 1rem;'>🎬 Welcome to Movie-Thruster</h3>
                <p style='color: #6c757d; margin-bottom: 2rem;'>Please login to access your personalized movie recommendations</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()

def main():
    check_authentication()
    
    # Initialize session state and database
    init_session_state()
    init_db()
    
    # Load data if not already loaded
    if not st.session_state.movies_loaded:
        with st.spinner("Loading movie data..."):
            movies, similarity, moviesemo = load_data()
            st.session_state.movies = movies
            st.session_state.similarity = similarity
            st.session_state.moviesemo = moviesemo
            st.session_state.movies_loaded = True
    
    # Setup sidebar
    make_sidebar()
    
    # Main content based on selection
    if st.session_state.user_menu == 'Recommend Similar Movies':
        recommend_display()
    elif st.session_state.user_menu == 'Recommend by Emotions':
        get_movie_details()
    elif st.session_state.user_menu == 'Browse All Movies':
        paging_movies()
    elif st.session_state.user_menu == 'Movie Details':
        movie_description()
    elif st.session_state.user_menu == 'My Watchlist':
        show_watchlist()
    elif st.session_state.user_menu == 'My Preferences':
        show_preferences()
    elif st.session_state.user_menu == 'Dashboard':
        show_dashboard()
    
    # Recent recommendations section (shown on all pages except dashboard)
    if st.session_state.user_menu != 'Dashboard':
        st.markdown("---")
        st.header("📋 Recently Recommended Movies")
        
        # Load recent recommendations if not loaded
        if not st.session_state.recent_recommendations:
            from components.utils import fetch_recommendations
            st.session_state.recent_recommendations = fetch_recommendations()
        
        if st.session_state.recent_recommendations:
            # Display as a table
            import pandas as pd
            df = pd.DataFrame(st.session_state.recent_recommendations, 
                             columns=['Movie', 'Genres', 'Rating', 'Date'])
            st.dataframe(df, use_container_width=True)
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button('🔄 Refresh Recommendations'):
                    from components.utils import fetch_recommendations
                    st.session_state.recent_recommendations = fetch_recommendations()
                    st.rerun()
            
            with col2:
                if st.button('🗑️ Clear All Recommendations'):
                    from components.utils import clear_recommendations
                    clear_recommendations()
                    st.session_state.recent_recommendations = []
                    st.success("All recommendations have been cleared!")
                    st.rerun()
            
            with col3:
                if st.button('📊 Show Genre Distribution'):
                    from components.utils import fetch_all_recommendations, display_genre_pie_chart
                    all_recommendations = fetch_all_recommendations()
                    display_genre_pie_chart(all_recommendations)
        else:
            st.info("No recommendations yet. Get some recommendations first!")

if __name__ == "__main__":
    main()