from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
)
from sqlalchemy.ext.declarative import as_declarative, declarative_base, declared_attr
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
    __tablename__ = "soldiers"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_commander = Column(Boolean, default=False)
    is_reserve = Column(Boolean, default=False)
    is_close_to_base = Column(Boolean, default=True)
    is_studying = Column(Boolean, default=False)
    score_id = Column(Integer, ForeignKey("scores.id"))
    score = relationship("Score", back_populates="soldier", cascade="all, delete-orphan")
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="soldier ", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.score:
            default_score = Score(score=0, soldier_id=self.id)
            self.score = default_score


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    min_consecutive_nights = Column(Integer, default=1)
    allow_guard_to_hold_shift = Column(Boolean, default=False)
    commanders_do_weekends = Column(Boolean, default=False)
    commanders_do_nights = Column(Boolean, default=False)
    soldiers = relationship("Soldier", back_populates="team", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="team", cascade="all, delete-orphan")
    timetable_id = Column(Integer, ForeignKey("timetables.id"), nullable=False)
    timetable = relationship("Timetable", back_populates="team")
    bcp_timetable_id = Column(Integer, ForeignKey("bcp_timetables.id"), nullable=False)
    bcp_timetable = relationship(
        "BCPTimetable", back_populates="team", cascade="all, delete-orphan"
    )


class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="scores", cascade="all, delete-orphan")
    soldier_id = Column(Integer, ForeignKey("soldiers.id"), nullable=False)
    soldier = relationship("Soldier", back_populates="score", cascade="all, delete-orphan")
    score = Column(Integer, default=0)


class Timetable(Base):
    __tablename__ = "timetables"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="timetable", cascade="all, delete-orphan")
    days = relationship("Day", back_populates="timetable", cascade="all, delete-orphan")


class Day(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    timetable_id = Column(Integer, ForeignKey("timetables.id"), nullable=False)
    timetable = relationship("Timetable", back_populates="days")
    day_soldier_assignments = relationship(
        "DaySoldierAssignment", back_populates="day", cascade="all, delete-orphan"
    )


class DaySoldierAssignment(Base):
    __tablename__ = "day_soldier_assignments"
    id = Column(Integer, primary_key=True)
    soldier_id = Column(Integer, ForeignKey("soldiers.id"), nullable=False)
    soldier = relationship("Soldier")
    day_id = Column(Integer, ForeignKey("days.id"), nullable=False)
    day = relationship("Day", back_populates="day_soldier_assignments")
    assignment = Column(Enum(enums.Assignment), nullable=False)
    extra_assignment_text = Column(String, default="")
    assignment_location = Column(Enum(enums.AssignmentLocation), default="Shalar")


class BCPTimetable(Base):
    __tablename__ = "bcp_timetables"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="bcp_timetable", cascade="all, delete-orphan")
    days = relationship("BCPDay", back_populates="timetable", cascade="all, delete-orphan")


class BCPDay(Base):
    __tablename__ = "bcp_days"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    timetable_id = Column(Integer, ForeignKey("bcp_timetables.id"), nullable=False)
    timetable = relationship("BCPTimetable", back_populates="days", cascade="all, delete-orphan")
    morning_soldier_id = Column(Integer, ForeignKey("soldiers.id"))
    morning_soldier = relationship("Soldier")
    night_soldier_id = Column(Integer, ForeignKey("soldiers.id"))
    night_soldier = relationship("Soldier")


class AssignmentScore(Base):
    __tablename__ = "assignment_scores"
    id = Column(Integer, primary_key=True)
    assignment = Column(Enum(enums.Assignment), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
