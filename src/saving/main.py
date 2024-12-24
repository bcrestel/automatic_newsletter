import logging

import pandas as pd

logger = logging.getLogger(__name__)
PATH_TO_FILE = "'../../secrets_vault/scored_news_stories.parquet'"


def runner(
    df_scored_news_stories_new: pd.DataFrame, path_to_file: str = PATH_TO_FILE
) -> None:
    try:
        df_scored_news_stories_existing = pd.read_parquet(path_to_file)
        df_scored_news_stories = pd.concat(
            [df_scored_news_stories_existing, df_scored_news_stories_new],
            ignore_index=True,
        )
    except:
        logger.warning(f"Could not read {path_to_file}. Starting from scratch.")
        df_scored_news_stories = df_scored_news_stories_new
    df_scored_news_stories.to_parquet(path_to_file)
