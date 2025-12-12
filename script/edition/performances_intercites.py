"""
Module d'analyse des performances du réseau Intercités dans le Sud Ouest.

Ce script :
- charge les données ferroviaires depuis plusieurs fichiers CSV via `load_all_data()`,
- filtre et nettoie les données spécifiques aux lignes Intercités,
- corrige les colonnes 'Départ' et 'Arrivée' selon certaines règles métier,
- agrège les données par relation Départ -> Arrivée,
- calcule des indicateurs tels que le taux de retard et d'annulation,
- génère un scatter plot interactif avec Plotly pour visualiser la performance des lignes.
"""

import pandas as pd
import plotly.express as px
from data_loader import DataLoader

import time
import psutil
import os

# Avant l'exécution
process = psutil.Process(os.getpid())
mem_avant = process.memory_info().rss / 1024 / 1024  # Mo

# Début du chronomètre
start_time = time.time()


# Chargement des données via la nouvelle classe
loader = DataLoader()
all_data = loader.load_all_data()

#Charger les fichiers "intercites" uniquement
data_dict = {k: df for k, df in all_data.items() if "intercites" in k}

#Vérification qu'on a bien chargé des données
if not data_dict:
    raise ValueError("Aucune donnée 'intercites' trouvée")

# Nettoyage spécifique pour chaque fichier

"""
Ce bloc :
- standardise les noms de colonnes,
- corrige l'ordre des colonnes 'Départ'/'Arrivée' pour certaines gares,
- applique des règles spécifiques pour Tarbes, Paris, etc.
"""
for k, df in data_dict.items():
    # Nettoyage de base des colonnes
    df.columns = df.columns.str.strip()
    
    if k == "tarbes_intercites":
        # Si Tarbes est en Départ, on inverse avec Arrivée
        if 'Départ' in df.columns and 'Arrivée' in df.columns:
            # Vérifier si Tarbes est dans Départ
            tarbes_in_depart = df['Départ'].astype(str).str.contains('Tarbes', case=False, na=False).any()
            if tarbes_in_depart:
                print(f"Correction inversion Départ/Arrivée pour {k}")
                # Inverser les colonnes
                df[['Départ', 'Arrivée']] = df[['Arrivée', 'Départ']]

    elif k in ["albi_intercites", "cerbere_intercites", "latour_de_carol_intercites"]:
        if 'Départ' in df.columns and 'Arrivée' in df.columns:
            # Ces lignes partent de Paris-Austerlitz, donc Paris devrait être en Départ
            paris_in_arrivee = df['Arrivée'].astype(str).str.contains('Paris', case=False, na=False).any()
            if paris_in_arrivee:
                print(f"Correction inversion Départ/Arrivée pour {k}")
                df[['Départ', 'Arrivée']] = df[['Arrivée', 'Départ']]

# Concaténer tous les DataFrames
df_complet = pd.concat(data_dict.values(), ignore_index=True)

# Standardisation des noms de colonnes
df_complet.columns = df_complet.columns.str.strip()

# Mapping des colonnes
mapping_colonnes = {
    'Date': 'Date',
    'Départ': 'Départ',
    'Arrivée': 'Arrivée',
    'Nombre de trains programmés': 'Trains_programmés',
    'Nombre de trains ayant circulé': 'Trains_circulés',
    'Nombre de trains annulés': 'Trains_annulés',
    "Nombre de trains en retard à l'arrivée": 'Trains_retard',
    'Taux de régularité': 'Taux_régularité'
}

# Renommer uniquement les colonnes qui existent
df_complet = df_complet.rename(columns={
    k: v for k, v in mapping_colonnes.items() 
    if k in df_complet.columns
})

# Nettoyage et validation
# Filtrer les lignes où Départ et Arrivée sont identiques ou manquantes
mask_valide = (
    df_complet['Départ'].notna() & 
    df_complet['Arrivée'].notna() & 
    (df_complet['Départ'] != df_complet['Arrivée'])
)
df_filtre = df_complet[mask_valide].copy()

# Conversion des colonnes numériques
colonnes_numeriques = ['Trains_programmés', 'Trains_circulés', 
                       'Trains_annulés', 'Trains_retard', 'Taux_régularité']

