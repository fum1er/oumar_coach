#!/usr/bin/env python3
"""
Elite Configuration - Configuration Centralisée pour Coach Cycliste Elite
Architecture niveau WorldTour avec profil utilisateur personnalisé
"""

import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import json

# === PROFIL ATHLÈTE PRINCIPAL ===

@dataclass
class EliteAthleteProfile:
    """Profil athlète elite avec toutes les données physio"""
    
    # Identité
    athlete_id: str = "main_athlete"
    name: str = "Cycliste Elite"
    birth_date: Optional[str] = None  # Format YYYY-MM-DD
    
    # Données physiologiques actuelles
    ftp_watts: int = 320
    hr_max_bpm: int = 196
    weight_kg: float = 70.0
    height_cm: float = 175.0
    
    # Métriques dérivées (calculées automatiquement)
    ftp_per_kg: float = None
    hr_zones: Dict[str, tuple] = None
    power_zones: Dict[str, Dict] = None
    
    # Historique de progression
    ftp_history: List[Dict] = None  # [{"date": "2024-01-01", "ftp": 315, "test_type": "20min"}]
    weight_history: List[Dict] = None
    hr_max_history: List[Dict] = None
    
    # Préférences d'entraînement
    experience_level: str = "advanced"  # beginner, intermediate, advanced, elite
    training_availability: Dict[str, int] = None  # {"weekdays": 60, "weekends": 120}
    preferred_training_times: List[str] = None  # ["06:00", "18:00"]
    
    # Objectifs et événements
    primary_goals: List[str] = None
    target_events: List[Dict] = None
    current_season_phase: str = "base"  # base, build, peak, recovery, transition
    
    # Équipement et setup
    bike_setup: Dict[str, Any] = None
    power_meter: Optional[str] = None
    trainer_type: Optional[str] = None
    
    # Données médicales/santé (optionnel)
    resting_hr: Optional[int] = None
    vo2_max: Optional[float] = None
    lactate_threshold_hr: Optional[int] = None
    
    def __post_init__(self):
        """Calcule les métriques dérivées automatiquement"""
        self._calculate_derived_metrics()
        self._init_default_values()
    
    def _calculate_derived_metrics(self):
        """Calcule FTP/kg, zones FC et puissance"""
        
        # FTP par kg
        self.ftp_per_kg = round(self.ftp_watts / self.weight_kg, 2)
        
        # Zones de fréquence cardiaque (méthode Karvonen modifiée)
        if not self.resting_hr:
            self.resting_hr = 50  # Valeur par défaut pour cycliste entraîné
        
        hr_reserve = self.hr_max_bpm - self.resting_hr
        
        self.hr_zones = {
            "Z1": (self.resting_hr + int(hr_reserve * 0.50), self.resting_hr + int(hr_reserve * 0.60)),
            "Z2": (self.resting_hr + int(hr_reserve * 0.60), self.resting_hr + int(hr_reserve * 0.70)),
            "Z3": (self.resting_hr + int(hr_reserve * 0.70), self.resting_hr + int(hr_reserve * 0.80)),
            "Z4": (self.resting_hr + int(hr_reserve * 0.80), self.resting_hr + int(hr_reserve * 0.90)),
            "Z5": (self.resting_hr + int(hr_reserve * 0.90), self.hr_max_bpm)
        }
        
        # Zones de puissance (% FTP)
        self.power_zones = {
            "Z1": {"min_watts": int(self.ftp_watts * 0.45), "max_watts": int(self.ftp_watts * 0.55), "name": "Récupération Active"},
            "Z2": {"min_watts": int(self.ftp_watts * 0.56), "max_watts": int(self.ftp_watts * 0.75), "name": "Endurance Aérobie"},
            "Z3": {"min_watts": int(self.ftp_watts * 0.76), "max_watts": int(self.ftp_watts * 0.90), "name": "Tempo"},
            "Z4": {"min_watts": int(self.ftp_watts * 0.91), "max_watts": int(self.ftp_watts * 1.05), "name": "Seuil Lactique"},
            "Z5": {"min_watts": int(self.ftp_watts * 1.06), "max_watts": int(self.ftp_watts * 1.20), "name": "VO2max"},
            "Z6": {"min_watts": int(self.ftp_watts * 1.21), "max_watts": int(self.ftp_watts * 1.50), "name": "Capacité Anaérobie"},
            "Z7": {"min_watts": int(self.ftp_watts * 1.51), "max_watts": int(self.ftp_watts * 3.00), "name": "Puissance Neuromusculaire"}
        }
    
    def _init_default_values(self):
        """Initialise les valeurs par défaut si non définies"""
        
        if self.ftp_history is None:
            self.ftp_history = [
                {"date": datetime.now().strftime("%Y-%m-%d"), "ftp": self.ftp_watts, "test_type": "initial"}
            ]
        
        if self.weight_history is None:
            self.weight_history = [
                {"date": datetime.now().strftime("%Y-%m-%d"), "weight": self.weight_kg}
            ]
        
        if self.training_availability is None:
            self.training_availability = {"weekdays": 60, "weekends": 120}
        
        if self.preferred_training_times is None:
            self.preferred_training_times = ["06:00", "18:00"]
        
        if self.primary_goals is None:
            self.primary_goals = ["improve_ftp", "endurance", "racing"]
        
        if self.target_events is None:
            self.target_events = []
        
        if self.bike_setup is None:
            self.bike_setup = {
                "bike_type": "road",
                "position": "aggressive",
                "crank_length": 172.5,
                "tire_pressure": {"front": 85, "rear": 87}
            }

