from pathlib import Path

PATH_TO_ROOT = Path("/home")
TOKEN_PATH = Path("secrets_vault/token.json")
CREDENTIAL_PATH = Path("secrets_vault/credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

VERSION = "1.0"

PATH_TO_DB = "/home/logs/database_news_stories.parquet"
