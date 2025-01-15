from datetime import datetime, timedelta

DATE_STR_FORMAT = "%Y-%m-%d"


def get_date_YYYY_MM_DD():
    now = datetime.now()
    return convert_datetime_to_YYYY_MM_DD(now)


def convert_datetime_to_YYYY_MM_DD(date: datetime) -> str:
    return date.strftime(DATE_STR_FORMAT)


def add_days(date: datetime, nb_days: int) -> datetime:
    return date + timedelta(days=nb_days)


def add_days_str(date: str, nb_days: int) -> str:
    _date = datetime.strptime(date, DATE_STR_FORMAT)
    _date_shifted = add_days(date=_date, nb_days=nb_days)
    return convert_datetime_to_YYYY_MM_DD(_date_shifted)
