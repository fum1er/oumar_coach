#!/usr/bin/env python3
"""
Cycling AI Agent - Prototype avec LangChain
Version de démarrage avant LangGraph
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path

# Charger le fichier .env automatiquement
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge automatiquement le .env
    ENV_LOADED = True
except ImportError:
    print("💡 Installez python-dotenv pour charger .env automatiquement: pip install python-dotenv")
    ENV_LOADED = False

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema import SystemMessage, HumanMessage, AIMessage
    from langchain.tools import BaseTool, tool
    from langchain.agents import create_openai_functions_agent, AgentExecutor
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️ LangChain non installé. Utilisez: pip install langchain langchain-openai")
    LANGCHAIN_AVAILABLE = False

# === STRUCTURES DE DONNÉES ===

@dataclass
class UserProfile:
    """Profil utilisateur persistant"""
    user_id: str = "default_user"
    name: str = "Cycliste"
    age: int = 30
    weight: float = 70.0
    ftp: int = 250
    ftp_history: List[tuple] = None  # [(date, ftp_value)]
    
    # Objectifs et préférences
    primary_goals: List[str] = None  # ["improve_ftp", "endurance", "weight_loss"]
    target_events: List[Dict] = None  # [{"name": "Century Ride", "date": "2025-08-15"}]
    available_time: Dict = None  # {"weekdays": 60, "weekends": 120}
    
    # Données d'entraînement
    recent_activities: List[Dict] = None
    training_load_history: List[float] = None
    fatigue_score: float = 0.0
    
    # Préférences système
    preferred_platforms: List[str] = None  # ["mywhoosh", "trainingpeaks"]
    
    def __post_init__(self):
        if self.ftp_history is None:
            self.ftp_history = [(datetime.now().strftime("%Y-%m-%d"), self.ftp)]
        if self.primary_goals is None:
            self.primary_goals = ["general_fitness"]
        if self.target_events is None:
            self.target_events = []
        if self.available_time is None:
            self.available_time = {"weekdays": 60, "weekends": 90}
        if self.recent_activities is None:
            self.recent_activities = []
        if self.training_load_history is None:
            self.training_load_history = []
        if self.preferred_platforms is None:
            self.preferred_platforms = ["mywhoosh"]

@dataclass
class WorkoutRequest:
    """Demande de séance d'entraînement"""
    duration_minutes: int
    workout_type: str  # "endurance", "threshold", "vo2max", "recovery"
    intensity_preference: str  # "easy", "moderate", "hard"
    target_date: str
    special_notes: str = ""

# === OUTILS LANGCHAIN ===

