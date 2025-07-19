#!/usr/bin/env python3
"""
Cycling AI Agent Elite - Version Complète Intégrée
Agent de coaching cycliste avec architecture elite complète :
- Configuration centralisée (Killian : 320W FTP, 196 FC max)
- Monitoring LangSmith automatique
- Performance tracking en temps réel
- Génération de séances personnalisées
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import re

# Ajouter le répertoire courant au path pour les imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Charger le .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Fichier .env chargé")
except ImportError:
    print("⚠️ python-dotenv non installé (optionnel)")

# === IMPORTS ELITE ===

# Configuration Elite (données personnelles Killian)
try:
    from config.elite_config import EliteCoachConfig, get_elite_config, init_elite_config
    ELITE_CONFIG_AVAILABLE = True
    print("✅ Configuration Elite disponible")
except ImportError:
    print("❌ Configuration Elite non trouvée - Créez config/elite_config.py")
    ELITE_CONFIG_AVAILABLE = False

# Monitoring Elite (LangSmith Observatory)
try:
    from langsmith_setup import EliteCyclingObservatory, init_elite_observatory, get_observatory, track_elite_operation
    ELITE_MONITORING_AVAILABLE = True
    print("✅ Monitoring Elite disponible")
except ImportError:
    print("❌ Monitoring Elite non trouvé - Créez langsmith_setup.py")
    ELITE_MONITORING_AVAILABLE = False

# LangChain imports avec gestion d'erreur
try:
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents import create_openai_functions_agent, AgentExecutor
    from tools.periodization_tool import create_periodization_tool
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain disponible")
except ImportError as e:
    print(f"⚠️ LangChain non installé: {e}")
    print("💡 Installez avec: pip install langchain langchain-openai langchain-community faiss-cpu")
    LANGCHAIN_AVAILABLE = False

# Imports modulaires existants
try:
    from core.models import UserProfile, WorkoutRequest
    from core.knowledge_base import KnowledgeBaseManager
    from core.calculations import TrainingCalculations
    from tools.knowledge_tool import create_knowledge_tool
    from tools.workout_tool import create_workout_tool
    from generators.workout_builder import WorkoutBuilder
    from generators.file_generators import FileGenerator
    
    MODULES_LOADED = True
    print("✅ Modules cycliste chargés")
    
except ImportError as e:
    print(f"❌ Erreur import modules: {e}")
    print("💡 Assurez-vous que tous les fichiers sont présents dans les bons dossiers")
    MODULES_LOADED = False

# === AGENT ELITE INTÉGRÉ ===

class EliteCyclingAIAgent:
    """
    Agent de coaching cycliste Elite avec architecture complète :
    - Configuration personnalisée (Killian : 320W FTP, 196 FC max)
    - Monitoring LangSmith temps réel
    - Performance tracking automatique
    - Génération de séances adaptées
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialise l'agent elite avec toute l'infrastructure"""
        
        print("\n🏆 INITIALISATION AGENT ELITE")
        print("=" * 50)
        
        # Vérifier les prérequis
        if not MODULES_LOADED:
            raise ImportError("Modules cycliste non disponibles")
        
        # 1. CONFIGURATION ELITE (données personnelles)
        self._init_elite_config()
        
        # 2. MONITORING ELITE (LangSmith Observatory)
        self._init_elite_monitoring()
        
        # 3. API Configuration
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API OpenAI requise. Définissez OPENAI_API_KEY ou passez-la en paramètre")
        
        # 4. Composants de base
        self._init_core_components()
        
        # 5. LangChain si disponible
        if LANGCHAIN_AVAILABLE:
            self._init_langchain_components()
        else:
            print("⚠️ Mode dégradé: LangChain non disponible")
            self.agent_executor = None
        
        print("🚀 Agent Elite initialisé avec succès !")
    
    def _init_elite_config(self):
        """Initialise la configuration elite avec les données personnelles"""
        
        if ELITE_CONFIG_AVAILABLE:
            try:
                # Charger la configuration existante
                self.elite_config = get_elite_config()
                
                # Si pas encore initialisée, créer avec les données de base
                if not hasattr(self.elite_config, 'athlete'):
                    self.elite_config = init_elite_config()
                
                # Afficher le profil chargé
                athlete = self.elite_config.athlete
                print(f"👤 PROFIL CHARGÉ : {athlete.name}")
                print(f"   • FTP: {athlete.ftp_watts}W ({athlete.ftp_per_kg}W/kg)")
                print(f"   • FC Max: {athlete.hr_max_bpm}bpm")
                print(f"   • Niveau: {athlete.experience_level}")
                
            except Exception as e:
                print(f"⚠️ Erreur chargement config elite: {e}")
                self.elite_config = None
        else:
            print("⚠️ Configuration elite non disponible - Utilisation valeurs par défaut")
            self.elite_config = None
    
    def _init_elite_monitoring(self):
        """Initialise le monitoring elite LangSmith"""
        
        if ELITE_MONITORING_AVAILABLE:
            try:
                # Initialiser l'observatoire global
                self.observatory = init_elite_observatory("killian-elite-coach")
                print(f"📊 Observatoire Elite activé - Session: {self.observatory.session_id}")
            except Exception as e:
                print(f"⚠️ Erreur monitoring: {e}")
                self.observatory = None
        else:
            print("⚠️ Monitoring elite non disponible")
            self.observatory = None
    
    def _init_core_components(self):
        """Initialise les composants de base"""
        try:
            self.knowledge_manager = KnowledgeBaseManager()
            self.calculator = TrainingCalculations()
            self.workout_builder = WorkoutBuilder()
            self.file_generator = FileGenerator()
            print("✅ Composants de base initialisés")
        except Exception as e:
            raise RuntimeError(f"Erreur initialisation composants: {e}")
    
    def _init_langchain_components(self):
        """Initialise les composants LangChain avec profil personnalisé"""
        try:
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
            
            # Outils (avec données personnalisées)
            self.tools = []
            try:
                knowledge_tool = create_knowledge_tool()
                workout_tool = create_workout_tool()
                periodization_tool = create_periodization_tool()
                
                self.tools = [knowledge_tool, workout_tool, periodization_tool]
                print("✅ Outils LangChain créés avec données personnalisées")
            except Exception as e:
                print(f"⚠️ Erreur création outils: {e}")
                self.tools = []
            
            # Prompt système personnalisé
            self.system_prompt = self._create_personalized_prompt()
            
            # Agent
            if self.tools:
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
                print("✅ Agent LangChain personnalisé initialisé")
            else:
                self.agent_executor = None
                print("⚠️ Agent non créé (pas d'outils)")
                
        except Exception as e:
            print(f"⚠️ Erreur LangChain: {e}")
            self.agent_executor = None
    
    def _create_personalized_prompt(self) -> ChatPromptTemplate:
        """Crée un prompt système personnalisé avec les données de l'athlète"""
        
        # Récupérer les données pour personnaliser le prompt
        if self.elite_config:
            athlete = self.elite_config.athlete
            athlete_info = f"""
PROFIL ATHLÈTE ACTUEL : {athlete.name}
• FTP: {athlete.ftp_watts}W ({athlete.ftp_per_kg}W/kg)
• FC Max: {athlete.hr_max_bpm}bpm
• Niveau: {athlete.experience_level}
• Zones clés: 
  - Z2 Endurance: {athlete.power_zones['Z2']['min_watts']}-{athlete.power_zones['Z2']['max_watts']}W
  - Z4 Seuil: {athlete.power_zones['Z4']['min_watts']}-{athlete.power_zones['Z4']['max_watts']}W
  - Z5 VO2max: {athlete.power_zones['Z5']['min_watts']}-{athlete.power_zones['Z5']['max_watts']}W
"""
        else:
            athlete_info = "PROFIL ATHLÈTE : Configuration par défaut (320W FTP)"
        
        system_message = f"""Tu es un COACH CYCLISTE IA D'ÉLITE personnalisé pour cet athlète spécifique.

{athlete_info}

🎯 MISSION PERSONNALISÉE:
- Créer des séances EXACTEMENT adaptées à ce profil
- Utiliser les zones de puissance PERSONNALISÉES calculées
- Proposer des progressions basées sur les données actuelles
- Monitorer et tracker toutes les interactions

⚡ GÉNÉRATION PERSONNALISÉE:
• Utilise TOUJOURS les données FTP réelles de l'athlète
• Adapte les zones selon le profil exact
• Propose des progressions cohérentes avec le niveau
• Justifie scientifiquement chaque recommandation

🔬 OUTILS DISPONIBLES:
• 'cycling_knowledge' pour la théorie scientifique
• 'generate_advanced_workout' avec les vraies données
• 'create_periodization_plan' pour la planification long terme

💡 COACHING PERSONNALISÉ:
• Analyse le profil complet avant chaque recommandation
• Adapte le langage au niveau d'expérience
• Propose des défis progressifs et réalisables
• Fournis des conseils pratiques d'exécution

🔧 WORKFLOW ELITE:
1. Analyser le profil athlète actuel
2. Adapter la recommandation aux capacités exactes
3. Générer avec les paramètres personnalisés
4. Expliquer le "pourquoi" scientifique
5. Proposer la suite logique

Sois un coach d'élite qui connaît parfaitement cet athlète ! 🏆"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    # === MÉTHODES PRINCIPALES AVEC MONITORING ===
    
    def chat(self, message: str) -> str:
        """Interface de chat avec monitoring automatique"""
        
        start_time = time.time()
        
        try:
            if self.agent_executor:
                # Mode complet avec LangChain + monitoring
                response = self.agent_executor.invoke(
                    {"input": message},
                    return_only_outputs=True
                )
                result = response.get("output", "Désolé, je n'ai pas pu traiter votre demande.")
                
                # Tracking automatique si observatoire disponible
                if self.observatory:
                    response_time = time.time() - start_time
                    self.observatory.counters["api_calls"] += 1
                
                return result
            else:
                # Mode dégradé avec monitoring
                return self._fallback_response_with_monitoring(message, start_time)
                
        except Exception as e:
            if self.observatory:
                response_time = time.time() - start_time
                self.observatory.counters["errors"] += 1
            
            print(f"⚠️ Erreur agent: {e}")
            return self._fallback_response_with_monitoring(message, start_time)
    
    def _fallback_response_with_monitoring(self, message: str, start_time: float) -> str:
        """Réponse de fallback avec monitoring intégré"""
        
        message_lower = message.lower()
        
        # Détection d'intention avec données personnalisées
        if any(word in message_lower for word in ['séance', 'workout', 'entrainement', 'entraînement']):
            result = self._create_personalized_workout(message_lower)
        elif any(word in message_lower for word in ['zone', 'puissance', 'ftp']):
            result = self._provide_personalized_zone_info(message_lower)
        elif any(word in message_lower for word in ['plan', 'periodisation', 'planification']):
            result = self._create_periodization_plan(message_lower)
        elif any(word in message_lower for word in ['aide', 'help', 'bonjour', 'salut']):
            result = self._provide_personalized_help()
        else:
            result = self._provide_default_help()
        
        # Monitoring
        if self.observatory:
            response_time = time.time() - start_time
            self.observatory.performance_metrics["response_times"].append(response_time)
            self.observatory.counters["api_calls"] += 1
        
        return result
    
    def _create_personalized_workout(self, message: str) -> str:
        """Création de séance avec données exactes de l'athlète"""
        
        start_time = time.time()
        
        try:
            # Utiliser les données réelles de l'athlète
            athlete_ftp = 320  # Données par défaut
            athlete_level = "advanced"
            athlete_name = "Cycliste"
            
            if self.elite_config:
                athlete_ftp = self.elite_config.athlete.ftp_watts
                athlete_level = self.elite_config.athlete.experience_level
                athlete_name = self.elite_config.athlete.name
            
            # Détection type et durée
            if 'vo2max' in message or 'vo2' in message:
                workout_type = 'vo2max'
            elif 'seuil' in message or 'threshold' in message or 'ftp' in message:
                workout_type = 'threshold'
            elif 'endurance' in message:
                workout_type = 'endurance'
            elif 'recovery' in message or 'récupération' in message:
                workout_type = 'recovery'
            else:
                workout_type = 'vo2max'  # Par défaut
            
            duration_match = re.search(r'(\d+)\s*(?:min|minutes?)', message)
            duration = int(duration_match.group(1)) if duration_match else 75
            
            # Créer la séance avec les données personnalisées
            workout = self.workout_builder.create_smart_workout(
                workout_type=workout_type,
                duration=duration,
                level=athlete_level,
                ftp=athlete_ftp
            )
            
            # Calculer métriques
            tss = self.calculator.calculate_tss(
                workout.segments, 
                workout.repeated_intervals, 
                athlete_ftp
            )
            workout.estimated_tss = tss
            
            # Générer fichiers
            files = self.file_generator.generate_all_formats(workout)
            
            # Monitoring avec les données personnalisées
            if self.observatory:
                response_time = time.time() - start_time
                self.observatory.track_workout_generation(
                    workout_type=workout_type,
                    duration=duration,
                    athlete_level=athlete_level,
                    ftp=athlete_ftp,
                    response_time=response_time,
                    success=True
                )
            
            return f"""✅ Séance personnalisée '{workout.name}' créée pour {athlete_name} !

👤 **Basée sur ton profil:**
• FTP: {athlete_ftp}W
• Niveau: {athlete_level}

📊 **Ta séance:**
{workout.description}

🎯 **Objectif scientifique:**
{workout.scientific_objective}

📈 **Tes métriques:**
• Durée: {workout.total_duration} minutes
• TSS estimé: {tss:.0f}
• Temps haute intensité: {self.calculator.calculate_high_intensity_time(workout)} minutes

📁 **Fichiers générés:**
{chr(10).join([f"• {k}: {Path(v).name}" for k, v in files.items()])}

💡 **Conseils personnalisés:**
{workout.coaching_tips}

🔥 **Coach Elite:** La séance est parfaitement calibrée sur tes {athlete_ftp}W de FTP !"""
            
        except Exception as e:
            if self.observatory:
                response_time = time.time() - start_time
                self.observatory.counters["errors"] += 1
            return f"❌ Erreur création séance personnalisée: {e}"
    
    def _provide_personalized_zone_info(self, message: str) -> str:
        """Informations sur les zones avec données exactes de l'athlète"""
        
        if not self.elite_config:
            return self.knowledge_manager.search_knowledge(message)
        
        athlete = self.elite_config.athlete
        
        # Détection zone spécifique
        zone_map = {'z1': 'Z1', 'z2': 'Z2', 'z3': 'Z3', 'z4': 'Z4', 'z5': 'Z5', 'z6': 'Z6', 'z7': 'Z7'}
        
        for zone_key, zone_id in zone_map.items():
            if zone_key in message:
                power_zone = athlete.power_zones[zone_id]
                hr_zone = athlete.hr_zones.get(zone_id, (0, 0)) if zone_id in ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'] else (0, 0)
                
                return f"""🔍 **Ta Zone {zone_id} personnalisée - {power_zone['name']}**

⚡ **Ta puissance:** {power_zone['min_watts']}-{power_zone['max_watts']}W
💓 **Ta FC:** {hr_zone[0] if hr_zone[0] > 0 else 'N/A'}-{hr_zone[1] if hr_zone[1] > 0 else 'N/A'}bpm
📊 **% de ton FTP ({athlete.ftp_watts}W):** {int(power_zone['min_watts']/athlete.ftp_watts*100)}-{int(power_zone['max_watts']/athlete.ftp_watts*100)}%

🎯 **Pour toi {athlete.name}:**
Cette zone représente {int((power_zone['min_watts'] + power_zone['max_watts'])/2)}W en moyenne.
Idéal pour {power_zone['name'].lower()}.

💡 **Conseil perso:** Utilise un capteur de puissance pour rester dans cette plage exacte !"""
        
        # Affichage de toutes les zones
        return f"""📊 **Tes zones de puissance personnalisées (FTP: {athlete.ftp_watts}W):**

• **Z1 Récupération:** {athlete.power_zones['Z1']['min_watts']}-{athlete.power_zones['Z1']['max_watts']}W
• **Z2 Endurance:** {athlete.power_zones['Z2']['min_watts']}-{athlete.power_zones['Z2']['max_watts']}W  ← Zone de base
• **Z3 Tempo:** {athlete.power_zones['Z3']['min_watts']}-{athlete.power_zones['Z3']['max_watts']}W
• **Z4 Seuil:** {athlete.power_zones['Z4']['min_watts']}-{athlete.power_zones['Z4']['max_watts']}W  ← Ton FTP !
• **Z5 VO2max:** {athlete.power_zones['Z5']['min_watts']}-{athlete.power_zones['Z5']['max_watts']}W  ← Intervalles durs
• **Z6 Anaérobie:** {athlete.power_zones['Z6']['min_watts']}-{athlete.power_zones['Z6']['max_watts']}W
• **Z7 Neuromusculaire:** {athlete.power_zones['Z7']['min_watts']}-{athlete.power_zones['Z7']['max_watts']}W

🎯 **Spécialement calculées pour toi !**"""
    
    def _create_periodization_plan(self, message: str) -> str:
        """Création d'un plan de périodisation personnalisé"""
        
        if not self.elite_config:
            return "⚠️ Plan de périodisation nécessite ta configuration elite"
        
        athlete = self.elite_config.athlete
        
        # Détection durée
        duration_match = re.search(r'(\d+)\s*(?:semaine|week)', message)
        duration_weeks = int(duration_match.group(1)) if duration_match else 12
        
        return f"""🗓️ **Plan de périodisation personnalisé pour {athlete.name}**

📊 **Basé sur ton profil:**
• FTP actuel: {athlete.ftp_watts}W
• Niveau: {athlete.experience_level}
• Objectifs: {', '.join(athlete.primary_goals)}

🎯 **Plan {duration_weeks} semaines:**
• Projection FTP: {athlete.ftp_watts}W → {int(athlete.ftp_watts * 1.08)}W (+{int(athlete.ftp_watts * 0.08)}W)
• Modèle recommandé: Polarisé (Seiler)
• TSS hebdomadaire: 300-450 points

📅 **Structure recommandée:**
• Semaines 1-5: Base aérobie (Z2 focus)
• Semaines 6-10: Développement (Z4-Z5)
• Semaines 11-{duration_weeks}: Pic et récupération

💡 **Pour générer le plan complet, utilise:**
"Crée un plan de {duration_weeks} semaines avec mes données"

🚀 **Ton coach elite va optimiser chaque phase pour maximiser tes gains !**"""
    
    def _provide_personalized_help(self) -> str:
        """Message d'aide personnalisé"""
        
        athlete_info = ""
        if self.elite_config:
            athlete = self.elite_config.athlete
            athlete_info = f"""
👤 **Ton profil actuel:**
• {athlete.name}
• FTP: {athlete.ftp_watts}W ({athlete.ftp_per_kg}W/kg)
• FC Max: {athlete.hr_max_bpm}bpm
• Niveau: {athlete.experience_level}
"""
        
        return f"""🏆 **Coach Elite Personnalisé**
{athlete_info}
📋 **Commandes spécialement pour toi:**
• `Crée-moi une séance VO2max de 75 minutes`
• `Séance threshold avec mes zones`
• `Plan de 12 semaines pour progression FTP`
• `Mes zones de puissance`
• `dashboard` - Voir tes statistiques
• `profil` - Afficher ton profil complet

🎯 **Séances adaptées à ton niveau:**
• **VO2max:** Intervalles calibrés sur tes capacités
• **Threshold:** Blocs au seuil de ton FTP
• **Endurance:** Base aérobie optimisée

💡 **Ton coach elite connaît ton profil et adapte tout automatiquement !**

Que veux-tu travailler aujourd'hui ? 🚀"""
    
    def _provide_default_help(self) -> str:
        """Aide par défaut avec invitation à personnaliser"""
        return """🚴 Coach Elite: Je peux t'aider avec des séances parfaitement calibrées !

• Génération de séances personnalisées
• Plans d'entraînement long terme  
• Informations sur tes zones exactes
• Conseils de progression

Essaie: "Crée-moi une séance VO2max de 75 minutes"

💎 **Mode Elite activé** - Toutes tes séances sont personnalisées avec tes vraies données !

Pour une expérience complète, assure-toi d'avoir :
• `config/elite_config.py` avec tes données
• `langsmith_setup.py` pour le monitoring"""
    
    def get_elite_dashboard(self) -> str:
        """Affiche le dashboard elite avec données personnalisées"""
        
        if not self.observatory:
            return "⚠️ Monitoring non disponible - Vérifiez langsmith_setup.py"
        
        dashboard = self.observatory.get_performance_dashboard()
        
        # Ajouter les infos personnelles
        athlete_info = ""
        if self.elite_config:
            athlete = self.elite_config.athlete
            athlete_info = f"""
👤 **TON PROFIL ACTUEL:**
• Nom: {athlete.name}
• FTP: {athlete.ftp_watts}W ({athlete.ftp_per_kg}W/kg)
• FC Max: {athlete.hr_max_bpm}bpm
• Niveau: {athlete.experience_level}
"""
        
        return f"""🏆 **DASHBOARD ELITE PERSONNALISÉ**
{athlete_info}
📊 **PERFORMANCES SESSION:**
• Temps de réponse moyen: {dashboard['performance_metrics']['avg_response_time_seconds']}s
• Taux de succès: {dashboard['performance_metrics']['success_rate_percent']}%
• Séances générées: {dashboard['usage_statistics']['workouts_generated']}
• Plans créés: {dashboard['usage_statistics']['plans_created']}

🎯 **USAGE POPULAIRE:**
{chr(10).join([f"• {workout}: {count}" for workout, count in dashboard['popular_features']['top_workout_types']]) if dashboard['popular_features']['top_workout_types'] else "• Aucune donnée encore"}

🔧 **SYSTÈME:**
• LangSmith: {dashboard['system_health']['langsmith_status']}
• Session: {dashboard['session_info']['session_id']}
• Uptime: {dashboard['system_health']['uptime']}
• Mémoire: {dashboard['system_health']['memory_usage']}"""
    
    def reset_conversation(self):
        """Reset de la conversation avec message personnalisé"""
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
            print("🔄 Conversation remise à zéro")
            if self.elite_config:
                print(f"👤 Profil {self.elite_config.athlete.name} toujours actif")

