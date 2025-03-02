import base64
import logging
import re
from typing import List

from bs4 import BeautifulSoup

from src.genai_model.genai_model import GenAIModel
from src.news_story import NewsStory
from src.newsletters.email import Email
from src.newsletters.parser.process_links import process_raw_url

logger = logging.getLogger(__name__)

SECTION_BREAKS = [
    "Tech Across the Globe",
    "Revalued",
    "Must read",
    "Today’s must read",
    "More from Bloomberg",
]
SPLIT_PATTERN = "\n\n"
HTML_PATTERN = r"<https://[^>]+>"


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
    for sec in SECTION_BREAKS:
        _tmp = txt.split(sec)
        if len(_tmp) == 1:
            logger.warning(
                f"Could not find keyword '{sec}' and therefore couldn't split. Skipping"
            )
            continue
        elif len(_tmp) > 2:
            logger.error(f"Should have gotten 2 pieces, instead got {len(_tmp)}.")
            logger.error(f"Original text to split: {txt}")
            raise ValueError(f"Error while splitting the text for section: '{sec}'.")
        logger.debug(f"section: {sec}, added text: {_tmp[0]}, original: {_tmp}")
        sections.append(_tmp[0])
        # Handle the last section
        if sec == "Must read" or sec == "Today’s must read":
            appended_txt = _tmp[1].lstrip().split(SPLIT_PATTERN)[0]
            logger.debug(f"Last section. Appended text is: {appended_txt}")
            sections.append(appended_txt)
            break
        else:
            txt = _tmp[1]
    sections = sections[1:]
    # Get the url's
    message = email["message"]
    for pp in message["payload"]["parts"]:
        if pp["mimeType"] == "text/html":
            body_data = pp["body"]["data"]
            text_html = base64.urlsafe_b64decode(body_data).decode()
            break
    urls = re.findall(
        r"\(https://[^\)]+\)",
        html_to_text_with_links(text_html)
        .split(SECTION_BREAKS[0])[1]
        .split(SECTION_BREAKS[-1])[0],
    )
    logger.debug(f"Found {len(urls)} url's in the article '{email['subject']}'.")
    logger.debug(f"url's: [{urls}]")
    news_stories = []
    for section in sections:
        articles = section.split(SPLIT_PATTERN)
        for art in articles:
            if "<>" in art or len(re.findall(HTML_PATTERN, art)) > 0:
                insert_url = True
            else:
                insert_url = False
            txt = art.replace("\n", "").strip()
            txt = re.sub(
                HTML_PATTERN, "", txt
            )  # remove as we've already grabbed the links before
            txt = txt.replace("<>", "")
            logger.debug(f"art '{art}' was cleaned up into '{txt}'")
            if len(txt) > 0:
                if ": " in txt:
                    txtsplit_out = txt.split(":")
                    if len(txtsplit_out) == 2:
                        title, summary = txtsplit_out
                    else:
                        logger.error(
                            f"Error in section '{section}' with article '{art} when splitting text '{txt}'"
                        )
                        raise ValueError(
                            f"Was expecting 2 entries after split according to ': ', instead got {len(txtsplit_out)}: {txtsplit_out}"
                        )
                else:
                    logger.debug(txt)
                    title_creator = GenAIModel(
                        model_type="small",
                        system_promt="You are journalist specialized in technology and artificial intelligence.",
                    )
                    title = title_creator.completion_str(
                        user_prompt=f"Create a title for a news article given a summary of that news article.\nOnly return the title and only return a single title.\nHere is the summary:\n{txt}"
                    )
                    summary = txt
                # Extract url
                if insert_url:
                    raw_url = urls.pop(0).lstrip("(").rstrip(")")
                    url, news_provider = process_raw_url(raw_url=raw_url)
                else:
                    url = ""
                    news_provider = "Not available"
                ns = NewsStory(
                    title=title.strip(),
                    url=url,
                    news_provider=news_provider,
                    source_of_the_news=email["sender"],
                    text="",
                    news_summary=summary.strip(),
                    date_source=email["date_utc"],
                    date_source_time_zone="utc",
                )
                news_stories.append(ns)
    logger.debug(
        f"Found {len(news_stories)} news stories in the article: {email['subject']}."
    )
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
