from collections import defaultdict
from typing import List

import pandas as pd


def print_dataframe_col_per_alphanumeric(df: pd.DataFrame, column: str) -> None:
    """
    Groups and prints unique values from a specified column of a Pandas DataFrame
    based on their first alphanumeric character.

    Each group is displayed with its uppercase alphanumeric character, the count
    of items in the group, and the grouped entries themselves.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the column to process.
    column : str
        The name of the column whose unique values will be grouped and printed.

    Returns:
    --------
    None
        This function prints the results to the console and does not return a value.

    Example:
    --------
    >>> import pandas as pd
    >>> data = {'names': ['Alice', 'Bob', 'Charlie', 'Anna', 'Brian']}
    >>> df = pd.DataFrame(data)
    >>> print_dataframe_col_per_alphanumeric(df, 'names')
    A (2): Alice, Anna
    B (2): Bob, Brian
    C (1): Charlie
    """
    groups = defaultdict(list)
    for entry in df[column].unique():
        first_char = entry[0].upper()  # Convert to uppercase for consistent grouping
        groups[first_char].append(entry)

    # Print the grouped entries
    for first_char, entries in sorted(groups.items()):
        print(f"{first_char} ({len(entries)}): {', '.join(entries)}")


def convert_list_of_dict_to_dataframe(
    list_of_dict: List[dict], dict_keys: List
) -> pd.DataFrame:
    """
    Converts a list of dictionaries into a Pandas DataFrame using a specified set of keys.

    Each dictionary in the input list is processed, and the specified keys are used to populate
    the columns of the resulting DataFrame. Missing keys in a dictionary will result in an
    empty string for the corresponding column.

    Parameters:
    -----------
    list_of_dict : List[dict]
        The list of dictionaries to convert into a DataFrame.
    dict_keys : List
        The list of keys to extract from each dictionary to form the columns of the DataFrame.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each column corresponds to a key from `dict_keys`, and each row
        corresponds to a dictionary from `list_of_dict`.

    Example:
    --------
    >>> list_of_dict = [
    ...     {"name": "Alice", "age": 25},
    ...     {"name": "Bob", "age": 30, "city": "New York"},
    ...     {"name": "Charlie", "city": "Los Angeles"}
    ... ]
    >>> dict_keys = ["name", "age", "city"]
    >>> convert_list_of_dict_to_dataframe(list_of_dict, dict_keys)
          name   age           city
    0    Alice    25
    1      Bob    30     New York
    2  Charlie         Los Angeles
    """
    list_results = [[] for _ in range(len(dict_keys))]
    for ns in list_of_dict:
        for idx, key in enumerate(dict_keys):
            try:
                res = ns[key]
            except KeyError as e:
                res = ""
            list_results[idx].append(res)
    return pd.DataFrame({key: list_results[idx] for idx, key in enumerate(dict_keys)})
