from transformers import pipeline
import logging
import re
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Updated model to use gpt-neo-1.3B for initial generation and t5-base for summarization
gen_model_name = 'EleutherAI/gpt-neo-1.3B'

# facebook/opt-2.7b
model_name = 'EleutherAI/gpt-neo-1.3B'
max_tweet_length = int(os.getenv('MAX_TWEET_LENGTH', 120))

# load model for text generation
try:
    logger.info(f'Initializing text-generation model: {model_name}')
    generator = pipeline('text-generation', model=model_name)
    logger.info('Model initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize model: {str(e)}')
    raise


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
    return text


def summarize_with_llm(text: str, max_length: int = max_tweet_length) -> str:
    """
    Summarizes the given text using a language model, ensuring a complete statement within the character limit.

    Args:
        text (str): The text to be summarized.
        max_length (int): The maximum length of the summary.

    Returns:
        str: The summarized text as a complete statement.
    """
    logger.info('Generating summary with LLM')
    prompt = (
        f"Please rephrase the following article into a concise statement: {text}"
        f" Make sure the statement is clear, under {max_length} characters, "
        "contains no special characters, and is written in correct English."
    )

    try:
        generated_text = generator(
            prompt,
            max_new_tokens=max_length,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            num_return_sequences=3,
            truncation=True,
            pad_token_id=generator.tokenizer.eos_token_id,
            return_full_text=False,
        )

        # select the best candidate that fits within the character limit
        for candidate in generated_text:
            gen_summary = candidate['generated_text'].strip()
            if len(gen_summary) <= max_length and gen_summary.endswith('.'):
                logger.debug('Summary generated successfully')
                return gen_summary

        # if no suitable candidate is found, truncate the first one
        gen_summary = generated_text[0]['generated_text'].strip()
        if len(gen_summary) > max_length:
            gen_summary = gen_summary[:max_length - 14].rsplit(' ', 1)[0] + '..[read more👇🏼]'
        elif not gen_summary.endswith('.'):
            gen_summary = gen_summary + '.'

        logger.debug('Summary generated and adjusted')
        return gen_summary

    except Exception as e:
        logger.error(f'Failed to generate summary: {str(e)}')
        return ""
