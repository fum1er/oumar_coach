#!/usr/bin/env python3
"""
Workout Tool - Outil de génération de séances avancé
Version complète corrigée sans erreurs BaseTool
"""

import os
from pathlib import Path
from typing import Dict, List

try:
    from langchain.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class BaseTool:
        def __init__(self):
            pass

class AdvancedWorkoutTool(BaseTool):
    """Outil de génération de séances avancé"""
    name = "generate_advanced_workout"
    description = "Génère une séance avancée avec justifications scientifiques. Paramètres: type, duration_minutes, athlete_level, ftp, objectives"
    
    def _run(self, type: str = "vo2max", duration_minutes: int = 75, 
             athlete_level: str = "intermediate", ftp: int = 320, 
             objectives: str = "improve_vo2max") -> str:
        """Génère une séance avancée complète"""
        
        try:
            # Créer les objets à chaque appel pour éviter les problèmes d'attributs
            from generators.workout_builder import WorkoutBuilder
            from generators.file_generators import FileGenerator
            from core.calculations import TrainingCalculations
            
            workout_builder = WorkoutBuilder()
            file_generator = FileGenerator()
            calculator = TrainingCalculations()
            
            # 1. Créer la séance intelligente
            workout = workout_builder.create_smart_workout(
                workout_type=type,
                duration=duration_minutes,
                level=athlete_level,
                ftp=ftp,
                objectives=objectives
            )
            
            # 2. Calculer métriques
            tss = calculator.calculate_tss(
                workout.segments, 
                workout.repeated_intervals, 
                ftp
            )
            workout.estimated_tss = tss
            
            # 3. Générer les fichiers
            files = file_generator.generate_all_formats(workout)
            files_info = "\n".join([f"• {k}: {Path(v).name}" for k, v in files.items()])
            
            # 4. Calculer temps de récupération
            recovery_time = calculator.estimate_recovery_time(tss, athlete_level)
            
            # 5. Analyser l'intensité
            high_intensity_time = calculator.calculate_high_intensity_time(workout)
            
            # 6. Créer le rapport
            return f"""✅ Séance avancée '{workout.name}' générée avec succès !

📊 RÉSUMÉ EXÉCUTIF:
{workout.description}

🎯 OBJECTIF SCIENTIFIQUE:
{workout.scientific_objective}

📁 FICHIERS GÉNÉRÉS:
{files_info}

📈 MÉTRIQUES CLÉS:
• TSS: {tss:.0f} points
• Temps haute intensité (Z4+): {high_intensity_time} minutes
• Temps de récupération: {recovery_time}

💡 NOTES D'ADAPTATION:
{workout.adaptation_notes}

🏃 CONSEILS DE COACHING:
{workout.coaching_tips}

🔬 ANALYSE SCIENTIFIQUE:
{self._create_analysis_report(workout, tss)}"""
            
        except Exception as e:
            return f"❌ Erreur lors de la génération avancée: {str(e)}"
    
    def _create_analysis_report(self, workout, tss: float) -> str:
        """Crée un rapport d'analyse simple"""
        # Analyser la charge d'entraînement
        if tss < 40:
            load_level = "Légère"
        elif tss < 60:
            load_level = "Modérée"
        elif tss < 80:
            load_level = "Élevée"
        elif tss < 120:
            load_level = "Très élevée"
        else:
            load_level = "Extrême"
        
        # Analyser le focus physiologique
        focus = "Endurance / Base aérobie"
        for interval in workout.repeated_intervals:
            if interval.work_power_pct[0] >= 1.06:  # Z5+
                focus = "VO2max / Puissance maximale aérobie"
                break
            elif interval.work_power_pct[0] >= 0.91:  # Z4
                focus = "Seuil lactique / FTP"
                break
        
        return f"""
📊 Charge d'entraînement: {load_level}
⚡ Focus physiologique: {focus}
🏃 Adaptations attendues: Amélioration spécifique {workout.type}"""

class SimpleWorkoutTool:
    """Version simplifiée de l'outil de génération"""
    
    def __init__(self):
        try:
            from generators.workout_builder import WorkoutBuilder
            from generators.file_generators import FileGenerator
            self.workout_builder = WorkoutBuilder()
            self.file_generator = FileGenerator()
            print("✅ Outil workout simplifié initialisé")
        except ImportError:
            self.workout_builder = None
            self.file_generator = None
            print("⚠️ Workout builder non disponible")
    
    def generate(self, workout_type: str = "vo2max", duration: int = 75, 
                level: str = "intermediate", ftp: int = 320) -> str:
        """Génération simplifiée"""
        if not self.workout_builder:
            return "❌ Constructeurs non disponibles"
        
        try:
            workout = self.workout_builder.create_smart_workout(
                workout_type, duration, level, ftp
            )
            
            if self.file_generator:
                files = self.file_generator.generate_all_formats(workout)
                return f"✅ Séance {workout.name} générée ! Fichiers: {len(files)}"
            else:
                return f"✅ Séance {workout.name} créée (pas de fichiers)"
                
        except Exception as e:
            return f"❌ Erreur: {e}"

def create_workout_tool():
    """Factory pour créer l'outil approprié"""
    if LANGCHAIN_AVAILABLE:
        try:
            return AdvancedWorkoutTool()
        except Exception as e:
            print(f"⚠️ Erreur création outil LangChain: {e}")
            return SimpleWorkoutTool()
    else:
        return SimpleWorkoutTool()