#!/usr/bin/env python3
"""
Periodization Tool - Outil LangChain pour la planification multi-semaines
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta

try:
    from langchain.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    class BaseTool:
        pass

class PeriodizationTool(BaseTool):
    """Outil de planification multi-semaines pour l'agent"""
    name = "create_periodization_plan"
    description = "Crée un plan d'entraînement périodisé sur plusieurs semaines. Paramètres: duration_weeks, target_events, model_type, athlete_level"
    
    def _run(self, duration_weeks: int = 12, target_events: str = "", 
             model_type: str = "polarized", athlete_level: str = "intermediate") -> str:
        """Crée un plan de périodisation complet"""
        
        try:
            # Importer le système de périodisation
            from periodization_system import (
                AdvancedPeriodizationEngine, 
                PeriodizationModel, 
                TrainingPhase
            )
            
            # Créer le moteur
            engine = AdvancedPeriodizationEngine()
            
            # Profil athlète par défaut (à terme, récupérer depuis la mémoire)
            athlete_profile = {
                "user_id": "current_user",
                "name": "Cycliste",
                "ftp": 320,
                "experience_level": athlete_level,
                "available_time": {"weekdays": 8, "weekends": 12},
                "primary_goals": ["improve_ftp", "racing"]
            }
            
            # Parser les événements cibles
            events = self._parse_target_events(target_events)
            
            # Déterminer le modèle de périodisation
            model = self._get_periodization_model(model_type)
            
            # Créer le plan
            plan = engine.create_periodization_plan(
                athlete_profile=athlete_profile,
                target_events=events,
                duration_weeks=duration_weeks,
                model=model
            )
            
            # Créer le calendrier
            calendar = engine.create_training_calendar(plan)
            
            # Sauvegarder les fichiers
            output_dir = Path("output_periodization")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sauvegarder le plan
            plan_file = output_dir / f"plan_{duration_weeks}w_{timestamp}.json"
            engine.export_plan_to_json(plan, str(plan_file))
            
            # Sauvegarder le calendrier
            calendar_file = output_dir / f"calendar_{duration_weeks}w_{timestamp}.json"
            with open(calendar_file, 'w', encoding='utf-8') as f:
                json.dump(calendar, f, indent=2, ensure_ascii=False)
            
            # Créer un rapport résumé
            summary = self._create_plan_summary(plan, calendar)
            
            return f"""✅ Plan de périodisation créé avec succès !

📊 RÉSUMÉ DU PLAN:
{summary}

📁 FICHIERS GÉNÉRÉS:
• Plan complet: {plan_file.name}
• Calendrier: {calendar_file.name}

🎯 MODÈLE UTILISÉ:
{model.value.title()} - Basé sur les recherches de {self._get_model_reference(model)}

📈 PROJECTION FTP:
{plan.current_ftp}W → {plan.projected_ftp}W (+{plan.projected_ftp - plan.current_ftp}W)

🔄 PROCHAINES ÉTAPES:
1. Consultez le calendrier détaillé
2. Adaptez selon vos contraintes personnelles
3. Suivez les séances générées automatiquement
4. Effectuez les tests FTP prévus

💡 CONSEIL: Ce plan est basé sur votre profil actuel. N'hésitez pas à l'ajuster selon vos sensations !"""
            
        except Exception as e:
            return f"❌ Erreur lors de la création du plan: {str(e)}"
    
    def _parse_target_events(self, events_str: str) -> List[Dict]:
        """Parse les événements cibles depuis une string"""
        if not events_str:
            return []
        
        events = []
        # Format simple: "Course FFC:2025-09-15,Gran Fondo:2025-10-20"
        for event_str in events_str.split(","):
            if ":" in event_str:
                name, date = event_str.split(":", 1)
                events.append({
                    "name": name.strip(),
                    "date": date.strip(),
                    "type": "road_race",
                    "priority": "A"
                })
        
        return events
    
    def _get_periodization_model(self, model_type: str):
        """Convertit le string en modèle de périodisation"""
        from periodization_system import PeriodizationModel
        
        model_mapping = {
            "polarized": PeriodizationModel.POLARIZED,
            "traditional": PeriodizationModel.TRADITIONAL,
            "block": PeriodizationModel.BLOCK,
            "pyramidal": PeriodizationModel.PYRAMIDAL
        }
        
        return model_mapping.get(model_type.lower(), PeriodizationModel.POLARIZED)
    
    def _get_model_reference(self, model) -> str:
        """Retourne la référence scientifique du modèle"""
        from periodization_system import PeriodizationModel
        
        references = {
            PeriodizationModel.POLARIZED: "Stephen Seiler",
            PeriodizationModel.TRADITIONAL: "Bompa & Buzzichelli",
            PeriodizationModel.BLOCK: "Vladimir Issurin",
            PeriodizationModel.PYRAMIDAL: "Laursen & Buchheit"
        }
        
        return references.get(model, "Recherche moderne")
    
    def _create_plan_summary(self, plan, calendar: Dict) -> str:
        """Crée un résumé du plan"""
        
        # Analyser la distribution des phases
        phase_distribution = {}
        for week in plan.weekly_plans:
            phase = week.phase.value
            phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
        
        # Calculer TSS moyen
        total_tss = sum(week.training_load.tss_target for week in plan.weekly_plans)
        avg_tss = total_tss / len(plan.weekly_plans)
        
        # Trouver la semaine la plus intense
        max_tss_week = max(plan.weekly_plans, key=lambda w: w.training_load.tss_target)
        
        summary = f"""
📅 Durée: {plan.total_weeks} semaines
📊 TSS moyen: {avg_tss:.0f} points/semaine
⚡ Semaine la plus intense: S{max_tss_week.week_number} ({max_tss_week.training_load.tss_target:.0f} TSS)

🔄 DISTRIBUTION DES PHASES:
{self._format_phase_distribution(phase_distribution)}

🎯 ÉVÉNEMENTS CIBLES:
{self._format_target_events(plan.target_events)}

📈 PROGRESSION ATTENDUE:
• FTP: +{plan.projected_ftp - plan.current_ftp}W ({((plan.projected_ftp / plan.current_ftp - 1) * 100):.1f}%)
• Amélioration basée sur votre niveau actuel ({plan.weekly_plans[0].training_load.tss_target:.0f} TSS de base)
        """
        
        return summary.strip()
    
    def _format_phase_distribution(self, distribution: Dict) -> str:
        """Formate la distribution des phases"""
        lines = []
        for phase, weeks in distribution.items():
            lines.append(f"• {phase.title()}: {weeks} semaines")
        return "\n".join(lines)
    
    def _format_target_events(self, events: List[Dict]) -> str:
        """Formate les événements cibles"""
        if not events:
            return "• Aucun événement spécifique (amélioration générale)"
        
        lines = []
        for event in events:
            lines.append(f"• {event['name']}: {event['date']}")
        return "\n".join(lines)