class WorkoutGeneratorTool(BaseTool):
    """Outil de génération de séances d'entraînement"""
    name = "generate_workout"
    description = "Génère une séance d'entraînement. Paramètres: type (endurance/threshold/vo2max/recovery), duration_minutes (int), notes (str)"
    
    def _run(self, type: str = "endurance", duration_minutes: int = 60, notes: str = "") -> str:
        """Génère une séance basée sur les paramètres simples"""
        try:
            # Profil utilisateur par défaut
            user_ftp = 320  # Utiliser la valeur mentionnée par l'utilisateur
            
            # Générer la séance selon le type
            workout = self._create_workout(type, duration_minutes, user_ftp)
            
            # Générer les fichiers
            files = self._generate_files(workout)
            
            return f"✅ Séance '{workout['name']}' générée avec succès!\n📁 Fichiers: {', '.join([f'{k}: {Path(v).name}' for k, v in files.items()])}"
            
        except Exception as e:
            return f"❌ Erreur lors de la génération: {str(e)}"
    
    def _create_workout(self, workout_type: str, duration: int, ftp: int) -> Dict:
        """Crée la structure de la séance"""
        if workout_type.lower() in ['vo2max', 'vo2', 'intervalle']:
            return self._create_vo2max_workout(duration, ftp)
        elif workout_type.lower() in ['threshold', 'seuil', 'z4']:
            return self._create_threshold_workout(duration, ftp)
        elif workout_type.lower() in ['recovery', 'recuperation', 'z1']:
            return self._create_recovery_workout(duration, ftp)
        else:  # endurance par défaut
            return self._create_endurance_workout(duration, ftp)
    
    def _create_endurance_workout(self, duration: int, ftp: int) -> Dict:
        """Crée une séance d'endurance"""
        warmup_time = min(15, duration // 6)
        cooldown_time = min(15, duration // 6)
        main_time = duration - warmup_time - cooldown_time
        
        intervals = [
            {
                'duration': warmup_time,
                'zone': 'Z1',
                'power_min': int(ftp * 0.0),
                'power_max': int(ftp * 0.55),
                'cadence': 85,
                'description': 'Échauffement progressif'
            },
            {
                'duration': main_time,
                'zone': 'Z2',
                'power_min': int(ftp * 0.56),
                'power_max': int(ftp * 0.75),
                'cadence': 90,
                'description': 'Endurance aérobie stable'
            },
            {
                'duration': cooldown_time,
                'zone': 'Z1',
                'power_min': int(ftp * 0.0),
                'power_max': int(ftp * 0.55),
                'cadence': 85,
                'description': 'Retour au calme'
            }
        ]
        
        return {
            'name': f'Endurance {duration}min',
            'description': 'Séance d\'endurance aérobie pour développer la base cardiovasculaire',
            'focus': 'endurance',
            'total_duration': duration,
            'intervals': intervals,
            'ftp': ftp
        }
    
    def _create_threshold_workout(self, duration: int, ftp: int) -> Dict:
        """Crée une séance de seuil"""
        # 2x20min threshold classique si assez de temps
        if duration >= 80:
            intervals = [
                {'duration': 15, 'zone': 'Z1', 'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55), 'cadence': 85, 'description': 'Échauffement'},
                {'duration': 10, 'zone': 'Z2', 'power_min': int(ftp * 0.56), 'power_max': int(ftp * 0.75), 'cadence': 90, 'description': 'Préparation'},
                {'duration': 20, 'zone': 'Z4', 'power_min': int(ftp * 0.91), 'power_max': int(ftp * 1.05), 'cadence': 95, 'description': 'Bloc seuil 1'},
                {'duration': 5, 'zone': 'Z2', 'power_min': int(ftp * 0.56), 'power_max': int(ftp * 0.75), 'cadence': 85, 'description': 'Récupération'},
                {'duration': 20, 'zone': 'Z4', 'power_min': int(ftp * 0.91), 'power_max': int(ftp * 1.05), 'cadence': 95, 'description': 'Bloc seuil 2'},
                {'duration': 10, 'zone': 'Z1', 'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55), 'cadence': 80, 'description': 'Retour au calme'}
            ]
            name = "Threshold 2x20min"
        else:
            # Version courte
            main_time = duration - 30
            intervals = [
                {'duration': 15, 'zone': 'Z1', 'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55), 'cadence': 85, 'description': 'Échauffement'},
                {'duration': main_time, 'zone': 'Z4', 'power_min': int(ftp * 0.91), 'power_max': int(ftp * 1.05), 'cadence': 95, 'description': 'Bloc seuil continu'},
                {'duration': 15, 'zone': 'Z1', 'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55), 'cadence': 80, 'description': 'Retour au calme'}
            ]
            name = f"Threshold {main_time}min"
        
        return {
            'name': name,
            'description': 'Séance de seuil lactique pour améliorer le FTP',
            'focus': 'threshold',
            'total_duration': duration,
            'intervals': intervals,
            'ftp': ftp
        }
    
    def _create_vo2max_workout(self, duration: int, ftp: int) -> Dict:
        """Crée une séance VO2max"""
        # 5x3min VO2max classique
        intervals = [
            {'duration': 15, 'zone': 'Z1', 'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55), 'cadence': 85, 'description': 'Échauffement'},
            {'duration': 10, 'zone': 'Z2', 'power_min': int(ftp * 0.56), 'power_max': int(ftp * 0.75), 'cadence': 90, 'description': 'Préparation'},
        ]
        
        # Ajouter les intervalles VO2max
        num_intervals = min(5, (duration - 40) // 6)  # 3min effort + 3min récup
        for i in range(num_intervals):
            intervals.append({
                'duration': 3, 'zone': 'Z5', 
                'power_min': int(ftp * 1.06), 'power_max': int(ftp * 1.20), 
                'cadence': 100, 'description': f'VO2max interval {i+1}/{num_intervals}'
            })
            if i < num_intervals - 1:  # Pas de récup après le dernier
                intervals.append({
                    'duration': 3, 'zone': 'Z2',
                    'power_min': int(ftp * 0.56), 'power_max': int(ftp * 0.75),
                    'cadence': 85, 'description': 'Récupération'
                })
        
        intervals.append({
            'duration': 15, 'zone': 'Z1',
            'power_min': int(ftp * 0.0), 'power_max': int(ftp * 0.55),
            'cadence': 80, 'description': 'Retour au calme'
        })
        
        return {
            'name': f'VO2max {num_intervals}x3min',
            'description': 'Séance VO2max pour développer la puissance maximale aérobie',
            'focus': 'vo2max',
            'total_duration': duration,
            'intervals': intervals,
            'ftp': ftp
        }
    
    def _create_recovery_workout(self, duration: int, ftp: int) -> Dict:
        """Crée une séance de récupération"""
        intervals = [
            {
                'duration': duration,
                'zone': 'Z1',
                'power_min': int(ftp * 0.0),
                'power_max': int(ftp * 0.55),
                'cadence': 85,
                'description': 'Récupération active - pédalage fluide'
            }
        ]
        
        return {
            'name': f'Recovery {duration}min',
            'description': 'Séance de récupération active pour favoriser la régénération',
            'focus': 'recovery',
            'total_duration': duration,
            'intervals': intervals,
            'ftp': ftp
        }
    
    def _generate_files(self, workout: Dict) -> Dict[str, str]:
        """Génère les fichiers ZWO et JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = workout['name'].replace(' ', '_').replace('×', 'x')
        
        output_dir = Path("output_agent")
        output_dir.mkdir(exist_ok=True)
        
        files_generated = {}
        
        # Génération ZWO
        try:
            zwo_file = output_dir / f"{safe_name}_{timestamp}.zwo"
            self._generate_zwo_file(workout, str(zwo_file))
            files_generated['ZWO (MyWhoosh)'] = str(zwo_file)
        except Exception as e:
            print(f"Erreur génération ZWO: {e}")
        
        # Génération JSON
        try:
            json_file = output_dir / f"{safe_name}_{timestamp}.json"
            self._generate_json_file(workout, str(json_file))
            files_generated['JSON (TrainingPeaks)'] = str(json_file)
        except Exception as e:
            print(f"Erreur génération JSON: {e}")
        
        return files_generated
    
    def _generate_zwo_file(self, workout: Dict, filename: str):
        """Génère fichier ZWO"""
        root = ET.Element("workout_file")
        
        # Métadonnées
        author = ET.SubElement(root, "author")
        author.text = "Cycling AI Coach"
        
        name = ET.SubElement(root, "name")
        name.text = workout['name']
        
        description = ET.SubElement(root, "description")
        description.text = workout['description']
        
        # Tags
        tags = ET.SubElement(root, "tags")
        tag = ET.SubElement(tags, "tag")
        tag.set("name", workout['focus'])
        
        # Workout
        workout_elem = ET.SubElement(root, "workout")
        
        for interval in workout['intervals']:
            if interval['zone'] == 'Z1':
                if 'chauffement' in interval['description'].lower():
                    step = ET.SubElement(workout_elem, "Warmup")
                else:
                    step = ET.SubElement(workout_elem, "Cooldown")
            else:
                step = ET.SubElement(workout_elem, "SteadyState")
            
            step.set("Duration", str(interval['duration'] * 60))
            step.set("PowerLow", f"{interval['power_min'] / workout['ftp']:.3f}")
            step.set("PowerHigh", f"{interval['power_max'] / workout['ftp']:.3f}")
            step.set("Cadence", str(interval['cadence']))
        
        # Sauvegarde avec indentation
        def indent_xml(elem, level=0):
            i = "\n" + level * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for child in elem:
                    indent_xml(child, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        
        indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
    
    def _generate_json_file(self, workout: Dict, filename: str):
        """Génère fichier JSON pour TrainingPeaks"""
        tp_workout = {
            "name": workout['name'],
            "description": workout['description'],
            "sport": "Bike",
            "totalTime": workout['total_duration'] * 60,
            "created": datetime.now().isoformat(),
            "intervals": []
        }
        
        for i, interval in enumerate(workout['intervals']):
            tp_interval = {
                "step": i + 1,
                "duration": interval['duration'] * 60,
                "powerZone": interval['zone'],
                "powerMin": interval['power_min'],
                "powerMax": interval['power_max'],
                "powerTarget": (interval['power_min'] + interval['power_max']) / 2,
                "cadence": interval['cadence'],
                "description": interval['description']
            }
            tp_workout['intervals'].append(tp_interval)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tp_workout, f, indent=2, ensure_ascii=False)

class UserProfileTool(BaseTool):
    """Outil de gestion du profil utilisateur"""
    name = "manage_user_profile"
    description = "Gère le profil utilisateur. Actions: read (lire), update_ftp (mettre à jour FTP), update_name (nom)"
    
    def _run(self, action: str, value: str = "") -> str:
        """Actions simplifiées: 'read', 'update_ftp', 'update_name'"""
        try:
            # Définir le chemin du fichier à chaque utilisation
            profile_file = Path("user_profiles") / "current_user.json"
            profile_file.parent.mkdir(exist_ok=True)
            
            if action == "read":
                return self._read_profile(profile_file)
            elif action == "update_ftp":
                return self._update_ftp(profile_file, value)
            elif action == "update_name":
                return self._update_name(profile_file, value)
            else:
                return f"Action '{action}' non reconnue. Utilisez: read, update_ftp, update_name"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _read_profile(self, profile_file: Path) -> str:
        """Lit le profil utilisateur existant"""
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                return f"Profil: {profile_data.get('name', 'Cycliste')} - FTP: {profile_data.get('ftp', 250)}W"
            except:
                pass
        
        # Créer profil par défaut
        default_profile = {
            "name": "Cycliste",
            "ftp": 320,  # Utiliser la valeur mentionnée
            "age": 30,
            "weight": 70
        }
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(default_profile, f, indent=2)
        
        return f"Profil créé: {default_profile['name']} - FTP: {default_profile['ftp']}W"
    
    def _update_ftp(self, profile_file: Path, ftp_value: str) -> str:
        """Met à jour le FTP"""
        try:
            ftp = int(ftp_value)
            if not 100 <= ftp <= 600:
                return "FTP doit être entre 100 et 600W"
            
            # Lire profil existant ou créer nouveau
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
            else:
                profile = {"name": "Cycliste", "age": 30, "weight": 70}
            
            profile['ftp'] = ftp
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            
            return f"✅ FTP mis à jour: {ftp}W"
            
        except ValueError:
            return "Erreur: FTP doit être un nombre entier"
    
    def _update_name(self, profile_file: Path, name: str) -> str:
        """Met à jour le nom"""
        if not name.strip():
            return "Erreur: nom ne peut pas être vide"
        
        # Lire profil existant ou créer nouveau
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
        else:
            profile = {"ftp": 250, "age": 30, "weight": 70}
        
        profile['name'] = name.strip()
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)
        
        return f"✅ Nom mis à jour: {name}"

# === AGENT PRINCIPAL ===

class CyclingAIAgent:
    """Agent de coaching cycliste conversationnel"""
    
    def __init__(self, openai_api_key: str = None):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain requis. Installez avec: pip install langchain langchain-openai")
        
        # Configuration
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API OpenAI requise. Définissez OPENAI_API_KEY ou passez-la en paramètre")
        
        # Initialisation LLM avec gestion d'erreur
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",  # Utiliser 3.5-turbo plus stable
                temperature=0.1,
                api_key=self.api_key,
                max_tokens=1000
            )
        except Exception as e:
            raise ValueError(f"Erreur initialisation LLM: {e}")
        
        # Mémoire conversationnelle simplifiée
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # Réduire à 5 pour éviter les problèmes
        )
        
        # Outils
        self.tools = [
            WorkoutGeneratorTool(),
            UserProfileTool()
        ]
        
        # Prompt système
        self.system_prompt = self._create_system_prompt()
        
        # Configuration agent avec gestion d'erreur
        try:
            self.agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.system_prompt
            )
            
            # Executor avec verbose=False pour éviter les erreurs de callback
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=self.memory,
                verbose=False,  # Désactiver verbose
                handle_parsing_errors=True,
                max_iterations=3  # Limiter les itérations
            )
        except Exception as e:
            raise ValueError(f"Erreur création agent: {e}")
    
    def _create_system_prompt(self) -> ChatPromptTemplate:
        """Crée le prompt système pour l'agent"""
        system_message = """Tu es un coach cycliste IA expert et bienveillant. 

EXPERTISE :
- Spécialiste en entraînement cycliste basé sur la science récente
- Connaissance approfondie de la périodisation, zones de puissance, TSS
- Maîtrise des protocoles d'entraînement (endurance, seuil, VO2max)

ZONES DE PUISSANCE (% FTP):
- Z1 (Récupération): 0-55% FTP
- Z2 (Endurance): 56-75% FTP  
- Z3 (Tempo): 76-90% FTP
- Z4 (Seuil): 91-105% FTP
- Z5 (VO2max): 106-120% FTP

PERSONNALITÉ :
- Bienveillant et encourageant, jamais condescendant
- Explique toujours le "pourquoi" derrière les recommandations
- S'adapte au niveau de l'utilisateur (débutant à expert)

INSTRUCTIONS :
- Si l'utilisateur est nouveau, demande ses informations de base (FTP, objectifs, temps disponible)
- Si il demande une séance, utilise l'outil generate_workout avec les paramètres appropriés
- Si il mentionne son FTP, utilise l'outil manage_user_profile pour le sauvegarder
- Sois conversationnel et naturel, pas robotique !
- Utilise les outils disponibles pour générer les fichiers d'entraînement

Réponds de manière conversationnelle et humaine."""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def chat(self, message: str) -> str:
        """Interface de chat principal"""
        try:
            # Utiliser invoke au lieu de run pour la nouvelle version de LangChain
            response = self.agent_executor.invoke(
                {"input": message},
                return_only_outputs=True
            )
            return response.get("output", "Désolé, je n'ai pas pu traiter votre demande.")
        except Exception as e:
            return f"Désolé, j'ai rencontré une erreur : {str(e)}"
    
    def reset_conversation(self):
        """Remet à zéro la conversation"""
        self.memory.clear()

# === INTERFACE SIMPLE ===

def main():
    """Interface de test simple"""
    print("🚴 CYCLING AI AGENT - Coach Conversationnel")
    print("=" * 50)
    print("Tapez 'quit' pour quitter, 'reset' pour nouvelle conversation")
    print()
    
    # Charger le .env explicitement
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Fichier .env chargé")
    except ImportError:
        print("⚠️ python-dotenv non installé, tentative lecture manuelle...")
    
    # Vérification clé API
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Si pas trouvée, essayer de lire le .env manuellement
    if not api_key and Path(".env").exists():
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY"):
                        api_key = line.split("=")[1].strip().strip("'\"")
                        print("✅ Clé API chargée depuis .env manuellement")
                        break
        except Exception as e:
            print(f"❌ Erreur lecture .env: {e}")
    
    if not api_key:
        print("⚠️ Clé API OpenAI non trouvée !")
        print("Définissez la variable d'environnement OPENAI_API_KEY")
        print("Ou modifiez le code pour la passer directement")
        
        # SOLUTION TEMPORAIRE : Décommentez et mettez votre clé ici (REMPLACEZ par votre vraie clé)
        # api_key = "sk-proj-VOTRE-CLE-ICI"  # <-- Décommentez et mettez votre vraie clé
        
        if not api_key:
            return
    
    try:
        # Initialisation agent
        agent = CyclingAIAgent(api_key)
        print("✅ Agent initialisé avec succès !")
        print()
        
        # Boucle conversationnelle
        while True:
            user_input = input("👤 Vous: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Au revoir ! Bon entraînement !")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                print("🔄 Conversation remise à zéro")
                continue
            elif not user_input:
                continue
            
            print("\n🤖 Coach IA: ", end="")
            response = agent.chat(user_input)
            print(response)
            print()
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if "langchain" in str(e).lower():
            print("💡 Installez LangChain : pip install langchain langchain-openai")

if __name__ == "__main__":
    main()