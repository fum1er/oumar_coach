#!/usr/bin/env python3
"""
Advanced Periodization System - Planification Multi-Semaines
Basé sur les théories des meilleurs coachs mondiaux (Coggan, Friel, Seiler, etc.)
"""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math

class PeriodizationModel(Enum):
    """Modèles de périodisation disponibles"""
    TRADITIONAL = "traditional"  # Periodization classique
    BLOCK = "block"              # Block periodization (Issurin)
    POLARIZED = "polarized"      # Polarized training (Seiler)
    PYRAMIDAL = "pyramidal"      # Pyramidal distribution
    REVERSE = "reverse"          # Reverse periodization

class TrainingPhase(Enum):
    """Phases d'entraînement"""
    BASE = "base"                # Phase de base
    BUILD = "build"              # Phase de développement
    PEAK = "peak"                # Phase de pic
    RECOVERY = "recovery"        # Phase de récupération
    COMPETITION = "competition"  # Phase de compétition
    TRANSITION = "transition"    # Phase de transition

@dataclass
class TrainingLoad:
    """Charge d'entraînement hebdomadaire"""
    tss_target: float
    hours_target: float
    intensity_distribution: Dict[str, float]  # Z1, Z2, Z3, Z4, Z5
    key_workouts: List[str]
    volume_emphasis: float  # 0-1
    intensity_emphasis: float  # 0-1

@dataclass
class WeeklyPlan:
    """Plan hebdomadaire détaillé"""
    week_number: int
    phase: TrainingPhase
    training_load: TrainingLoad
    workouts: Dict[str, Dict]  # {day: workout_info}
    focus: str
    rationale: str
    adaptations_expected: List[str]
    recovery_emphasis: float

@dataclass
class PeriodizationPlan:
    """Plan de périodisation complet"""
    athlete_id: str
    start_date: datetime
    end_date: datetime
    target_events: List[Dict]
    periodization_model: PeriodizationModel
    weekly_plans: List[WeeklyPlan]
    total_weeks: int
    current_ftp: int
    projected_ftp: int
    
