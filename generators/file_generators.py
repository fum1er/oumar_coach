#!/usr/bin/env python3
"""
File Generators - Génération de fichiers d'entraînement (ZWO, JSON, TCX, etc.)
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class FileGenerator:
    """Générateur de fichiers d'entraînement multi-formats"""
    
    def __init__(self, output_dir: str = "output_advanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Créer sous-dossiers
        (self.output_dir / "zwo").mkdir(exist_ok=True)
        (self.output_dir / "json").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
    
    def generate_all_formats(self, workout) -> Dict[str, str]:
        """Génère tous les formats disponibles"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_filename(workout.name)
        
        files = {}
        
        try:
            # 1. ZWO pour MyWhoosh/Zwift
            zwo_file = self.output_dir / "zwo" / f"{safe_name}_{timestamp}.zwo"
            if self._generate_zwo_file(workout, str(zwo_file)):
                files['ZWO (MyWhoosh/Zwift)'] = str(zwo_file)
            
            # 2. JSON pour TrainingPeaks
            tp_file = self.output_dir / "json" / f"{safe_name}_{timestamp}_tp.json"
            if self._generate_trainingpeaks_json(workout, str(tp_file)):
                files['JSON (TrainingPeaks)'] = str(tp_file)
            
            # 3. JSON structure complète
            structure_file = self.output_dir / "json" / f"{safe_name}_{timestamp}_structure.json"
            if self._generate_structure_json(workout, str(structure_file)):
                files['JSON (Structure)'] = str(structure_file)
            
            # 4. Rapport détaillé
            report_file = self.output_dir / "reports" / f"{safe_name}_{timestamp}_report.md"
            if self._generate_detailed_report(workout, str(report_file)):
                files['Rapport (Markdown)'] = str(report_file)
            
        except Exception as e:
            print(f"⚠️ Erreur génération fichiers: {e}")
        
        return files
    
    def _sanitize_filename(self, name: str) -> str:
        """Nettoie un nom pour créer un nom de fichier valide"""
        # Remplacer caractères problématiques
        replacements = {
            ' ': '_', '×': 'x', '+': '_plus_', '/': '_', 
            '\\': '_', ':': '_', '*': '_', '?': '_',
            '"': '_', '<': '_', '>': '_', '|': '_'
        }
        
        safe_name = name
        for old, new in replacements.items():
            safe_name = safe_name.replace(old, new)
        
        # Limiter la longueur
        return safe_name[:50]
    
    def _generate_zwo_file(self, workout, filename: str) -> bool:
        """Génère un fichier ZWO optimisé pour MyWhoosh/Zwift"""
        try:
            root = ET.Element("workout_file")
            
            # Métadonnées enrichies
            author = ET.SubElement(root, "author")
            author.text = "Advanced Cycling AI Coach"
            
            name = ET.SubElement(root, "name")
            name.text = workout.name
            
            description = ET.SubElement(root, "description")
            description.text = f"{workout.description}\n\n🎯 {workout.scientific_objective}"
            
            # Tags multiples pour catégorisation
            tags = ET.SubElement(root, "tags")
            tag_names = [workout.type, "scientific", "ai_generated"]
            if workout.estimated_tss > 80:
                tag_names.append("high_intensity")
            
            for tag_name in tag_names:
                tag = ET.SubElement(tags, "tag")
                tag.set("name", tag_name)
            
            # Workout principal
            workout_elem = ET.SubElement(root, "workout")
            
            # Ajouter segments de base
            for segment in workout.segments:
                step = self._create_zwo_step(workout_elem, segment)
            
            # Ajouter intervalles répétés
            for interval in workout.repeated_intervals:
                for rep in range(interval.repetitions):
                    # Interval de travail
                    work_step = ET.SubElement(workout_elem, "SteadyState")
                    work_step.set("Duration", str(interval.work_duration * 60))
                    work_step.set("PowerLow", f"{interval.work_power_pct[0]:.3f}")
                    work_step.set("PowerHigh", f"{interval.work_power_pct[1]:.3f}")
                    work_step.set("Cadence", str(interval.work_cadence))
                    
                    # Ajouter description comme commentaire (pas standard ZWO mais informatif)
                    work_step.set("Description", f"{interval.work_description} ({rep+1}/{interval.repetitions})")
                    
                    # Interval de repos (sauf après le dernier)
                    if rep < interval.repetitions - 1 and interval.rest_duration > 0:
                        rest_step = ET.SubElement(workout_elem, "SteadyState")
                        rest_step.set("Duration", str(interval.rest_duration * 60))
                        rest_step.set("PowerLow", f"{interval.rest_power_pct[0]:.3f}")
                        rest_step.set("PowerHigh", f"{interval.rest_power_pct[1]:.3f}")
                        rest_step.set("Cadence", str(interval.rest_cadence))
                        rest_step.set("Description", interval.rest_description)
            
            # Indentation pour lisibilité
            self._indent_xml(root)
            
            # Sauvegarde
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération ZWO: {e}")
            return False
    
    def _create_zwo_step(self, parent, segment):
        """Crée un élément ZWO selon le type de segment"""
        if segment.type == "Warmup":
            step = ET.SubElement(parent, "Warmup")
        elif segment.type == "Cooldown":
            step = ET.SubElement(parent, "Cooldown")
        else:
            step = ET.SubElement(parent, "SteadyState")
        
        step.set("Duration", str(segment.duration_minutes * 60))
        step.set("PowerLow", f"{segment.power_pct_ftp[0]:.3f}")
        step.set("PowerHigh", f"{segment.power_pct_ftp[1]:.3f}")
        step.set("Cadence", str(segment.cadence_rpm))
        
        return step
    
    def _generate_trainingpeaks_json(self, workout, filename: str) -> bool:
        """Génère JSON optimisé pour TrainingPeaks"""
        try:
            tp_data = {
                "name": workout.name,
                "description": workout.description,
                "sport": "Bike",
                "totalTime": workout.total_duration * 60,
                "estimatedTSS": workout.estimated_tss,
                "workoutType": workout.type,
                "scientificObjective": workout.scientific_objective,
                "adaptationNotes": workout.adaptation_notes,
                "coachingTips": workout.coaching_tips,
                "created": datetime.now().isoformat(),
                "ftp": workout.ftp,
                "intervals": []
            }
            
            step_index = 1
            
            # Ajouter segments
            for segment in workout.segments:
                tp_data["intervals"].append({
                    "step": step_index,
                    "duration": segment.duration_minutes * 60,
                    "type": segment.type,
                    "powerMin": int(segment.power_pct_ftp[0] * workout.ftp),
                    "powerMax": int(segment.power_pct_ftp[1] * workout.ftp),
                    "powerTarget": int((segment.power_pct_ftp[0] + segment.power_pct_ftp[1]) / 2 * workout.ftp),
                    "powerPctFTP": {
                        "min": segment.power_pct_ftp[0],
                        "max": segment.power_pct_ftp[1]
                    },
                    "cadence": segment.cadence_rpm,
                    "description": segment.description,
                    "scientificRationale": segment.scientific_rationale
                })
                step_index += 1
            
            # Ajouter intervalles répétés
            for interval in workout.repeated_intervals:
                for rep in range(interval.repetitions):
                    # Work interval
                    tp_data["intervals"].append({
                        "step": step_index,
                        "duration": interval.work_duration * 60,
                        "type": "Work",
                        "repetition": f"{rep+1}/{interval.repetitions}",
                        "powerMin": int(interval.work_power_pct[0] * workout.ftp),
                        "powerMax": int(interval.work_power_pct[1] * workout.ftp),
                        "powerTarget": int((interval.work_power_pct[0] + interval.work_power_pct[1]) / 2 * workout.ftp),
                        "powerPctFTP": {
                            "min": interval.work_power_pct[0],
                            "max": interval.work_power_pct[1]
                        },
                        "cadence": interval.work_cadence,
                        "description": interval.work_description,
                        "scientificRationale": interval.scientific_rationale
                    })
                    step_index += 1
                    
                    # Rest interval (sauf dernier)
                    if rep < interval.repetitions - 1 and interval.rest_duration > 0:
                        tp_data["intervals"].append({
                            "step": step_index,
                            "duration": interval.rest_duration * 60,
                            "type": "Rest",
                            "powerMin": int(interval.rest_power_pct[0] * workout.ftp),
                            "powerMax": int(interval.rest_power_pct[1] * workout.ftp),
                            "powerTarget": int((interval.rest_power_pct[0] + interval.rest_power_pct[1]) / 2 * workout.ftp),
                            "powerPctFTP": {
                                "min": interval.rest_power_pct[0],
                                "max": interval.rest_power_pct[1]
                            },
                            "cadence": interval.rest_cadence,
                            "description": interval.rest_description
                        })
                        step_index += 1
            
            # Sauvegarde
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tp_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération JSON TrainingPeaks: {e}")
            return False
    
    def _generate_structure_json(self, workout, filename: str) -> bool:
        """Génère JSON avec structure complète pour développeurs"""
        try:
            structure_data = {
                "metadata": {
                    "name": workout.name,
                    "type": workout.type,
                    "description": workout.description,
                    "scientific_objective": workout.scientific_objective,
                    "total_duration_minutes": workout.total_duration,
                    "estimated_tss": workout.estimated_tss,
                    "ftp": workout.ftp,
                    "generated_at": datetime.now().isoformat(),
                    "generator": "Advanced Cycling AI Coach"
                },
                "segments": [
                    {
                        "type": seg.type,
                        "duration_minutes": seg.duration_minutes,
                        "power_pct_ftp": {
                            "min": seg.power_pct_ftp[0],
                            "max": seg.power_pct_ftp[1]
                        },
                        "power_watts": {
                            "min": int(seg.power_pct_ftp[0] * workout.ftp),
                            "max": int(seg.power_pct_ftp[1] * workout.ftp)
                        },
                        "cadence_rpm": seg.cadence_rpm,
                        "description": seg.description,
                        "scientific_rationale": seg.scientific_rationale
                    }
                    for seg in workout.segments
                ],
                "repeated_intervals": [
                    {
                        "repetitions": interval.repetitions,
                        "work_phase": {
                            "duration_minutes": interval.work_duration,
                            "power_pct_ftp": {
                                "min": interval.work_power_pct[0],
                                "max": interval.work_power_pct[1]
                            },
                            "power_watts": {
                                "min": int(interval.work_power_pct[0] * workout.ftp),
                                "max": int(interval.work_power_pct[1] * workout.ftp)
                            },
                            "cadence_rpm": interval.work_cadence,
                            "description": interval.work_description
                        },
                        "rest_phase": {
                            "duration_minutes": interval.rest_duration,
                            "power_pct_ftp": {
                                "min": interval.rest_power_pct[0],
                                "max": interval.rest_power_pct[1]
                            },
                            "power_watts": {
                                "min": int(interval.rest_power_pct[0] * workout.ftp),
                                "max": int(interval.rest_power_pct[1] * workout.ftp)
                            },
                            "cadence_rpm": interval.rest_cadence,
                            "description": interval.rest_description
                        },
                        "scientific_rationale": interval.scientific_rationale
                    }
                    for interval in workout.repeated_intervals
                ],
                "coaching_notes": {
                    "adaptation_notes": workout.adaptation_notes,
                    "coaching_tips": workout.coaching_tips
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(structure_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération JSON structure: {e}")
            return False
    
    def _generate_detailed_report(self, workout, filename: str) -> bool:
        """Génère un rapport détaillé en Markdown"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {workout.name}\n\n")
                f.write(f"**Type:** {workout.type.upper()}\n")
                f.write(f"**Durée:** {workout.total_duration} minutes\n")
                f.write(f"**TSS Estimé:** {workout.estimated_tss:.0f}\n")
                f.write(f"**FTP:** {workout.ftp}W\n")
                f.write(f"**Généré le:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n")
                
                f.write(f"## Description\n\n")
                f.write(f"{workout.description}\n\n")
                
                f.write(f"## Objectif Scientifique\n\n")
                f.write(f"{workout.scientific_objective}\n\n")
                
                f.write(f"## Structure de la Séance\n\n")
                
                # Segments
                if workout.segments:
                    f.write("### Segments de Base\n\n")
                    for i, segment in enumerate(workout.segments, 1):
                        power_min = int(segment.power_pct_ftp[0] * workout.ftp)
                        power_max = int(segment.power_pct_ftp[1] * workout.ftp)
                        f.write(f"{i}. **{segment.type}** - {segment.duration_minutes}min\n")
                        f.write(f"   - Puissance: {power_min}-{power_max}W ({segment.power_pct_ftp[0]*100:.0f}-{segment.power_pct_ftp[1]*100:.0f}% FTP)\n")
                        f.write(f"   - Cadence: {segment.cadence_rpm} rpm\n")
                        f.write(f"   - Description: {segment.description}\n")
                        if segment.scientific_rationale:
                            f.write(f"   - Justification: {segment.scientific_rationale}\n")
                        f.write("\n")
                
                # Intervalles répétés
                if workout.repeated_intervals:
                    f.write("### Intervalles Répétés\n\n")
                    for i, interval in enumerate(workout.repeated_intervals, 1):
                        work_power_min = int(interval.work_power_pct[0] * workout.ftp)
                        work_power_max = int(interval.work_power_pct[1] * workout.ftp)
                        rest_power_min = int(interval.rest_power_pct[0] * workout.ftp)
                        rest_power_max = int(interval.rest_power_pct[1] * workout.ftp)
                        
                        f.write(f"**Série {i}: {interval.repetitions} répétitions**\n\n")
                        f.write(f"- **Travail:** {interval.work_duration}min à {work_power_min}-{work_power_max}W ({interval.work_power_pct[0]*100:.0f}-{interval.work_power_pct[1]*100:.0f}% FTP)\n")
                        f.write(f"  - Cadence: {interval.work_cadence} rpm\n")
                        f.write(f"  - Description: {interval.work_description}\n")
                        
                        if interval.rest_duration > 0:
                            f.write(f"- **Repos:** {interval.rest_duration}min à {rest_power_min}-{rest_power_max}W ({interval.rest_power_pct[0]*100:.0f}-{interval.rest_power_pct[1]*100:.0f}% FTP)\n")
                            f.write(f"  - Cadence: {interval.rest_cadence} rpm\n")
                            f.write(f"  - Description: {interval.rest_description}\n")
                        
                        if interval.scientific_rationale:
                            f.write(f"- **Justification:** {interval.scientific_rationale}\n")
                        f.write("\n")
                
                f.write(f"## Notes d'Adaptation\n\n")
                f.write(f"{workout.adaptation_notes}\n\n")
                
                f.write(f"## Conseils de Coaching\n\n")
                f.write(f"{workout.coaching_tips}\n\n")
                
                f.write(f"## Conseils Pratiques\n\n")
                f.write("### Avant la séance\n")
                f.write("- Échauffement de 10-15 minutes\n")
                f.write("- Hydratation optimale\n")
                f.write("- Vérifier matériel (capteur puissance, fréquence cardiaque)\n\n")
                
                f.write("### Pendant la séance\n")
                f.write("- Respecter les zones de puissance\n")
                f.write("- Maintenir cadence recommandée\n")
                f.write("- Écouter son corps\n\n")
                
                f.write("### Après la séance\n")
                f.write("- Retour au calme de 10-15 minutes\n")
                f.write("- Réhydratation\n")
                f.write("- Récupération active selon planning\n\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération rapport: {e}")
            return False
    
    def _indent_xml(self, elem, level=0):
        """Indente le XML pour améliorer la lisibilité"""
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