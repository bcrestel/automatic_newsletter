import logging

import pandas as pd

logger = logging.getLogger(__name__)
PATH_TO_DB = "'../../secrets_vault/scored_news_stories.parquet'"
UNIQUE_ID_COL = "unique_id"


class Database:
    def __init__(self, path_to_db: str = PATH_TO_DB):
        self.path_to_db = path_to_db
        # Load db
        try:
            self.db = pd.read_parquet(path_to_db)
        except FileNotFoundError as e:
            logger.warning(f"Could not find {path_to_db}. Starting from scratch.")
            self.db = None
    
    def get_max_unique_id(self):
        if self.db is None:
            max_unique_id = 0
        else:
            if UNIQUE_ID_COL not in self.db.columns:
                logger.error(
                    f"Could not find column in {UNIQUE_ID_COL} in existing dataframe. "
                    + f"Therefore, cannot create a {UNIQUE_ID_COL} for the new data. "
                    + f"Fix this by adding and populating a {UNIQUE_ID_COL} column in {PATH_TO_DB}."
                )
                raise KeyError(
                    f"Could not find column {UNIQUE_ID_COL} in existing dataframe: {self.db.columns}"
                )
            max_unique_id = (
                self.db[UNIQUE_ID_COL].max().item()
            )
        return max_unique_id
    
    def get_starting_unique_id(self):
        max_unique_id = self.get_max_unique_id()
        if max_unique_id == 0:
            starting_id = 0
        else:
            starting_id = max_unique_id + 1
        return starting_id
    
    def append_data(self, df_new: pd.DataFrame): 
        if UNIQUE_ID_COL not in df_new.columns:
            self.add_unique_id_to_dataframe(df_new)
        db_new = pd.concat([self.db, df_new], axis=0, ignore_index=True)
        self.check_unique_id_in_db(db_new)
        self.update_db(db_new)
    
    def add_unique_id_to_dataframe(self, df: pd.DataFrame):
        starting_unique_id = self.get_starting_unique_id()
        df[UNIQUE_ID_COL] = range(
            starting_unique_id, starting_unique_id + len(df)
        )
    
    def check_unique_id_in_db(self, db: pd.DataFrame):
        nb_unique_ids = len(db[UNIQUE_ID_COL].unique())
        if nb_unique_ids != len(db):
            logger.error(f"Found {nb_unique_ids} and db has {len(db)} entries.")
            raise ValueError(f"Found {nb_unique_ids} and db has {len(db)} entries.")

    def update_db(self, db_new: pd.DataFrame):
        self.db = db_new
        self.db.to_parquet(self.path_to_db)