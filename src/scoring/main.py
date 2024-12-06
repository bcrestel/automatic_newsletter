import pandas as pd
from typing import List

from src.news_story import NewsStory
from src.utils.pandas import convert_list_of_dict_to_dataframe

def runner(list_news_stories: List[dict]) -> pd.DataFrame:
    news_stories_keys = NewsStory.__annotations__.keys()
    df_news_stories = convert_list_of_dict_to_dataframe(list_news_stories, news_stories_keys)

    return df_news_stories