from typing import Any


def save_to_text(file_path: str, content: Any, open_mode: str = "w") -> None:
    with open(file_path, open_mode) as file:
        file.write(content)


def load_from_text(file_path: str) -> Any:
    with open(file_path, "r") as file:
        data = file.read()
    return data
