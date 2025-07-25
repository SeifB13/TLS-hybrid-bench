#!/usr/bin/env python3
"""
CARI (Crypto-Agility Readiness Index) Calculator

Calcule l'indice de maturité organisationnelle pour la transition post-quantique
basé sur l'enquête ANSSI auprès des éditeurs français (2023-2024).

Usage:
    python compute_cari.py [--input FILE] [--output DIR]

Author: SeifB13
Date: Juillet 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging


class CARICalculator:
    """Calculateur de l'indice CARI (Crypto-Agility Readiness Index)."""
    
    # Poids des critères (source: enquête ANSSI 2023-2024)
    WEIGHTS = {
        "manque_normes": 12,               # Manque de normes d'hybridation
        "hybridation_non_standard": 10,   # Hybridation non standardisée
        "lib_reference": 10,               # Bibliothèques de référence manquantes
        "referentiels": 8,                 # Référentiels obsolètes
        "equipement_HW": 8,                # Équipements matériels non compatibles
        "perf_signature": 5,               # Performance des signatures
        "plan_transition": 15,             # Plan de transition absent
        "certif_biblio": 12,               # Certification des bibliothèques
        "manque_sensi": 10,                # Manque de sensibilisation
        "cost_skills": 10                  # Coût de montée en compétences
    }
    
    def __init__(self, output_dir: str = "data/output"):
        """
        Initialise le calculateur CARI.
        
        Args:
            output_dir: Répertoire de sortie pour les résultats
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, input_file: str) -> pd.DataFrame:
        """
        Charge les données d'entrée.
        
        Args:
            input_file: Fichier CSV avec les scores par catégorie
            
        Returns:
            DataFrame indexé par catégorie
        """
        try:
            df = pd.read_csv(input_file).set_index("categorie")
            self.logger.info(f"Données chargées: {len(df)} catégories, {len(df.columns)} critères")
            return df
        except Exception as e:
            raise RuntimeError(f"Erreur chargement données: {e}")
            
    def calculate_cari(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule l'indice CARI pour chaque catégorie.
        
        Args:
            df: DataFrame avec les scores (1-5, où 5 = frein maximal)
            
        Returns:
            DataFrame avec les scores CARI (0-100%)
        """
        weights = pd.Series(self.WEIGHTS)
        
        # Vérification de la cohérence
        missing_weights = set(df.columns) - set(weights.index)
        if missing_weights:
            raise ValueError(f"Poids manquants pour: {missing_weights}")
            
        # Calcul CARI = score pondéré inversé
        # Score brut = somme(poids * (5 - score_frein))
        raw_scores = (weights * (5 - df)).sum(axis=1)
        
        # Normalisation sur 100%
        max_possible = raw_scores.max()
        cari_scores = 100 * raw_scores / max_possible
        
        cari_df = cari_scores.round(1).to_frame(name="CARI")
        
        self.logger.info("CARI calculé:")
        for category, score in cari_df["CARI"].items():
            self.logger.info(f"  {category}: {score}%")
            
        return cari_df
        
    def generate_analysis(self, df: pd.DataFrame, cari_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Génère l'analyse détaillée des résultats.
        
        Args:
            df: DataFrame des scores originaux
            cari_df: DataFrame des scores CARI
            
        Returns:
            Dictionnaire d'analyse
        """
        analysis = {
            "summary": {
                "categories": len(cari_df),
                "criteria": len(df.columns),
                "max_score": float(cari_df["CARI"].max()),
                "min_score": float(cari_df["CARI"].min()),
                "mean_score": float(cari_df["CARI"].mean())
            },
            "scores": {
                category: {
                    "cari": float(score),
                    "ranking": int(rank)
                }
                for rank, (category, score) in enumerate(
                    cari_df["CARI"].sort_values(ascending=False).items(), 1
                )
            },
            "criteria_weights": self.WEIGHTS,
            "interpretation": self._interpret_scores(cari_df),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "methodology": "ANSSI Survey 2023-2024",
                "total_weight": sum(self.WEIGHTS.values())
            }
        }
        
        return analysis
        
    def _interpret_scores(self, cari_df: pd.DataFrame) -> Dict[str, str]:
        """Interprète les scores CARI."""
        interpretations = {}
        
        for category, score in cari_df["CARI"].items():
            if score >= 90:
                level = "Excellent - Prêt pour la transition PQC"
            elif score >= 80:
                level = "Bon - Quelques freins à lever"
            elif score >= 70:
                level = "Modéré - Préparation nécessaire"
            elif score >= 60:
                level = "Faible - Efforts importants requis"
            else:
                level = "Très faible - Transition à risque"
                
            interpretations[category] = level
            
        return interpretations
        
    def generate_radar_charts(self, df: pd.DataFrame, output_dir: str = None) -> List[str]:
        """
        Génère les diagrammes radar pour chaque catégorie.
        
        Args:
            df: DataFrame des scores originaux
            output_dir: Répertoire de sortie (auto si None)
            
        Returns:
            Liste des fichiers générés
        """
        if output_dir is None:
            output_dir = self.output_dir / "figures"
            
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        weights = pd.Series(self.WEIGHTS)
        generated_files = []
        
        for category in df.index:
            output_path = Path(output_dir) / f"CARI_radar_{category}.pdf"
            self._create_radar_chart(df.loc[category], weights, category, output_path)
            generated_files.append(str(output_path))
            
        self.logger.info(f"Radars générés: {len(generated_files)} fichiers")
        return generated_files
        
    def _create_radar_chart(self, row: pd.Series, weights: pd.Series, 
                           category: str, output_path: str):
        """Crée un diagramme radar pour une catégorie."""
        labels = weights.index
        
        # Conversion: score frein -> score maturité (5 - frein)
        values = list((5 - row[labels]).values)
        values += values[:1]  # Fermeture du polygon
        
        # Angles pour le radar
        angles = np.linspace(0, 2 * np.pi, len(labels) + 1)
        
        # Création du graphique
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, polar=True)
        
        # Tracé et remplissage
        ax.plot(angles, values, 'o-', linewidth=2, color="steelblue")
        ax.fill(angles, values, alpha=0.25, color="lightblue")
        
        # Configuration des axes
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, 
                         [self._format_label(label) for label in labels], 
                         fontsize=10)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'])
        ax.grid(True)
        
        # Titre
        category_names = {
            "specialistes": "Éditeurs Spécialistes",
            "sensibilises": "Éditeurs Sensibilisés", 
            "non_sensibilises": "Éditeurs Non Sensibilisés"
        }
        title = category_names.get(category, category.title())
        ax.set_title(f"Maturité Crypto-Agile\n{title}", 
                    pad=20, fontsize=14, fontweight='bold')
        
        # Sauvegarde
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Radar sauvegardé: {output_path}")
        
    def _format_label(self, label: str) -> str:
        """Formate les labels pour l'affichage."""
        label_mapping = {
            "manque_normes": "Normes",
            "hybridation_non_standard": "Hybridation",
            "lib_reference": "Bibliothèques",
            "referentiels": "Référentiels",
            "equipement_HW": "Matériel",
            "perf_signature": "Performances",
            "plan_transition": "Plan transition",
            "certif_biblio": "Certification",
            "manque_sensi": "Sensibilisation",
            "cost_skills": "Compétences"
        }
        return label_mapping.get(label, label)
        
    def save_results(self, cari_df: pd.DataFrame, analysis: Dict[str, Any],
                    filename_prefix: str = "cari_results") -> Dict[str, str]:
        """
        Sauvegarde tous les résultats CARI.
        
        Args:
            cari_df: DataFrame des scores CARI
            analysis: Analyse détaillée
            filename_prefix: Préfixe des fichiers
            
        Returns:
            Dictionnaire des fichiers créés
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files = {}
        
        # Scores CSV
        csv_path = self.output_dir / f"{filename_prefix}_{timestamp}.csv"
        cari_df.to_csv(csv_path)
        files["scores_csv"] = str(csv_path)
        
        # Analyse JSON
        json_path = self.output_dir / f"{filename_prefix}_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        files["analysis_json"] = str(json_path)
        
        # Export LaTeX
        tex_path = self.output_dir / f"{filename_prefix}_{timestamp}.tex"
        latex_table = cari_df.to_latex(
            column_format="l c",
            index=True,
            bold_rows=True,
            caption="Crypto-Agility Readiness Index (CARI)",
            label="tab:cari"
        )
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_table)
        files["latex_table"] = str(tex_path)
        
        # Rapport Markdown
        md_path = self.output_dir / f"{filename_prefix}_report_{timestamp}.md"
        self._generate_markdown_report(analysis, md_path)
        files["markdown_report"] = str(md_path)
        
        return files
        
    def _generate_markdown_report(self, analysis: Dict[str, Any], output_path: str):
        """Génère un rapport Markdown des résultats CARI."""
        report = f"""# CARI Analysis Report

Generated: {analysis["metadata"]["timestamp"]}
Methodology: {analysis["metadata"]["methodology"]}

## Summary

- **Categories analyzed**: {analysis["summary"]["categories"]}
- **Criteria evaluated**: {analysis["summary"]["criteria"]}
- **Score range**: {analysis["summary"]["min_score"]:.1f}% - {analysis["summary"]["max_score"]:.1f}%
- **Average maturity**: {analysis["summary"]["mean_score"]:.1f}%

## Individual Scores

"""
        
        for category, data in analysis["scores"].items():
            interpretation = analysis["interpretation"][category]
            report += f"### {category.title()}\n"
            report += f"- **CARI Score**: {data['cari']:.1f}%\n"
            report += f"- **Ranking**: #{data['ranking']}\n"
            report += f"- **Interpretation**: {interpretation}\n\n"
            
        report += """## Methodology

The CARI index evaluates organizational readiness for post-quantum cryptography transition across 10 weighted criteria:

"""
        
        for criterion, weight in analysis["criteria_weights"].items():
            report += f"- **{criterion}**: {weight}% weight\n"
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)


def main():
    """Fonction principale CLI."""
    parser = argparse.ArgumentParser(
        description="CARI Calculator - Crypto-Agility Readiness Index",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--input", "-i",
        default="data/input/cari_input.csv",
        help="Fichier CSV d'entrée avec les scores"
    )
    
    parser.add_argument(
        "--output", "-o", 
        default="data/output",
        help="Répertoire de sortie"
    )
    
    parser.add_argument(
        "--radar", "-r",
        action="store_true",
        help="Générer les diagrammes radar"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialisation
        calculator = CARICalculator(output_dir=args.output)
        
        # Chargement et calcul
        df = calculator.load_data(args.input)
        cari_df = calculator.calculate_cari(df)
        analysis = calculator.generate_analysis(df, cari_df)
        
        # Génération des radars si demandé
        if args.radar:
            calculator.generate_radar_charts(df)
            
        # Sauvegarde
        files = calculator.save_results(cari_df, analysis)
        
        # Affichage résultats
        print("\n" + "="*60)
        print("RÉSULTATS CARI (Crypto-Agility Readiness Index)")
        print("="*60)
        
        for category, data in analysis["scores"].items():
            print(f"{category:15s}: {data['cari']:5.1f}% - {analysis['interpretation'][category]}")
            
        print(f"\nFichiers générés:")
        for file_type, path in files.items():
            print(f"  {file_type}: {path}")
            
    except Exception as e:
        logging.error(f"Erreur pendant le calcul CARI: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
