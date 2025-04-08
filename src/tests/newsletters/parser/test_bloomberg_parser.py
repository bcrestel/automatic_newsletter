from src.newsletters.parser.bloomberg_tech import bloomberg_tech_parser
from src.utils.io.pickle import load_from_pickle

PATH_TO_EMAIL = "/home/src/tests/data/email_bloomberg.pickle"

_parsed_email = None


def load_email():
    return load_from_pickle(PATH_TO_EMAIL)


def get_parsed_email():
    global _parsed_email
    if _parsed_email is None:
        _parsed_email = bloomberg_tech_parser(load_email())
    return _parsed_email


def test_parse():
    _ = get_parsed_email()


def test_check_len():
    parsed_email = get_parsed_email()
    assert len(parsed_email) == 5


def test_check_content():
    parsed_email = get_parsed_email()
    #
    entry_0 = parsed_email[0]
    assert entry_0["title"] == "New iPads"
    #
    entry_1 = parsed_email[1]
    assert entry_1["title"] == "French satellites"
    #
    entry_2 = parsed_email[2]
    assert entry_2["title"] == "Tencent on top"
    #
    entry_end = parsed_email[-1]
    assert (
        entry_end["url"]
        == "https://www.bloomberg.com/news/articles/2025-03-05/trump-calls-for-end-to-52-billion-chips-act-subsidy-program?cmpid=tech-in-brief"
    )
    #
    for entry in parsed_email:
        assert entry["url"].startswith("http")
        assert (
            entry["source_of_the_news"]
            == "Bloomberg Technology <noreply@news.bloomberg.com>"
        )
        assert entry["date_source_time_zone"] == "utc"
        assert entry["date_source"] == "Wed, 05 Mar 2025 13:08:45 +0000"
        assert entry["news_provider"] == "www.bloomberg.com"
        assert entry["news_summary"] != ""