# === FONCTIONS UTILITAIRES ===

def check_dependencies() -> Dict[str, bool]:
    """Vérifie les dépendances installées"""
    deps = {
        "langchain": LANGCHAIN_AVAILABLE,
        "modules": MODULES_LOADED,
        "elite_config": ELITE_CONFIG_AVAILABLE,
        "elite_monitoring": ELITE_MONITORING_AVAILABLE,
        "openai_key": bool(os.getenv("OPENAI_API_KEY"))
    }
    return deps

def print_dependency_status():
    """Affiche le statut des dépendances"""
    deps = check_dependencies()
    
    print("\n🔍 **Statut des dépendances:**")
    for name, status in deps.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'OK' if status else 'Manquant'}")
    
    if not deps["langchain"]:
        print("\n💡 **Pour installer LangChain:**")
        print("pip install langchain langchain-openai langchain-community faiss-cpu")
    
    if not deps["elite_config"]:
        print("\n💡 **Pour la configuration elite:**")
        print("Créez le fichier config/elite_config.py avec vos données")
    
    if not deps["elite_monitoring"]:
        print("\n💡 **Pour le monitoring elite:**")
        print("Créez le fichier langsmith_setup.py")
    
    if not deps["openai_key"]:
        print("\n💡 **Pour configurer OpenAI:**")
        print("Créez un fichier .env avec: OPENAI_API_KEY=votre_clé_ici")

