import random
import schedule
import time
import logging
from datetime import datetime, timedelta
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
                break  # Post only one tweet per call to this function
        else:
            logging.info('No AI news to tweet')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")


def schedule_tweets(job, max_tweets):
    """
    Schedule tweets to be posted randomly throughout the day.
    """
    # determine the number of tweets to post today (between 1 and max_tweets)
    num_tweets_today = random.randint(1, max_tweets)
    logging.info(f"Scheduling {num_tweets_today} tweets for today")

    # schedule tweets at random times throughout the day
    for _ in range(num_tweets_today):
        # calculate a random time within the day
        now = datetime.now()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        time_left = (end_of_day - now).total_seconds()
        random_seconds = random.randint(0, int(time_left))
        tweet_time = now + timedelta(seconds=random_seconds)

        # schedule the job
        schedule.every().day.at(tweet_time.strftime("%H:%M")).do(job)
        logging.info(f"Scheduled tweet at {tweet_time.strftime('%H:%M')}")


def run_scheduler(max_tweets=4):
    """
    Run the scheduler to post a random number of tweets daily.
    """
    logging.info('Starting daily scheduler')
    while True:
        schedule.clear()

        # schedule tweets for today
        schedule_tweets(tweet_ai_news, max_tweets)

        while schedule.jobs:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if there's something to run

        # wait until the next day
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        sleep_seconds = (tomorrow.replace(hour=0, minute=0, second=0) - now).total_seconds()
        logging.info(f"Sleeping for {int(sleep_seconds/3600)} hours until the next day's schedule.")
        time.sleep(sleep_seconds)
