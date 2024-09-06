from datetime import date

from utils import enums


def get_weekend_or_weekday(date: date) -> enums.WeekDayType:
    return enums.WeekDayType.Weekend if date.weekday() in [4, 5] else enums.WeekDayType.Weekday
