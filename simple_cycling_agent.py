#!/usr/bin/env python3
"""
Version simplifiée et garantie de fonctionner
Sans RAG complexe, focus sur la génération de séances
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple
from pathlib import Path

# Configuration simple
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base de connaissances simple
ZONES = {
    'Z1': {'min': 0.45, 'max': 0.55, 'name': 'Récupération Active'},
    'Z2': {'min': 0.56, 'max': 0.75, 'name': 'Endurance Aérobie'},
    'Z3': {'min': 0.76, 'max': 0.90, 'name': 'Tempo'},
    'Z4': {'min': 0.91, 'max': 1.05, 'name': 'Seuil Lactique'},
    'Z5': {'min': 1.06, 'max': 1.20, 'name': 'VO2max'},
}

@dataclass
class SimpleWorkout:
    """Structure simple de séance"""
    name: str
    description: str
    intervals: List[Dict]
    total_duration: int
    ftp: int
    tss: float

class SimpleCyclingCoach:
    """Coach cycliste simplifié mais fonctionnel"""
    
    def __init__(self, ftp: int = 320):
        self.ftp = ftp
        self.output_dir = Path("output_simple")
        self.output_dir.mkdir(exist_ok=True)
        print(f"✅ Coach simplifié initialisé - FTP: {ftp}W")
    
    def create_vo2max_workout(self, duration: int = 75, num_intervals: int = 4) -> SimpleWorkout:
        """Crée une séance VO2max optimisée"""
        intervals = [
            # Échauffement
            {
                'duration': 15, 'zone': 'Z1', 
                'power_min': int(self.ftp * 0.50), 'power_max': int(self.ftp * 0.60),
                'cadence': 85, 'description': 'Échauffement progressif'
            },
            # Préparation
            {
                'duration': 10, 'zone': 'Z2',
                'power_min': int(self.ftp * 0.65), 'power_max': int(self.ftp * 0.75),
                'cadence': 90, 'description': 'Préparation aérobie'
            }
        ]
        
        # Intervalles VO2max
        for i in range(num_intervals):
            # Work
            intervals.append({
                'duration': 3, 'zone': 'Z5',
                'power_min': int(self.ftp * 1.06), 'power_max': int(self.ftp * 1.20),
                'cadence': 100, 'description': f'VO2max interval {i+1}/{num_intervals}'
            })
            # Rest (sauf dernier)
            if i < num_intervals - 1:
                intervals.append({
                    'duration': 3, 'zone': 'Z2',
                    'power_min': int(self.ftp * 0.60), 'power_max': int(self.ftp * 0.70),
                    'cadence': 85, 'description': 'Récupération active'
                })
        
        # Retour au calme
        intervals.append({
            'duration': 15, 'zone': 'Z1',
            'power_min': int(self.ftp * 0.45), 'power_max': int(self.ftp * 0.55),
            'cadence': 80, 'description': 'Retour au calme'
        })
        
        # Calculer TSS
        total_tss = sum([
            (interval['duration'] / 60) * ((interval['power_min'] + interval['power_max']) / 2 / self.ftp) ** 2 * 100
            for interval in intervals
        ])
        
        return SimpleWorkout(
            name=f"VO2max {num_intervals}x3min",
            description=f"Séance VO2max avec {num_intervals} intervalles de 3 minutes",
            intervals=intervals,
            total_duration=sum(interval['duration'] for interval in intervals),
            ftp=self.ftp,
            tss=total_tss
        )
    
    def create_threshold_workout(self, duration: int = 80) -> SimpleWorkout:
        """Crée une séance seuil 2x20min"""
        intervals = [
            # Échauffement
            {'duration': 15, 'zone': 'Z1', 'power_min': int(self.ftp * 0.50), 'power_max': int(self.ftp * 0.60), 'cadence': 85, 'description': 'Échauffement'},
            # Préparation
            {'duration': 10, 'zone': 'Z2', 'power_min': int(self.ftp * 0.65), 'power_max': int(self.ftp * 0.75), 'cadence': 90, 'description': 'Préparation'},
            # Bloc 1
            {'duration': 20, 'zone': 'Z4', 'power_min': int(self.ftp * 0.95), 'power_max': int(self.ftp * 1.05), 'cadence': 95, 'description': 'Bloc seuil 1/2'},
            # Récupération
            {'duration': 5, 'zone': 'Z2', 'power_min': int(self.ftp * 0.60), 'power_max': int(self.ftp * 0.70), 'cadence': 85, 'description': 'Récupération'},
            # Bloc 2
            {'duration': 20, 'zone': 'Z4', 'power_min': int(self.ftp * 0.95), 'power_max': int(self.ftp * 1.05), 'cadence': 95, 'description': 'Bloc seuil 2/2'},
            # Retour au calme
            {'duration': 10, 'zone': 'Z1', 'power_min': int(self.ftp * 0.45), 'power_max': int(self.ftp * 0.55), 'cadence': 80, 'description': 'Retour au calme'}
        ]
        
        total_tss = sum([
            (interval['duration'] / 60) * ((interval['power_min'] + interval['power_max']) / 2 / self.ftp) ** 2 * 100
            for interval in intervals
        ])
        
        return SimpleWorkout(
            name="Threshold 2x20min",
            description="Séance de seuil lactique classique 2x20 minutes",
            intervals=intervals,
            total_duration=sum(interval['duration'] for interval in intervals),
            ftp=self.ftp,
            tss=total_tss
        )
    
    def create_endurance_workout(self, duration: int = 90) -> SimpleWorkout:
        """Crée une séance endurance"""
        warmup = 15
        cooldown = 15
        main = duration - warmup - cooldown
        
        intervals = [
            {'duration': warmup, 'zone': 'Z1', 'power_min': int(self.ftp * 0.50), 'power_max': int(self.ftp * 0.60), 'cadence': 85, 'description': 'Échauffement'},
            {'duration': main, 'zone': 'Z2', 'power_min': int(self.ftp * 0.65), 'power_max': int(self.ftp * 0.75), 'cadence': 90, 'description': 'Endurance stable'},
            {'duration': cooldown, 'zone': 'Z1', 'power_min': int(self.ftp * 0.45), 'power_max': int(self.ftp * 0.55), 'cadence': 85, 'description': 'Retour au calme'}
        ]
        
        total_tss = sum([
            (interval['duration'] / 60) * ((interval['power_min'] + interval['power_max']) / 2 / self.ftp) ** 2 * 100
            for interval in intervals
        ])
        
        return SimpleWorkout(
            name=f"Endurance {duration}min",
            description=f"Séance d'endurance aérobie de {duration} minutes",
            intervals=intervals,
            total_duration=duration,
            ftp=self.ftp,
            tss=total_tss
        )
    
    def generate_files(self, workout: SimpleWorkout) -> Dict[str, str]:
        """Génère les fichiers ZWO et JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = workout.name.replace(' ', '_').replace('×', 'x')
        
        files = {}
        
        # ZWO
        zwo_file = self.output_dir / f"{safe_name}_{timestamp}.zwo"
        self._generate_zwo(workout, str(zwo_file))
        files['ZWO'] = str(zwo_file)
        
        # JSON
        json_file = self.output_dir / f"{safe_name}_{timestamp}.json"
        self._generate_json(workout, str(json_file))
        files['JSON'] = str(json_file)
        
        return files
    
    def _generate_zwo(self, workout: SimpleWorkout, filename: str):
        """Génère fichier ZWO"""
        root = ET.Element("workout_file")
        
        author = ET.SubElement(root, "author")
        author.text = "Simple Cycling Coach"
        
        name = ET.SubElement(root, "name")
        name.text = workout.name
        
        description = ET.SubElement(root, "description")
        description.text = workout.description
        
        tags = ET.SubElement(root, "tags")
        tag = ET.SubElement(tags, "tag")
        tag.set("name", "scientifique")
        
        workout_elem = ET.SubElement(root, "workout")
        
        for interval in workout.intervals:
            if interval['zone'] == 'Z1' and 'chauffement' in interval['description'].lower():
                step = ET.SubElement(workout_elem, "Warmup")
            elif interval['zone'] == 'Z1' and 'retour' in interval['description'].lower():
                step = ET.SubElement(workout_elem, "Cooldown")
            else:
                step = ET.SubElement(workout_elem, "SteadyState")
            
            step.set("Duration", str(interval['duration'] * 60))
            step.set("PowerLow", f"{interval['power_min'] / self.ftp:.3f}")
            step.set("PowerHigh", f"{interval['power_max'] / self.ftp:.3f}")
            step.set("Cadence", str(interval['cadence']))
        
        # Indentation
        self._indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
    
    def _generate_json(self, workout: SimpleWorkout, filename: str):
        """Génère fichier JSON"""
        data = {
            "name": workout.name,
            "description": workout.description,
            "sport": "Bike",
            "totalTime": workout.total_duration * 60,
            "estimatedTSS": round(workout.tss, 1),
            "ftp": workout.ftp,
            "created": datetime.now().isoformat(),
            "intervals": []
        }
        
        for i, interval in enumerate(workout.intervals):
            data["intervals"].append({
                "step": i + 1,
                "duration": interval['duration'] * 60,
                "zone": interval['zone'],
                "powerMin": interval['power_min'],
                "powerMax": interval['power_max'],
                "powerTarget": (interval['power_min'] + interval['power_max']) // 2,
                "cadence": interval['cadence'],
                "description": interval['description']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _indent_xml(self, elem, level=0):
        """Indentation XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def interactive_session(self):
        """Session interactive simple"""
        print("\n🚴 Session Interactive - Coach Cycliste Simplifié")
        print("=" * 50)
        
        while True:
            print("\nOptions disponibles :")
            print("1. Séance VO2max (75min)")
            print("2. Séance Threshold (80min)")
            print("3. Séance Endurance (90min)")
            print("4. Séance personnalisée")
            print("5. Modifier FTP")
            print("6. Quitter")
            
            choice = input("\nVotre choix (1-6) : ").strip()
            
            if choice == '1':
                workout = self.create_vo2max_workout()
                files = self.generate_files(workout)
                print(f"✅ {workout.name} créée - TSS: {workout.tss:.0f}")
                print(f"📁 Fichiers: {', '.join(files.values())}")
                
            elif choice == '2':
                workout = self.create_threshold_workout()
                files = self.generate_files(workout)
                print(f"✅ {workout.name} créée - TSS: {workout.tss:.0f}")
                print(f"📁 Fichiers: {', '.join(files.values())}")
                
            elif choice == '3':
                workout = self.create_endurance_workout()
                files = self.generate_files(workout)
                print(f"✅ {workout.name} créée - TSS: {workout.tss:.0f}")
                print(f"📁 Fichiers: {', '.join(files.values())}")
                
            elif choice == '4':
                try:
                    workout_type = input("Type (vo2max/threshold/endurance) : ").strip().lower()
                    duration = int(input("Durée en minutes : ").strip())
                    
                    if workout_type == 'vo2max':
                        workout = self.create_vo2max_workout(duration)
                    elif workout_type == 'threshold':
                        workout = self.create_threshold_workout(duration)
                    else:
                        workout = self.create_endurance_workout(duration)
                    
                    files = self.generate_files(workout)
                    print(f"✅ {workout.name} créée - TSS: {workout.tss:.0f}")
                    print(f"📁 Fichiers: {', '.join(files.values())}")
                    
                except ValueError:
                    print("❌ Erreur : durée doit être un nombre")
                    
            elif choice == '5':
                try:
                    new_ftp = int(input(f"Nouveau FTP (actuel: {self.ftp}W) : ").strip())
                    if 100 <= new_ftp <= 600:
                        self.ftp = new_ftp
                        print(f"✅ FTP mis à jour : {new_ftp}W")
                    else:
                        print("❌ FTP doit être entre 100 et 600W")
                except ValueError:
                    print("❌ Erreur : FTP doit être un nombre")
                    
            elif choice == '6':
                print("👋 Au revoir ! Bon entraînement !")
                break
            else:
                print("❌ Choix invalide")

def main():
    """Interface principale simplifiée"""
    print("🚴 CYCLING COACH - Version Simplifiée et Robuste")
    print("=" * 55)
    
    # FTP par défaut
    default_ftp = 320
    try:
        ftp_input = input(f"Votre FTP en watts (défaut: {default_ftp}W) : ").strip()
        ftp = int(ftp_input) if ftp_input else default_ftp
        if not 100 <= ftp <= 600:
            print("⚠️ FTP hors limites, utilisation de la valeur par défaut")
            ftp = default_ftp
    except ValueError:
        print("⚠️ Valeur invalide, utilisation de la valeur par défaut")
        ftp = default_ftp
    
    # Initialiser le coach
    coach = SimpleCyclingCoach(ftp)
    
    # Session interactive
    coach.interactive_session()

if __name__ == "__main__":
    main()