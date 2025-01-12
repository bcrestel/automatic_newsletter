import logging
from typing import Dict, List, Tuple

import pandas as pd

from src.config import CREDENTIAL_PATH, PATH_TO_ROOT, SCOPES, TOKEN_PATH
from src.news_story import NewsStory
from src.scoring.google_sheets import GoogleSheets
from src.scoring.structured_news_stories import StructuredNewsStories
from src.utils.pandas import convert_list_of_dict_to_dataframe

logger = logging.getLogger(__name__)


def runner(list_news_stories: List[NewsStory]) -> Tuple[pd.DataFrame, Dict]:
    """Convert list of news storires into a dataframe and calculate different scores

    Args:
        list_news_stories (List[NewsStory]): list of news stories, eg, as provided by src.newsletters.main.runner

    Returns:
        Tuple[pd.DataFrame, Dict]: dataframe of scored news stories, categories of themes used in scoring
    """
    # Convert the news stories to a dataframe
    logger.info(f"Converting all news stories to a structured format.")
    struc_newsstories = StructuredNewsStories(list_news_stories=list_news_stories)

    # Load the target fields
    logger.info(f"Querying the metadata tags from Google Sheets.")
    sheets = GoogleSheets(
        path_to_token=PATH_TO_ROOT / TOKEN_PATH,
        path_to_credentials=PATH_TO_ROOT / CREDENTIAL_PATH,
        scopes=SCOPES,
    )
    target_fields = sheets.get_all_tables()

    # Add metadata and calculate the score
    struc_newsstories.add_all_metadata_and_score(all_target_fields=target_fields)

    return struc_newsstories.df_news_stories, target_fields
