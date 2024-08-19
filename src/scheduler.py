import random
import time
import logging
from datetime import datetime
from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import client
import os

posted_urls = set()

def load_posted_urls(file_path="posted_links.txt"):
    """Load posted URLs from the file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                posted_urls.add(line.strip())
                logging.info(f'Posted URLs loaded successfully.')

def save_posted_url(url, file_path="posted_links.txt"):
    """Save a new URL to the file."""
    with open(file_path, "a") as file:
        file.write(url + "\n")
        logging.info(f'Posted URLs saved successfully.')

def tweet_ai_news():
    logging.info(f'Tweeting process started at {datetime.now()}!')
    load_posted_urls()
    try:
        tech_news = fetch_latest_tech_news()
        if tech_news:
            for title, content, link in tech_news:
                if link in posted_urls:
                    logging.info(f'This link is already posted: {link}')
                    continue

                # clean the content before processing
                clean_content = clean_text(f"{content}")
                final_tweet = summarize_with_llm(clean_content, max_length=120)
                full_tweet = f"{final_tweet} {link}"

                response = client.create_tweet(text=full_tweet)
                logging.info(f'Tweet posted successfully: {response}')

                posted_urls.add(link)
                save_posted_url(link)
        else:
            logging.info('No AI news to tweet')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")
