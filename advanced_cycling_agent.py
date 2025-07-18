#!/usr/bin/env python3
"""
Cycling AI Agent - Version Avancée Corrigée
Corrige les problèmes de l'agent original et améliore la fonctionnalité
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import re

# Charger le .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# LangChain imports avec gestion d'erreur et imports corrects
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.tools import BaseTool
    from langchain.agents import create_openai_functions_agent, AgentExecutor
    from langchain.schema import Document
    from langchain_community.vectorstores import FAISS  # Import corrigé
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LangChain non installé complètement. Erreur: {e}")
    print("Utilisez: pip install langchain langchain-openai langchain-community faiss-cpu")
    LANGCHAIN_AVAILABLE = False

# === BASE DE CONNAISSANCES CYCLISTE ===

CYCLING_KNOWLEDGE_BASE = {
    "zones_definition": {
        "Z1": {
            "name": "Récupération Active",
            "power_pct_ftp": [0.45, 0.55],
            "hr_pct_max": [50, 60],
            "cadence_rpm": [70, 80],
            "objective": "Récupération sanguine, élimination des déchets métaboliques",
            "duration_typical": "30-120 minutes",
            "when_use": "Jours de récupération, retour au calme, entre intervalles"
        },
        "Z2": {
            "name": "Endurance Aérobie",
            "power_pct_ftp": [0.56, 0.75],
            "hr_pct_max": [60, 75],
            "cadence_rpm": [85, 95],
            "objective": "Améliorer endurance fondamentale, métabolisme des graisses, capacité aérobie",
            "duration_typical": "60-300 minutes",
            "when_use": "Base d'entraînement, sorties longues, échauffement final"
        },
        "Z3": {
            "name": "Tempo",
            "power_pct_ftp": [0.76, 0.90],
            "hr_pct_max": [76, 85],
            "cadence_rpm": [85, 95],
            "objective": "Améliorer capacité aérobie sans fatigue excessive, endurance musculaire",
            "duration_typical": "20-90 minutes",
            "when_use": "Blocs tempo, préparation aux efforts soutenus"
        },
        "Z4": {
            "name": "Seuil Lactique (FTP)",
            "power_pct_ftp": [0.91, 1.05],
            "hr_pct_max": [88, 92],
            "cadence_rpm": [85, 95],
            "objective": "Améliorer seuil anaérobie, FTP, capacité à maintenir efforts intenses",
            "duration_typical": "8-60 minutes par bloc",
            "when_use": "Améliorations FTP, préparation courses longues"
        },
        "Z5": {
            "name": "VO2max (PMA)",
            "power_pct_ftp": [1.06, 1.20],
            "hr_pct_max": [93, 100],
            "cadence_rpm": [95, 105],
            "objective": "Améliorer puissance maximale aérobie, consommation d'oxygène",
            "duration_typical": "3-8 minutes par intervalle",
            "when_use": "Ascensions courtes, efforts en peloton, pic de forme"
        },
        "Z6": {
            "name": "Capacité Anaérobie",
            "power_pct_ftp": [1.21, 1.50],
            "hr_pct_max": [95, 100],
            "cadence_rpm": [100, 120],
            "objective": "Améliorer capacité anaérobie, force explosive, sprints",
            "duration_typical": "30 secondes - 2 minutes",
            "when_use": "Sprints, montées explosives, finales de course"
        },
        "Z7": {
            "name": "Puissance Neuromusculaire",
            "power_pct_ftp": [1.51, 3.00],
            "hr_pct_max": [90, 100],
            "cadence_rpm": [110, 130],
            "objective": "Améliorer coordination neuromusculaire, force maximale",
            "duration_typical": "5-15 secondes",
            "when_use": "Sprints courts, développement force explosive"
        }
    },
    
    "workout_structures": {
        "warmup": {
            "duration_minutes": [10, 20],
            "progression": "Z1 → Z2 → Z3 optionnel",
            "power_pct_ftp": [0.50, 0.75],
            "cadence_rpm": [80, 90],
            "notes": "Progression graduelle, peut inclure micro-intervalles d'activation"
        },
        "cooldown": {
            "duration_minutes": [10, 20],
            "intensity": "Z1 stable",
            "power_pct_ftp": [0.40, 0.55],
            "cadence_rpm": [75, 85],
            "notes": "Élimination déchets métaboliques, favorise récupération"
        },
        "vo2max_intervals": {
            "duration_minutes": [3, 8],
            "intensity": "Z5",
            "recovery_ratio": "1:0.5 à 1:1",
            "repetitions": [3, 6],
            "recovery_intensity": "Z2",
            "notes": "Pousse PMA, améliore consommation O2, cadence élevée recommandée"
        },
        "threshold_intervals": {
            "duration_minutes": [8, 40],
            "intensity": "Z4",
            "recovery_ratio": "1:0.25 à 1:0.5",
            "repetitions": [2, 5],
            "recovery_intensity": "Z2",
            "notes": "Améliore FTP, sustainable power, cadence normale"
        }
    },
    
    "athlete_adaptations": {
        "beginner": {
            "vo2max_intervals": {"max_reps": 3, "max_duration": 3, "recovery_ratio": "1:1"},
            "threshold_intervals": {"max_duration": 15, "recovery_ratio": "1:0.5"},
            "weekly_intensity": 0.15
        },
        "intermediate": {
            "vo2max_intervals": {"max_reps": 5, "max_duration": 5, "recovery_ratio": "1:0.75"},
            "threshold_intervals": {"max_duration": 25, "recovery_ratio": "1:0.25"},
            "weekly_intensity": 0.20
        },
        "advanced": {
            "vo2max_intervals": {"max_reps": 6, "max_duration": 8, "recovery_ratio": "1:0.5"},
            "threshold_intervals": {"max_duration": 40, "recovery_ratio": "1:0.25"},
            "weekly_intensity": 0.25
        }
    }
}

# === STRUCTURES DE DONNÉES AMÉLIORÉES ===

@dataclass
class WorkoutSegment:
    """Segment d'entraînement avec justification scientifique"""
    type: str
    duration_minutes: int
    power_pct_ftp: Tuple[float, float]
    cadence_rpm: int
    description: str
    scientific_rationale: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

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

