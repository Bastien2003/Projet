Ce diagramme représente le planning prévisionnel du projet, découpé en 4 grandes phases.  
Les couleurs indiquent l’état d’avancement de chaque tâche :

| Couleur / Statut | Signification |
|------------------|---------------|
| 🟩 Vert          | Tâche terminée |
| 🟨 Jaune         | Tâche en cours |
| ⬜ Gris clair     | Tâche à faire |

---

```mermaid
gantt
    title Diagramme de Gantt du projet
    dateFormat  YYYY-MM-DD
    axisFormat  %d-%b
    excludes    weekends

    %% -----------------------------
    %% Phase 1 : Création du site
    %% -----------------------------
    section Phase 1 : Création du site
    Créer le site vide           :done,   task1, 2025-10-21, 2025-10-27

    %% -----------------------------
    %% Phase 2 : Données et graphes
    %% -----------------------------
    section Phase 2 : Données et graphes
    Créer la carte des gares     :active, task2, 2025-10-28, 2025-11-03
    Créer les graphes            :        task3, 2025-11-04, 2025-11-10

    %% -----------------------------
    %% Phase 3 : Visualisation
    %% -----------------------------
    section Phase 3 : Visualisation
    Afficher les graphes         :        task4, 2025-11-11, 2025-11-14
    Exporter les graphes         :        task5, 2025-11-15, 2025-11-18

    %% -----------------------------
    %% Phase 4 : Finalisation
    %% -----------------------------
    section Phase 4 : Finalisation
    Mise en page du site         :        task6, 2025-11-19, 2025-11-22
