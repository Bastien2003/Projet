import pandas as pd
import json
from data_loader import load_all_data


# --- Charger uniquement les fichiers "intercites"
data_dict = {k: df for k, df in load_all_data().items() if 'intercites' in k}

REQUIRED_COLS = [
    "Nombre de trains en retard à l'arrivée",
    "Nombre de trains annulés",
    "Nombre de trains programmés",
    "Nombre de trains ayant circulé",
    "Date"
]

# Vérification et concaténation
frames = []
for k, df in data_dict.items():
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"Fichier {k} incomplet, colonnes manquantes: {missing}")
    frames.append(df)

# Extraire les DataFrames individuellement
albi = data_dict['albi_intercites']
bayonne = data_dict['bayonne_intercites']
beziers = data_dict['beziers_intercites']
cerbere = data_dict['cerbere_intercites']
latour = data_dict['latour_de_carol_intercites']
nimes = data_dict['nimes_intercites']
tarbes = data_dict['tarbes_intercites']
toulouse = data_dict['toulouse_intercites']

# Ajout données
albi['Ville'], albi['Départ'] = 'Albi', 'Paris-Austerlitz'
bayonne['Ville'], bayonne['Départ'] = 'Bayonne', 'Toulouse-Matabiau'
beziers['Ville'], beziers['Départ'] = 'Beziers', 'Clermont-Ferrand'
cerbere['Ville'], cerbere['Départ'] = 'Cerbere', 'Paris-Austerlitz'
latour['Ville'], latour['Départ'] = 'Latour de Carol', 'Paris-Austerlitz'
nimes['Ville'], nimes['Départ'] = 'Nîmes', 'Clermont-Ferrand'
tarbes['Ville'], tarbes['Départ'] = 'Tarbes', 'Paris-Austerlitz'
toulouse['Ville'] = 'Toulouse'
if 'Départ' not in toulouse.columns:
    toulouse['Départ'] = 'Inconnu'

# Combinaison et dates
toutes_donnees = pd.concat([albi, bayonne, beziers, cerbere, latour, nimes, tarbes, toulouse], ignore_index=True)
toutes_donnees['Date_complete'] = pd.to_datetime(toutes_donnees['Date'].astype(str) + '-01', errors='coerce')
toutes_donnees['Annee'] = toutes_donnees['Date_complete'].dt.year
toutes_donnees['Mois'] = toutes_donnees['Date_complete'].dt.month
toutes_donnees['Date_iso'] = toutes_donnees['Date_complete'].dt.strftime('%Y-%m-%d')

COLONNE_RETARD = "Nombre de trains en retard à l'arrivée"
COLONNE_ANNULE = "Nombre de trains annulés"
COLONNE_PROGRAMME = "Nombre de trains programmés"
COLONNE_CIRCULE = "Nombre de trains ayant circulé"

# Colonnes à exporter pour JS
cols_export = ['Ville', 'Départ', 'Date', 'Date_iso', 'Annee', 'Mois',
               COLONNE_RETARD, COLONNE_ANNULE, COLONNE_PROGRAMME, COLONNE_CIRCULE]


donnees_js = toutes_donnees[cols_export].to_dict('records')

