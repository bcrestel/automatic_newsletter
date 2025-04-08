from src.newsletters.parser.tldr import tldr_parser
from src.utils.io.pickle import load_from_pickle

PATH_TO_EMAIL = "/home/src/tests/data/email_tldr.pickle"

_parsed_email = None


def load_email():
    return load_from_pickle(PATH_TO_EMAIL)


def get_parsed_email():
    global _parsed_email
    if _parsed_email is None:
        _parsed_email = tldr_parser(load_email())
    return _parsed_email


def test_parse():
    _ = get_parsed_email()


def test_check_len():
    parsed_email = get_parsed_email()
    assert len(parsed_email) == 11


def test_check_content():
    parsed_email = get_parsed_email()
    #
    entry_0 = parsed_email[0]
    assert entry_0["title"] == "OPENAI O1 SYSTEM CARD"
    #
    entry_end = parsed_email[-1]
    assert (
        entry_end["title"]
        == "SAM ALTMAN SAYS ARTIFICIAL GENERAL INTELLIGENCE IS ON THE HORIZON"
    )
    #
    entry_end4 = parsed_email[-4]
    assert entry_end4["title"] == "OPENAI PARTNERS WITH ANDURIL"
    #
    for entry in parsed_email:
        assert entry["url"].startswith("http")
        assert entry["source_of_the_news"] == "TLDR AI <dan@tldrnewsletter.com>"
        assert entry["date_source_time_zone"] == "utc"
        assert entry["date_source"] == "Fri, 6 Dec 2024 14:16:24 +0000"
        assert entry["news_provider"] != ""
        assert entry["news_summary"] != ""
