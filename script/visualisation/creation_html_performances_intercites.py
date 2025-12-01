import pandas as pd
import json
from data_loader import load_all_data

#Charger les fichiers "intercites" uniquement
data_dict = {k: df for k, df in load_all_data().items() if "intercites" in k}

# Correction Départ/Arrivée
for k, df in data_dict.items():
    df.columns = df.columns.str.strip()
    if k == "tarbes_intercites":
        if 'Départ' in df.columns and 'Arrivée' in df.columns:
            tarbes_in_depart = df['Départ'].astype(str).str.contains('Tarbes', case=False, na=False).any()
            if tarbes_in_depart:
                df[['Départ', 'Arrivée']] = df[['Arrivée', 'Départ']]
    elif k in ["albi_intercites", "cerbere_intercites", "latour_de_carol_intercites"]:
        if 'Départ' in df.columns and 'Arrivée' in df.columns:
            paris_in_arrivee = df['Arrivée'].astype(str).str.contains('Paris', case=False, na=False).any()
            if paris_in_arrivee:
                df[['Départ', 'Arrivée']] = df[['Arrivée', 'Départ']]

# Concaténer tous les DataFrames
df_complet = pd.concat(data_dict.values(), ignore_index=True)
df_complet.columns = df_complet.columns.str.strip()

# Renommer colonnes
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
df_complet = df_complet.rename(columns={k: v for k, v in mapping_colonnes.items() if k in df_complet.columns})

# Nettoyage et conversion des colonnes numériques
df_filtre = df_complet[
    df_complet['Départ'].notna() & 
    df_complet['Arrivée'].notna() & 
    (df_complet['Départ'] != df_complet['Arrivée'])
].copy()

for col in ['Trains_programmés', 'Trains_circulés', 'Trains_annulés', 'Trains_retard', 'Taux_régularité']:
    if col in df_filtre.columns:
        df_filtre[col] = pd.to_numeric(
            df_filtre[col].astype(str)
                     .str.replace(',', '.', regex=False)
                     .str.replace(' ', '', regex=False),
            errors='coerce'
        )

# Agrégation par Départ / Arrivée
df_summary = df_filtre.groupby(['Départ', 'Arrivée']).agg({
    'Trains_programmés':'sum',
    'Trains_circulés':'sum',
    'Trains_retard':'sum',
    'Trains_annulés':'sum',
    'Taux_régularité':'mean'
}).reset_index()

df_summary['Taux_annulation'] = (df_summary['Trains_annulés'] / df_summary['Trains_programmés'] * 100).round(1).fillna(0)
df_summary['Taux_retard'] = (df_summary['Trains_retard'] / df_summary['Trains_circulés'] * 100).round(1).fillna(0)

# Préparer les données pour JS
donnees_js = df_summary.to_dict('records')

# Générer le HTML avec Plotly Scatter
html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Performance Intercités Occitanie</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
<h1>Performance Intercités - Occitanie</h1>
<div id="graph" style="width:100%;height:700px;"></div>
<script>
const data = {json.dumps(donnees_js, ensure_ascii=False)};

// Extraire les gares uniques pour une palette
// Extraire les gares uniques pour une palette
const garesDepart = [...new Set(data.map(d => d.Départ))];

// Palette 10 couleurs
const couleurs = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf"
];

const colorMap = {{}};
garesDepart.forEach((gare, i) => {{
    colorMap[gare] = couleurs[i % couleurs.length];
}});

// Créer une trace par gare de départ
const traces = garesDepart.map(gare => {{
    const rows = data.filter(d => d.Départ === gare);

    return {{
        name: gare,
        x: rows.map(d => d.Trains_programmés),
        y: rows.map(d => d.Taux_régularité),
        mode: 'markers',
        marker: {{
            size: rows.map(d => Math.sqrt(d.Trains_retard) * 3),
            color: colorMap[gare],
            sizemode: 'area',
            sizeref:
                2.0 * Math.max(...data.map(d => Math.sqrt(d.Trains_retard))) / 40 ** 2,
            line: {{ width: 1, color: 'DarkSlateGrey' }}
        }},
        text: rows.map(d => d.Arrivée),
        customdata: rows.map(d => [
            d.Départ, d.Trains_programmés, d.Trains_circulés,
            d.Taux_régularité, d.Trains_retard, d.Trains_annulés,
            d.Taux_annulation, d.Taux_retard
        ]),
        hovertemplate:
            "<b>%{{text}}</b><br>Gare de Départ: %{{customdata[0]}}<br>" +
            "Programmes: %{{customdata[1]:,}}<br>" +
            "Circulés: %{{customdata[2]:,}}<br>" +
            "Taux régularité: %{{customdata[3]:.1f}}%<br>" +
            "Retard: %{{customdata[4]:,}}<br>" +
            "Annulés: %{{customdata[5]:,}}<br>" +
            "Taux annulation: %{{customdata[6]:.1f}}%<br>" +
            "Taux retard: %{{customdata[7]:.1f}}%<extra></extra>"
    }};
}});

const minY = Math.min(...data.map(d => d.Taux_régularité));
const maxY = Math.max(...data.map(d => d.Taux_régularité));

const layout = {{
    title: "Performance du réseau Intercités d'Occitanie",
    xaxis: {{ title: "Trains programmés", tickformat: ",d" }},
    yaxis: {{ title: "Taux de régularité (%)",  range: [minY - 2, maxY + 2] }},
    hovermode: "closest"
}};

Plotly.newPlot('graph', traces, layout);
</script>
</body>
</html>
"""

with open("graph_interactif_performance.html","w",encoding="utf-8") as f:
    f.write(html_content)

print("Fichier HTML créé: graph_interactif_performance.html")
