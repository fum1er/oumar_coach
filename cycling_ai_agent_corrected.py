#!/usr/bin/env python3
"""
Cycling AI Agent - Version Corrigée et Modulaire
Agent de coaching cycliste avec architecture modulaire
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
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

# === IMPORTS MODULAIRES ===

try:
    # Core modules
    from core.models import UserProfile, WorkoutRequest
    from core.knowledge_base import KnowledgeBaseManager
    from core.calculations import TrainingCalculations
    
    # Tools
    from tools.knowledge_tool import create_knowledge_tool
    from tools.workout_tool import create_workout_tool
    
    # Generators
    from generators.workout_builder import WorkoutBuilder
    from generators.file_generators import FileGenerator
    
    MODULES_LOADED = True
    print("✅ Modules cycliste chargés")
    
except ImportError as e:
    print(f"❌ Erreur import modules: {e}")
    print("💡 Assurez-vous que tous les fichiers sont présents dans les bons dossiers")
    MODULES_LOADED = False

# === AGENT PRINCIPAL CORRIGÉ ===

class CyclingAIAgent:
    """Agent de coaching cycliste modulaire et robuste"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialise l'agent avec gestion d'erreurs robuste"""
        
        # Vérifier les prérequis
        if not MODULES_LOADED:
            raise ImportError("Modules cycliste non disponibles")
        
        # Configuration API
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API OpenAI requise. Définissez OPENAI_API_KEY ou passez-la en paramètre")
        
        # Initialiser les composants de base
        self._init_core_components()
        
        # Initialiser LangChain si disponible
        if LANGCHAIN_AVAILABLE:
            self._init_langchain_components()
        else:
            print("⚠️ Mode dégradé: LangChain non disponible")
            self.agent_executor = None
    
    def _init_core_components(self):
        """Initialise les composants de base (toujours disponibles)"""
        try:
            self.knowledge_manager = KnowledgeBaseManager()
            self.calculator = TrainingCalculations()
            self.workout_builder = WorkoutBuilder()
            self.file_generator = FileGenerator()
            print("✅ Composants de base initialisés")
        except Exception as e:
            raise RuntimeError(f"Erreur initialisation composants: {e}")
    
    def _init_langchain_components(self):
        """Initialise les composants LangChain (optionnel)"""
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
            
            # Outils (avec fallback)
            self.tools = []
            try:
                knowledge_tool = create_knowledge_tool()
                workout_tool = create_workout_tool()
                self.tools = [knowledge_tool, workout_tool]
                print("✅ Outils LangChain créés")
            except Exception as e:
                print(f"⚠️ Erreur création outils: {e}")
                self.tools = []
            
            # Prompt système
            self.system_prompt = self._create_system_prompt()
            
            # Agent (si outils disponibles)
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

            # Outils (avec le nouveau)
            self.tools = []
            try:
                knowledge_tool = create_knowledge_tool()
                workout_tool = create_workout_tool()
                periodization_tool = create_periodization_tool()  # ⭐ NOUVEAU
                
                self.tools = [knowledge_tool, workout_tool, periodization_tool]
                print("✅ Outils LangChain créés (avec périodisation)")
            except Exception as e:
                print(f"⚠️ Erreur création outils: {e}")
                print("✅ Agent LangChain initialisé")
            else:
                self.agent_executor = None
                print("⚠️ Agent non créé (pas d'outils)")
                
        except Exception as e:
            print(f"⚠️ Erreur LangChain: {e}")
            self.agent_executor = None
    
    def _create_system_prompt(self) -> ChatPromptTemplate:
        """Crée le prompt système optimisé"""
        system_message = """Tu es un COACH CYCLISTE IA D'ÉLITE avec une expertise scientifique approfondie.

⚡ PÉRIODISATION AVANCÉE:
- Utilise 'create_periodization_plan' pour créer des plans multi-semaines
- Basé sur les théories de Seiler, Coggan, Friel, Issurin
- Modèles: Polarisé, Pyramidal, Traditionnel, Block
- Personnalisation selon niveau et événements cibles

🗓️ PLANIFICATION:
- Plans de 8-20 semaines
- Progression scientifique des charges
- Périodisation par phases
- Adaptation aux contraintes personnelles 

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
        """Interface de chat avec fallback intelligent"""
        
        if self.agent_executor:
            # Mode complet avec LangChain
            try:
                response = self.agent_executor.invoke(
                    {"input": message},
                    return_only_outputs=True
                )
                return response.get("output", "Désolé, je n'ai pas pu traiter votre demande.")
            except Exception as e:
                print(f"⚠️ Erreur agent: {e}")
                return self._fallback_response(message)
        else:
            # Mode dégradé sans LangChain
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """Réponse de fallback sans LangChain"""
        message_lower = message.lower()
        
        # Détection d'intention simple
        if any(word in message_lower for word in ['séance', 'workout', 'entrainement', 'entraînement']):
            return self._create_simple_workout(message_lower)
        elif any(word in message_lower for word in ['zone', 'puissance', 'ftp']):
            return self._provide_zone_info(message_lower)
        elif any(word in message_lower for word in ['aide', 'help', 'bonjour', 'salut']):
            return self._provide_help()
        else:
            return """🚴 Coach IA: Je peux vous aider avec :
