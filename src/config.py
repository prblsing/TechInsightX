import os
import logging
from dotenv import load_dotenv
import tweepy

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logging.info('Starting configuration setup')

# load environment variables
load_dotenv()
logging.info('Environment variables loaded successfully')

# Twitter API credentials and client initialization
try:
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('BEARER_TOKEN')
    hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
    model_name = os.getenv('MODEL_NAME', 'EleutherAI/gpt-neo-1.3B')
    max_tweet_length = int(os.getenv('MAX_TWEET_LENGTH', 120))

    # initialize the Twitter client
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    logging.info('Twitter API client initialized successfully')
except KeyError as e:
    logging.critical(f'Missing environment variable: {e}', exc_info=True)
    raise
except Exception as e:
    logging.critical('Failed to initialize Twitter API client', exc_info=True)
    raise
