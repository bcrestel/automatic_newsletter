import logging
from pathlib import Path
from typing import List

from src.config import CREDENTIAL_PATH, SCOPES, TOKEN_PATH
from src.gmail import Gmail
from src.news_story import NewsStory
from src.newsletters.config import NEWSLETTER_AND_PARSER
from src.newsletters.email import Email
from src.utils.list import flatten_list_of_lists

logger = logging.getLogger(__name__)


def runner(after: str, before: str) -> List[NewsStory]:
    """Fetch and parse newsletters from assigned gmail account

    Args:
        after (str): start date of the range. format "YYYY-MM-DD". Inclusive
        before (str): end date of the range. format "YYYY-MM-DD". Inclusive

    Returns:
        List[NewsStory]: List of processed news stories
    """
    gmail = Gmail(
        path_to_token=TOKEN_PATH,
        path_to_credentials=CREDENTIAL_PATH,
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
        logger.info(f"Found {len(value)} emails from sender {key}")

    # Extract the news stories from the emails
    logger.info("Parsing emails to extract news stories")
    news_stories = []
    parser_error: List[Email] = []
    for _sender, list_emails in emails.items():
        for email in list_emails:
            try:
                news_stories.append(NEWSLETTER_AND_PARSER[_sender](email))
            except Exception as e:
                logger.error(
                    f"Could not parse email with subject '{email['subject']} from sender '{_sender}' sent on {email['date_utc']}"
                )
                logger.error(e)
                parser_error.append(email)
    news_stories = flatten_list_of_lists(news_stories)
    logger.info(
        f"Newsletters block complete. Found {len(news_stories)} news stories in total."
    )
    if len(parser_error) > 0:
        logger.info(f"Failed to parse {len(parser_error)} email(s).")
        logger.info([email["subject"] for email in parser_error])

    return news_stories, parser_error
