from datetime import date
from typing import List, Optional
from db.models import AssignmentScore, Day, DaySoldierAssignment, Score
from utils import enums, exceptions
from db import DBSession

def update_score_after_assignment(score_entity: Score, assignment: enums.Assignment):
    score_for_assignment: Optional[AssignmentScore] = None
    with DBSession as session:
        score_for_assignment = session.query(AssignmentScore).filter(AssignmentScore.assignment == assignment).first()
        if not score_for_assignment:
            raise exceptions.NotFound(f'Cannot find assignment score for {assignment.name}')
    setattr(score_entity, 'score', score_entity.score + score_for_assignment.score)

def get_existing_assignments_for_date(date: date) -> List[DaySoldierAssignment]:
    with DBSession as session:
        day = session.query(Day).filter(Day.date == date).first()
        if day is None:
            raise exceptions.NotFound(f"No Day found for the date {date}")
        assignments = session.query(DaySoldierAssignment).filter(DaySoldierAssignment.day_id == day.id).all()
        return assignments
    
def get_assignment_scores() -> List[AssignmentScore]:
    with DBSession as session:
        return session.query(AssignmentScore).all()