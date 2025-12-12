# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Projet'
copyright = '2025, Regnat'
author = 'Regnat'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',  # pour générer la doc des modules Python
    'sphinx.ext.viewcode'  # pour inclure le code source
]

templates_path = ['_templates']
exclude_patterns = []

language = 'fr'

# Ajouter le chemin vers les dossiers contenant les modules Python
import os
import sys

# Pour data_fetcher.py
sys.path.insert(0, r"C:\Users\neore\OneDrive\Bureau\M1\Projet\roadmap\1erSite")
# Pour data_loader.py et les autres modules dans script/edition
sys.path.insert(0, r"C:\Users\neore\OneDrive\Bureau\M1\Projet\script\edition")

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # joli thème
html_static_path = ['_static']