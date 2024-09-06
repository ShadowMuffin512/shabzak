import enum


class WeekDayType(enum.Enum):
    Weekday = "יום רגיל"
    Weekend = "יום סופש"


class Assignment(enum.Enum):
    HalfDay = "חצי יום"
    DayAndNight = "יום ולילה"
    Day = "יום"
    Morning = "בוקר"
    Afternoon = "צהריים"
    Night = "לילה"
    After = "אפטר"
    Before = "ביפור"
    GuardDuty = "שמירה"
    Sick = "גימלים"
    Holiday = "חופשה"
    Onboarding = "חפיפה"
    Tashtiot = "תשתיות"
    WeekendHome = "בבית"
    BCPHome = "רידוד"


class AssignmentLocation(enum.Enum):
    Shalar = "שלר"
    Kirya = "קריה"


DEFAULT_ASSIGNMENT_SCORES = {
    Assignment.HalfDay: 1,
    Assignment.DayAndNight: 10,
    Assignment.Day: 6,
    Assignment.Morning: 4,
    Assignment.Afternoon: 3,
    Assignment.Night: 6,
    Assignment.After: -1,
    Assignment.Before: -2,
    Assignment.GuardDuty: 10,
    Assignment.Sick: -3,
    Assignment.Holiday: -6,
    Assignment.Onboarding: 2,
    Assignment.Tashtiot: 10,
    Assignment.WeekendHome: 0,
    Assignment.BCPHome: -2,
}
