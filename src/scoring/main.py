import logging
from typing import List

import pandas as pd

from src.config import CREDENTIAL_PATH, SCOPES, TOKEN_PATH
from src.news_story import NewsStory
from src.scoring.config import PATH_TO_ROOT
from src.scoring.google_sheets import GoogleSheets
from src.scoring.structured_news_stories import StructuredNewsStories
from src.utils.pandas import convert_list_of_dict_to_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


def runner(list_news_stories: List[NewsStory]) -> pd.DataFrame:
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

    # TODO: Add metadata to df_news_stories according to target_fields

    return struc_newsstories, target_fields
