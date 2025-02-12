import argparse
import logging
from typing import List

from src.config import PATH_TO_DB
from src.newsletters.main import runner as runner_newsletters
from src.reporting.main import runner as runner_reporting
from src.saving.main import runner as runner_saving
from src.scoring.main import runner as runner_scoring

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)
logger = logging.getLogger(__name__)


def runner_pipeline(
    report_date_range: List[str],
    path_to_db: str,
    create_report: bool,
    save_db: bool,
    parse_news_stories: bool,
):
    """Run the end-to-end pipeline from extract news stories to creating and emailing the report

    Args:
        report_date_range (List[str]): start and end date, eg ["2024-12-01", "2024-12-09"].
            Start date is set to midnight (so inclusive).
            End date is set to 23:59:59 (so inclusive too).
        path_to_db (str): path to database where news stories are logged
        create_report (bool): if True, will create a report
        save_db (bool): if True, will save to db (at path_to_db)
        parse_news_stories (bool): if True, will fetch and parse new newstories
    """
    if not parse_news_stories and not create_report:
        logger.warning(
            "You need to select at least --parse_news_stories or --create_report. "
            + "Since both are set to False, no action will be taken."
        )
    else:
        logger.info(
            f"Running pipeline for the time period: "
            + f"{report_date_range[0]} - {report_date_range[1]}"
        )
    if parse_news_stories:
        logger.info("Parsing newsletters for that time period")
        list_news_stories = runner_newsletters(
            after=report_date_range[0], before=report_date_range[1]
        )
        logger.info("Scoring all collected news stories")
        df_scored_news_stories, target_fields = runner_scoring(
            list_news_stories=list_news_stories
        )
        if save_db:
            logger.info("Saving scored news stories to db")
            runner_saving(
                df_scored_news_stories_new=df_scored_news_stories, path_to_db=path_to_db
            )
    if create_report:
        logger.info("Creating and sending report")
        if parse_news_stories:
            runner_reporting(
                df_scored_news_stories=df_scored_news_stories,
                target_fields=target_fields,
                report_date_range=report_date_range,
            )
        else:
            runner_reporting(
                path_to_db=path_to_db,
                target_fields=target_fields,
                report_date_range=report_date_range,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze news sources and automatically create a newsletter."
    )
    parser.add_argument(
        "--start_date",
        required=True,
        type=str,
        help="Start date in format 'YYYY-MM-DD' (Inclusive)",
    )
    parser.add_argument(
        "--end_date",
        required=True,
        type=str,
        help="End date in format 'YYYY-MM-DD' (Inclusive)",
    )
    parser.add_argument(
        "--parse_news_stories",
        action="store_true",
        help="If True, will query new data for the range of dates specified, "
        + "parse the news stories, and score them",
    )
    parser.add_argument(
        "--save_db",
        action="store_true",
        help="If True, will save to the database. "
        + "Only works if we also have 'parse_news_stories' set to True",
    )
    parser.add_argument(
        "--create_report", action="store_true", help="If True, will create a report"
    )

    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    create_report = args.create_report
    save_db = args.save_db
    parse_news_stories = args.parse_news_stories
    if save_db and not parse_news_stories:
        logger.warning(
            f"save_db will be inactive as parse_news_stories was set to False"
        )
        save_db = False

    runner_pipeline(
        report_date_range=[start_date, end_date],
        path_to_db=PATH_TO_DB,
        create_report=create_report,
        save_db=save_db,
        parse_news_stories=parse_news_stories,
    )
