import pytest

from src.utils.io.pickle import load_from_pickle
from src.newsletters.parser.alpha_signal import alpha_signal_parser

PATH_TO_ALPHA_EMAIL = "/home/src/tests/data/email_alpha.pickle"

_parsed_email = None

def load_email():
    return load_from_pickle(PATH_TO_ALPHA_EMAIL)

def get_parsed_email():
    global _parsed_email
    if _parsed_email is None:
        _parsed_email = alpha_signal_parser(load_email())
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
    assert entry_0['title'] == "OpenAI’s Sam Altman outlines AI trends"
    #
    entry_end = parsed_email[-1]
    assert entry_end['title'] == "Automate GitHub PRs in seconds"
    #
    entry_end4 = parsed_email[-4]
    assert entry_end4['title'] == "Deploy and fine-tune DeepSeek-R1 models on AWS"
    #
    for entry in parsed_email:
        assert entry['url'].startswith("http")
        assert entry["source_of_the_news"] == "AlphaSignal <news@alphasignal.ai>"
        assert entry["date_source_time_zone"] == "utc"
        assert entry["date_source"] == "Mon, 10 Feb 2025 16:26:58 +0000"
        assert entry["news_provider"] != ""
        assert entry["news_summary"] != ""