• Génération de séances d'entraînement personnalisées
• Informations sur les zones de puissance
• Conseils d'entraînement cycliste

Essayez: "Crée-moi une séance VO2max de 75 minutes" ou "Explique-moi la zone 4"
            
💡 Pour une expérience complète, installez LangChain avec:
pip install langchain langchain-openai langchain-community"""
    
    def _create_simple_workout(self, message: str) -> str:
        """Création de séance simplifiée sans LangChain"""
        try:
            # Détection type
            if 'vo2max' in message or 'vo2' in message:
                workout_type = 'vo2max'
            elif 'seuil' in message or 'threshold' in message or 'ftp' in message:
                workout_type = 'threshold'
            elif 'endurance' in message:
                workout_type = 'endurance'
            else:
                workout_type = 'vo2max'  # Par défaut
            
            # Détection durée
            import re
            duration_match = re.search(r'(\d+)\s*(?:min|minutes?)', message)
            duration = int(duration_match.group(1)) if duration_match else 75
            
            # Créer la séance
            workout = self.workout_builder.create_smart_workout(
                workout_type=workout_type,
                duration=duration,
                level="intermediate",
                ftp=320
            )
            
            # Calculer métriques
            tss = self.calculator.calculate_tss(
                workout.segments, 
                workout.repeated_intervals, 
                workout.ftp
            )
            workout.estimated_tss = tss
            
            # Générer fichiers
            files = self.file_generator.generate_all_formats(workout)
            
            return f"""✅ Séance '{workout.name}' créée !

📊 **Résumé:**
{workout.description}

🎯 **Objectif:**
{workout.scientific_objective}

📈 **Métriques:**
• Durée: {workout.total_duration} minutes
• TSS estimé: {tss:.0f}
• Temps haute intensité: {self.calculator.calculate_high_intensity_time(workout)} minutes

📁 **Fichiers générés:**
{chr(10).join([f"• {k}: {Path(v).name}" for k, v in files.items()])}

💡 **Conseils:**
{workout.coaching_tips}

🔧 **Mode dégradé actif** - Installez LangChain pour plus de fonctionnalités"""
            
        except Exception as e:
            return f"❌ Erreur création séance: {e}"
    
    def _provide_zone_info(self, message: str) -> str:
        """Fournit des informations sur les zones"""
        # Détection zone
        zone_map = {'z1': 'Z1', 'z2': 'Z2', 'z3': 'Z3', 'z4': 'Z4', 'z5': 'Z5'}
        
        for zone_key, zone_id in zone_map.items():
            if zone_key in message:
                zone_info = self.knowledge_manager.get_zone_info(zone_id)
                if zone_info:
                    return f"""🔍 **Zone {zone_id} - {zone_info.name}**