# === CONFIGURATION SYSTÈME ELITE ===

@dataclass
class LangSmithConfig:
    """Configuration LangSmith pour monitoring elite"""
    
    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: str = "https://api.smith.langchain.com"
    project_name: str = "elite-cycling-coach"
    
    # Tags pour organisation
    default_tags: List[str] = None
    environment: str = "development"  # development, staging, production
    
    # Sampling pour performance
    trace_sampling_rate: float = 1.0  # 1.0 = 100% des traces
    
    def __post_init__(self):
        if self.default_tags is None:
            self.default_tags = ["elite", "cycling", "ai-coach"]
        
        # Auto-détection clé API
        if self.api_key is None:
            self.api_key = os.getenv("LANGSMITH_API_KEY")

@dataclass
class LangGraphConfig:
    """Configuration LangGraph pour workflows complexes"""
    
    # Threads et parallélisme
    max_concurrent_threads: int = 4
    default_thread_timeout: int = 300  # 5 minutes
    
    # Retry policies
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Memory et state
    enable_persistence: bool = True
    state_backend: str = "memory"  # memory, redis, postgres
    
    # Workflows disponibles
    available_workflows: List[str] = None
    
    def __post_init__(self):
        if self.available_workflows is None:
            self.available_workflows = [
                "workout_generation",
                "periodization_planning", 
                "performance_analysis",
                "race_strategy",
                "recovery_monitoring"
            ]

@dataclass
class APIConfig:
    """Configuration pour intégrations API externes"""
    
    # Strava Integration
    strava_enabled: bool = False
    strava_client_id: Optional[str] = None
    strava_client_secret: Optional[str] = None
    
    # TrainingPeaks Integration  
    trainingpeaks_enabled: bool = False
    trainingpeaks_api_key: Optional[str] = None
    
    # Wahoo/MyWhoosh Integration
    wahoo_enabled: bool = False
    mywhoosh_enabled: bool = True
    
    # Weather APIs
    openweather_api_key: Optional[str] = None
    
    # Rate limiting
    api_rate_limits: Dict[str, int] = None
    
    def __post_init__(self):
        if self.api_rate_limits is None:
            self.api_rate_limits = {
                "strava": 600,  # requests per 15min
                "trainingpeaks": 1000,  # requests per hour
                "openweather": 1000  # requests per day
            }
        
        # Auto-détection clés API
        self.strava_client_id = os.getenv("STRAVA_CLIENT_ID")
        self.strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.trainingpeaks_api_key = os.getenv("TRAININGPEAKS_API_KEY")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")