class AdvancedPeriodizationEngine:
    """Moteur de périodisation avancé basé sur la science"""
    
    def __init__(self):
        # Charger les modèles scientifiques
        self.load_scientific_models()
        
        # Distributions d'intensité par modèle
        self.intensity_distributions = {
            PeriodizationModel.POLARIZED: {
                "Z1": 0.75, "Z2": 0.05, "Z3": 0.05, "Z4": 0.05, "Z5": 0.10
            },
            PeriodizationModel.PYRAMIDAL: {
                "Z1": 0.60, "Z2": 0.20, "Z3": 0.10, "Z4": 0.07, "Z5": 0.03
            },
            PeriodizationModel.TRADITIONAL: {
                "Z1": 0.50, "Z2": 0.25, "Z3": 0.15, "Z4": 0.07, "Z5": 0.03
            }
        }
        
        # Progressions de charge par phase
        self.load_progressions = {
            TrainingPhase.BASE: [0.7, 0.8, 0.9, 0.6],      # 3+1 pattern
            TrainingPhase.BUILD: [0.8, 0.9, 1.0, 0.7],     # Build pattern
            TrainingPhase.PEAK: [0.9, 1.0, 0.8, 0.5],      # Peak pattern
            TrainingPhase.RECOVERY: [0.4, 0.5, 0.6, 0.7],  # Recovery pattern
        }
    
    def load_scientific_models(self):
        """Charge les modèles scientifiques des grands coachs"""
        
        # Modèle Coggan (Training and Racing with a Power Meter)
        self.coggan_model = {
            "phase_duration": {
                TrainingPhase.BASE: 8,      # 8 semaines
                TrainingPhase.BUILD: 8,     # 8 semaines
                TrainingPhase.PEAK: 4,      # 4 semaines
                TrainingPhase.RECOVERY: 1   # 1 semaine
            },
            "ftp_improvement": {
                "beginner": 0.15,     # 15% amélioration possible
                "intermediate": 0.08,  # 8% amélioration
                "advanced": 0.05      # 5% amélioration
            }
        }
        
        # Modèle Friel (The Cyclist's Training Bible)
        self.friel_model = {
            "abilities": {
                "endurance": {"zones": ["Z1", "Z2"], "emphasis": [0.3, 0.7]},
                "force": {"zones": ["Z4", "Z5"], "emphasis": [0.7, 0.3]},
                "speed_skills": {"zones": ["Z6", "Z7"], "emphasis": [0.5, 0.5]},
                "muscular_endurance": {"zones": ["Z3", "Z4"], "emphasis": [0.4, 0.6]},
                "anaerobic_endurance": {"zones": ["Z5", "Z6"], "emphasis": [0.6, 0.4]},
                "power": {"zones": ["Z6", "Z7"], "emphasis": [0.3, 0.7]}
            }
        }
        
        # Modèle Seiler (Polarized Training)
        self.seiler_model = {
            "polarized_split": {
                "low_intensity": 0.80,    # 80% du temps
                "moderate_intensity": 0.00, # 0% du temps (éviter Z3)
                "high_intensity": 0.20    # 20% du temps
            },
            "weekly_structure": {
                "hard_days": 2,   # 2 jours intenses max
                "easy_days": 4,   # 4 jours faciles
                "rest_days": 1    # 1 jour repos
            }
        }
    
    def create_periodization_plan(self, 
                                athlete_profile: Dict,
                                target_events: List[Dict],
                                duration_weeks: int,
                                model: PeriodizationModel = PeriodizationModel.POLARIZED) -> PeriodizationPlan:
        """Crée un plan de périodisation complet"""
        
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Déterminer les phases
        phases = self._calculate_phases(duration_weeks, target_events)
        
        # Créer les plans hebdomadaires
        weekly_plans = []
        current_week = 1
        
        for phase_info in phases:
            phase_weeks = self._create_phase_weeks(
                phase_info, current_week, athlete_profile, model
            )
            weekly_plans.extend(phase_weeks)
            current_week += len(phase_weeks)
        
        # Projeter l'amélioration FTP
        projected_ftp = self._calculate_projected_ftp(
            athlete_profile["ftp"], 
            athlete_profile["experience_level"], 
            duration_weeks
        )
        
        return PeriodizationPlan(
            athlete_id=athlete_profile["user_id"],
            start_date=start_date,
            end_date=end_date,
            target_events=target_events,
            periodization_model=model,
            weekly_plans=weekly_plans,
            total_weeks=duration_weeks,
            current_ftp=athlete_profile["ftp"],
            projected_ftp=projected_ftp
        )
    
    def _calculate_phases(self, duration_weeks: int, target_events: List[Dict]) -> List[Dict]:
        """Calcule les phases optimales selon les événements cibles"""
        
        if not target_events:
            # Plan standard sans événement spécifique
            return self._create_standard_phases(duration_weeks)
        
        # Plan axé sur les événements
        main_event = target_events[0]  # Événement principal
        event_date = datetime.strptime(main_event["date"], "%Y-%m-%d")
        
        # Calculer les phases en rétroplanification
        phases = []
        
        # Phase de pic (2-3 semaines avant l'événement)
        peak_weeks = 3
        phases.append({
            "phase": TrainingPhase.PEAK,
            "weeks": peak_weeks,
            "end_week": duration_weeks - 1,
            "description": f"Pic pour {main_event['name']}"
        })
        
        # Phase de développement (6-8 semaines)
        build_weeks = min(8, duration_weeks - peak_weeks - 2)
        phases.append({
            "phase": TrainingPhase.BUILD,
            "weeks": build_weeks,
            "end_week": duration_weeks - peak_weeks - 1,
            "description": "Développement spécifique"
        })
        
        # Phase de base (reste du temps)
        base_weeks = duration_weeks - peak_weeks - build_weeks
        if base_weeks > 0:
            phases.append({
                "phase": TrainingPhase.BASE,
                "weeks": base_weeks,
                "end_week": build_weeks,
                "description": "Construction de la base aérobie"
            })
        
        return list(reversed(phases))  # Remettre dans l'ordre chronologique
    
    def _create_standard_phases(self, duration_weeks: int) -> List[Dict]:
        """Crée des phases standard sans événement spécifique"""
        
        phases = []
        
        if duration_weeks >= 12:
            # Plan long terme
            base_ratio = 0.5
            build_ratio = 0.3
            peak_ratio = 0.2
        elif duration_weeks >= 8:
            # Plan moyen terme
            base_ratio = 0.4
            build_ratio = 0.4
            peak_ratio = 0.2
        else:
            # Plan court terme
            base_ratio = 0.3
            build_ratio = 0.5
            peak_ratio = 0.2
        
        base_weeks = max(1, int(duration_weeks * base_ratio))
        build_weeks = max(1, int(duration_weeks * build_ratio))
        peak_weeks = duration_weeks - base_weeks - build_weeks
        
        phases.append({
            "phase": TrainingPhase.BASE,
            "weeks": base_weeks,
            "description": "Développement de la base aérobie"
        })
        
        phases.append({
            "phase": TrainingPhase.BUILD,
            "weeks": build_weeks,
            "description": "Développement de la puissance"
        })
        
        phases.append({
            "phase": TrainingPhase.PEAK,
            "weeks": peak_weeks,
            "description": "Optimisation de la forme"
        })
        
        return phases
    
    def _create_phase_weeks(self, phase_info: Dict, start_week: int, 
                           athlete_profile: Dict, model: PeriodizationModel) -> List[WeeklyPlan]:
        """Crée les semaines d'une phase"""
        
        phase = phase_info["phase"]
        weeks_count = phase_info["weeks"]
        weekly_plans = []
        
        # Charge de base selon le niveau
        base_tss = self._calculate_base_tss(athlete_profile)
        
        # Progression de charge pour cette phase
        load_progression = self.load_progressions[phase]
        
        for week_offset in range(weeks_count):
            week_number = start_week + week_offset
            
            # Calculer la charge pour cette semaine
            progress_index = week_offset % len(load_progression)
            load_multiplier = load_progression[progress_index]
            
            # Ajuster selon la phase
            phase_multiplier = self._get_phase_multiplier(phase)
            week_tss = base_tss * phase_multiplier * load_multiplier
            
            # Distribution d'intensité selon le modèle
            intensity_dist = self._get_intensity_distribution(phase, model)
            
            # Créer la charge d'entraînement
            training_load = TrainingLoad(
                tss_target=week_tss,
                hours_target=week_tss / 60,  # Approximation
                intensity_distribution=intensity_dist,
                key_workouts=self._select_key_workouts(phase, week_offset),
                volume_emphasis=self._get_volume_emphasis(phase),
                intensity_emphasis=self._get_intensity_emphasis(phase)
            )
            
            # Créer le plan hebdomadaire
            weekly_plan = WeeklyPlan(
                week_number=week_number,
                phase=phase,
                training_load=training_load,
                workouts=self._create_weekly_workouts(phase, training_load),
                focus=self._get_phase_focus(phase),
                rationale=self._get_phase_rationale(phase, week_offset),
                adaptations_expected=self._get_expected_adaptations(phase),
                recovery_emphasis=self._get_recovery_emphasis(phase, progress_index)
            )
            
            weekly_plans.append(weekly_plan)
        
        return weekly_plans
    
    def _calculate_base_tss(self, athlete_profile: Dict) -> float:
        """Calcule la charge TSS de base selon le profil"""
        
        experience_multipliers = {
            "beginner": 250,
            "intermediate": 350,
            "advanced": 450,
            "elite": 550
        }
        
        base_tss = experience_multipliers.get(
            athlete_profile.get("experience_level", "intermediate"), 350
        )
        
        # Ajuster selon le temps disponible
        available_hours = athlete_profile.get("available_time", {})
        weekly_hours = available_hours.get("weekdays", 5) + available_hours.get("weekends", 8)
        
        # Normaliser selon les heures disponibles
        if weekly_hours < 6:
            base_tss *= 0.7
        elif weekly_hours > 12:
            base_tss *= 1.3
        
        return base_tss
    
    def _get_phase_multiplier(self, phase: TrainingPhase) -> float:
        """Multiplicateur de charge selon la phase"""
        multipliers = {
            TrainingPhase.BASE: 0.9,
            TrainingPhase.BUILD: 1.1,
            TrainingPhase.PEAK: 1.0,
            TrainingPhase.RECOVERY: 0.5
        }
        return multipliers.get(phase, 1.0)
    
    def _get_intensity_distribution(self, phase: TrainingPhase, 
                                   model: PeriodizationModel) -> Dict[str, float]:
        """Distribution d'intensité selon phase et modèle"""
        
        base_dist = self.intensity_distributions.get(model, 
                                                   self.intensity_distributions[PeriodizationModel.POLARIZED])
        
        # Ajuster selon la phase
        if phase == TrainingPhase.BASE:
            # Plus d'endurance en phase de base
            return {
                "Z1": base_dist["Z1"] * 1.2,
                "Z2": base_dist["Z2"] * 1.1,
                "Z3": base_dist["Z3"] * 0.8,
                "Z4": base_dist["Z4"] * 0.6,
                "Z5": base_dist["Z5"] * 0.5
            }
        elif phase == TrainingPhase.BUILD:
            # Plus d'intensité en phase de développement
            return {
                "Z1": base_dist["Z1"] * 0.9,
                "Z2": base_dist["Z2"] * 0.9,
                "Z3": base_dist["Z3"] * 1.2,
                "Z4": base_dist["Z4"] * 1.3,
                "Z5": base_dist["Z5"] * 1.5
            }
        elif phase == TrainingPhase.PEAK:
            # Intensité ciblée en phase de pic
            return {
                "Z1": base_dist["Z1"] * 1.1,
                "Z2": base_dist["Z2"] * 0.8,
                "Z3": base_dist["Z3"] * 0.9,
                "Z4": base_dist["Z4"] * 1.2,
                "Z5": base_dist["Z5"] * 1.8
            }
        
        return base_dist
    
    def _select_key_workouts(self, phase: TrainingPhase, week_offset: int) -> List[str]:
        """Sélectionne les séances clés selon la phase"""
        
        workout_library = {
            TrainingPhase.BASE: [
                "Endurance 90-120min",
                "Tempo 2x20min",
                "Endurance 60min + Force"
            ],
            TrainingPhase.BUILD: [
                "Threshold 2x20min",
                "VO2max 5x4min",
                "Endurance 90min"
            ],
            TrainingPhase.PEAK: [
                "VO2max 6x3min",
                "Anaerobic 5x2min",
                "Openers 3x1min"
            ]
        }
        
        return workout_library.get(phase, ["Endurance 60min"])
    
    def _create_weekly_workouts(self, phase: TrainingPhase, 
                               training_load: TrainingLoad) -> Dict[str, Dict]:
        """Crée la répartition hebdomadaire des séances"""
        
        workouts = {}
        
        # Structure selon le modèle Seiler (2 jours intenses, 4 faciles, 1 repos)
        if phase == TrainingPhase.BASE:
            workouts = {
                "monday": {"type": "endurance", "duration": 60, "intensity": "Z2"},
                "tuesday": {"type": "threshold", "duration": 90, "intensity": "Z4"},
                "wednesday": {"type": "recovery", "duration": 45, "intensity": "Z1"},
                "thursday": {"type": "endurance", "duration": 90, "intensity": "Z2"},
                "friday": {"type": "rest"},
                "saturday": {"type": "endurance", "duration": 120, "intensity": "Z2"},
                "sunday": {"type": "recovery", "duration": 60, "intensity": "Z1"}
            }
        elif phase == TrainingPhase.BUILD:
            workouts = {
                "monday": {"type": "recovery", "duration": 45, "intensity": "Z1"},
                "tuesday": {"type": "vo2max", "duration": 75, "intensity": "Z5"},
                "wednesday": {"type": "endurance", "duration": 60, "intensity": "Z2"},
                "thursday": {"type": "threshold", "duration": 90, "intensity": "Z4"},
                "friday": {"type": "rest"},
                "saturday": {"type": "endurance", "duration": 90, "intensity": "Z2"},
                "sunday": {"type": "recovery", "duration": 60, "intensity": "Z1"}
            }
        elif phase == TrainingPhase.PEAK:
            workouts = {
                "monday": {"type": "recovery", "duration": 45, "intensity": "Z1"},
                "tuesday": {"type": "vo2max", "duration": 60, "intensity": "Z5"},
                "wednesday": {"type": "rest"},
                "thursday": {"type": "openers", "duration": 45, "intensity": "Z6"},
                "friday": {"type": "rest"},
                "saturday": {"type": "endurance", "duration": 60, "intensity": "Z2"},
                "sunday": {"type": "recovery", "duration": 45, "intensity": "Z1"}
            }
        
        return workouts
    
    def _get_phase_focus(self, phase: TrainingPhase) -> str:
        """Retourne le focus principal de la phase"""
        focuses = {
            TrainingPhase.BASE: "Développement de la base aérobie",
            TrainingPhase.BUILD: "Développement de la puissance spécifique",
            TrainingPhase.PEAK: "Optimisation de la forme et récupération",
            TrainingPhase.RECOVERY: "Récupération et régénération"
        }
        return focuses.get(phase, "Entraînement général")
    
    def _get_phase_rationale(self, phase: TrainingPhase, week_offset: int) -> str:
        """Justification scientifique de la phase"""
        
        base_rationales = {
            TrainingPhase.BASE: "Développement des adaptations cardiovasculaires et mitochondriales par un volume élevé en Zone 2",
            TrainingPhase.BUILD: "Amélioration de la puissance spécifique et de la tolérance lactique par des intervalles ciblés",
            TrainingPhase.PEAK: "Optimisation neuromusculaire et récupération avant compétition"
        }
        
        return base_rationales.get(phase, "Entraînement adapté au niveau")
    
    def _get_expected_adaptations(self, phase: TrainingPhase) -> List[str]:
        """Adaptations physiologiques attendues"""
        
        adaptations = {
            TrainingPhase.BASE: [
                "Augmentation de la densité mitochondriale",
                "Amélioration de l'efficacité cardiaque",
                "Optimisation du métabolisme des graisses",
                "Renforcement des tissus conjonctifs"
            ],
            TrainingPhase.BUILD: [
                "Amélioration de la VO2max",
                "Augmentation de la puissance au seuil",
                "Amélioration de la tolérance lactique",
                "Développement de la force spécifique"
            ],
            TrainingPhase.PEAK: [
                "Optimisation neuromusculaire",
                "Amélioration de l'économie de mouvement",
                "Récupération des systèmes énergétiques",
                "Affûtage psychologique"
            ]
        }
        
        return adaptations.get(phase, ["Adaptations générales"])
    
    def _get_volume_emphasis(self, phase: TrainingPhase) -> float:
        """Emphase sur le volume (0-1)"""
        emphases = {
            TrainingPhase.BASE: 0.8,
            TrainingPhase.BUILD: 0.6,
            TrainingPhase.PEAK: 0.3
        }
        return emphases.get(phase, 0.5)
    
    def _get_intensity_emphasis(self, phase: TrainingPhase) -> float:
        """Emphase sur l'intensité (0-1)"""
        emphases = {
            TrainingPhase.BASE: 0.2,
            TrainingPhase.BUILD: 0.7,
            TrainingPhase.PEAK: 0.8
        }
        return emphases.get(phase, 0.5)
    
    def _get_recovery_emphasis(self, phase: TrainingPhase, week_in_cycle: int) -> float:
        """Emphase sur la récupération selon le cycle"""
        
        base_recovery = {
            TrainingPhase.BASE: 0.3,
            TrainingPhase.BUILD: 0.4,
            TrainingPhase.PEAK: 0.6
        }.get(phase, 0.4)
        
        # Semaine de récupération tous les 3-4 semaines
        if week_in_cycle == 3:  # 4e semaine = récupération
            return base_recovery * 1.5
        
        return base_recovery
    
    def _calculate_projected_ftp(self, current_ftp: int, level: str, weeks: int) -> int:
        """Calcule l'amélioration FTP projetée"""
        
        # Potentiel d'amélioration selon Coggan
        improvement_rates = self.coggan_model["ftp_improvement"]
        max_improvement = improvement_rates.get(level, 0.08)
        
        # Facteur temporel (amélioration logarithmique)
        time_factor = min(1.0, weeks / 20)  # Plateau après 20 semaines
        
        # Calcul de l'amélioration
        improvement = current_ftp * max_improvement * time_factor
        
        return int(current_ftp + improvement)
    
    def export_plan_to_json(self, plan: PeriodizationPlan, filename: str):
        """Exporte le plan en JSON"""
        
        def convert_enums(obj):
            """Convertit les enums en strings pour JSON"""
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        plan_dict = asdict(plan)
        
        # Convertir les enums
        for key, value in plan_dict.items():
            if isinstance(value, Enum):
                plan_dict[key] = value.value
        
        # Convertir les dates
        plan_dict["start_date"] = plan.start_date.isoformat()
        plan_dict["end_date"] = plan.end_date.isoformat()
        
        # Convertir les phases dans weekly_plans
        for week in plan_dict["weekly_plans"]:
            week["phase"] = week["phase"].value
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan_dict, f, indent=2, ensure_ascii=False)
    
    def create_training_calendar(self, plan: PeriodizationPlan) -> Dict:
        """Crée un calendrier d'entraînement détaillé"""
        
        calendar = {
            "athlete_id": plan.athlete_id,
            "plan_overview": {
                "duration_weeks": plan.total_weeks,
                "periodization_model": plan.periodization_model.value,
                "ftp_progression": f"{plan.current_ftp}W → {plan.projected_ftp}W",
                "target_events": plan.target_events
            },
            "weekly_calendar": []
        }
        
        current_date = plan.start_date
        
        for week_plan in plan.weekly_plans:
            week_info = {
                "week_number": week_plan.week_number,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "phase": week_plan.phase.value,
                "focus": week_plan.focus,
                "target_tss": week_plan.training_load.tss_target,
                "target_hours": week_plan.training_load.hours_target,
                "daily_workouts": {}
            }
            
            # Créer les séances quotidiennes
            for day, workout_info in week_plan.workouts.items():
                day_date = current_date + timedelta(days=list(week_plan.workouts.keys()).index(day))
                
                week_info["daily_workouts"][day] = {
                    "date": day_date.strftime("%Y-%m-%d"),
                    "workout": workout_info,
                    "rationale": f"Semaine {week_plan.week_number} - {week_plan.phase.value}"
                }
            
            calendar["weekly_calendar"].append(week_info)
            current_date += timedelta(weeks=1)
        
        return calendar

