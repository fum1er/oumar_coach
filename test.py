#!/usr/bin/env python3
"""
Cycling Coach IA - Générateur de Programmes d'Entraînement
Basé sur les recherches récentes en periodization cycliste

Version: 0.1.0 - MVP Starter
Auteur: Coach IA Project
"""

import os
import datetime
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONSTANTES SCIENTIFIQUES ===

# Zones de puissance basées sur FTP (Functional Threshold Power)
POWER_ZONES = {
    'Z1': {'min': 0.00, 'max': 0.55, 'name': 'Active Recovery', 'description': 'Récupération active'},
    'Z2': {'min': 0.56, 'max': 0.75, 'name': 'Endurance', 'description': 'Endurance aérobie'},
    'Z3': {'min': 0.76, 'max': 0.90, 'name': 'Tempo', 'description': 'Tempo/Seuil aérobie'},
    'Z4': {'min': 0.91, 'max': 1.05, 'name': 'Lactate Threshold', 'description': 'Seuil lactique'},
    'Z5': {'min': 1.06, 'max': 1.20, 'name': 'VO2max', 'description': 'Puissance maximale aérobie'},
    'Z6': {'min': 1.21, 'max': 1.50, 'name': 'Anaerobic Capacity', 'description': 'Capacité anaérobie'},
    'Z7': {'min': 1.51, 'max': 3.00, 'name': 'Neuromuscular Power', 'description': 'Puissance neuromusculaire'}
}

# Zones de fréquence cardiaque (Edwards' model)
HR_ZONES = {
    'Z1': {'min': 50, 'max': 59, 'multiplier': 1},
    'Z2': {'min': 60, 'max': 69, 'multiplier': 2},
    'Z3': {'min': 70, 'max': 79, 'multiplier': 3},
    'Z4': {'min': 80, 'max': 89, 'multiplier': 4},
    'Z5': {'min': 90, 'max': 100, 'multiplier': 5}
}

# === CLASSES DE DONNÉES ===

@dataclass
class UserProfile:
    """Profil utilisateur avec données physiologiques"""
    name: str
    age: int
    weight: float  # kg
    height: float  # cm
    ftp: int  # watts
    hr_max: int  # bpm
    experience_level: str  # 'beginner', 'intermediate', 'advanced', 'elite'
    weekly_hours: float  # heures par semaine disponibles
    goals: List[str]  # objectives principaux

@dataclass
class WorkoutInterval:
    """Interval d'entraînement avec zone et durée"""
    duration_minutes: int
    power_zone: str
    cadence_target: Optional[int] = None
    description: str = ""
    
    def get_power_range(self, ftp: int) -> Tuple[int, int]:
        """Calcule la plage de puissance pour cet interval"""
        zone_data = POWER_ZONES[self.power_zone]
        power_min = int(ftp * zone_data['min'])
        power_max = int(ftp * zone_data['max'])
        return power_min, power_max

@dataclass
class Workout:
    """Séance d'entraînement complète"""
    name: str
    description: str
    intervals: List[WorkoutInterval]
    total_duration: int  # minutes
    estimated_tss: float
    focus: str  # 'endurance', 'threshold', 'vo2max', 'anaerobic', 'recovery'

# === MOTEUR DE CALCULS SCIENTIFIQUES ===

class TrainingMetrics:
    """Calculs des métriques d'entraînement scientifiquement validées"""
    
    @staticmethod
    def calculate_tss(duration_hours: float, normalized_power: float, ftp: int) -> float:
        """
        Calcule le Training Stress Score (TSS) selon Coggan
        TSS = (duration_hours × NP × IF) / (FTP × 1.0) × 100
        """
        intensity_factor = normalized_power / ftp
        return (duration_hours * normalized_power * intensity_factor) / (ftp * 1.0) * 100
    
    @staticmethod
    def estimate_workout_tss(workout: Workout, ftp: int) -> float:
        """Estime le TSS d'une séance basé sur les intervals"""
        total_tss = 0
        
        for interval in workout.intervals:
            power_min, power_max = interval.get_power_range(ftp)
            avg_power = (power_min + power_max) / 2
            duration_hours = interval.duration_minutes / 60
            
            # Utilisation de la puissance moyenne comme approximation du NP
            interval_tss = TrainingMetrics.calculate_tss(duration_hours, avg_power, ftp)
            total_tss += interval_tss
            
        return total_tss
    
    @staticmethod
    def calculate_etrimp(duration_minutes: int, hr_zone: str) -> float:
        """Calcule Edwards' TRIMP pour un interval"""
        zone_data = HR_ZONES[hr_zone]
        return (duration_minutes / 60) * zone_data['multiplier']

