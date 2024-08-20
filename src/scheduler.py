import random
import time
import logging
from datetime import datetime
from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import client
import os

posted_urls = set()

def load_posted_urls(file_path=POSTED_LINKS_FILE):
    """Load posted URLs from the file."""
    logging.info(f'Loading posted URLs from {file_path}')
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                url, date_posted = line.strip().split(',', 1)
                posted_urls.add(url)
                logging.info(f'Loaded posted URL: {url} (Posted on: {date_posted})')
    else:
        logging.info(f'{file_path} does not exist. No URLs loaded.')

def save_posted_url(url, file_path=POSTED_LINKS_FILE):
    """Save a new URL to the file with the current date."""
    with open(file_path, "a") as file:
        date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{url},{date_posted}\n")
        logging.info(f'Saved posted URL: {url} (Posted on: {date_posted})')

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
