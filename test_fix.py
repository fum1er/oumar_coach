#!/usr/bin/env python3
"""
Test après correction des erreurs de syntaxe
"""

import sys
from pathlib import Path

def test_syntax(file_path):
    """Test la syntaxe d'un fichier Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, file_path, 'exec')
        return True, "OK"
    except SyntaxError as e:
        return False, f"Ligne {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def test_imports():
    """Test les imports principaux"""
    print("🔍 Test des imports...")
    
    modules = [
        ("core.knowledge_base", "KnowledgeBaseManager"),
        ("core.models", "UserProfile"),
        ("core.calculations", "TrainingCalculations"),
        ("tools.knowledge_tool", "create_knowledge_tool"),
        ("generators.workout_builder", "WorkoutBuilder"),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")

def test_basic_functionality():
    """Test les fonctionnalités de base"""
    print("\n🧪 Test des fonctionnalités de base...")
    
    try:
        # Test 1: KnowledgeBaseManager
        from core.knowledge_base import KnowledgeBaseManager
        kb = KnowledgeBaseManager()
        result = kb.search_knowledge("zone 4")
        print("✅ KnowledgeBaseManager fonctionne")
        
        # Test 2: WorkoutBuilder
        from generators.workout_builder import WorkoutBuilder
        builder = WorkoutBuilder()
        workout = builder.create_smart_workout("vo2max", 75, "intermediate", 320)
        print(f"✅ WorkoutBuilder fonctionne - {workout.name}")
        
        # Test 3: Knowledge Tool
        from tools.knowledge_tool import create_knowledge_tool
        tool = create_knowledge_tool()
        print("✅ Knowledge Tool créé")
        
        # Test 4: File Generator
        from generators.file_generators import FileGenerator
        file_gen = FileGenerator()
        print("✅ FileGenerator initialisé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur fonctionnalité: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 TEST APRÈS CORRECTION")
    print("=" * 40)
    
    # Test 1: Syntaxe des fichiers principaux
    print("1. Test de syntaxe...")
    files_to_check = [
        "tools/knowledge_tool.py",
        "core/knowledge_base.py",
        "core/models.py",
        "generators/workout_builder.py",
    ]
    
    syntax_ok = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            ok, msg = test_syntax(file_path)
            status = "✅" if ok else "❌"
            print(f"  {status} {file_path}: {msg}")
            if not ok:
                syntax_ok = False
        else:
            print(f"  🚫 {file_path}: Fichier manquant")
            syntax_ok = False
    
    if not syntax_ok:
        print("\n❌ Erreurs de syntaxe détectées. Corrigez avant de continuer.")
        return
    
    # Test 2: Imports
    test_imports()
    
    # Test 3: Fonctionnalités
    if test_basic_functionality():
        print("\n🎉 TOUS LES TESTS PASSENT !")
        print("Vous pouvez maintenant lancer:")
        print("  python start.py")
    else:
        print("\n⚠️ Certains tests échouent. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
