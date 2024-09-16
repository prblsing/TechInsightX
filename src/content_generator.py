from transformers import pipeline
import re
from config import *

logger = logging.getLogger(__name__)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Updated model to use facebook/bart-large-cnn for summarization
summarizer_model_name = 'facebook/bart-large-cnn'
max_tweet_length = int(os.getenv('MAX_TWEET_LENGTH', 120))

# Load model for summarization
try:
    logger.info(f'Initializing summarization model: {summarizer_model_name}')
    summarizer = pipeline('summarization', model=summarizer_model_name)
    logger.info('Summarization model initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize summarization model: {str(e)}')
    raise

offensive_words = ["fuck", "shit", "damn", "bitch", "asshole", "fucking", "fucker"]

def contains_offensive_language(text: str) -> bool:
    """
    Check if the text contains any offensive language.

    Args:
        text (str): The text to be checked.

    Returns:
        bool: True if offensive language is found, False otherwise.
    """
    for word in offensive_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
            return True
    return False

def clean_text(text: str) -> str:
    """
    Cleans the text by removing HTML tags, extra spaces, and URLs.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Replace offensive words with asterisks
    for word in offensive_words:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '*' * len(word), text, flags=re.IGNORECASE)

    return text

def summarize_with_llm(text: str, max_length: int = max_tweet_length) -> str:
    """
    Summarizes the given text using facebook/bart-large-cnn, ensuring the summary fits within the character limit.

    Args:
        text (str): The text to be summarized.
        max_length (int): The maximum length of the summary.

    Returns:
        str: The summarized text as a complete statement.
    """
    logger.info('Generating summary with BART model')
    
    # Ensure max_length doesn't exceed the limit of the summarization model
    model_max_length = 1024
    if len(text) > model_max_length:
        text = text[:model_max_length]
    
    try:
        summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        generated_summary = summary[0]['summary_text'].strip()

        if len(generated_summary) <= max_length:
            logger.debug('Summary generated successfully')
            return generated_summary
        else:
            logger.debug('Generated summary exceeds the max length, truncating')
            return generated_summary[:max_length - 14].rsplit(' ', 1)[0] + '..[read more👇🏼]'

    except Exception as e:
        logger.error(f'Failed to generate summary: {str(e)}')
        return ""
