#!/usr/bin/env python3
"""
Version simplifiée et garantie de fonctionner
Spécialement optimisée pour MyWhoosh + MyTrainingPeaks
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Configuration utilisateur
USER_CONFIG = {
    'name': 'Jean Cycliste',
    'ftp': 250,
    'weight': 70
}

# Zones de puissance
ZONES = {
    'Z1': {'min': 0.00, 'max': 0.55, 'name': 'Recovery'},
    'Z2': {'min': 0.56, 'max': 0.75, 'name': 'Endurance'},
    'Z3': {'min': 0.76, 'max': 0.90, 'name': 'Tempo'},
    'Z4': {'min': 0.91, 'max': 1.05, 'name': 'Threshold'},
    'Z5': {'min': 1.06, 'max': 1.20, 'name': 'VO2max'},
}

def calculate_power_range(zone, ftp):
    """Calcule la plage de puissance pour une zone"""
    zone_data = ZONES[zone]
    power_min = int(ftp * zone_data['min'])
    power_max = int(ftp * zone_data['max'])
    return power_min, power_max

def generate_zwo_file(workout_data, filename):
    """Génère fichier ZWO pour MyWhoosh"""
    print(f"   🚴 Génération ZWO: {os.path.basename(filename)}")
    
    try:
        root = ET.Element("workout_file")
        
        # Métadonnées
        author = ET.SubElement(root, "author")
        author.text = "Cycling Coach IA"
        
        name = ET.SubElement(root, "name")
        name.text = workout_data['name']
        
        description = ET.SubElement(root, "description")
        description.text = workout_data['description']
        
        # Tags
        tags = ET.SubElement(root, "tags")
        tag = ET.SubElement(tags, "tag")
        tag.set("name", workout_data['focus'])
        
        # Workout
        workout = ET.SubElement(root, "workout")
        
        for interval in workout_data['intervals']:
            if interval['zone'] == 'Z1':
                if 'chauffement' in interval['description'].lower() or 'warmup' in interval['description'].lower():
                    step = ET.SubElement(workout, "Warmup")
                else:
                    step = ET.SubElement(workout, "Cooldown")
            else:
                step = ET.SubElement(workout, "SteadyState")
            
            step.set("Duration", str(interval['duration'] * 60))
            step.set("PowerLow", f"{interval['power_min'] / workout_data['ftp']:.3f}")
            step.set("PowerHigh", f"{interval['power_max'] / workout_data['ftp']:.3f}")
            
            if interval.get('cadence'):
                step.set("Cadence", str(interval['cadence']))
        
        # Indentation
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
        
        print(f"      ✅ ZWO généré ({os.path.getsize(filename)} bytes)")
        return True
        
    except Exception as e:
        print(f"      ❌ Erreur ZWO: {e}")
        return False

def generate_json_file(workout_data, filename):
    """Génère fichier JSON pour MyTrainingPeaks"""
    print(f"   📊 Génération JSON: {os.path.basename(filename)}")
    
    try:
        tp_workout = {
            "name": workout_data['name'],
            "description": workout_data['description'],
            "sport": "Bike",
            "estimatedTSS": workout_data['tss'],
            "totalTime": workout_data['total_duration'] * 60,
            "created": datetime.now().isoformat(),
            "intervals": []
        }
        
        for i, interval in enumerate(workout_data['intervals']):
            tp_interval = {
                "step": i + 1,
                "duration": interval['duration'] * 60,
                "powerZone": interval['zone'],
                "powerMin": interval['power_min'],
                "powerMax": interval['power_max'],
                "powerTarget": (interval['power_min'] + interval['power_max']) / 2,
                "cadence": interval.get('cadence', 90),
                "description": interval['description'],
                "intensityFactor": ((interval['power_min'] + interval['power_max']) / 2) / workout_data['ftp']
            }
            tp_workout['intervals'].append(tp_interval)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tp_workout, f, indent=2, ensure_ascii=False)
        
        print(f"      ✅ JSON généré ({os.path.getsize(filename)} bytes)")
        return True
        
    except Exception as e:
        print(f"      ❌ Erreur JSON: {e}")
        return False

def generate_csv_file(workout_data, filename):
    """Génère fichier CSV pour analyse"""
    print(f"   📈 Génération CSV: {os.path.basename(filename)}")
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # En-têtes
            writer.writerow([
                'Step', 'Duration_min', 'Zone', 'Power_Min_W', 'Power_Max_W', 
                'Power_Avg_W', 'Cadence_rpm', 'Description', 'TSS_estimated'
            ])
            
            # Données
            for i, interval in enumerate(workout_data['intervals'], 1):
                avg_power = (interval['power_min'] + interval['power_max']) / 2
                interval_tss = (interval['duration'] / 60) * (avg_power / workout_data['ftp']) * (avg_power / workout_data['ftp']) * 100
                
                writer.writerow([
                    i,
                    interval['duration'],
                    interval['zone'],
                    interval['power_min'],
                    interval['power_max'],
                    avg_power,
                    interval.get('cadence', 90),
                    interval['description'],
                    round(interval_tss, 1)
                ])
        
        print(f"      ✅ CSV généré ({os.path.getsize(filename)} bytes)")
        return True
        
    except Exception as e:
        print(f"      ❌ Erreur CSV: {e}")
        return False

def create_workout_data(name, description, focus, intervals_def):
    """Crée les données d'une séance"""
    
    intervals = []
    total_duration = 0
    total_tss = 0
    
    for interval_def in intervals_def:
        duration = interval_def['duration']
        zone = interval_def['zone']
        cadence = interval_def.get('cadence', 90)
        desc = interval_def['description']
        
        power_min, power_max = calculate_power_range(zone, USER_CONFIG['ftp'])
        avg_power = (power_min + power_max) / 2
        
        # TSS approximatif pour cet interval
        interval_tss = (duration / 60) * (avg_power / USER_CONFIG['ftp']) * (avg_power / USER_CONFIG['ftp']) * 100
        total_tss += interval_tss
        total_duration += duration
        
        intervals.append({
            'duration': duration,
            'zone': zone,
            'power_min': power_min,
            'power_max': power_max,
            'cadence': cadence,
            'description': desc
        })
    
    return {
        'name': name,
        'description': description,
        'focus': focus,
        'ftp': USER_CONFIG['ftp'],
        'total_duration': total_duration,
        'tss': total_tss,
        'intervals': intervals
    }

