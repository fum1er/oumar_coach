#!/usr/bin/env python3
"""
Knowledge Base - Base de connaissances cycliste scientifique
"""

from typing import Dict, Any
from .models import PowerZone

# === BASE DE CONNAISSANCES CYCLISTE ===

# Zones de puissance selon la recherche récente
POWER_ZONES = {
    'Z1': PowerZone(
        name="Récupération Active",
        power_pct_ftp=(0.45, 0.55),
        hr_pct_max=(50, 60),
        cadence_rpm=(70, 80),
        objective="Récupération sanguine, élimination des déchets métaboliques",
        duration_typical="30-120 minutes",
        when_use="Jours de récupération, retour au calme, entre intervalles"
    ),
    'Z2': PowerZone(
        name="Endurance Aérobie",
        power_pct_ftp=(0.56, 0.75),
        hr_pct_max=(60, 75),
        cadence_rpm=(85, 95),
        objective="Améliorer endurance fondamentale, métabolisme des graisses, capacité aérobie",
        duration_typical="60-300 minutes",
        when_use="Base d'entraînement, sorties longues, échauffement final"
    ),
    'Z3': PowerZone(
        name="Tempo",
        power_pct_ftp=(0.76, 0.90),
        hr_pct_max=(76, 85),
        cadence_rpm=(85, 95),
        objective="Améliorer capacité aérobie sans fatigue excessive, endurance musculaire",
        duration_typical="20-90 minutes",
        when_use="Blocs tempo, préparation aux efforts soutenus"
    ),
    'Z4': PowerZone(
        name="Seuil Lactique (FTP)",
        power_pct_ftp=(0.91, 1.05),
        hr_pct_max=(88, 92),
        cadence_rpm=(85, 95),
        objective="Améliorer seuil anaérobie, FTP, capacité à maintenir efforts intenses",
        duration_typical="8-60 minutes par bloc",
        when_use="Améliorations FTP, préparation courses longues"
    ),
    'Z5': PowerZone(
        name="VO2max (PMA)",
        power_pct_ftp=(1.06, 1.20),
        hr_pct_max=(93, 100),
        cadence_rpm=(95, 105),
        objective="Améliorer puissance maximale aérobie, consommation d'oxygène",
        duration_typical="3-8 minutes par intervalle",
        when_use="Ascensions courtes, efforts en peloton, pic de forme"
    ),
    'Z6': PowerZone(
        name="Capacité Anaérobie",
        power_pct_ftp=(1.21, 1.50),
        hr_pct_max=(95, 100),
        cadence_rpm=(100, 120),
        objective="Améliorer capacité anaérobie, force explosive, sprints",
        duration_typical="30 secondes - 2 minutes",
        when_use="Sprints, montées explosives, finales de course"
    ),
    'Z7': PowerZone(
        name="Puissance Neuromusculaire",
        power_pct_ftp=(1.51, 3.00),
        hr_pct_max=(90, 100),
        cadence_rpm=(110, 130),
        objective="Améliorer coordination neuromusculaire, force maximale",
        duration_typical="5-15 secondes",
        when_use="Sprints courts, développement force explosive"
    )
}

# Structures d'entraînement validées
WORKOUT_STRUCTURES = {
    "warmup": {
        "duration_minutes": (10, 20),
        "progression": "Z1 → Z2 → Z3 optionnel",
        "power_pct_ftp": (0.50, 0.75),
        "cadence_rpm": (80, 90),
        "notes": "Progression graduelle, peut inclure micro-intervalles d'activation"
    },
    "cooldown": {
        "duration_minutes": (10, 20),
        "intensity": "Z1 stable",
        "power_pct_ftp": (0.40, 0.55),
        "cadence_rpm": (75, 85),
        "notes": "Élimination déchets métaboliques, favorise récupération"
    },
    "vo2max_intervals": {
        "duration_minutes": (3, 8),
        "intensity": "Z5",
        "recovery_ratio": "1:0.5 à 1:1",
        "repetitions": (3, 6),
        "recovery_intensity": "Z2",
        "notes": "Pousse PMA, améliore consommation O2, cadence élevée recommandée"
    },
    "threshold_intervals": {
        "duration_minutes": (8, 40),
        "intensity": "Z4",
        "recovery_ratio": "1:0.25 à 1:0.5",
        "repetitions": (2, 5),
        "recovery_intensity": "Z2",
        "notes": "Améliore FTP, sustainable power, cadence normale"
    }
}

