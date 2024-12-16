import base64
import logging
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.newsletters.email import Email
from src.utils.google import recreate_token

logger = logging.getLogger(__name__)


class Gmail:
    def __init__(
        self, path_to_token: Path, path_to_credentials: Path, scopes: List[str]
    ) -> None:
        self.path_to_token = path_to_token
        self.path_to_credentials = path_to_credentials
        self.scopes = scopes
        self.service = self.create_services()

    def create_services(self):
        creds = Credentials.from_authorized_user_file(
            filename=self.path_to_token, scopes=self.scopes
        )
        return build("gmail", "v1", credentials=creds)

    def fetch_emails(
        self, sender: str, after: str = "1900/12/31", before: str = "2100/12/31"
    ) -> List[Email]:
        logger.debug(f"Fetch email for sender {sender} from {after} until {before}.")
        query = f"after:{after} before:{before} from:{sender}"
        try:
            results = (
                self.service.users().messages().list(userId="me", q=query).execute()
            )
        except RefreshError as e:
            logger.warning("Your Google token has expired.")
            recreate_token(
                path_to_token=self.path_to_token,
                path_to_credentials=self.path_to_credentials,
                scopes=self.scopes,
            )
            self.service = self.create_services()
            results = (
                self.service.users().messages().list(userId="me", q=query).execute()
            )
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
