import os
import logging
from datetime import datetime
import random
import time
from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import log_dir, generate_hashtags_from_content, client
import csv

posted_urls = {}
current_date = datetime.now().strftime('%Y%b%d')
posted_links_file = os.path.join(log_dir, f"posted_links_{current_date}.csv")


def initialize_posted_links_file(file_path=posted_links_file):
    """Initialize the CSV file if it does not exist."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Link", "Date", "DateTime"])
        logging.info(f'Created new CSV file: {file_path}')


def load_posted_urls(file_path=posted_links_file):
    """Load posted URLs from the CSV file."""
    posted_urls.clear()
    if os.path.exists(file_path):
        with open(file_path, "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                posted_urls[row["Link"]] = row["DateTime"]
        logging.info(f'Loaded posted URLs from {file_path}')
    else:
        logging.info(f'{file_path} does not exist. No URLs loaded.')


def save_posted_url(url, file_path=posted_links_file):
    """Save a new URL to the CSV file."""
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(file_path, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, current_date, date_time])
    logging.info(f'Saved posted URL: {url} at {date_time}')


def tweet_ai_news():
    logging.info(f'Tweeting process started at {datetime.now()}!')
    initialize_posted_links_file()
    load_posted_urls()
    try:
        tech_news = fetch_latest_tech_news()
        if tech_news:
            for title, content, link in tech_news:
                if link in posted_urls:
                    logging.info(f'This link is already posted: {link}')
                    continue

                # Clean the content before processing
                logging.info(f"Input content - {content=}")
                clean_content = clean_text(f"{content}")
                logging.info(f"clean content - {clean_content=}")
                final_tweet = summarize_with_llm(clean_content, max_length=120)
                for_hashtag = summarize_with_llm(clean_content, max_length=250)
                hashtags = generate_hashtags_from_content(for_hashtag)

                # Add hashtags to the tweet
                if hashtags:
                    final_tweet += " " + " ".join(hashtags[:3])

                full_tweet = f"{final_tweet} {link}"
                logging.info(f"{full_tweet=}")

                # Uncomment the next line to actually post the tweet
                response = client.create_tweet(text=full_tweet)
                logging.info(f'Tweet posted successfully: {response}')
                save_posted_url(link)
                logging.info(f'Tweet link saved successfully.')
                sleep_time = random.randint(180, 600)
                logging.info(f"Sleeping for {sleep_time // 60} minutes and {sleep_time % 60} seconds.")
                time.sleep(sleep_time)
        else:
            logging.info('No AI news to tweet.')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")
