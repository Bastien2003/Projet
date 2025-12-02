"""
TESTS SPÉCIFIQUES pour le module Intercités Occitanie

"""
import pandas as pd
import unittest
from datetime import datetime
import sys
import os

# Simule l'import de tes modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestIntercitesDash(unittest.TestCase):
    """Tests unitaires pour l'application Dash Intercités"""
    
    def setUp(self):
        """Prépare des données de test avant chaque test"""
        # Crée des données similaires à celles de ton app
        self.df_test = pd.DataFrame({
            'Ville': ['Albi', 'Albi', 'Toulouse', 'Toulouse'],
            'Départ': ['Paris-Austerlitz', 'Paris-Austerlitz', 'Bordeaux', 'Bordeaux'],
            'Annee': [2023, 2024, 2023, 2024],
            'Date': ['2023-01', '2024-01', '2023-01', '2024-01'],
            "Nombre de trains en retard à l'arrivée": [10, 15, 5, 8],
            "Nombre de trains annulés": [2, 3, 1, 0],
            "Nombre de trains programmés": [100, 110, 120, 115],
            "Nombre de trains ayant circulé": [98, 107, 119, 115]
        })
        
        # Ajoute les colonnes Date_complete comme dans le code
        self.df_test['Date_complete'] = pd.to_datetime(
            self.df_test['Date'].astype(str) + '-01', 
            format='%Y-%m-%d', 
            errors='coerce'
        )
        self.df_test['Mois'] = self.df_test['Date_complete'].dt.month
    
    def test_filtrage_intercites(self):
        """Test que seuls les fichiers intercites sont gardés"""
        data_dict = {
            'albi_intercites': pd.DataFrame({'test': [1]}),
            'toulouse_tgv': pd.DataFrame({'test': [2]}),
            'tarbes_intercites': pd.DataFrame({'test': [3]})
        }
        
        # Simule le filtre
        filtered = {k: df for k, df in data_dict.items() if 'intercites' in k}
        
        self.assertEqual(len(filtered), 2)
        self.assertIn('albi_intercites', filtered)
        self.assertIn('tarbes_intercites', filtered)
        self.assertNotIn('toulouse_tgv', filtered)
        print("Filtrage intercités OK")
    
    def test_verification_colonnes_requises(self):
        """Test que les colonnes requises existent (comme dans le code)"""
        REQUIRED_COLS = [
            "Nombre de trains en retard à l'arrivée",
            "Nombre de trains annulés",
            "Nombre de trains programmés", 
            "Nombre de trains ayant circulé",
            "Date"
        ]
        
        # Test avec un DataFrame similaire au notre
        df_test = pd.DataFrame({
            "Nombre de trains en retard à l'arrivée": [10],
            "Nombre de trains annulés": [2],
            "Nombre de trains programmés": [100],
            "Nombre de trains ayant circulé": [98],
            "Date": ["2023-01"],
            "Départ": ["Paris-Austerlitz"],
            "Arrivée": ["Albi"]
        })
        
        for col in REQUIRED_COLS:
            self.assertIn(col, df_test.columns, f"Colonne manquante: {col}")
        print("Colonnes requises OK")
    
    def test_get_available_years(self):
        """Test la fonction get_available_years (simulée)"""
        print("🧪 Test get_available_years...")
        
        # Simule la fonction
        def get_available_years(df, ville, gare=None):
            data = df[df['Ville'] == ville]
            if gare:
                data = data[data['Départ'] == gare]
            years = sorted(data['Annee'].dropna().unique(), reverse=True)
            return years
        
        # Test avec ville seule
        annees_albi = get_available_years(self.df_test, 'Albi')
        self.assertEqual(annees_albi, [2024, 2023])
        
        # Test avec ville et gare
        annees_toulouse = get_available_years(self.df_test, 'Toulouse', 'Bordeaux')
        self.assertEqual(annees_toulouse, [2024, 2023])
        print("obtenir les années disponibles OK")
    
    def test_update_gare_logic(self):
        """Test la logique de ton callback update_gare"""
        print("🧪 Test logique update_gare...")
        
        def update_gare_logic(df, ville):
            if not ville:
                return [], None, True, {'display': 'none'}, {'display': 'none'}
            
            gares = sorted(df[df['Ville'] == ville]['Départ'].dropna().unique())
            
            if len(gares) <= 1:
                value = gares[0] if len(gares) == 1 else None
                return [], value, True, {'display': 'none'}, {'display': 'none'}
            
            options = [{'label': g, 'value': g} for g in gares]
            value = gares[0]
            return options, value, False, {'display': 'block'}, {'display': 'block'}
        
        # Test avec ville ayant plusieurs gares (simulé)
        df_multiple = pd.DataFrame({
            'Ville': ['TestVille', 'TestVille', 'TestVille'],
            'Départ': ['Gare1', 'Gare2', 'Gare3']
        })
        
        options, value, disabled, style_dropdown, style_container = update_gare_logic(
            df_multiple, 'TestVille'
        )
        
        self.assertEqual(len(options), 3)
        self.assertEqual(value, 'Gare1')
        self.assertFalse(disabled)
        self.assertEqual(style_dropdown, {'display': 'block'})
        print("Logique update_gare OK")
    
    def test_filtrage_dataframe(self):
        """Test les filtres comme dans le callback update_graphique"""
        
        # Ville seule
        data_ville = self.df_test[self.df_test['Ville'] == 'Albi']
        self.assertEqual(len(data_ville), 2)
        
        # Ville + Année
        data_ville_annee = self.df_test[
            (self.df_test['Ville'] == 'Albi') & 
            (self.df_test['Annee'] == 2023)
        ]
        self.assertEqual(len(data_ville_annee), 1)
        self.assertEqual(data_ville_annee["Nombre de trains en retard à l'arrivée"].iloc[0], 10)
        
        # Ville + Gare + Année
        data_complet = self.df_test[
            (self.df_test['Ville'] == 'Albi') & 
            (self.df_test['Départ'] == 'Paris-Austerlitz') & 
            (self.df_test['Annee'] == 2023)
        ]
        self.assertEqual(len(data_complet), 1)
        print("Filtrage DataFrame OK")
    
    def test_tri_par_date(self):
        """Test le tri par date comme dans le code"""
        
        # Crée des dates non triées
        df_non_trie = pd.DataFrame({
            'Date_complete': pd.to_datetime(['2023-03-01', '2023-01-01', '2023-02-01']),
            'Valeur': [30, 10, 20]
        })
        
        # Trie comme dans le code
        df_trie = df_non_trie.sort_values('Date_complete')
        
        self.assertEqual(df_trie['Date_complete'].iloc[0], pd.Timestamp('2023-01-01'))
        self.assertEqual(df_trie['Date_complete'].iloc[1], pd.Timestamp('2023-02-01'))
        self.assertEqual(df_trie['Date_complete'].iloc[2], pd.Timestamp('2023-03-01'))
        print("✅ Tri par date OK")
    
    def test_cas_donnees_vides(self):
        """Test la gestion des cas où il n'y a pas de données"""
        
        df_vide = pd.DataFrame()
        
        # Test avec DataFrame vide
        resultat = df_vide[df_vide['Ville'] == 'Inexistant']
        self.assertTrue(resultat.empty)
        
        # Test filtrage sur ville inexistante
        resultat_ville = self.df_test[self.df_test['Ville'] == 'VilleInexistante']
        self.assertTrue(resultat_ville.empty)
        print("✅ Cas données vides OK")
    
    def test_colonnes_ajoutees(self):
        """Test que les colonnes Ville et Départ sont correctement ajoutées"""
        
        # Simule l'ajout de colonnes
        df_albi = pd.DataFrame({"Date": ["2023-01"]})
        df_albi['Ville'] = 'Albi'
        df_albi['Départ'] = 'Paris-Austerlitz'
        
        df_toulouse = pd.DataFrame({"Date": ["2023-01"]})
        df_toulouse['Ville'] = 'Toulouse'
        df_toulouse['Départ'] = 'Inconnu'
        
        self.assertEqual(df_albi['Ville'].iloc[0], 'Albi')
        self.assertEqual(df_albi['Départ'].iloc[0], 'Paris-Austerlitz')
        self.assertEqual(df_toulouse['Ville'].iloc[0], 'Toulouse')
        self.assertEqual(df_toulouse['Départ'].iloc[0], 'Inconnu')
        print("✅ Colonnes ajoutées OK")

#EXECUTION
if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTS SPÉCIFIQUES INTERCITÉS")
    print("="*50)
    
    # Crée et exécute les tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntercitesDash)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*50)
    if result.wasSuccessful():
        print("TOUS LES TESTS INTERCITÉS PASSENT !")
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*50)
