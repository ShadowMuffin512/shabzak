from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
from sqlalchemy import desc
from db.models import (
    Team,
    Soldier,
    DaySoldierAssignment,
    Timetable,
    Day,
    Score,
    BCPDay,
    AssignmentScore,
)
from db import DBSession
from utils import enums, model_actions

SCORE_LIMIT = 20

ASSIGNMENTS_CONTAINING_OTHERS = {
    enums.Assignment.DayAndNight: [
        enums.Assignment.Day,
        enums.Assignment.Afternoon,
        enums.Assignment.Night,
        enums.Assignment.Morning,
    ],
    enums.Assignment.Day: [enums.Assignment.Morning, enums.Assignment.Afternoon],
}
STARTING_ASSIGNMENTS_TO_FILL = {
    enums.WeekDayTypes.Weekday: [
        enums.Assignment.Morning,
        enums.Assignment.Afternoon,
        enums.Assignment.Night,
    ],
    enums.WeekDayTypes.Weekend: [enums.Assignment.Day, enums.Assignment.Night],
}
DEFAULT_ASSIGNMENT = enums.Assignment.Morning
COMMANDER_DISALLOWED_ASSIGNMENTS = [
    enums.Assignment.Night,
    enums.Assignment.DayAndNight,
    enums.Assignment.Onboarding,
    enums.Assignment.Afternoon,
]


def calculate_main_days(
    team: Team, timetable: Timetable, start_date: date, num_days: int
) -> List[Day]:
    calculated_days: List[Day] = []
    updated_scores: List[Score] = []
    assignment_scores = model_actions.get_assignment_scores()
    for days_passed in range(num_days):
        date_to_calculate = start_date + timedelta(days=days_passed)
        locked_assignments = model_actions.get_existing_assignments_for_date(date_to_calculate)
        calculated_day = calculate_main_day(
            assignment_scores, team, timetable, date_to_calculate, calculated_days, locked_assignments, updated_scores
        )
        calculated_days.append(calculated_day["new_day"])
        updated_scores = calculated_day["updated_scores"]
    return calculated_days


def calculate_main_day(
    assignment_scores: List[AssignmentScore],
    team: Team,
    timetable: Timetable,
    date_to_calculate: date,
    prev_days: List[Day] = [],
    locked_assignments: List[DaySoldierAssignment] = [],
    scores: List[Score] = [],
) -> Dict:
    one_week_ago = datetime.now() - timedelta(weeks=1)
    soldiers: List[Soldier] = []
    assignments_to_fill = filter_preexisting_assignments(
        STARTING_ASSIGNMENTS_TO_FILL[get_weekend_or_weekday(date_to_calculate)], locked_assignments
    )
    created_assignments = []

    with DBSession() as session:
        prev_days += (
            session.query(Day)
            .filter(Day.timetable_id == timetable.id, Day.created_at >= one_week_ago)
            .order_by(desc(Day.created_at))
            .all()
        )

        soldiers = session.query(Soldier).filter(Soldier.team_id == team.id).all()
        scores = (
            scores
            or session.query(Score)
            .filter(Score.soldier_id.in_([soldier.id for soldier in soldiers]))
            .all()
        )

    # Assignments and score updates
    for soldier in soldiers:
        assignment = calculate_day_assignment_for_soldier(
            assignment_scores, team, soldier, scores, assignments_to_fill, locked_assignments
        )
        # Update the score based on the assignment
        model_actions.update_score_after_assignment(
            get_score_for_soldier(scores, soldier), enums.Assignment[assignment.assignment]
        )
        created_assignments.append(assignment)

    return {
        "new_day": Day(
            date=date_to_calculate,
            timetable=timetable,
            timetable_id=timetable.id,
            day_soldier_assignments=created_assignments,
        ),
        "updated_scores": scores,
    }


def get_weekend_or_weekday(date: date) -> enums.WeekDayTypes:
    return enums.WeekDayTypes.Weekend if date.weekday() in [4, 5] else enums.WeekDayTypes.Weekday


def get_score_for_soldier(scores: List[Score], soldier: Soldier) -> Score:
    return next(score for score in scores if score.soldier_id == soldier.id)


def filter_preexisting_assignments(
    assignments_to_fill: List[enums.Assignment], filled_assignments: List[DaySoldierAssignment]
) -> List[enums.Assignment]:
    filled_assignment_names: List[enums.Assignment] = [
        enums.Assignment[assignment.assignment] for assignment in filled_assignments
    ]
    for filled_assignment in filled_assignment_names:
        filled_assignment_names.extend(ASSIGNMENTS_CONTAINING_OTHERS.get(filled_assignment, []))
    return [item for item in assignments_to_fill if item not in filled_assignment_names]


def calculate_day_assignment_for_soldier(
    last_night_soldier: Soldier,
    consecutive_nights: int,
    assignment_scores: List[AssignmentScore],
    team: Team,
    soldier: Soldier,
    scores: List[Score],
    assignments_to_fill: List[enums.Assignment],
    locked_assignments: List[DaySoldierAssignment] = [],
) -> DaySoldierAssignment:
    if soldier.id in [assignment.soldier_id for assignment in locked_assignments]:
        return next(
            assignment for assignment in locked_assignments if assignment.soldier_id == soldier.id
        )
    selected_assignnment: enums.Assignment = DEFAULT_ASSIGNMENT
    sorted_scoretable = sorted(scores, key=lambda score: score.score)
    prospective_score = get_score_for_soldier(scores, soldier)
    allowed_assignments_for_soldier = [
        assignment for assignment in enums.Assignment
        if (soldier.is_commander and assignment not in COMMANDER_DISALLOWED_ASSIGNMENTS) or not soldier.is_commander
    ]
    if (team.min_consecutive_nights > consecutive_nights and last_night_soldier.id == soldier.id):
        selected_assignnment = enums.Assignment.Night
    else:
        
    prospective_score += next([score for score in assignment_scores if score.assigmnent == enums.Assignment.Night]).score
    
    return DaySoldierAssignment(
        soldier_id=soldier.id,
        assignment=selected_assignnment.name
    )
