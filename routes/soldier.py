from typing import Dict
from eel import expose
from db import DBSession
from db.models import Soldier, Team
from utils.model_to_dict import model_to_dict

@expose
def get_soldiers_for_team(team_id: int) -> Dict:
    try:
        with DBSession as session:
            team = session.query(Team).filter(Team.id == team_id).first()
            if not team:
                return {'status': 'error', 'error': f'Team with ID {team_id} not found'}
            soldiers = team.soldiers
            soldiers_data = [model_to_dict(soldier) for soldier in soldiers]
            return {'status': 'success', 'data': soldiers_data}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@expose
def get_soldier(soldier_id: int) -> Dict:
    try:
        with DBSession as session:
            soldier = session.query(Soldier).filter(Soldier.id == soldier_id).first()
            if not soldier:
                return {'status': 'error', 'error': f'Soldier with ID {soldier_id} not found'}
            soldier_data = model_to_dict(soldier)
            return {'status': 'success', 'data': soldier_data}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@expose
def add_soldier(soldier_data: Dict) -> Dict:
    try:
        with DBSession as session:
            soldier = Soldier(**soldier_data)
            session.add(soldier)
            session.commit()
            added_soldier_data = model_to_dict(soldier)
            return {'status': 'success', 'data': added_soldier_data}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@expose
def update_soldier(soldier_id: int, soldier_data: Dict) -> Dict:
    try:
        with DBSession as session:
            soldier = session.query(Soldier).filter(Soldier.id == soldier_id).first()
            if not soldier:
                return {'status': 'error', 'error': f'Soldier with ID {soldier_id} not found'}
            for key, value in soldier_data.items():
                if hasattr(soldier, key):
                    setattr(soldier, key, value)
            session.commit()
            updated_soldier_data = model_to_dict(soldier)
            return {'status': 'success', 'data': updated_soldier_data}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@expose
def delete_soldier(soldier_id: int) -> Dict:
    try:
        with DBSession as session:
            soldier = session.query(Soldier).filter(Soldier.id == soldier_id).first()
            if not soldier:
                return {'status': 'error', 'error': f'Soldier with ID {soldier_id} not found'}
            session.delete(soldier)
            session.commit()
            return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
