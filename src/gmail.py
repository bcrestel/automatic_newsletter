import base64
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
        self.service = self._create_services()

    def fetch_emails(
        self, sender: str, after: str = "1900-12-31", before: str = "2100-12-31"
    ) -> List[Email]:
        """Fetch emails from the gmail server

        Args:
            sender (str): fetch emails for that sender only
            after (str, optional): Starting date of the range of emails, in format YYYY-MM-DD, understood at midnight in local time zone. Defaults to "1900-12-31".
            before (str, optional): Ending date of the range of emails, in format YYYY-MM-DD, understood at 23:59:59 in local time zone. Defaults to "2100-12-31".
            The timezone for after/before may be PST at midnight (https://developers.google.com/gmail/api/guides/filtering). But clearly, the email dates are in UTC.

        Returns:
            List[Email]: list of Email objects
        """
        logger.debug(f"Fetch email for sender {sender} from {after} until {before}.")
        after_int = self._convert_to_unix_time(after + " 00:00:00")
        before_int = self._convert_to_unix_time(before + " 23:59:59")
        query = f"after:{after_int} before:{before_int} from:{sender}"
        try:
            results = self._get_messages(query=query)
        except RefreshError as e:
            logger.warning("Your Google token has expired.")
            recreate_token(
                path_to_token=self.path_to_token,
                path_to_credentials=self.path_to_credentials,
                scopes=self.scopes,
            )
            self.service = self._create_services()
            results = self._get_messages(query=query)
        messages = results.get("messages", [])
        emails = [
            self._create_email_from_message(message=message) for message in messages
        ]
        return [email for email in emails if email["sender"] == sender]

    def send_email(self, sender: str, recipient: str, subject: str, body: str) -> None:
        # Create the message
        message = MIMEMultipart()
        message["to"] = recipient
        message["from"] = sender
        message["subject"] = subject

        # Attach the body as text
        msg = MIMEText(body)
        message.attach(msg)

        # Encode the message to base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        try:
            message = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )
            logger.info(f'Message {subject} sent; message ID: {message["id"]}')
        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    def _convert_to_unix_time(self, date_time: str) -> int:
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())

    def _get_messages(self, query: str):
        return self.service.users().messages().list(userId="me", q=query).execute()

    def _create_services(self):
        creds = Credentials.from_authorized_user_file(
            filename=self.path_to_token, scopes=self.scopes
        )
        return build("gmail", "v1", credentials=creds)

    def _create_email_from_message(self, message: dict) -> Email:
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
            text=self._get_text_from_message(message=message),
        )

    def _get_text_from_message(self, message: dict) -> str:
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
                f"email {email_id}, from: {sender}, with subject: "
                + f"{subject}, sent on {date_utc} has mimeType: {mimeType}"
            )
            raise NotImplementedError
