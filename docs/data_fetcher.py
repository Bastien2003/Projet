import pooch
from pathlib import Path

# URL de base sur GitHub
BASE_URL = "https://raw.githubusercontent.com/Bastien2003/Projet/main/roadmap/1erSite/"

CSV_FILES = [
    "albi_retard_arrivee_intercites.csv",
    "bayonne_retard_arrivee_intercites.csv",
    "beziers_retard_arrivee_intercites.csv",
    "cerbere_retard_arrivee_intercites.csv",
    "latour_de_carol_retard_arrivee_intercites.csv",
    "montpellier_retard_arrivee+depart_tgv.csv",
    "nimes_retard_arrivee_intercites.csv",
    "perpignan_retard_arrivee+depart_tgv.csv",
    "tarbes_retard_arrivee_intercites.csv",
    "toulouse_matabiau_retard_arrivee_intercites.csv"
]

# Dossier local pour le cache
DATA_DIR = Path(__file__).parent / "data"

# Création du fetcher Pooch
fetcher = pooch.create(
    path=DATA_DIR,
    base_url=BASE_URL,
    registry={csv: None for csv in CSV_FILES}  # pas de hash pour l'instant
)

def get_csv(filename: str) -> str:
    """
    Retourne le chemin local du CSV téléchargé ou mis en cache.
    """
    return str(fetcher.fetch(filename))

