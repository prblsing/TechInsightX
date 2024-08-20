import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime

# Define the directory for logs and posted URLs
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # One level up from 'src'
OPS_DIR = os.path.join(BASE_DIR, 'etc/ops')
LOG_FILE = os.path.join(OPS_DIR, f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
POSTED_LINKS_FILE = os.path.join(OPS_DIR, 'posted_links.txt')

# Ensure the directory exists
os.makedirs(OPS_DIR, exist_ok=True)

# Ensure the posted_links.txt file exists
if not os.path.exists(POSTED_LINKS_FILE):
    with open(POSTED_LINKS_FILE, 'w') as file:
        logging.info(f'{POSTED_LINKS_FILE} created.')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
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