# === GÉNÉRATEUR DE PROGRAMMES ===

class WorkoutGenerator:
    """Générateur de séances basé sur la recherche récente"""
    
    def __init__(self, user_profile: UserProfile):
        self.user = user_profile
        
    def generate_endurance_workout(self, duration_minutes: int = 90) -> Workout:
        """Génère une séance d'endurance (Zone 2 principalement)"""
        intervals = [
            WorkoutInterval(15, 'Z1', 85, "Échauffement progressif"),
            WorkoutInterval(duration_minutes - 30, 'Z2', 90, "Endurance stable - conversation possible"),
            WorkoutInterval(15, 'Z1', 85, "Retour au calme")
        ]
        
        workout = Workout(
            name=f"Endurance {duration_minutes}min",
            description="Séance d'endurance aérobie pour développer la base",
            intervals=intervals,
            total_duration=duration_minutes,
            estimated_tss=0,
            focus='endurance'
        )
        
        workout.estimated_tss = TrainingMetrics.estimate_workout_tss(workout, self.user.ftp)
        return workout
    
    def generate_threshold_workout(self) -> Workout:
        """Génère une séance de seuil (Sweet Spot / Threshold)"""
        intervals = [
            WorkoutInterval(15, 'Z1', 85, "Échauffement"),
            WorkoutInterval(10, 'Z2', 90, "Préparation"),
            WorkoutInterval(20, 'Z4', 95, "Bloc seuil 1 - maintenir la puissance"),
            WorkoutInterval(5, 'Z2', 85, "Récupération"),
            WorkoutInterval(20, 'Z4', 95, "Bloc seuil 2 - concentration mentale"),
            WorkoutInterval(5, 'Z2', 85, "Récupération"),
            WorkoutInterval(15, 'Z4', 95, "Bloc seuil 3 - finir fort"),
            WorkoutInterval(10, 'Z1', 80, "Retour au calme")
        ]
        
        workout = Workout(
            name="Threshold 3x(20-20-15)",
            description="Séance de seuil lactique pour améliorer le FTP",
            intervals=intervals,
            total_duration=100,
            estimated_tss=0,
            focus='threshold'
        )
        
        workout.estimated_tss = TrainingMetrics.estimate_workout_tss(workout, self.user.ftp)
        return workout
    
    def generate_vo2max_workout(self) -> Workout:
        """Génère une séance VO2max (intervals courts haute intensité)"""
        intervals = [
            WorkoutInterval(15, 'Z1', 85, "Échauffement"),
            WorkoutInterval(10, 'Z2', 90, "Préparation"),
        ]
        
        # 5 × (3min Z5 / 3min Z2)
        for i in range(5):
            intervals.append(WorkoutInterval(3, 'Z5', 100, f"Interval VO2max {i+1}/5 - respiration profonde"))
            if i < 4:  # Pas de récup après le dernier
                intervals.append(WorkoutInterval(3, 'Z2', 85, "Récupération active"))
        
        intervals.append(WorkoutInterval(15, 'Z1', 80, "Retour au calme"))
        
        workout = Workout(
            name="VO2max 5×3min",
            description="Séance VO2max pour développer la puissance maximale aérobie",
            intervals=intervals,
            total_duration=75,
            estimated_tss=0,
            focus='vo2max'
        )
        
        workout.estimated_tss = TrainingMetrics.estimate_workout_tss(workout, self.user.ftp)
        return workout

# === MOTEUR DE PÉRIODISATION ===

