#!/usr/bin/env python3
"""
Test final après correction complète des imports
"""

def test_complete_system():
    """Test du système complet"""
    print("🧪 TEST SYSTÈME COMPLET")
    print("=" * 40)
    
    try:
        # Test 1: KnowledgeBaseManager
        print("1. Test KnowledgeBaseManager...")
        from core.knowledge_base import KnowledgeBaseManager
        kb = KnowledgeBaseManager()
        result = kb.search_knowledge("zone 4")
        print("✅ KnowledgeBaseManager: OK")
        
        # Test 2: WorkoutBuilder (le problématique)
        print("2. Test WorkoutBuilder...")
        from generators.workout_builder import WorkoutBuilder
        builder = WorkoutBuilder()
        print("✅ WorkoutBuilder importé: OK")
        
        # Test 3: Génération de séance
        print("3. Test génération séance...")
        workout = builder.create_smart_workout("vo2max", 75, "intermediate", 320)
        print(f"✅ Séance générée: {workout.name}")
        
        # Test 4: Calculs
        print("4. Test calculs...")
        from core.calculations import TrainingCalculations
        calc = TrainingCalculations()
        tss = calc.calculate_tss(workout.segments, workout.repeated_intervals, 320)
        print(f"✅ TSS calculé: {tss:.0f}")
        
        # Test 5: Génération de fichiers
        print("5. Test génération fichiers...")
        from generators.file_generators import FileGenerator
        file_gen = FileGenerator()
        files = file_gen.generate_all_formats(workout)
        print(f"✅ Fichiers générés: {len(files)}")
        
        # Test 6: Outils LangChain
        print("6. Test outils...")
        from tools.knowledge_tool import create_knowledge_tool
        from tools.workout_tool import create_workout_tool
        
        knowledge_tool = create_knowledge_tool()
        workout_tool = create_workout_tool()
        print("✅ Outils créés: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_startup():
    """Test démarrage de l'agent"""
    print("\n🤖 TEST DÉMARRAGE AGENT")
    print("=" * 40)
    
    try:
        # Import de l'agent principal
        from cycling_ai_agent_corrected import CyclingAIAgent, check_dependencies
        
        # Vérifier les dépendances
        deps = check_dependencies()
        print("Dépendances:")
        for name, status in deps.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}")
        
        # Test création agent (mode dégradé si pas de clé)
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            print("Tentative création agent complet...")
            agent = CyclingAIAgent()
            print("✅ Agent créé avec succès")
        else:
            print("⚠️ Pas de clé OpenAI, test mode dégradé")
            # Test sans initialisation complète
            print("✅ Structure agent OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal"""
    print("🚀 TEST FINAL - SYSTÈME CYCLISTE IA")
    print("=" * 50)
    
    # Test 1: Système de base
    system_ok = test_complete_system()
    
    # Test 2: Agent
    agent_ok = test_agent_startup()
    
    # Résultat final
    print("\n" + "=" * 50)
    if system_ok and agent_ok:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("Vous pouvez maintenant lancer:")
        print("  python start.py")
        print("\nCommandes de test:")
        print("  'Crée une séance VO2max de 75 minutes'")
        print("  'Explique la zone 4'")
        print("  'help'")
    else:
        print("⚠️ Certains tests échouent")
        if not system_ok:
            print("❌ Problème système de base")
        if not agent_ok:
            print("❌ Problème agent")

if __name__ == "__main__":
    main()