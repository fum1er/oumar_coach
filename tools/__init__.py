# === tools/__init__.py ===
"""
Tools module - Outils LangChain pour l'agent
"""

from .knowledge_tool import CyclingKnowledgeTool, create_knowledge_tool
from .workout_tool import AdvancedWorkoutTool, create_workout_tool

__all__ = [
    'CyclingKnowledgeTool',
    'AdvancedWorkoutTool', 
    'create_knowledge_tool',
    'create_workout_tool'
]
