import os
import logging
from datetime import datetime
from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import client

posted_urls = set()
log_dir = os.getenv('LOG_DIR', 'etc/ops')
posted_links_file = os.path.join(log_dir, "posted_links.txt")


def load_posted_urls(file_path=posted_links_file):
    """Load posted URLs from the file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                posted_urls.add(line.strip())
        logging.info(f'Following posted URLs are loaded successfully from {file_path}:\nposted_urls')
    else:
        logging.info(f'{file_path} does not exist. No URLs loaded.')


def save_posted_url(url, file_path=posted_links_file):
    """Save a new URL to the file."""
    with open(file_path, "a") as file:
        file.write(f"{url} (Posted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
    logging.info(f'Saved posted URL: {url} (Posted on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")})')


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

                # Clean the content before processing
                clean_content = clean_text(f"{content}")
                final_tweet = summarize_with_llm(clean_content, max_length=120)
                full_tweet = f"{final_tweet} {link}"

                response = client.create_tweet(text=full_tweet)
                logging.info(f'Tweet posted successfully: {response}')

                save_posted_url(link)
        else:
            logging.info('No AI news to tweet.')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")


def run_scheduler():
    logging.info('Starting scheduler')
    tweet_ai_news()
