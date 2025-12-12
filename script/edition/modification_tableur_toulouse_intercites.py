import pandas as pd
import os 

"""
Script de traitement des données de trains à Toulouse-Matabiau.

Ce script effectue les opérations suivantes :
1. Lecture d'un fichier CSV contenant les informations sur les trains (programmés, circulés, annulés, retardés).
2. Affichage des colonnes et du nombre de lignes initiales.
3. Regroupement des données par date et gare de départ, en sommant ou moyennant certaines colonnes.
4. Export des données regroupées dans un nouveau fichier CSV.
5. Affichage du chemin absolu du fichier résultant.

Dépendances :
- pandas
- os

Chemins des fichiers à modifier selon l'environnement utilisateur.
"""

toulouse = pd.read_csv("C:/Users/SCD-UM/Documents/bases/toulouse_matabiau_retard_arrivee_intercites.csv", sep=";", encoding="UTF-8")
print("Colonnes:", list(toulouse.columns))


print(f"Lignes avant: {len(toulouse)}")

# Regrouper par mois et gare
toulouse_regroupe = toulouse.groupby(['Date', 'Départ']).agg({
    'Nombre de trains programmés': 'sum',
    'Nombre de trains ayant circulé': 'sum',
    'Nombre de trains annulés': 'sum',
    "Nombre de trains en retard à l'arrivée": 'sum',
    'Taux de régularité': 'mean',
    "Nombre de trains à l'heure pour un train en retard à l'arrivée": 'mean',
    'Arrivée': 'first'
}).reset_index()

print(f"Lignes après: {len(toulouse_regroupe)}")


nouveau_toulouse= "C:/Users/SCD-UM/Documents/bases/toulouse_matabiau_retard_arrivee_intercites_REGOUPE.csv"
toulouse_regroupe.to_csv(nouveau_toulouse, sep=";", encoding="UTF-8", index=False)


chemin_absolu = os.path.abspath(nouveau_toulouse)
print(f"Chemin absolu: {chemin_absolu}")
