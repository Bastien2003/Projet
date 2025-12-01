import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import dash
from dash.exceptions import PreventUpdate
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from data_loader import load_all_data

# Charger tous les CSV
data_dict = {k: df for k, df in load_all_data().items() if 'intercites' in k}

REQUIRED_COLS = [
    "Nombre de trains en retard à l'arrivée",
    "Nombre de trains annulés",
    "Nombre de trains programmés",
    "Nombre de trains ayant circulé",
    "Date"
]

frames = []
try:
    for k, df in data_dict.items():
        # Vérifier les colonnes attendues
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            raise KeyError(f"Fichier {k} incomplet, colonnes manquantes: {missing}")
        frames.append(df)
    print("Toutes les données sont chargées")
except Exception as e:
    print(f"Erreur chargement: {e}")
    raise

# Extraire les DataFrames individuels
albi = data_dict['albi_intercites']
bayonne = data_dict['bayonne_intercites']
beziers = data_dict['beziers_intercites']
cerbere = data_dict['cerbere_intercites']
latour = data_dict['latour_de_carol_intercites']
nimes = data_dict['nimes_intercites']
tarbes = data_dict['tarbes_intercites']
toulouse = data_dict['toulouse_intercites']

albi['Ville'] = 'Albi'
albi['Départ'] = 'Paris-Austerlitz'

bayonne['Ville'] = 'Bayonne'
bayonne['Départ'] = 'Toulouse-Matabiau'

beziers['Ville'] = 'Beziers'
beziers['Départ'] = 'Clermont-Ferrand'

cerbere['Ville'] = 'Cerbere'
cerbere['Départ'] = 'Paris-Austerlitz'

latour['Ville'] = 'Latour de Carol'
latour['Départ'] = 'Paris-Austerlitz'

nimes['Ville'] = 'Nîmes'
nimes['Départ'] = 'Clermont-Ferrand'

tarbes['Ville'] = 'Tarbes'
tarbes['Départ'] = 'Paris-Austerlitz'

toulouse['Ville'] = 'Toulouse'
if 'Départ' not in toulouse.columns:
    toulouse['Départ'] = 'Inconnu'

# Combinaison et conversion des dates
toutes_donnees = pd.concat([albi, bayonne, beziers, cerbere, latour, nimes, tarbes, toulouse], ignore_index=True)

# On s'attend que la colonne "Date" soit au format YYYY-MM (ex: '2023-01').
# Si ce n'est pas le cas, la conversion affichera NaT pour les lignes non conformes.
toutes_donnees['Date_complete'] = pd.to_datetime(toutes_donnees['Date'].astype(str) + '-01', format='%Y-%m-%d', errors='coerce')

# Extraire l'année et le mois pour faciliter le filtrage
toutes_donnees['Annee'] = toutes_donnees['Date_complete'].dt.year
toutes_donnees['Mois'] = toutes_donnees['Date_complete'].dt.month

# Constantes colonnes 
COLONNE_RETARD = "Nombre de trains en retard à l'arrivée"
COLONNE_ANNULE = "Nombre de trains annulés"
COLONNE_PROGRAMME = "Nombre de trains programmés"
COLONNE_CIRCULE = "Nombre de trains ayant circulé"
COLONNE_DATE = "Date"

# Application Dash 
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# nous servira a obtenir les années disponibles pour une ville et une gare
def get_available_years(df, ville, gare=None):
    data = df[df['Ville'] == ville]
    if gare:
        data = data[data['Départ'] == gare]
    years = sorted(data['Annee'].dropna().unique(), reverse=True)
    return years

# Layout
app.layout = dbc.Container([
    html.H1("Analyse des retards ferroviaires - Occitanie", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Label("Choisir la ville:"),
                    dcc.Dropdown(
                        id='ville-dropdown',
                        options=[{'label': v, 'value': v} for v in sorted(toutes_donnees['Ville'].dropna().unique())],
                        value=sorted(toutes_donnees['Ville'].dropna().unique())[0]
                    ),
                    html.Br(),

                    # Container gare : le dropdown (la barre des options) existe toujours (elle est initialement cachée)
                    html.Div(
                        id='gare-container',
                        children=[
                            html.Label("Choisir la gare de départ:"),
                            dcc.Dropdown(
                                id='gare-dropdown',
                                options=[],
                                value=None,
                                disabled=True,
                                clearable=False,
                                style={'display': 'none'}  # caché au départ
                            )
                        ]
                    ),
                    html.Br(),
                    html.Div(id='annee-container', children=[
                        html.Label("Choisir l'année:"),
                        dcc.Dropdown(id='annee-dropdown', options=[], value=None, disabled=True)
                    ]),
                    html.Br(),
                    html.P("Graphique montrant les trains programmés, ayant circulé, en retard et annulés.")
                ])
            ])
        ], width=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graphique')
                ])
            ])
        ], width=9)
    ])
], fluid=True)

