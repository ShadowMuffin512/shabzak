from sqlalchemy.orm import Session as SessionType
from db import DBSession
from db.models import AssignmentScore
from utils import enums

def init_db():
    with DBSession as session:
        set_assignment_scores(session)
        

def set_assignment_scores(session: SessionType):
    found_assignment_scores = session.query(AssignmentScore).all()
    needed_assignment_scores = set(enums.Assignment.__members__.keys())
    missing_keys = needed_assignment_scores - set([assignment.assignment for assignment in found_assignment_scores])
    for key in missing_keys:
        score = enums.DEFAULT_ASSIGNMENT_SCORES[enums.Assignment[key]]
        session.add(AssignmentScore(assignment=key, score=score))