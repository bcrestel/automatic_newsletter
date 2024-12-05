import logging
import re
from typing import List

from src.news_story import NewsStory
from src.newsletters.email import Email

logger = logging.getLogger(__name__)


SPLIT_PATTERN = "\r\n\r\n"
TITLE_PATTERN = r"READ\)[\s\r\n]*\[\d+\]"


def tldr_parser(email: Email) -> List[NewsStory]:
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
                    url=ref.strip()[:-1],
                    source_of_the_news=email["sender"],
                    news_summary=summary,
                    date_source=email["date_utc"],
                )
            )
            ii = ii + 2
        else:
            ii = ii + 1

    # Map url reference number to url
    links = list_text[-1].split("\r\n")
    map_ref_to_url = {}
    for ll in links:
        if ll.startswith("["):
            ref, url = ll.split("] ")
            map_ref_to_url[ref[1:]] = url
    for ns in news_stories:
        ns["url"] = map_ref_to_url[ns["url"]]
    return news_stories