class PeriodizationEngine:
    """Moteur de périodisation basé sur la recherche récente"""
    
    def __init__(self, user_profile: UserProfile):
        self.user = user_profile
        self.generator = WorkoutGenerator(user_profile)
    
    def generate_weekly_plan(self, week_number: int, periodization_type: str = 'block') -> Dict:
        """
        Génère un plan hebdomadaire selon le modèle de périodisation
        
        Args:
            week_number: Semaine dans le cycle (1-4)
            periodization_type: 'block' ou 'traditional'
        """
        if periodization_type == 'block':
            return self._generate_block_week(week_number)
        else:
            return self._generate_traditional_week(week_number)
    
    def _generate_block_week(self, week_number: int) -> Dict:
        """Génère une semaine selon la Block Periodization"""
        
        # Distribution selon recherche récente : focus par bloc
        if week_number == 1:  # Semaine endurance
            workouts = {
                'monday': {'type': 'recovery', 'workout': None},
                'tuesday': self.generator.generate_endurance_workout(90),
                'wednesday': self.generator.generate_endurance_workout(60),
                'thursday': self.generator.generate_endurance_workout(120),
                'friday': {'type': 'recovery', 'workout': None},
                'saturday': self.generator.generate_endurance_workout(150),
                'sunday': {'type': 'recovery', 'workout': None}
            }
        elif week_number == 2:  # Semaine seuil
            workouts = {
                'monday': {'type': 'recovery', 'workout': None},
                'tuesday': self.generator.generate_threshold_workout(),
                'wednesday': self.generator.generate_endurance_workout(60),
                'thursday': self.generator.generate_threshold_workout(),
                'friday': {'type': 'recovery', 'workout': None},
                'saturday': self.generator.generate_endurance_workout(90),
                'sunday': {'type': 'recovery', 'workout': None}
            }
        elif week_number == 3:  # Semaine VO2max
            workouts = {
                'monday': {'type': 'recovery', 'workout': None},
                'tuesday': self.generator.generate_vo2max_workout(),
                'wednesday': self.generator.generate_endurance_workout(45),
                'thursday': self.generator.generate_vo2max_workout(),
                'friday': {'type': 'recovery', 'workout': None},
                'saturday': self.generator.generate_endurance_workout(75),
                'sunday': {'type': 'recovery', 'workout': None}
            }
        else:  # Semaine 4 - récupération
            workouts = {
                'monday': {'type': 'recovery', 'workout': None},
                'tuesday': self.generator.generate_endurance_workout(45),
                'wednesday': {'type': 'recovery', 'workout': None},
                'thursday': self.generator.generate_endurance_workout(60),
                'friday': {'type': 'recovery', 'workout': None},
                'saturday': self.generator.generate_endurance_workout(75),
                'sunday': {'type': 'recovery', 'workout': None}
            }
        
        # Calcul TSS hebdomadaire
        weekly_tss = sum([
            workout.estimated_tss for workout in workouts.values() 
            if isinstance(workout, Workout)
        ])
        
        return {
            'week_number': week_number,
            'focus': self._get_week_focus(week_number),
            'workouts': workouts,
            'weekly_tss': weekly_tss,
            'periodization': 'block'
        }
    
    def _get_week_focus(self, week_number: int) -> str:
        """Retourne le focus de la semaine selon le modèle block"""
        focuses = {1: 'Endurance Base', 2: 'Threshold', 3: 'VO2max', 4: 'Recovery'}
        return focuses.get(week_number, 'Mixed')

# === GÉNÉRATEUR DE FICHIERS ===

