from typing import Dict

from eel import expose

from db import DBSession
from db.models import Score, Soldier
from utils.model_to_dict import model_to_dict


@expose
def get_scores_for_team(team_id: str) -> Dict:
    try:
        with DBSession() as session:
            scores = session.query(Score).join(Soldier).filter(Soldier.team_id == team_id).all()
            scores_data = [model_to_dict(score) for score in scores]
            return {"status": "success", "data": scores_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def get_score_for_soldier(soldier_id: str) -> Dict:
    try:
        with DBSession() as session:
            score = session.query(Score).join(Soldier).filter(Soldier.id == soldier_id).first()
            if not score:
                return {
                    "status": "error",
                    "error": f"Score for soldier with ID {soldier_id} not found",
                }
            score_data = model_to_dict(score)
            return {"status": "success", "data": score_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def override_score_for_soldier(soldier_id: str, new_score: int) -> Dict:
    try:
        with DBSession() as session:
            score = session.query(Score).join(Soldier).filter(Soldier.id == soldier_id).first()
            if not score:
                return {
                    "status": "error",
                    "error": f"Score for soldier with ID {soldier_id} not found",
                }
            setattr(score, "score", new_score)
            session.commit()
            return {"status": "success", "data": score}
    except Exception as e:
        return {"status": "error", "error": str(e)}
