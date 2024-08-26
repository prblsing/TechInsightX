from news_fetcher import fetch_latest_tech_news
from content_generator import clean_text, summarize_with_llm
from config import *

logger = logging.getLogger(__name__)

posted_urls = {}


def load_posted_urls(file_path=posted_links_file):
    """Load posted URLs from the CSV file."""
    posted_urls.clear()

    if os.path.exists(file_path):
        with open(file_path, "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                posted_urls[row["Link"]] = row["DateTime"]
        logging.info(f'Loaded posted URLs from {file_path}')
    else:
        logging.info(f'{file_path} does not exist. No URLs loaded.')


def save_posted_url(url, file_path=posted_links_file):
    """Save a new URL to the CSV file."""
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(file_path, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, current_date, date_time])
    logging.info(f'Saved posted URL: {url} at {date_time}')


def tweet_ai_news():
    logging.info(f'Tweeting process started at {datetime.now()}!')
    initialize_posted_links_file()
    load_posted_urls()
    try:
        tech_news = fetch_latest_tech_news()
        if tech_news:
            for title, content, link in tech_news:
                if link in posted_urls:
                    logging.info(f'This link is already posted: {link}')
                    continue

                # Clean the content before processing
                logging.info(f"Input content - {content=}")
                clean_content = clean_text(f"{content}")
                logging.info(f"clean content - {clean_content=}")
                final_tweet = summarize_with_llm(clean_content, max_length=120)
                full_tweet = f"{final_tweet} {link}"

                # response = client.create_tweet(text=full_tweet)
                # logging.info(f'Tweet posted successfully: {response}')

                save_posted_url(link)
        else:
            logging.info('No AI news to tweet.')
    except Exception as e:
        logging.error(f"Failed to post tweet: {str(e)}")
