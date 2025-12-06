#%%
import os
import pandas as pd
import plotly.graph_objects as go
import webbrowser

# ============================================================
# 1 — CHEMIN VERS LE DOSSIER DES CSV
# ============================================================
DATA_FOLDER = os.path.join("..", "data", "base_de_donnees_version_csv")

if not os.path.isdir(DATA_FOLDER):
    raise ValueError(f"Le dossier n'existe pas : {DATA_FOLDER}")

def charger_csv(data_folder):
    fichiers = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    if not fichiers:
        raise ValueError("Aucun fichier CSV trouvé dans le dossier !")

    frames = []
    for fichier in fichiers:
        path = os.path.join(data_folder, fichier)
        print(f"[OK] Chargement : {fichier}")
        try:
            df = pd.read_csv(path, sep=";", low_memory=False)
        except:
            df = pd.read_csv(path, low_memory=False)
        df["source_fichier"] = fichier
        frames.append(df)

    return pd.concat(frames, ignore_index=True)

df = charger_csv(DATA_FOLDER)

# ============================================================
# 2 — DÉTECTION AUTOMATIQUE COLONNE VILLE/GARE
# ============================================================
COLONNE_VILLE = next(
    (col for col in df.columns if "ville" in col.lower() or "gare" in col.lower()),
    None
)
if COLONNE_VILLE is None:
    raise ValueError("Impossible de trouver une colonne représentant la ville ou la gare !")

print(f"Colonne détectée pour ville/gare : {COLONNE_VILLE}")

# Nettoyage de la colonne ville/gare
df = df.dropna(subset=[COLONNE_VILLE])
df[COLONNE_VILLE] = df[COLONNE_VILLE].astype(str).str.upper()
print(f"Nombre de lignes après nettoyage : {len(df)}")

# ============================================================
# 3 — IDENTIFIER LES COLONNES NUMÉRIQUES UTILES
# ============================================================
# Convertir toutes les colonnes en numériques si possible
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="ignore")

# Exclure les colonnes 'Code Uic' et celles contenant 'Total'
colonnes_numeriques = [
    c for c in df.columns 
    if pd.api.types.is_numeric_dtype(df[c])
       and "CODE UIC" not in c.upper()
       and "NON VOYAGEURS" not in c.upper()
       and "CODE POSTAL" not in c.upper()
       and df[c].sum() > 0  # au moins une valeur >0
]

if not colonnes_numeriques:
    raise ValueError("Aucune colonne utile avec des valeurs numériques supérieures à 0.")

print("Colonnes retenues pour le graphique :", colonnes_numeriques)

# ============================================================
# 4 — CALCUL DES MOYENNES PAR VILLE
# ============================================================
stats = df.groupby(COLONNE_VILLE)[colonnes_numeriques].mean().reset_index()
villes = stats[COLONNE_VILLE].unique()

# ============================================================
# 5 — GRAPHIQUE INTERACTIF
# ============================================================
colonnes_simplifiees = [c.replace("_", " ").title() for c in colonnes_numeriques]
mapping = dict(zip(colonnes_simplifiees, colonnes_numeriques))

ville_defaut = villes[0]
y_defaut = stats[stats[COLONNE_VILLE] == ville_defaut][colonnes_numeriques].iloc[0].values

fig = go.Figure()
fig.add_trace(go.Bar(
    x=colonnes_simplifiees,
    y=y_defaut,
    name=ville_defaut
))

# Menu déroulant
buttons = []
for ville in villes:
    y_vals = stats[stats[COLONNE_VILLE] == ville][colonnes_numeriques].iloc[0].values
    buttons.append(dict(
        label=ville,
        method="update",
        args=[
            {"y": [y_vals], "name": ville},
            {"title": f"Nombre total de voyageurs – {ville}"}
        ]
    ))

fig.update_layout(
    title=f"Nombre total de voyageurs – {ville_defaut}",
    xaxis_title="Nombre total de voyageurs",
    yaxis_title="Valeur moyenne",
    updatemenus=[{
        "buttons": buttons,
        "direction": "down",
        "x": 1.2,
        "y": 1.0
    }]
)

# Sauvegarde et affichage du graphique
fig.write_html("graphique.html")
webbrowser.open("graphique.html")
