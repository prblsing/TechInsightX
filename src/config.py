import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime

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
logger = logging.getLogger(__name__)
logger.info('Starting configuration setup')

# Load environment variables
load_dotenv()
logger.info('Environment variables loaded successfully')

# Twitter API credentials and client initialization
try:
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('BEARER_TOKEN')
    hf_token = os.getenv('HUGGINGFACE_API_TOKEN')

    # Market IDs (Previously WOEID)
    markets = os.getenv('MARKETS', '23424848,23424977,23424975').split(',')  # Default: India, USA, UK

    # Initialize the Twitter client
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    logger.info('Twitter API client initialized successfully')
except KeyError as e:
    logger.critical(f'Missing environment variable: {e}', exc_info=True)
    raise
except Exception as e:
    logger.critical('Failed to initialize Twitter API client', exc_info=True)
    raise


def fetch_trending_hashtags():
    """
    Fetch trending hashtags for given markets.
    """
    try:
        hashtags = set()
        for market in markets:
            logger.info(f'Fetching trending hashtags for market: {market}')
            trends = client.get_place_trends(id=market.strip())
            if trends:
                for trend in trends[0]['trends']:
                    if trend['name'].startswith('#'):
                        hashtags.add(trend['name'])
        logger.info(f'Top trending hashtags: {hashtags}')
        return list(hashtags)
    except Exception as e:
        logger.error(f'Failed to fetch trending hashtags: {e}')
        return []
