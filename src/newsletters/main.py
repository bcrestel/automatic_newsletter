import logging
from typing import List

from config import NEWSLETTER_AND_PARSER
from gmail import Gmail

from news_story import NewsStory

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


def runner(after: str, before: str) -> List[NewsStory]:
    gmail = Gmail()

    # Fetch emails from the selected newsletters for the given range of dates
    all_senders = NEWSLETTER_AND_PARSER.keys()
    emails = {
        _sender: gmail.fetch_emails(sender=_sender, after=after, before=before)
        for _sender in all_senders
    }

    # Extract the news stories from the emails
    news_stories = [
        _parser(emails[_sender]) for _sender, _parser in NEWSLETTER_AND_PARSER.items()
    ]

    return news_stories