class FileGenerator:
    """Génère les fichiers .fit et .txt explicatifs"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/fit_files", exist_ok=True)
        os.makedirs(f"{output_dir}/explanations", exist_ok=True)
    
    def generate_workout_files(self, workout: Workout, user: UserProfile) -> Dict[str, str]:
        """Génère les fichiers .fit et .txt pour une séance"""
        
        # Nom de fichier sécurisé
        safe_name = "".join(c for c in workout.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Fichiers de sortie
        fit_filename = f"{self.output_dir}/fit_files/{safe_name}_{timestamp}.fit"
        txt_filename = f"{self.output_dir}/explanations/{safe_name}_{timestamp}.txt"
        
        # Génération fichier .fit (placeholder - sera implémenté avec fit-tool)
        self._generate_fit_file(workout, user, fit_filename)
        
        # Génération fichier explicatif
        self._generate_explanation_file(workout, user, txt_filename)
        
        return {
            'fit_file': fit_filename,
            'explanation_file': txt_filename
        }
    
    def _generate_fit_file(self, workout: Workout, user: UserProfile, filename: str):
        """Génère le fichier .fit (TODO: implémenter avec fit-tool)"""
        # Placeholder - sera implémenté avec la librairie fit-tool
        logger.info(f"TODO: Générer fichier FIT {filename}")
        
        # Pour l'instant, créer un fichier texte avec les données
        with open(filename.replace('.fit', '_data.txt'), 'w', encoding='utf-8') as f:
            f.write(f"# Données FIT pour {workout.name}\n")
            f.write(f"# Utilisateur: {user.name} (FTP: {user.ftp}W)\n\n")
            
            current_time = 0
            for i, interval in enumerate(workout.intervals):
                power_min, power_max = interval.get_power_range(user.ftp)
                power_avg = (power_min + power_max) / 2
                
                f.write(f"Interval {i+1}: {interval.duration_minutes}min\n")
                f.write(f"  Zone: {interval.power_zone} ({power_min}-{power_max}W, moy: {power_avg:.0f}W)\n")
                f.write(f"  Cadence: {interval.cadence_target or 90} rpm\n")
                f.write(f"  Temps: {current_time}-{current_time + interval.duration_minutes}min\n\n")
                
                current_time += interval.duration_minutes
    
    def _generate_explanation_file(self, workout: Workout, user: UserProfile, filename: str):
        """Génère le fichier explicatif détaillé"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"🚴 SÉANCE D'ENTRAÎNEMENT CYCLISTE - {workout.name.upper()}\n")
            f.write("=" * 60 + "\n\n")
            
            # Informations générales
            f.write(f"👤 CYCLISTE: {user.name}\n")
            f.write(f"📊 FTP: {user.ftp}W | Poids: {user.weight}kg | Ratio: {user.ftp/user.weight:.1f}W/kg\n")
            f.write(f"⏱️  DURÉE TOTALE: {workout.total_duration} minutes\n")
            f.write(f"🎯 FOCUS: {workout.focus.upper()}\n")
            f.write(f"📈 TSS ESTIMÉ: {workout.estimated_tss:.1f}\n\n")
            
            # Description
            f.write("📝 DESCRIPTION:\n")
            f.write(f"{workout.description}\n\n")
            
            # Détail des intervals
            f.write("🔄 STRUCTURE DE LA SÉANCE:\n")
            f.write("-" * 40 + "\n")
            
            for i, interval in enumerate(workout.intervals, 1):
                power_min, power_max = interval.get_power_range(user.ftp)
                zone_info = POWER_ZONES[interval.power_zone]
                
                f.write(f"{i:2d}. {interval.duration_minutes:2d}min | {interval.power_zone} ")
                f.write(f"({power_min}-{power_max}W) | {zone_info['name']}\n")
                f.write(f"    💡 {interval.description}\n")
                if interval.cadence_target:
                    f.write(f"    🔄 Cadence cible: {interval.cadence_target} rpm\n")
                f.write("\n")
            
            # Conseils scientifiques
            f.write("🧠 CONSEILS BASÉS SUR LA RECHERCHE:\n")
            f.write("-" * 40 + "\n")
            
            if workout.focus == 'endurance':
                f.write("• Maintenir une conversation possible (effort aérobie)\n")
                f.write("• Respiration nasale si possible\n")
                f.write("• Focus sur l'efficacité du pédalage\n")
                f.write("• Développe les adaptations mitochondriales\n")
                
            elif workout.focus == 'threshold':
                f.write("• Effort 'comfortablement dur' - limite de la conversation\n")
                f.write("• Maintenir la puissance stable sur chaque bloc\n")
                f.write("• Améliore l'utilisation du lactate comme carburant\n")
                f.write("• Crucial pour l'amélioration du FTP\n")
                
            elif workout.focus == 'vo2max':
                f.write("• Respiration profonde et contrôlée\n")
                f.write("• Accepter l'inconfort - normal à cette intensité\n")
                f.write("• Récupération active importante entre intervals\n")
                f.write("• Développe la capacité cardiovasculaire maximale\n")
            
            f.write("\n")
            
            # Nutrition et hydratation
            f.write("🥤 NUTRITION & HYDRATATION:\n")
            f.write("-" * 40 + "\n")
            f.write("• Avant: Glucides 1-2h avant (1-2g/kg poids corps)\n")
            f.write("• Pendant: 200-250ml d'eau toutes les 15-20min\n")
            if workout.total_duration > 90:
                f.write("• Pendant: 30-60g glucides/heure après 90min\n")
            f.write("• Après: Protéines + glucides dans les 30min\n\n")
            
            # Récupération
            f.write("💤 RÉCUPÉRATION:\n")
            f.write("-" * 40 + "\n")
            f.write("• Retour au calme de 10-15min minimum\n")
            f.write("• Étirements légers post-séance\n")
            f.write("• Sommeil: 7-9h pour adaptation optimale\n")
            f.write("• Jour suivant: Récupération active ou repos selon plan\n\n")
            
            # Métriques à surveiller
            f.write("📊 MÉTRIQUES À SURVEILLER:\n")
            f.write("-" * 40 + "\n")
            f.write("• Puissance moyenne et normalized power\n")
            f.write("• Fréquence cardiaque moyenne par zone\n")
            f.write("• Variabilité de la puissance (coefficient de variation)\n")
            f.write("• RPE (échelle de 1-10) pour chaque interval\n")
            f.write("• TSS final vs TSS planifié\n\n")
            
            f.write(f"Généré le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")
            f.write("Basé sur les recherches récentes en periodization cycliste 2023-2025\n")

