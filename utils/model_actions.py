from datetime import date, timedelta
from typing import Callable, List, Optional

from sqlalchemy import Column, desc

from db import DBSession
from db.models import AssignmentScore, Day, DaySoldierAssignment, Score, Soldier, Team, Timetable
from utils import enums, exceptions

OrderFunc = Callable[[Column], Column]


def update_score_after_assignment(score_entity: Score, assignment: enums.Assignment):
    score_for_assignment: Optional[AssignmentScore] = None
    with DBSession as session:
        score_for_assignment = (
            session.query(AssignmentScore).filter(AssignmentScore.assignment == assignment).first()
        )
        if not score_for_assignment:
            raise exceptions.NotFound(f"Cannot find assignment score for {assignment.name}")
    setattr(score_entity, "score", score_entity.score + score_for_assignment.score)


def get_soldiers_for_team(team: Team) -> List[Soldier]:
    with DBSession as session:
        return session.query(Soldier).filter(Soldier.team_id == team.id).all()


def get_scores_for_team(team: Team) -> List[Score]:
    with DBSession as session:
        return session.query(Score).filter(Score.team_id == team.id).all()


def get_existing_assignments_for_date(date: date) -> List[DaySoldierAssignment]:
    with DBSession as session:
        day = session.query(Day).filter(Day.date == date).first()
        if day is None:
            raise exceptions.NotFound(f"No Day found for the date {date}")
        assignments = (
            session.query(DaySoldierAssignment).filter(DaySoldierAssignment.day_id == day.id).all()
        )
        return assignments


def get_assignments_for_day(day: Day) -> List[DaySoldierAssignment]:
    with DBSession as session:
        return (
            session.query(DaySoldierAssignment).filter(DaySoldierAssignment.day_id == day.id).all()
        )


def get_soldier_from_assignment(assignment: DaySoldierAssignment) -> Soldier:
    with DBSession as session:
        found_soldier = session.query(Soldier).filter(Soldier.id == assignment.soldier_id).first()
        if not found_soldier:
            raise exceptions.NotFound(f"Cannot find soldier with ID {assignment.soldier_id}")
        return found_soldier


def get_assignment_scores() -> List[AssignmentScore]:
    with DBSession as session:
        return session.query(AssignmentScore).all()


def get_timetable_for_team(team: Team) -> Timetable:
    with DBSession as session:
        found_timetable = session.query(Timetable).filter(Timetable.team_id == team.id).first()
        if not found_timetable:
            raise exceptions.NotFound(f"Cannot find timetable for team ID {team.id}")
        return found_timetable


def get_lookback_days_from_timetable(
    timetable: Timetable, start_day: date, lookback_duration_days: int, order_func: OrderFunc = desc
) -> List[Day]:
    with DBSession as session:
        oldest_date = start_day - timedelta(days=lookback_duration_days)
        return (
            session.query(Day)
            .filter(Day.timetable_id == timetable.id, Day.created_at >= oldest_date)
            .order_by(order_func(Day.created_at))
            .all()
        )
