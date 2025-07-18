#!/usr/bin/env python3
"""
Core Models - Structures de données pour le coach cycliste
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

@dataclass
class UserProfile:
    """Profil utilisateur complet"""
    user_id: str = "default_user"
    name: str = "Cycliste"
    age: int = 30
    weight: float = 70.0  # kg
    ftp: int = 320  # watts
    ftp_history: List[tuple] = None  # [(date, ftp_value)]
    
    # Objectifs et préférences
    primary_goals: List[str] = None  # ["improve_ftp", "endurance", "weight_loss"]
    target_events: List[Dict] = None  # [{"name": "Century Ride", "date": "2025-08-15"}]
    available_time: Dict = None  # {"weekdays": 60, "weekends": 120}
    
    # Données d'entraînement
    recent_activities: List[Dict] = None
    training_load_history: List[float] = None
    fatigue_score: float = 0.0
    
    # Préférences système
    preferred_platforms: List[str] = None  # ["mywhoosh", "trainingpeaks"]
    experience_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    
    def __post_init__(self):
        if self.ftp_history is None:
            self.ftp_history = [(datetime.now().strftime("%Y-%m-%d"), self.ftp)]
        if self.primary_goals is None:
            self.primary_goals = ["general_fitness"]
        if self.target_events is None:
            self.target_events = []
        if self.available_time is None:
            self.available_time = {"weekdays": 60, "weekends": 90}
        if self.recent_activities is None:
            self.recent_activities = []
        if self.training_load_history is None:
            self.training_load_history = []
        if self.preferred_platforms is None:
            self.preferred_platforms = ["mywhoosh"]

@dataclass
class PowerZone:
    """Définition d'une zone de puissance"""
    name: str
    power_pct_ftp: Tuple[float, float]
    hr_pct_max: Tuple[int, int]
    cadence_rpm: Tuple[int, int]
    objective: str
    duration_typical: str
    when_use: str

@dataclass
class WorkoutSegment:
    """Segment d'entraînement avec justification scientifique"""
    type: str  # "Warmup", "SteadyState", "Cooldown"
    duration_minutes: int
    power_pct_ftp: Tuple[float, float]
    cadence_rpm: int
    description: str
    scientific_rationale: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def get_power_watts(self, ftp: int) -> Tuple[int, int]:
        """Calcule la puissance en watts"""
        return (int(self.power_pct_ftp[0] * ftp), int(self.power_pct_ftp[1] * ftp))

@dataclass
class RepeatedInterval:
    """Intervalles répétés avec structure Work/Rest"""
    repetitions: int
    work_duration: int
    work_power_pct: Tuple[float, float]
    work_cadence: int
    rest_duration: int
    rest_power_pct: Tuple[float, float]
    rest_cadence: int
    work_description: str
    rest_description: str
    scientific_rationale: str = ""
    
    def get_total_duration(self) -> int:
        """Durée totale des intervalles"""
        return self.repetitions * (self.work_duration + self.rest_duration)

@dataclass
class SmartWorkout:
    """Séance d'entraînement intelligente avec justifications"""
    name: str
    type: str  # "vo2max", "threshold", "endurance", "recovery"
    description: str
    scientific_objective: str
    total_duration: int
    segments: List[WorkoutSegment]
    repeated_intervals: List[RepeatedInterval]
    ftp: int
    adaptation_notes: str = ""
    coaching_tips: str = ""
    estimated_tss: float = 0.0
    
    def calculate_actual_duration(self) -> int:
        """Calcule la durée réelle basée sur les segments et intervalles"""
        duration = sum(seg.duration_minutes for seg in self.segments)
        duration += sum(interval.get_total_duration() for interval in self.repeated_intervals)
        return duration

@dataclass
class WorkoutRequest:
    """Demande de séance d'entraînement"""
    duration_minutes: int
    workout_type: str  # "endurance", "threshold", "vo2max", "recovery"
    intensity_preference: str  # "easy", "moderate", "hard"
    target_date: str
    athlete_level: str = "intermediate"
    special_notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)