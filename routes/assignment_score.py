from typing import Dict

from eel import expose

from db import DBSession
from db.models import AssignmentScore
from utils.model_to_dict import model_to_dict


@expose
def get_assignment_scores() -> Dict:
    try:
        with DBSession() as session:
            assignment_scores = session.query(AssignmentScore).all()
            assignment_scores_data = [model_to_dict(score) for score in assignment_scores]
            return {"status": "success", "data": assignment_scores_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def get_assignment_score(score_id: str) -> Dict:
    try:
        with DBSession() as session:
            assignment_score = (
                session.query(AssignmentScore).filter(AssignmentScore.id == score_id).first()
            )
            if not assignment_score:
                return {"status": "error", "error": f"AssignmentScore with ID {score_id} not found"}
            assignment_score_data = model_to_dict(assignment_score)
            return {"status": "success", "data": assignment_score_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def update_assignment_score(score_id: str, score_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            assignment_score = (
                session.query(AssignmentScore).filter(AssignmentScore.id == score_id).first()
            )
            if not assignment_score:
                return {"status": "error", "error": f"AssignmentScore with ID {score_id} not found"}
            for key, value in score_data.items():
                if hasattr(assignment_score, key):
                    setattr(assignment_score, key, value)
            session.commit()
            updated_score_data = model_to_dict(assignment_score)
            return {"status": "success", "data": updated_score_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}
