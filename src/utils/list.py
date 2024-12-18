from typing import Any, List


def flatten_list_of_lists(list_of_lists: List[List[Any]]) -> List[Any]:
    return [entry_ for list_ in list_of_lists for entry_ in list_]
