from pathlib import Path

TOKEN_PATH = Path("/home/secrets_vault/token.json")
CREDENTIAL_PATH = Path("/home/secrets_vault/credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

VERSION = "1.0"

PATH_TO_LOGS_FOLDER = Path("/home/logs")
PATH_TO_DB = PATH_TO_LOGS_FOLDER / Path("database_news_stories.parquet")
