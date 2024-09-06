from sqlalchemy import Table, Column, Integer, String, DateTime, Date, ForeignKey, Boolean, func, Enum, MetaData
from sqlalchemy.ext.declarative import declarative_base, as_declarative, declared_attr
from sqlalchemy.orm import relationship

from utils import enums


@as_declarative()
class Base:
    metadata: MetaData
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Soldier(Base):
    __tablename__ = 'soldiers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_commander = Column(Boolean, default=False)
    is_reserve = Column(Boolean, default=False)
    is_close_to_base = Column(Boolean, default=True)
    is_studying = Column(Boolean, default=False)
    score_id = Column(Integer, ForeignKey('scores.id'))
    score = relationship('Score', back_populates='users', cascade='all, delete-orphan')
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team = relationship('Team', back_populates='soldiers', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.score:
            default_score = Score(score=0, soldier_id=self.id)
            self.score = default_score

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    min_consecutive_nights = Column(Integer, default=1)
    allow_before_day_off = Column(Boolean, default=False)
    commanders_do_weekends = Column(Boolean, default=False)
    commanders_do_nights = Column(Boolean, default=False)
    soldiers = relationship('Soldier', back_populates='team', cascade='all, delete-orphan')

class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    soldier_id = Column(Integer, ForeignKey('soldiers.id'), nullable=False)
    soldier = relationship('Soldier', back_populates='scores', cascade='all, delete-orphan')
    score = Column(Integer, default=0)

class Timetable(Base):
    __tablename__ = 'timetables'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team = relationship('Team', back_populates='timetables', cascade='all, delete-orphan')
    days = relationship('Day', back_populates='timetable', cascade='all, delete-orphan')

class Day(Base):
    __tablename__ = 'days'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    timetable_id = Column(Integer, ForeignKey('timetables.id'), nullable=False)
    timetable = relationship('Timetable', back_populates='days')
    day_soldier_assignments = relationship('DaySoldierAssignment', back_populates='day', cascade='all, delete-orphan')

class DaySoldierAssignment(Base):
    __tablename__ = 'day_soldier_assignments'
    id = Column(Integer, primary_key=True)
    soldier_id = Column(Integer, ForeignKey('soldiers.id'))
    soldier = relationship('Soldier', back_populates='day_soldier_assignments')
    day_id = Column(Integer, ForeignKey('days.id'))
    day = relationship('Day', back_populates='day_soldier_assignments')
    assignment = Column(Enum(enums.Assignment), nullable=False)
    extra_assignment_text = Column(String, default='')
    assignment_location = Column(Enum(enums.AssignmentLocation), default='Shalar')

class BCPTimetable(Base):
    __tablename__ = 'bcp_timetables'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team = relationship('Team', back_populates='bcp_timetables')
    days = relationship('BCPDay', back_populates='bcp_timetables', cascade='all, delete-orphan')

class BCPDay(Base):
    __tablename__ = 'bcp_days'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)    
    timetable_id = Column(Integer, ForeignKey('bcp_timetables.id'), nullable=False)
    timetable = relationship('BCPTimetable', back_populates='bcp_days', cascade='all, delete-orphan')
    morning_soldier_id = Column(Integer, ForeignKey('soldiers.id'))
    morning_soldier = relationship('Soldier', back_populates='bcp_day_soldier_assignments')
    night_soldier_id = Column(Integer, ForeignKey('soldiers.id'))
    night_soldier = relationship('Soldier', back_populates='bcp_day_soldier_assignments')

class AssignmentScore(Base):
    __tablename__ = 'assignment_scores'
    id = Column(Integer, primary_key=True)
    assignment = Column(Enum(enums.Assignment), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
