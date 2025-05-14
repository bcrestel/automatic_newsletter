from src.config import REPORT_DATE_PATH
from src.main import runner_pipeline
from src.utils.date import add_days_str, get_date_YYYY_MM_DD
from src.utils.io.text import load_from_text, save_to_text

if __name__ == "__main__":
    """Run the main pipeline from last date found in REPORT_DATE_PATH up until TODAY, using the following default options:
        path_to_db=False,  # path_to_db=PATH_TO_DB,
        create_report=True,
        save_db=False,  # save_db=True,
        parse_news_stories=True,
    At the end, update REPORT_DATE_PATH with TODAY's date
    """
    report_date = load_from_text(REPORT_DATE_PATH).rstrip()
    last_date = report_date.split("\n")[-1]
    today_date = get_date_YYYY_MM_DD()
    start_date = add_days_str(last_date, 1)
    end_date = add_days_str(today_date, -1)
    runner_pipeline(
        report_date_range=[start_date, end_date],
        path_to_db=False,  # path_to_db=PATH_TO_DB,
        create_report=True,
        save_db=False,  # save_db=True,
        parse_news_stories=True,
    )
    save_to_text(REPORT_DATE_PATH, end_date + "\n", open_mode="a")
