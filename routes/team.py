from typing import Dict

from eel import expose

from db import DBSession
from db.models import BCPTimetable, Team, Timetable
from utils.model_to_dict import model_to_dict


@expose
def get_teams() -> Dict:
    try:
        with DBSession() as session:
            teams = session.query(Team).all()
            teams_data = [model_to_dict(team) for team in teams]
            return {"status": "success", "data": teams_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def get_team(team_id: str) -> Dict:
    try:
        with DBSession() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                return {"status": "error", "error": f"Team with ID {team_id} not found"}
            team_data = model_to_dict(team)
            return {"status": "success", "data": team_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def add_team(team_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            team = Team(**team_data)
            session.add(team)
            session.commit()
            added_team_data = model_to_dict(team)
            return {"status": "success", "data": added_team_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def update_team(team_id: str, team_data: Dict) -> Dict:
    try:
        with DBSession() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                return {"status": "error", "error": f"Team with ID {team_id} not found"}
            for key, value in team_data.items():
                if hasattr(team, key):
                    setattr(team, key, value)
            session.commit()
            updated_team_data = model_to_dict(team)
            return {"status": "success", "data": updated_team_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@expose
def delete_team(team_id: str) -> Dict:
    try:
        with DBSession() as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                return {"status": "error", "error": f"Team with ID {team_id} not found"}
            session.delete(team)
            session.commit()
            return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
