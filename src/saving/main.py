import logging
from pathlib import Path

import pandas as pd

from src.saving.database import Database

logger = logging.getLogger(__name__)
# TODO: review PATH_TO_DB. Could be log/ folder at root, and that folder is mounted in the docker file


def runner(df_scored_news_stories_new: pd.DataFrame, path_to_db: Path) -> None:
    """Add unique_id to df_scored_news_stories_new and add to existing db (if any)

    Args:
        df_scored_news_stories_new (pd.DataFrame): current dataframe of news stories
        path_to_db (Path): path to the existing db. Defaults to PATH_TO_DB.

    Raises:
        KeyError: if existing database doesn't have unique_id column. This needs to be fixed manually.
    """
    db = Database(path_to_db=path_to_db)
    db.append_data(df_new=df_scored_news_stories_new)
