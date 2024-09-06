from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import desc
from db import DBSession
from db.models import BCPDay, BCPTimetable, Day, DaySoldierAssignment, Soldier, Team
from utils import enums

ASSIGNMENTS_ALLOWING_BCP = [
    enums.Assignment.Home,
    enums.Assignment.Morning,
    enums.Assignment.Afternoon,
    enums.Assignment.Before,
]

def calculate_bcp_days(team: Team, timetable: BCPTimetable, start_day: date, num_days: int) -> List[BCPDay]:
    calculated_days: List[BCPDay] = []
    for days_passed in range(num_days):
        day_to_calculate = start_day + timedelta(days=days_passed)
        calculated_days.append(calculate_bcp_day(team, timetable, day_to_calculate, calculated_days))
    return calculated_days


def calculate_bcp_day(
    team: Team, timetable: BCPTimetable, day_to_calculate: date, prev_days: List[BCPDay] = []
) -> BCPDay:
    one_week_ago = datetime.now() - timedelta(weeks=1)
    main_day_soldier_assignments: List[DaySoldierAssignment] = []
    eligible_soldiers: List[Soldier] = []
    soldiers_ordered_by_fairness: List[Soldier] = []
    with DBSession as session:
        prev_days += (
            session.query(BCPDay)
            .filter(BCPDay.timetable_id == timetable.id, BCPDay.created_at >= one_week_ago)
            .order_by(desc(BCPDay.created_at))
            .all()
        ) or []
        main_day = session.query(Day).filter(Day.date == day_to_calculate).first()
        if main_day:
            main_day_soldier_assignments = main_day.day_soldier_assignments
        eligible_soldiers = (
            session.query(Soldier)
            .filter(Soldier.team_id == team.id, Soldier.is_close_to_base)
            .all()
        )
    eligible_soldiers = filter_soldiers_with_allowing_assignments(
        main_day_soldier_assignments, eligible_soldiers
    )
    for bcp_day in prev_days:
        bcp_day_soldiers = [bcp_day.morning_soldier, bcp_day.night_soldier]
        soldiers_ordered_by_fairness.extend(bcp_day_soldiers)
    soldiers_ordered_by_fairness = [
        soldier for soldier in eligible_soldiers if soldier not in soldiers_ordered_by_fairness
    ] + soldiers_ordered_by_fairness
    return BCPDay(
        timetable_id=timetable.id,
        morning_solder_id=soldiers_ordered_by_fairness[1],
        night_soldier_id=soldiers_ordered_by_fairness[0],
    )


def filter_soldiers_with_allowing_assignments(
    day_soldier_assignments: List[DaySoldierAssignment], soldiers: List[Soldier]
) -> List[Soldier]:
    if not day_soldier_assignments:
        return soldiers
    soldier_assignments = {
        assignment.soldier_id: assignment for assignment in day_soldier_assignments
    }
    filtered_soldiers = []
    for soldier in soldiers:
        assignment = soldier_assignments.get(soldier.id)
        if not assignment or assignment.assignment in ASSIGNMENTS_ALLOWING_BCP:
            filtered_soldiers.append(soldier)
    return filtered_soldiers