@dataclass
class PerformanceConfig:
    """Configuration performance système"""
    
    # Cache settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 heure
    max_cache_size_mb: int = 100
    
    # Response times cibles
    target_workout_generation_time: float = 2.0  # secondes
    target_plan_generation_time: float = 5.0
    target_analysis_time: float = 1.0
    
    # Batch processing
    enable_batch_processing: bool = True
    batch_size: int = 10
    
    # Monitoring
    enable_performance_monitoring: bool = True
    log_slow_operations: bool = True
    slow_operation_threshold: float = 3.0  # secondes

# === CONFIGURATION PRINCIPALE ===

class EliteCoachConfig:
    """Configuration centralisée pour le coach cycliste elite"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialise la configuration elite"""
        
        # Configuration par défaut
        self.athlete = EliteAthleteProfile()
        self.langsmith = LangSmithConfig()
        self.langgraph = LangGraphConfig()
        self.apis = APIConfig()
        self.performance = PerformanceConfig()
        
        # Métadonnées système
        self.system_info = {
            "version": "1.0.0-elite",
            "created": datetime.now().isoformat(),
            "config_file": config_file,
            "environment": os.getenv("COACH_ENV", "development")
        }
        
        # Charger config custom si fournie
        if config_file:
            self.load_from_file(config_file)
        
        # Auto-update depuis variables d'environnement
        self._update_from_env()
    
    def _update_from_env(self):
        """Met à jour la config depuis les variables d'environnement"""
        
        # Athlète
        if os.getenv("ATHLETE_FTP"):
            self.athlete.ftp_watts = int(os.getenv("ATHLETE_FTP"))
            self.athlete._calculate_derived_metrics()
        
        if os.getenv("ATHLETE_HR_MAX"):
            self.athlete.hr_max_bpm = int(os.getenv("ATHLETE_HR_MAX"))
            self.athlete._calculate_derived_metrics()
        
        if os.getenv("ATHLETE_WEIGHT"):
            self.athlete.weight_kg = float(os.getenv("ATHLETE_WEIGHT"))
            self.athlete._calculate_derived_metrics()
        
        # Environnement
        env = os.getenv("COACH_ENV", "development")
        self.langsmith.environment = env
        self.system_info["environment"] = env
        
        # Performance selon environnement
        if env == "production":
            self.performance.enable_performance_monitoring = True
            self.langsmith.trace_sampling_rate = 0.1  # 10% en prod
        elif env == "development":
            self.performance.log_slow_operations = True
            self.langsmith.trace_sampling_rate = 1.0  # 100% en dev
    
    def get_athlete_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'athlète pour affichage"""
        
        return {
            "name": self.athlete.name,
            "ftp": f"{self.athlete.ftp_watts}W",
            "ftp_per_kg": f"{self.athlete.ftp_per_kg}W/kg",
            "hr_max": f"{self.athlete.hr_max_bpm}bpm",
            "level": self.athlete.experience_level,
            "power_zones": {
                zone: f"{data['min_watts']}-{data['max_watts']}W"
                for zone, data in self.athlete.power_zones.items()
            },
            "hr_zones": {
                zone: f"{hr_range[0]}-{hr_range[1]}bpm"
                for zone, hr_range in self.athlete.hr_zones.items()
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        
        return {
            "version": self.system_info["version"],
            "environment": self.system_info["environment"],
            "integrations": {
                "langsmith": self.langsmith.enabled and bool(self.langsmith.api_key),
                "strava": self.apis.strava_enabled and bool(self.apis.strava_client_id),
                "trainingpeaks": self.apis.trainingpeaks_enabled and bool(self.apis.trainingpeaks_api_key),
                "weather": bool(self.apis.openweather_api_key)
            },
            "performance": {
                "caching": self.performance.enable_caching,
                "monitoring": self.performance.enable_performance_monitoring,
                "target_response_time": f"{self.performance.target_workout_generation_time}s"
            }
        }
    
    def save_to_file(self, filepath: str):
        """Sauvegarde la configuration dans un fichier"""
        
        config_data = {
            "athlete": asdict(self.athlete),
            "langsmith": asdict(self.langsmith),
            "langgraph": asdict(self.langgraph),
            "apis": asdict(self.apis),
            "performance": asdict(self.performance),
            "system_info": self.system_info
        }
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration sauvegardée: {filepath}")
    
    def load_from_file(self, filepath: str):
        """Charge la configuration depuis un fichier"""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Reconstituer les objets dataclass
            if "athlete" in config_data:
                self.athlete = EliteAthleteProfile(**config_data["athlete"])
            
            if "langsmith" in config_data:
                self.langsmith = LangSmithConfig(**config_data["langsmith"])
            
            if "langgraph" in config_data:
                self.langgraph = LangGraphConfig(**config_data["langgraph"])
            
            if "apis" in config_data:
                self.apis = APIConfig(**config_data["apis"])
            
            if "performance" in config_data:
                self.performance = PerformanceConfig(**config_data["performance"])
            
            print(f"✅ Configuration chargée: {filepath}")
            
        except Exception as e:
            print(f"⚠️ Erreur chargement config: {e}")
    
    def print_elite_config(self):
        """Affiche la configuration elite de manière claire"""
        
        print("\n🏆 ELITE CYCLING COACH - CONFIGURATION")
        print("=" * 55)
        
        # Athlète
        print(f"👤 ATHLÈTE:")
        print(f"   • Nom: {self.athlete.name}")
        print(f"   • FTP: {self.athlete.ftp_watts}W ({self.athlete.ftp_per_kg}W/kg)")
        print(f"   • FC Max: {self.athlete.hr_max_bpm}bpm")
        print(f"   • Niveau: {self.athlete.experience_level}")
        print(f"   • Poids: {self.athlete.weight_kg}kg")
        
        # Zones de puissance clés
        print(f"\n⚡ ZONES DE PUISSANCE:")
        for zone in ["Z2", "Z4", "Z5"]:
            data = self.athlete.power_zones[zone]
            print(f"   • {zone} ({data['name']}): {data['min_watts']}-{data['max_watts']}W")
        
        # Système
        status = self.get_system_status()
        print(f"\n🔧 SYSTÈME:")
        print(f"   • Version: {status['version']}")
        print(f"   • Environnement: {status['environment']}")
        print(f"   • LangSmith: {'✅' if status['integrations']['langsmith'] else '❌'}")
        print(f"   • Monitoring: {'✅' if status['performance']['monitoring'] else '❌'}")
        
        # Objectifs
        print(f"\n🎯 OBJECTIFS:")
        for goal in self.athlete.primary_goals:
            print(f"   • {goal.replace('_', ' ').title()}")
        
        print("=" * 55)

# === INSTANCE GLOBALE ===

# Configuration globale du coach elite
elite_config = None

def init_elite_config(config_file: Optional[str] = None) -> EliteCoachConfig:
    """Initialise la configuration elite globale"""
    global elite_config
    elite_config = EliteCoachConfig(config_file)
    return elite_config

def get_elite_config() -> EliteCoachConfig:
    """Retourne la configuration elite globale"""
    global elite_config
    if elite_config is None:
        elite_config = EliteCoachConfig()
    return elite_config

# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__":
    print("🚴‍♂️ Test Elite Configuration System")
    
    # Initialiser avec tes données perso
    config = EliteCoachConfig()
    
    # Mettre à jour avec tes vraies données
    config.athlete.name = "Killian Guélou"
    config.athlete.ftp_watts = 320
    config.athlete.hr_max_bpm = 196
    config.athlete.weight_kg = 80.0  # Ajuste selon ton poids
    config.athlete.experience_level = "advanced"
    config.athlete.primary_goals = ["improve_ftp", "racing", "endurance"]
    
    # Recalculer les métriques
    config.athlete._calculate_derived_metrics()
    
    # Afficher la config
    config.print_elite_config()
    
    # Résumé athlète
    print("\n📊 RÉSUMÉ ATHLÈTE:")
    summary = config.get_athlete_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Sauvegarder la config
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    config.save_to_file("config/my_elite_config.json")
    
    print("\n✅ Configuration elite créée et sauvegardée !")