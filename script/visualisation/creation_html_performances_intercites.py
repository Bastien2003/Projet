import pandas as pd
import plotly.express as px


fichiers = {
    'albi': "C:/Users/SCD-UM/Documents/bases/albi_retard_arrivee_intercites.csv",
    'bayonne': "C:/Users/SCD-UM/Documents/bases/bayonne_retard_arrivee_intercites.csv", 
    'beziers': "C:/Users/SCD-UM/Documents/bases/beziers_retard_arrivee_intercites.csv",
    'cerbere': "C:/Users/SCD-UM/Documents/bases/cerbere_retard_arrivee_intercites.csv",
    'latour': "C:/Users/SCD-UM/Documents/bases/latour_de_carol_retard_arrivee_intercites.csv",
    'nimes': "C:/Users/SCD-UM/Documents/bases/nimes_retard_arrivee_intercites.csv",
    'tarbes': "C:/Users/SCD-UM/Documents/bases/tarbes_retard_arrivee_intercites.csv",
    'toulouse': "C:/Users/SCD-UM/Documents/bases/toulouse_matabiau_retard_arrivee_intercites_REGOUPE.csv"
}

# 2. CHARGEMENT DES DONNEES AVEC POINTS-VIRGULES
liste_dataframes = []

for ville, chemin in fichiers.items():
    try:
        # Charger avec point-virgule comme séparateur
        df_temp = pd.read_csv(chemin, encoding='utf-8', sep=';')
        
        # Pour Toulouse, on garde la colonne Départ originale
        if ville == 'toulouse':
            df_temp['Ville_départ'] = df_temp['Départ']
        else:
            df_temp['Ville_départ'] = ville.capitalize()
            
        liste_dataframes.append(df_temp)
        print(f"✅ {ville.capitalize()} : {len(df_temp)} lignes")
        
    except Exception as e:
        try:
            df_temp = pd.read_csv(chemin, encoding='latin-1', sep=';')
            if ville == 'toulouse':
                df_temp['Ville_départ'] = df_temp['Départ']
            else:
                df_temp['Ville_départ'] = ville.capitalize()
            liste_dataframes.append(df_temp)
        except Exception as e2:
            print( f" impossible de charger {ville} : {e2}")

# Combiner toutes les données
df_complet = pd.concat(liste_dataframes, ignore_index=True)


# 3. NETTOYAGE DES COLONNES
df_complet.columns = df_complet.columns.str.strip()

# Renommer les colonnes
mapping_colonnes = {
    'Date': 'Date',
    'Départ': 'Départ', 
    'Arrivée': 'Arrivée',
    'Nombre de trains programmés': 'Trains_programmés',
    'Nombre de trains ayant circulé': 'Trains_circulés',
    'Nombre de trains annulés': 'Trains_annulés',
    "Nombre de trains en retard à l'arrivée": 'Trains_retard',
    'Taux de régularité': 'Taux_régularité',
    'Ville_départ': 'Ville_départ'
}

df_complet = df_complet.rename(columns=mapping_colonnes)

df_filtre = df_complet[df_complet['Départ'] != df_complet['Arrivée']].copy()

# 5. PRÉPARATION DES DONNÉES
colonnes_numeriques = ['Trains_programmés', 'Trains_circulés', 'Trains_annulés', 'Trains_retard', 'Taux_régularité']

for col in colonnes_numeriques:
    if col in df_filtre.columns:
        df_filtre[col] = df_filtre[col].astype(str).str.replace(',', '.').str.replace(' ', '')
        df_filtre[col] = pd.to_numeric(df_filtre[col], errors='coerce')

# 6. 
df_summary = df_filtre.groupby(['Départ', 'Arrivée']).agg({
    'Trains_programmés': 'sum',
    'Trains_circulés': 'sum',
    'Taux_régularité': 'mean',  # On garde la moyenne du taux SNCF
    'Trains_retard': 'sum',
    'Trains_annulés': 'sum'
}).reset_index()


# Taux d'annulation
df_summary['Taux_annulation'] = (
    df_summary['Trains_annulés'] / df_summary['Trains_programmés'] * 100
).round(1)

# Taux de retard 
df_summary['Taux_retard'] = (
    df_summary['Trains_retard'] / df_summary['Trains_circulés'] * 100
).round(1)

# Nettoyer les données
df_summary = df_summary[df_summary['Taux_régularité'].notna()]
df_summary = df_summary[df_summary['Taux_régularité'].between(0, 100)]

# 7. CRÉATION DU PLOT SIMPLIFIÉ

fig = px.scatter(
    df_summary,
    x='Trains_programmés',
    y='Taux_régularité', 
    size='Trains_retard',
    color='Départ',
    hover_name='Arrivée',
    custom_data=['Départ', 'Trains_programmés', 'Trains_circulés', 'Taux_régularité', 
                 'Trains_retard', 'Trains_annulés', 'Taux_annulation', 'Taux_retard'],
    title='Analyse de Performance du Réseau Intercités d\'occitanie<br><sub>Taille = Nombre de retards | Couleur = Gare de départ</sub>',
    labels={
        'Trains_programmés': 'Trains Programmes (total)',
        'Taux_régularité': 'Taux de Régularité SNCF (%)',
        'Départ': 'Gare de Départ',
        'Trains_retard': 'Retards totaux'
    },
    size_max=40
)

# 8. FORMATAGE DES AXES
fig.update_layout(
    xaxis=dict(
        showgrid=True, 
        title="Traffic total (trains programmés)",
        tickformat=',d'
    ),
    yaxis=dict(
        showgrid=True, 
        title="Fiabilité (taux de régularité SNCF %)",
        ticksuffix='%'
    ),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    plot_bgcolor='rgba(248,248,248,0.8)',
    height=700,
    showlegend=True
)


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
    marker=dict(
        opacity=0.7,
        line=dict(width=1, color='DarkSlateGrey'),
        sizemin=4
    )
)

# 9. AFFICHAGE ET SAUVEGARDE

fig.show()

fig.write_html("C:/Users/SCD-UM/Documents/bases/performance_intercites_simple.html")
print("Graphique sauvegardé : performance_intercites_simple.html")

# 10. STATISTIQUES SIMPLES
print("\n TOP 5 DES RELATIONS LES PLUS FIABLES :")
top_fiables = df_summary.nlargest(5, 'Taux_régularité')[['Départ', 'Arrivée', 'Taux_régularité', 'Trains_programmés']]
print(top_fiables.to_string(index=False))

print("\n TOP 5 DES RELATIONS LES MOINS FIABLES :")
top_problematiques = df_summary.nsmallest(5, 'Taux_régularité')[['Départ', 'Arrivée', 'Taux_régularité', 'Trains_programmés']]
print(top_problematiques.to_string(index=False))
