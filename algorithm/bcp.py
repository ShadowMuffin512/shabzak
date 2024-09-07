from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import desc

from db import DBSession
from db.models import BCPDay, BCPTimetable, Day, DaySoldierAssignment, Soldier, Team, Timetable
from utils import enums, model_actions


class BCPEngine:
    timetable_lookback_days = 7
    assignments_allowing_bcp = [
        enums.Assignment.WeekendHome,
        enums.Assignment.Morning,
        enums.Assignment.Afternoon,
        enums.Assignment.Before,
        enums.Assignment.BCPHome,
    ]

    def __init__(self, team: Team, prev_bcp_days: List[BCPDay] = []):
        self.team: Team = team
        self.prev_bcp_days: List[BCPDay] = prev_bcp_days
        self.timetable: Timetable = model_actions.get_timetable_for_team(self.team)
        self.soldiers: List[Soldier] = BCPEngine.filter_soldiers_close_to_base(
            model_actions.get_soldiers_for_team(self.team)
        )

    @staticmethod
    def filter_soldiers_close_to_base(soldiers: List[Soldier]) -> List[Soldier]:
        return [soldier for soldier in soldiers if soldier.is_close_to_base]

    def calculate_bcp_days(self, start_day: date, num_days: int) -> List[BCPDay]:
        calculated_days: List[BCPDay] = self.prev_bcp_days
        for days_passed in range(num_days):
            day_to_calculate = start_day + timedelta(days=days_passed)
            calculated_days.append(self.calculate_bcp_day(day_to_calculate, calculated_days))
        return calculated_days

    def calculate_bcp_day(self, day_to_calculate: date, prev_bcp_days: List[BCPDay] = []) -> BCPDay:
        main_day_soldier_assignments: List[DaySoldierAssignment] = []
        eligible_soldiers: List[Soldier] = []
        soldiers_ordered_by_fairness: List[Soldier] = []
        with DBSession() as session:
            prev_bcp_days += (
                session.query(BCPDay)
                .filter(
                    BCPDay.timetable_id == self.timetable.id,
                    BCPDay.created_at >= BCPEngine.timetable_lookback_days,
                )
                .order_by(desc(BCPDay.created_at))
                .all()
            ) or []
            main_day = session.query(Day).filter(Day.date == day_to_calculate).first()
            if main_day:
                main_day_soldier_assignments = main_day.day_soldier_assignments
        eligible_soldiers = self.filter_soldiers_with_allowing_assignments(
            main_day_soldier_assignments, self.soldiers
        )
        for bcp_day in prev_bcp_days:
            bcp_day_soldiers = [bcp_day.morning_soldier, bcp_day.night_soldier]
            soldiers_ordered_by_fairness.extend(bcp_day_soldiers)
        soldiers_ordered_by_fairness = [
            soldier for soldier in eligible_soldiers if soldier not in soldiers_ordered_by_fairness
        ] + soldiers_ordered_by_fairness
        return BCPDay(
            timetable_id=self.timetable.id,
            morning_soldier_id=soldiers_ordered_by_fairness[1].id,
            night_soldier_id=soldiers_ordered_by_fairness[0].id,
        )

    def filter_soldiers_with_allowing_assignments(
        self, day_soldier_assignments: List[DaySoldierAssignment], soldiers: List[Soldier]
    ) -> List[Soldier]:
        if not day_soldier_assignments:
            return soldiers
        soldier_assignments = {
            assignment.soldier_id: assignment for assignment in day_soldier_assignments
        }
        filtered_soldiers = []
        for soldier in soldiers:
            assignment = soldier_assignments.get(soldier.id)
            if not assignment or assignment.assignment in BCPEngine.assignments_allowing_bcp:
                filtered_soldiers.append(soldier)
        return filtered_soldiers
