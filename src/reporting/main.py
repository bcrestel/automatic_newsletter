from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from src.config import CREDENTIAL_PATH, SCOPES, TOKEN_PATH
from src.gmail import Gmail
from src.reporting.report import Report
from src.utils.io.text import load_from_text


def runner(
    report_date_range: List[str],
    target_fields: Dict,
    df_scored_news_stories: Optional[pd.DataFrame] = None,
    path_to_db: Optional[str] = None,
    debug_mode: bool = True,
) -> None:
    # Create report
    report = Report(
        df_scored_news_stories=df_scored_news_stories,
        path_to_db=path_to_db,
        target_fields=target_fields,
        score_col="score_category_count",
        report_date_range=report_date_range,
        debug_mode=debug_mode,
    )
    report_html = report.create_report()
    # Email report
    gmail_api = Gmail(
        path_to_token=TOKEN_PATH,
        path_to_credentials=CREDENTIAL_PATH,
        scopes=SCOPES,
    )
    sender = load_from_text("/home/secrets_vault/email_sender.txt").rstrip()
    recipients = load_from_text("/home/secrets_vault/email_recipients.txt").split("\n")
    subject = (
        f"Report automatic_newsletter: {report_date_range[0]} -- {report_date_range[1]}"
    )
    for recipient in recipients:
        gmail_api.send_email(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=report_html,
            email_subtype="html",
        )