⚡ **Puissance:** {zone_info.power_pct_ftp[0]*100:.0f}-{zone_info.power_pct_ftp[1]*100:.0f}% FTP
💓 **Fréquence cardiaque:** {zone_info.hr_pct_max[0]}-{zone_info.hr_pct_max[1]}% FCmax
🔄 **Cadence:** {zone_info.cadence_rpm[0]}-{zone_info.cadence_rpm[1]} RPM

🎯 **Objectif:**
{zone_info.objective}

⏰ **Durée typique:** {zone_info.duration_typical}

🏃 **Utilisation:** {zone_info.when_use}"""
        
        return self.knowledge_manager.search_knowledge(message)
    
    def _provide_help(self) -> str:
        """Message d'aide"""
        return """🚴 **Cycling AI Coach - Guide d'utilisation**

📋 **Commandes disponibles:**
• `Crée une séance VO2max de 75 minutes`
• `Séance threshold pour intermédiaire`
• `Explique la zone 4`
• `Infos sur le seuil lactique`

🎯 **Types de séances:**
• **VO2max:** Intervalles haute intensité (Z5)
• **Threshold:** Séances au seuil (Z4) 
• **Endurance:** Base aérobie (Z2)
• **Recovery:** Récupération active (Z1)

⚙️ **Paramètres personnalisables:**
• Durée (30-180 minutes)
• Niveau (débutant/intermédiaire/avancé)
• Type d'objectif

💡 **Pour une expérience complète:**
Installez LangChain pour des conversations avancées et personnalisation poussée.

Que souhaitez-vous faire aujourd'hui ? 🚀"""
    
    def reset_conversation(self):
        """Reset de la conversation"""
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
            print("🔄 Conversation remise à zéro")

# === FONCTIONS UTILITAIRES ===

def check_dependencies() -> Dict[str, bool]:
    """Vérifie les dépendances installées"""
    deps = {
        "langchain": LANGCHAIN_AVAILABLE,
        "modules": MODULES_LOADED,
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
    
    if not deps["openai_key"]:
        print("\n💡 **Pour configurer OpenAI:**")
        print("Créez un fichier .env avec: OPENAI_API_KEY=votre_clé_ici")

# === INTERFACE PRINCIPALE ===

def main():
    """Interface principale robuste"""
    print("🚴 CYCLING AI COACH - Version Corrigée et Modulaire")
    print("=" * 65)
    
    # Vérifier les dépendances
    print_dependency_status()
    
    if not MODULES_LOADED:
        print("\n❌ Modules de base manquants. Impossible de continuer.")
        return
    
    # Vérifier clé API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ Clé API OpenAI non trouvée !")
        print("L'agent fonctionnera en mode dégradé (sans IA conversationnelle)")
        print("Pour activer toutes les fonctionnalités, définissez OPENAI_API_KEY")
        
        choice = input("\nContinuer en mode dégradé ? (o/n): ").lower()
        if choice != 'o':
            return
    
    try:
        # Initialiser l'agent
        coach = CyclingAIAgent()
        
        print(f"\n✅ Coach IA initialisé avec succès !")
        
        if coach.agent_executor:
            print("🧠 Mode complet: LangChain + IA conversationnelle")
        else:
            print("⚙️ Mode dégradé: Fonctionnalités de base disponibles")
        
        print("\nTapez 'quit' pour quitter, 'reset' pour nouvelle conversation")
        print("Tapez 'help' pour voir les commandes disponibles")
        print()
        
        # Boucle conversationnelle
        while True:
            user_input = input("👤 Vous: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Au revoir ! Excellents entraînements !")
                break
            elif user_input.lower() == 'reset':
                coach.reset_conversation()
                continue
            elif user_input.lower() in ['help', 'aide']:
                print(coach._provide_help())
                continue
            elif not user_input:
                continue
            
            print(f"\n🤖 Coach IA: ")
            response = coach.chat(user_input)
            print(response)
            print()
    
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        print("💡 Vérifiez que tous les modules sont correctement installés")

if __name__ == "__main__":
    main()