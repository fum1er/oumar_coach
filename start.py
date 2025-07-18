#!/usr/bin/env python3
"""
Cycling AI Coach - Démarrage Simple
Point d'entrée principal du coach cycliste IA
"""

import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Point d'entrée principal"""
    print("🚴 Cycling AI Coach - Démarrage")
    print("=" * 40)
    
    try:
        # Import de l'agent principal
        from cycling_ai_agent_corrected import main as agent_main
        
        # Lancer l'agent
        agent_main()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Assurez-vous que tous les fichiers sont présents")
        
        # Mode ultra-simplifié de démarrage
        print("\n🔧 Tentative de mode simplifié...")
        try:
            from simple_cycling_agent import main as simple_main
            simple_main()
        except ImportError:
            print("❌ Mode simplifié non disponible")
            print("Vérifiez l'installation des modules")
    
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()