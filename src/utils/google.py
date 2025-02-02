import logging
import os
import shutil
from pathlib import Path
from typing import List

from google_auth_oauthlib.flow import InstalledAppFlow

from src.utils.date import get_date_YYYY_MM_DD

logger = logging.getLogger(__name__)


def recreate_token(path_to_token: str, path_to_credentials: str, scopes: List[str]):
    logger.info(f"Replacing Google token in {path_to_token} with a new one.")
    # move existing token (if it exists) to delete folder
    path_to_delete_folder = Path(os.path.dirname(path_to_token), "delete")
    if not os.path.isdir(path_to_delete_folder):
        path_to_delete_folder.mkdir(parents=True, exist_ok=False)
    try:
        dest_path = Path(path_to_delete_folder, f"token_{get_date_YYYY_MM_DD()}.json")
        shutil.move(path_to_token, dest_path)
        logger.info(f"Moved old token {path_to_token} to {dest_path}")
    except FileNotFoundError as e:
        logger.warning(
            f"File {path_to_token} does not exist. Skipping the step to move the old token."
        )
    # re-create new token
    flow = InstalledAppFlow.from_client_secrets_file(path_to_credentials, scopes)
    creds = flow.run_local_server(port=8080, bind_addr="0.0.0.0", open_browser=False)
    with open(path_to_token, "w") as token:
        token.write(creds.to_json())
        logger.info(f"Wrote new token at {path_to_token}")
