from sqlalchemy.orm import Session as SessionType

from db import DBSession
from db.models import AssignmentScore
from utils import enums


def init_db():
    with DBSession() as session:
        set_assignment_scores(session)


def set_assignment_scores(session: SessionType):
    found_assignment_scores = session.query(AssignmentScore).all()
    needed_assignment_scores = set(enums.Assignment)
    existing_assignment_scores = set(
        assignment.assignment for assignment in found_assignment_scores
    )
    missing_keys = needed_assignment_scores - existing_assignment_scores
    for assignment in missing_keys:
        score = enums.DEFAULT_ASSIGNMENT_SCORES[assignment]
        session.add(AssignmentScore(assignment=assignment, score=score))
