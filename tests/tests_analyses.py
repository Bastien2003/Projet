import pandas as pd
import unittest
import numpy as np

class TestAnalysisFunctions(unittest.TestCase):
    """Tests pour les fonctions d'analyse"""
    
    def test_calcul_taux_retard(self):
        """Test calcul du taux de retard"""
        
        def calcul_taux_retard(trains_retard, trains_circules):
            if trains_circules == 0:
                return 0
            return (trains_retard / trains_circules) * 100
        
        # Test normal
        self.assertEqual(calcul_taux_retard(15, 100), 15.0)
        
        # Test avec zéro train circulé
        self.assertEqual(calcul_taux_retard(10, 0), 0)
        
        # Test avec valeurs décimales
        self.assertAlmostEqual(calcul_taux_retard(7, 50), 14.0)
        print("Calcul taux retard OK")
    
    def test_calcul_taux_annulation(self):
        """Test calcul du taux d'annulation"""
        
        def calcul_taux_annulation(trains_annules, trains_programmes):
            if trains_programmes == 0:
                return 0
            return (trains_annules / trains_programmes) * 100
        
        self.assertEqual(calcul_taux_annulation(5, 100), 5.0)
        self.assertEqual(calcul_taux_annulation(0, 100), 0.0)
        self.assertEqual(calcul_taux_annulation(10, 0), 0)
        print("Calcul taux annulation OK")
    
    def test_calcul_moyenne(self):
        """Test calcul de moyenne simple"""
        
        def calcul_moyenne(valeurs):
            if not valeurs:
                return 0
            return sum(valeurs) / len(valeurs)
        
        self.assertEqual(calcul_moyenne([10, 20, 30]), 20.0)
        self.assertEqual(calcul_moyenne([5]), 5.0)
        self.assertEqual(calcul_moyenne([]), 0)
        print("Calcul moyenne OK")
    
    def test_calcul_moyenne_ponderee(self):
        """Test calcul de moyenne pondérée"""
        
        def calcul_moyenne_ponderee(valeurs, poids):
            if not valeurs or sum(poids) == 0:
                return 0
            return sum(v * p for v, p in zip(valeurs, poids)) / sum(poids)
        
        # Test simple
        self.assertAlmostEqual(
            calcul_moyenne_ponderee([10, 20, 30], [1, 2, 3]), 
            23.333, 
            places=3
        )
        
        # Test avec poids nuls
        self.assertEqual(calcul_moyenne_ponderee([10, 20], [0, 0]), 0)
        print("Calcul moyenne pondérée OK")
    
    def test_calcul_ecart_type(self):
        """Test calcul d'écart type"""
        
        def calcul_ecart_type(valeurs):
            if len(valeurs) < 2:
                return 0
            moyenne = sum(valeurs) / len(valeurs)
            variance = sum((x - moyenne) ** 2 for x in valeurs) / (len(valeurs) - 1)
            return variance ** 0.5
        
        data = [10, 20, 30, 40]
        ecart = calcul_ecart_type(data)
        
        self.assertGreater(ecart, 0)
        self.assertIsInstance(ecart, float)
        
        # Pour liste d'un seul élément
        self.assertEqual(calcul_ecart_type([10]), 0)
        print("Calcul écart type OK")
    
    def test_groupement_par_mois(self):
        """Test groupement des données par mois"""
        
        # Crée des données avec dates
        df = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-15', '2023-01-20', '2023-02-10', '2023-02-25']),
            'Valeur': [10, 20, 30, 40]
        })
        
        # Extrait le mois
        df['Mois'] = df['Date'].dt.month
        
        # Groupe par mois
        grouped = df.groupby('Mois')['Valeur'].sum().reset_index()
        
        self.assertEqual(len(grouped), 2)
        self.assertEqual(grouped[grouped['Mois'] == 1]['Valeur'].iloc[0], 30)  # 10+20
        self.assertEqual(grouped[grouped['Mois'] == 2]['Valeur'].iloc[0], 70)  # 30+40
        print("Groupement par mois OK")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("FONCTIONS D'ANALYSE")
    print("="*50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalysisFunctions)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*50)
    if result.wasSuccessful():
        print("TOUS LES TESTS D'ANALYSE PASSENT !")
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*50)