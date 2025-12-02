import unittest
from datetime import datetime
import re

class TestUtilsFunctions(unittest.TestCase):
    
    def test_formatage_date(self):
        """Test formatage de dates"""
        
        def formater_date_mois(date_str):
            """Convertit '2023-01' en datetime"""
            try:
                return datetime.strptime(date_str + '-01', '%Y-%m-%d')
            except ValueError:
                return None
        
        # Test conversion normale
        date = formater_date_mois('2023-01')
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)
        
        # Test date invalide
        date_invalide = formater_date_mois('2023-13')
        self.assertIsNone(date_invalide)
        
        print("Formatage date OK")
    
    def test_extraction_annee_mois(self):
        """Test extraction année et mois d'une date"""
        
        def extraire_annee(date_str):
            return int(date_str.split('-')[0]) if '-' in date_str else None
        
        def extraire_mois(date_str):
            parts = date_str.split('-')
            return int(parts[1]) if len(parts) > 1 else None
        
        self.assertEqual(extraire_annee('2023-01'), 2023)
        self.assertEqual(extraire_annee('2024-12'), 2024)
        self.assertEqual(extraire_mois('2023-01'), 1)
        self.assertEqual(extraire_mois('2023-12'), 12)
        self.assertIsNone(extraire_annee('invalid'))
        
        print("Extraction année/mois OK")
    
    def test_nettoyage_texte(self):
        """Test nettoyage de texte"""
        
        def nettoyer_texte(texte):
            """Nettoie le texte : minuscules, sans espaces superflus"""
            if not texte:
                return ''
            return texte.strip().lower()
        
        def supprimer_accents(texte):
            """Supprime les accents"""
            if not texte:
                return ''
            replacements = {
                'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
                'à': 'a', 'â': 'a', 'ä': 'a',
                'î': 'i', 'ï': 'i',
                'ô': 'o', 'ö': 'o',
                'ù': 'u', 'û': 'u', 'ü': 'u',
                'ç': 'c'
            }
            for accented, plain in replacements.items():
                texte = texte.replace(accented, plain)
            return texte
        
        # Test nettoyage basique
        self.assertEqual(nettoyer_texte('  ALBI  '), 'albi')
        self.assertEqual(nettoyer_texte('Toulouse-Matabiau'), 'toulouse-matabiau')
        self.assertEqual(nettoyer_texte(''), '')
        
        # Test suppression accents
        self.assertEqual(supprimer_accents('élégant'), 'elegant')
        self.assertEqual(supprimer_accents('île'), 'ile')
        self.assertEqual(supprimer_accents('garçon'), 'garcon')
        
        print("Nettoyage texte OK")
    
    def test_validation_nombre(self):
        
        def est_nombre_valide(valeur, min_val=0, max_val=1000):
            """Valide qu'une valeur est un nombre dans une plage"""
            try:
                nombre = float(valeur)
                return min_val <= nombre <= max_val
            except (ValueError, TypeError):
                return False
        
        # Tests positifs
        self.assertTrue(est_nombre_valide('100'))
        self.assertTrue(est_nombre_valide(50))
        self.assertTrue(est_nombre_valide(0))
        self.assertTrue(est_nombre_valide(1000))
        
        # Tests négatifs
        self.assertFalse(est_nombre_valide(-10))
        self.assertFalse(est_nombre_valide(1001))
        self.assertFalse(est_nombre_valide('abc'))
        self.assertFalse(est_nombre_valide(None))
        
        # Test avec plage personnalisée
        self.assertTrue(est_nombre_valide(500, 0, 1000))
        self.assertFalse(est_nombre_valide(1500, 0, 1000))
        
        print("Validation nombre OK")
    
    def test_formatage_nombre(self):
        """Test formatage de nombres"""
        
        def formater_nombre(nombre, decimales=0):
            """Formate un nombre avec séparateur de milliers"""
            try:
                if decimales == 0:
                    return f"{int(nombre):,}".replace(',', ' ')
                else:
                    return f"{nombre:,.{decimales}f}".replace(',', ' ').replace('.', ',')
            except (ValueError, TypeError):
                return str(nombre)
        
        self.assertEqual(formater_nombre(1000), '1 000')
        self.assertEqual(formater_nombre(1234567), '1 234 567')
        self.assertEqual(formater_nombre(1234.567, 2), '1 234,57')
        self.assertEqual(formater_nombre('invalid'), 'invalid')
        
        print("Formatage nombre OK")
    
    def test_generation_id_unique(self):
        """Test génération d'ID uniques"""
        
        def generer_id(prefixe, index):
            """Génère un ID unique"""
            return f"{prefixe}_{index:03d}"
        
        ids = [generer_id('ville', i) for i in range(1, 4)]
        
        self.assertEqual(ids[0], 'ville_001')
        self.assertEqual(ids[1], 'ville_002')
        self.assertEqual(ids[2], 'ville_003')
        
        # Vérifie unicité
        self.assertEqual(len(set(ids)), 3)
        
        print("Génération ID OK")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTS FONCTIONS UTILITAIRES")
    print("="*50)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUtilsFunctions)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*50)
    if result.wasSuccessful():
        print("TOUS LES TESTS UTILITAIRES PASSENT !")
    else:
        print("CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*50)