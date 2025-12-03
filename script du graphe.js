// --- Fonction pour charger un CSV et retourner un tableau d'objets ---
async function loadCSV(url, villeFromFile = null) {
    const res = await fetch(url);
    const text = await res.text();
    const rows = text.trim().split("\n").map(r => r.split(","));

    const headers = rows[0].map(h => h.trim().toLowerCase());
    const dataRows = rows.slice(1);

    const data = dataRows.map(r => {
        let obj = {};
        headers.forEach((h, i) => obj[h] = r[i]);
        if (villeFromFile && !obj["ville"]) obj["ville"] = villeFromFile;
        if (obj["retard"]) obj["retard"] = parseFloat(obj["retard"].replace(",", "."));
        return obj;
    });
    return data;
}

// --- Liste des fichiers CSV (tous ceux dans base_de_donnees_version_csv) ---
const files = [
    "albi_retard_arrivee_intercites.csv",
    "bayonne_retard_arrivee_intercites.csv",
    "beziers_retard_arrivee_intercites.csv",
    "cerbere_retard_arrivee_intercites.csv",
    "latour_de_carol_retard_arrivee_intercites.csv",
    "montpellier_retard_arrivee+depart_tgv.csv",
    "nimes_retard_arrivee+depart_tgv.csv",
    "nimes_retard_arrivee_intercites.csv",
    "occitanie_retard_arrivee.csv",
    "perpignan_retard_arrivee+depart_tgv.csv",
    "retard_france_intercites.csv",
    "tarbes_retard_arrivee_intercites.csv",
    "toulouse_matabiau_retard_arrivee+depart_tgv.csv",
    "toulouse_matabiau_retard_arrivee_intercites.csv"
];

const folder = "data/base_de_donnees_version_csv/";

let DATA = [];

async function init() {
    for (const f of files) {
        // Déduire la ville du nom du fichier si possible
        const villeFromFile = f.split("_")[0];
        const csvData = await loadCSV(folder + f, villeFromFile);
        DATA = DATA.concat(csvData);
    }

    const modeSelect = document.getElementById("mode");
    const choixSelect = document.getElementById("choix");

    modeSelect.addEventListener("change", updateDropdown);
    choixSelect.addEventListener("change", updateGraph);

    updateDropdown();
}

// --- Mettre à jour le menu déroulant ---
function updateDropdown() {
    const mode = document.getElementById("mode").value;
    const choixSelect = document.getElementById("choix");

    let values = [];
    if (mode === "ville") {
        values = [...new Set(DATA.map(d => d.ville))].sort();
    } else {
        values = [...new Set(DATA.map(d => d.cause))].sort();
    }

    choixSelect.innerHTML = values.map(v => `<option value="${v}">${v}</option>`).join("");
    updateGraph();
}

// --- Mettre à jour le graphique ---
function updateGraph() {
    const mode = document.getElementById("mode").value;
    const choix = document.getElementById("choix").value;

    const filtered = DATA.filter(d => d.retard && d.cause);

    let x = [];
    let y = [];
    let title = "";

    if (mode === "ville") {
        const subset = filtered.filter(d => d.ville === choix);
        const group = {};
        subset.forEach(d => {
            if (!group[d.cause]) group[d.cause] = [];
            group[d.cause].push(d.retard);
        });
        x = Object.keys(group);
        y = x.map(k => group[k].reduce((a, b) => a + b) / group[k].length);
        title = `Retard moyen par cause – ${choix}`;
    } else {
        const subset = filtered.filter(d => d.cause === choix);
        const group = {};
        subset.forEach(d => {
            if (!group[d.ville]) group[d.ville] = [];
            group[d.ville].push(d.retard);
        });
        x = Object.keys(group);
        y = x.map(k => group[k].reduce((a, b) => a + b) / group[k].length);
        title = `Retard moyen par ville – Cause : ${choix}`;
    }

    Plotly.newPlot("graph", [{
        type: "bar",
        x: x,
        y: y
    }], {
        title: title,
        xaxis: { title: mode === "ville" ? "Causes" : "Villes" },
        yaxis: { title: "Retard moyen (min)" }
    });
}

init();