@dataclass
class SmartWorkout:
    """Séance d'entraînement intelligente avec justifications"""
    name: str
    type: str
    description: str
    scientific_objective: str
    total_duration: int
    segments: List[WorkoutSegment]
    repeated_intervals: List[RepeatedInterval]
    ftp: int
    adaptation_notes: str = ""
    coaching_tips: str = ""

# === OUTIL RAG POUR KNOWLEDGE BASE CORRIGÉ ===

class CyclingKnowledgeTool(BaseTool):
    """Outil RAG pour accéder à la base de connaissances cycliste"""
    name = "cycling_knowledge"
    description = "Recherche dans la base de connaissances cycliste pour obtenir des informations précises sur les zones, structures et adaptations"
    
    def __init__(self):
        super().__init__()
        # Stocker explicitement la base de connaissances
        self.kb = CYCLING_KNOWLEDGE_BASE
        self.vectorstore = None
        
        # Créer les documents pour le RAG
        documents = self._create_documents()
        
        # Initialiser le RAG si possible
        if LANGCHAIN_AVAILABLE:
            try:
                embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                splits = text_splitter.split_documents(documents)
                self.vectorstore = FAISS.from_documents(splits, embeddings)
            except Exception as e:
                print(f"⚠️ Erreur initialisation RAG: {e}")
                print("Utilisation du mode recherche simple")
                self.vectorstore = None
    
    def _create_documents(self) -> List[Document]:
        """Crée les documents pour le RAG"""
        documents = []
        
        # Documents sur les zones
        for zone, data in self.kb["zones_definition"].items():
            content = f"""Zone {zone} - {data['name']}:
Puissance: {data['power_pct_ftp'][0]*100:.0f}-{data['power_pct_ftp'][1]*100:.0f}% FTP
Fréquence cardiaque: {data['hr_pct_max'][0]}-{data['hr_pct_max'][1]}% FCmax
Cadence: {data['cadence_rpm'][0]}-{data['cadence_rpm'][1]} RPM
Objectif: {data['objective']}
Durée typique: {data['duration_typical']}
Utilisation: {data['when_use']}"""
            
            documents.append(Document(
                page_content=content,
                metadata={"type": "zone", "zone": zone}
            ))
        
        # Documents sur les structures
        for structure, data in self.kb["workout_structures"].items():
            content = f"""Structure {structure}:
{json.dumps(data, indent=2, ensure_ascii=False)}"""
            
            documents.append(Document(
                page_content=content,
                metadata={"type": "structure", "structure": structure}
            ))
        
        return documents
    
    def _run(self, query: str) -> str:
        """Recherche dans la base de connaissances"""
        try:
            if self.vectorstore:
                # Recherche vectorielle
                docs = self.vectorstore.similarity_search(query, k=3)
                results = "\n\n".join([doc.page_content for doc in docs])
                return f"Informations trouvées:\n{results}"
            else:
                # Recherche simple par mots-clés
                return self._simple_search(query)
                
        except Exception as e:
            return f"Erreur recherche: {str(e)}"
    
    def _simple_search(self, query: str) -> str:
        """Recherche simple par mots-clés si RAG indisponible"""
        results = []
        query_lower = query.lower()
        
        # Recherche dans les zones
        for zone, data in self.kb["zones_definition"].items():
            if any(term in query_lower for term in [zone.lower(), data['name'].lower(), 'zone', 'puissance']):
                results.append(f"Zone {zone} - {data['name']}: {data['objective']}")
        
        # Recherche dans les structures
        for structure, data in self.kb["workout_structures"].items():
            if any(term in query_lower for term in [structure, 'structure', 'entrainement']):
                results.append(f"Structure {structure}: {data.get('notes', 'Informations disponibles')}")
        
        return "\n".join(results) if results else "Aucune information trouvée pour cette requête"

