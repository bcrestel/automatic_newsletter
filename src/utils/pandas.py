from collections import defaultdict
from typing import List

import pandas as pd


def print_dataframe_col_per_alphanumeric(df: pd.DataFrame, column: str):
    groups = defaultdict(list)
    for entry in df[column].unique():
        first_char = entry[0].upper()  # Convert to uppercase for consistent grouping
        groups[first_char].append(entry)

    # Print the grouped entries
    for first_char, entries in sorted(groups.items()):
        print(f"{first_char} ({len(entries)}): {', '.join(entries)}")


def convert_list_of_dict_to_dataframe(list_of_dict: List[dict], dict_keys: List) -> pd.DataFrame:
    list_results = [[] for _ in range(len(dict_keys))]
    for ns in list_of_dict:
        for idx, key in enumerate(dict_keys):
            try:
                res = ns[key]
            except KeyError as e:
                res = ''
            list_results[idx].append(res)
    return pd.DataFrame({key: list_results[idx] for idx, key in enumerate(dict_keys)})