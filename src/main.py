from scheduler import schedule_tweets_for_now, tweet_ai_news
# from retweet_bot import search_and_retweet
import logging

if __name__ == "__main__":
    try:
        logging.info('Starting tweet scheduling')
        MAX_TWEETS_PER_DAY = 2
        schedule_tweets_for_now(tweet_ai_news, MAX_TWEETS_PER_DAY)

        # TBD
        # search_and_retweet("AI", max_tweets=2)

        # run_scheduler()
    except Exception as e:
        logging.critical('Unhandled exception in main application', exc_info=True)
