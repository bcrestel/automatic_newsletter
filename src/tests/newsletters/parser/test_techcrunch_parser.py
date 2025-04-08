from src.newsletters.parser.tech_crunch import tech_crunch_parser
from src.utils.io.pickle import load_from_pickle

PATH_TO_EMAIL = "/home/src/tests/data/email_techcrunch.pickle"

_parsed_email = None


def load_email():
    return load_from_pickle(PATH_TO_EMAIL)


def get_parsed_email():
    global _parsed_email
    if _parsed_email is None:
        _parsed_email = tech_crunch_parser(load_email())
    return _parsed_email


def test_parse():
    _ = get_parsed_email()


def test_check_len():
    parsed_email = get_parsed_email()
    assert len(parsed_email) == 16


def test_check_content():
    parsed_email = get_parsed_email()
    #
    entry_0 = parsed_email[0]
    assert entry_0["title"] == "Joining forces"
    #
    entry_end2 = parsed_email[-2]
    assert entry_end2["title"] == "First fund"
    #
    entry_2 = parsed_email[2]
    assert entry_2["title"] == "Going solo"
    #
    for entry in parsed_email:
        if type(entry["url"]) == str:
            assert entry["url"].startswith("http")
        else:
            for url in entry["url"]:
                assert url.startswith("http")
        assert entry["source_of_the_news"] == "TechCrunch <newsletters@techcrunch.com>"
        assert entry["date_source_time_zone"] == "utc"
        assert entry["date_source"] == "Fri, 7 Feb 2025 08:00:52 -0800"
        assert entry["news_provider"] != ""
        assert entry["news_summary"] != ""
