import logging

from src.newsletters.main import runner as runner_newsletters
from src.reporting.main import runner as runner_reporting
from src.saving.main import runner as runner_saving
from src.scoring.main import runner as runner_scoring

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s -- l.%(lineno)d: %(message)s",
)


def runner():
    raise NotImplementedError
    # TODO: identify day of the week. If weekday, run daily recap (Full pipeline). If Saturday, run weekly recap (use already processed and saved news stories)
    report_date_range = ["2024-12-01", "2024-12-03"]
    news_stories = runner_newsletters(
        after=report_date_range[0], before=report_date_range[1]
    )
    df_news_stories, target_fields = runner_scoring(news_stories)
    runner_saving(df_news_stories, "log/test.parquet")
    runner_reporting(
        df_scored_news_stories=df_news_stories,
        target_fields=target_fields,
        report_date_range=report_date_range,
    )
