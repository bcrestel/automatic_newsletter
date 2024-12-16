from typing import List

import pandas as pd

from src.config import CREDENTIAL_PATH, SCOPES, TOKEN_PATH
from src.news_story import NewsStory
from src.scoring.config import PATH_TO_ROOT
from src.scoring.google_sheets import GoogleSheets
from src.utils.pandas import convert_list_of_dict_to_dataframe


def runner(list_news_stories: List[dict]) -> pd.DataFrame:
    # Convert the news stories to a dataframe
    news_stories_keys = NewsStory.__annotations__.keys()
    df_news_stories = convert_list_of_dict_to_dataframe(
        list_news_stories, news_stories_keys
    )

    # Load the target fields
    sheets = GoogleSheets(
        path_to_token=PATH_TO_ROOT / TOKEN_PATH,
        path_to_credentials=PATH_TO_ROOT / CREDENTIAL_PATH,
        scopes=SCOPES,
    )
    target_fields = sheets.get_all_tables()

    # TODO: Add metadata to df_news_stories according to target_fields

    return df_news_stories, target_fields