# === EXEMPLE D'UTILISATION ===

def create_example_plan():
    """Crée un plan d'exemple pour démonstration"""
    
    # Profil athlète
    athlete_profile = {
        "user_id": "cyclist_001",
        "name": "Jean Cycliste",
        "ftp": 320,
        "experience_level": "intermediate",
        "available_time": {"weekdays": 8, "weekends": 12},
        "primary_goals": ["improve_ftp", "racing"]
    }
    
    # Événements cibles
    target_events = [
        {
            "name": "Course FFC Open 3",
            "date": "2025-09-15",
            "type": "road_race",
            "priority": "A"
        }
    ]
    
    # Créer le moteur de périodisation
    engine = AdvancedPeriodizationEngine()
    
    # Créer le plan (16 semaines)
    plan = engine.create_periodization_plan(
        athlete_profile=athlete_profile,
        target_events=target_events,
        duration_weeks=16,
        model=PeriodizationModel.POLARIZED
    )
    
    # Exporter le plan
    engine.export_plan_to_json(plan, "plan_periodization_16w.json")
    
    # Créer le calendrier
    calendar = engine.create_training_calendar(plan)
    
    return plan, calendar

if __name__ == "__main__":
    print("🚴 Création d'un plan de périodisation d'exemple...")
    plan, calendar = create_example_plan()
    
    print(f"✅ Plan créé: {plan.total_weeks} semaines")
    print(f"📈 FTP: {plan.current_ftp}W → {plan.projected_ftp}W")
    print(f"🎯 Modèle: {plan.periodization_model.value}")
    print(f"📅 Événements: {len(plan.target_events)}")
    
    # Afficher les premières semaines
    print("\n📋 Premières semaines:")
    for i, week in enumerate(plan.weekly_plans[:4]):
        print(f"  S{week.week_number}: {week.phase.value} - TSS {week.training_load.tss_target:.0f} - {week.focus}")