#!/usr/bin/env python3
"""
Tests unitaires pour TLS Hybrid Bench

Usage: python -m pytest tests/ -v
"""

import unittest
import pandas as pd
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cari_analysis.compute_cari import CARICalculator


class TestCARICalculator(unittest.TestCase):
    """Tests pour le calculateur CARI."""
    
    def setUp(self):
        """Configuration des tests."""
        self.calculator = CARICalculator()
        
        # Données de test basées sur l'enquête ANSSI
        self.test_data = pd.DataFrame({
            'manque_normes': [2, 3, 4],
            'hybridation_non_standard': [1, 3, 4],
            'lib_reference': [1, 3, 4],
            'referentiels': [2, 3, 4],
            'equipement_HW': [2, 3, 4],
            'perf_signature': [1, 3, 4],
            'plan_transition': [1, 4, 5],
            'certif_biblio': [2, 3, 4],
            'manque_sensi': [2, 3, 5],
            'cost_skills': [3, 4, 5]
        }, index=['specialistes', 'sensibilises', 'non_sensibilises'])
        
    def test_weights_sum_to_100(self):
        """Vérifier que les poids totalisent 100%."""
        total_weight = sum(self.calculator.WEIGHTS.values())
        self.assertEqual(total_weight, 100)
        
    def test_cari_calculation(self):
        """Tester le calcul de l'indice CARI."""
        cari_scores = self.calculator.calculate_cari(self.test_data)
        
        # Vérifications de base
        self.assertEqual(len(cari_scores), 3)
        self.assertTrue(all(0 <= score <= 100 for score in cari_scores['CARI']))
        
        # Vérifier l'ordre (spécialistes > sensibilisés > non_sensibilisés)
        self.assertGreater(cari_scores.loc['specialistes', 'CARI'], 
                          cari_scores.loc['sensibilises', 'CARI'])
        self.assertGreater(cari_scores.loc['sensibilises', 'CARI'],
                          cari_scores.loc['non_sensibilises', 'CARI'])
        
    def test_score_ranges(self):
        """Tester les plages de scores attendues."""
        cari_scores = self.calculator.calculate_cari(self.test_data)
        
        # Spécialistes devraient avoir un score élevé (>90%)
        self.assertGreaterEqual(cari_scores.loc['specialistes', 'CARI'], 90)
        
        # Non sensibilisés devraient avoir un score plus faible (<80%)
        self.assertLess(cari_scores.loc['non_sensibilises', 'CARI'], 80)
        
    def test_analysis_generation(self):
        """Tester la génération de l'analyse."""
        cari_scores = self.calculator.calculate_cari(self.test_data)
        analysis = self.calculator.generate_analysis(self.test_data, cari_scores)
        
        # Vérifier la structure de l'analyse
        self.assertIn('summary', analysis)
        self.assertIn('scores', analysis)
        self.assertIn('criteria_weights', analysis)
        self.assertIn('interpretation', analysis)
        self.assertIn('metadata', analysis)
        
        # Vérifier les métriques de résumé
        summary = analysis['summary']
        self.assertEqual(summary['categories'], 3)
        self.assertEqual(summary['criteria'], 10)


class TestDataValidation(unittest.TestCase):
    """Tests de validation des données."""
    
    def test_cari_input_file(self):
        """Tester la validité du fichier d'entrée CARI."""
        input_file = os.path.join(os.path.dirname(__file__), 
                                 '..', 'data', 'input', 'cari_input.csv')
        
        if os.path.exists(input_file):
            df = pd.read_csv(input_file).set_index('categorie')
            
            # Vérifier la structure
            self.assertEqual(len(df), 3)  # 3 catégories
            self.assertEqual(len(df.columns), 10)  # 10 critères
            
            # Vérifier les plages de valeurs (1-5)
            self.assertTrue(((df >= 1) & (df <= 5)).all().all())
            
            # Vérifier les noms des catégories
            expected_categories = ['specialistes', 'sensibilises', 'non_sensibilises']
            self.assertTrue(all(cat in df.index for cat in expected_categories))


if __name__ == '__main__':
    # Exécuter les tests
    unittest.main(verbosity=2)
