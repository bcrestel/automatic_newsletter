from pathlib import Path

SECRETS_VAULT_PATH = Path("/home/secrets_vault")
TOKEN_PATH = SECRETS_VAULT_PATH / Path("token.json")
CREDENTIAL_PATH = SECRETS_VAULT_PATH / Path("credentials.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

VERSION = "1.2.4"

PATH_TO_LOGS_FOLDER = Path("/home/logs")
PATH_TO_DB = PATH_TO_LOGS_FOLDER / Path("database_news_stories.parquet")
REPORT_DATE_PATH = PATH_TO_LOGS_FOLDER / Path("report_date.txt")
