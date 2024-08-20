import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# define the directory for logs and posted URLs
OPS_DIR = os.path.join(os.path.dirname(__file__), '../etc/ops')
LOG_FILE = os.path.join(OPS_DIR, f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
POSTED_LINKS_FILE = os.path.join(OPS_DIR, 'posted_links.txt')

# ensure the directory exists
os.makedirs(OPS_DIR, exist_ok=True)

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
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
