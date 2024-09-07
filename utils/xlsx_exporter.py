from typing import Any, Dict, List

import openpyxl
from openpyxl import styles

from db.models import Team
from utils import enums, model_actions


class XlsxExporter:

    assignmentColors = {
        enums.Assignment.After: "7fe249",
        enums.Assignment.Before: "7fe249",
        enums.Assignment.BCPHome: "ecab5d",
        enums.Assignment.WeekendHome: "ecab5d",
        enums.Assignment.GuardDuty: "afafaf",
        enums.Assignment.Tashtiot: "afafaf",
        enums.Assignment.Holiday: "ecab5d",
        enums.Assignment.Sick: "ecab5d",
        enums.Assignment.Onboarding: "739fd2",
        enums.Assignment.Day: "0c8452",
        enums.Assignment.DayAndNight: "baba42",
        enums.Assignment.HalfDay: "92ed6b",
        enums.Assignment.Morning: "7cdb64",
        enums.Assignment.Afternoon: "64dba9",
        enums.Assignment.Night: "6467db",
    }

    timetableHeaderRowColor = "a84300"
    nameColumnColor = "a84300"
    bcpRowColor = "e1bb40"

    def __init__(self, team_ids: List[str]):
        self.workbook = openpyxl.Workbook()
        self.teams: List[Team] = model_actions.get_teams_from_ids(team_ids)
        self.export_data_structure: Dict[str, Any] = {team.name: {} for team in self.teams}

    def create_worksheets(self):
        for i, team in enumerate(self.teams):
            self.workbook.create_sheet(team.name, i)