# Callback (fonction qui sera un argument dans une autre fonction plus tard) pour mettre à jour le contenu du container gare (dropdown toujours rendu)
@app.callback(
    Output('gare-dropdown', 'options'),
    Output('gare-dropdown', 'value'),
    Output('gare-dropdown', 'disabled'),
    Output('gare-dropdown', 'style'),
    Output('gare-container', 'style'),
    Input('ville-dropdown', 'value')
)
def update_gare(ville):
    if not ville:
        # garder caché et vide
        return [], None, True, {'display': 'none'}, {'display': 'none'}

    # Récupérer les gares pour la ville
    gares = sorted(
        toutes_donnees[toutes_donnees['Ville'] == ville]['Départ']
        .dropna()
        .unique()
    )

    # Si 0 ou 1 gare -> on cache le dropdown (la barre des options) (mais il existe toujours dans le layout)
    if len(gares) <= 1:
        # si 1 gare, on peut préremplir la valeur (utile pour le filtrage ensuite)
        value = gares[0] if len(gares) == 1 else None
        return [], value, True, {'display': 'none'}, {'display': 'none'}

    # Si plusieurs gares -> on affiche et on remplit les options
    options = [{'label': g, 'value': g} for g in gares]
    value = gares[0]  # valeur par défaut (première)
    return options, value, False, {'display': 'block'}, {'display': 'block'}



# Callback (fonction qui sera un argument dans une autre fonction plus tard) pour mettre à jour les années disponibles (dépend de ville ET gare)
@app.callback(
    Output('annee-container', 'children'),
    Input('ville-dropdown', 'value'),
    Input('gare-dropdown', 'value')
)
def update_annee(ville, gare):
    if not ville:
        return html.Div()

    annees = get_available_years(toutes_donnees, ville, gare)
    if not annees:
        return html.P("Aucune donnée disponible pour la combinaison sélectionnée")

    # Si une seule année, la liste de choix est désactivée
    disabled = len(annees) == 1
    return [
        html.Label("Choisir l'année:"),
        dcc.Dropdown(
            id='annee-dropdown',
            options=[{'label': str(a), 'value': a} for a in annees],
            value=annees[0],
            disabled=disabled
        )
    ]

# Callback (fonction qui sera un argument dans une autre fonction plus tard) unique pour mettre à jour le graphique (dépend de ville, gare, année)
@app.callback(
    Output('graphique', 'figure'),
    Input('ville-dropdown', 'value'),
    Input('gare-dropdown', 'value'),
    Input('annee-dropdown', 'value')
)
def update_graphique(ville, gare, annee):
    if not ville:
        return go.Figure().update_layout(title="Sélectionnez une ville")

    # Si l'année ou la gare n'est pas fournie, on tente de prendre la première disponible
    if gare is None:
        gares = sorted(toutes_donnees[toutes_donnees['Ville'] == ville]['Départ'].dropna().unique())
        gare = gares[0] if gares else None

    if annee is None:
        annees = get_available_years(toutes_donnees, ville, gare)
        annee = annees[0] if annees else None

    if annee is None:
        return go.Figure().update_layout(title=f"Aucune donnée pour {ville}")

    # Filtrer
    data = toutes_donnees[(toutes_donnees['Ville'] == ville) & (toutes_donnees['Annee'] == int(annee))]
    if gare:
        data = data[data['Départ'] == gare]

    if data.empty:
        titre = f"Aucune donnée pour {gare or 'N/A'} → {ville} en {annee}"
        return go.Figure().update_layout(title=titre)

    # Tri par date
    data = data.sort_values('Date_complete')
    # Construire la figure
    fig = go.Figure()
    pastel_retard = '#FFE3AA'
    pastel_annule = '#FFD1DC'
    pastel_programme = '#B5EAD7'
    pastel_circule = '#2E86AB'
    fig.add_trace(go.Bar(x=data['Date_complete'], y=data[COLONNE_RETARD], name='Trains en retard'))
    fig.add_trace(go.Bar(x=data['Date_complete'], y=data[COLONNE_ANNULE], name='Trains annulés'))
    fig.add_trace(go.Scatter(x=data['Date_complete'], y=data[COLONNE_PROGRAMME], name='Trains programmés', mode='lines'))
    fig.add_trace(go.Scatter(x=data['Date_complete'], y=data[COLONNE_CIRCULE], name='Trains ayant circulé', mode='lines'))

    titre = f"Performance ferroviaire : {gare or data['Départ'].iloc[0]} → {ville} en {annee}"

    fig.update_layout(
        title=titre,
        barmode='stack',
        xaxis_title='Mois',
        yaxis_title='Nombre de trains',
        legend=dict(x=0.02, y=0.98)
    )

    return fig


if __name__ == '__main__':
    print("Application disponible sur: http://localhost:8050")
    app.run(debug=True, port=8050)
