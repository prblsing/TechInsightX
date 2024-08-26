from scheduler import tweet_ai_news
# from retweet_bot import search_and_retweet
from config import *

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logging.info('Starting tweet scheduling')
        MAX_TWEETS_PER_DAY = 2
        tweet_ai_news()

        # TBD
        # search_and_retweet("AI", max_tweets=2)

        # run_scheduler()
    except Exception as e:
        logging.critical('Unhandled exception in main application', exc_info=True)
