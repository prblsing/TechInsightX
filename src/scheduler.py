import random
import schedule
import time
import logging
from datetime import datetime
from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import client

posted_urls = set()


def tweet_ai_news():
    logging.info(f'Tweeting process started at {datetime.now()}!')
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
        else:
            logging.info('No AI news to tweet')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")


def schedule_tweets_for_now(job, max_tweets):
    """
    Schedule tweets at short intervals for testing purposes.
    """
    for _ in range(random.randint(1, max_tweets)):
        # schedule the job for every 10 minute, starting now
        schedule.every(10).minutes.do(job)
