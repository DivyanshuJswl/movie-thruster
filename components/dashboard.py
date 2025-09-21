# components/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from components.utils import *

def show_dashboard():
    st.header("📊 Recommendation Dashboard")
    
    # Fetch all recommendations
    all_recommendations = fetch_all_recommendations()
    
    if not all_recommendations:
        st.info("No recommendations yet. Get some recommendations first!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(all_recommendations, columns=['Movie', 'Genres', 'Rating', 'Date'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Recommendations", len(df))
    
    with col2:
        avg_rating = df['Rating'].mean()
        st.metric("Average Rating", f"{avg_rating:.1f}/10")
    
    with col3:
        unique_movies = df['Movie'].nunique()
        st.metric("Unique Movies", unique_movies)
    
    with col4:
        latest_date = df['Date'].max().strftime("%Y-%m-%d")
        st.metric("Latest Recommendation", latest_date)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Ratings distribution
        st.subheader("Rating Distribution")
        fig = px.histogram(df, x='Rating', nbins=10, title="Distribution of Movie Ratings")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recommendations over time
        st.subheader("Recommendations Over Time")
        time_df = df.groupby(df['Date'].dt.date).size().reset_index(name='Count')
        fig = px.line(time_df, x='Date', y='Count', title="Daily Recommendations")
        st.plotly_chart(fig, use_container_width=True)
    
    # Genre analysis
    st.subheader("Genre Analysis")
    display_genre_pie_chart(all_recommendations)
    
    # Recent recommendations table
    st.subheader("Recent Recommendations")
    st.dataframe(df.head(10), use_container_width=True)