import logging
import re
from typing import List

import emoji

from src.news_story import NewsStory
from src.newsletters.email import Email
from src.newsletters.parser.process_links import replace_link_numbers_with_url

logger = logging.getLogger(__name__)

SECTIONS = [
    "TOP NEWS",
    "TRENDING SIGNALS",
    "TOP PAPERS",
    "PYTHON TIP",
]
SPLIT_PATTERN = "\r\n\r\n \t*\r\n"


def alpha_signal_parser(email: Email) -> List[NewsStory]:
    txt = email["text"]
    sections = []
    for sec in SECTIONS:
        _tmp = txt.split(sec)
        sections.append(_tmp[0])
        txt = _tmp[1]
    sections = sections[1:]
    news_stories = []
    for section in sections:
        articles = section.split(SPLIT_PATTERN)
        for art in articles[1:]:
            txt = emoji.replace_emoji(art, replace="").replace("\r\n", " ").strip()
            ns = NewsStory(
                title=txt.split("[")[0].strip(),
                url=txt.split("[")[1].split("]")[0],
                source_of_the_news=email["sender"],
                news_summary=re.sub(r"\[(\d+)\]", "", txt.split(":")[-1].strip()),
                date_source=email["date_utc"],
                date_source_time_zone="utc",
            )
            news_stories.append(ns)
    # Replace reference numbers by actual url
    all_links = email["text"].split("Links:\r\n------\r\n")[-1]
    replace_link_numbers_with_url(all_links=all_links, news_stories=news_stories)
    return news_stories
