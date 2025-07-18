#!/usr/bin/env python3
"""
Calculations - Moteur de calculs scientifiques pour l'entraînement cycliste
"""

from typing import List, Tuple
from .models import WorkoutSegment, RepeatedInterval, SmartWorkout

class TrainingCalculations:
    """Calculs scientifiques pour l'entraînement cycliste"""
    
    @staticmethod
    def calculate_tss(segments: List[WorkoutSegment], 
                     intervals: List[RepeatedInterval], 
                     ftp: int) -> float:
        """
        Calcule le Training Stress Score (TSS) selon Coggan
        TSS = (duration_hours × NP × IF) / (FTP × 1.0) × 100
        """
        total_tss = 0
        
        # TSS des segments
        for segment in segments:
            avg_power_pct = (segment.power_pct_ftp[0] + segment.power_pct_ftp[1]) / 2
            duration_hours = segment.duration_minutes / 60
            # TSS = duration_hours * (intensity_factor^2) * 100
            tss = duration_hours * (avg_power_pct ** 2) * 100
            total_tss += tss
        
        # TSS des intervalles répétés
        for interval in intervals:
            # Work intervals
            work_avg_pct = (interval.work_power_pct[0] + interval.work_power_pct[1]) / 2
            work_duration_hours = (interval.work_duration * interval.repetitions) / 60
            work_tss = work_duration_hours * (work_avg_pct ** 2) * 100
            
            # Rest intervals
            if interval.rest_duration > 0:
                rest_avg_pct = (interval.rest_power_pct[0] + interval.rest_power_pct[1]) / 2
                rest_duration_hours = (interval.rest_duration * interval.repetitions) / 60
                rest_tss = rest_duration_hours * (rest_avg_pct ** 2) * 100
            else:
                rest_tss = 0
            
            total_tss += work_tss + rest_tss
        
        return total_tss
    
    @staticmethod
    def calculate_intensity_factor(workout: SmartWorkout) -> float:
        """Calcule le Facteur d'Intensité moyen de la séance"""
        total_weighted_power = 0
        total_duration = 0
        
        # Segments
        for segment in segments:
            avg_power_pct = (segment.power_pct_ftp[0] + segment.power_pct_ftp[1]) / 2
            duration = segment.duration_minutes
            total_weighted_power += avg_power_pct * duration
            total_duration += duration
        
        # Intervalles
        for interval in workout.repeated_intervals:
            # Work
            work_avg_pct = (interval.work_power_pct[0] + interval.work_power_pct[1]) / 2
            work_duration = interval.work_duration * interval.repetitions
            total_weighted_power += work_avg_pct * work_duration
            total_duration += work_duration
            
            # Rest
            if interval.rest_duration > 0:
                rest_avg_pct = (interval.rest_power_pct[0] + interval.rest_power_pct[1]) / 2
                rest_duration = interval.rest_duration * interval.repetitions
                total_weighted_power += rest_avg_pct * rest_duration
                total_duration += rest_duration
        
        return total_weighted_power / total_duration if total_duration > 0 else 0
    
    @staticmethod
    def calculate_high_intensity_time(workout: SmartWorkout, threshold_pct: float = 0.91) -> int:
        """Calcule le temps passé au-dessus d'un seuil (défaut: Z4+)"""
        high_intensity_time = 0
        
        # Segments
        for segment in workout.segments:
            if segment.power_pct_ftp[0] >= threshold_pct:
                high_intensity_time += segment.duration_minutes
        
        # Intervalles
        for interval in workout.repeated_intervals:
            if interval.work_power_pct[0] >= threshold_pct:
                high_intensity_time += interval.work_duration * interval.repetitions
        
        return high_intensity_time
    
    @staticmethod
    def estimate_recovery_time(tss: float, athlete_level: str = "intermediate") -> str:
        """Estime le temps de récupération selon le TSS et le niveau"""
        # Facteurs de récupération selon le niveau
        recovery_factors = {
            "beginner": 1.3,
            "intermediate": 1.0,
            "advanced": 0.8,
            "elite": 0.6
        }
        
        factor = recovery_factors.get(athlete_level, 1.0)
        adjusted_tss = tss * factor
        
        if adjusted_tss < 40:
            return "12-18 heures"
        elif adjusted_tss < 60:
            return "18-24 heures"
        elif adjusted_tss < 80:
            return "24-36 heures"
        elif adjusted_tss < 120:
            return "36-48 heures"
        else:
            return "48-72 heures"
    
    @staticmethod
    def calculate_power_zones(ftp: int) -> dict:
        """Calcule toutes les zones de puissance en watts"""
        from .knowledge_base import POWER_ZONES
        
        zones_watts = {}
        for zone_id, zone in POWER_ZONES.items():
            min_watts = int(ftp * zone.power_pct_ftp[0])
            max_watts = int(ftp * zone.power_pct_ftp[1])
            zones_watts[zone_id] = {
                'name': zone.name,
                'min_watts': min_watts,
                'max_watts': max_watts,
                'avg_watts': (min_watts + max_watts) // 2,
                'pct_ftp': zone.power_pct_ftp
            }
        
        return zones_watts
    
    @staticmethod
    def validate_workout_structure(workout: SmartWorkout) -> List[str]:
        """Valide la structure d'une séance et retourne les problèmes"""
        issues = []
        
        # Vérifier la durée
        calculated_duration = workout.calculate_actual_duration()
        if abs(calculated_duration - workout.total_duration) > 5:  # Tolérance 5 min
            issues.append(f"Durée incohérente: calculée {calculated_duration}min vs annoncée {workout.total_duration}min")
        
        # Vérifier les zones de puissance
        for segment in workout.segments:
            if segment.power_pct_ftp[0] < 0.4 or segment.power_pct_ftp[1] > 3.0:
                issues.append(f"Zone de puissance invalide dans segment: {segment.power_pct_ftp}")
            if segment.power_pct_ftp[0] >= segment.power_pct_ftp[1]:
                issues.append(f"Puissance min >= max dans segment: {segment.power_pct_ftp}")
        
        for interval in workout.repeated_intervals:
            if interval.work_power_pct[0] < 0.4 or interval.work_power_pct[1] > 3.0:
                issues.append(f"Zone de travail invalide: {interval.work_power_pct}")
            if interval.rest_power_pct[0] < 0.3 or interval.rest_power_pct[1] > 1.0:
                issues.append(f"Zone de repos invalide: {interval.rest_power_pct}")
        
        # Vérifier la structure logique
        if not workout.segments:
            issues.append("Aucun segment défini")
        
        # Chercher échauffement et retour au calme
        has_warmup = any(seg.type == "Warmup" for seg in workout.segments)
        has_cooldown = any(seg.type == "Cooldown" for seg in workout.segments)
        
        if not has_warmup and workout.total_duration > 30:
            issues.append("Échauffement recommandé pour séances > 30min")
        if not has_cooldown and workout.total_duration > 30:
            issues.append("Retour au calme recommandé pour séances > 30min")
        
        return issues
    
    @staticmethod
    def optimize_intervals_for_level(base_intervals: dict, level: str) -> dict:
        """Optimise les paramètres d'intervalles selon le niveau"""
        from .knowledge_base import ATHLETE_ADAPTATIONS
        
        adaptations = ATHLETE_ADAPTATIONS.get(level, ATHLETE_ADAPTATIONS["intermediate"])
        optimized = base_intervals.copy()
        
        if 'vo2max' in optimized:
            vo2_adapt = adaptations.get('vo2max_intervals', {})
            optimized['vo2max']['max_reps'] = min(
                optimized['vo2max'].get('repetitions', 5),
                vo2_adapt.get('max_reps', 5)
            )
            optimized['vo2max']['max_duration'] = min(
                optimized['vo2max'].get('work_duration', 4),
                vo2_adapt.get('max_duration', 4)
            )
        
        if 'threshold' in optimized:
            threshold_adapt = adaptations.get('threshold_intervals', {})
            optimized['threshold']['max_duration'] = min(
                optimized['threshold'].get('work_duration', 20),
                threshold_adapt.get('max_duration', 20)
            )
        
        return optimized