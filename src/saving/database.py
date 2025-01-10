import logging

import pandas as pd

logger = logging.getLogger(__name__)
UNIQUE_ID_COL = "unique_id"


class Database:
    def __init__(self, path_to_db: str):
        self.path_to_db = path_to_db
        # Load db
        try:
            self.db = pd.read_parquet(path_to_db)
        except FileNotFoundError as e:
            logger.warning(f"Could not find {path_to_db}. Starting from scratch.")
            self.db = None

    def append_data(self, df_new: pd.DataFrame):
        if UNIQUE_ID_COL not in df_new.columns:
            self._add_unique_id_to_dataframe(df_new)
        db_new = pd.concat([self.db, df_new], axis=0, ignore_index=True)
        self._check_unique_id_in_db(db_new)
        self._update_db(db_new)

    def get_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError
        # read data from the start_date and end_date

    def _get_max_unique_id(self):
        if self.db is None:
            max_unique_id = 0
        else:
            if UNIQUE_ID_COL not in self.db.columns:
                logger.error(
                    f"Could not find the column {UNIQUE_ID_COL} in the existing database. "
                    + f"Fix this error by adding and populating a {UNIQUE_ID_COL} column manually."
                )
                raise KeyError(
                    f"Could not find the column {UNIQUE_ID_COL} in the existing database: {self.db.columns}"
                )
            max_unique_id = self.db[UNIQUE_ID_COL].max().item()
        return max_unique_id

    def _get_starting_unique_id(self):
        max_unique_id = self._get_max_unique_id()
        return 0 if max_unique_id == 0 else max_unique_id + 1

    def _add_unique_id_to_dataframe(self, df: pd.DataFrame):
        starting_unique_id = self._get_starting_unique_id()
        df[UNIQUE_ID_COL] = range(starting_unique_id, starting_unique_id + len(df))

    def _check_unique_id_in_db(self, db: pd.DataFrame):
        nb_unique_ids = len(db[UNIQUE_ID_COL].unique())
        if nb_unique_ids != len(db):
            logger.error(f"Found {nb_unique_ids} and db has {len(db)} entries.")
            raise ValueError(f"Found {nb_unique_ids} and db has {len(db)} entries.")

    def _update_db(self, db_new: pd.DataFrame):
        self.db = db_new
        self.db.to_parquet(self.path_to_db)
