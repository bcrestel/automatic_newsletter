from parser.tldr import tldr_parser
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = Path("secrets_vault/token.json")

NEWSLETTER_AND_PARSER = {"TLDR AI <dan@tldrnewsletter.com>": tldr_parser}
