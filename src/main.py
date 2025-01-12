import argparse
import logging
from typing import List

from src.config import PATH_TO_DB
from src.newsletters.main import runner as runner_newsletters
from src.reporting.main import runner as runner_reporting
from src.saving.main import runner as runner_saving
from src.scoring.main import runner as runner_scoring
from src.utils.date import get_date_YYYY_MM_DD

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


def runner_from_newsstories_to_report(report_date_range: List[str], path_to_db: str):
    """Run the end-to-end pipeline from extract news stories to creating and emailing the report

    Args:
        report_date_range (List[str]): start and end date, eg ["2024-12-01", "2024-12-09"].
        Start date is set to midnight (so inclusive).
        End date is set to 23:59:59 (so inclusive too).
    """
    logger.info(
        f"Running end-to-end pipeline to create a report for range: "
        + f"{report_date_range[0]} - {report_date_range[1]}"
    )
    list_news_stories = runner_newsletters(
        after=report_date_range[0], before=report_date_range[1]
    )
    df_scored_news_stories, target_fields = runner_scoring(
        list_news_stories=list_news_stories
    )
    runner_saving(
        df_scored_news_stories_new=df_scored_news_stories, path_to_db=path_to_db
    )
    runner_reporting(
        df_scored_news_stories=df_scored_news_stories,
        target_fields=target_fields,
        report_date_range=report_date_range,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script.")
    parser.add_argument("start_date", type=str, help="YYYY-MM-DD. Inclusive")
    parser.add_argument("end_date", type=str, help="YYYY-MM-DD. Inclusive")

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date

    runner_from_newsstories_to_report(
        report_date_range=[start_date, end_date], path_to_db=PATH_TO_DB
    )


# def runner():
#    last_report_date = get_last_report_date()
#    today_date = get_date_YYYY_MM_DD()
#    day_of_the_week = get_date_of_the_week
#    if day_of_the_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
#        run_daily_report(today_date, last_report_date)
#    if day_of_the_week == "Saturday":
#        run_weekly_report(today_date)
