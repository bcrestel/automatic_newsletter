import logging
import re
from typing import List

from src.genai_model.genai_model import GenAIModel
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
TOP_NEWS_START = "WHAT'S NEW"
TOP_NEWS_END = "TRY NOW"
SPLIT_LINES = "\r\n\r\n"
SPLIT_PATTERN = "\r\n\r\n \t*\r\n"


def alpha_signal_parser(email: Email) -> List[NewsStory]:
    """Parser for the AlphaSignal newsletter

    Args:
        email (Email): AlphaSignal email

    Returns:
        List[NewsStory]: List of NewStory objects extracted from email
    """
    logger.info(f"Parsing email '{email['subject']}'")
    txt = email["text"]
    lines = txt.split("TOP NEWS")[1].split(SPLIT_LINES)
    news_stories = []
    for line in lines:
        if "\t*\r" in line and re.search(r"\[\d+\]", line):
            txt = line.lstrip(" \t*\r\n").replace("\r\n", " ").strip()
            ns = NewsStory(
                title=txt.split("[")[0].strip(),
                url=txt.split("[")[1].split("]")[0],
                source_of_the_news=email["sender"],
                text="",
                news_summary=re.sub(r"\[(\d+)\]", "", txt.split(":")[-1].strip()),
                date_source=email["date_utc"],
                date_source_time_zone="utc",
            )
            if len(news_stories) == 0:
                ns["text"] = get_text_for_top_news(email["text"])
                summarizer = GenAIModel(model_type="small")
                summary = summarizer.completion_str(
                    f"Summarize the following article: {ns['text']}"
                )
                ns["news_summary"] = summary.strip()
            news_stories.append(ns)
    # Replace reference numbers by actual url
    all_links = email["text"].split("Links:\r\n------\r\n")[-1]
    replace_link_numbers_with_url(all_links=all_links, news_stories=news_stories)
    return news_stories


def get_text_for_top_news(email_text: str) -> str:
    return (
        email_text.split(SECTIONS[0])[2]
        .split(TOP_NEWS_START)[1]
        .split(SECTIONS[1])[0]
        .split(TOP_NEWS_END)[0]
        .replace("\r\n", " ")
        .strip()
    )