# === OUTIL GÉNÉRATION AVANCÉE SIMPLIFIÉ ===

class AdvancedWorkoutTool(BaseTool):
    """Outil de génération de séances avancé simplifié"""
    name = "generate_advanced_workout"
    description = "Génère une séance avancée avec justifications scientifiques. Paramètres: type, duration_minutes, athlete_level, ftp, objectives"
    
    def _run(self, type: str = "vo2max", duration_minutes: int = 75, athlete_level: str = "intermediate", ftp: int = 320, objectives: str = "improve_vo2max") -> str:
        """Génère une séance avancée avec toutes les optimisations"""
        try:
            # Créer la séance intelligente
            workout = self._create_smart_workout(type, duration_minutes, athlete_level, ftp, objectives)
            
            # Générer les fichiers
            files = self._generate_workout_files(workout)
            
            # Créer le rapport détaillé
            report = self._create_detailed_report(workout)
            
            return f"""✅ Séance avancée '{workout.name}' générée !

📊 RÉSUMÉ:
{workout.description}

🎯 OBJECTIF SCIENTIFIQUE:
{workout.scientific_objective}

📁 FICHIERS GÉNÉRÉS:
{chr(10).join([f"• {k}: {Path(v).name}" for k, v in files.items()])}

💡 NOTES D'ADAPTATION:
{workout.adaptation_notes}

🏃 CONSEILS DE COACHING:
{workout.coaching_tips}

📋 RAPPORT DÉTAILLÉ:
{report}"""
            
        except Exception as e:
            return f"❌ Erreur génération avancée: {str(e)}"
    
    def _create_smart_workout(self, workout_type: str, duration: int, level: str, ftp: int, objectives: str) -> SmartWorkout:
        """Crée une séance intelligente selon le type"""
        
        level_adaptations = CYCLING_KNOWLEDGE_BASE["athlete_adaptations"].get(
            level, CYCLING_KNOWLEDGE_BASE["athlete_adaptations"]["intermediate"]
        )
        
        if workout_type.lower() in ['vo2max', 'vo2', 'pma']:
            return self._create_advanced_vo2max(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['threshold', 'seuil', 'ftp']:
            return self._create_advanced_threshold(duration, level, ftp, level_adaptations)
        elif workout_type.lower() in ['endurance', 'z2']:
            return self._create_advanced_endurance(duration, level, ftp, level_adaptations)
        else:
            return self._create_advanced_vo2max(duration, level, ftp, level_adaptations)
    
    def _create_advanced_vo2max(self, duration: int, level: str, ftp: int, adaptations: Dict) -> SmartWorkout:
        """Crée une séance VO2max avancée"""
        
        # Paramètres selon le niveau
        max_reps = adaptations["vo2max_intervals"]["max_reps"]
        max_duration = adaptations["vo2max_intervals"]["max_duration"]
        recovery_ratio = adaptations["vo2max_intervals"]["recovery_ratio"]
        
        # Calcul des durées optimales
        work_duration = min(max_duration, 4)
        rest_duration = int(work_duration * 0.75)  # Ratio simplifié
        
        # Calculer le nombre de répétitions possible
        warmup_time = 15
        cooldown_time = 15
        activation_time = 10
        available_time = duration - warmup_time - cooldown_time - activation_time
        
        single_rep_time = work_duration + rest_duration
        calculated_reps = min(max_reps, available_time // single_rep_time)
        actual_reps = max(3, calculated_reps)
        
        # Zones selon la base de connaissances
        z1_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z1"]["power_pct_ftp"]
        z2_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z2"]["power_pct_ftp"]
        z5_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z5"]["power_pct_ftp"]
        
        # Segments
        segments = [
            WorkoutSegment(
                type="Warmup",
                duration_minutes=warmup_time,
                power_pct_ftp=(0.50, 0.65),
                cadence_rpm=85,
                description="Échauffement progressif avec activation cardiovasculaire",
                scientific_rationale="Préparation du système cardiovasculaire et augmentation graduelle du flux sanguin musculaire"
            ),
            WorkoutSegment(
                type="SteadyState",
                duration_minutes=activation_time,
                power_pct_ftp=z2_power,
                cadence_rpm=90,
                description="Activation aérobie pré-intervalles",
                scientific_rationale="Activation des voies métaboliques aérobies avant les efforts en Zone 5"
            ),
            WorkoutSegment(
                type="Cooldown",
                duration_minutes=cooldown_time,
                power_pct_ftp=(0.40, 0.50),
                cadence_rpm=80,
                description="Retour au calme actif pour élimination lactate",
                scientific_rationale="Maintien circulation sanguine pour élimination déchets métaboliques"
            )
        ]
        
        # Intervalles répétés
        repeated_intervals = [
            RepeatedInterval(
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
        
        # Calcul TSS estimé
        estimated_tss = self._calculate_tss(segments, repeated_intervals, ftp)
        
        return SmartWorkout(
            name=f"VO2max Optimisé {actual_reps}×{work_duration}min",
            type="vo2max",
            description=f"Séance VO2max scientifiquement optimisée pour niveau {level} : {actual_reps} intervalles de {work_duration} minutes en Zone 5",
            scientific_objective="Amélioration de la Puissance Maximale Aérobie (PMA) et de la consommation maximale d'oxygène (VO2max) à travers des intervalles spécifiques de 3-4 minutes à 106-120% FTP",
            total_duration=duration,
            segments=segments,
            repeated_intervals=repeated_intervals,
            ftp=ftp,
            adaptation_notes=f"Adapté pour {level}: {actual_reps} répétitions (max {max_reps}), récupération {recovery_ratio}, cadence élevée (100 rpm) pour optimiser la vélocité",
            coaching_tips=f"Maintenez une cadence élevée (95-105 rpm), respirez profondément, acceptez l'inconfort en fin d'intervalle. TSS estimé: {estimated_tss:.0f}"
        )
    
    def _create_advanced_threshold(self, duration: int, level: str, ftp: int, adaptations: Dict) -> SmartWorkout:
        """Crée une séance seuil avancée"""
        max_duration = adaptations["threshold_intervals"]["max_duration"]
        
        # Structure 2x20min ou adaptée
        if duration >= 80 and max_duration >= 20:
            work_blocks = [20, 20]
            recovery_time = 5
        else:
            # Adapter selon la durée et le niveau
            available_work = duration - 30  # 15min warmup + 15min cooldown
            if max_duration >= available_work:
                work_blocks = [available_work]
                recovery_time = 0
            else:
                num_blocks = min(3, available_work // max_duration)
                work_blocks = [max_duration] * num_blocks
                recovery_time = 5
        
        z1_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z1"]["power_pct_ftp"]
        z2_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z2"]["power_pct_ftp"]
        z4_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z4"]["power_pct_ftp"]
        
        segments = [
            WorkoutSegment(
                type="Warmup",
                duration_minutes=15,
                power_pct_ftp=(0.50, 0.65),
                cadence_rpm=85,
                description="Échauffement progressif",
                scientific_rationale="Préparation progressive au seuil lactique"
            ),
            WorkoutSegment(
                type="Cooldown",
                duration_minutes=15,
                power_pct_ftp=(0.40, 0.50),
                cadence_rpm=80,
                description="Retour au calme",
                scientific_rationale="Élimination progressive du lactate"
            )
        ]
        
        repeated_intervals = []
        for i, work_time in enumerate(work_blocks):
            repeated_intervals.append(
                RepeatedInterval(
                    repetitions=1,
                    work_duration=work_time,
                    work_power_pct=z4_power,
                    work_cadence=95,
                    rest_duration=recovery_time if i < len(work_blocks) - 1 else 0,
                    rest_power_pct=z2_power,
                    rest_cadence=85,
                    work_description=f"Bloc seuil {i+1}/{len(work_blocks)} - Maintenir FTP",
                    rest_description="Récupération active",
                    scientific_rationale=f"Bloc {work_time}min au seuil lactique pour améliorer FTP"
                )
            )
        
        estimated_tss = self._calculate_tss(segments, repeated_intervals, ftp)
        
        return SmartWorkout(
            name=f"Threshold {'+'.join(map(str, work_blocks))}min",
            type="threshold",
            description=f"Séance de seuil lactique avec {len(work_blocks)} bloc(s) pour améliorer le FTP",
            scientific_objective="Amélioration du seuil lactique (FTP) et de la capacité à maintenir des efforts soutenus",
            total_duration=duration,
            segments=segments,
            repeated_intervals=repeated_intervals,
            ftp=ftp,
            adaptation_notes=f"Adapté pour {level}: blocs de {work_blocks} minutes, récupération active",
            coaching_tips=f"Maintenez une puissance stable, respirez de façon contrôlée. TSS estimé: {estimated_tss:.0f}"
        )
    
    def _create_advanced_endurance(self, duration: int, level: str, ftp: int, adaptations: Dict) -> SmartWorkout:
        """Crée une séance endurance avancée"""
        warmup_time = 15
        cooldown_time = 15
        main_time = duration - warmup_time - cooldown_time
        
        z1_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z1"]["power_pct_ftp"]
        z2_power = CYCLING_KNOWLEDGE_BASE["zones_definition"]["Z2"]["power_pct_ftp"]
        
        segments = [
            WorkoutSegment(
                type="Warmup",
                duration_minutes=warmup_time,
                power_pct_ftp=(0.50, 0.65),
                cadence_rpm=85,
                description="Échauffement progressif",
                scientific_rationale="Activation graduelle du système cardiovasculaire"
            ),
            WorkoutSegment(
                type="SteadyState",
                duration_minutes=main_time,
                power_pct_ftp=z2_power,
                cadence_rpm=90,
                description="Endurance aérobie stable - conversation possible",
                scientific_rationale="Développement des adaptations mitochondriales et de l'efficacité cardiaque"
            ),
            WorkoutSegment(
                type="Cooldown",
                duration_minutes=cooldown_time,
                power_pct_ftp=(0.40, 0.50),
                cadence_rpm=85,
                description="Retour au calme actif",
                scientific_rationale="Maintien de la circulation pour l'élimination des déchets"
            )
        ]
        
        estimated_tss = self._calculate_tss(segments, [], ftp)
        
        return SmartWorkout(
            name=f"Endurance {duration}min",
            type="endurance",
            description=f"Séance d'endurance aérobie de {main_time} minutes pour développer la base cardiovasculaire",
            scientific_objective="Développement de l'endurance fondamentale, amélioration de l'efficacité cardiaque et du métabolisme des graisses",
            total_duration=duration,
            segments=segments,
            repeated_intervals=[],
            ftp=ftp,
            adaptation_notes=f"Intensité modérée pour {level}, focus sur l'efficacité du pédalage",
            coaching_tips=f"Maintenez une conversation possible, cadence fluide 85-95 rpm. TSS estimé: {estimated_tss:.0f}"
        )
    
    def _calculate_tss(self, segments: List[WorkoutSegment], intervals: List[RepeatedInterval], ftp: int) -> float:
        """Calcule le TSS estimé"""
        total_tss = 0
        
        # TSS des segments
        for segment in segments:
            avg_power_pct = (segment.power_pct_ftp[0] + segment.power_pct_ftp[1]) / 2
            duration_hours = segment.duration_minutes / 60
            tss = duration_hours * (avg_power_pct ** 2) * 100
            total_tss += tss
        
        # TSS des intervalles
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
    
    def _generate_workout_files(self, workout: SmartWorkout) -> Dict[str, str]:
        """Génère tous les formats de fichiers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = workout.name.replace(' ', '_').replace('×', 'x').replace('+', '_')
        
        output_dir = Path("output_advanced")
        output_dir.mkdir(exist_ok=True)
        
        files = {}
        
        try:
            # 1. JSON intermédiaire
            json_structure = self._create_json_structure(workout)
            json_file = output_dir / f"{safe_name}_{timestamp}_structure.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_structure, f, indent=2, ensure_ascii=False)
            files['JSON Structure'] = str(json_file)
            
            # 2. ZWO optimisé
            zwo_file = output_dir / f"{safe_name}_{timestamp}.zwo"
            self._generate_optimized_zwo(workout, str(zwo_file))
            files['ZWO (MyWhoosh)'] = str(zwo_file)
            
            # 3. JSON TrainingPeaks
            tp_file = output_dir / f"{safe_name}_{timestamp}_tp.json"
            self._generate_trainingpeaks_json(workout, str(tp_file))
            files['JSON (TrainingPeaks)'] = str(tp_file)
            
        except Exception as e:
            print(f"⚠️ Erreur génération fichiers: {e}")
        
        return files
    
    def _create_json_structure(self, workout: SmartWorkout) -> Dict:
        """Crée la structure JSON intermédiaire claire"""
        return {
            "workout_info": {
                "name": workout.name,
                "type": workout.type,
                "description": workout.description,
                "scientific_objective": workout.scientific_objective,
                "total_duration_minutes": workout.total_duration,
                "ftp": workout.ftp,
                "estimated_tss": self._calculate_tss(workout.segments, workout.repeated_intervals, workout.ftp)
            },
            "segments": [
                {
                    "type": seg.type,
                    "duration_minutes": seg.duration_minutes,
                    "power_pct_ftp": seg.power_pct_ftp,
                    "power_watts": [int(seg.power_pct_ftp[0] * workout.ftp), int(seg.power_pct_ftp[1] * workout.ftp)],
                    "cadence_rpm": seg.cadence_rpm,
                    "description": seg.description,
                    "scientific_rationale": seg.scientific_rationale
                }
                for seg in workout.segments
            ],
            "repeated_intervals": [
                {
                    "repetitions": interval.repetitions,
                    "work_block": {
                        "duration_minutes": interval.work_duration,
                        "power_pct_ftp": interval.work_power_pct,
                        "power_watts": [int(interval.work_power_pct[0] * workout.ftp), int(interval.work_power_pct[1] * workout.ftp)],
                        "cadence_rpm": interval.work_cadence,
                        "description": interval.work_description
                    },
                    "rest_block": {
                        "duration_minutes": interval.rest_duration,
                        "power_pct_ftp": interval.rest_power_pct,
                        "power_watts": [int(interval.rest_power_pct[0] * workout.ftp), int(interval.rest_power_pct[1] * workout.ftp)],
                        "cadence_rpm": interval.rest_cadence,
                        "description": interval.rest_description
                    },
                    "scientific_rationale": interval.scientific_rationale
                }
                for interval in workout.repeated_intervals
            ],
            "coaching_notes": {
                "adaptation_notes": workout.adaptation_notes,
                "coaching_tips": workout.coaching_tips
            }
        }
    
    def _generate_optimized_zwo(self, workout: SmartWorkout, filename: str):
        """Génère un fichier ZWO optimisé"""
        root = ET.Element("workout_file")
        
        # Métadonnées améliorées
        author = ET.SubElement(root, "author")
        author.text = "Advanced Cycling AI Coach"
        
        name = ET.SubElement(root, "name")
        name.text = workout.name
        
        description = ET.SubElement(root, "description")
        description.text = f"{workout.description}\n\n🎯 {workout.scientific_objective}"
        
        # Tags multiples
        tags = ET.SubElement(root, "tags")
        for tag_name in [workout.type, "scientific", "optimized"]:
            tag = ET.SubElement(tags, "tag")
            tag.set("name", tag_name)
        
        # Workout principal
        workout_elem = ET.SubElement(root, "workout")
        
        # Ajouter segments
        for segment in workout.segments:
            if segment.type == "Warmup":
                step = ET.SubElement(workout_elem, "Warmup")
            elif segment.type == "Cooldown":
                step = ET.SubElement(workout_elem, "Cooldown")
            else:
                step = ET.SubElement(workout_elem, "SteadyState")
            
            step.set("Duration", str(segment.duration_minutes * 60))
            step.set("PowerLow", f"{segment.power_pct_ftp[0]:.3f}")
            step.set("PowerHigh", f"{segment.power_pct_ftp[1]:.3f}")
            step.set("Cadence", str(segment.cadence_rpm))
        
        # Ajouter intervalles répétés
        for interval in workout.repeated_intervals:
            for rep in range(interval.repetitions):
                # Work interval
                work_step = ET.SubElement(workout_elem, "SteadyState")
                work_step.set("Duration", str(interval.work_duration * 60))
                work_step.set("PowerLow", f"{interval.work_power_pct[0]:.3f}")
                work_step.set("PowerHigh", f"{interval.work_power_pct[1]:.3f}")
                work_step.set("Cadence", str(interval.work_cadence))
                
                # Rest interval (sauf après le dernier)
                if rep < interval.repetitions - 1 and interval.rest_duration > 0:
                    rest_step = ET.SubElement(workout_elem, "SteadyState")
                    rest_step.set("Duration", str(interval.rest_duration * 60))
                    rest_step.set("PowerLow", f"{interval.rest_power_pct[0]:.3f}")
                    rest_step.set("PowerHigh", f"{interval.rest_power_pct[1]:.3f}")
                    rest_step.set("Cadence", str(interval.rest_cadence))
        
        # Indentation et sauvegarde
        self._indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
    
    def _generate_trainingpeaks_json(self, workout: SmartWorkout, filename: str):
        """Génère JSON pour TrainingPeaks"""
        tp_data = {
            "name": workout.name,
            "description": workout.description,
            "sport": "Bike",
            "totalTime": workout.total_duration * 60,
            "estimatedTSS": self._calculate_tss(workout.segments, workout.repeated_intervals, workout.ftp),
            "scientificObjective": workout.scientific_objective,
            "adaptationNotes": workout.adaptation_notes,
            "coachingTips": workout.coaching_tips,
            "created": datetime.now().isoformat(),
            "intervals": []
        }
        
        step_index = 1
        
        # Ajouter segments
        for segment in workout.segments:
            tp_data["intervals"].append({
                "step": step_index,
                "duration": segment.duration_minutes * 60,
                "type": segment.type,
                "powerMin": int(segment.power_pct_ftp[0] * workout.ftp),
                "powerMax": int(segment.power_pct_ftp[1] * workout.ftp),
                "powerTarget": int((segment.power_pct_ftp[0] + segment.power_pct_ftp[1]) / 2 * workout.ftp),
                "cadence": segment.cadence_rpm,
                "description": segment.description,
                "scientificRationale": segment.scientific_rationale
            })
            step_index += 1
        
        # Ajouter intervalles répétés
        for interval in workout.repeated_intervals:
            for rep in range(interval.repetitions):
                # Work
                tp_data["intervals"].append({
                    "step": step_index,
                    "duration": interval.work_duration * 60,
                    "type": "Work",
                    "repetition": f"{rep+1}/{interval.repetitions}",
                    "powerMin": int(interval.work_power_pct[0] * workout.ftp),
                    "powerMax": int(interval.work_power_pct[1] * workout.ftp),
                    "powerTarget": int((interval.work_power_pct[0] + interval.work_power_pct[1]) / 2 * workout.ftp),
                    "cadence": interval.work_cadence,
                    "description": interval.work_description,
                    "scientificRationale": interval.scientific_rationale
                })
                step_index += 1
                
                # Rest (sauf dernier)
                if rep < interval.repetitions - 1 and interval.rest_duration > 0:
                    tp_data["intervals"].append({
                        "step": step_index,
                        "duration": interval.rest_duration * 60,
                        "type": "Rest",
                        "powerMin": int(interval.rest_power_pct[0] * workout.ftp),
                        "powerMax": int(interval.rest_power_pct[1] * workout.ftp),
                        "powerTarget": int((interval.rest_power_pct[0] + interval.rest_power_pct[1]) / 2 * workout.ftp),
                        "cadence": interval.rest_cadence,
                        "description": interval.rest_description
                    })
                    step_index += 1
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tp_data, f, indent=2, ensure_ascii=False)
    
    def _create_detailed_report(self, workout: SmartWorkout) -> str:
        """Crée un rapport détaillé de la séance"""
        tss = self._calculate_tss(workout.segments, workout.repeated_intervals, workout.ftp)
        
        return f"""
🔬 ANALYSE SCIENTIFIQUE:
• TSS Estimé: {tss:.0f}
• Charge d'entraînement: {'Élevée' if tss > 100 else 'Modérée' if tss > 60 else 'Légère'}
• Temps en zone haute (Z4+): {self._calculate_high_intensity_time(workout)} minutes

⚡ ADAPTATIONS PHYSIOLOGIQUES ATTENDUES:
• Amélioration VO2max: {'+++' if workout.type == 'vo2max' else '++' if workout.type == 'threshold' else '+'}
• Amélioration capacité tampon lactate: {'++' if workout.type in ['vo2max', 'threshold'] else '+'}
• Amélioration coordination neuromusculaire: {'++' if workout.type == 'vo2max' else '+'}
• Temps de récupération recommandé: {'24-48h' if tss > 80 else '12-24h'}
"""
    
    def _calculate_high_intensity_time(self, workout: SmartWorkout) -> int:
        """Calcule le temps passé en zone haute intensité"""
        high_intensity_time = 0
        
        for segment in workout.segments:
            if segment.power_pct_ftp[0] >= 0.91:  # Z4+
                high_intensity_time += segment.duration_minutes
        
        for interval in workout.repeated_intervals:
            if interval.work_power_pct[0] >= 0.91:  # Z4+
                high_intensity_time += interval.work_duration * interval.repetitions
        
        return high_intensity_time
    
    def _indent_xml(self, elem, level=0):
        """Indentation XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

# === AGENT PRINCIPAL CORRIGÉ ===

class AdvancedCyclingAgent:
    """Agent de coaching cycliste avancé avec RAG et contextualisation"""
    
    def __init__(self, openai_api_key: str = None):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain requis")
        
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API OpenAI requise")
        
        # LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=self.api_key,
            max_tokens=1500
        )
        
        # Mémoire
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=8
        )
        
        # Outils avancés
        self.tools = [
            CyclingKnowledgeTool(),
            AdvancedWorkoutTool()
        ]
        
        # Prompt système avancé
        self.system_prompt = self._create_advanced_prompt()
        
        # Agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _create_advanced_prompt(self) -> ChatPromptTemplate:
        """Prompt système avancé avec toutes les optimisations"""
        system_message = """Tu es un COACH CYCLISTE IA D'ÉLITE avec une expertise scientifique approfondie.

🧠 EXPERTISE AVANCÉE:
• Physiologie de l'exercice et adaptations cardiovasculaires
• Périodisation basée sur les recherches récentes (2023-2025)
• Zones d'entraînement précises avec justifications métaboliques
• Personnalisation selon profil, niveau, objectifs et données de performance

🔬 BASE DE CONNAISSANCES:
• Utilise l'outil 'cycling_knowledge' pour accéder à des informations précises
• Zones de puissance: Z1 (45-55% FTP) à Z7 (150-300% FTP)
• Structures d'entraînement validées scientifiquement
• Adaptations selon niveau (débutant/intermédiaire/avancé)

⚡ GÉNÉRATION DE SÉANCES:
• Utilise 'generate_advanced_workout' pour créer des séances optimisées
• JAMAIS de valeurs 0.000 pour la puissance (minimum 40% FTP)
• Justifications scientifiques pour chaque segment
• Adaptation automatique selon niveau et objectifs

🎯 PERSONNALISATION:
• Analyse toujours le profil complet de l'athlète
• Adapte volume, intensité et complexité selon le niveau
• Intègre les objectifs spécifiques (FTP, endurance, compétition)
• Fournit des conseils de coaching personnalisés

💬 COMMUNICATION:
• Explique TOUJOURS le "pourquoi" scientifique
• Utilise un langage motivant et encourageant
• Structure tes réponses avec émojis pour la clarté
• Fournis des conseils pratiques d'exécution

🔧 WORKFLOW:
1. Si demande de séance → Utilise generate_advanced_workout avec paramètres précis
2. Si question technique → Utilise cycling_knowledge pour informations exactes
3. Toujours contextualiser et personnaliser selon l'utilisateur
4. Terminer par des conseils pratiques et motivation

Sois un coach d'élite qui rivalise avec les meilleurs entraîneurs mondiaux !"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def chat(self, message: str) -> str:
        """Interface de chat avancée"""
        try:
            response = self.agent_executor.invoke(
                {"input": message},
                return_only_outputs=True
            )
            return response.get("output", "Désolé, je n'ai pas pu traiter votre demande.")
        except Exception as e:
            return f"Désolé, j'ai rencontré une erreur : {str(e)}"
    
    def reset_conversation(self):
        """Reset de la conversation"""
        self.memory.clear()

# === INTERFACE PRINCIPALE CORRIGÉE ===

def main():
    """Interface principale du coach avancé"""
    print("🚴 CYCLING AI COACH - Version Elite avec RAG (Corrigée)")
    print("=" * 60)
    print("Tapez 'quit' pour quitter, 'reset' pour nouvelle conversation")
    print()
    
    try:
        # Vérification clé API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Clé API OpenAI non trouvée !")
            print("Définissez la variable d'environnement OPENAI_API_KEY")
            return
        
        # Initialisation
        coach = AdvancedCyclingAgent()
        print("✅ Coach IA Elite initialisé avec succès !")
        print("🧠 Base de connaissances RAG active")
        print("⚡ Génération avancée disponible")
        print()
        
        # Conversation
        while True:
            user_input = input("👤 Vous: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Au revoir ! Excellents entraînements !")
                break
            elif user_input.lower() == 'reset':
                coach.reset_conversation()
                print("🔄 Conversation remise à zéro")
                continue
            elif not user_input:
                continue
            
            print(f"\n🤖 Coach Elite: ", end="")
            response = coach.chat(user_input)
            print(response)
            print()
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("💡 Assurez-vous d'avoir installé toutes les dépendances :")
        print("pip install langchain langchain-openai langchain-community faiss-cpu python-dotenv")

if __name__ == "__main__":
    main()