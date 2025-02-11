import base64
import logging
import re
from typing import List

from bs4 import BeautifulSoup

from src.genai_model.genai_model import GenAIModel
from src.news_story import NewsStory
from src.newsletters.email import Email
from src.utils.web.url import expand_url, remove_trackers

logger = logging.getLogger(__name__)

SECTIONS = [
    "Tech Across the Globe",
    "Revalued",
    "Must read",
]
SPLIT_PATTERN = "\n\n"


def bloomberg_tech_parser(email: Email) -> List[NewsStory]:
    """Parser for the Bloomberg Technology newsletter

    Args:
        email (Email): AlphaSignal email

    Returns:
        List[NewsStory]: List of NewStory objects extracted from email
    """
    logger.info(f"Parsing email '{email['subject']}'")
    txt = email["text"]
    sections = []
    for sec in SECTIONS:
        _tmp = txt.split(sec)
        sections.append(_tmp[0])
        txt = _tmp[1]
    sections = sections[1:]
    news_stories = []
    url_idx = 0
    url_dict = {}
    for section in sections:
        articles = section.split(SPLIT_PATTERN)
        for art in articles:
            txt = art.replace("\n", "").strip()
            url_dict[url_idx] = txt.split("<>")[0]
            txt = txt.replace("<>", "")
            if len(txt) > 0:
                if ": " in txt:
                    title, summary = txt.split(":")
                else:
                    logger.debug(txt)
                    title_creator = GenAIModel(model_type="small")
                    title = title_creator.completion_str(
                        user_prompt=f"Create a title for the following summary of a news article: {txt}"
                    )
                    summary = txt
                ns = NewsStory(
                    title=title.strip(),
                    url=url_idx,
                    source_of_the_news=email["sender"],
                    text="",
                    news_summary=summary.strip(),
                    date_source=email["date_utc"],
                    date_source_time_zone="utc",
                )
                news_stories.append(ns)
                url_idx += 1
    # TODO: add url to news_stories
    # Get the url
    message = email["message"]
    for pp in message["payload"]["parts"]:
        if pp["mimeType"] == "text/html":
            body_data = pp["body"]["data"]
            text_html = base64.urlsafe_b64decode(body_data).decode()
    urls = re.findall(
        r"\(https://[^\)]+\)",
        html_to_text_with_links(text_html).split(SECTIONS[0])[1].split(SECTIONS[-1])[0],
    )
    for ns in news_stories:
        raw_url = urls[ns["url"]].lstrip("(").rstrip(")")
        expanded_url = expand_url(raw_url)
        clean_furl = remove_trackers(expanded_url)
        ns["url"] = clean_furl.url
        ns["news_provider"] = clean_furl.host
    return news_stories


def html_to_text_with_links(html):
    soup = BeautifulSoup(html, "html.parser")

    # Process <a> tags to keep text + URL
    for a in soup.find_all("a"):
        link_text = a.get_text()
        link_href = a.get("href")
        if link_href:
            a.replace_with(f"{link_text} ({link_href})")  # Replace with text + URL

    return soup.get_text()  # Get cleaned text
