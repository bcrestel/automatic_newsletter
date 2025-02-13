import logging
from typing import List, Tuple

from src.news_story import NewsStory
from src.utils.web.url import expand_url, remove_trackers

logger = logging.getLogger(__name__)

SPLIT_LINKS = "\r\n"


def replace_link_numbers_with_url(
    all_links: str, news_stories: List[NewsStory]
) -> None:
    """replace the link number in each of the news_stories entries and
    replace those with the actual url, according to the mapping provided in all_links

    Args:
        all_links (str): single string containing a list of link numbers
        in square brackets next to the url.
        For example,
        [1] http://www.website.com
        [2] http:///www.another_website.com
        ...
        news_stories (List[NewsStory]): List of NewsStory object,
        where the entry for 'url' is a number corresponding to the mapping in all_links.
        For example,
        NewsStory[3]["url"] = '2'
    """
    links = all_links.split(SPLIT_LINKS)
    map_ref_to_url = {}
    for ll in links:
        if ll.startswith("["):
            ref, url = ll.split("] ")
            map_ref_to_url[ref[1:]] = url
    # Map url reference number to a clean url (str):
    for ns in news_stories:
        ref_nb = ns["url"]
        raw_url = map_ref_to_url[ref_nb]
        url, news_provider = process_raw_url(raw_url=raw_url)
        ns["url"] = url
        ns["news_provider"] = news_provider


def process_raw_url(raw_url: str) -> Tuple[str, str]:
    """Takes an url, potentially shortened, masked, and/or containing tackers,
    and return its clean version (direct link to the page) and its host

    Args:
        raw_url (str): string of the url to clean up

    Returns:
        Tuple[str, str]: the clean url, the hsot of that url
    """
    try:
        expanded_url = expand_url(raw_url)
        clean_furl = remove_trackers(expanded_url)
        url = clean_furl.url
        host = clean_furl.host
    except:
        logger.warning(f"Could not process url: {raw_url}. Will keep the original one.")
        url = raw_url
        host = "Not available"
    return url, host
