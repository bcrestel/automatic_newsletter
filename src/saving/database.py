import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
UNIQUE_ID_COL = "unique_id"


class Database:
    def __init__(self, path_to_db: str):
        self.path_to_db = Path(path_to_db)
        try:
            self.db = pd.read_parquet(self.path_to_db)
        except FileNotFoundError as e:
            logger.warning(f"Could not find the file {self.path_to_db}.")
            logger.info(
                f"We'll also create {self.path_to_db.parent} if it doesn't exist already."
            )
            self.path_to_db.parent.mkdir(parents=True, exist_ok=True)
            self.db = None

    def append_data(self, df_new: pd.DataFrame):
        if UNIQUE_ID_COL not in df_new.columns:
            logger.info(
                f"No column {UNIQUE_ID_COL} found in df_new. Adding and populating one now."
            )
            self._add_unique_id_to_dataframe(df_new)
        db_new = pd.concat([self.db, df_new], axis=0, ignore_index=True)
        self._check_unique_id_in_db(db_new)
        self._update_db(db_new)

    def get_data_from_range_dates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Query data from database given a range of dates

        Args:
            start_date (str): Date in format YY-MM-DD
            end_date (str): Date in format YY-MM-DD

        Raises:
            NotImplementedError: doesn't work if the database contains more than one time zone

        Returns:
            pd.DataFrame: query
        """
        # Convert start_date and end_date to the time zone used in the database
        all_date_source_time_zone = self.db["date_source_time_zone"].unique()
        if len(all_date_source_time_zone) != 1:
            logger.error(
                f"Database contains news stories in multiple time zones ({all_date_source_time_zone}). That case is not implemented yet."
            )
            raise NotImplementedError
        else:
            date_source_time_zone = all_date_source_time_zone.item()
        start_date = pd.Timestamp(start_date + " 00:00", tz=date_source_time_zone)
        end_date = pd.Timestamp(end_date + " 23:59", tz=date_source_time_zone)
        # Create the mask and query
        mask_date = (start_date < self.db["date_source"]) & (
            self.db["date_source"] < end_date
        )
        return self.db[mask_date]

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
        logger.debug(f"Creating unique identifier from value {starting_unique_id}.")
        df[UNIQUE_ID_COL] = range(starting_unique_id, starting_unique_id + len(df))

    def _check_unique_id_in_db(self, db: pd.DataFrame):
        nb_unique_ids = len(db[UNIQUE_ID_COL].unique())
        if nb_unique_ids != len(db):
            logger.error(f"Found {nb_unique_ids} and db has {len(db)} entries.")
            raise ValueError(f"Found {nb_unique_ids} and db has {len(db)} entries.")
        else:
            logger.info(f"All values in the {UNIQUE_ID_COL} column are unique.")

    def _update_db(self, db_new: pd.DataFrame):
        self.db = db_new
        logger.info(f"Saving updated database to {self.path_to_db}")
        self.db.to_parquet(self.path_to_db)
