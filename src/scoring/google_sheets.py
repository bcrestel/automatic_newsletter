import logging
import re
from pathlib import Path
from typing import Any, Dict, List

import inflect
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.scoring.config import (
    PATH_TO_ROOT,
    PATH_TO_SPREADSHEET_ID,
    SPREADSHEET_TABS_TO_ATTR,
)
from src.utils.list import flatten_list_of_lists

PATTERN_AI = r"\b[a-zA-Z]*\s?AI\b"
PATTERN_ACRONYMS = r"\b[A-Z,.]+\b"
EXCEPTION_LIST = ["VC"]

logger = logging.getLogger(__name__)


class GoogleSheets:
    def __init__(
        self, path_to_token: Path, path_to_credentials: Path, scopes: List[str]
    ) -> None:
        self.path_to_token = path_to_token
        self.path_to_credentials = path_to_credentials
        self.scopes = scopes
        self.service = self.create_services()
        with open(PATH_TO_ROOT / PATH_TO_SPREADSHEET_ID, "r") as f:
            self.spreadsheet_id = f.readline().strip()

    def create_services(self) -> Any:
        creds = Credentials.from_authorized_user_file(
            filename=self.path_to_token, scopes=self.scopes
        )
        return build("sheets", "v4", credentials=creds)

    def get_all_tables(self) -> Dict[str, Dict[str, List[str]]]:
        tables = {}
        for tab in SPREADSHEET_TABS_TO_ATTR.keys():
            table = self.get_table(tab=tab)
            self.verify_table(tab=tab, table=table)
            tables[tab] = table
        return tables

    def get_table(self, tab: str) -> Dict[str, List[str]]:
        spreadsheet = self.service.spreadsheets()
        result = (
            spreadsheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=tab)
            .execute()
        )
        values = result.get("values", [])
        values = values[1:]  # ignore the header
        res_dict = {val[0]: val[1:] for val in values}
        # Add the plural of the words in the tab "themes"
        if tab == "themes":
            res_dict = {key: self.add_plurals(val) for key, val in res_dict.items()}
        return res_dict

    def verify_table(self, tab: str, table: Dict[str, str]) -> None:
        flat_list = flatten_list_of_lists(list(table.values()))
        if len(flat_list) != len(set(flat_list)):
            logger.error(f"Some non-unique entries were found in table {tab}")
            logger.error(
                f"len(flat_list)={len(flat_list)}, whereas len(set(flat_list))={len(set(flat_list))}"
            )
            logger.error(flat_list)
            raise ValueError(f"Non unique entries in table {tab}")

    def add_plurals(self, words: List[str]) -> List[str]:
        all_words = [self.plural(word) for word in words]
        return flatten_list_of_lists(all_words)

    def plural(self, word: str) -> List[str]:
        if word not in EXCEPTION_LIST and (
            re.fullmatch(PATTERN_AI, word) or re.fullmatch(PATTERN_ACRONYMS, word)
        ):
            return [word]
        else:
            p = inflect.engine()
            pl = p.plural(word)
            if pl == word:
                return [word]
            else:
                return [word, p.plural(word)]
