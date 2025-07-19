#!/usr/bin/env python3
"""
LangSmith Setup - Elite Cycling Coach Observatory
Monitoring, observabilité et analytics niveau WorldTour
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# LangSmith imports
try:
    from langsmith import Client, traceable
    from langsmith.run_helpers import get_current_run_tree
    LANGSMITH_AVAILABLE = True
except ImportError:
    print("⚠️ LangSmith non installé. Installez avec: pip install langsmith")
    LANGSMITH_AVAILABLE = False
    # Fallback decorator
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator

# Configuration logging élite
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EliteCyclingObservatory:
    """
    Observatoire Elite pour le coaching cycliste
    Niveau WorldTour - Tracking et analytics avancés
    """
    
    def __init__(self, project_name: str = "elite-cycling-coach"):
        """Initialise l'observatoire elite"""
        
        self.project_name = project_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configuration LangSmith
        self.langsmith_config = self._setup_langsmith()
        
        # Métriques de performance
        self.performance_metrics = {
            "response_times": [],
            "accuracy_scores": [],
            "user_satisfaction": [],
            "workout_effectiveness": [],
            "ftp_improvements": []
        }
        
        # Compteurs elite
        self.counters = {
            "workouts_generated": 0,
            "plans_created": 0,
            "athletes_coached": 0,
            "api_calls": 0,
            "errors": 0
        }
        
        # Analytics avancées
        self.analytics = {
            "peak_usage_hours": [],
            "popular_workout_types": {},
            "athlete_progression": {},
            "system_performance": {}
        }
        
        logger.info(f"🚴‍♂️ Elite Observatory initialisé - Session: {self.session_id}")
    
    def _setup_langsmith(self) -> Dict[str, Any]:
        """Configure LangSmith pour monitoring elite"""
        
        config = {
            "enabled": False,
            "client": None,
            "project_name": self.project_name,
            "tags": ["elite", "cycling", "worldtour"]
        }
        
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith non disponible - Mode standalone")
            return config
        
        # Vérifier les variables d'environnement
        api_key = os.getenv("LANGSMITH_API_KEY")
        endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        if not api_key:
            logger.warning("LANGSMITH_API_KEY non définie - Mode standalone")
            return config
        
        try:
            # Initialiser le client LangSmith
            client = Client(
                api_url=endpoint,
                api_key=api_key
            )
            
            # Créer/vérifier le projet
            try:
                client.create_project(
                    project_name=self.project_name,
                    description="Elite Cycling Coach - Monitoring niveau WorldTour"
                )
                logger.info(f"✅ Projet LangSmith créé: {self.project_name}")
            except Exception:
                logger.info(f"📋 Projet LangSmith existant: {self.project_name}")
            
            config.update({
                "enabled": True,
                "client": client,
                "endpoint": endpoint
            })
            
            logger.info("🚀 LangSmith configuré avec succès!")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration LangSmith: {e}")
            config["error"] = str(e)
        
        return config
    
    @traceable(name="workout_generation")
    def track_workout_generation(self, 
                                workout_type: str,
                                duration: int, 
                                athlete_level: str,
                                ftp: int,
                                response_time: float,
                                success: bool = True) -> Dict[str, Any]:
        """Track la génération d'une séance avec métriques elite"""
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "workout_type": workout_type,
            "duration_minutes": duration,
            "athlete_level": athlete_level,
            "ftp": ftp,
            "response_time_seconds": response_time,
            "success": success
        }
        
        # Métriques de performance
        self.performance_metrics["response_times"].append(response_time)
        
        # Compteurs
        if success:
            self.counters["workouts_generated"] += 1
        else:
            self.counters["errors"] += 1
        
        # Analytics
        workout_stats = self.analytics["popular_workout_types"]
        workout_stats[workout_type] = workout_stats.get(workout_type, 0) + 1
        
        # Log elite
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(
            f"{status} Workout Generated | "
            f"Type: {workout_type} | "
            f"Duration: {duration}min | "
            f"Level: {athlete_level} | "
            f"Response: {response_time:.2f}s"
        )
        
        return metrics
    
    @traceable(name="periodization_planning")
    def track_periodization_planning(self,
                                   duration_weeks: int,
                                   athlete_level: str,
                                   model_type: str,
                                   events_count: int,
                                   response_time: float,
                                   success: bool = True) -> Dict[str, Any]:
        """Track la création de plans de périodisation"""
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "duration_weeks": duration_weeks,
            "athlete_level": athlete_level,
            "periodization_model": model_type,
            "target_events": events_count,
            "response_time_seconds": response_time,
            "success": success
        }
        
        # Compteurs
        if success:
            self.counters["plans_created"] += 1
        else:
            self.counters["errors"] += 1
        
        # Log
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(
            f"{status} Periodization Plan | "
            f"Weeks: {duration_weeks} | "
            f"Model: {model_type} | "
            f"Level: {athlete_level} | "
            f"Response: {response_time:.2f}s"
        )
        
        return metrics
    
    @traceable(name="athlete_analysis")
    def track_athlete_analysis(self,
                             athlete_id: str,
                             analysis_type: str,
                             data_points: int,
                             insights_generated: int,
                             response_time: float) -> Dict[str, Any]:
        """Track l'analyse approfondie d'un athlète"""
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "athlete_id": athlete_id,
            "analysis_type": analysis_type,
            "data_points_analyzed": data_points,
            "insights_generated": insights_generated,
            "response_time_seconds": response_time
        }
        
        # Analytics athlète
        if athlete_id not in self.analytics["athlete_progression"]:
            self.analytics["athlete_progression"][athlete_id] = {
                "analyses_count": 0,
                "total_insights": 0,
                "avg_response_time": 0
            }
        
        athlete_stats = self.analytics["athlete_progression"][athlete_id]
        athlete_stats["analyses_count"] += 1
        athlete_stats["total_insights"] += insights_generated
        athlete_stats["avg_response_time"] = (
            (athlete_stats["avg_response_time"] * (athlete_stats["analyses_count"] - 1) + response_time) 
            / athlete_stats["analyses_count"]
        )
        
        logger.info(
            f"🔍 Athlete Analysis | "
            f"ID: {athlete_id} | "
            f"Type: {analysis_type} | "
            f"Data Points: {data_points} | "
            f"Insights: {insights_generated} | "
            f"Time: {response_time:.2f}s"
        )
        
        return metrics
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Génère un dashboard de performance elite"""
        
        # Calculs de performance
        avg_response_time = (
            sum(self.performance_metrics["response_times"]) / 
            len(self.performance_metrics["response_times"])
            if self.performance_metrics["response_times"] else 0
        )
        
        # Taux de succès
        total_operations = self.counters["workouts_generated"] + self.counters["plans_created"]
        success_rate = (
            (total_operations / (total_operations + self.counters["errors"]) * 100)
            if total_operations + self.counters["errors"] > 0 else 100
        )
        
        # Top workout types
        sorted_workouts = sorted(
            self.analytics["popular_workout_types"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        dashboard = {
            "session_info": {
                "session_id": self.session_id,
                "project": self.project_name,
                "langsmith_enabled": self.langsmith_config["enabled"],
                "timestamp": datetime.now().isoformat()
            },
            "performance_metrics": {
                "avg_response_time_seconds": round(avg_response_time, 3),
                "success_rate_percent": round(success_rate, 2),
                "total_operations": total_operations,
                "error_count": self.counters["errors"]
            },
            "usage_statistics": {
                "workouts_generated": self.counters["workouts_generated"],
                "plans_created": self.counters["plans_created"],
                "athletes_coached": len(self.analytics["athlete_progression"]),
                "api_calls": self.counters["api_calls"]
            },
            "popular_features": {
                "top_workout_types": sorted_workouts[:5],
                "athletes_with_most_analyses": self._get_top_athletes()
            },
            "system_health": {
                "langsmith_status": "Connected" if self.langsmith_config["enabled"] else "Standalone",
                "memory_usage": self._get_memory_usage(),
                "uptime": self._get_uptime()
            }
        }
        
        return dashboard
    
    def _get_top_athletes(self) -> List[Dict[str, Any]]:
        """Retourne les athlètes avec le plus d'analyses"""
        athletes = self.analytics["athlete_progression"]
        sorted_athletes = sorted(
            athletes.items(),
            key=lambda x: x[1]["analyses_count"],
            reverse=True
        )
        
        return [
            {
                "athlete_id": athlete_id,
                "analyses_count": stats["analyses_count"],
                "total_insights": stats["total_insights"]
            }
            for athlete_id, stats in sorted_athletes[:5]
        ]
    
    def _get_memory_usage(self) -> str:
        """Retourne l'usage mémoire (approximatif)"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f} MB"
        except ImportError:
            return "N/A (psutil non installé)"
    
    def _get_uptime(self) -> str:
        """Retourne l'uptime de la session"""
        start_time = datetime.strptime(self.session_id, "%Y%m%d_%H%M%S")
        uptime = datetime.now() - start_time
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def export_analytics(self, filepath: Optional[str] = None) -> str:
        """Exporte les analytics en JSON"""
        
        if not filepath:
            output_dir = Path("analytics_export")
            output_dir.mkdir(exist_ok=True)
            filepath = output_dir / f"elite_analytics_{self.session_id}.json"
        
        dashboard = self.get_performance_dashboard()
        
        # Ajouter les données détaillées
        export_data = {
            "dashboard": dashboard,
            "detailed_metrics": self.performance_metrics,
            "raw_analytics": self.analytics,
            "configuration": {
                "langsmith_enabled": self.langsmith_config["enabled"],
                "project_name": self.project_name
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Analytics exportées: {filepath}")
        return str(filepath)
    
    def print_elite_summary(self):
        """Affiche un résumé elite des performances"""
        
        dashboard = self.get_performance_dashboard()
        
        print("\n🏆 ELITE CYCLING COACH - PERFORMANCE DASHBOARD")
        print("=" * 60)
        
        # Performance
        perf = dashboard["performance_metrics"]
        print(f"⚡ Performance:")
        print(f"   • Temps de réponse moyen: {perf['avg_response_time_seconds']}s")
        print(f"   • Taux de succès: {perf['success_rate_percent']}%")
        print(f"   • Opérations totales: {perf['total_operations']}")
        
        # Usage
        usage = dashboard["usage_statistics"]
        print(f"\n📊 Utilisation:")
        print(f"   • Séances générées: {usage['workouts_generated']}")
        print(f"   • Plans créés: {usage['plans_created']}")
        print(f"   • Athlètes coachés: {usage['athletes_coached']}")
        
        # Top features
        top_workouts = dashboard["popular_features"]["top_workout_types"]
        if top_workouts:
            print(f"\n🎯 Types de séances populaires:")
            for workout_type, count in top_workouts:
                print(f"   • {workout_type}: {count}")
        
        # System health
        health = dashboard["system_health"]
        print(f"\n🔧 Système:")
        print(f"   • LangSmith: {health['langsmith_status']}")
        print(f"   • Mémoire: {health['memory_usage']}")
        print(f"   • Uptime: {health['uptime']}")
        
        print(f"\n📋 Session: {self.session_id}")
        print("=" * 60)

# === CONFIGURATION GLOBALE ===

# Instance globale de l'observatoire
observatory = None

def init_elite_observatory(project_name: str = "elite-cycling-coach") -> EliteCyclingObservatory:
    """Initialise l'observatoire elite global"""
    global observatory
    observatory = EliteCyclingObservatory(project_name)
    return observatory

def get_observatory() -> Optional[EliteCyclingObservatory]:
    """Retourne l'observatoire global"""
    return observatory

# === DECORATORS ELITE ===

def track_elite_operation(operation_type: str):
    """Décorateur pour tracker les opérations elite"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if observatory:
                    # Track selon le type d'opération
                    if operation_type == "workout_generation":
                        observatory.track_workout_generation(
                            workout_type=kwargs.get("workout_type", "unknown"),
                            duration=kwargs.get("duration", 0),
                            athlete_level=kwargs.get("level", "unknown"),
                            ftp=kwargs.get("ftp", 0),
                            response_time=response_time,
                            success=success
                        )
                    
                    observatory.counters["api_calls"] += 1
            
            return result
        return wrapper
    return decorator

# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__":
    # Test de l'observatoire elite
    print("🚴‍♂️ Test Elite Cycling Observatory")
    
    # Initialiser
    obs = init_elite_observatory("elite-cycling-coach-test")
    
    # Simuler quelques opérations
    import time
    
    # Simulation génération de séances
    obs.track_workout_generation(
        workout_type="vo2max",
        duration=75,
        athlete_level="elite",
        ftp=420,  # FTP de Pogačar level 😉
        response_time=1.2
    )
    
    obs.track_workout_generation(
        workout_type="threshold",
        duration=90,
        athlete_level="elite", 
        ftp=420,
        response_time=0.8
    )
    
    # Simulation planning
    obs.track_periodization_planning(
        duration_weeks=16,
        athlete_level="elite",
        model_type="polarized",
        events_count=3,
        response_time=2.1
    )
    
    # Simulation analyse athlète
    obs.track_athlete_analysis(
        athlete_id="pogacar_001",
        analysis_type="performance_trend",
        data_points=1000,
        insights_generated=15,
        response_time=0.5
    )
    
    # Afficher le dashboard
    obs.print_elite_summary()
    
    # Exporter les analytics
    export_path = obs.export_analytics()
    print(f"\n📁 Analytics exportées: {export_path}")