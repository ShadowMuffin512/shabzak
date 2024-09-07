from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Self

import utils
from db import DBSession
from db.models import (
    AssignmentScore,
    BCPDay,
    Day,
    DaySoldierAssignment,
    Score,
    Soldier,
    Team,
    Timetable,
)
from utils import enums, model_actions


class ShabzakEngine:
    timetable_lookback_days = 7
    default_assignment = {
        enums.WeekDayType.Weekday: enums.Assignment.Morning,
        enums.WeekDayType.Weekend: enums.Assignment.WeekendHome,
    }
    default_starting_assignments = {
        enums.WeekDayType.Weekday: [
            enums.Assignment.Morning,
            enums.Assignment.Afternoon,
            enums.Assignment.Night,
        ],
        enums.WeekDayType.Weekend: [enums.Assignment.Day, enums.Assignment.Night],
    }
    assignments_containing_others = {
        enums.Assignment.DayAndNight: [
            enums.Assignment.Day,
            enums.Assignment.Afternoon,
            enums.Assignment.Night,
            enums.Assignment.Morning,
        ],
        enums.Assignment.Day: [enums.Assignment.Morning, enums.Assignment.Afternoon],
    }
    assigments_allowing_after = {
        enums.WeekDayType.Weekday: [
            enums.Assignment.Night,
            enums.Assignment.Tashtiot,
            enums.Assignment.GuardDuty,
            enums.Assignment.DayAndNight,
        ],
        enums.WeekDayType.Weekend: [
            enums.Assignment.Day,
            enums.Assignment.Night,
            enums.Assignment.DayAndNight,
            enums.Assignment.Tashtiot,
            enums.Assignment.GuardDuty,
        ],
    }
    commander_disallowed_assignments = [
        enums.Assignment.Night,
        enums.Assignment.DayAndNight,
        enums.Assignment.Onboarding,
        enums.Assignment.Afternoon,
    ]

    def __init__(self, team: Team) -> None:
        self.consecutive_nights: int = 0
        self.start_date: Optional[date] = None
        self.team: Team = team
        self.timetable: Timetable = model_actions.get_timetable_for_team(self.team)
        self.soldiers: List[Soldier] = model_actions.get_soldiers_for_team(self.team)
        self.last_night_soldier: Optional[Soldier] = None
        self.scores: List[Score] = model_actions.get_scores_for_team(self.team)
        self.assignment_scores: List[AssignmentScore] = model_actions.get_assignment_scores()

    @staticmethod
    def filter_preexisting_assignments(
        assignments_to_fill: List[enums.Assignment], filled_assignments: List[DaySoldierAssignment]
    ) -> List[enums.Assignment]:
        filled_assignment_names: List[enums.Assignment] = [
            enums.Assignment[assignment.assignment] for assignment in filled_assignments
        ]
        for filled_assignment in filled_assignment_names:
            filled_assignment_names.extend(
                ShabzakEngine.assignments_containing_others.get(filled_assignment, [])
            )
        return [item for item in assignments_to_fill if item not in filled_assignment_names]

    def get_score_for_soldier(self, soldier: Soldier) -> Score:
        return next((score for score in self.scores if soldier.score_id == score.id))

    def sort_soldiers_by_score(self) -> List[Soldier]:
        return sorted(self.soldiers, key=lambda soldier: self.get_score_for_soldier(soldier).score)

    def sort_assignments_by_score(
        self, assignments: List[enums.Assignment], reverse: bool = True
    ) -> List[enums.Assignment]:
        return sorted(
            assignments,
            key=lambda assignment: self.get_score_for_assignment(assignment).score,
            reverse=reverse,
        )

    def get_score_for_assignment(self, assignment: enums.Assignment) -> AssignmentScore:
        return next(
            (
                assignment_score
                for assignment_score in self.assignment_scores
                if assignment_score.assignment == assignment
            ),
        )

    def get_initial_consecutive_night_streak(self, days: List[Day]) -> int:
        if not days:
            return 0
        last_found_soldier: Optional[Soldier] = self.get_night_soldier(days[0])
        streak = 1
        for day in days[1:]:
            if self.get_night_soldier(day) != last_found_soldier:
                return streak
            streak += 1
        return streak

    def get_soldier_assignment_for_day(
        self, day: Day, soldier: Soldier
    ) -> Optional[DaySoldierAssignment]:
        day_assignments = model_actions.get_assignments_for_day(day)
        if not day_assignments:
            return None
        soldier_assignment = next(
            (assignment for assignment in day_assignments if assignment.soldier_id == soldier.id),
            None,
        )
        return soldier_assignment

    def get_night_soldier(self, day: Day) -> Soldier:
        assignments = model_actions.get_assignments_for_day(day)
        shifts_including_nights = [enums.Assignment.Night, enums.Assignment.DayAndNight]
        if self.team.allow_guard_to_hold_shift:
            shifts_including_nights.extend([enums.Assignment.GuardDuty, enums.Assignment.Tashtiot])
        night_assignment = next(
            (
                assignment
                for assignment in assignments
                if assignment.assignment in shifts_including_nights
            ),
        )
        return model_actions.get_soldier_from_assignment(night_assignment)

    def calculate_days(self, start_date: date, num_days_to_calculate: int) -> List[Day]:
        new_calculated_days: List[Day] = []
        self.calculated_days: List[Day] = model_actions.get_lookback_days_from_timetable(
            self.timetable, start_date, ShabzakEngine.timetable_lookback_days
        )
        if self.calculated_days:
            self.last_night_soldier = self.get_night_soldier(self.calculated_days[0])
            self.consecutive_nights = self.get_initial_consecutive_night_streak(
                self.calculated_days
            )
        self.start_date = start_date
        for days_passed in range(num_days_to_calculate):
            date_to_calculate = self.start_date + timedelta(days=days_passed)
            day_to_calculate = Day(date=date_to_calculate, timetable_id=self.timetable.id)
            existing_assignments = model_actions.get_existing_assignments_for_date(
                date_to_calculate
            )
            self.soldiers = self.sort_soldiers_by_score()
            day_assignments = self.get_new_day_assignments(day_to_calculate, existing_assignments)
            new_day = Day(
                date=date_to_calculate,
                timetable_id=self.timetable.id,
            )
            for day_assignment in day_assignments:
                day_assignment.day = new_day
            self.calculated_days.append(new_day)
            new_calculated_days.append(new_day)
        return new_calculated_days

    def get_new_day_assignments(
        self, day: Day, existing_assignments: List[DaySoldierAssignment]
    ) -> List[DaySoldierAssignment]:
        prev_day: Optional[Day] = self.calculated_days[0] if self.calculated_days else None
        new_assignments = deepcopy(existing_assignments)
        for soldier in self.soldiers:
            prospective_assignment = self.create_new_assignment_for_soldier(
                soldier, day, prev_day, new_assignments
            )
            if prospective_assignment:
                new_assignments.append(prospective_assignment)
        return new_assignments

    def create_new_assignment_for_soldier(
        self,
        soldier: Soldier,
        day: Day,
        prev_day: Optional[Day],
        existing_assignments: List[DaySoldierAssignment],
    ) -> Optional[DaySoldierAssignment]:
        weekend_or_weekday: enums.WeekDayType = utils.get_weekend_or_weekday(day.date)
        edge_case_assignment = self.handle_day_assignment_edge_cases(
            soldier, existing_assignments, day, prev_day
        )
        if edge_case_assignment:
            return edge_case_assignment
        available_assignments = self.sort_assignments_by_score(
            self.get_available_assignments(soldier, existing_assignments, day.date)
        )
        selected_assignment = (
            available_assignments[0]
            if available_assignments
            else ShabzakEngine.default_assignment[weekend_or_weekday]
        )
        if selected_assignment == enums.Assignment.Night:
            self.last_night_soldier = soldier
            self.consecutive_nights = 1
        return DaySoldierAssignment(
            soldier_id=soldier.id, day_id=day.id, assignment=selected_assignment.name
        )

    def handle_day_assignment_edge_cases(
        self,
        soldier: Soldier,
        existing_assignments: List[DaySoldierAssignment],
        day: Day,
        prev_day: Optional[Day],
    ) -> Optional[DaySoldierAssignment]:
        if [
            assignment for assignment in existing_assignments if assignment.soldier_id == soldier.id
        ]:  # Soldier already has an assignment
            return None
        if (
            soldier == self.last_night_soldier
            and self.team.min_consecutive_nights > self.consecutive_nights
        ):  # Handling mininum consecutive nights
            self.consecutive_nights += 1
            return DaySoldierAssignment(
                soldier_id=soldier.id, day_id=day.id, assignment=enums.Assignment.Night.name
            )
        if prev_day:  # After-assignment calculation if applicable
            previous_soldier_assignment = self.get_soldier_assignment_for_day(prev_day, soldier)
            previous_weekend_or_weekday = utils.get_weekend_or_weekday(prev_day.date)
            if (
                previous_soldier_assignment
                and enums.Assignment[previous_soldier_assignment.assignment]
                in ShabzakEngine.assigments_allowing_after[previous_weekend_or_weekday]
            ):
                return DaySoldierAssignment(
                    soldier_id=soldier.id,
                    day_id=day.id,
                    assignment=enums.Assignment.After.name,
                )
        return None

    def get_available_assignments(
        self, soldier: Soldier, existing_assignments: List[DaySoldierAssignment], date: date
    ) -> List[enums.Assignment]:
        weekend_or_weekday = utils.get_weekend_or_weekday(date)
        available_assignments = ShabzakEngine.filter_preexisting_assignments(
            ShabzakEngine.default_starting_assignments[weekend_or_weekday], existing_assignments
        )
        if soldier.is_commander:
            if not self.team.commanders_do_nights:
                available_assignments = [
                    assignment
                    for assignment in enums.Assignment
                    if assignment != enums.Assignment.Night
                ]
            if (
                not self.team.commanders_do_weekends
                and weekend_or_weekday == enums.WeekDayType.Weekend
            ):
                available_assignments = [
                    assignment
                    for assignment in enums.Assignment
                    if assignment != enums.Assignment.Day
                ]
        if (
            not soldier.is_close_to_base
            and weekend_or_weekday == enums.WeekDayType.Weekend
            and enums.Assignment.Day not in available_assignments
        ):
            available_assignments = [enums.Assignment.DayAndNight]

        if self.team.allow_guard_to_hold_shift:
            available_assignments = self.filter_guard_shifts(
                available_assignments, weekend_or_weekday
            )
        return available_assignments

    def filter_guard_shifts(
        self, initial_assignments: List[enums.Assignment], weekend_or_weekday: enums.WeekDayType
    ) -> List[enums.Assignment]:
        available_assignments = [*initial_assignments]
        eligible_guard_shift_types = [enums.Assignment.GuardDuty, enums.Assignment.Tashtiot]
        shifts_to_remove = {
            enums.WeekDayType.Weekday: [enums.Assignment.Night],
            enums.WeekDayType.Weekend: [enums.Assignment.Day, enums.Assignment.Night],
        }
        if eligible_guard_shift_types in initial_assignments:
            available_assignments = [
                assignment
                for assignment in available_assignments
                if assignment not in shifts_to_remove[weekend_or_weekday]
            ]
        return available_assignments