for col in colonnes_numeriques:
    if col in df_filtre.columns:
        df_filtre[col] = (
            df_filtre[col]
            .astype(str)
            .str.replace(',', '.', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace(r'[^\d\.\-]', '', regex=True)
        )
        df_filtre[col] = pd.to_numeric(df_filtre[col], errors='coerce')

# Afficher les relations uniques pour vérifier
print("\n RELATIONS UNIQUES DÉPART -> ARRIVÉE")
relations_uniques = df_filtre[['Départ', 'Arrivée']].drop_duplicates()
print(relations_uniques.sort_values(['Départ', 'Arrivée']).to_string())

# Compter les occurrences
print("\n NOMBRE DE RELATIONS PAR GARE DE DÉPART ===")
depart_counts = df_filtre['Départ'].value_counts()
print(depart_counts)

print("\n NOMBRE DE RELATIONS PAR GARE D'ARRIVÉE")
arrivee_counts = df_filtre['Arrivée'].value_counts()
print(arrivee_counts)


# Agrégation et calcul des taux

"""
Ce bloc :
- agrège les données par relation Départ -> Arrivée,
- calcule le taux d'annulation et le taux de retard,
- filtre les valeurs aberrantes et prépare les données pour la visualisation.
"""
# Agrégation
df_summary = df_filtre.groupby(['Départ', 'Arrivée']).agg({
    'Trains_programmés': 'sum',
    'Trains_circulés': 'sum',
    'Taux_régularité': 'mean',
    'Trains_retard': 'sum',
    'Trains_annulés': 'sum'
}).reset_index()

# Calcul des taux
df_summary['Taux_annulation'] = (
    df_summary['Trains_annulés'] / df_summary['Trains_programmés'] * 100
).round(1)
df_summary['Taux_annulation'] = df_summary['Taux_annulation'].fillna(0)

df_summary['Taux_retard'] = (
    df_summary['Trains_retard'] / df_summary['Trains_circulés'] * 100
).round(1)
df_summary['Taux_retard'] = df_summary['Taux_retard'].fillna(0)

# Filtrer les valeurs aberrantes
df_summary = df_summary[
    df_summary['Taux_régularité'].notna() & 
    df_summary['Taux_régularité'].between(0, 100)
]

# VÉRIFICATION FINALE DES DONNÉES
print(f"Nombre total de relations: {len(df_summary)}")
print(f"Gares de départ uniques: {df_summary['Départ'].nunique()}")
print(f"Gares d'arrivée uniques: {df_summary['Arrivée'].nunique()}")



# Visualisation avec Plotly

"""
Ce bloc :
- crée un scatter plot interactif avec Plotly Express,
- taille des points = nombre de trains en retard,
- couleur = gare de départ,
- axes formatés et infobulles personnalisées pour toutes les métriques.
"""
fig = px.scatter(
    df_summary,
    x='Trains_programmés',
    y='Taux_régularité',
    size='Trains_retard',
    color='Départ',  
    hover_name='Arrivée',
    custom_data=['Départ', 'Trains_programmés', 'Trains_circulés', 'Taux_régularité', 
                 'Trains_retard', 'Trains_annulés', 'Taux_annulation', 'Taux_retard'],
    title='Analyse de Performance du Réseau Intercités du Sud Ouest<br><sub>Taille = Nombre de retards | Couleur = Gare de départ</sub>',
    labels={
        'Trains_programmés': 'Trains Programmes (total)',
        'Taux_régularité': 'Taux de Régularité SNCF (%)',
        'Départ': 'Gare de Départ',
        'Trains_retard': 'Retards totaux'
    },
    size_max=40
)

# Formatage axes
fig.update_layout(
    xaxis=dict(showgrid=True, title="Traffic total (trains programmés)", tickformat=',d'),
    yaxis=dict(showgrid=True, title="Fiabilité (taux de régularité SNCF %)", ticksuffix='%'),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    plot_bgcolor='rgba(248,248,248,0.8)',
    height=700,
    showlegend=True,
    legend=dict(
        title="Gares de départ",
        itemsizing='constant'
    )
)
#infobulle
fig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{hovertext}</b>",
        "Gare de départ: %{customdata[0]}",
        "Trains programmés: %{customdata[1]:,}",
        "Trains ayant circulé: %{customdata[2]:,}",
        "Taux de régularité SNCF: %{customdata[3]:.1f}%",
        "Trains en retard: %{customdata[4]:,}",
        "Trains annulés: %{customdata[5]:,}",
        "Taux d'annulation: %{customdata[6]:.1f}%",
        "Taux de retard: %{customdata[7]:.1f}%",
        "<extra></extra>"
    ]),
    marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey'), sizemin=4)
)

# Affichage
fig.show()

# Après l'exécution
mem_apres = process.memory_info().rss / 1024 / 1024  # Mo
print(f"Mémoire utilisée : {mem_apres - mem_avant:.2f} Mo")

end_time = time.time()
execution_time = end_time - start_time

print(f"Temps d'exécution : {execution_time:.2f} secondes")