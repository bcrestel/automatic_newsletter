import logging

import pandas as pd

logger = logging.getLogger(__name__)

# TODO: review PATH_TO_FILE. Could be log/ folder at root, and that folder is mounted in the docker file
PATH_TO_FILE = "'../../secrets_vault/scored_news_stories.parquet'"
UNIQUE_ID_COL = "unique_id"


def runner(
    df_scored_news_stories_new: pd.DataFrame, path_to_file: str = PATH_TO_FILE
) -> None:
    """Add unique_id to df_scored_news_stories_new and add to existing db (if any)

    Args:
        df_scored_news_stories_new (pd.DataFrame): current dataframe of news stories
        path_to_file (str, optional): path to the existing db. Defaults to PATH_TO_FILE.

    Raises:
        KeyError: if existing database doesn't have unique_id column. This needs to be fixed manually.
    """
    # Load existing db
    try:
        df_scored_news_stories_existing = pd.read_parquet(path_to_file)
    except FileNotFoundError as e:
        logger.warning(f"Could not find {path_to_file}. Starting from scratch.")
        df_scored_news_stories_existing = None
    # Add a unique identifier to the next dataframe
    if df_scored_news_stories_existing is None:
        start_unique_id = 0
    else:
        if UNIQUE_ID_COL not in df_scored_news_stories_existing.columns:
            logger.error(
                f"Could not find column in {UNIQUE_ID_COL} in existing dataframe. "
                + f"Therefore, cannot create a {UNIQUE_ID_COL} for the new data. "
                + f"Fix this by adding and populating a {UNIQUE_ID_COL} column in {PATH_TO_FILE}."
            )
            raise KeyError(
                f"Could not find column {UNIQUE_ID_COL} in existing dataframe: {df_scored_news_stories_existing.columns}"
            )
        start_unique_id = (
            df_scored_news_stories_existing[UNIQUE_ID_COL].max().item() + 1
        )
    df_scored_news_stories_new[UNIQUE_ID_COL] = range(
        start_unique_id, start_unique_id + len(df_scored_news_stories_new)
    )
    # Combine new and existing dataframes
    df_scored_news_stories = pd.concat(
        [df_scored_news_stories_existing, df_scored_news_stories_new],
        axis=0,
        ignore_index=True,
    )
    df_scored_news_stories.to_parquet(path_to_file)
