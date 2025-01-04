from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.config import SCOPES
from src.gmail import Gmail
from src.reporting.report import Report
from src.utils.io.text import load_from_text


def runner(
    df_scored_news_stories: pd.DataFrame,
    target_fields: Dict,
    report_date_range: List[str],
    debug_mode: bool = True,
) -> None:
    # Create report
    report = Report(
        df_scored_news_stories=df_scored_news_stories,
        target_fields=target_fields,
        report_date_range=report_date_range,
        debug_mode=debug_mode,
    )
    report_str = report.create_report()
    # Email report
    gmail_api = Gmail(
        path_to_token=Path("../../secrets_vault/token.json"),
        path_to_credentials=Path("../../secrets_vault/credentials.json"),
        scopes=SCOPES,
    )
    sender = load_from_text("../../secrets_vault/email_sender.txt").rstrip()
    recipients = load_from_text("../../secrets_vault/email_recipients.txt").split("\n")
    subject = (
        f"Report automatic_newsletter: {report_date_range[0]} -- {report_date_range[1]}"
    )
    for recipient in recipients:
        gmail_api.send_email(
            sender=sender, recipient=recipient, subject=subject, body=report_str
        )
