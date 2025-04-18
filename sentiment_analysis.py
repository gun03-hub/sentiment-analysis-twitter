import tweepy
import pandas as pd
import time
import random
from textblob import TextBlob
from concurrent.futures import ThreadPoolExecutor
from config import BEARER_TOKEN  # Store API key separately

# Authenticate with Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

cache = {}  # Cache for previous queries

def clean_tweet(tweet):
    """Remove URLs, mentions, and special characters from a tweet."""
    return " ".join(word for word in tweet.split() if not word.startswith(("@", "http")))

def analyze_sentiment(tweet):
    """Analyze sentiment using TextBlob (Positive, Neutral, Negative)."""
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity == 0:
        return "Neutral"
    else:
        return "Negative"

def analyze_sentiment_parallel(tweets):
    """Run sentiment analysis in parallel for faster processing."""
    with ThreadPoolExecutor() as executor:
        sentiments = list(executor.map(analyze_sentiment, tweets))
    return sentiments

def get_tweets(query, count=10):
    """Fetch tweets using Twitter API v2 with improved rate limit handling."""
    if query in cache:
        return cache[query]

    all_tweets = []
    max_retries = 5
    retry_count = 0
    
    while len(all_tweets) < count and retry_count < max_retries:
        try:
            # Request in smaller batches
            batch_size = min(100, count - len(all_tweets))
            time.sleep(2)  # Consistent delay between requests
            
            tweets = client.search_recent_tweets(
                query=query,
                tweet_fields=["created_at"],
                max_results=batch_size,
                next_token=None if not all_tweets else tweets.meta.get("next_token")
            )
            
            if not tweets.data:
                break
                
            all_tweets.extend(tweets.data)
            
        except tweepy.TooManyRequests:
            retry_count += 1
            wait_time = 15  # Fixed wait time
            print(f"⚠️ Rate limit reached. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            continue
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break

    if not all_tweets:
        return pd.DataFrame(columns=["Date", "Tweet", "Sentiment"])

    cleaned_tweets = [clean_tweet(tweet.text) for tweet in all_tweets]
    sentiments = analyze_sentiment_parallel(cleaned_tweets)

    data = [[tweet.created_at, text, sentiment] 
            for tweet, text, sentiment in zip(all_tweets, cleaned_tweets, sentiments)]
    df = pd.DataFrame(data, columns=["Date", "Tweet", "Sentiment"])
    
    cache[query] = df
    return df
