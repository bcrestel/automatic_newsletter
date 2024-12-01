import json
import logging
from pathlib import Path
from typing import Optional

from src.utils.date import get_date_YYYY_MM_DD
from src.utils.path import (
    change_permission_single_file,
    chmod_from_bottom_to_top,
    chmod_from_top_to_bottom,
    get_shasum,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s--l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


class ProtectedFolder:
    def __init__(self, root_folder: str, log_file_name: str = "log.json") -> None:
        self.root_folder = Path(root_folder)
        self.log_file_name = log_file_name

    def save_file(
        self,
        save_function: callable,
        parameters: dict,
        source: str = "",
        file_path: Optional[str] = None,
    ) -> None:
        if file_path is None:
            file_path = parameters["file_path"]
        file_path = Path(file_path)
        log_path = self.log_file_path(file_path)
        chmod_from_top_to_bottom(self.root_folder, log_path, permission=0o744)
        save_function(**parameters)
        self.add_entry_to_log(file_path=file_path, source=source)
        change_permission_single_file(file_path, permission=0o444)
        chmod_from_bottom_to_top(self.root_folder, log_path, permission=0o544)

    def log_file_path(self, file_path: Path) -> Path:
        return file_path.parent / self.log_file_name

    def add_entry_to_log(self, file_path: Path, source: str):
        log_file_path = self.log_file_path(file_path)
        if log_file_path.exists():
            with open(log_file_path, "r") as file:
                data = json.load(file)
        else:
            data = []
        logger.debug(data)

        # Create new entry for json
        with open(file_path, "r") as file:
            shasum = get_shasum(file)
        new_entry = {
            "file_name": f"{file_path.name}",
            "source": f"{source}",
            "date": f"{get_date_YYYY_MM_DD()}",
            "shasum": f"{shasum}",
        }
        data.append(new_entry)
        logger.debug(data)
        with open(log_file_path, "w") as file:
            json.dump(data, file, indent=4)

    # TODO: move chmod_* functions here after confirming they are not used anywhere else
