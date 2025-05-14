import logging
from typing import Any

import requests
from furl import furl
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

TRACKERS = [
    # Google Analytics: https://support.google.com/analytics/answer/10917952#zippy=%2Cin-this-article
    "utm_id",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_source_platform",
    "utm_term",
    "utm_content",
    "utm_creative_format",
    "utm_marketing_tactic",
    # Other
    "ref",
]


def expand_url(short_url: str) -> str:
    """Expand a short or re-directed url

    Args:
        short_url (str): url to be expanded

    Returns:
        str: expanded url
    """
    logger.debug(f"Expanding url: {short_url}")
    try:
        try:
            response = requests.head(short_url, allow_redirects=True, timeout=4)
        except requests.RequestException as e:
            response = requests.get(
                short_url, allow_redirects=True, stream=True, timeout=4
            )
        expanded_url = response.url
    except requests.Timeout as e:
        logger.warning(
            f"Both HEAD and GET timed out for url: {short_url}. Keeping the original url."
        )
        expanded_url = short_url
    except ConnectionError as e:
        logger.warning(
            f"requests.head failed for url {short_url}. Keeping the original url."
        )
        expanded_url = short_url
    return expanded_url


def remove_trackers(dirty_url: str) -> Any:
    """remove trackers from a given url

    Args:
        dirty_url (str): full url containing trackers

    Returns:
        Any: clean url, without trackers, in furl format
    """
    parsed_url = furl(dirty_url)
    for tracker in TRACKERS:
        parsed_url.args.pop(tracker, None)
    return parsed_url
