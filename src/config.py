import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime, timedelta

# Setup directory and log file
base_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(base_dir, '..', 'etc', 'ops')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%b%d_%H%M%S")}.log')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logging.info('Starting configuration setup')

# Load environment variables
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

    # Market IDs (Previously WOEID)
    markets = os.getenv('MARKETS', '23424848, 23424977, 23424975').split(',')  # Default: India, USA, UK

    # Initialize the Twitter client
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
