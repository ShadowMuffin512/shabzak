import uuid

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
    func,
)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import foreign, relationship, remote

from utils import enums


@as_declarative()
class Base:
    metadata: MetaData

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Score(Base):
    __tablename__ = "scores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    score = Column(Integer, default=0)


class Soldier(Base):
    __tablename__ = "soldiers"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_commander = Column(Boolean, default=False)
    is_reserve = Column(Boolean, default=False)
    is_close_to_base = Column(Boolean, default=True)
    is_onboarding = Column(Boolean, default=False)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", foreign_keys=[team_id])
    score_id = Column(String(36), ForeignKey("scores.id"))
    score = relationship(
        "Score",
        foreign_keys=[score_id],
        single_parent=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.score:
            default_score = Score(score=0, soldier_id=self.id, team_id=self.team_id)
            self.score = default_score


class Team(Base):
    __tablename__ = "teams"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    min_consecutive_nights = Column(Integer, default=1)
    allow_guard_to_hold_shift = Column(Boolean, default=False)
    commanders_do_weekends = Column(Boolean, default=False)
    commanders_do_nights = Column(Boolean, default=False)
    timetable = relationship(
        "Timetable", back_populates="team", uselist=False, cascade="all, delete-orphan"
    )
    bcp_timetable = relationship(
        "BCPTimetable", back_populates="team", uselist=False, cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.timetable:
            self.timetable = Timetable(team_id=self.id)

        if not self.bcp_timetable:
            self.bcp_timetable = BCPTimetable(team_id=self.id)


class Timetable(Base):
    __tablename__ = "timetables"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="timetable", foreign_keys=[team_id])


class Day(Base):
    __tablename__ = "days"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    timetable_id = Column(String(36), ForeignKey("timetables.id"), nullable=False)
    timetable = relationship("Timetable")


class DaySoldierAssignment(Base):
    __tablename__ = "day_soldier_assignments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    soldier_id = Column(String(36), ForeignKey("soldiers.id"), nullable=False)
    soldier = relationship("Soldier")
    day_id = Column(String(36), ForeignKey("days.id"), nullable=False)
    day = relationship("Day")
    assignment = Column(Enum(enums.Assignment), nullable=False)
    extra_assignment_text = Column(String, default="")
    assignment_location = Column(Enum(enums.AssignmentLocation), default="Shalar")


class BCPTimetable(Base):
    __tablename__ = "bcp_timetables"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    team = relationship("Team", back_populates="bcp_timetable", foreign_keys=[team_id])
    days = relationship("BCPDay", cascade="all, delete-orphan", back_populates="timetable")


class BCPDay(Base):
    __tablename__ = "bcp_days"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    timetable_id = Column(String(36), ForeignKey("bcp_timetables.id"), nullable=False)
    timetable = relationship("BCPTimetable", foreign_keys=[timetable_id])
    morning_soldier_id = Column(String(36), ForeignKey("soldiers.id"))
    morning_soldier = relationship("Soldier", foreign_keys=[morning_soldier_id])
    night_soldier_id = Column(String(36), ForeignKey("soldiers.id"))
    night_soldier = relationship("Soldier", foreign_keys=[night_soldier_id])


class AssignmentScore(Base):
    __tablename__ = "assignment_scores"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment = Column(Enum(enums.Assignment), nullable=False, unique=True)
    score = Column(Integer, nullable=False)
