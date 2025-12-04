import os
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# 1 — CHEMIN VERS LE DOSSIER DES CSV
# ============================================================

DATA_FOLDER = os.path.join("data", "base_de_donnees_version_csv")

def charger_csv(data_folder):
    if not os.path.isdir(data_folder):
        raise ValueError(f"Le dossier n'existe pas : {data_folder}")

    fichiers = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
    frames = []

    if not fichiers:
        raise ValueError("Aucun fichier CSV trouvé dans base_de_donnees_version_csv !")

    for fichier in fichiers:
        path = os.path.join(data_folder, fichier)
        print(f"Chargement du fichier : {path}")

        try:
            df = pd.read_csv(path, sep=";", low_memory=False)
        except:
            df = pd.read_csv(path, low_memory=False)

        df["source_fichier"] = fichier
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


df = charger_csv(DATA_FOLDER)


# ============================================================
# 2 — TROUVER AUTOMATIQUEMENT LA COLONNE VILLE/GARE
# ============================================================

COLONNE_VILLE = None

for col in df.columns:
    col_norm = col.lower()
    if "ville" in col_norm or "gare" in col_norm:
        COLONNE_VILLE = col
        break

if COLONNE_VILLE is None:
    raise ValueError("Impossible de trouver une colonne représentant la ville ou la gare !")


# ============================================================
# 3 — IDENTIFIER LES COLONNES DES RETARDS / CAUSES
# ============================================================

colonnes_retard = [
    col for col in df.columns
    if "retard" in col.lower() or "cause" in col.lower()
]

if not colonnes_retard:
    raise ValueError("Aucune colonne contenant 'retard' ou 'cause' n'a été trouvée.")


print("\nColonnes utilisées pour les retards / causes :")
for c in colonnes_retard:
    print("  →", c)


# ============================================================
# 4 — NETTOYAGE & CALCUL DES MOYENNES
# ============================================================

df = df.dropna(subset=[COLONNE_VILLE])
df[COLONNE_VILLE] = df[COLONNE_VILLE].astype(str).str.upper()

# Convertir en numérique lorsque possible
for col in colonnes_retard:
    df[col] = pd.to_numeric(df[col], errors="ignore")


# Certaines colonnes peuvent être non-numériques → on garde que les numériques
colonnes_numeriques = [c for c in colonnes_retard if pd.api.types.is_numeric_dtype(df[c])]

if not colonnes_numeriques:
    raise ValueError("Les colonnes retard/cause ne contiennent pas de valeurs numériques.")

stats = df.groupby(COLONNE_VILLE)[colonnes_numeriques].mean().reset_index()


# ============================================================
# 5 — GRAPHIQUE INTERACTIF
# ============================================================

villes = stats[COLONNE_VILLE].unique()
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
            {"title": f"Retards et causes – {ville}"}
        ]
    ))


fig.update_layout(
    title=f"Retards et causes – {ville_defaut}",
    xaxis_title="Types de retard / Causes",
    yaxis_title="Valeur moyenne",
    updatemenus=[{
        "buttons": buttons,
        "direction": "down",
        "x": 1.20,
        "y": 1.0
    }]
)

fig.show()
