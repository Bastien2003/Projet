// --- 1) Charger tous les CSV depuis le dossier /data ---
async function loadCSVs() {
    const files = [
        "albi_retard_arrivee_intercites.csv",
        "bayonne_retard_arrivee_intercites.csv",
        "beziers_retard_arrivee_intercites.csv",
        "cerbere_retard_arrivee_intercites.csv",
        "frequentation_gares_occitanie.csv",
        "latour_de_carol_retard_arrivee_intercites.csv",
        "liste_gares_occitanie.csv",
        "montpellier_retard_arrivee+depart_tgv.csv",
        "nimes_retard_arrivee+depart_tgv.csv",
        "nimes_retard_arrivee_intercites.csv",
        "occitanie_retard_arrivee.csv",
        "perpignan_retard_arrivee+depart_tgv.csv",
        "retard_france_intercites.csv",
        "tarbes_retard_arrivee_intercites.csv",
        "temps_moyen_narbonne-paris.csv",
        "temps_moyen_occitanie-paris.csv",
        "temps_moyens_montpellier-paris.csv",
        "toulouse_matabiau_retard_arrivee+depart_tgv.csv",
        "toulouse_matabiau_retard_arrivee_intercites.csv"
    ];

    let allData = [];

    for (const file of files) {
        const response = await fetch("data/" + file);
        const text = await response.text();

        // CSV → tableau d’objets
        const rows = text.split("\n").map(r => r.split(","));

        const headers = rows[0].map(h => h.trim().toLowerCase());
        const dataRows = rows.slice(1);

        dataRows.forEach(r => {
            let obj = {};
            headers.forEach((h, i) => obj[h] = r[i]);

            // Ajout de la ville depuis le nom de fichier si absente
            if (!obj["ville"]) {
                obj["ville"] = file.split("_")[0];
            }

            if (obj["retard"]) obj["retard"] = parseFloat(obj["retard"]);
            allData.push(obj);
        });
    }

    return allData;
}

let DATA = [];

async function init() {
    DATA = await loadCSVs();

    const mode = document.getElementById("mode");
    const choix = document.getElementById("choix");

    mode.addEventListener("change", updateDropdown);
    choix.addEventListener("change", updateGraph);

    updateDropdown();
}

// --- 2) Mettre à jour le second menu ---
function updateDropdown() {
    const mode = document.getElementById("mode").value;
    const choix = document.getElementById("choix");

    let values = [];

    if (mode === "ville") {
        values = [...new Set(DATA.map(d => d.ville))].sort();
    } else {
        values = [...new Set(DATA.map(d => d.cause))].sort();
    }

    choix.innerHTML = values.map(v => `<option value="${v}">${v}</option>`).join("");

    updateGraph();
}

// --- 3) Mettre à jour le graphique ---
function updateGraph() {
    const mode = document.getElementById("mode").value;
    const choix = document.getElementById("choix").value;

    let filtered = DATA.filter(d => d.retard && d.cause);

    let x = [];
    let y = [];

    if (mode === "ville") {
        const subset = filtered.filter(d => d.ville === choix);

        const group = {};
        subset.forEach(d => {
            if (!group[d.cause]) group[d.cause] = [];
            group[d.cause].push(d.retard);
        });

        x = Object.keys(group);
        y = x.map(k => group[k].reduce((a, b) => a + b) / group[k].length);

        var title = `Retard moyen par cause – ${choix}`;

    } else {
        const subset = filtered.filter(d => d.cause === choix);

        const group = {};
        subset.forEach(d => {
            if (!group[d.ville]) group[d.ville] = [];
            group[d.ville].push(d.retard);
        });

        x = Object.keys(group);
        y = x.map(k => group[k].reduce((a, b) => a + b) / group[k].length);

        var title = `Retard moyen par ville – Cause : ${choix}`;
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
