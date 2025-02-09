import logging
import re
from typing import List

from src.news_story import NewsStory
from src.newsletters.email import Email
from src.utils.web.url import expand_url, remove_trackers

logger = logging.getLogger(__name__)


SPLIT_PATTERN = "\r\n\r\n"
TITLE_PATTERN = r"READ\)[\s\r\n]*\[\d+\]"


# TODO: Profile that function and speed it up
def tldr_parser(email: Email) -> List[NewsStory]:
    """Parser for the TLDR newsletter

    Args:
        email (Email): TLDR email

    Returns:
        List[NewsStory]: List of NewStory objects extracted from email
    """
    logger.debug(f"Parsing email: {email['subject']}")
    list_text = email["text"].split(SPLIT_PATTERN)
    news_stories = []
    ii = 0
    while ii < len(list_text):
        if re.search(TITLE_PATTERN, list_text[ii]):
            title, ref = list_text[ii].split("[")
            title = title[: title.rfind("(")].strip()
            summary = list_text[ii + 1].strip().replace("\r\n", " ")
            news_stories.append(
                NewsStory(
                    title=title,
                    url=ref.strip()[:-1],  # ref nb for the url
                    source_of_the_news=email["sender"],
                    news_summary=summary,
                    date_source=email["date_utc"],
                    date_source_time_zone="utc",
                )
            )
            ii = ii + 2
        else:
            ii = ii + 1

    # Build mapping from reference number to url's:
    all_links = list_text[-1]
    links = all_links.split("\r\n")
    map_ref_to_url = {}
    for ll in links:
        if ll.startswith("["):
            ref, url = ll.split("] ")
            map_ref_to_url[ref[1:]] = url
    # Map url reference number to a clean url (str):
    for ns in news_stories:
        ref_nb = ns["url"]
        raw_url = map_ref_to_url[ref_nb]
        expanded_url = expand_url(raw_url)
        clean_furl = remove_trackers(expanded_url)
        ns["url"] = clean_furl.url
        ns["news_provider"] = clean_furl.host
    return news_stories