# === INTERFACE PRINCIPALE ELITE ===

def main():
    """Interface principale du coach elite intégré"""
    print("🏆 ELITE CYCLING COACH - Architecture Complète Intégrée")
    print("=" * 65)
    
    # Vérifications préalables
    print_dependency_status()
    
    if not MODULES_LOADED:
        print("\n❌ Modules de base manquants. Impossible de continuer.")
        return
    
    # Vérifier clé API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ Clé API OpenAI non trouvée !")
        print("L'agent fonctionnera en mode dégradé")
        
        choice = input("\nContinuer en mode dégradé ? (o/n): ").lower()
        if choice != 'o':
            return
    
    try:
        # Initialiser l'agent elite
        coach = EliteCyclingAIAgent()
        
        print(f"\n🚀 Coach Elite initialisé avec succès !")
        
        if coach.agent_executor:
            print("🧠 Mode complet: LangChain + Monitoring + Config personnalisée")
        else:
            print("⚙️ Mode dégradé: Fonctionnalités de base avec données personnalisées")
        
        # Afficher le profil si disponible
        if coach.elite_config:
            athlete = coach.elite_config.athlete
            print(f"\n👤 Profil actif: {athlete.name} - {athlete.ftp_watts}W FTP ({athlete.ftp_per_kg}W/kg)")
        
        print("\nCommandes spéciales:")
        print("• 'dashboard' - Tableau de bord elite")
        print("• 'profil' - Afficher le profil complet")
        print("• 'quit' - Quitter")
        print("• 'reset' - Nouvelle conversation")
        print("• 'help' - Guide d'utilisation")
        print()
        
        # Boucle conversationnelle elite
        while True:
            user_input = input("👤 Vous: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Au revoir ! Excellents entraînements !")
                if coach.observatory:
                    print("\n📊 Résumé de la session:")
                    coach.observatory.print_elite_summary()
                break
                
            elif user_input.lower() == 'reset':
                coach.reset_conversation()
                continue
                
            elif user_input.lower() == 'dashboard':
                print(coach.get_elite_dashboard())
                continue
                
            elif user_input.lower() == 'profil':
                if coach.elite_config:
                    coach.elite_config.print_elite_config()
                else:
                    print("⚠️ Profil non disponible - Créez config/elite_config.py")
                continue
                
            elif user_input.lower() in ['help', 'aide']:
                print(coach._provide_personalized_help())
                continue
                
            elif not user_input:
                continue
            
            print(f"\n🤖 Coach Elite: ")
            response = coach.chat(user_input)
            print(response)
            print()
    
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        print("💡 Vérifiez que tous les modules sont correctement installés")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()