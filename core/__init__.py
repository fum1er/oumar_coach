"""
Core module - Composants de base du coach cycliste
"""

from .models import (
    UserProfile, 
    PowerZone, 
    WorkoutSegment, 
    RepeatedInterval, 
    SmartWorkout, 
    WorkoutRequest
)

from .knowledge_base import (
    POWER_ZONES,
    WORKOUT_STRUCTURES,
    ATHLETE_ADAPTATIONS,
    KnowledgeBaseManager
)

from .calculations import TrainingCalculations

__all__ = [
    'UserProfile',
    'PowerZone', 
    'WorkoutSegment',
    'RepeatedInterval',
    'SmartWorkout',
    'WorkoutRequest',
    'POWER_ZONES',
    'WORKOUT_STRUCTURES', 
    'ATHLETE_ADAPTATIONS',
    'KnowledgeBaseManager',
    'TrainingCalculations'
]