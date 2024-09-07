from typing import Dict, List

import eel

from db import DBSession
from db.models import BCPDay, BCPTimetable
from utils.model_to_dict import model_to_dict


@eel.expose
def get_bcp_days() -> Dict:
    try:
        with DBSession() as session:
            bcp_days = session.query(BCPDay).all()
            bcp_days_data = [model_to_dict(bcp_day) for bcp_day in bcp_days]
            return {"status": "success", "data": bcp_days_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@eel.expose
def get_bcp_day(bcp_day_id: str) -> Dict:
    try:
        with DBSession() as session:
            bcp_day = session.query(BCPDay).filter(BCPDay.id == bcp_day_id).first()
            if not bcp_day:
                return {"status": "error", "error": f"BCP Day with ID {bcp_day_id} not found"}
            bcp_day_data = model_to_dict(bcp_day)
            return {"status": "success", "data": bcp_day_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@eel.expose
def add_bcp_day(bcp_day_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            timetable = (
                session.query(BCPTimetable)
                .filter(BCPTimetable.id == bcp_day_data["timetable_id"])
                .first()
            )
            if not timetable:
                return {
                    "status": "error",
                    "error": f"Timetable with ID {bcp_day_data['timetable_id']} not found",
                }

            bcp_day = BCPDay(**bcp_day_data)
            session.add(bcp_day)
            session.commit()
            added_bcp_day_data = model_to_dict(bcp_day)
            return {"status": "success", "data": added_bcp_day_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@eel.expose
def update_bcp_day(bcp_day_id: str, bcp_day_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            bcp_day = session.query(BCPDay).filter(BCPDay.id == bcp_day_id).first()
            if not bcp_day:
                return {"status": "error", "error": f"BCP Day with ID {bcp_day_id} not found"}

            for key, value in bcp_day_data.items():
                if hasattr(bcp_day, key):
                    setattr(bcp_day, key, value)

            session.commit()
            updated_bcp_day_data = model_to_dict(bcp_day)
            return {"status": "success", "data": updated_bcp_day_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@eel.expose
def delete_bcp_day(bcp_day_id: str) -> Dict:
    try:
        with DBSession() as session:
            bcp_day = session.query(BCPDay).filter(BCPDay.id == bcp_day_id).first()
            if not bcp_day:
                return {"status": "error", "error": f"BCP Day with ID {bcp_day_id} not found"}

            session.delete(bcp_day)
            session.commit()
            return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