# Création du fichier HTML
html_content = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyse des retards ferroviaires - Occitanie</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .container {{
            max-width: 1400px;
            margin-top: 20px;
        }}
        .card {{
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: none;
            border-radius: 10px;
        }}
        .card-body {{
            padding: 25px;
        }}
        h1 {{
            color: #2c3e50;
            font-weight: 700;
            margin-bottom: 30px;
            text-align: center;
        }}
        .control-group {{
            margin-bottom: 20px;
        }}
        label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
        }}
        .form-select {{
            border-radius: 8px;
            border: 2px solid #e9ecef;
            padding: 10px 15px;
            transition: all 0.3s ease;
        }}
        .form-select:focus {{
            border-color: #2E86AB;
            box-shadow: 0 0 0 0.2rem rgba(46, 134, 171, 0.25);
        }}
        #graphique {{
            width: 100%;
            height: 600px;
            background: white;
            border-radius: 10px;
            padding: 15px;
        }}
        .loading {{
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Analyse des retards ferroviaires - Occitanie</h1>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <div class="control-group">
                            <label for="ville-select" class="form-label">Choisir la ville:</label>
                            <select id="ville-select" class="form-select">
                                <option value="">Sélectionnez une ville</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label for="gare-select" class="form-label">Choisir la gare de départ:</label>
                            <select id="gare-select" class="form-select" disabled>
                                <option value="">-- Sélectionnez d'abord une ville --</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label for="annee-select" class="form-label">Choisir l'année:</label>
                            <select id="annee-select" class="form-select" disabled>
                                <option value="">-- Sélectionnez d'abord une ville --</option>
                            </select>
                        </div>
                        
                        <p class="text-muted mt-4">
                            Graphique montrant les trains programmés, ayant circulé, en retard et annulés.
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-9">
                <div class="card">
                    <div class="card-body">
                        <div id="graphique" class="loading">
                            Chargement du graphique...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Données intégrées dans la page
        const toutesDonnees = {json.dumps(donnees_js, ensure_ascii=False)};
        
        // Variables globales
        let currentVille = '';
        let currentGare = '';
        let currentAnnee = '';

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {{
            initialiserApplication();
        }});

        function initialiserApplication() {{
            initialiserSelectVilles();
            ajouterEcouteurs();
            mettreAJourGraphique();
        }}

        function initialiserSelectVilles() {{
            const villes = [...new Set(toutesDonnees.map(d => d.Ville))].sort();
            const select = document.getElementById('ville-select');
            
            villes.forEach(ville => {{
                const option = document.createElement('option');
                option.value = ville;
                option.textContent = ville;
                select.appendChild(option);
            }});

            // Sélectionner Albi par défaut
            if (villes.includes('Albi')) {{
                select.value = 'Albi';
                select.dispatchEvent(new Event('change'));
            }}
        }}

        function ajouterEcouteurs() {{
            document.getElementById('ville-select').addEventListener('change', function(e) {{
                currentVille = e.target.value;
                mettreAJourGares();
                mettreAJourAnnees();
                mettreAJourGraphique();
            }});

            document.getElementById('gare-select').addEventListener('change', function(e) {{
                currentGare = e.target.value;
                mettreAJourAnnees();
                mettreAJourGraphique();
            }});

            document.getElementById('annee-select').addEventListener('change', function(e) {{
                currentAnnee = e.target.value;
                mettreAJourGraphique();
            }});
        }}

        function mettreAJourGares() {{
            const selectGare = document.getElementById('gare-select');
            
            if (!currentVille) {{
                selectGare.innerHTML = '<option value="">-- Sélectionnez d\\'abord une ville --</option>';
                selectGare.disabled = true;
                return;
            }}

            const gares = [...new Set(toutesDonnees
                .filter(d => d.Ville === currentVille)
                .map(d => d.Départ))].sort();

            selectGare.innerHTML = '';
            
            if (gares.length > 1) {{
                gares.forEach(gare => {{
                    const option = document.createElement('option');
                    option.value = gare;
                    option.textContent = gare;
                    selectGare.appendChild(option);
                }});
                selectGare.disabled = false;
                currentGare = gares[0];
                selectGare.value = currentGare;
            }} else {{
                selectGare.innerHTML = '<option value="">Une seule gare disponible</option>';
                selectGare.disabled = true;
                currentGare = gares.length === 1 ? gares[0] : '';
            }}
        }}

        function mettreAJourAnnees() {{
            const selectAnnee = document.getElementById('annee-select');
            
            if (!currentVille) {{
                selectAnnee.innerHTML = '<option value="">-- Sélectionnez d\\'abord une ville --</option>';
                selectAnnee.disabled = true;
                return;
            }}

            let donneesFiltrees = toutesDonnees.filter(d => d.Ville === currentVille);
            if (currentGare) {{
                donneesFiltrees = donneesFiltrees.filter(d => d.Départ === currentGare);
            }}

            const annees = [...new Set(donneesFiltrees.map(d => d.Annee))].sort((a, b) => b - a);

            selectAnnee.innerHTML = '';
            
            if (annees.length > 0) {{
                annees.forEach(annee => {{
                    const option = document.createElement('option');
                    option.value = annee;
                    option.textContent = annee;
                    selectAnnee.appendChild(option);
                }});
                selectAnnee.disabled = false;
                currentAnnee = annees[0];
                selectAnnee.value = currentAnnee;
            }} else {{
                selectAnnee.innerHTML = '<option value="">Aucune donnée</option>';
                selectAnnee.disabled = true;
                currentAnnee = '';
            }}
        }}

        function mettreAJourGraphique() {{
            if (!currentVille) {{
                document.getElementById('graphique').innerHTML = '<div class="loading">Sélectionnez une ville pour afficher le graphique</div>';
                return;
            }}

            // Filtrer les données
            let donneesFiltrees = toutesDonnees.filter(d => d.Ville === currentVille);
            
            if (currentGare) {{
                donneesFiltrees = donneesFiltrees.filter(d => d.Départ === currentGare);
            }}
            
            if (currentAnnee) {{
                donneesFiltrees = donneesFiltrees.filter(d => d.Annee === parseInt(currentAnnee));
            }}

            // Grouper par mois
            const donneesParMois = {{}};
            donneesFiltrees.forEach(d => {{
                if (!donneesParMois[d.Date]) {{
                    donneesParMois[d.Date] = {{
                        date: new Date(d.Date_iso),
                        retard: 0,
                        annules: 0,
                        programmes: 0,
                        circules: 0
                    }};
                }}
                donneesParMois[d.Date].retard += d["{COLONNE_RETARD}"] || 0;
                donneesParMois[d.Date].annules += d["{COLONNE_ANNULE}"] || 0;
                donneesParMois[d.Date].programmes += d["{COLONNE_PROGRAMME}"] || 0;
                donneesParMois[d.Date].circules += d["{COLONNE_CIRCULE}"] || 0;
            }});

            const donneesTriées = Object.values(donneesParMois).sort((a, b) => a.date - b.date);

            if (donneesTriées.length === 0) {{
                document.getElementById('graphique').innerHTML = '<div class="loading">Aucune donnée disponible pour cette sélection</div>';
                return;
            }}

            // Créer le graphique Plotly
            const traceRetard = {{
                x: donneesTriées.map(d => d.date),
                y: donneesTriées.map(d => d.retard),
                name: 'Trains en retard',
                type: 'bar',
                marker: {{ color: '#FFC966' }}
            }};

            const traceAnnules = {{
                x: donneesTriées.map(d => d.date),
                y: donneesTriées.map(d => d.annules),
                name: 'Trains annulés',
                type: 'bar',
                marker: {{ color: '#D4A5A5' }}
            }};

            const traceProgrammes = {{
                x: donneesTriées.map(d => d.date),
                y: donneesTriées.map(d => d.programmes),
                name: 'Trains programmés',
                type: 'scatter',
                mode: 'lines',
                line: {{ color: '#B5EAD7', width: 3 }}
            }};

            const traceCircules = {{
                x: donneesTriées.map(d => d.date),
                y: donneesTriées.map(d => d.circules),
                name: 'Trains ayant circulé',
                type: 'scatter',
                mode: 'lines',
                line: {{ color: '#2E86AB', width: 4, dash: 'dash' }}
            }};

            const layout = {{
                title: getTitre(),
                barmode: 'stack',
                xaxis: {{ 
                    title: 'Mois',
                    tickformat: '%b %Y'
                }},
                yaxis: {{ title: 'Nombre de trains' }},
                legend: {{ x: 0.02, y: 0.98 }},
                hovermode: 'closest',
                paper_bgcolor: 'white',
                plot_bgcolor: 'white'
            }};

            Plotly.newPlot('graphique', [traceRetard, traceAnnules, traceProgrammes, traceCircules], layout, {{responsive: true}});
        }}

        function getTitre() {{
            let titre = 'Performance ferroviaire : ';
            
            if (currentGare) {{
                titre += currentGare + ' → ' + currentVille;
            }} else {{
                // Trouver la gare par défaut
                const gares = [...new Set(toutesDonnees
                    .filter(d => d.Ville === currentVille)
                    .map(d => d.Départ))].sort();
                titre += (gares[0] || '') + ' → ' + currentVille;
            }}
            
            if (currentAnnee) {{
                titre += ' en ' + currentAnnee;
            }}
            
            return titre;
        }}
    </script>
</body>
</html>
'''

