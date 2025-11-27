import pandas as pd
import os 
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