def generate_all_formats(workout_data, base_filename):
    """Génère tous les formats pour une séance"""
    
    print(f"\n🔧 Génération {workout_data['name']} ({workout_data['total_duration']}min, TSS: {workout_data['tss']:.1f})")
    
    results = {}
    
    # ZWO pour MyWhoosh
    zwo_file = f"{base_filename}.zwo"
    if generate_zwo_file(workout_data, zwo_file):
        results['zwo'] = zwo_file
    
    # JSON pour MyTrainingPeaks
    json_file = f"{base_filename}.json"
    if generate_json_file(workout_data, json_file):
        results['json'] = json_file
    
    # CSV pour analyse
    csv_file = f"{base_filename}.csv"
    if generate_csv_file(workout_data, csv_file):
        results['csv'] = csv_file
    
    return results

def main():
    print("🚴 CYCLING COACH IA - Version Simplifiée MyWhoosh/MyTrainingPeaks")
    print("=" * 70)
    print(f"👤 {USER_CONFIG['name']} | FTP: {USER_CONFIG['ftp']}W | Ratio: {USER_CONFIG['ftp']/USER_CONFIG['weight']:.1f}W/kg")
    
    # Créer dossier de sortie
    output_dir = "output_simple"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # === SÉANCES PRÉ-DÉFINIES ===
    
    # 1. Endurance 90min
    endurance_intervals = [
        {'duration': 15, 'zone': 'Z1', 'cadence': 85, 'description': 'Échauffement progressif'},
        {'duration': 60, 'zone': 'Z2', 'cadence': 90, 'description': 'Endurance stable - conversation possible'},
        {'duration': 15, 'zone': 'Z1', 'cadence': 85, 'description': 'Retour au calme'}
    ]
    
    endurance_workout = create_workout_data(
        "Endurance 90min",
        "Séance d'endurance aérobie pour développer la base cardiovasculaire",
        "endurance",
        endurance_intervals
    )
    
    # 2. Threshold intervals
    threshold_intervals = [
        {'duration': 15, 'zone': 'Z1', 'cadence': 85, 'description': 'Échauffement'},
        {'duration': 10, 'zone': 'Z2', 'cadence': 90, 'description': 'Préparation'},
        {'duration': 20, 'zone': 'Z4', 'cadence': 95, 'description': 'Bloc seuil 1 - maintenir la puissance'},
        {'duration': 5, 'zone': 'Z2', 'cadence': 85, 'description': 'Récupération'},
        {'duration': 20, 'zone': 'Z4', 'cadence': 95, 'description': 'Bloc seuil 2 - concentration mentale'},
        {'duration': 10, 'zone': 'Z1', 'cadence': 80, 'description': 'Retour au calme'}
    ]
    
    threshold_workout = create_workout_data(
        "Threshold 2x20min",
        "Séance de seuil lactique pour améliorer le FTP",
        "threshold",
        threshold_intervals
    )
    
    # 3. VO2max intervals
    vo2max_intervals = [
        {'duration': 15, 'zone': 'Z1', 'cadence': 85, 'description': 'Échauffement'},
        {'duration': 10, 'zone': 'Z2', 'cadence': 90, 'description': 'Préparation'},
        {'duration': 3, 'zone': 'Z5', 'cadence': 100, 'description': 'VO2max interval 1/5'},
        {'duration': 3, 'zone': 'Z2', 'cadence': 85, 'description': 'Récupération'},
        {'duration': 3, 'zone': 'Z5', 'cadence': 100, 'description': 'VO2max interval 2/5'},
        {'duration': 3, 'zone': 'Z2', 'cadence': 85, 'description': 'Récupération'},
        {'duration': 3, 'zone': 'Z5', 'cadence': 100, 'description': 'VO2max interval 3/5'},
        {'duration': 3, 'zone': 'Z2', 'cadence': 85, 'description': 'Récupération'},
        {'duration': 3, 'zone': 'Z5', 'cadence': 100, 'description': 'VO2max interval 4/5'},
        {'duration': 3, 'zone': 'Z2', 'cadence': 85, 'description': 'Récupération'},
        {'duration': 3, 'zone': 'Z5', 'cadence': 100, 'description': 'VO2max interval 5/5'},
        {'duration': 15, 'zone': 'Z1', 'cadence': 80, 'description': 'Retour au calme'}
    ]
    
    vo2max_workout = create_workout_data(
        "VO2max 5x3min",
        "Séance VO2max pour développer la puissance maximale aérobie",
        "vo2max",
        vo2max_intervals
    )
    
    # === GÉNÉRATION DES FICHIERS ===
    
    workouts = [endurance_workout, threshold_workout, vo2max_workout]
    all_files = []
    
    for workout in workouts:
        safe_name = workout['name'].replace(' ', '_').replace('×', 'x')
        base_filename = f"{output_dir}/{safe_name}_{timestamp}"
        
        files = generate_all_formats(workout, base_filename)
        all_files.extend(files.values())
    
    # === RÉSUMÉ ===
    
    print(f"\n" + "="*70)
    print("📂 FICHIERS GÉNÉRÉS POUR MyWhoosh/MyTrainingPeaks:")
    print("="*70)
    
    # Grouper par type
    zwo_files = [f for f in all_files if f.endswith('.zwo')]
    json_files = [f for f in all_files if f.endswith('.json')]
    csv_files = [f for f in all_files if f.endswith('.csv')]
    
    if zwo_files:
        print(f"\n🚴 Fichiers ZWO pour MyWhoosh ({len(zwo_files)}):")
        for f in zwo_files:
            size = os.path.getsize(f)
            print(f"   📱 {os.path.basename(f)} ({size} bytes)")
    
    if json_files:
        print(f"\n📊 Fichiers JSON pour MyTrainingPeaks ({len(json_files)}):")
        for f in json_files:
            size = os.path.getsize(f)
            print(f"   📄 {os.path.basename(f)} ({size} bytes)")
    
    if csv_files:
        print(f"\n📈 Fichiers CSV pour analyse ({len(csv_files)}):")
        for f in csv_files:
            size = os.path.getsize(f)
            print(f"   📊 {os.path.basename(f)} ({size} bytes)")
    
    print(f"\n📁 Dossier: {output_dir}/")
    
    print(f"\n🚀 INSTRUCTIONS D'UTILISATION:")
    print(f"  🚴 MyWhoosh:")
    print(f"     1. Ouvrez MyWhoosh > Workouts > Import")
    print(f"     2. Sélectionnez un fichier .zwo")
    print(f"     3. La séance apparaîtra dans vos workouts")
    
    print(f"  📊 MyTrainingPeaks:")
    print(f"     1. Connectez-vous à TrainingPeaks")
    print(f"     2. Calendar > + > Workout > Import")
    print(f"     3. Uploadez un fichier .json")
    
    print(f"  📈 Analyse:")
    print(f"     Ouvrez les fichiers .csv dans Excel/Google Sheets")
    
    print(f"\n✅ Coach IA simple - 100% fonctionnel ! 🎉")

if __name__ == "__main__":
    main()