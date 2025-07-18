# test_periodization.py
#!/usr/bin/env python3
"""Test du système de périodisation"""

def test_periodization_system():
    print("🧪 Test du système de périodisation...")
    
    try:
        # Test 1: Import du moteur
        from periodization_system import (
            AdvancedPeriodizationEngine,
            PeriodizationModel,
            create_example_plan
        )
        print("✅ Imports OK")
        
        # Test 2: Création d'un plan d'exemple
        plan, calendar = create_example_plan()
        print(f"✅ Plan créé: {plan.total_weeks} semaines")
        
        # Test 3: Outil LangChain
        from tools.periodization_tool import create_periodization_tool
        tool = create_periodization_tool()
        print("✅ Outil LangChain créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_periodization_system()