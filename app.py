import streamlit as st
from sentiment_analysis import get_tweets
import time

st.title("Twitter Sentiment Analysis")

query = st.text_input("Enter search term:")
count = st.slider("Number of tweets:", 1, 100, 10)

if st.button("Analyze"):
    if query:
        with st.spinner('Fetching tweets... This might take a while for larger requests...'):
            try:
                progress_bar = st.progress(0)
                df = get_tweets(query, count)
                progress_bar.progress(100)
                
                # Display statistics
                st.success(f"Retrieved {len(df)} tweets!")
                
                # Show sentiment distribution
                sentiment_counts = df['Sentiment'].value_counts()
                st.write("### Sentiment Distribution")
                st.bar_chart(sentiment_counts)
                
                # Display the full dataframe
                st.write("### Detailed Results")
                st.dataframe(df)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a search term")
