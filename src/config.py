import os
import logging
from dotenv import load_dotenv
import tweepy
from datetime import datetime
import re
from collections import Counter

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

# Define a list of AI and technology-related terms
tech_terms = set([
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural network',
    'technology', 'tech', 'software', 'hardware', 'computer', 'algorithm', 'data',
    'digital', 'innovation', 'startup', 'internet', 'cloud', 'iot', 'robotics',
    'automation', 'blockchain', 'cybersecurity', 'programming', 'coding', 'app',
    'mobile', 'web', 'network', 'server', 'database', 'analytics', 'vr', 'ar',
    'virtual reality', 'augmented reality', 'quantum computing', '5g', 'cryptocurrency',
    'bitcoin', 'fintech', 'biotech', 'nanotech', 'big data', 'api', 'ui', 'ux',
    'devops', 'agile', 'saas', 'paas', 'iaas', 'edge computing', 'microservices'
])


def smart_tokenize(text):
    """
    A smarter tokenizer that preserves capitalized words and handles punctuation.
    """
    # Split on whitespace while preserving capitalized words
    tokens = re.findall(r'\b(?:[A-Z][a-z]+|[a-z]+|[A-Z]+)\b', text)
    return tokens


def extract_keywords(content):
    """
    Extracts keywords from the given content using a smarter approach.
    Args:
        content (str): The content to extract keywords from.
    Returns:
        list: A list of keywords.
    """
    tokens = smart_tokenize(content)
    # A more comprehensive list of stop words
    stop_words = set(
        ['the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be',
         'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could',
         'may', 'might', 'must', 'ought', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their', 'this', 'that',
         'these', 'those'])

    # Keep capitalized words and words not in stop_words
    keywords = [word for word in tokens if word not in stop_words or word[0].isupper()]

    # Count frequency of keywords
    keyword_freq = Counter(keywords)

    # Calculate relevance score (frequency + tech relevance)
    keyword_scores = {}
    for word, freq in keyword_freq.items():
        tech_relevance = 1 if word.lower() in tech_terms else 0
        keyword_scores[word] = freq + tech_relevance * 2  # Give more weight to tech terms

    # Sort keywords by score, then by length (prefer longer words)
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: (-x[1], -len(x[0])))

    # Take the top 5 keywords
    top_keywords = [word for word, _ in sorted_keywords[:5]]

    return top_keywords


def generate_hashtags(keywords):
    """
    Generates hashtags from the list of keywords.
    Args:
        keywords (list): A list of keywords.
    Returns:
        list: A list of hashtags.
    """
    hashtags = ['#' + keyword for keyword in keywords]
    return hashtags


def generate_hashtags_from_content(content):
    """
    Extracts keywords from the content and generates hashtags.
    Args:
        content (str): The content to extract keywords from and generate hashtags.
    Returns:
        list: A list of the top two most relevant hashtags.
    """
    keywords = extract_keywords(content)
    all_hashtags = generate_hashtags(keywords)

    # Filter hashtags for tech relevance
    tech_relevant_hashtags = [
        hashtag for hashtag in all_hashtags
        if hashtag[1:].lower() in tech_terms  # Remove '#' for comparison
    ]

    # If we have at least 2 tech-relevant hashtags, return those
    if len(tech_relevant_hashtags) >= 2:
        return tech_relevant_hashtags[:2]
    # If we have 1 tech-relevant hashtag, return it plus the next most relevant hashtag
    elif len(tech_relevant_hashtags) == 1:
        return tech_relevant_hashtags + [hashtag for hashtag in all_hashtags if hashtag not in tech_relevant_hashtags][
                                        :1]
    # If no tech-relevant hashtags, return the top 2 from the original list
    else:
        return all_hashtags[:2]


# Example usage
if __name__ == "__main__":
    test_cases = [
        "Google's new passport app lets you scan your passport. Chrome syncs your tabs everywhere, and Apple..[read more]",
        "Artificial Intelligence and Machine Learning are revolutionizing the tech industry.",
        "Breaking: SpaceX successfully launches Starship, marking a new era in space exploration.",
        "New study shows that regular exercise can significantly improve mental health.",
        "Apple unveils iPhone 15 with groundbreaking features at their annual event.",
        "Tech giants collaborate on new AI ethics guidelines to ensure responsible development.",
    ]

    for i, case in enumerate(test_cases, 1):
        hashtags = generate_hashtags_from_content(case)
        print(f"\nTest case {i}:")
        print("Content:", case)
        print("Generated hashtags:", hashtags)