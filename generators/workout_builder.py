#!/usr/bin/env python3
"""
Workout Builder - Constructeur intelligent de séances d'entraînement
"""

from typing import List, Dict, Tuple

class WorkoutBuilder:
    """Constructeur intelligent de séances cyclistes"""
    
    def __init__(self):
        # Charger les modules de base
        try:
            from core.knowledge_base import POWER_ZONES, ATHLETE_ADAPTATIONS, KnowledgeBaseManager
            from core.models import WorkoutSegment, RepeatedInterval, SmartWorkout
            from core.calculations import TrainingCalculations
            
            self.power_zones = POWER_ZONES
            self.adaptations = ATHLETE_ADAPTATIONS
            self.knowledge_manager = KnowledgeBaseManager()
            self.calculator = TrainingCalculations()
            self.WorkoutSegment = WorkoutSegment
            self.RepeatedInterval = RepeatedInterval
            self.SmartWorkout = SmartWorkout
        except ImportError:
            # Import absolu si relatif échoue
            try:
                from core.knowledge_base import POWER_ZONES, ATHLETE_ADAPTATIONS, KnowledgeBaseManager
                from core.models import WorkoutSegment, RepeatedInterval, SmartWorkout
                from core.calculations import TrainingCalculations
                
                self.power_zones = POWER_ZONES
                self.adaptations = ATHLETE_ADAPTATIONS
                self.knowledge_manager = KnowledgeBaseManager()
                self.calculator = TrainingCalculations()
                self.WorkoutSegment = WorkoutSegment
                self.RepeatedInterval = RepeatedInterval
                self.SmartWorkout = SmartWorkout
            except ImportError as e:
                print(f"⚠️ Erreur import builder: {e}")
                raise
    
    def create_smart_workout(self, workout_type: str, duration: int, 
                           level: str, ftp: int, objectives: str = "") -> 'SmartWorkout':
        """Crée une séance intelligente selon les paramètres"""
        
        # Obtenir les adaptations pour le niveau
        level_adaptations = self.adaptations.get(level, self.adaptations["intermediate"])
        
        # Dispatcher selon le type
        if workout_type.lower() in ['vo2max', 'vo2', 'pma']:
            return self._create_vo2max_workout(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['threshold', 'seuil', 'ftp']:
            return self._create_threshold_workout(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['endurance', 'z2', 'base']:
            return self._create_endurance_workout(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['recovery', 'recuperation', 'z1']:
            return self._create_recovery_workout(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['tempo', 'z3']:
            return self._create_tempo_workout(duration, level, ftp, level_adaptations)
        else:
            # Par défaut, créer VO2max
            return self._create_vo2max_workout(duration, level, ftp, level_adaptations)
    
    def _create_vo2max_workout(self, duration: int, level: str, ftp: int, adaptations: Dict) -> 'SmartWorkout':
        """Crée une séance VO2max scientifiquement optimisée"""
        
        # Paramètres selon le niveau
        max_reps = adaptations["vo2max_intervals"]["max_reps"]
        max_duration = adaptations["vo2max_intervals"]["max_duration"]
        recovery_ratio = adaptations["vo2max_intervals"]["recovery_ratio"]
        
        # Zones de puissance
        z1_power = self.power_zones["Z1"].power_pct_ftp
        z2_power = self.power_zones["Z2"].power_pct_ftp
        z5_power = self.power_zones["Z5"].power_pct_ftp
        
        # Calcul des durées optimales
        work_duration = min(max_duration, 4)  # 3-4 min optimal pour VO2max
        rest_duration = max(2, int(work_duration * recovery_ratio))
        
        # Calculer nombre de répétitions possibles
        warmup_time = 15
        cooldown_time = 15
        activation_time = 10
        available_time = duration - warmup_time - cooldown_time - activation_time
        
        single_rep_time = work_duration + rest_duration
        calculated_reps = min(max_reps, available_time // single_rep_time)
        actual_reps = max(3, calculated_reps)  # Minimum 3 pour efficacité
        
        # Segments de base
        segments = [
            self.WorkoutSegment(
                type="Warmup",
                duration_minutes=warmup_time,
                power_pct_ftp=(z1_power[0], z2_power[0]),
                cadence_rpm=85,
                description="Échauffement progressif avec activation cardiovasculaire",
                scientific_rationale="Préparation du système cardiovasculaire et augmentation graduelle du flux sanguin musculaire"
            ),
            self.WorkoutSegment(
                type="SteadyState",
                duration_minutes=activation_time,
                power_pct_ftp=z2_power,
                cadence_rpm=90,
                description="Activation aérobie pré-intervalles",
                scientific_rationale="Activation des voies métaboliques aérobies avant les efforts en Zone 5"
            ),
            self.WorkoutSegment(
                type="Cooldown",
                duration_minutes=cooldown_time,
                power_pct_ftp=(z1_power[0] * 0.8, z1_power[1]),
                cadence_rpm=80,
                description="Retour au calme actif pour élimination lactate",
                scientific_rationale="Maintien circulation sanguine pour élimination déchets métaboliques"
            )
        ]
        
        # Intervalles répétés VO2max
        repeated_intervals = [
            self.RepeatedInterval(
                repetitions=actual_reps,
                work_duration=work_duration,
                work_power_pct=z5_power,
                work_cadence=100,
                rest_duration=rest_duration,
                rest_power_pct=z2_power,
                rest_cadence=85,
                work_description=f"VO2max Z5 - Puissance maximale aérobie",
                rest_description="Récupération active Z2 - Maintien flux sanguin",
                scientific_rationale=f"Intervalles {actual_reps}×{work_duration}min optimisés pour stimuler VO2max sans fatigue excessive pour niveau {level}"
            )
        ]
        
        return self.SmartWorkout(
            name=f"VO2max Optimisé {actual_reps}×{work_duration}min",
            type="vo2max",
            description=f"Séance VO2max scientifiquement optimisée pour niveau {level} : {actual_reps} intervalles de {work_duration} minutes en Zone 5",
            scientific_objective="Amélioration de la Puissance Maximale Aérobie (PMA) et de la consommation maximale d'oxygène (VO2max) à travers des intervalles spécifiques de 3-4 minutes à 106-120% FTP",
            total_duration=duration,
            segments=segments,
            repeated_intervals=repeated_intervals,
            ftp=ftp,
            adaptation_notes=f"Adapté pour {level}: {actual_reps} répétitions (max {max_reps}), récupération ratio {recovery_ratio}, cadence élevée (100 rpm) pour optimiser la vélocité",
            coaching_tips=f"Maintenez une cadence élevée (95-105 rpm), respirez profondément, acceptez l'inconfort en fin d'intervalle. Focus sur la régularité plutôt que les pics de puissance."
        )
    
    def _create_threshold_workout(self, duration: int, level: str, ftp: int, adaptations: Dict) -> 'SmartWorkout':
        """Crée une séance de seuil lactique optimisée"""
        
        max_duration = adaptations["threshold_intervals"]["max_duration"]
        recovery_ratio = adaptations["threshold_intervals"]["recovery_ratio"]
        
        # Zones de puissance
        z1_power = self.power_zones["Z1"].power_pct_ftp
        z2_power = self.power_zones["Z2"].power_pct_ftp
        z4_power = self.power_zones["Z4"].power_pct_ftp
        
        # Déterminer structure selon durée et niveau
        if duration >= 80 and max_duration >= 20:
            # Structure classique 2x20min
            work_blocks = [20, 20]
            recovery_time = int(20 * recovery_ratio)
        elif duration >= 65 and max_duration >= 15:
            # Structure alternative 3x15min
            work_blocks = [15, 15, 15]
            recovery_time = int(15 * recovery_ratio)
        else:
            # Bloc unique adapté
            available_work = duration - 30  # 15min warmup + 15min cooldown
            work_duration = min(max_duration, available_work)
            work_blocks = [work_duration]
            recovery_time = 0
        
        # Segments de base
        segments = [
            self.WorkoutSegment(
                type="Warmup",
                duration_minutes=15,
                power_pct_ftp=(z1_power[0], z2_power[1]),
                cadence_rpm=85,
                description="Échauffement progressif avec préparation au seuil",
                scientific_rationale="Préparation progressive au seuil lactique avec activation métabolique"
            ),
            self.WorkoutSegment(
                type="Cooldown",
                duration_minutes=15,
                power_pct_ftp=(z1_power[0] * 0.8, z1_power[1]),
                cadence_rpm=80,
                description="Retour au calme avec élimination lactate",
                scientific_rationale="Élimination progressive du lactate accumulé"
            )
        ]
        
        # Intervalles de seuil
        repeated_intervals = []
        for i, work_time in enumerate(work_blocks):
            repeated_intervals.append(
                self.RepeatedInterval(
                    repetitions=1,
                    work_duration=work_time,
                    work_power_pct=z4_power,
                    work_cadence=95,
                    rest_duration=recovery_time if i < len(work_blocks) - 1 else 0,
                    rest_power_pct=z2_power,
                    rest_cadence=85,
                    work_description=f"Bloc seuil {i+1}/{len(work_blocks)} - Maintenir FTP stable",
                    rest_description="Récupération active - Préparer bloc suivant",
                    scientific_rationale=f"Bloc {work_time}min au seuil lactique (91-105% FTP) pour améliorer la capacité à métaboliser le lactate"
                )
            )
        
        return self.SmartWorkout(
            name=f"Threshold {'+'.join(map(str, work_blocks))}min",
            type="threshold",
            description=f"Séance de seuil lactique avec {len(work_blocks)} bloc(s) pour améliorer le FTP et la capacité à maintenir des efforts soutenus",
            scientific_objective="Amélioration du seuil lactique (FTP) et de la capacité à maintenir des efforts soutenus à l'intensité critique",
            total_duration=duration,
            segments=segments,
            repeated_intervals=repeated_intervals,
            ftp=ftp,
            adaptation_notes=f"Adapté pour {level}: blocs de {work_blocks} minutes, récupération {recovery_ratio}, focus sur la régularité",
            coaching_tips="Effort 'comfortablement dur' - limite de conversation. Maintenez une puissance stable, respirez de façon contrôlée, restez aérodynamique."
        )
    
    def _create_endurance_workout(self, duration: int, level: str, ftp: int, adaptations: Dict) -> 'SmartWorkout':
        """Crée une séance d'endurance aérobie"""
        
        # Zones de puissance
        z1_power = self.power_zones["Z1"].power_pct_ftp
        z2_power = self.power_zones["Z2"].power_pct_ftp
        
        # Répartition du temps
        warmup_time = min(15, duration // 6)
        cooldown_time = min(15, duration // 6)
        main_time = duration - warmup_time - cooldown_time
        
        # Segments
        segments = [
            self.WorkoutSegment(
                type="Warmup",
                duration_minutes=warmup_time,
                power_pct_ftp=(z1_power[0], z2_power[0]),
                cadence_rpm=85,
                description="Échauffement progressif en douceur",
                scientific_rationale="Activation graduelle du système cardiovasculaire et préparation métabolique"
            ),
            self.WorkoutSegment(
                type="SteadyState",
                duration_minutes=main_time,
                power_pct_ftp=z2_power,
                cadence_rpm=90,
                description="Endurance aérobie stable - conversation possible",
                scientific_rationale="Développement des adaptations mitochondriales, amélioration de l'efficacité cardiaque et du métabolisme des graisses"
            ),
            self.WorkoutSegment(
                type="Cooldown",
                duration_minutes=cooldown_time,
                power_pct_ftp=(z1_power[0] * 0.8, z1_power[1]),
                cadence_rpm=85,
                description="Retour au calme progressif",
                scientific_rationale="Maintien de la circulation pour faciliter la récupération"
            )
        ]
        
        return self.SmartWorkout(
            name=f"Endurance {duration}min",
            type="endurance",
            description=f"Séance d'endurance aérobie de {main_time} minutes pour développer la base cardiovasculaire",
            scientific_objective="Développement de l'endurance fondamentale, amélioration de l'efficacité cardiaque et du métabolisme des graisses",
            total_duration=duration,
            segments=segments,
            repeated_intervals=[],
            ftp=ftp,
            adaptation_notes=f"Intensité modérée pour {level}, focus sur l'efficacité du pédalage et la respiration",
            coaching_tips="Maintenez une conversation possible, cadence fluide 85-95 rpm, respiration nasale si possible. Hydratez-vous régulièrement."
        )
    
    def _create_recovery_workout(self, duration: int, level: str, ftp: int, adaptations: Dict) -> 'SmartWorkout':
        """Crée une séance de récupération active"""
        
        z1_power = self.power_zones["Z1"].power_pct_ftp
        
        # Séance entièrement en Z1
        segments = [
            self.WorkoutSegment(
                type="SteadyState",
                duration_minutes=duration,
                power_pct_ftp=(z1_power[0] * 0.9, z1_power[1] * 0.9),  # Légèrement plus facile
                cadence_rpm=85,
                description="Récupération active - pédalage très fluide",
                scientific_rationale="Maintien circulation sanguine pour élimination déchets métaboliques et favoriser la récupération"
            )
        ]
        
        return self.SmartWorkout(
            name=f"Recovery {duration}min",
            type="recovery",
            description=f"Séance de récupération active de {duration} minutes pour favoriser la régénération",
            scientific_objective="Favoriser la récupération par maintien d'une circulation sanguine optimale et élimination des déchets métaboliques",
            total_duration=duration,
            segments=segments,
            repeated_intervals=[],
            ftp=ftp,
            adaptation_notes=f"Intensité très légère, focus sur la fluidité du mouvement",
            coaching_tips="Pédalage très décontracté, cadence naturelle, respiration profonde. L'objectif est la récupération, pas l'entraînement."
        )
    
    def _create_tempo_workout(self, duration: int, level: str, ftp: int, adaptations: Dict) -> 'SmartWorkout':
        """Crée une séance tempo (Z3)"""
        
        z1_power = self.power_zones["Z1"].power_pct_ftp
        z2_power = self.power_zones["Z2"].power_pct_ftp
        z3_power = self.power_zones["Z3"].power_pct_ftp
        
        # Structure avec blocs tempo
        warmup_time = 15
        cooldown_time = 15
        available_time = duration - warmup_time - cooldown_time
        
        # Blocs tempo selon durée
        if available_time >= 40:
            # 2 blocs de 20min
            tempo_blocks = [20, 20]
            recovery_between = 5
        elif available_time >= 25:
            # 1 bloc long
            tempo_blocks = [available_time - 5]
            recovery_between = 0
        else:
            # Bloc unique court
            tempo_blocks = [available_time]
            recovery_between = 0
        
        segments = [
            self.WorkoutSegment(
                type="Warmup",
                duration_minutes=warmup_time,
                power_pct_ftp=(z1_power[0], z2_power[1]),
                cadence_rpm=85,
                description="Échauffement progressif",
                scientific_rationale="Préparation au tempo"
            ),
            self.WorkoutSegment(
                type="Cooldown",
                duration_minutes=cooldown_time,
                power_pct_ftp=(z1_power[0], z1_power[1]),
                cadence_rpm=80,
                description="Retour au calme",
                scientific_rationale="Récupération progressive"
            )
        ]
        
        # Intervalles tempo
        repeated_intervals = []
        for i, block_duration in enumerate(tempo_blocks):
            repeated_intervals.append(
                self.RepeatedInterval(
                    repetitions=1,
                    work_duration=block_duration,
                    work_power_pct=z3_power,
                    work_cadence=90,
                    rest_duration=recovery_between if i < len(tempo_blocks) - 1 else 0,
                    rest_power_pct=z2_power,
                    rest_cadence=85,
                    work_description=f"Bloc tempo {i+1}/{len(tempo_blocks)} - Rythme soutenu",
                    rest_description="Récupération active",
                    scientific_rationale=f"Bloc tempo {block_duration}min en Zone 3 pour développer l'endurance musculaire"
                )
            )
        
        return self.SmartWorkout(
            name=f"Tempo {'+'.join(map(str, tempo_blocks))}min",
            type="tempo",
            description=f"Séance tempo avec {len(tempo_blocks)} bloc(s) pour développer l'endurance musculaire",
            scientific_objective="Développement de l'endurance musculaire et de la capacité aérobie par des efforts soutenus en Zone 3",
            total_duration=duration,
            segments=segments,
            repeated_intervals=repeated_intervals,
            ftp=ftp,
            adaptation_notes=f"Effort soutenu mais contrôlable pour {level}",
            coaching_tips="Rythme soutenu mais gérable, maintenir une respiration contrôlée. Idéal pour préparation aux courses longues."
        )