# Adaptations selon niveau d'athlète
ATHLETE_ADAPTATIONS = {
    "beginner": {
        "vo2max_intervals": {"max_reps": 3, "max_duration": 3, "recovery_ratio": 1.0},
        "threshold_intervals": {"max_duration": 15, "recovery_ratio": 0.5},
        "weekly_intensity": 0.15,
        "max_workout_duration": 90,
        "recommended_frequency": 3
    },
    "intermediate": {
        "vo2max_intervals": {"max_reps": 5, "max_duration": 5, "recovery_ratio": 0.75},
        "threshold_intervals": {"max_duration": 25, "recovery_ratio": 0.25},
        "weekly_intensity": 0.20,
        "max_workout_duration": 120,
        "recommended_frequency": 4
    },
    "advanced": {
        "vo2max_intervals": {"max_reps": 6, "max_duration": 8, "recovery_ratio": 0.5},
        "threshold_intervals": {"max_duration": 40, "recovery_ratio": 0.25},
        "weekly_intensity": 0.25,
        "max_workout_duration": 180,
        "recommended_frequency": 5
    },
    "elite": {
        "vo2max_intervals": {"max_reps": 8, "max_duration": 8, "recovery_ratio": 0.5},
        "threshold_intervals": {"max_duration": 60, "recovery_ratio": 0.2},
        "weekly_intensity": 0.30,
        "max_workout_duration": 240,
        "recommended_frequency": 6
    }
}

# Recommandations nutritionnelles
NUTRITION_GUIDELINES = {
    "pre_workout": {
        "timing_hours": 1.5,
        "carbs_per_kg": (1, 2),
        "hydration_ml": 500,
        "notes": "Glucides facilement digestibles, éviter fibres et graisses"
    },
    "during_workout": {
        "carbs_per_hour": (30, 60),
        "hydration_ml_per_15min": (150, 250),
        "electrolytes": "Sodium 200-300mg/L",
        "notes": "Commencer à boire dès le début, glucides après 60-90min"
    },
    "post_workout": {
        "timing_minutes": 30,
        "carbs_per_kg": (1, 1.5),
        "protein_per_kg": (0.3, 0.5),
        "ratio_carbs_protein": "3:1 à 4:1",
        "notes": "Fenêtre d'opportunité pour récupération optimale"
    }
}

# Messages de coaching selon le contexte
COACHING_MESSAGES = {
    "vo2max": {
        "pre_workout": "Préparez-vous mentalement, ces intervalles vont être intenses !",
        "during_work": "Respirez profondément, maintenez la cadence élevée",
        "during_rest": "Récupération active, préparez le prochain effort",
        "post_workout": "Excellent travail ! Ces efforts vont booster votre VO2max"
    },
    "threshold": {
        "pre_workout": "Concentration et régularité seront clés aujourd'hui",
        "during_work": "Trouvez votre rythme de croisière, c'est 'comfortablement dur'",
        "during_rest": "Récupération courte, restez focalisé",
        "post_workout": "Parfait pour améliorer votre FTP et endurance !"
    },
    "endurance": {
        "pre_workout": "Longue séance aujourd'hui, économisez votre énergie",
        "during_work": "Conversation possible, rythme aérobie stable",
        "post_workout": "Base solide construite, excellente séance d'endurance !"
    }
}

class KnowledgeBaseManager:
    """Gestionnaire de la base de connaissances"""
    
    @staticmethod
    def get_zone_info(zone_id: str) -> PowerZone:
        """Récupère les informations d'une zone"""
        return POWER_ZONES.get(zone_id)
    
    @staticmethod
    def get_adaptations_for_level(level: str) -> Dict[str, Any]:
        """Récupère les adaptations pour un niveau"""
        return ATHLETE_ADAPTATIONS.get(level, ATHLETE_ADAPTATIONS["intermediate"])
    
    @staticmethod
    def get_workout_structure(structure_type: str) -> Dict[str, Any]:
        """Récupère une structure d'entraînement"""
        return WORKOUT_STRUCTURES.get(structure_type)
    
    @staticmethod
    def get_coaching_message(workout_type: str, phase: str) -> str:
        """Récupère un message de coaching"""
        messages = COACHING_MESSAGES.get(workout_type, {})
        return messages.get(phase, "Donnez le meilleur de vous-même !")
    
    @staticmethod
    def search_knowledge(query: str) -> str:
        """Recherche simple dans la base de connaissances"""
        results = []
        query_lower = query.lower()
        
        # Recherche dans les zones
        for zone_id, zone in POWER_ZONES.items():
            if any(term in query_lower for term in [
                zone_id.lower(), zone.name.lower(), 'zone', 'puissance'
            ]):
                results.append(f"Zone {zone_id} - {zone.name}: {zone.objective}")
        
        # Recherche dans les structures
        for structure, data in WORKOUT_STRUCTURES.items():
            if any(term in query_lower for term in [structure, 'structure', 'entrainement']):
                results.append(f"Structure {structure}: {data.get('notes', 'Informations disponibles')}")
        
        return "\n".join(results) if results else "Aucune information trouvée pour cette requête"