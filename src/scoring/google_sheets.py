from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.scoring.config import PATH_TO_ROOT, PATH_TO_SPREADSHEET_ID, SPREADSHEET_TABS


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

    def get_all_tables(self) -> Dict[str, pd.DataFrame]:
        tables = {}
        for tab in SPREADSHEET_TABS:
            table = self.get_table(tab=tab)
            self.verify_table(tab=tab, table=table)
            tables[tab] = table
        return tables

    def get_table(self, tab: str) -> pd.DataFrame:
        spreadsheet = self.service.spreadsheets()
        result = (
            spreadsheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=tab)
            .execute()
        )
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0])

    def verify_table(self, tab: str, table: pd.DataFrame) -> None:
        if tab == "personalities":
            max_count = (
                table.apply(lambda x: (" ").join(x), axis=1).value_counts().max().item()
            )
        else:
            target_col = [col for col in table.columns if col.startswith("col")]
            max_count = (
                pd.Series(table[target_col].values.flatten())
                .value_counts(dropna=True)
                .max()
                .item()
            )
        if max_count != 1:
            raise ValueError(f"Non unique entries in table {tab}")
