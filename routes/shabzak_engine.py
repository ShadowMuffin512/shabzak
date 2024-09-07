from typing import Any, Dict

import dateutil.parser
from eel import expose

from algorithm.bcp import BCPEngine
from algorithm.main import ShabzakEngine
from db import DBSession
from db.models import BCPDay, Day, DaySoldierAssignment, Team
from utils import exceptions
from utils.model_to_dict import model_to_dict


@expose
def get_prospective_future_assignments(team_id: str, start_date_str: str, num_days: int) -> Dict:
    try:
        with DBSession() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise exceptions.NotFound(f"Team not found with ID {team_id}")
            start_date = dateutil.parser.isoparse(start_date_str).date()
            shabzak_engine = ShabzakEngine(team)
            result = shabzak_engine.calculate_days(start_date, num_days)
            return {"status": "success", "result": [model_to_dict(day) for day in result]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def commit_prospective_assignments(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with DBSession() as session:
            days_data = data.get("days", [])

            for day_data in days_data:
                day_id = day_data.get("id")
                day_date = dateutil.parser.isoparse(day_data.get("date")).date()
                assignments = day_data.get("day_soldier_assignments", [])

                day = session.query(Day).filter(Day.id == day_id).first()
                if not day:
                    day = Day(id=day_id, date=day_date)
                    session.add(day)
                else:
                    day.date = day_date

                for assignment_data in assignments:
                    assignment_id = assignment_data.get("id")
                    soldier_id = assignment_data.get("soldier_id")
                    assignment = assignment_data.get("assignment")

                    day_soldier_assignment = (
                        session.query(DaySoldierAssignment)
                        .filter(DaySoldierAssignment.id == assignment_id)
                        .first()
                    )
                    if not day_soldier_assignment:
                        day_soldier_assignment = DaySoldierAssignment(
                            id=assignment_id,
                            day_id=day_id,
                            soldier_id=soldier_id,
                            assignment=assignment,
                        )
                        session.add(day_soldier_assignment)
                    else:
                        day_soldier_assignment.soldier_id = soldier_id
                        day_soldier_assignment.assignment = assignment

            session.commit()
            return {"status": "success", "message": "Assignments updated successfully"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "error": str(e)}


@expose
def get_prospective_bcp_future_assignments(
    team_id: str, start_date_str: str, num_days: int
) -> Dict:
    try:
        with DBSession() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise exceptions.NotFound(f"Team not found with ID {team_id}")
            start_date = dateutil.parser.isoparse(start_date_str).date()
            bcp_engine = BCPEngine(team)
            result = bcp_engine.calculate_bcp_days(start_date, num_days)
            return {"status": "success", "result": [model_to_dict(bcp_day) for bcp_day in result]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def commit_prospective_bcp_assignments(data: Dict[str, Any]) -> Dict:
    try:
        with DBSession() as session:
            for bcp_day_data in data["bcp_days"]:
                bcp_day = session.query(BCPDay).filter(BCPDay.id == bcp_day_data["id"]).first()
                if not bcp_day:
                    bcp_day = BCPDay(
                        id=bcp_day_data["id"], timetable_id=bcp_day_data["timetable_id"]
                    )

                for key, value in bcp_day_data.items():
                    setattr(bcp_day, key, value)

                session.add(bcp_day)

            session.commit()
            return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
