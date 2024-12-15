from pathlib import Path

from src.newsletters.parser.tldr import tldr_parser

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = Path("secrets_vault/token.json")
CREDENTIAL_PATH = Path("secrets_vault/credentials.json")

NEWSLETTER_AND_PARSER = {"TLDR AI <dan@tldrnewsletter.com>": tldr_parser}
