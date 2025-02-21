import logging
import re
from typing import List

from src.genai_model.genai_model import GenAIModel
from src.news_story import NewsStory
from src.newsletters.email import Email
from src.newsletters.parser.process_links import process_raw_url
from src.utils.list import flatten_list_of_lists

logger = logging.getLogger(__name__)

SECTION_BREAKS = [
    "Most interesting startup stories from the week",
    "Most interesting VC and funding news this week",
    "Last but not least",
    "Featured jobs from CrunchBoard",
]

SPLIT_PATTERN = "\r\n\r\n"


def tech_crunch_parser(email: Email) -> List[NewsStory]:
    logger.info(f"Parsing email '{email['subject']}'")
    txt = email["text"]
    sections = []
    for idx, sec in enumerate(SECTION_BREAKS):
        _tmp = txt.split(sec)
        if len(_tmp) != 2:
            logger.error(f"Should have gotten 2 pieces, instead got {len(_tmp)}.")
            logger.error(f"Original text to split: {txt}")
            raise ValueError(f"Error while splitting the text for section: '{sec}'.")
        logger.debug(f"section: {sec}")
        is_last_section = idx == len(SECTION_BREAKS) - 1
        if idx > 0:
            if is_last_section:
                summary = "".join(
                    _tmp[0].strip().split("Image Credits: ")[1].split("\r\n\r\n")[1:]
                )
                url = (
                    re.findall(r"\(https://[^\)]+\)", summary)[0]
                    .lstrip("(")
                    .rstrip(")")
                )
                title_creator = GenAIModel(
                    model_type="small",
                    system_promt="You are journalist specialized in technology and artificial intelligence.",
                )
                title = title_creator.completion_str(
                    user_prompt=f"Create a title for a news article given a summary of that news article.\nOnly return the title and only return a single title.\nHere is the summary:\n{summary}"
                ).strip()
                ns = NewsStory(
                    title=title,
                    url=url,
                    news_provider="techcrunch.com",
                    source_of_the_news=email["sender"],
                    text="",
                    news_summary=re.sub(r"\(https://[^\)]+\)", "", summary),
                    date_source=email["date_utc"],
                    date_source_time_zone="utc",
                )
                sections.append([ns])
            else:
                sections.append(process_section(_tmp[0], email))
        txt = _tmp[1]
    return flatten_list_of_lists(sections)


def process_section(section: str, email: Email) -> List[NewsStory]:
    articles = section.strip().split(SPLIT_PATTERN)
    threshold = 1e9
    news_stories = []
    for idx, art in enumerate(articles):
        if art.startswith("Image Credits:"):
            threshold = idx + 2
        if idx >= threshold:
            art_no_url = re.sub(r"\(https://[^\)]+\)", "", art)
            if ":" in art_no_url:
                splits = art_no_url.split(":")
                title = splits[0].strip()
                summary = "".join(splits[1:]).strip()
            elif "?" in art_no_url:
                splits = art_no_url.split("?")
                title = splits[0].strip()
                summary = "".join(splits[1:]).strip()
            else:
                summary = art_no_url
                title_creator = GenAIModel(
                    model_type="small",
                    system_promt="You are journalist specialized in technology and artificial intelligence.",
                )
                title = title_creator.completion_str(
                    user_prompt=f"Create a title for a news article given a summary of that news article.\nOnly return the title and only return a single title.\nHere is the summary:\n{summary}"
                ).strip()
            dirty_urls = re.findall(r"\(https://[^\)]+\)", art)
            urls = [url.lstrip("(").rstrip(")") for url in dirty_urls]
            if len(urls) == 1:
                urls = urls[0]
            ns = NewsStory(
                title=title,
                url=urls,
                news_provider="techcrunch.com",
                source_of_the_news=email["sender"],
                text="",
                news_summary=summary,
                date_source=email["date_utc"],
                date_source_time_zone="utc",
            )
            news_stories.append(ns)
    return news_stories
