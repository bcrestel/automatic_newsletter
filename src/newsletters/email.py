from typing import TypedDict


class Email(TypedDict):
    sender: str
    subject: str
    date_utc: str
    id: str
    text: str
