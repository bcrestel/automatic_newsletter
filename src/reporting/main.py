from typing import Dict, List

import pandas as pd

from src.reporting.report import Report


def runner(
    df_scored_news_stories: pd.DataFrame,
    target_fields: Dict,
    report_date_range: List[str],
) -> str:
    report = Report(
        df_scored_news_stories=df_scored_news_stories,
        target_fields=target_fields,
        report_date_range=report_date_range,
    )
    report_str = report.create_report()
    return report_str
