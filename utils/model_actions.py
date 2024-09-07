from datetime import date, timedelta
from typing import Any, Callable, List, Optional

from sqlalchemy import desc

from db import DBSession
from db.models import AssignmentScore, Day, DaySoldierAssignment, Score, Soldier, Team, Timetable
from utils import enums, exceptions

orderFunc = Callable[[Any], Any]


def get_teams_from_ids(ids: List[str]) -> List[Team]:
    with DBSession() as session:
        teams = session.query(Team).filter(Team.id.in_(ids)).all()
        if len(teams) != len(ids):
            raise exceptions.NotFound(
                f'Some of the teams are missing from the IDs - {",".join(ids)}'
            )
        return teams


def get_updated_score_after_assignment_update(
    assignment: DaySoldierAssignment,
    prev_assignment: Optional[DaySoldierAssignment],
    prev_score: Score,
    is_assignment_deleted: bool,
) -> int:
    with DBSession() as session:
        assignment_score_model = (
            session.query(AssignmentScore)
            .filter(AssignmentScore.assignment == assignment.assignment)
            .first()
        )
        if not assignment_score_model:
            raise exceptions.NotFound(f"Score for assignment {assignment.assignment} not found")
        assignment_score = assignment_score_model.score
        if is_assignment_deleted:
            return prev_score.score - assignment_score
        if prev_assignment:
            prev_assignment_score_model = (
                session.query(AssignmentScore)
                .filter(AssignmentScore.assignment == prev_assignment.assignment)
                .first()
            )
            if not prev_assignment_score_model:
                raise exceptions.NotFound(f"Score for assignment {assignment.assignment} not found")
            prev_assignment_score = prev_assignment_score_model.score
            return prev_score.score - prev_assignment_score + assignment_score
        return prev_score.score + assignment_score


def get_soldiers_for_team(team: Team) -> List[Soldier]:
    with DBSession() as session:
        return session.query(Soldier).filter(Soldier.team_id == team.id).all()


def get_scores_for_team(team: Team) -> List[Score]:
    with DBSession() as session:
        return session.query(Score).filter(Score.team_id == team.id).all()


def get_existing_assignments_for_date(date: date) -> List[DaySoldierAssignment]:
    with DBSession() as session:
        day = session.query(Day).filter(Day.date == date).first()
        if day is None:
            raise exceptions.NotFound(f"No Day found for the date {date}")
        assignments = (
            session.query(DaySoldierAssignment).filter(DaySoldierAssignment.day_id == day.id).all()
        )
        return assignments


def get_assignments_for_day(day: Day) -> List[DaySoldierAssignment]:
    with DBSession() as session:
        return (
            session.query(DaySoldierAssignment).filter(DaySoldierAssignment.day_id == day.id).all()
        )


def get_soldier_from_assignment(assignment: DaySoldierAssignment) -> Soldier:
    with DBSession() as session:
        found_soldier = session.query(Soldier).filter(Soldier.id == assignment.soldier_id).first()
        if not found_soldier:
            raise exceptions.NotFound(f"Cannot find soldier with ID {assignment.soldier_id}")
        return found_soldier


def get_soldier_score_from_assignment(assignment: DaySoldierAssignment) -> Score:
    with DBSession() as session:
        return (
            session.query(Score)
            .join(Soldier)
            .join(DaySoldierAssignment)
            .filter(DaySoldierAssignment.soldier_id == assignment.soldier_id)
            .filter(Soldier.id == DaySoldierAssignment.soldier_id)
            .first()
        )


def get_assignment_scores() -> List[AssignmentScore]:
    with DBSession() as session:
        return session.query(AssignmentScore).all()


def get_timetable_for_team(team: Team) -> Timetable:
    with DBSession() as session:
        found_timetable = session.query(Timetable).filter(Timetable.team_id == team.id).first()
        if not found_timetable:
            raise exceptions.NotFound(f"Cannot find timetable for team ID {team.id}")
        return found_timetable


def get_lookback_days_from_timetable(
    timetable: Timetable, start_day: date, lookback_duration_days: int, order_func: orderFunc = desc
) -> List[Day]:
    with DBSession() as session:
        oldest_date = start_day - timedelta(days=lookback_duration_days)
        return (
            session.query(Day)
            .filter(Day.timetable_id == timetable.id, Day.created_at >= oldest_date)
            .order_by(order_func(Day.created_at))
            .all()
        )
