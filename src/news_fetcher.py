import feedparser
from typing import List, Tuple
from config import *

logger = logging.getLogger(__name__)


def fetch_latest_tech_news() -> List[Tuple[str, str, str]]:
    """
    Fetches the latest tech news from various RSS feeds.

    Returns:
        A list of tuples containing the title, summary, and link of the news articles.
    """
    logging.info('Fetching latest tech news from RSS feeds')
    rss_feeds = [
        "https://blog.ml.cmu.edu/feed/",
        "https://code.facebook.com/posts/rss",
        "https://deepmind.com/blog/feed/basic/",
        "http://news.mit.edu/rss/topic/artificial-intelligence2",
        "http://www.reddit.com/r/MachineLearning/.rss",
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.feedburner.com/TechCrunch/startups",
        "https://www.cnet.com/rss/news/",
        "https://blogs.gartner.com/smarterwithgartner/feed/",
        "https://techradar.com/rss",
        "http://pcmag.com/feeds/rss/latest",
        "https://nesslabs.com/feed",
        "http://www.forbes.com/entrepreneurs/index.xml",
        "https://developer.atlassian.com/blog/feed.xml",
        "https://blog.twitter.com/engineering/en_us/blog.rss"
    ]

    all_entries = []
    for feed_url in rss_feeds:
        try:
            logging.debug(f'Parsing feed: {feed_url}')
            feed = feedparser.parse(feed_url)
            all_entries.extend(feed.entries)
        except Exception as e:
            logging.error(f'Error parsing feed {feed_url}: {str(e)}')

    logging.info(f'Total entries found: {len(all_entries)}')

    # Sort entries by published date
    all_entries.sort(key=lambda entry: entry.published_parsed, reverse=True)

    # Filter for entries within the last 24 hours and related to AI
    recent_entries = [
        entry for entry in all_entries
        if datetime(*entry.published_parsed[:6]) > datetime.now() - timedelta(hours=24)
           and ('AI' in entry.title or 'artificial intelligence' in entry.title or 'machine learning' in entry.title)
    ]
    logging.info(f'Recent AI-related entries found: {len(recent_entries)}')

    return [(entry.title, entry.summary, entry.link) for entry in recent_entries]
