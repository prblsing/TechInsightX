from transformers import pipeline
import logging
import re
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure logging
logger = logging.getLogger(__name__)

# Updated model to use gpt-neo-1.3B for initial generation and t5-base for summarization
gen_model_name = 'EleutherAI/gpt-neo-1.3B'
max_tweet_length = int(os.getenv('MAX_TWEET_LENGTH', 120))

try:
    logger.info(f'Initializing text-generation model: {gen_model_name}')
    generator = pipeline('text-generation', model=gen_model_name)
    logger.info('Model initialized successfully')
except Exception as e:
    logger.error(f'Failed to initialize model: {str(e)}')
    raise

offensive_words = ["fuck", "shit", "damn", "bitch", "asshole", "fucking", "fucker"]

def contains_offensive_language(text: str) -> bool:
    for word in offensive_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
            return True
    return False

def clean_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    for word in offensive_words:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '*' * len(word), text, flags=re.IGNORECASE)
    return text

def clean_generated_text(generated_text, prompt):
    if prompt in generated_text:
        return generated_text.replace(prompt, '').strip()
    return generated_text.strip()

def summarize_with_llm(text: str, max_length: int = max_tweet_length) -> str:
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
        for candidate in generated_text:
            gen_summary = candidate['generated_text'].strip()
            if len(gen_summary) <= max_length and gen_summary.endswith('.'):
                logger.debug('Summary generated successfully')
                return gen_summary
        gen_summary = generated_text[0]['generated_text'].strip()
        if len(gen_summary) > max_length:
            gen_summary = gen_summary[:max_length - 14].rsplit(' ', 1)[0] + '..[read more👇🏼]'
        elif not gen_summary.endswith('.'):
            gen_summary = gen_summary + '.'
        logger.debug('Summary generated and adjusted')
        cleaned_summary = clean_generated_text(generated_text=gen_summary, prompt=prompt)
        return cleaned_summary
    except Exception as e:
        logger.error(f'Failed to generate summary: {str(e)}')
        return ""