class SimplePeriodizationTool:
    """Version simplifiée sans LangChain"""
    
    def __init__(self):
        try:
            from periodization_system import AdvancedPeriodizationEngine
            self.engine = AdvancedPeriodizationEngine()
            print("✅ Outil périodisation simplifié initialisé")
        except ImportError:
            self.engine = None
            print("⚠️ Moteur de périodisation non disponible")
    
    def create_plan(self, duration_weeks: int = 12, athlete_level: str = "intermediate") -> str:
        """Crée un plan simple"""
        if not self.engine:
            return "❌ Moteur de périodisation non disponible"
        
        try:
            # Profil simple
            athlete_profile = {
                "user_id": "simple_user",
                "name": "Cycliste",
                "ftp": 320,
                "experience_level": athlete_level,
                "available_time": {"weekdays": 8, "weekends": 12},
                "primary_goals": ["improve_ftp"]
            }
            
            from periodization_system import PeriodizationModel
            
            # Créer le plan
            plan = self.engine.create_periodization_plan(
                athlete_profile=athlete_profile,
                target_events=[],
                duration_weeks=duration_weeks,
                model=PeriodizationModel.POLARIZED
            )
            
            return f"""✅ Plan {duration_weeks} semaines créé !
📈 FTP: {plan.current_ftp}W → {plan.projected_ftp}W
🎯 Modèle: Polarisé (Seiler)
📊 {len(plan.weekly_plans)} semaines planifiées"""
            
        except Exception as e:
            return f"❌ Erreur: {e}"

def create_periodization_tool():
    """Factory pour créer l'outil approprié"""
    if LANGCHAIN_AVAILABLE:
        try:
            return PeriodizationTool()
        except Exception as e:
            print(f"⚠️ Erreur création outil LangChain: {e}")
            return SimplePeriodizationTool()
    else:
        return SimplePeriodizationTool()