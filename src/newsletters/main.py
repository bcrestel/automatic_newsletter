import logging
from pathlib import Path
from typing import List

from src.news_story import NewsStory
from src.newsletters.config import (
    CREDENTIAL_PATH,
    NEWSLETTER_AND_PARSER,
    SCOPES,
    TOKEN_PATH,
)
from src.newsletters.gmail import Gmail

PATH_TO_ROOT = Path("../..")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


def runner(after: str, before: str) -> List[NewsStory]:
    gmail = Gmail(
        path_to_token=PATH_TO_ROOT / TOKEN_PATH,
        path_to_credentials=PATH_TO_ROOT / CREDENTIAL_PATH,
        scopes=SCOPES,
    )

    # Fetch emails from the selected newsletters for the given range of dates
    logger.info("Query emails")
    all_senders = NEWSLETTER_AND_PARSER.keys()
    emails = {
        _sender: gmail.fetch_emails(sender=_sender, after=after, before=before)
        for _sender in all_senders
    }
    logger.info(f"Using {len(emails.keys())} sender(s): {emails.keys()}.")
    for key, value in emails.items():
        logger.debug(f"Found {len(value)} emails from sender {key}")

    # Extract the news stories from the emails
    logger.info("Parsing emails to extract news stories")
    news_stories = [
        NEWSLETTER_AND_PARSER[_sender](email)
        for _sender, list_emails in emails.items()
        for email in list_emails
    ]
    news_stories = [new_story for n_s in news_stories for new_story in n_s]
    logger.info(f"Newsletters block complete. Found {len(news_stories)} news stories.")

    return news_stories
