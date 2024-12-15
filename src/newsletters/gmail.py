import os
import shutil
import base64
import logging
from pathlib import Path
from typing import List, TypedDict

from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from src.newsletters.config import SCOPES, TOKEN_PATH, CREDENTIAL_PATH
from src.newsletters.email import Email
from src.utils.date import get_date_YYYY_MM_DD

PATH_TO_ROOT = Path("../..")

logger = logging.getLogger(__name__)


class Gmail:
    def __init__(self) -> None:
        self.path_to_token = PATH_TO_ROOT / TOKEN_PATH
        self.service = self.create_services(path_to_token=self.path_to_token, scopes=SCOPES)

    @staticmethod
    def create_services(path_to_token: str, scopes: str):
        creds = Credentials.from_authorized_user_file(filename=path_to_token, scopes=scopes)
        return build("gmail", "v1", credentials=creds)

    def fetch_emails(
        self, sender: str, after: str = "1900/12/31", before: str = "2100/12/31"
    ) -> List[Email]:
        logger.debug(f"Fetch email for sender {sender} from {after} until {before}.")
        query = f"after:{after} before:{before} from:{sender}"
        try:
            results = self.service.users().messages().list(userId="me", q=query).execute()
        except RefreshError as e:
            logger.warning("Your Google token has expired. We'll create a new one.")
            path_to_credentials = PATH_TO_ROOT / CREDENTIAL_PATH
            self.recreate_token(path_to_token=self.path_to_token, path_to_credentials=path_to_credentials, scopes=SCOPES)
            self.service = self.create_services(path_to_token=self.path_to_token, scopes=SCOPES)
            results = self.service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        emails = [
            self.create_email_from_message(message=message) for message in messages
        ]
        return [email for email in emails if email["sender"] == sender]

    def create_email_from_message(self, message: dict) -> Email:
        email_id = message["id"]
        message = (
            self.service.users().messages().get(userId="me", id=email_id).execute()
        )
        headers = message["payload"]["headers"]
        return Email(
            sender=next(
                header["value"] for header in headers if header["name"] == "From"
            ),
            subject=next(
                header["value"] for header in headers if header["name"] == "Subject"
            ),
            date_utc=next(
                header["value"] for header in headers if header["name"] == "Date"
            ),
            id=email_id,
            text=self.get_text_from_message(message=message),
        )

    def get_text_from_message(self, message: dict) -> str:
        mimeType = message["payload"]["mimeType"]
        if mimeType == "multipart/alternative":
            # for a multipart email, look for the plain text part
            for pp in message["payload"]["parts"]:
                if pp["mimeType"] == "text/plain":
                    body_data = pp["body"]["data"]
                    return base64.urlsafe_b64decode(body_data).decode()
        elif mimeType == "text/plain":
            body_data = message["payload"]["body"]["data"]
            return base64.urlsafe_b64decode(body_data).decode()
        elif mimeType == "text/html":
            body_data = message["payload"]["body"]["data"]
            text_html = base64.urlsafe_b64decode(body_data).decode()
            return BeautifulSoup(text_html, "html.parser").get_text()
        else:
            headers = message["payload"]["headers"]
            sender = next(
                header["value"] for header in headers if header["name"] == "From"
            )
            subject = next(
                header["value"] for header in headers if header["name"] == "Subject"
            )
            date_utc = next(
                header["value"] for header in headers if header["name"] == "Date"
            )
            email_id = message["id"]
            logger.error(
                f"email {email_id}, from: {sender}, with subject: {subject}, sent on {date_utc} has mimeType: {mimeType}"
            )
            raise NotImplementedError

    @staticmethod
    def recreate_token(path_to_token: str, path_to_credentials: str, scopes: list[str]):
        # move existing token to delete folder
        path_to_delete_folder = Path(os.path.dirname(path_to_token), "delete")
        if not os.path.isdir(path_to_delete_folder):
            path_to_delete_folder.mkdir(parents=True, exist_ok=False)
        shutil.move(path_to_token, Path(path_to_delete_folder, f"token_{get_date_YYYY_MM_DD()}.json"))
        # re-create new token
        flow = InstalledAppFlow.from_client_secrets_file(path_to_credentials, scopes)
        creds = flow.run_local_server(port=8080, bind_addr='0.0.0.0')
        with open(path_to_token, "w") as token:
            token.write(creds.to_json())