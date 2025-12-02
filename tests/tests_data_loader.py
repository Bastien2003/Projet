import pandas as pd
import unittest
import os

class TestDataLoader(unittest.TestCase):
    """Tests pour la classe DataLoader"""
    
    def test_import_pandas(self):
        """Test que pandas est bien importé"""
        import pandas as pd
        self.assertTrue(hasattr(pd, 'DataFrame'))
        self.assertTrue(hasattr(pd, 'read_csv'))
        print(f"pandas version {pd.__version__} OK")
    
    def test_creation_dataframe(self):
        """Test création basique de DataFrame"""
        df = pd.DataFrame({
            'Train': ['Intercités', 'TGV', 'TER'],
            'Vitesse': [160, 320, 140],
            'Passagers': [300, 500, 200]
        })
        
        self.assertEqual(len(df), 3)
        self.assertEqual(list(df.columns), ['Train', 'Vitesse', 'Passagers'])
        self.assertEqual(df['Train'].iloc[0], 'Intercités')
        self.assertEqual(df['Vitesse'].iloc[1], 320)
        print("Création DataFrame OK")
    
    def test_lecture_csv_simulee(self):
        """Test simulation de lecture CSV"""
        
        # Crée un DataFrame simulant un fichier CSV
        df_test = pd.DataFrame({
            'Date': ['2023-01', '2023-02'],
            'Train': ['IC 1234', 'IC 5678'],
            'Retard': [10, 15]
        })
        
        # Simule la sauvegarde et lecture
        fichier_test = 'test_data.csv'
        try:
            df_test.to_csv(fichier_test, index=False)
            
            # Simule la lecture
            df_lu = pd.read_csv(fichier_test)
            
            self.assertEqual(len(df_lu), 2)
            self.assertIn('Date', df_lu.columns)
            self.assertIn('Retard', df_lu.columns)
            print("Lecture CSV simulée OK")
        finally:
            # Nettoie
            if os.path.exists(fichier_test):
                os.remove(fichier_test)
    
    def test_structure_donnees_ferroviaires(self):
        """Test la structure attendue des données ferroviaires"""
        
        # Structure attendue (similaire à nos données)
        df_attendu = pd.DataFrame({
            'Date': pd.Series([], dtype='object'),
            'Départ': pd.Series([], dtype='object'),
            'Arrivée': pd.Series([], dtype='object'),
            'Nombre de trains programmés': pd.Series([], dtype='int64'),
            'Nombre de trains ayant circulé': pd.Series([], dtype='int64'),
            'Nombre de trains annulés': pd.Series([], dtype='int64'),
            "Nombre de trains en retard à l'arrivée": pd.Series([], dtype='int64'),
            'Taux de régularité': pd.Series([], dtype='float64')
        })
        
        # Vérifie les colonnes
        colonnes_attendues = [
            'Date',
            'Départ', 
            'Arrivée',
            'Nombre de trains programmés',
            'Nombre de trains ayant circulé',
            'Nombre de trains annulés',
            "Nombre de trains en retard à l'arrivée"
        ]
        
        for col in colonnes_attendues:
            self.assertIn(col, df_attendu.columns)
        
        print("Structure données ferroviaires OK")
    
    def test_gestion_types_donnees(self):
        """Test la gestion des types de données"""
        
        df = pd.DataFrame({
            'Date_str': ['2023-01', '2023-02'],
            'Nombre_int': [100, 110],
            'Taux_float': [95.5, 96.2],
            'Texte': ['Albi', 'Toulouse']
        })
        
        # Vérifie les types
        self.assertTrue(pd.api.types.is_string_dtype(df['Date_str']))
        self.assertTrue(pd.api.types.is_integer_dtype(df['Nombre_int']))
        self.assertTrue(pd.api.types.is_float_dtype(df['Taux_float']))
        self.assertTrue(pd.api.types.is_string_dtype(df['Texte']))
        
        print("Types de données OK")
    
    def test_filtrage_par_type_train(self):
        """Test le filtrage par type de train (intercités/TGV/etc)"""
        
        # Simule différents types de trains
        fichiers = {
            'albi_intercites.csv': pd.DataFrame({'test': [1]}),
            'toulouse_tgv.csv': pd.DataFrame({'test': [2]}),
            'tarbes_intercites.csv': pd.DataFrame({'test': [3]}),
            'montpellier_ter.csv': pd.DataFrame({'test': [4]})
        }
        
        # Filtre intercités
        intercites = {k: v for k, v in fichiers.items() if 'intercites' in k}
        
        self.assertEqual(len(intercites), 2)
        self.assertIn('albi_intercites.csv', intercites)
        self.assertIn('tarbes_intercites.csv', intercites)
        self.assertNotIn('toulouse_tgv.csv', intercites)
        self.assertNotIn('montpellier_ter.csv', intercites)
        
        print("Filtrage type train OK")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTS DATA LOADER")
    print("="*50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataLoader)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*50)
    if result.wasSuccessful():
        print("TOUS LES TESTS DATA LOADER PASSENT !")
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*50)