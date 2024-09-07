from copy import deepcopy
from typing import Dict, Optional

import dateutil.parser
from eel import expose

from db import DBSession
from db.models import Day, DaySoldierAssignment, Score
from utils import model_actions
from utils.model_to_dict import model_to_dict


@expose
def get_day_soldier_assignments(day_id: str) -> Dict:
    try:
        with DBSession() as session:
            day = session.query(Day).filter(Day.id == day_id).first()
            if not day:
                return {"status": "error", "error": f"Day with ID {day_id} not found"}
            assignments = (
                session.query(DaySoldierAssignment)
                .filter(DaySoldierAssignment.day_id == day.id)
                .all()
            )
            assignments_data = [model_to_dict(assignment) for assignment in assignments]
            return {"status": "success", "data": assignments_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def get_day_soldier_assignment(assignment_id: str) -> Dict:
    try:
        with DBSession() as session:
            assignment = (
                session.query(DaySoldierAssignment)
                .filter(DaySoldierAssignment.id == assignment_id)
                .first()
            )
            if not assignment:
                return {"status": "error", "error": f"Assignment with ID {assignment_id} not found"}
            assignment_data = model_to_dict(assignment)
            return {"status": "success", "data": assignment_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def add_day_soldier_assignment(assignment_data: Dict) -> Dict:
    """
    Req body:

    {
        date: date
        assginment: <assignment_fields>
        day_id: id or none
        timetable_id: id
    }
    """
    try:
        with DBSession() as session:
            day_id = assignment_data.get("day_id")
            if day_id:
                day = session.query(Day).filter(Day.id == day_id).first()
                if not day:
                    return {"status": "error", "error": f"Day with ID {day_id} not found"}
            else:
                day = Day(
                    date=dateutil.parser.isoparse(assignment_data["date"]).date(),
                    timetable_id=assignment_data["timetable_id"],
                )
            assignment = DaySoldierAssignment(**assignment_data["assignment"], day=day)
            soldier_score: Score = model_actions.get_soldier_score_from_assignment(assignment)
            new_score = model_actions.get_updated_score_after_assignment_update(
                assignment, None, soldier_score, False
            )
            setattr(soldier_score, "score", new_score)
            session.add(assignment)
            session.commit()
            added_assignment_data = model_to_dict(assignment)
            return {"status": "success", "data": added_assignment_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def update_day_soldier_assignment(assignment_id: str, assignment_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            assignment: Optional[DaySoldierAssignment] = (
                session.query(DaySoldierAssignment)
                .filter(DaySoldierAssignment.id == assignment_id)
                .first()
            )
            if not assignment:
                return {"status": "error", "error": f"Assignment with ID {assignment_id} not found"}
            prev_assignment: DaySoldierAssignment = deepcopy(assignment)
            for key, value in assignment_data.items():
                if hasattr(assignment, key):
                    setattr(assignment, key, value)
            soldier_score: Score = model_actions.get_soldier_score_from_assignment(assignment)
            new_score = model_actions.get_updated_score_after_assignment_update(
                assignment, prev_assignment, soldier_score, False
            )
            setattr(soldier_score, "score", new_score)
            session.commit()
            updated_assignment_data = model_to_dict(assignment)
            return {"status": "success", "data": updated_assignment_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def delete_day_soldier_assignment(assignment_id: str) -> Dict:
    try:
        with DBSession() as session:
            assignment: Optional[DaySoldierAssignment] = (
                session.query(DaySoldierAssignment)
                .filter(DaySoldierAssignment.id == assignment_id)
                .first()
            )
            if not assignment:
                return {"status": "error", "error": f"Assignment with ID {assignment_id} not found"}
            session.delete(assignment)
            soldier_score: Score = model_actions.get_soldier_score_from_assignment(assignment)
            new_score = model_actions.get_updated_score_after_assignment_update(
                assignment, None, soldier_score, True
            )
            setattr(soldier_score, "score", new_score)
            session.commit()
            return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