# === INTERFACE PRINCIPALE ===

def main():
    """Fonction principale - démonstration du système"""
    
    print("🚴 Cycling Coach IA - Générateur de Programmes d'Entraînement")
    print("=" * 60)
    
    # Profil utilisateur exemple
    user = UserProfile(
        name="Jean Cycliste",
        age=35,
        weight=70,
        height=175,
        ftp=250,
        hr_max=185,
        experience_level="intermediate",
        weekly_hours=8,
        goals=["Améliorer FTP", "Course longue distance"]
    )
    
    print(f"👤 Profil: {user.name} | FTP: {user.ftp}W | Ratio: {user.ftp/user.weight:.1f}W/kg")
    print()
    
    # Initialisation des moteurs
    generator = WorkoutGenerator(user)
    periodization = PeriodizationEngine(user)
    file_gen = FileGenerator()
    
    # Génération d'exemples de séances
    workouts = [
        generator.generate_endurance_workout(90),
        generator.generate_threshold_workout(),
        generator.generate_vo2max_workout()
    ]
    
    print("📋 Séances générées:")
    for workout in workouts:
        print(f"  • {workout.name} - {workout.total_duration}min - TSS: {workout.estimated_tss:.1f}")
        
        # Génération des fichiers
        files = file_gen.generate_workout_files(workout, user)
        print(f"    📁 Fichiers: {os.path.basename(files['explanation_file'])}")
    
    print()
    
    # Génération plan hebdomadaire
    print("📅 Plan hebdomadaire (Block Periodization - Semaine 1):")
    weekly_plan = periodization.generate_weekly_plan(1, 'block')
    
    for day, workout in weekly_plan['workouts'].items():
        if isinstance(workout, Workout):
            print(f"  {day.capitalize():10}: {workout.name} (TSS: {workout.estimated_tss:.1f})")
        else:
            print(f"  {day.capitalize():10}: Récupération")
    
    print(f"\n📊 TSS hebdomadaire total: {weekly_plan['weekly_tss']:.1f}")
    print(f"🎯 Focus semaine: {weekly_plan['focus']}")
    
    print("\n✅ Démonstration terminée ! Consultez le dossier 'output' pour les fichiers générés.")

if __name__ == "__main__":
    main()